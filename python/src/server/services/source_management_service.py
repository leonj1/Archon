"""
Source Management Service

Handles source metadata, summaries, and management.
Consolidates both utility functions and class-based service.
"""

import os
from typing import Any

from ..config.logfire_config import get_logger, search_logger
from .client_manager import get_connection_manager

logger = get_logger(__name__)


def _get_model_choice() -> str:
    """Get MODEL_CHOICE with direct fallback."""
    try:
        # Direct cache/env fallback
        from .credential_service import credential_service

        if credential_service._cache_initialized and "MODEL_CHOICE" in credential_service._cache:
            model = credential_service._cache["MODEL_CHOICE"]
        else:
            model = os.getenv("MODEL_CHOICE", "gpt-4.1-nano")
        logger.debug(f"Using model choice: {model}")
        return model
    except Exception as e:
        logger.warning(f"Error getting model choice: {e}, using default")
        return "gpt-4.1-nano"


def extract_source_summary(
    source_id: str, content: str, max_length: int = 500, provider: str = None
) -> str:
    """
    Extract a summary for a source from its content using an LLM.

    This function uses the configured provider to generate a concise summary of the source content.

    Args:
        source_id: The source ID (domain)
        content: The content to extract a summary from
        max_length: Maximum length of the summary
        provider: Optional provider override

    Returns:
        A summary string
    """
    # Default summary if we can't extract anything meaningful
    default_summary = f"Content from {source_id}"

    if not content or len(content.strip()) == 0:
        return default_summary

    # Get the model choice from credential service (RAG setting)
    model_choice = _get_model_choice()
    search_logger.info(f"Generating summary for {source_id} using model: {model_choice}")

    # Limit content length to avoid token limits
    truncated_content = content[:25000] if len(content) > 25000 else content

    # Create the prompt for generating the summary
    prompt = f"""<source_content>
{truncated_content}
</source_content>

The above content is from the documentation for '{source_id}'. Please provide a concise summary (3-5 sentences) that describes what this library/tool/framework is about. The summary should help understand what the library/tool/framework accomplishes and the purpose.
"""

    try:
        try:
            import os

            import openai

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                # Try to get from credential service with direct fallback
                from .credential_service import credential_service

                if (
                    credential_service._cache_initialized
                    and "OPENAI_API_KEY" in credential_service._cache
                ):
                    cached_key = credential_service._cache["OPENAI_API_KEY"]
                    if isinstance(cached_key, dict) and cached_key.get("is_encrypted"):
                        api_key = credential_service._decrypt_value(cached_key["encrypted_value"])
                    else:
                        api_key = cached_key
                else:
                    api_key = os.getenv("OPENAI_API_KEY", "")

            if not api_key:
                raise ValueError("No OpenAI API key available")

            client = openai.OpenAI(api_key=api_key)
            search_logger.info("Successfully created LLM client fallback for summary generation")
        except Exception as e:
            search_logger.error(f"Failed to create LLM client fallback: {e}")
            return default_summary

        # Call the OpenAI API to generate the summary
        response = client.chat.completions.create(
            model=model_choice,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides concise library/tool/framework summaries.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        # Extract the generated summary with proper error handling
        if not response or not response.choices or len(response.choices) == 0:
            search_logger.error(f"Empty or invalid response from LLM for {source_id}")
            return default_summary

        message_content = response.choices[0].message.content
        if message_content is None:
            search_logger.error(f"LLM returned None content for {source_id}")
            return default_summary

        summary = message_content.strip()

        # Ensure the summary is not too long
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."

        return summary

    except Exception as e:
        search_logger.error(
            f"Error generating summary with LLM for {source_id}: {e}. Using default summary."
        )
        return default_summary


def generate_source_title_and_metadata(
    source_id: str,
    content: str,
    knowledge_type: str = "technical",
    tags: list[str] | None = None,
    provider: str = None,
) -> tuple[str, dict[str, Any]]:
    """
    Generate a user-friendly title and metadata for a source based on its content.

    Args:
        source_id: The source ID (domain)
        content: Sample content from the source
        knowledge_type: Type of knowledge (default: "technical")
        tags: Optional list of tags

    Returns:
        Tuple of (title, metadata)
    """
    # Default title is the source ID
    title = source_id

    # Try to generate a better title from content
    if content and len(content.strip()) > 100:
        try:
            try:
                import os

                import openai

                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    # Try to get from credential service with direct fallback
                    from .credential_service import credential_service

                    if (
                        credential_service._cache_initialized
                        and "OPENAI_API_KEY" in credential_service._cache
                    ):
                        cached_key = credential_service._cache["OPENAI_API_KEY"]
                        if isinstance(cached_key, dict) and cached_key.get("is_encrypted"):
                            api_key = credential_service._decrypt_value(
                                cached_key["encrypted_value"]
                            )
                        else:
                            api_key = cached_key
                    else:
                        api_key = os.getenv("OPENAI_API_KEY", "")

                if not api_key:
                    raise ValueError("No OpenAI API key available")

                client = openai.OpenAI(api_key=api_key)
            except Exception as e:
                search_logger.error(
                    f"Failed to create LLM client fallback for title generation: {e}"
                )
                # Don't proceed if client creation fails
                raise

            model_choice = _get_model_choice()

            # Limit content for prompt
            sample_content = content[:3000] if len(content) > 3000 else content

            prompt = f"""Based on this content from {source_id}, generate a concise, descriptive title (3-6 words) that captures what this source is about:

{sample_content}

Provide only the title, nothing else."""

            response = client.chat.completions.create(
                model=model_choice,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates concise titles.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            generated_title = response.choices[0].message.content.strip()
            # Clean up the title
            generated_title = generated_title.strip("\"'")
            if len(generated_title) < 50:  # Sanity check
                title = generated_title

        except Exception as e:
            search_logger.error(f"Error generating title for {source_id}: {e}")

    # Build metadata
    metadata = {"knowledge_type": knowledge_type, "tags": tags or [], "auto_generated": True}

    return title, metadata


async def update_source_info(
    source_id: str,
    summary: str,
    word_count: int,
    content: str = "",
    knowledge_type: str = "technical",
    tags: list[str] | None = None,
    update_frequency: int = 7,
    original_url: str | None = None,
):
    """
    Update or insert source information in the sources table.

    Args:
        source_id: The source ID (domain)
        summary: Summary of the source
        word_count: Total word count for the source
        content: Sample content for title generation
        knowledge_type: Type of knowledge
        tags: List of tags
        update_frequency: Update frequency in days
        original_url: Original URL for the source
    """
    try:
        manager = get_connection_manager()
        
        async with manager.get_primary() as db:
            # First, check if source already exists to preserve title
            existing_result = await db.select(
                "sources", 
                columns=["title"], 
                filters={"source_id": source_id}
            )

            if existing_result.success and existing_result.data:
                # Source exists - preserve the existing title
                existing_title = existing_result.data[0]["title"]
                search_logger.info(f"Preserving existing title for {source_id}: {existing_title}")

                # Update metadata while preserving title
                metadata = {
                    "knowledge_type": knowledge_type,
                    "tags": tags or [],
                    "auto_generated": False,  # Mark as not auto-generated since we're preserving
                    "update_frequency": update_frequency,
                }
                if original_url:
                    metadata["original_url"] = original_url

                # Update existing source (preserving title)
                update_data = {
                    "summary": summary,
                    "total_word_count": word_count,
                    "metadata": metadata,
                }
                
                result = await db.update(
                    "sources",
                    update_data,
                    filters={"source_id": source_id}
                )

                if not result.success:
                    raise RuntimeError(f"Failed to update source: {result.error}")

                search_logger.info(
                    f"Updated source {source_id} while preserving title: {existing_title}"
                )
            else:
                # New source - generate title and metadata
                title, metadata = generate_source_title_and_metadata(
                    source_id, content, knowledge_type, tags
                )

                # Add update_frequency and original_url to metadata
                metadata["update_frequency"] = update_frequency
                if original_url:
                    metadata["original_url"] = original_url

                # Insert new source
                insert_data = {
                    "source_id": source_id,
                    "title": title,
                    "summary": summary,
                    "total_word_count": word_count,
                    "metadata": metadata,
                }
                
                result = await db.insert("sources", insert_data)
                
                if not result.success:
                    raise RuntimeError(f"Failed to insert source: {result.error}")
                    
                search_logger.info(f"Created new source {source_id} with title: {title}")

    except Exception as e:
        search_logger.error(f"Error updating source {source_id}: {e}")
        raise  # Re-raise the exception so the caller knows it failed


class SourceManagementService:
    """Service class for source management operations"""

    def __init__(self):
        """Initialize service"""
        pass

    async def get_available_sources(self) -> tuple[bool, dict[str, Any]]:
        """
        Get all available sources from the sources table.

        Returns a list of all unique sources that have been crawled and stored.

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            manager = get_connection_manager()
            
            async with manager.get_reader() as db:
                result = await db.select("sources")
                
                if not result.success:
                    return False, {"error": f"Database error: {result.error}"}

                sources = []
                for row in result.data:
                    sources.append({
                        "source_id": row["source_id"],
                        "title": row.get("title", ""),
                        "summary": row.get("summary", ""),
                        "created_at": row.get("created_at", ""),
                        "updated_at": row.get("updated_at", ""),
                    })

                return True, {"sources": sources, "total_count": len(sources)}

        except Exception as e:
            logger.error(f"Error retrieving sources: {e}")
            return False, {"error": f"Error retrieving sources: {str(e)}"}

    async def delete_source(self, source_id: str) -> tuple[bool, dict[str, Any]]:
        """
        Delete a source and all associated crawled pages and code examples from the database.

        Args:
            source_id: The source ID to delete

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            logger.info(f"Starting delete_source for source_id: {source_id}")
            manager = get_connection_manager()
            
            # Use transaction for cascading deletes
            async with manager.get_primary() as db:
                async with await db.begin_transaction() as tx:
                    pages_deleted = 0
                    code_deleted = 0
                    source_deleted = 0
                    
                    # Delete from crawled_pages table
                    try:
                        logger.info(f"Deleting from crawled_pages table for source_id: {source_id}")
                        pages_result = await db.delete(
                            "crawled_pages", 
                            filters={"source_id": source_id},
                            returning=["id"]
                        )
                        
                        if not pages_result.success:
                            logger.error(f"Failed to delete from crawled_pages: {pages_result.error}")
                            return False, {"error": f"Failed to delete crawled pages: {pages_result.error}"}
                            
                        pages_deleted = len(pages_result.data) if pages_result.data else 0
                        logger.info(f"Deleted {pages_deleted} pages from crawled_pages")
                    except Exception as pages_error:
                        logger.error(f"Failed to delete from crawled_pages: {pages_error}")
                        return False, {"error": f"Failed to delete crawled pages: {str(pages_error)}"}

                    # Delete from code_examples table
                    try:
                        logger.info(f"Deleting from code_examples table for source_id: {source_id}")
                        code_result = await db.delete(
                            "code_examples", 
                            filters={"source_id": source_id},
                            returning=["id"]
                        )
                        
                        if not code_result.success:
                            logger.error(f"Failed to delete from code_examples: {code_result.error}")
                            return False, {"error": f"Failed to delete code examples: {code_result.error}"}
                            
                        code_deleted = len(code_result.data) if code_result.data else 0
                        logger.info(f"Deleted {code_deleted} code examples")
                    except Exception as code_error:
                        logger.error(f"Failed to delete from code_examples: {code_error}")
                        return False, {"error": f"Failed to delete code examples: {str(code_error)}"}

                    # Delete from sources table
                    try:
                        logger.info(f"Deleting from sources table for source_id: {source_id}")
                        source_result = await db.delete(
                            "sources", 
                            filters={"source_id": source_id},
                            returning=["id"]
                        )
                        
                        if not source_result.success:
                            logger.error(f"Failed to delete from sources: {source_result.error}")
                            return False, {"error": f"Failed to delete source: {source_result.error}"}
                            
                        source_deleted = len(source_result.data) if source_result.data else 0
                        logger.info(f"Deleted {source_deleted} source records")
                    except Exception as source_error:
                        logger.error(f"Failed to delete from sources: {source_error}")
                        return False, {"error": f"Failed to delete source: {str(source_error)}"}

                    # Transaction will auto-commit on successful exit
                    logger.info("Delete operation completed successfully")
                    return True, {
                        "source_id": source_id,
                        "pages_deleted": pages_deleted,
                        "code_examples_deleted": code_deleted,
                        "source_records_deleted": source_deleted,
                    }

        except Exception as e:
            logger.error(f"Unexpected error in delete_source: {e}")
            return False, {"error": f"Error deleting source: {str(e)}"}

    async def update_source_metadata(
        self,
        source_id: str,
        title: str = None,
        summary: str = None,
        word_count: int = None,
        knowledge_type: str = None,
        tags: list[str] = None,
    ) -> tuple[bool, dict[str, Any]]:
        """
        Update source metadata.

        Args:
            source_id: The source ID to update
            title: Optional new title
            summary: Optional new summary
            word_count: Optional new word count
            knowledge_type: Optional new knowledge type
            tags: Optional new tags list

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            manager = get_connection_manager()
            
            async with manager.get_primary() as db:
                # Build update data
                update_data = {}
                if title is not None:
                    update_data["title"] = title
                if summary is not None:
                    update_data["summary"] = summary
                if word_count is not None:
                    update_data["total_word_count"] = word_count

                # Handle metadata fields
                if knowledge_type is not None or tags is not None:
                    # Get existing metadata
                    existing_result = await db.select(
                        "sources",
                        columns=["metadata"],
                        filters={"source_id": source_id}
                    )
                    
                    if not existing_result.success:
                        return False, {"error": f"Failed to get existing metadata: {existing_result.error}"}
                    
                    metadata = existing_result.data[0].get("metadata", {}) if existing_result.data else {}

                    if knowledge_type is not None:
                        metadata["knowledge_type"] = knowledge_type
                    if tags is not None:
                        metadata["tags"] = tags

                    update_data["metadata"] = metadata

                if not update_data:
                    return False, {"error": "No update data provided"}

                # Update the source
                result = await db.update(
                    "sources",
                    update_data,
                    filters={"source_id": source_id},
                    returning=["source_id"]
                )

                if result.success and result.data:
                    return True, {"source_id": source_id, "updated_fields": list(update_data.keys())}
                else:
                    return False, {"error": f"Source with ID {source_id} not found or update failed: {result.error}"}

        except Exception as e:
            logger.error(f"Error updating source metadata: {e}")
            return False, {"error": f"Error updating source metadata: {str(e)}"}

    async def create_source_info(
        self,
        source_id: str,
        content_sample: str,
        word_count: int = 0,
        knowledge_type: str = "technical",
        tags: list[str] = None,
        update_frequency: int = 7,
    ) -> tuple[bool, dict[str, Any]]:
        """
        Create source information entry.

        Args:
            source_id: The source ID
            content_sample: Sample content for generating summary
            word_count: Total word count for the source
            knowledge_type: Type of knowledge (default: "technical")
            tags: List of tags
            update_frequency: Update frequency in days

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            if tags is None:
                tags = []

            # Generate source summary using the utility function
            source_summary = extract_source_summary(source_id, content_sample)

            # Create the source info using the utility function
            await update_source_info(
                source_id,
                source_summary,
                word_count,
                content_sample[:5000],
                knowledge_type,
                tags,
                update_frequency,
            )

            return True, {
                "source_id": source_id,
                "summary": source_summary,
                "word_count": word_count,
                "knowledge_type": knowledge_type,
                "tags": tags,
            }

        except Exception as e:
            logger.error(f"Error creating source info: {e}")
            return False, {"error": f"Error creating source info: {str(e)}"}

    async def get_source_details(self, source_id: str) -> tuple[bool, dict[str, Any]]:
        """
        Get detailed information about a specific source.

        Args:
            source_id: The source ID to look up

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            manager = get_connection_manager()
            
            async with manager.get_reader() as db:
                # Get source metadata
                source_result = await db.select(
                    "sources",
                    filters={"source_id": source_id}
                )

                if not source_result.success or not source_result.data:
                    return False, {"error": f"Source with ID {source_id} not found"}

                source_data = source_result.data[0]

                # Get page count
                page_count = await db.count(
                    "crawled_pages",
                    filters={"source_id": source_id}
                )

                # Get code example count
                code_count = await db.count(
                    "code_examples",
                    filters={"source_id": source_id}
                )

                return True, {
                    "source": source_data,
                    "page_count": page_count,
                    "code_example_count": code_count,
                }

        except Exception as e:
            logger.error(f"Error getting source details: {e}")
            return False, {"error": f"Error getting source details: {str(e)}"}

    async def list_sources_by_type(self, knowledge_type: str = None) -> tuple[bool, dict[str, Any]]:
        """
        List sources filtered by knowledge type.

        Args:
            knowledge_type: Optional knowledge type filter

        Returns:
            Tuple of (success, result_dict)
        """
        try:
            manager = get_connection_manager()
            
            async with manager.get_reader() as db:
                # Get all sources (filtering by JSON field is database-specific)
                result = await db.select("sources")
                
                if not result.success:
                    return False, {"error": f"Database error: {result.error}"}

                sources = []
                for row in result.data:
                    metadata = row.get("metadata", {})
                    
                    # Filter by knowledge_type if specified
                    if knowledge_type and metadata.get("knowledge_type", "") != knowledge_type:
                        continue
                    
                    sources.append({
                        "source_id": row["source_id"],
                        "title": row.get("title", ""),
                        "summary": row.get("summary", ""),
                        "knowledge_type": metadata.get("knowledge_type", ""),
                        "tags": metadata.get("tags", []),
                        "total_word_count": row.get("total_word_count", 0),
                        "created_at": row.get("created_at", ""),
                        "updated_at": row.get("updated_at", ""),
                    })

                return True, {
                    "sources": sources,
                    "total_count": len(sources),
                    "knowledge_type_filter": knowledge_type,
                }

        except Exception as e:
            logger.error(f"Error listing sources by type: {e}")
            return False, {"error": f"Error listing sources by type: {str(e)}"}
