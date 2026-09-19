"""Supported Hermes native plugin registration; no internal Hermes imports."""
from .guard import observe, pre_tool_call


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
