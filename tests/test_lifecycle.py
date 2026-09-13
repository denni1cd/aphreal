import asyncio
import json

import pytest
from fastapi.testclient import TestClient

from aphrael.app import create_app
from aphrael.config import Settings
from aphrael.storage import InstanceLock, Store
from test_engine import wait_task


def request(**changes):
    return {"objective": "Inspect", "tool": "system.status", **changes}


def test_cancel_queued_running_and_continue(tmp_path):
    with TestClient(create_app(Settings(data_dir=tmp_path))) as client:
        first = client.post('/api/tasks', json=request(delay_seconds=3)).json()['id']
        wait_task(client, first, 'RUNNING')
        second = client.post('/api/tasks', json=request()).json()['id']
        assert client.get(f'/api/tasks/{second}').json()['status'] == 'QUEUED'
        assert client.post(f'/api/tasks/{second}/cancel', json={}).json()['status'] == 'CANCELLED'
        assert client.post(f'/api/tasks/{first}/cancel', json={}).json()['status'] == 'CANCELLED'
        third = client.post('/api/tasks', json=request()).json()['id']
        assert wait_task(client, third)['status'] == 'COMPLETED'
        for task_id in (first, second):
            task = client.get(f'/api/tasks/{task_id}').json()
            assert task['status'] == 'CANCELLED'
            assert not task['evidence']
            assert not task['verification']['verified']
        # Cancelling terminal work is idempotent and cannot rewrite history.
        assert client.post(f'/api/tasks/{third}/cancel', json={}).json()['status'] == 'COMPLETED'


@pytest.mark.parametrize('mode', ['no_evidence', 'mismatch', 'exception', 'mutate_result'])
def test_worker_cannot_attest_own_success(tmp_path, mode):
    class UntrustedWorker:
        async def run(self, task, execute, cancelled):
            if mode == 'exception':
                raise RuntimeError('private worker content')
            if mode == 'mismatch':
                await execute('repository.status', {})
            if mode == 'mutate_result':
                value = await execute(task['tool'], task['arguments'])
                value['result'] = 'fabricated'
            return {'success': True, 'evidence': [{'ok': True}]}
    app = create_app(Settings(data_dir=tmp_path))
    app.state.core.workers['untrusted'] = UntrustedWorker()
    app.state.core.settings.profiles['test'] = {'worker': 'untrusted'}
    with TestClient(app) as client:
        task_id = client.post('/api/tasks', json=request(profile='test')).json()['id']
        result = wait_task(client, task_id)
        if mode == 'mutate_result':
            assert result['status'] == 'COMPLETED'
            assert result['result'] != 'fabricated'
        else:
            assert result['status'] == 'FAILED'
            assert not result['verification']['verified']
        next_id = client.post('/api/tasks', json=request()).json()['id']
        assert wait_task(client, next_id)['status'] == 'COMPLETED'


def test_failed_capability_evidence_is_not_completed(tmp_path):
    with TestClient(create_app(Settings(data_dir=tmp_path))) as client:
        task_id = client.post('/api/tasks', json=request(tool='filesystem.read', arguments={'path':'does-not-exist.txt'})).json()['id']
        task = wait_task(client, task_id)
        assert task['status'] == 'FAILED'
        assert task['evidence'][0]['ok'] is False


def test_profiles_input_validation_and_local_boundary(tmp_path):
    with TestClient(create_app(Settings(data_dir=tmp_path))) as client:
        for profile in ('voice', 'fast', 'deep', 'coding', 'local', 'unknown'):
            assert client.post('/api/tasks', json=request(profile=profile)).status_code == 400
        assert client.get('/api/health').status_code == 200
        assert client.post('/api/tasks', json=request(delay_seconds=-1)).status_code == 422
        assert client.post('/api/tasks', json=request(approved=True)).status_code == 422
        assert client.post('/api/tasks', json=request(), headers={'Origin':'https://foreign.example'}).status_code == 403
        assert client.get('/api/health', headers={'Host':'foreign.example'}).status_code == 403
        assert client.post('/api/tasks', content='{}').status_code == 415
        assert client.get('/api/tasks/missing').status_code == 404
        assert client.post('/api/tools/invoke',json={'tool':'missing','arguments':{}}).status_code in (400,403)


def test_degraded_subsystems_are_not_healthy(tmp_path):
    app = create_app(Settings(data_dir=tmp_path))
    with TestClient(app) as client:
        core = app.state.core
        healthy = core.store.healthy
        core.store.healthy = lambda: False
        assert client.get('/api/health').status_code == 503
        core.store.healthy = healthy
        core.executor_error = 'failure'
        assert client.get('/api/health').status_code == 503
        core.executor_error = None
        core.registry.describe = lambda: []
        assert client.get('/api/health').status_code == 503


def test_recovery_of_active_and_queued_work(tmp_path):
    store = Store(tmp_path / 'tasks.sqlite3')
    active = store.create(request(arguments={}, delay_seconds=0), 'general')
    store.transition(active['id'], {'QUEUED'}, 'RUNNING', 'Started')
    queued = store.create(request(arguments={}, delay_seconds=0), 'general')
    with TestClient(create_app(Settings(data_dir=tmp_path))) as client:
        result = client.get('/api/tasks/'+active['id']).json()
        assert result['status'] == 'FAILED'
        assert 'Interrupted' in result['error']
        assert wait_task(client, queued['id'])['status'] == 'COMPLETED'


