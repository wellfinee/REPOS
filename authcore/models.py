import uuid
from django.db import models
from django.utils import timezone


class RefreshToken(models.Model):
    """
    Храним refresh по jti (id токена). Это даёт revoke/rotation.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    jti = models.UUIDField(unique=True, db_index=True)

    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    revoked_at = models.DateTimeField(null=True, blank=True)
    replaced_by_jti = models.UUIDField(null=True, blank=True)
    is_persistent = models.BooleanField(default=False)

    class Meta:
        db_table = "refresh_tokens"

    @property
    def is_active(self):
        return self.revoked_at is None and self.expires_at > timezone.now()