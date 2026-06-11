"""Custom model fields shared across apps."""

from __future__ import annotations

import base64
import hashlib
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import models


def medical_data_fernet() -> Fernet:
    """Return a Fernet instance for medical data encryption."""
    configured_key = getattr(settings, "MEDICAL_DATA_FERNET_KEY", None)
    if configured_key:
        return Fernet(configured_key.encode())
    digest = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


class EncryptedTextField(models.TextField):
    """TextField that encrypts values before database persistence."""

    prefix = "enc$"

    def get_prep_value(self, value: Any) -> str:
        """Encrypt plaintext before writing to the database."""
        prepared_value = super().get_prep_value(value)
        if prepared_value in (None, ""):
            return ""
        if isinstance(prepared_value, str) and prepared_value.startswith(self.prefix):
            return prepared_value
        token = medical_data_fernet().encrypt(str(prepared_value).encode()).decode()
        return f"{self.prefix}{token}"

    def from_db_value(self, value: Any, _expression: Any, _connection: Any) -> str:
        """Decrypt ciphertext after reading from the database."""
        return self._decrypt(value)

    def to_python(self, value: Any) -> str:
        """Normalize encrypted or plain input to Python text."""
        value = super().to_python(value)
        return self._decrypt(value)

    def _decrypt(self, value: Any) -> str:
        """Return plaintext for an encrypted value."""
        if value in (None, ""):
            return ""
        text = str(value)
        if not text.startswith(self.prefix):
            return text
        token = text.removeprefix(self.prefix)
        try:
            return medical_data_fernet().decrypt(token.encode()).decode()
        except InvalidToken:
            return ""
