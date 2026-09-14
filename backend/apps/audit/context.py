from contextlib import contextmanager
from contextvars import ContextVar


_current_actor = ContextVar("audit_actor", default=None)
_current_request_metadata = ContextVar(
    "audit_request_metadata",
    default=None,
)


def get_current_actor():
    return _current_actor.get()


def get_current_request_metadata() -> dict:
    return _current_request_metadata.get() or {}


@contextmanager
def audit_context(*, actor=None, metadata=None):
    actor_token = _current_actor.set(actor)
    metadata_token = _current_request_metadata.set(metadata or {})

    try:
        yield
    finally:
        _current_actor.reset(actor_token)
        _current_request_metadata.reset(metadata_token)
