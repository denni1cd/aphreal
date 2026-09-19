"""Aphrael policy at Hermes' supported pre_tool_call boundary.

This is a same-user policy, not an OS sandbox. A separately configured
fail_closed shell hook invokes this file even if native plugin loading fails.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
from datetime import datetime, timezone


class Denied(Exception):
    pass


def inside(path, root):
    return path == root or root in path.parents


def policy_file(profile_name=None):
    override = os.environ.get('APHRAEL_POLICY_FILE')
    if override:
        return Path(override)
    home = Path(os.environ['HERMES_HOME'])
    # A profile may be selected by Hermes' context while HERMES_HOME remains
    # the machine root. Shell hooks receive that active profile in their wire
    # payload; native plugins capture ctx.profile_name at registration.
    if profile_name and (home / 'profiles').is_dir():
        candidate = home / 'profiles' / profile_name / 'aphrael-policy.json'
        if candidate.is_file():
            return candidate
    return home / 'aphrael-policy.json'


def policy(profile_name=None):
    p = json.loads(policy_file(profile_name).read_text(encoding='utf-8-sig'))
    for key in ('workspace', 'write_roots', 'protected_paths', 'role', 'evidence_root', 'board'):
        if key not in p:
            raise Denied('Incomplete trusted policy')
    if p['role'] not in ('parent', 'worker', 'reviewer') or not p['board']:
        raise Denied('Invalid role or board')
    if os.environ.get('HERMES_KANBAN_BOARD') != p['board']:
        raise Denied('Kanban board not pinned')
    return p


def sensitive(name):
    n = name.lower()
    return ((n.startswith('.') and n != '.env.example') or
            n in {'private', 'secrets', 'runtime', 'memories', 'memory', 'logs', '__pycache__', 'node_modules', 'venv', 'config.yaml', 'auth.json'} or
            n.endswith(('.db', '.sqlite', '.sqlite3', '.pem', '.key', '.pfx', '.log')))


def read_roots(p):
    return [Path(x).resolve(strict=True) for x in p.get('read_roots', [p['workspace']])]


def checked_path(value, p, write=False, profile_name=None):
    if not isinstance(value, str) or not value or '\x00' in value:
        raise Denied('Invalid path')
    # Windows ADS, device paths, UNC, traversal and ambiguous trailing names.
    raw = value.replace('\\', '/')
    tail = raw[2:] if re.match(r'^[A-Za-z]:/', raw) else raw
    if ':' in tail or raw.startswith('//') or any(x == '..' or x.endswith((' ', '.')) for x in tail.split('/') if x not in ('', '.')):
        raise Denied('Ambiguous path denied')
    root = Path(p['workspace']).resolve(strict=True)
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    path = Path(os.path.abspath(path))
    matching_roots = [r for r in read_roots(p) if inside(path, r)]
    if not matching_roots:
        raise Denied('Outside approved read roots')
    # Nested read roots cannot bypass a private directory in a broader root.
    if any(sensitive(x) for r in matching_roots for x in path.relative_to(r).parts):
        raise Denied('Private path')
    # Runtime controls and reviewer evidence are private for every operation.
    # Distribution source controls must remain immutable to agents, but a
    # reviewer needs read-only access to inspect the guard and setup code.
    always_private = [Path(p['workspace']).resolve().parent / '.hermes',
                      Path(p['evidence_root']).resolve(), policy_file(profile_name).resolve()]
    if any(inside(path, x) for x in always_private):
        raise Denied('Protected control state')
    if write and any(inside(path, Path(x).resolve()) for x in p['protected_paths']):
        raise Denied('Protected control state')
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        try:
            info = current.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 0x400:
            raise Denied('Link or reparse point')
        if stat.S_ISREG(info.st_mode) and info.st_nlink != 1:
            raise Denied('Hardlink')
    if write and (p['role'] == 'reviewer' or not any(inside(path, Path(x).resolve()) for x in p['write_roots'])):
        raise Denied('Write not authorized')
    return path


PASSIVE = {'memory', 'session_search', 'session_read', 'todo', 'skills_list', 'skill_view'}
KANBAN = {'kanban_show', 'kanban_list', 'kanban_create', 'kanban_complete', 'kanban_block', 'kanban_comment',
          'kanban_request_review', 'kanban_request_changes', 'kanban_heartbeat', 'kanban_unblock', 'kanban_link', 'kanban_attachments'}


def decide(tool_name, args, p):
    if not isinstance(args, dict):
        raise Denied('Invalid arguments')
    if tool_name in {'read_file', 'write_file', 'patch', 'search_files'}:
        write = tool_name in {'write_file', 'patch'}
        path = checked_path(args.get('path', '.' if tool_name == 'search_files' else ''), p, write)
        if write and len(json.dumps(args)) > 1048576:
            raise Denied('Write too large')
        if tool_name == 'search_files' and path.is_dir():
            # Stock recursive search must not encounter any private/link target.
            # Reject broad trees; users can search a safe narrower directory.
            count = 0
            for base, dirs, files in os.walk(path, followlinks=False):
                for name in dirs + files:
                    checked_path(str(Path(base) / name), p)
                    count += 1
                    if count > 20000:
                        raise Denied('Search scope too large')
        return {'action': 'modify', 'args': {'path': str(path)}}
    if tool_name == 'terminal':
        # No shell interpretation of model-supplied text beyond these literals.
        allowed = {'pwd', 'uname -s', 'git --no-pager -c core.fsmonitor=false -c core.untrackedCache=false status --short', 'git --no-pager rev-parse HEAD', 'git --no-pager branch --show-current'}
        if args.get('command') not in allowed or set(args) - {'command', 'workdir', 'timeout'}:
            raise Denied('Arbitrary terminal command denied')
        workdir = checked_path(args.get('workdir', p['workspace']), p)
        if workdir not in read_roots(p):
            raise Denied('Terminal must use an approved root')
        return {'action': 'modify', 'args': {'workdir': str(workdir)}}
    if tool_name in PASSIVE:
        return None
    if tool_name == 'delegate_task':
        if p['role'] == 'reviewer':
            raise Denied('Reviewer cannot delegate authority')
        return None
    if tool_name in KANBAN:
        if args.get('board', p['board']) != p['board'] or args.get('artifacts'):
            raise Denied('Foreign board or unchecked attachment')
        return {'action': 'modify', 'args': {'board': p['board']}}
    if tool_name in {'aphrael_verify_file', 'aphrael_verification_status'}:
        if tool_name == 'aphrael_verify_file' and p['role'] != 'reviewer':
            raise Denied('Only reviewer may observe verification')
        return None
    raise Denied('Tool is outside approved capability surface')


def pre_tool_call(tool_name='', args=None, profile_name=None, **kwargs):
    try:
        return decide(tool_name, args, policy(profile_name))
    except BaseException:
        # Hermes skips Python callback exceptions: never let one escape.
        return {'action': 'block', 'message': 'Aphrael policy denied the operation or could not validate its controls.'}


def observe(args, verify=False, profile_name=None):
    try:
        p = policy(profile_name)
        if set(args) != {'task_id', 'request_id'}:
            raise Denied('Exact request identity required')
        if not all(isinstance(v, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,128}', v) for v in args.values()):
            raise Denied('Invalid identity')
        root = Path(p['evidence_root'])
        spec_bytes = (root / 'requests' / (args['request_id'] + '.json')).read_bytes()
        spec = json.loads(spec_bytes)
        if any(spec.get(k) != v for k, v in args.items()) or spec.get('board') != p['board']:
            raise Denied('Request/task/board mismatch')
        path = checked_path(spec['path'], p, profile_name=profile_name)
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        digest = hashlib.sha256(spec_bytes).hexdigest()
        record_path = root / 'observations' / (args['request_id'] + '.json')
        if verify:
            if p['role'] != 'reviewer':
                raise Denied('Independent reviewer required')
            record = {**args, 'board': p['board'], 'spec_sha256': digest, 'observed_sha256': observed,
                      'verified': observed == spec['sha256'], 'observed_at': datetime.now(timezone.utc).isoformat(),
                      'authority': 'aphrael-reviewer-file-observation', 'lifecycle_done_is_verification': False}
            record_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = record_path.with_suffix('.tmp')
            tmp.write_text(json.dumps(record), encoding='utf-8')
            tmp.replace(record_path)
            return json.dumps(record)
        record = json.loads(record_path.read_text(encoding='utf-8'))
        valid = (record.get('verified') is True and record.get('spec_sha256') == digest and
                 record.get('observed_sha256') == observed == spec['sha256'] and
                 all(record.get(k) == v for k, v in args.items()) and record.get('board') == p['board'])
        return json.dumps({**args, 'verified': valid, 'lifecycle_done_is_verification': False})
    except Exception:
        return json.dumps({'verified': False, 'error': 'No valid independent observation for this trusted request; missing, failed, changed, or denied.'})


if __name__ == '__main__':
    try:
        payload = json.load(sys.stdin)
        result = pre_tool_call(payload.get('tool_name', ''), payload.get('tool_input'), profile_name=payload.get('profile'))
        print(json.dumps(result or {}))
    except BaseException:
        print(json.dumps({'action': 'block', 'message': 'Aphrael policy hook failed closed.'}))
        sys.exit(1)
