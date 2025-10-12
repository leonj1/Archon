"""
Prompt Service Module for Archon

This module provides a singleton service for managing AI agent prompts.
Prompts are loaded from the database at startup and cached in memory for
fast access during agent operations.
"""

from datetime import datetime
from typing import Optional

from ..config.logfire_config import get_logger
from ..repositories.database_repository import DatabaseRepository
from ..repositories.supabase_repository import SupabaseDatabaseRepository
from ..utils import get_supabase_client

logger = get_logger(__name__)


class PromptService:
    """Singleton service for managing AI agent prompts."""

    _instance = None
    _prompts: dict[str, str] = {}
    _last_loaded: datetime | None = None
    _repository: Optional[DatabaseRepository] = None

    def __new__(cls, repository: Optional[DatabaseRepository] = None):
        """
        Ensure singleton pattern.

        Args:
            repository: DatabaseRepository instance (only used on first instantiation)
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, repository: Optional[DatabaseRepository] = None, supabase_client=None):
        """
        Initialize with optional repository or supabase client.

        Args:
            repository: DatabaseRepository instance (preferred)
            supabase_client: Legacy supabase client (for backward compatibility)
        """
        if self._repository is None:
            if repository is not None:
                self._repository = repository
            elif supabase_client is not None:
                self._repository = SupabaseDatabaseRepository(supabase_client)
            else:
                self._repository = SupabaseDatabaseRepository(get_supabase_client())

    async def load_prompts(self) -> None:
        """
        Load all prompts from database into memory.
        This should be called at application startup.
        """
        try:
            logger.info("Loading prompts from database...")

            prompts_data = await self._repository.get_all_prompts()

            if prompts_data:
                self._prompts = {
                    prompt["prompt_name"]: prompt["prompt"] for prompt in prompts_data
                }
                self._last_loaded = datetime.now()
                logger.info(f"Loaded {len(self._prompts)} prompts into memory")
            else:
                logger.warning("No prompts found in database")

        except Exception as e:
            logger.error(f"Failed to load prompts: {e}")
            # Continue with empty prompts rather than crash
            self._prompts = {}

    def get_prompt(self, prompt_name: str, default: str | None = None) -> str:
        """
        Get a prompt by name.

        Args:
            prompt_name: The name of the prompt to retrieve
            default: Default prompt to return if not found

        Returns:
            The prompt text or default value
        """
        if default is None:
            default = "You are a helpful AI assistant."

        prompt = self._prompts.get(prompt_name, default)

        if prompt == default and prompt_name not in self._prompts:
            logger.warning(f"Prompt '{prompt_name}' not found, using default")

        return prompt

    async def reload_prompts(self) -> None:
        """
        Reload prompts from database.
        Useful for refreshing prompts after they've been updated.
        """
        logger.info("Reloading prompts...")
        await self.load_prompts()

    def get_all_prompt_names(self) -> list[str]:
        """Get a list of all available prompt names."""
        return list(self._prompts.keys())

    def get_last_loaded_time(self) -> datetime | None:
        """Get the timestamp of when prompts were last loaded."""
        return self._last_loaded


# Global instance
prompt_service = PromptService()