def test_single_instance_lock(tmp_path):
    first = InstanceLock(tmp_path / 'worker.lock')
    second = InstanceLock(tmp_path / 'worker.lock')
    first.acquire()
    try:
        with pytest.raises(RuntimeError, match='already'):
            second.acquire()
    finally:
        first.release()
    second.acquire()
    second.release()


def test_configuration(tmp_path, monkeypatch):
    config = tmp_path / 'profiles.json'
    config.write_text(json.dumps({'default_profile':'coding','profiles':{'coding':{'worker':'deterministic','model':None}}}))
    monkeypatch.setenv('APHRAEL_CONFIG', str(config))
    monkeypatch.setenv('APHRAEL_DATA_DIR', str(tmp_path / 'state'))
    settings = Settings.from_env()
    with TestClient(create_app(settings)) as client:
        task_id = client.post('/api/tasks', json=request()).json()['id']
        task = wait_task(client, task_id)
        assert task['status'] == 'COMPLETED' and task['profile'] == 'coding'
    with pytest.raises(ValueError, match='outside'):
        Settings(data_dir=Settings().repo / 'data')
    config.write_text('{"unexpected":true}')
    with pytest.raises(ValueError):
        Settings.from_env()


def test_policy_denies_immediate_and_delegated_without_running_handler(tmp_path):
    from aphrael.capabilities import Tool, Empty
    invoked = []
    app = create_app(Settings(data_dir=tmp_path))
    app.state.core.registry.register(Tool('restricted', 'Test only', Empty, Empty, lambda args: invoked.append(True) or {}, risk='approval_required'))
    class Worker:
        async def run(self, task, execute, cancelled):
            await execute('restricted', {})
    app.state.core.workers['policy-test'] = Worker()
    app.state.core.settings.profiles['policy-test'] = {'worker':'policy-test'}
    with TestClient(app) as client:
        assert client.post('/api/tools/invoke',json={'tool':'restricted','arguments':{}}).status_code == 403
        assert client.post('/api/tasks',json=request(tool='restricted')).status_code == 403
        task_id = client.post('/api/tasks',json=request(profile='policy-test')).json()['id']
        assert wait_task(client, task_id)['status'] == 'FAILED'
        assert not invoked


def test_cancel_during_capability_does_not_complete_or_overlap(tmp_path):
    import threading
    from aphrael.capabilities import Tool, Empty
    entered, release = threading.Event(), threading.Event()
    def slow(args):
        entered.set()
        assert release.wait(5)
        return {}
    app = create_app(Settings(data_dir=tmp_path))
    app.state.core.registry.register(Tool('slow', 'Test only', Empty, Empty, slow))
    with TestClient(app) as client:
        task_id = client.post('/api/tasks',json=request(tool='slow')).json()['id']
        assert entered.wait(3)
        try:
            client.post('/api/tasks/'+task_id+'/cancel',json={})
            queued_id = client.post('/api/tasks',json=request()).json()['id']
            assert client.get('/api/tasks/'+queued_id).json()['status'] == 'QUEUED'
        finally:
            release.set()
        assert wait_task(client,queued_id)['status'] == 'COMPLETED'
        task = client.get('/api/tasks/'+task_id).json()
        assert task['status'] == 'CANCELLED' and not task['verification']['verified']


def test_cancel_at_running_transition_never_executes(tmp_path):
    from aphrael.capabilities import Tool, Empty
    calls = []
    app = create_app(Settings(data_dir=tmp_path))
    core = app.state.core
    core.registry.register(Tool('probe', 'Harmless seam fixture', Empty, Empty, lambda args: calls.append(True) or {}))
    original = core.store.transition
    def transition(task_id, allowed, status, message, **updates):
        result = original(task_id, allowed, status, message, **updates)
        if status == 'RUNNING':
            core.cancel(task_id)
        return result
    core.store.transition = transition
    with TestClient(app) as client:
        task_id = client.post('/api/tasks',json=request(tool='probe')).json()['id']
        assert wait_task(client,task_id)['status'] == 'CANCELLED'
    assert not calls


def test_direct_adapter_gets_same_validation(tmp_path):
    app = create_app(Settings(data_dir=tmp_path))
    core = app.state.core
    with pytest.raises(ValueError):
        core.create_task(request(id='overwrite-authority', status='COMPLETED'))
    with pytest.raises(ValueError):
        core.create_task(request(delay_seconds=-1))
    with TestClient(app) as client:
        task = core.create_task(request())
        assert wait_task(client, task['id'])['status'] == 'COMPLETED'


def test_invalid_config_and_http_length_fail_cleanly(tmp_path):
    with pytest.raises(ValueError, match='default_profile'):
        Settings(data_dir=tmp_path, default_profile=[])
    with pytest.raises(ValueError, match='source repository'):
        Settings(repo=tmp_path, data_dir=Settings().repo / 'runtime')
    with TestClient(create_app(Settings(data_dir=tmp_path))) as client:
        for value in ('invalid', '-1'):
            assert client.get('/api/health',headers={'Content-Length':value}).status_code == 400
        assert client.get('/api/health').status_code == 200
