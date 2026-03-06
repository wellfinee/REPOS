# accounts/api/throttles.py
from rest_framework.throttling import SimpleRateThrottle

class LoginIdentifierThrottle(SimpleRateThrottle):
    scope = "login_user"

    def get_cache_key(self, request, view):
        # Только для POST логина
        if request.method != "POST":
            return None

        identifier = (request.data.get("identifier") or "").strip().lower()
        if not identifier:
            return None

        return self.cache_format % {
            "scope": self.scope,
            "ident": identifier,
        }

    @property
    def cache_format(self):
        # делаем отдельный неймспейс
        return "throttle_%(scope)s_%(ident)s"