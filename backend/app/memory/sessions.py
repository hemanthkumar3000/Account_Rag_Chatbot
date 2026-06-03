# backend/app/memory/sessions.py

from typing import Dict, List

_SESSIONS: Dict[str, List[str]] = {}


def get_history(session_id: str, limit: int = 4) -> List[str]:
    history = _SESSIONS.get(session_id, [])
    return history[-limit:]


def append_to_history(session_id: str, user_msg: str, assistant_msg: str) -> None:
    history = _SESSIONS.get(session_id, [])
    history = history[-4:]
    history.append(f"User: {user_msg}")
    history.append(f"Assistant: {assistant_msg}")
    _SESSIONS[session_id] = history