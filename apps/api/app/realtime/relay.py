from __future__ import annotations
import asyncio
import json
from fastapi import Request
from glide import GlideClient, GlideClientConfiguration, NodeAddress
from app.core.config import get_settings


async def boardroom_stream(workspace_id: str, request: Request):
    """SSE generator. Subscribes a dedicated GLIDE client to the workspace's
    boardroom channel and relays each published message to the browser. Valkey
    never faces the public internet; the browser holds no datastore credentials.
    """
    s = get_settings()
    channel = f"boardroom:{workspace_id}"
    queue: asyncio.Queue = asyncio.Queue()

    def _on_message(msg, _context):
        queue.put_nowait(msg.message)

    config = GlideClientConfiguration(
        addresses=[NodeAddress(host=s.valkey_host, port=s.valkey_port)],
        use_tls=s.valkey_use_tls,
        pubsub_subscriptions=GlideClientConfiguration.PubSubSubscriptions(
            channels_and_patterns={
                GlideClientConfiguration.PubSubChannelModes.Exact: {channel}
            },
            callback=_on_message,
            context=None,
        ),
    )
    subscriber = None
    is_mock = False
    try:
        subscriber = await GlideClient.create(config)
    except Exception:
        from app.services.valkey_service import get_mock_client
        mock_client = get_mock_client()
        if channel not in mock_client._pubsub_queues:
            mock_client._pubsub_queues[channel] = []
        mock_client._pubsub_queues[channel].append(queue)
        is_mock = True

    try:
        while True:
            if await request.is_disconnected():
                break
            try:
                message = await asyncio.wait_for(queue.get(), timeout=15)
                data = message if isinstance(message, str) else json.dumps(message, default=str)
                yield {"event": "boardroom", "data": data}
            except asyncio.TimeoutError:
                yield {"event": "ping", "data": "keepalive"}
    finally:
        if subscriber is not None:
            await subscriber.close()
        elif is_mock:
            try:
                mock_client._pubsub_queues[channel].remove(queue)
            except Exception:
                pass
