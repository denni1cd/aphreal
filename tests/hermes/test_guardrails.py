import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

PLUGIN = Path(__file__).resolve().parents[2] / 'plugins' / 'aphrael_guardrails' / 'guard.py'
PROVISION = Path(__file__).resolve().parents[2] / 'scripts' / 'provision_aphrael_evidence.py'
spec = importlib.util.spec_from_file_location('aphrael_guard_test', PLUGIN)
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


@pytest.fixture
def boundary(tmp_path, monkeypatch):
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    output = workspace / 'outputs'
    output.mkdir()
    private = tmp_path / 'private'
    private.mkdir()
    p = dict(workspace=str(workspace), write_roots=[str(output)], protected_paths=[],
             role='worker', evidence_root=str(private), board='aphrael')
    policy_path = private / 'policy.json'
    policy_path.write_text(json.dumps(p))
    monkeypatch.setenv('APHRAEL_POLICY_FILE', str(policy_path))
    monkeypatch.setenv('HERMES_KANBAN_BOARD', 'aphrael')
    return p, policy_path, workspace, output, private


@pytest.mark.parametrize('path', ['../private/file', '.env', 'runtime/x', 'x:secret', '//server/file', 'foo./x', 'config.yaml'])
def test_private_and_ambiguous_paths_blocked(boundary, path):
    assert guard.pre_tool_call('read_file', {'path': path})['action'] == 'block'


def test_stock_file_scope_and_write_authority(boundary):
    p, _, workspace, output, _ = boundary
    (workspace / 'README.md').write_text('ground truth')
    assert guard.pre_tool_call('read_file', {'path': 'README.md'})['args']['path'] == str(workspace / 'README.md')
    assert guard.pre_tool_call('write_file', {'path': 'README.md', 'content': 'bad'})['action'] == 'block'
    assert guard.pre_tool_call('write_file', {'path': 'outputs/new.txt', 'content': 'ok'})['action'] == 'modify'
    assert guard.pre_tool_call('patch', {'path': 'outputs/new.txt', 'new_string': 'ok'})['action'] == 'modify'


def test_search_cannot_follow_hardlinks_or_private_tree(boundary):
    _, _, workspace, output, private = boundary
    secret = private / 'fixture.txt'
    secret.write_text('synthetic private')
    os.link(secret, output / 'innocent.txt')
    assert guard.pre_tool_call('read_file', {'path': 'outputs/innocent.txt'})['action'] == 'block'
    assert guard.pre_tool_call('search_files', {'path': 'outputs', 'pattern': 'synthetic'})['action'] == 'block'


@pytest.mark.skipif(os.name != 'nt', reason='Windows junction regression')
def test_windows_junction(boundary):
    _, _, _, output, private = boundary
    # Creating a disposable junction does not inspect any real private state.
    result = subprocess.run(['cmd', '/c', 'mklink', '/J', str(output / 'junction'), str(private)], capture_output=True)
    assert result.returncode == 0
    assert guard.pre_tool_call('search_files', {'path': 'outputs', 'pattern': '*'})['action'] == 'block'


def test_shell_unknown_tool_and_board_cannot_bypass(boundary):
    for name, args in [('terminal', {'command': 'cat ~/.codex/auth.json'}),
                       ('terminal', {'command': 'pwd; whoami'}), ('python', {'code': 'print(1)'}),
                       ('kanban_show', {'board': 'other'}), ('kanban_complete', {'artifacts': ['/private/x']})]:
        assert guard.pre_tool_call(name, args)['action'] == 'block'
    assert guard.pre_tool_call('terminal', {'command': 'pwd'})['action'] == 'modify'


def test_missing_corrupt_policy_and_board_fail_closed(boundary, monkeypatch):
    _, policy_path, *_ = boundary
    monkeypatch.setenv('HERMES_KANBAN_BOARD', 'wrong')
    assert guard.pre_tool_call('memory', {})['action'] == 'block'
    policy_path.write_text('{bad')
    assert guard.pre_tool_call('read_file', {'path': 'README.md'})['action'] == 'block'
    policy_path.unlink()
    assert guard.pre_tool_call('memory', {})['action'] == 'block'


def test_shell_hook_protocol_blocks_crash(boundary):
    run = subprocess.run([sys.executable, str(PLUGIN)], input='invalid', text=True, capture_output=True)
    assert run.returncode == 1
    assert json.loads(run.stdout)['action'] == 'block'


