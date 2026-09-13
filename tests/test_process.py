"""A real HTTP server, real worker and real process death/restart; no mocks."""
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

import httpx


def test_real_process_restart(tmp_path):
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    env = {**os.environ, 'APHRAEL_DATA_DIR': str(tmp_path / 'runtime'), 'APHRAEL_PORT': str(port)}
    env.pop('APHRAEL_CONFIG', None)
    base = f'http://127.0.0.1:{port}'

    def start():
        process = subprocess.Popen([sys.executable, '-m', 'aphrael'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            assert process.poll() is None, 'Server exited before becoming healthy'
            try:
                if httpx.get(base+'/api/health', timeout=1).status_code == 200:
                    return process
            except httpx.HTTPError:
                pass
            time.sleep(.05)
        process.kill()
        process.wait()
        raise AssertionError('Server never became healthy')

    def wait(task_id, target):
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            task = httpx.get(base+'/api/tasks/'+task_id).json()
            if task['status'] == target:
                return task
            time.sleep(.05)
        raise AssertionError(task)

    process = start()
    try:
        with httpx.Client(base_url=base) as client:
            done_id = client.post('/api/tasks', json={'objective':'Repository inspection','tool':'repository.status'}).json()['id']
            done = wait(done_id, 'COMPLETED')
            assert done['verification']['verified']
            direct_commit = subprocess.check_output(['git','rev-parse','HEAD'], text=True).strip()
            assert done['result']['commit'] == direct_commit
            active_id = client.post('/api/tasks', json={'objective':'Interrupted work','tool':'system.status','delay_seconds':30}).json()['id']
            wait(active_id,'RUNNING')
            queued_id = client.post('/api/tasks', json={'objective':'Queued work','tool':'system.status'}).json()['id']
            assert client.get('/api/tasks/'+queued_id).json()['status'] == 'QUEUED'
            assert client.get('/api/health').json()['healthy']
        process.kill()
        process.wait(timeout=5)
        process = start()
        assert httpx.get(base+'/api/tasks/'+done_id).json() == done
        assert wait(active_id, 'FAILED')['error'].startswith('Interrupted')
        assert wait(queued_id, 'COMPLETED')['verification']['verified']
    finally:
        process.terminate()
        process.wait(timeout=5)
