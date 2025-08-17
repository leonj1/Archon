"""
Settings Repository Interface

Interface for settings and credentials management including encryption,
categories, and secure storage operations.
"""

from abc import abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from .base_repository import BaseRepository


class SettingEntity:
    """Setting entity representation."""
    
    def __init__(
        self,
        id: str,
        key: str,
        value: Optional[str] = None,
        encrypted_value: Optional[str] = None,
        is_encrypted: bool = False,
        category: Optional[str] = None,
        description: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.key = key
        self.value = value
        self.encrypted_value = encrypted_value
        self.is_encrypted = is_encrypted
        self.category = category
        self.description = description
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """
        Convert entity to dictionary.
        
        Args:
            include_sensitive: Whether to include encrypted values
        """
        data = {
            "id": self.id,
            "key": self.key,
            "value": self.value if not self.is_encrypted else None,
            "is_encrypted": self.is_encrypted,
            "category": self.category,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        
        if include_sensitive:
            data["encrypted_value"] = self.encrypted_value
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SettingEntity":
        """Create entity from dictionary."""
        return cls(**data)
    
    def get_actual_value(self, decryptor=None) -> Optional[str]:
        """
        Get the actual value, decrypting if necessary.
        
        Args:
            decryptor: Function to decrypt encrypted values
            
        Returns:
            The actual value or None if encrypted and no decryptor provided
        """
        if not self.is_encrypted:
            return self.value
        
        if decryptor and self.encrypted_value:
            try:
                return decryptor(self.encrypted_value)
            except Exception:
                return None
        
        return None


class ISettingsRepository(BaseRepository[SettingEntity]):
    """
    Interface for settings repository operations.
    Extends BaseRepository with settings-specific functionality.
    """
    
    @abstractmethod
    async def get_by_key(self, key: str) -> Optional[SettingEntity]:
        """
        Get setting by key.
        
        Args:
            key: Setting key
            
        Returns:
            Setting entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_category(self, category: str) -> List[SettingEntity]:
        """
        Get all settings in a specific category.
        
        Args:
            category: Category name
            
        Returns:
            List of settings in the category
        """
        pass
    
    @abstractmethod
    async def get_encrypted_settings(self) -> List[SettingEntity]:
        """
        Get all encrypted settings.
        
        Returns:
            List of encrypted settings
        """
        pass
    
    @abstractmethod
    async def get_unencrypted_settings(self) -> List[SettingEntity]:
        """
        Get all unencrypted settings.
        
        Returns:
            List of unencrypted settings
        """
        pass
    
    @abstractmethod
    async def set_value(
        self, 
        key: str, 
        value: str,
        category: Optional[str] = None,
        description: Optional[str] = None,
        encrypt: bool = False
    ) -> Optional[SettingEntity]:
        """
        Set a setting value (create or update).
        
        Args:
            key: Setting key
            value: Setting value
            category: Optional category
            description: Optional description
            encrypt: Whether to encrypt the value
            
        Returns:
            Setting entity or None if operation failed
        """
        pass
    
    @abstractmethod
    async def set_encrypted_value(
        self, 
        key: str, 
        encrypted_value: str,
        category: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[SettingEntity]:
        """
        Set an encrypted setting value.
        
        Args:
            key: Setting key
            encrypted_value: Pre-encrypted value
            category: Optional category
            description: Optional description
            
        Returns:
            Setting entity or None if operation failed
        """
        pass
    
    @abstractmethod
    async def update_value(self, key: str, value: str) -> Optional[SettingEntity]:
        """
        Update existing setting value.
        
        Args:
            key: Setting key
            value: New value
            
        Returns:
            Updated setting entity or None if update failed
        """
        pass
    
    @abstractmethod
    async def update_encrypted_value(
        self, 
        key: str, 
        encrypted_value: str
    ) -> Optional[SettingEntity]:
        """
        Update existing encrypted setting value.
        
        Args:
            key: Setting key
            encrypted_value: New encrypted value
            
        Returns:
            Updated setting entity or None if update failed
        """
        pass
    
    @abstractmethod
    async def delete_by_key(self, key: str) -> bool:
        """
        Delete setting by key.
        
        Args:
            key: Setting key
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def update_category(self, key: str, category: str) -> Optional[SettingEntity]:
        """
        Update setting category.
        
        Args:
            key: Setting key
            category: New category
            
        Returns:
            Updated setting entity or None if update failed
        """
        pass
    
    @abstractmethod
    async def update_description(self, key: str, description: str) -> Optional[SettingEntity]:
        """
        Update setting description.
        
        Args:
            key: Setting key
            description: New description
            
        Returns:
            Updated setting entity or None if update failed
        """
        pass
    
    @abstractmethod
    async def toggle_encryption(self, key: str, encrypt: bool) -> Optional[SettingEntity]:
        """
        Toggle encryption status for a setting.
        Note: This should handle encryption/decryption of the value.
        
        Args:
            key: Setting key
            encrypt: Whether to encrypt (True) or decrypt (False)
            
        Returns:
            Updated setting entity or None if operation failed
        """
        pass
    
    @abstractmethod
    async def get_categories(self) -> List[str]:
        """
        Get all unique categories.
        
        Returns:
            List of category names
        """
        pass
    
    @abstractmethod
    async def search_settings(
        self, 
        keyword: str,
        include_descriptions: bool = True
    ) -> List[SettingEntity]:
        """
        Search settings by keyword in key or description.
        
        Args:
            keyword: Search keyword
            include_descriptions: Whether to search in descriptions
            
        Returns:
            List of matching settings
        """
        pass
    
    @abstractmethod
    async def get_settings_summary(self) -> Dict[str, Any]:
        """
        Get summary of settings (counts by category, encryption status, etc.).
        
        Returns:
            Dictionary with settings summary
        """
        pass
    
    @abstractmethod
    async def bulk_update_category(
        self, 
        keys: List[str], 
        category: str
    ) -> int:
        """
        Update category for multiple settings.
        
        Args:
            keys: List of setting keys
            category: New category
            
        Returns:
            Number of settings successfully updated
        """
        pass
    
    @abstractmethod
    async def export_settings(
        self, 
        category: Optional[str] = None,
        include_encrypted: bool = False
    ) -> Dict[str, Any]:
        """
        Export settings for backup or migration.
        
        Args:
            category: Optional category filter
            include_encrypted: Whether to include encrypted values (dangerous!)
            
        Returns:
            Dictionary with exported settings
        """
        pass
    
    @abstractmethod
    async def import_settings(
        self, 
        settings_data: Dict[str, Any],
        overwrite_existing: bool = False
    ) -> int:
        """
        Import settings from exported data.
        
        Args:
            settings_data: Settings data to import
            overwrite_existing: Whether to overwrite existing settings
            
        Returns:
            Number of settings successfully imported
        """
        pass
    
    @abstractmethod
    async def validate_setting_key(self, key: str) -> bool:
        """
        Validate if a setting key is properly formatted.
        
        Args:
            key: Setting key to validate
            
        Returns:
            True if key is valid
        """
        pass
    
    @abstractmethod
    async def get_default_settings(self) -> Dict[str, Dict[str, Any]]:
        """
        Get default settings that should be created on first run.
        
        Returns:
            Dictionary of default settings with their properties
        """
        pass