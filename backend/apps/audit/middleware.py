from apps.audit.context import audit_context


class AuditContextMiddleware:
    """
    Stores the authenticated user and limited request metadata in a
    ContextVar for the duration of the request.

    Do not put request bodies, cookies, authorization headers, or other
    secrets into the audit metadata.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)

        if not getattr(user, "is_authenticated", False):
            user = None

        user_agent = request.META.get("HTTP_USER_AGENT", "")

        metadata = {
            "method": request.method,
            "path": request.path,
            "remote_addr": request.META.get("REMOTE_ADDR", ""),
            "user_agent": user_agent[:500],
        }

        with audit_context(
            actor=user,
            metadata=metadata,
        ):
            return self.get_response(request)
