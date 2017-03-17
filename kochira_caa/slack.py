"""
Slack compatibility hacks.

!sux slack
"""

from kochira.service import Service

service = Service(__name__, __doc__)

@service.hook("channel_message", priority=9999)
def eat_self_messages(ctx, target, origin, message):
    if origin.lower() == ctx.client.nickname.lower():
        return service.EAT

@service.hook("channel_message", priority=9999)
def eat_slack_generated_messages(ctx, target, origin, message):
    if message.startswith("@{} mentioned a file:".format(origin)):
        return service.EAT
