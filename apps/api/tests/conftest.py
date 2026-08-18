import sys
import types


class _Dummy:
    def __init__(self, *a, **k):
        pass


def _module(name: str, **attrs) -> types.ModuleType:
    m = types.ModuleType(name)
    for k, v in attrs.items():
        setattr(m, k, v)
    sys.modules[name] = m
    return m


# valkey-glide
_module("glide", GlideClient=_Dummy, GlideClientConfiguration=_Dummy, NodeAddress=_Dummy)


# firebase-admin (not used by the pure-logic modules, stubbed for safety)
_module("firebase_admin", initialize_app=lambda *a, **k: None, get_app=lambda *a, **k: None, _apps=[])
_module("firebase_admin.credentials", Certificate=_Dummy)
_module("firebase_admin.db", reference=lambda *a, **k: _Dummy())
_module("firebase_admin.auth", verify_id_token=lambda *a, **k: {"uid": "test"})
