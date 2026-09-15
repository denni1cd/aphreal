"""Install and check Aphrael assets using the official Hermes profile CLI.

Only distribution-owned files are backed up. This code never opens auth stores,
memories, sessions or credential files. It is setup automation, not an agent runtime.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone
import yaml

PIN = '49c6d4a9e0dddc64d6333c5b1fcc9d911463a8fd'
PROFILES = {'aphrael': 'parent', 'aphrael-worker': 'worker', 'aphrael-reviewer': 'reviewer', 'aphrael-dispatcher': 'parent'}

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)

def cli(root, *args, capture=False):
    env = os.environ.copy()
    env.update(HERMES_HOME=str(root), HERMES_KANBAN_HOME=str(root / 'aphrael-board'), HERMES_KANBAN_BOARD='aphrael', PYTHONIOENCODING='utf-8')
    env.pop('APHRAEL_POLICY_FILE', None)
    result = subprocess.run([sys.executable, '-m', 'hermes_cli.main', *args], env=env,
                            text=True, encoding='utf-8', capture_output=capture)
    if result.returncode:
        raise RuntimeError(f'Hermes {args[0]} failed (exit {result.returncode})')
    return result.stdout if capture else ''

def owned_paths(source):
    manifest = yaml.safe_load((source / 'distribution.yaml').read_text(encoding='utf-8'))
    owned = manifest.get('distribution_owned')
    if not owned:
        raise RuntimeError('An explicit distribution_owned allowlist is required')
    for rel in owned:
        if Path(rel).is_absolute() or '..' in Path(rel).parts or not (source / rel).exists():
            raise RuntimeError('Invalid or missing owned asset: ' + rel)
    return owned

def configure(root, source, name, role, workspace, model):
    profile = root / 'profiles' / name
    config_path = profile / 'config.yaml'
    config = yaml.safe_load(config_path.read_text(encoding='utf-8')) or {}
    # Keep user tuning but explicitly reconcile mandatory security controls.
    model_config = config.setdefault('model', {})
    model_config['provider'] = 'openai-codex'
    # Set the distribution default once.  Subsequent updates must keep a model
    # selected by the user or verified against their authenticated account.
    model_config.setdefault('default', model)
    config['fallback_providers'] = []
    config.setdefault('approvals', {}).update(mode='manual', cron_mode='deny', single_query_mode='deny', unattended_mode='deny')
    config.setdefault('plugins', {})['enabled'] = list(dict.fromkeys(config.get('plugins', {}).get('enabled', []) + ['aphrael_guardrails']))
    # Plugins are registered by Hermes from `plugins.enabled`; they are not
    # toolset identifiers. Remove the legacy entry before it becomes a silent
    # unknown-toolset warning in a profile preserved across updates.
    platform_toolsets = config.setdefault('platform_toolsets', {})
    cli_toolsets = platform_toolsets.get('cli', [])
    if isinstance(cli_toolsets, list):
        platform_toolsets['cli'] = [item for item in cli_toolsets if item != 'aphrael_guardrails']
    guard = profile / 'plugins' / 'aphrael_guardrails' / 'guard.py'
    command = f'"{Path(sys.executable).as_posix()}" "{guard.as_posix()}"'
    hooks = config.setdefault('hooks', {})
    pre = [x for x in hooks.get('pre_tool_call', []) if x.get('name') != 'aphrael-policy']
    pre.append({'name': 'aphrael-policy', 'command': command, 'timeout': 15, 'fail_closed': True})
    hooks['pre_tool_call'] = pre
    config['hooks_auto_accept'] = False
    config.setdefault('skills', {})['inline_shell'] = False
    config.setdefault('kanban', {}).update(dispatch_in_gateway=True, dispatch_interval_seconds=5, review_dispatch=True)
    config.setdefault('terminal', {}).update(backend='local', cwd=str(workspace))
    config.setdefault('delegation', {}).update(subagent_auto_approve=False, inherit_mcp_toolsets=False, fallback_providers=[])
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding='utf-8')
    env_path = profile / '.env'
    if not env_path.exists():
        env_path.write_text(
            '# Per-profile secrets for Aphrael. Do not commit this file.\n'
            '# OpenAI Codex OAuth is stored by Hermes, not here.\n',
            encoding='utf-8',
        )
    # Supported manual consent format; only approve this reviewed guard command.
    allow_path = profile / 'shell-hooks-allowlist.json'
    allow = json.loads(allow_path.read_text(encoding='utf-8')) if allow_path.exists() else {'approvals': []}
    pair = {'event': 'pre_tool_call', 'command': command}
    if pair not in allow['approvals']:
        allow['approvals'].append(pair)
    dump(allow_path, allow)
    policy = {'workspace': str(workspace), 'read_roots': [str(workspace), str(source)], 'write_roots': [str(workspace / 'output')],
              'protected_paths': [str(root), str(source / 'plugins'), str(source / 'scripts')],
              'role': role, 'evidence_root': str(root / 'aphrael-evidence'), 'board': 'aphrael'}
    dump(profile / 'aphrael-policy.json', policy)
    # Role is operational context, not a substitute for the policy above.
    if name != 'aphrael':
        soul = profile / 'SOUL.md'
        soul.write_text(soul.read_text(encoding='utf-8') + f'\nYou serve as Aphrael’s {role}. Keep your findings factual and concise.\n', encoding='utf-8')
    return profile

def check(root, source):
    if os.environ.get('HERMES_SAFE_MODE', '').lower() in ('1', 'true', 'yes'):
        raise RuntimeError('HERMES_SAFE_MODE disables required guardrails; normal Aphrael startup refused')
    board = root / 'aphrael-board' / 'kanban' / 'boards' / 'aphrael'
    if not (board / 'board.json').exists():
        raise RuntimeError('Aphrael board missing; run SETUP_APHRAEL.ps1')
    for name, role in PROFILES.items():
        p = root / 'profiles' / name
        if (p / 'aphrael-update-in-progress').exists():
            raise RuntimeError('Interrupted profile update; run setup to restore the owned-file backup')
        config = yaml.safe_load((p / 'config.yaml').read_text(encoding='utf-8'))
        if not (p / '.env').is_file():
            raise RuntimeError('Profile .env bootstrap file missing; run setup to restore it')
        policy = json.loads((p / 'aphrael-policy.json').read_text(encoding='utf-8'))
        if policy['role'] != role or policy['board'] != 'aphrael':
            raise RuntimeError('Aphrael policy role/board mismatch')
        guard = p / 'plugins' / 'aphrael_guardrails' / 'guard.py'
        if not guard.is_file() or 'aphrael_guardrails' not in config.get('plugins', {}).get('enabled', []):
            raise RuntimeError('Required Aphrael plugin absent or disabled')
        hooks = config.get('hooks', {}).get('pre_tool_call', [])
        expected = f'"{Path(sys.executable).as_posix()}" "{guard.as_posix()}"'
        if not any(h.get('command') == expected and h.get('fail_closed') is True for h in hooks):
            raise RuntimeError('Required fail-closed Aphrael policy hook missing')
        consent = json.loads((p / 'shell-hooks-allowlist.json').read_text(encoding='utf-8'))
        if not any(a.get('event') == 'pre_tool_call' and a.get('command') == expected for a in consent['approvals']):
            raise RuntimeError('Required policy hook consent missing')
        approvals = config.get('approvals', {})
        if approvals.get('mode') != 'manual' or any(approvals.get(k) != 'deny' for k in ('cron_mode', 'single_query_mode', 'unattended_mode')):
            raise RuntimeError('Required approval settings changed; run setup to reconcile')
        if config.get('fallback_providers') or config.get('model', {}).get('provider') != 'openai-codex':
            raise RuntimeError('Unexpected provider/fallback configuration')
        if config.get('skills', {}).get('inline_shell') is not False:
            raise RuntimeError('Skill inline shell must remain disabled')
    print('Aphrael profile checks passed: four isolated homes, pinned board, required policy and approvals.')

def safe_remove(path, profile):
    path = path.resolve()
    if path == profile or profile not in path.parents:
        raise RuntimeError('Refusing to remove a path outside the owned profile')
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def restore_interrupted(profile):
    marker = profile / 'aphrael-update-in-progress'
    if not marker.exists():
        return
    backup = Path(marker.read_text(encoding='utf-8').strip())
    manifest = backup / 'restore.json'
    if not manifest.is_file():
        raise RuntimeError('Interrupted profile update has no valid Aphrael backup')
    record = json.loads(manifest.read_text(encoding='utf-8'))
    if Path(record.get('profile', '')).resolve() != profile.resolve():
        raise RuntimeError('Interrupted profile update backup targets another profile')
    for rel in record.get('paths', []):
        target = profile / rel
        safe_remove(target, profile)
        prior = backup / rel
        if prior.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(prior, target) if prior.is_dir() else shutil.copy2(prior, target)
    marker.unlink()

def install(root, source, workspace, model):
    if source == root or source in root.parents or source == workspace or source in workspace.parents:
        raise RuntimeError('Runtime and writable workspace must be outside the source checkout')
    owned = owned_paths(source)
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / 'output').mkdir(exist_ok=True)
    for sub in ('requests', 'observations'):
        (root / 'aphrael-evidence' / sub).mkdir(parents=True, exist_ok=True)
    board_root = root / 'aphrael-board'
    if not (board_root / 'kanban' / 'boards' / 'aphrael' / 'board.json').exists():
        cli(root, 'kanban', 'boards', 'create', 'aphrael', '--name', 'Aphrael', '--default-workdir', str(workspace))
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')
    for name, role in PROFILES.items():
        profile = root / 'profiles' / name
        restore_interrupted(profile)
        existing = (profile / 'distribution.yaml').exists()
        backup = root / 'aphrael-backups' / stamp / name
        paths = list(dict.fromkeys(owned + ['config.yaml', 'aphrael-policy.json', 'shell-hooks-allowlist.json']))
        if existing:
            for rel in paths:
                item = profile / rel
                if item.exists():
                    dest = backup / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copytree(item, dest) if item.is_dir() else shutil.copy2(item, dest)
            dump(backup / 'restore.json', {'paths': paths, 'profile': str(profile)})
            (profile / 'aphrael-update-in-progress').write_text(str(backup), encoding='utf-8')
        try:
            if existing:
                cli(root, 'profile', 'update', name, '--yes')
            else:
                cli(root, 'profile', 'install', str(source), '--name', name, '--yes')
            configure(root, source, name, role, workspace, model)
        except BaseException:
            if existing:
                for rel in paths:
                    safe_remove(profile / rel, profile)
                    old = backup / rel
                    if old.exists():
                        dest = profile / rel
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copytree(old, dest) if old.is_dir() else shutil.copy2(old, dest)
                (profile / 'aphrael-update-in-progress').unlink(missing_ok=True)
            raise
        (profile / 'aphrael-update-in-progress').unlink(missing_ok=True)
    check(root, source)
    dump(Path.home() / '.aphrael' / 'installation.json', {'root': str(root), 'source': str(source), 'workspace': str(workspace), 'python': sys.executable, 'hermes_commit': PIN})

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['install', 'check'])
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--workspace', type=Path, default=Path.home() / 'AphraelWorkspace')
    parser.add_argument('--model', default='gpt-5.5')
    args = parser.parse_args()
    root, source = args.root.resolve(), args.source.resolve()
    if args.action == 'check':
        check(root, source)
    else:
        install(root, source, args.workspace.resolve(), args.model)

if __name__ == '__main__':
    main()
