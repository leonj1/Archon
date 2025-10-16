"""
Source Status Manager for Crawl Orchestration

Manages source crawl status updates and verification.
"""


from ....config.logfire_config import get_logger, safe_logfire_error, safe_logfire_info
from ....repositories.database_repository import DatabaseRepository

logger = get_logger(__name__)


class SourceStatusManager:
    """Manages source crawl status updates and verification."""

    def __init__(self, repository: DatabaseRepository):
        """
        Initialize the source status manager.

        Args:
            repository: Database repository instance
        """
        self.repository = repository

    async def update_to_completed(self, source_id: str) -> bool:
        """
        Update source crawl status to 'completed' and verify the update.

        Args:
            source_id: The source ID to update

        Returns:
            True if update was successful and verified, False otherwise
        """
        from ...source_management_service import update_source_info

        try:
            existing_source = await self.repository.get_source_by_id(source_id)
            if not existing_source:
                logger.error(f"Source not found for status update | source_id={source_id}")
                return False

            safe_logfire_info(
                f"Attempting to update crawl_status to 'completed' | source_id={source_id}"
            )

            await update_source_info(
                repository=self.repository,
                source_id=source_id,
                summary=existing_source.get("summary", ""),
                word_count=existing_source.get("total_word_count", 0),
                crawl_status="completed",
            )

            safe_logfire_info(f"Updated source crawl_status to completed | source_id={source_id}")

            # Verify the update persisted
            return await self._verify_status_update(source_id, "completed")

        except Exception as e:
            logger.warning(f"Failed to update source crawl_status: {e}")
            safe_logfire_error(f"Failed to update source crawl_status | error={e}")
            return False

    async def update_to_failed(self, source_id: str | None) -> bool:
        """
        Update source crawl status to 'failed'.

        Args:
            source_id: The source ID to update (optional)

        Returns:
            True if update was successful, False otherwise
        """
        from ...source_management_service import update_source_info

        if not source_id:
            return False

        try:
            existing_source = await self.repository.get_source_by_id(source_id)
            if not existing_source:
                return False

            await update_source_info(
                repository=self.repository,
                source_id=source_id,
                summary=existing_source.get("summary", ""),
                word_count=existing_source.get("total_word_count", 0),
                crawl_status="failed",
            )

            safe_logfire_info(f"Updated source crawl_status to failed | source_id={source_id}")
            return True

        except Exception as e:
            logger.warning(f"Failed to update source crawl_status on error: {e}")
            return False

    async def _verify_status_update(self, source_id: str, expected_status: str) -> bool:
        """
        Verify that a status update persisted correctly.

        Args:
            source_id: The source ID to verify
            expected_status: The expected status value

        Returns:
            True if status matches expected, False otherwise
        """
        safe_logfire_info(f"Verifying crawl_status update for source_id={source_id}")

        verified_source = await self.repository.get_source_by_id(source_id)
        if not verified_source:
            logger.error(f"CRITICAL: Failed to verify source after update | source_id={source_id}")
            return False

        verified_metadata = verified_source.get("metadata", {})
        verified_status = verified_metadata.get("crawl_status", "MISSING")

        safe_logfire_info(
            f"Verified crawl_status after update | source_id={source_id} | "
            f"status={verified_status} | expected={expected_status} | "
            f"match={verified_status == expected_status}"
        )

        if verified_status != expected_status:
            logger.error(
                f"CRITICAL: crawl_status update failed to persist | "
                f"source_id={source_id} | expected={expected_status} | actual={verified_status}"
            )
            safe_logfire_error(
                f"crawl_status mismatch | source_id={source_id} | "
                f"expected={expected_status} | actual={verified_status}"
            )
            return False

        return True