def test_profile_local_policy_default(boundary, monkeypatch):
    _, policy_path, *_ = boundary
    (policy_path.parent / 'aphrael-policy.json').write_bytes(policy_path.read_bytes())
    monkeypatch.delenv('APHRAEL_POLICY_FILE')
    monkeypatch.setenv('HERMES_HOME', str(policy_path.parent))
    assert guard.pre_tool_call('memory', {}) is None


def test_machine_root_selects_active_profile_policy(boundary, monkeypatch, tmp_path):
    _, policy_path, *_ = boundary
    root = tmp_path / 'hermes'
    selected = root / 'profiles' / 'aphrael' / 'aphrael-policy.json'
    selected.parent.mkdir(parents=True)
    selected.write_bytes(policy_path.read_bytes())
    monkeypatch.delenv('APHRAEL_POLICY_FILE')
    monkeypatch.setenv('HERMES_HOME', str(root))
    assert guard.pre_tool_call('memory', {}, profile_name='aphrael') is None


def test_worker_claims_replay_wrong_task_and_changed_file_not_verified(boundary):
    p, policy_path, _, output, private = boundary
    artifact = output / 'result.txt'
    artifact.write_bytes(b'expected')
    requests = private / 'requests'
    requests.mkdir()
    request = dict(task_id='task1', request_id='request1', board='aphrael', path=str(artifact),
                   sha256=hashlib.sha256(b'expected').hexdigest())
    (requests / 'request1.json').write_text(json.dumps(request))
    args = {'task_id': 'task1', 'request_id': 'request1'}
    assert json.loads(guard.observe(args, verify=True))['verified'] is False
    assert json.loads(guard.observe({**args, 'verified': True}, verify=True))['verified'] is False
    p['role'] = 'reviewer'
    policy_path.write_text(json.dumps(p))
    assert json.loads(guard.observe(args, verify=True))['verified'] is True
    assert json.loads(guard.observe(args))['verified'] is True
    assert json.loads(guard.observe({**args, 'task_id': 'task2'}))['verified'] is False
    # Replacing even a semantically similar request invalidates prior evidence.
    request_file = requests / 'request1.json'
    original = request_file.read_bytes()
    request_file.write_text(json.dumps({**request, 'revision': 2}))
    assert json.loads(guard.observe(args))['verified'] is False
    request_file.write_bytes(original)
    artifact.write_bytes(b'wrong')
    assert json.loads(guard.observe(args))['verified'] is False
    assert json.loads(guard.observe(args, verify=True))['verified'] is False
    artifact.unlink()
    assert json.loads(guard.observe(args, verify=True))['verified'] is False


def test_reviewer_cannot_write_or_spawn_worker(boundary):
    p, policy_path, *_ = boundary
    p['role'] = 'reviewer'
    policy_path.write_text(json.dumps(p))
    assert guard.pre_tool_call('write_file', {'path': 'outputs/a', 'content': 'x'})['action'] == 'block'
    assert guard.pre_tool_call('delegate_task', {'task': 'approve'})['action'] == 'block'
    assert guard.pre_tool_call('aphrael_work_delegate', {'instruction': 'task'})['action'] == 'block'
    assert guard.pre_tool_call('aphrael_work_status', {'request_id': 'a' * 32}) is None
    assert guard.pre_tool_call('aphrael_work_recall', {}) is None
    assert guard.pre_tool_call('aphrael_work_recent', {}) is None


def test_parent_can_use_native_work_tools_without_terminal_authority(boundary):
    assert guard.pre_tool_call('tool_search', {'queries': ['Aphrael Work']}) is None
    assert guard.pre_tool_call('tool_describe', {'names': ['aphrael_work_recent']}) is None
    assert guard.pre_tool_call('aphrael_work_delegate', {'instruction': 'task'}) is None
    assert guard.pre_tool_call('aphrael_work_status', {'request_id': 'a' * 32}) is None
    assert guard.pre_tool_call('aphrael_work_recall', {}) is None
    assert guard.pre_tool_call('aphrael_work_recent', {}) is None
    assert guard.pre_tool_call('terminal', {'command': 'python scripts/aphrael_work_bridge.py'})['action'] == 'block'


