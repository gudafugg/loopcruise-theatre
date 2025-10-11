

# -*- coding: utf-8 -*-
"""
SSE endpoints (agent-agnostic)
- GET  /api/v1/stream/sse?session_id=...   : Server-Sent Events stream
- POST /api/v1/stream/start                : Create a session_id (no agent needed)
This module is self-contained: it ships a minimal in-memory SSE hub
so you can verify the front-end EventSource without wiring agents yet.
"""

from __future__ import annotations

import asyncio
import json
from typing import Dict, Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse

router = APIRouter()


# ------------------------------
# Minimal in-memory SSE Hub
# ------------------------------
class _SSEHub:
    """A very small, per-process hub that keeps an asyncio.Queue
    for each session_id. This is intentionally simple so we can
    test SSE end-to-end before integrating agents/engine.
    """

    def __init__(self) -> None:
        self._queues: Dict[str, asyncio.Queue] = {}
        self._locks: Dict[str, asyncio.Lock] = {}

    def create_session(self, session_id: str) -> str:
        if session_id not in self._queues:
            self._queues[session_id] = asyncio.Queue()
            self._locks[session_id] = asyncio.Lock()
        return session_id

    def has_session(self, session_id: str) -> bool:
        return session_id in self._queues

    def get_queue(self, session_id: str) -> Optional[asyncio.Queue]:
        return self._queues.get(session_id)

    async def publish(self, session_id: str, event: dict) -> None:
        """Publish an event to a session stream."""
        q = self._queues.get(session_id)
        if not q:
            return
        # Ensure ordering within the same session
        lock = self._locks.setdefault(session_id, asyncio.Lock())
        async with lock:
            await q.put(event)

    def close(self, session_id: str) -> None:
        self._queues.pop(session_id, None)
        self._locks.pop(session_id, None)


_hub = _SSEHub()


def _format_sse(event: dict) -> str:
    """Format a dict as SSE frame. `event` should contain:
       - type: str
       - data: any (will be JSON-serialized)
    """
    ev_type = event.get("type") or "message"
    data = event.get("data")
    try:
        payload = json.dumps(data, ensure_ascii=False)
    except Exception:
        payload = json.dumps({"error": "non-serializable data"}, ensure_ascii=False)
    # Each event ends with a blank line
    return f"event: {ev_type}\n" f"data: {payload}\n\n"


# ------------------------------
# Public endpoints
# ------------------------------
@router.post("/start")
async def start_stream(req: dict) -> dict:
    """Create (or ensure) a session for SSE streaming.
    Returns a session_id. This does NOT start any agent;
    it's solely for wiring the transport layer.

    Body (optional):
    {
      "session_id": "sess_123",  # if omitted, we generate one
      "hello": true               # if true, send a test event after connect
    }
    """
    session_id = req.get("session_id") if isinstance(req, dict) else None
    hello = bool(req.get("hello")) if isinstance(req, dict) else False

    if not session_id:
        # lightweight unique id; good enough for local dev
        session_id = f"sess_{asyncio.get_running_loop().time():.6f}".replace(".", "")

    _hub.create_session(session_id)

    # Stash a hello flag in a side channel by publishing a status,
    # but only after the client has a chance to connect to /sse.
    if hello:
        async def _delayed_greet() -> None:
            await asyncio.sleep(0.1)
            await _hub.publish(session_id, {"type": "status", "data": "connected"})
        asyncio.create_task(_delayed_greet())

    return {"session_id": session_id}


@router.get("/sse")
async def sse(request: Request, session_id: str):
    """SSE stream endpoint.

    Client usage (JS):
        const es = new EventSource(`/api/v1/stream/sse?session_id=${sid}`);
        es.addEventListener('status', e => console.log('status:', e.data));
        es.addEventListener('npc',    e => console.log('npc:', e.data));
        es.addEventListener('done',   e => es.close());

    This endpoint is transport-only: it simply reads events from the session queue
    and forwards them as SSE frames. Other parts of the app can do:
        await _hub.publish(session_id, {"type":"npc","data":{"speaker_id":"dingqi","text":"..."}})
    """
    if not _hub.has_session(session_id):
        return JSONResponse({"error": "invalid session_id"}, status_code=400)

    queue = _hub.get_queue(session_id)

    async def event_generator():
        # Heartbeat interval to keep proxies from closing idle connections
        HEARTBEAT_SEC = 15
        while True:
            if await request.is_disconnected():
                break
            try:
                event = await asyncio.wait_for(queue.get(), timeout=HEARTBEAT_SEC)
                yield _format_sse(event)
            except asyncio.TimeoutError:
                # comment line as SSE heartbeat
                yield ":\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ------------------------------
# Helper endpoint for manual testing (optional)
# ------------------------------
@router.post("/emit")
async def emit(req: dict):
    """Manually push an event into a session (useful before agents are wired).

    Body:
    {
      "session_id": "sess_xxx",
      "type": "npc",
      "data": {"speaker_id":"dingqi","text":"你好，甲板的风很大。"}
    }
    """
    if not isinstance(req, dict):
        return JSONResponse({"error": "invalid body"}, status_code=400)

    session_id = req.get("session_id")
    ev_type = req.get("type") or "message"
    data = req.get("data") or {}

    if not session_id or not _hub.has_session(session_id):
        return JSONResponse({"error": "invalid session_id"}, status_code=400)

    await _hub.publish(session_id, {"type": ev_type, "data": data})
    return {"ok": True}