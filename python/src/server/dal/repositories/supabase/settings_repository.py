"""
Supabase Settings Repository Implementation

Concrete implementation of settings repository for Supabase database backend.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json
import re

from ...interfaces import IDatabase, QueryResult
from ..interfaces.settings_repository_interface import ISettingsRepository, SettingEntity


class SupabaseSettingsRepository(ISettingsRepository):
    """
    Supabase implementation of settings repository.
    Handles settings CRUD operations for Supabase database backend.
    """
    
    def __init__(self, database: IDatabase, table_name: str = "settings"):
        """Initialize Supabase settings repository."""
        super().__init__(database, table_name)
    
    async def create(self, entity_data: Dict[str, Any]) -> Optional[SettingEntity]:
        """Create a new setting entity."""
        try:
            # Ensure required fields are present
            if "id" not in entity_data:
                entity_data["id"] = f"setting-{datetime.utcnow().strftime('%Y%m%d-%H%M%S-%f')[:20]}"
            
            # Set timestamps
            now = datetime.utcnow()
            entity_data.setdefault("created_at", now.isoformat())
            entity_data.setdefault("updated_at", now.isoformat())
            
            # Set defaults
            entity_data.setdefault("is_encrypted", False)
            
            result = await self._database.insert(self._table_name, entity_data)
            
            if result.success and result.data:
                return SettingEntity.from_dict(result.data[0])
            return None
            
        except Exception:
            return None
    
    async def get_by_id(self, entity_id: str) -> Optional[SettingEntity]:
        """Get setting entity by ID."""
        try:
            result = await self._database.select(
                self._table_name,
                filters={"id": entity_id}
            )
            
            if result.success and result.data:
                return SettingEntity.from_dict(result.data[0])
            return None
            
        except Exception:
            return None
    
    async def update(self, entity_id: str, update_data: Dict[str, Any]) -> Optional[SettingEntity]:
        """Update an existing setting entity."""
        try:
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self._database.update(
                self._table_name,
                update_data,
                filters={"id": entity_id}
            )
            
            if result.success and result.data:
                return SettingEntity.from_dict(result.data[0])
            return None
            
        except Exception:
            return None
    
    async def delete(self, entity_id: str) -> bool:
        """Delete a setting entity by ID."""
        try:
            result = await self._database.delete(
                self._table_name,
                filters={"id": entity_id}
            )
            return result.success and result.affected_rows > 0
        except Exception:
            return False
    
    async def list_all(
        self, 
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[SettingEntity]:
        """List all setting entities."""
        try:
            result = await self._database.select(
                self._table_name,
                order_by=order_by or "key ASC",
                limit=limit,
                offset=offset
            )
            
            if result.success:
                return [SettingEntity.from_dict(row) for row in result.data]
            return []
            
        except Exception:
            return []
    
    async def find_by_criteria(
        self, 
        criteria: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[SettingEntity]:
        """Find setting entities matching criteria."""
        try:
            result = await self._database.select(
                self._table_name,
                filters=criteria,
                order_by=order_by or "key ASC",
                limit=limit,
                offset=offset
            )
            
            if result.success:
                return [SettingEntity.from_dict(row) for row in result.data]
            return []
            
        except Exception:
            return []
    
    async def count(self, criteria: Optional[Dict[str, Any]] = None) -> int:
        """Count setting entities."""
        try:
            return await self._database.count(self._table_name, criteria)
        except Exception:
            return 0
    
    async def exists(self, entity_id: str) -> bool:
        """Check if setting entity exists."""
        try:
            return await self._database.exists(self._table_name, {"id": entity_id})
        except Exception:
            return False
    
    # Settings-specific methods
    
    async def get_by_key(self, key: str) -> Optional[SettingEntity]:
        """Get setting by key."""
        try:
            result = await self._database.select(
                self._table_name,
                filters={"key": key}
            )
            
            if result.success and result.data:
                return SettingEntity.from_dict(result.data[0])
            return None
            
        except Exception:
            return None
    
    async def get_by_category(self, category: str) -> List[SettingEntity]:
        """Get all settings in a specific category."""
        try:
            return await self.find_by_criteria(
                {"category": category},
                order_by="key ASC"
            )
        except Exception:
            return []
    
    async def get_encrypted_settings(self) -> List[SettingEntity]:
        """Get all encrypted settings."""
        try:
            return await self.find_by_criteria(
                {"is_encrypted": True},
                order_by="key ASC"
            )
        except Exception:
            return []
    
    async def get_unencrypted_settings(self) -> List[SettingEntity]:
        """Get all unencrypted settings."""
        try:
            return await self.find_by_criteria(
                {"is_encrypted": False},
                order_by="key ASC"
            )
        except Exception:
            return []
    
    async def set_value(
        self, 
        key: str, 
        value: str,
        category: Optional[str] = None,
        description: Optional[str] = None,
        encrypt: bool = False
    ) -> Optional[SettingEntity]:
        """Set a setting value (create or update)."""
        try:
            # Check if setting already exists
            existing = await self.get_by_key(key)
            
            if existing:
                # Update existing setting
                update_data = {
                    "value": value if not encrypt else None,
                    "encrypted_value": value if encrypt else None,
                    "is_encrypted": encrypt,
                }
                
                if category is not None:
                    update_data["category"] = category
                if description is not None:
                    update_data["description"] = description
                
                return await self.update(existing.id, update_data)
            else:
                # Create new setting
                setting_data = {
                    "key": key,
                    "value": value if not encrypt else None,
                    "encrypted_value": value if encrypt else None,
                    "is_encrypted": encrypt,
                    "category": category,
                    "description": description,
                }
                
                return await self.create(setting_data)
                
        except Exception:
            return None
    
    async def set_encrypted_value(
        self, 
        key: str, 
        encrypted_value: str,
        category: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[SettingEntity]:
        """Set an encrypted setting value."""
        try:
            # Check if setting already exists
            existing = await self.get_by_key(key)
            
            if existing:
                # Update existing setting
                update_data = {
                    "value": None,
                    "encrypted_value": encrypted_value,
                    "is_encrypted": True,
                }
                
                if category is not None:
                    update_data["category"] = category
                if description is not None:
                    update_data["description"] = description
                
                return await self.update(existing.id, update_data)
            else:
                # Create new setting
                setting_data = {
                    "key": key,
                    "value": None,
                    "encrypted_value": encrypted_value,
                    "is_encrypted": True,
                    "category": category,
                    "description": description,
                }
                
                return await self.create(setting_data)
                
        except Exception:
            return None
    
    async def update_value(self, key: str, value: str) -> Optional[SettingEntity]:
        """Update existing setting value."""
        try:
            existing = await self.get_by_key(key)
            if not existing:
                return None
            
            update_data = {
                "value": value if not existing.is_encrypted else None,
                "encrypted_value": value if existing.is_encrypted else None,
            }
            
            return await self.update(existing.id, update_data)
            
        except Exception:
            return None
    
    async def update_encrypted_value(
        self, 
        key: str, 
        encrypted_value: str
    ) -> Optional[SettingEntity]:
        """Update existing encrypted setting value."""
        try:
            existing = await self.get_by_key(key)
            if not existing:
                return None
            
            update_data = {
                "value": None,
                "encrypted_value": encrypted_value,
                "is_encrypted": True,
            }
            
            return await self.update(existing.id, update_data)
            
        except Exception:
            return None
    
    async def delete_by_key(self, key: str) -> bool:
        """Delete setting by key."""
        try:
            result = await self._database.delete(
                self._table_name,
                filters={"key": key}
            )
            return result.success and result.affected_rows > 0
        except Exception:
            return False
    
    async def update_category(self, key: str, category: str) -> Optional[SettingEntity]:
        """Update setting category."""
        try:
            existing = await self.get_by_key(key)
            if not existing:
                return None
            
            return await self.update(existing.id, {"category": category})
            
        except Exception:
            return None
    
    async def update_description(self, key: str, description: str) -> Optional[SettingEntity]:
        """Update setting description."""
        try:
            existing = await self.get_by_key(key)
            if not existing:
                return None
            
            return await self.update(existing.id, {"description": description})
            
        except Exception:
            return None
    
    async def toggle_encryption(self, key: str, encrypt: bool) -> Optional[SettingEntity]:
        """Toggle encryption status for a setting."""
        try:
            existing = await self.get_by_key(key)
            if not existing:
                return None
            
            # Note: This is a simplified implementation.
            # In a real system, you'd need to handle encryption/decryption here.
            # For now, we just toggle the flag and move the value between fields.
            
            if encrypt and not existing.is_encrypted:
                # Moving to encrypted (would need encryption here)
                update_data = {
                    "value": None,
                    "encrypted_value": existing.value,  # This should be encrypted!
                    "is_encrypted": True,
                }
            elif not encrypt and existing.is_encrypted:
                # Moving to unencrypted (would need decryption here)
                update_data = {
                    "value": existing.encrypted_value,  # This should be decrypted!
                    "encrypted_value": None,
                    "is_encrypted": False,
                }
            else:
                # No change needed
                return existing
            
            return await self.update(existing.id, update_data)
            
        except Exception:
            return None
    
    async def get_categories(self) -> List[str]:
        """Get all unique categories."""
        try:
            result = await self._database.select(
                self._table_name,
                columns=["category"]
            )
            
            if not result.success:
                return []
            
            # Extract unique categories, filtering out None values
            categories = set()
            for row in result.data:
                category = row.get("category")
                if category:
                    categories.add(category)
            
            return sorted(list(categories))
            
        except Exception:
            return []
    
    async def search_settings(
        self, 
        keyword: str,
        include_descriptions: bool = True
    ) -> List[SettingEntity]:
        """Search settings by keyword in key or description."""
        try:
            # Get all settings and filter in memory
            all_settings = await self.list_all()
            
            keyword_lower = keyword.lower()
            matching_settings = []
            
            for setting in all_settings:
                if keyword_lower in setting.key.lower():
                    matching_settings.append(setting)
                elif (include_descriptions and 
                      setting.description and 
                      keyword_lower in setting.description.lower()):
                    matching_settings.append(setting)
            
            return matching_settings
            
        except Exception:
            return []
    
    async def get_settings_summary(self) -> Dict[str, Any]:
        """Get summary of settings (counts by category, encryption status, etc.)."""
        try:
            all_settings = await self.list_all()
            
            summary = {
                "total_settings": len(all_settings),
                "encrypted_count": 0,
                "unencrypted_count": 0,
                "by_category": {},
            }
            
            for setting in all_settings:
                # Count encryption status
                if setting.is_encrypted:
                    summary["encrypted_count"] += 1
                else:
                    summary["unencrypted_count"] += 1
                
                # Count by category
                category = setting.category or "uncategorized"
                summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
            
            return summary
            
        except Exception:
            return {
                "total_settings": 0,
                "encrypted_count": 0,
                "unencrypted_count": 0,
                "by_category": {},
            }
    
    async def bulk_update_category(
        self, 
        keys: List[str], 
        category: str
    ) -> int:
        """Update category for multiple settings."""
        try:
            updated_count = 0
            
            for key in keys:
                result = await self.update_category(key, category)
                if result:
                    updated_count += 1
            
            return updated_count
            
        except Exception:
            return 0
    
    async def export_settings(
        self, 
        category: Optional[str] = None,
        include_encrypted: bool = False
    ) -> Dict[str, Any]:
        """Export settings for backup or migration."""
        try:
            # Get settings based on criteria
            if category:
                settings = await self.get_by_category(category)
            else:
                settings = await self.list_all()
            
            export_data = {
                "exported_at": datetime.utcnow().isoformat(),
                "category_filter": category,
                "settings": []
            }
            
            for setting in settings:
                setting_data = setting.to_dict(include_sensitive=include_encrypted)
                export_data["settings"].append(setting_data)
            
            return export_data
            
        except Exception:
            return {"exported_at": datetime.utcnow().isoformat(), "settings": []}
    
    async def import_settings(
        self, 
        settings_data: Dict[str, Any],
        overwrite_existing: bool = False
    ) -> int:
        """Import settings from exported data."""
        try:
            imported_count = 0
            settings_list = settings_data.get("settings", [])
            
            for setting_data in settings_list:
                key = setting_data.get("key")
                if not key:
                    continue
                
                # Check if setting exists
                existing = await self.get_by_key(key)
                
                if existing and not overwrite_existing:
                    continue  # Skip existing settings
                
                # Remove internal fields that shouldn't be imported
                import_data = {k: v for k, v in setting_data.items() 
                             if k not in ["id", "created_at", "updated_at"]}
                
                if existing:
                    # Update existing
                    result = await self.update(existing.id, import_data)
                    if result:
                        imported_count += 1
                else:
                    # Create new
                    result = await self.create(import_data)
                    if result:
                        imported_count += 1
            
            return imported_count
            
        except Exception:
            return 0
    
    async def validate_setting_key(self, key: str) -> bool:
        """Validate if a setting key is properly formatted."""
        try:
            # Basic validation rules:
            # - Must not be empty
            # - Must contain only alphanumeric characters, underscores, dots, and hyphens
            # - Must not start or end with special characters
            # - Must be reasonable length
            
            if not key or len(key) == 0:
                return False
            
            if len(key) > 255:  # Reasonable length limit
                return False
            
            # Check pattern: alphanumeric, underscore, dot, hyphen
            pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9_.-]*[a-zA-Z0-9]$')
            
            # For single character keys, just check if alphanumeric
            if len(key) == 1:
                return key.isalnum()
            
            return bool(pattern.match(key))
            
        except Exception:
            return False
    
    async def get_default_settings(self) -> Dict[str, Dict[str, Any]]:
        """Get default settings that should be created on first run."""
        return {
            "app_version": {
                "value": "1.0.0",
                "category": "system",
                "description": "Current application version",
                "is_encrypted": False,
            },
            "projects_enabled": {
                "value": "true",
                "category": "features",
                "description": "Enable projects and task management",
                "is_encrypted": False,
            },
            "embedding_model": {
                "value": "text-embedding-ada-002",
                "category": "ai",
                "description": "Default embedding model for vector search",
                "is_encrypted": False,
            },
            "max_crawl_depth": {
                "value": "3",
                "category": "crawling",
                "description": "Maximum depth for website crawling",
                "is_encrypted": False,
            },
            "default_chunk_size": {
                "value": "1000",
                "category": "processing",
                "description": "Default chunk size for document processing",
                "is_encrypted": False,
            },
        }