def test_additional_read_root_does_not_expand_write_authority(boundary):
    p, policy_path, workspace, _, _ = boundary
    source = workspace.parent / 'source'
    source.mkdir()
    (source / 'README.md').write_text('real source observation')
    p['read_roots'] = [str(workspace), str(source)]
    policy_path.write_text(json.dumps(p))
    path = str(source / 'README.md')
    assert guard.pre_tool_call('read_file', {'path': path})['args']['path'] == path
    assert guard.pre_tool_call('write_file', {'path': path, 'content': 'bad'})['action'] == 'block'
    assert guard.pre_tool_call('read_file', {'path': 'outputs/a'})['args']['path'] == str(workspace / 'outputs' / 'a')
    args = {'command': 'git --no-pager rev-parse HEAD', 'workdir': str(source)}
    assert guard.pre_tool_call('terminal', args)['args']['workdir'] == str(source)
    assert guard.pre_tool_call('terminal', {**args, 'workdir': str(workspace / 'outputs')})['action'] == 'block'
    assert guard.pre_tool_call('terminal', {**args, 'command': 'git reset --hard'})['action'] == 'block'
    assert guard.pre_tool_call('terminal', {**args, 'approval': True})['action'] == 'block'


def test_common_read_only_git_inspection_commands_are_allowed(boundary):
    _, _, workspace, _, _ = boundary
    for command in (
        'git status --short', 'git status --short --branch',
        'git branch --show-current', 'git rev-parse HEAD',
        'git log -1 --oneline --decorate', 'git --no-pager log -5 --oneline',
        'git remote -v',
    ):
        result = guard.pre_tool_call('terminal', {
            'command': command, 'workdir': str(workspace),
        })
        assert result['args']['workdir'] == str(workspace)


def test_protected_source_is_reviewable_but_never_writable(boundary):
    p, policy_path, workspace, _, _ = boundary
    source = workspace.parent / 'source'
    source.mkdir()
    guard_file = source / 'guard.py'
    guard_file.write_text('reviewable source')
    p['read_roots'] = [str(workspace), str(source)]
    p['protected_paths'] = [str(source)]
    policy_path.write_text(json.dumps(p))
    assert guard.pre_tool_call('read_file', {'path': str(guard_file)})['action'] == 'modify'
    assert guard.pre_tool_call('write_file', {'path': str(guard_file), 'content': 'bad'})['action'] == 'block'


def test_nested_read_root_does_not_authorize_private_paths(boundary):
    p, policy_path, workspace, _, _ = boundary
    private = workspace / '.hidden'
    private.mkdir()
    (private / 'text').write_text('synthetic')
    p['read_roots'] = [str(workspace), str(private)]
    policy_path.write_text(json.dumps(p))
    assert guard.pre_tool_call('read_file', {'path': str(private / 'text')})['action'] == 'block'


def test_search_approved_root_prunes_private_descendants(boundary):
    _, _, workspace, _, _ = boundary
    hidden = workspace / '.git'
    hidden.mkdir()
    (hidden / 'config').write_text('private')
    public = workspace / 'tests'
    public.mkdir()
    (public / 'test_example.py').write_text('def test_example(): pass')
    result = guard.pre_tool_call('search_files', {
        'target': 'files', 'pattern': '*.py', 'path': str(workspace), 'limit': 50,
    })
    assert result['args']['path'] == str(workspace)
    assert guard.pre_tool_call('search_files', {
        'target': 'files', 'pattern': '*', 'path': str(hidden),
    })['action'] == 'block'


def test_operator_provisions_immutable_expected_outcome(tmp_path):
    workspace = tmp_path / 'workspace'
    output = workspace / 'output'
    output.mkdir(parents=True)
    expected = tmp_path / 'expected.txt'
    expected.write_bytes(b'expected content')
    command = [sys.executable, str(PROVISION), '--evidence-root', str(tmp_path / 'evidence'),
               '--workspace', str(workspace), '--task-id', 'task1', '--request-id', 'request1',
               '--content-file', str(expected), '--path', str(output / 'result.txt')]
    first = subprocess.run(command, text=True, capture_output=True)
    assert first.returncode == 0
    request = json.loads((tmp_path / 'evidence' / 'requests' / 'request1.json').read_text())
    assert request['sha256'] == hashlib.sha256(b'expected content').hexdigest()
    assert subprocess.run(command, text=True, capture_output=True).returncode != 0
