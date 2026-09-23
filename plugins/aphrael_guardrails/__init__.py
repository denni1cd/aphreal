"""Supported Hermes native plugin registration; no internal Hermes imports."""
import json

from .guard import observe, pre_tool_call
from . import work_bridge


def register(ctx):
    profile_name = ctx.profile_name

    def policy_hook(tool_name='', args=None, **kwargs):
        return pre_tool_call(tool_name, args, profile_name=profile_name, **kwargs)

    ctx.register_hook('pre_tool_call', policy_hook)
    for name, verify in [('aphrael_verify_file', True), ('aphrael_verification_status', False)]:
        schema = {'name': name, 'description': (
            'Independently read and hash a file against an externally authorized request. Reviewer only.' if verify else
            'Check independent file evidence against current bytes. Kanban done is not verification.'),
            'parameters': {'type': 'object', 'properties': {
                'task_id': {'type': 'string'}, 'request_id': {'type': 'string'}},
                'required': ['task_id', 'request_id'], 'additionalProperties': False}}
        def handler(args, _verify=verify, **kwargs):
            return observe(args, verify=_verify, profile_name=profile_name)
        ctx.register_tool(name=name, toolset='aphrael_guardrails', schema=schema, handler=handler)

    work_tools = [
        ('aphrael_work_delegate',
         'Delegate an authorized natural-language repository task to ChatGPT Work through a GitHub PR.',
         {'instruction': {'type': 'string'}, 'base': {'type': 'string'}}, ['instruction']),
        ('aphrael_work_status',
         'Verify the durable GitHub result for an existing Aphrael Work request.',
         {'request_id': {'type': 'string'}}, ['request_id']),
        ('aphrael_work_recall',
         'Recall a durable completed and verified Work result without rerunning the task.',
         {'request_id': {'type': 'string'}}, []),
        ('aphrael_work_recent',
         'List recent Work handoffs and their exact request IDs; status is last observed, not live.',
         {'limit': {'type': 'integer', 'minimum': 1, 'maximum': 50}}, []),
    ]
    for name, description, properties, required in work_tools:
        schema = {'name': name, 'description': description,
                  'parameters': {'type': 'object', 'properties': properties,
                                 'required': required, 'additionalProperties': False}}

        def work_handler(args, _name=name, **kwargs):
            try:
                if _name == 'aphrael_work_delegate':
                    record = work_bridge.delegate_to_work(args['instruction'], args.get('base', work_bridge.BASE))
                    output = {key: record[key] for key in ('request_id', 'pr_url', 'status', 'base')}
                elif _name == 'aphrael_work_status':
                    record = work_bridge.check(args['request_id'])
                    output = {key: record[key] for key in ('request_id', 'status')}
                    for key in ('detail', 'result', 'pr_url', 'result_comment_url'):
                        if key in record:
                            output[key] = record[key]
                elif _name == 'aphrael_work_recent':
                    output = {'status': 'ok', 'requests': work_bridge.recent(args.get('limit', 10))}
                else:
                    record = work_bridge.recall(args.get('request_id'))
                    output = {key: record[key] for key in ('request_id', 'status', 'result', 'pr_url')}
                    if 'result_comment_url' in record:
                        output['result_comment_url'] = record['result_comment_url']
                return json.dumps(output)
            except Exception as exc:
                return json.dumps({'status': 'failed', 'detail': str(exc)})

        ctx.register_tool(name=name, toolset='aphrael_guardrails', schema=schema, handler=work_handler)
