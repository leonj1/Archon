"""
Supabase Project Repository Implementation

Concrete implementation of project repository for Supabase database backend.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from ...interfaces import IDatabase, QueryResult
from ..interfaces.project_repository_interface import IProjectRepository, ProjectEntity


class SupabaseProjectRepository(IProjectRepository):
    """
    Supabase implementation of project repository.
    Handles project CRUD operations for Supabase database backend.
    """
    
    def __init__(self, database: IDatabase, table_name: str = "projects"):
        """
        Initialize Supabase project repository.
        
        Args:
            database: Supabase database interface
            table_name: Projects table name
        """
        super().__init__(database, table_name)
    
    async def create(self, entity_data: Dict[str, Any]) -> Optional[ProjectEntity]:
        """Create a new project."""
        try:
            # Ensure required fields are present
            if "id" not in entity_data:
                entity_data["id"] = f"project-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
            
            # Set timestamps
            now = datetime.utcnow()
            entity_data.setdefault("created_at", now.isoformat())
            entity_data.setdefault("updated_at", now.isoformat())
            
            # Set defaults
            entity_data.setdefault("status", "active")
            entity_data.setdefault("version", 1)
            entity_data.setdefault("features", [])
            entity_data.setdefault("docs", {})
            entity_data.setdefault("metadata", {})
            
            # Execute insert query
            query = f"""
                INSERT INTO {self._table_name} 
                (id, title, description, status, created_at, updated_at, metadata, 
                 github_repo, features, docs, version)
                VALUES 
                (:id, :title, :description, :status, :created_at, :updated_at, :metadata,
                 :github_repo, :features, :docs, :version)
                RETURNING *
            """
            
            result = await self._execute_query(query, entity_data)
            
            if result.rows:
                return ProjectEntity.from_dict(result.rows[0])
            return None
            
        except Exception as e:
            # Log error but don't crash - let caller handle
            return None
    
    async def get_by_id(self, entity_id: str) -> Optional[ProjectEntity]:
        """Get project by ID."""
        try:
            query = f"SELECT * FROM {self._table_name} WHERE id = :id"
            result = await self._execute_query(query, {"id": entity_id})
            
            if result.rows:
                return ProjectEntity.from_dict(result.rows[0])
            return None
            
        except Exception:
            return None
    
    async def update(self, entity_id: str, update_data: Dict[str, Any]) -> Optional[ProjectEntity]:
        """Update an existing project."""
        try:
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Build SET clause
            set_clauses = []
            params = {"id": entity_id}
            
            for key, value in update_data.items():
                param_key = f"update_{key}"
                set_clauses.append(f"{key} = :{param_key}")
                params[param_key] = value
            
            query = f"""
                UPDATE {self._table_name} 
                SET {', '.join(set_clauses)}
                WHERE id = :id
                RETURNING *
            """
            
            result = await self._execute_query(query, params)
            
            if result.rows:
                return ProjectEntity.from_dict(result.rows[0])
            return None
            
        except Exception:
            return None
    
    async def delete(self, entity_id: str) -> bool:
        """Delete a project by ID."""
        try:
            query = f"DELETE FROM {self._table_name} WHERE id = :id"
            result = await self._execute_query(query, {"id": entity_id})
            return result.rows_affected > 0
        except Exception:
            return False
    
    async def list_all(
        self, 
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[ProjectEntity]:
        """List all projects with optional pagination and ordering."""
        try:
            query = f"SELECT * FROM {self._table_name}"
            params = {}
            
            # Add ordering
            if order_by:
                query += f" ORDER BY {order_by}"
            else:
                query += " ORDER BY updated_at DESC"
            
            # Add pagination
            if limit:
                query += " LIMIT :limit"
                params["limit"] = limit
            
            if offset:
                query += " OFFSET :offset"
                params["offset"] = offset
            
            result = await self._execute_query(query, params)
            return [ProjectEntity.from_dict(row) for row in result.rows]
            
        except Exception:
            return []
    
    async def find_by_criteria(
        self, 
        criteria: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order_by: Optional[str] = None
    ) -> List[ProjectEntity]:
        """Find projects matching given criteria."""
        try:
            where_clause, params = self._build_where_clause(criteria)
            
            query = f"SELECT * FROM {self._table_name}"
            if where_clause:
                query += f" {where_clause}"
            
            # Add ordering
            if order_by:
                query += f" ORDER BY {order_by}"
            else:
                query += " ORDER BY updated_at DESC"
            
            # Add pagination
            if limit:
                query += " LIMIT :limit"
                params["limit"] = limit
            
            if offset:
                query += " OFFSET :offset"
                params["offset"] = offset
            
            result = await self._execute_query(query, params)
            return [ProjectEntity.from_dict(row) for row in result.rows]
            
        except Exception:
            return []
    
    async def count(self, criteria: Optional[Dict[str, Any]] = None) -> int:
        """Count projects matching optional criteria."""
        try:
            query = f"SELECT COUNT(*) as count FROM {self._table_name}"
            params = {}
            
            if criteria:
                where_clause, params = self._build_where_clause(criteria)
                if where_clause:
                    query += f" {where_clause}"
            
            result = await self._execute_query(query, params)
            return result.rows[0]["count"] if result.rows else 0
            
        except Exception:
            return 0
    
    async def exists(self, entity_id: str) -> bool:
        """Check if project exists by ID."""
        try:
            query = f"SELECT 1 FROM {self._table_name} WHERE id = :id LIMIT 1"
            result = await self._execute_query(query, {"id": entity_id})
            return len(result.rows) > 0
        except Exception:
            return False
    
    # Project-specific methods
    
    async def get_by_title(self, title: str) -> Optional[ProjectEntity]:
        """Get project by title."""
        try:
            query = f"SELECT * FROM {self._table_name} WHERE title = :title LIMIT 1"
            result = await self._execute_query(query, {"title": title})
            
            if result.rows:
                return ProjectEntity.from_dict(result.rows[0])
            return None
            
        except Exception:
            return None
    
    async def get_by_status(self, status: str) -> List[ProjectEntity]:
        """Get all projects with a specific status."""
        return await self.find_by_criteria({"status": status})
    
    async def get_by_github_repo(self, github_repo: str) -> Optional[ProjectEntity]:
        """Get project by GitHub repository."""
        try:
            query = f"SELECT * FROM {self._table_name} WHERE github_repo = :github_repo LIMIT 1"
            result = await self._execute_query(query, {"github_repo": github_repo})
            
            if result.rows:
                return ProjectEntity.from_dict(result.rows[0])
            return None
            
        except Exception:
            return None
    
    async def add_feature(self, project_id: str, feature: str) -> bool:
        """Add a feature to a project."""
        try:
            # Get current features
            project = await self.get_by_id(project_id)
            if not project:
                return False
            
            features = list(project.features) if project.features else []
            if feature not in features:
                features.append(feature)
                return await self.update_features(project_id, features)
            
            return True  # Feature already exists
            
        except Exception:
            return False
    
    async def remove_feature(self, project_id: str, feature: str) -> bool:
        """Remove a feature from a project."""
        try:
            # Get current features
            project = await self.get_by_id(project_id)
            if not project:
                return False
            
            features = list(project.features) if project.features else []
            if feature in features:
                features.remove(feature)
                return await self.update_features(project_id, features)
            
            return True  # Feature already removed
            
        except Exception:
            return False
    
    async def get_features(self, project_id: str) -> List[str]:
        """Get all features for a project."""
        try:
            project = await self.get_by_id(project_id)
            return list(project.features) if project and project.features else []
        except Exception:
            return []
    
    async def update_features(self, project_id: str, features: List[str]) -> bool:
        """Update the complete feature list for a project."""
        try:
            result = await self.update(project_id, {"features": features})
            return result is not None
        except Exception:
            return False
    
    async def update_metadata(
        self, 
        project_id: str, 
        metadata: Dict[str, Any]
    ) -> Optional[ProjectEntity]:
        """Update project metadata."""
        return await self.update(project_id, {"metadata": metadata})
    
    async def update_docs(
        self, 
        project_id: str, 
        docs: Dict[str, Any]
    ) -> Optional[ProjectEntity]:
        """Update project documentation references."""
        return await self.update(project_id, {"docs": docs})
    
    async def archive_project(self, project_id: str) -> bool:
        """Archive a project (set status to archived)."""
        try:
            result = await self.update(project_id, {"status": "archived"})
            return result is not None
        except Exception:
            return False
    
    async def activate_project(self, project_id: str) -> bool:
        """Activate a project (set status to active)."""
        try:
            result = await self.update(project_id, {"status": "active"})
            return result is not None
        except Exception:
            return False
    
    async def increment_version(self, project_id: str) -> Optional[ProjectEntity]:
        """Increment the project version number."""
        try:
            project = await self.get_by_id(project_id)
            if not project:
                return None
            
            new_version = project.version + 1 if project.version else 1
            return await self.update(project_id, {"version": new_version})
            
        except Exception:
            return None
    
    async def search_by_keyword(
        self, 
        keyword: str,
        include_archived: bool = False
    ) -> List[ProjectEntity]:
        """Search projects by keyword in title or description."""
        try:
            criteria = {}
            if not include_archived:
                criteria["status"] = "active"
            
            # Use SQL LIKE for keyword search
            where_conditions = []
            params = {"keyword": f"%{keyword}%"}
            
            where_conditions.append("(title ILIKE :keyword OR description ILIKE :keyword)")
            
            if not include_archived:
                where_conditions.append("status = :status")
                params["status"] = "active"
            
            where_clause = "WHERE " + " AND ".join(where_conditions)
            
            query = f"""
                SELECT * FROM {self._table_name} 
                {where_clause}
                ORDER BY updated_at DESC
            """
            
            result = await self._execute_query(query, params)
            return [ProjectEntity.from_dict(row) for row in result.rows]
            
        except Exception:
            return []
    
    async def get_recent_projects(
        self, 
        limit: int = 10,
        include_archived: bool = False
    ) -> List[ProjectEntity]:
        """Get recently updated projects."""
        try:
            criteria = {}
            if not include_archived:
                criteria["status"] = "active"
            
            return await self.find_by_criteria(
                criteria, 
                limit=limit, 
                order_by="updated_at DESC"
            )
            
        except Exception:
            return []
    
    async def get_projects_with_feature(self, feature: str) -> List[ProjectEntity]:
        """Get all projects that have a specific feature."""
        try:
            # For JSON array containment in PostgreSQL/Supabase
            query = f"""
                SELECT * FROM {self._table_name} 
                WHERE features @> :feature_array
                ORDER BY updated_at DESC
            """
            
            result = await self._execute_query(query, {"feature_array": [feature]})
            return [ProjectEntity.from_dict(row) for row in result.rows]
            
        except Exception:
            return []