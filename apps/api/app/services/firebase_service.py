import asyncio
import os
import json
import uuid
import firebase_admin
from firebase_admin import credentials, db
from app.core.config import get_settings

_initialized = False
_use_mock_db = False
_mock_db_path = "mock_db.json"
_mock_data: dict = {}


def _load_mock_db():
    global _mock_data
    if os.path.exists(_mock_db_path):
        try:
            with open(_mock_db_path, "r", encoding="utf-8") as f:
                _mock_data = json.load(f)
        except Exception:
            _mock_data = {}
    else:
        _mock_data = {}


def _save_mock_db():
    try:
        with open(_mock_db_path, "w", encoding="utf-8") as f:
            json.dump(_mock_data, f, indent=2)
    except Exception:
        pass


def _get_node(path: str):
    parts = [p for p in path.split("/") if p]
    curr = _mock_data
    for p in parts:
        if not isinstance(curr, dict):
            return None
        curr = curr.get(p)
    return curr


def _set_node(path: str, value):
    parts = [p for p in path.split("/") if p]
    if not parts:
        global _mock_data
        _mock_data = value
        _save_mock_db()
        return
    curr = _mock_data
    for p in parts[:-1]:
        if p not in curr or not isinstance(curr[p], dict):
            curr[p] = {}
        curr = curr[p]
    curr[parts[-1]] = value
    _save_mock_db()


def _update_node(path: str, value: dict):
    parts = [p for p in path.split("/") if p]
    if not parts:
        return
    curr = _mock_data
    for p in parts[:-1]:
        if p not in curr or not isinstance(curr[p], dict):
            curr[p] = {}
        curr = curr[p]
    p_last = parts[-1]
    if p_last not in curr or not isinstance(curr[p_last], dict):
        curr[p_last] = {}
    curr[p_last].update(value)
    _save_mock_db()


def _push_node(path: str, value: dict) -> str:
    new_key = str(uuid.uuid4()).replace("-", "")[:16]
    parts = [p for p in path.split("/") if p]
    curr = _mock_data
    for p in parts:
        if p not in curr or not isinstance(curr[p], dict):
            curr[p] = {}
        curr = curr[p]
    if not isinstance(curr, dict):
        _set_node(path, {})
        curr = _get_node(path)
    curr[new_key] = value
    _save_mock_db()
    return new_key


def init_firebase() -> None:
    global _initialized, _use_mock_db
    if _initialized:
        return
    s = get_settings()
    if not s.firebase_db_url or (not s.firebase_service_account_json and not s.google_application_credentials):
        print("[Firebase] No Firebase credentials or URL provided. Falling back to Mock local JSON database.")
        _use_mock_db = True
        _load_mock_db()
        _initialized = True
        return

    try:
        if s.firebase_service_account_json:
            cred = credentials.Certificate(json.loads(s.firebase_service_account_json))
        else:
            cred = credentials.Certificate(s.google_application_credentials)
        firebase_admin.initialize_app(cred, {"databaseURL": s.firebase_db_url})
        print("[Firebase] Successfully initialized Firebase Admin SDK.")
    except Exception as exc:
        print(f"[Firebase] Failed to initialize Firebase Admin: {exc}. Falling back to Mock local JSON database.")
        _use_mock_db = True
        _load_mock_db()
    _initialized = True


# Realtime Database is synchronous in the Admin SDK; wrap in a thread to stay async-safe.
async def db_get(path: str):
    if _use_mock_db:
        return _get_node(path)
    return await asyncio.to_thread(lambda: db.reference(path).get())


async def db_set(path: str, value) -> None:
    if _use_mock_db:
        _set_node(path, value)
        return
    await asyncio.to_thread(lambda: db.reference(path).set(value))


async def db_update(path: str, value: dict) -> None:
    if _use_mock_db:
        _update_node(path, value)
        return
    await asyncio.to_thread(lambda: db.reference(path).update(value))


async def db_push(path: str, value: dict) -> str:
    if _use_mock_db:
        return _push_node(path, value)
    ref = await asyncio.to_thread(lambda: db.reference(path).push(value))
    return ref.key


def is_mock_db() -> bool:
    return _use_mock_db
