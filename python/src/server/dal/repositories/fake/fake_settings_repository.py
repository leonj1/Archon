"""
Fake in-memory implementation of SettingsRepository for testing.
"""
import threading
import base64
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from cryptography.fernet import Fernet

from ..interfaces.settings_repository import SettingsRepository
from ...models.settings import Setting


class FakeSettingsRepository(SettingsRepository):
    """In-memory implementation of SettingsRepository for testing."""
    
    def __init__(self):
        self._settings: Dict[str, Setting] = {}
        self._lock = threading.RLock()
        # Generate a test encryption key
        self._encryption_key = Fernet.generate_key()
        self._fernet = Fernet(self._encryption_key)

    def _encrypt_value(self, value: str) -> str:
        """Encrypt a sensitive value."""
        try:
            encrypted_bytes = self._fernet.encrypt(value.encode())
            return base64.b64encode(encrypted_bytes).decode()
        except Exception:
            # If encryption fails, return the value as-is for testing
            return value

    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a sensitive value."""
        try:
            encrypted_bytes = base64.b64decode(encrypted_value.encode())
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception:
            # If decryption fails, return the value as-is for testing
            return encrypted_value

    async def get_setting(self, key: str) -> Optional[Setting]:
        """Get a setting by key."""
        with self._lock:
            setting = self._settings.get(key)
            if setting and setting.is_encrypted and setting.value:
                # Return decrypted copy
                decrypted_setting = Setting(
                    key=setting.key,
                    value=self._decrypt_value(setting.value),
                    is_encrypted=setting.is_encrypted,
                    description=setting.description,
                    metadata=setting.metadata,
                    created_at=setting.created_at,
                    updated_at=setting.updated_at
                )
                return decrypted_setting
            return setting

    async def set_setting(
        self,
        key: str,
        value: str,
        is_encrypted: bool = False,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Setting:
        """Set a setting value."""
        with self._lock:
            now = datetime.now(timezone.utc)
            
            # Encrypt value if needed
            stored_value = self._encrypt_value(value) if is_encrypted else value
            
            existing_setting = self._settings.get(key)
            if existing_setting:
                # Update existing setting
                existing_setting.value = stored_value
                existing_setting.is_encrypted = is_encrypted
                if description is not None:
                    existing_setting.description = description
                if metadata is not None:
                    existing_setting.metadata = metadata
                existing_setting.updated_at = now
                setting = existing_setting
            else:
                # Create new setting
                setting = Setting(
                    key=key,
                    value=stored_value,
                    is_encrypted=is_encrypted,
                    description=description,
                    metadata=metadata or {},
                    created_at=now,
                    updated_at=now
                )
                self._settings[key] = setting
            
            # Return setting with decrypted value if encrypted
            if is_encrypted:
                return Setting(
                    key=setting.key,
                    value=value,  # Return original unencrypted value
                    is_encrypted=setting.is_encrypted,
                    description=setting.description,
                    metadata=setting.metadata,
                    created_at=setting.created_at,
                    updated_at=setting.updated_at
                )
            return setting

    async def delete_setting(self, key: str) -> bool:
        """Delete a setting."""
        with self._lock:
            if key in self._settings:
                del self._settings[key]
                return True
            return False

    async def list_settings(
        self,
        prefix: Optional[str] = None,
        include_encrypted: bool = True
    ) -> List[Setting]:
        """List settings with optional filtering."""
        with self._lock:
            settings = []
            
            for setting in self._settings.values():
                # Apply prefix filter
                if prefix and not setting.key.startswith(prefix):
                    continue
                
                # Apply encryption filter
                if not include_encrypted and setting.is_encrypted:
                    continue
                
                # Decrypt if needed
                if setting.is_encrypted and setting.value:
                    decrypted_setting = Setting(
                        key=setting.key,
                        value=self._decrypt_value(setting.value),
                        is_encrypted=setting.is_encrypted,
                        description=setting.description,
                        metadata=setting.metadata,
                        created_at=setting.created_at,
                        updated_at=setting.updated_at
                    )
                    settings.append(decrypted_setting)
                else:
                    settings.append(setting)
            
            # Sort by key
            settings.sort(key=lambda s: s.key)
            return settings

    async def get_settings_by_prefix(self, prefix: str) -> Dict[str, str]:
        """Get settings as a key-value dict filtered by prefix."""
        settings = await self.list_settings(prefix=prefix)
        return {s.key: s.value or "" for s in settings}

    async def bulk_set_settings(
        self,
        settings: Dict[str, tuple[str, bool]]
    ) -> List[Setting]:
        """Set multiple settings at once."""
        result_settings = []
        
        for key, (value, is_encrypted) in settings.items():
            setting = await self.set_setting(key, value, is_encrypted)
            result_settings.append(setting)
        
        return result_settings

    async def setting_exists(self, key: str) -> bool:
        """Check if a setting exists."""
        with self._lock:
            return key in self._settings

    async def get_setting_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get just the metadata for a setting."""
        with self._lock:
            setting = self._settings.get(key)
            return setting.metadata if setting else None

    async def update_setting_metadata(
        self,
        key: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Update just the metadata for a setting."""
        with self._lock:
            setting = self._settings.get(key)
            if not setting:
                return False
            
            setting.metadata = metadata
            setting.updated_at = datetime.now(timezone.utc)
            return True

    # Common setting operations
    async def get_api_key(self, provider: str) -> Optional[str]:
        """Get an API key for a provider."""
        setting = await self.get_setting(f"api_key_{provider}")
        return setting.value if setting else None

    async def set_api_key(self, provider: str, api_key: str) -> bool:
        """Set an API key for a provider."""
        await self.set_setting(
            f"api_key_{provider}",
            api_key,
            is_encrypted=True,
            description=f"API key for {provider}"
        )
        return True

    async def get_feature_flag(self, flag_name: str) -> bool:
        """Get a feature flag value."""
        setting = await self.get_setting(f"feature_{flag_name}")
        if not setting:
            return False
        return setting.value.lower() in ("true", "1", "yes", "on")

    async def set_feature_flag(self, flag_name: str, enabled: bool) -> bool:
        """Set a feature flag value."""
        await self.set_setting(
            f"feature_{flag_name}",
            "true" if enabled else "false",
            description=f"Feature flag for {flag_name}"
        )
        return True

    async def get_user_preference(self, pref_name: str) -> Optional[str]:
        """Get a user preference."""
        setting = await self.get_setting(f"pref_{pref_name}")
        return setting.value if setting else None

    async def set_user_preference(self, pref_name: str, value: str) -> bool:
        """Set a user preference."""
        await self.set_setting(
            f"pref_{pref_name}",
            value,
            description=f"User preference for {pref_name}"
        )
        return True

    # Configuration management
    async def get_config_section(self, section: str) -> Dict[str, str]:
        """Get all settings for a configuration section."""
        return await self.get_settings_by_prefix(f"config_{section}_")

    async def set_config_section(
        self,
        section: str,
        config: Dict[str, str]
    ) -> bool:
        """Set all settings for a configuration section."""
        settings_to_set = {}
        for key, value in config.items():
            full_key = f"config_{section}_{key}"
            settings_to_set[full_key] = (value, False)
        
        await self.bulk_set_settings(settings_to_set)
        return True

    # JSON value helpers
    async def get_json_setting(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a setting value as parsed JSON."""
        setting = await self.get_setting(key)
        if not setting or not setting.value:
            return None
        
        try:
            return json.loads(setting.value)
        except json.JSONDecodeError:
            return None

    async def set_json_setting(
        self,
        key: str,
        value: Dict[str, Any],
        description: Optional[str] = None
    ) -> bool:
        """Set a setting value as JSON."""
        json_value = json.dumps(value, separators=(',', ':'))
        await self.set_setting(key, json_value, description=description)
        return True

    # Test utility methods
    def clear_all(self) -> None:
        """Clear all settings (for testing)."""
        with self._lock:
            self._settings.clear()

    def get_all_settings(self) -> List[Setting]:
        """Get all settings with encrypted values (for testing)."""
        with self._lock:
            return list(self._settings.values())

    def get_encryption_key(self) -> bytes:
        """Get the encryption key (for testing)."""
        return self._encryption_key

    def count_settings(self) -> int:
        """Count total settings (for testing)."""
        with self._lock:
            return len(self._settings)

    def count_encrypted_settings(self) -> int:
        """Count encrypted settings (for testing)."""
        with self._lock:
            return len([s for s in self._settings.values() if s.is_encrypted])