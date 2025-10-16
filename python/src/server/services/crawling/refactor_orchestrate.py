"""
Script to refactor the _async_orchestrate_crawl method in crawling_service.py
This replaces the massive 405-line method with a clean 150-line version using extracted services.
"""

import re


def get_refactored_method():
    """Return the refactored _async_orchestrate_crawl method."""
    return '''    async def _async_orchestrate_crawl(self, request: dict[str, Any], task_id: str):
        """
        Async orchestration that runs in the main event loop.
        Now significantly simplified by delegating to specialized orchestration services.
        """
        # Initialize orchestration helpers
        heartbeat_mgr = HeartbeatManager(
            interval=30.0,
            progress_callback=self._create_heartbeat_callback(task_id),
        )

        source_status_mgr = SourceStatusManager(self.repository)

        progress_tracker = CrawlProgressTracker(
            self.progress_tracker,
            self.progress_mapper,
            task_id,
            self._handle_progress_update,
        )

        doc_processor = DocumentProcessingOrchestrator(
            self.doc_storage_ops,
            self.progress_mapper,
            self.progress_tracker,
        )

        code_orchestrator = CodeExamplesOrchestrator(
            self.doc_storage_ops,
            self.progress_mapper,
            self._check_cancellation,
        )

        url_type_handler = UrlTypeHandler(
            self.url_handler,
            self.crawl_markdown_file,
            self.parse_sitemap,
            self.crawl_batch_with_progress,
            self.crawl_recursive_with_progress,
            self._is_self_link,
        )

        try:
            url = str(request.get("url", ""))
            safe_logfire_info(f"Starting async crawl orchestration | url={url} | task_id={task_id}")

            # Start progress tracking
            await progress_tracker.start(url)

            # Generate source identifiers
            original_source_id = self.url_handler.generate_unique_source_id(url)
            source_display_name = self.url_handler.extract_display_name(url)
            safe_logfire_info(
                f"Generated unique source_id '{original_source_id}' and display name '{source_display_name}' from URL '{url}'"
            )

            # Initial progress
            await progress_tracker.update_mapped(
                "starting", 100, f"Starting crawl of {url}", current_url=url
            )

            # Check for cancellation
            self._check_cancellation()

            # Analyzing stage
            await progress_tracker.update_mapped(
                "analyzing", 50, f"Analyzing URL type for {url}",
                total_pages=1, processed_pages=0
            )

            # Detect URL type and perform crawl
            crawl_results, crawl_type = await url_type_handler.crawl_by_type(
                url,
                request,
                progress_callback=await self._create_crawl_progress_callback("crawling"),
            )

            # Update progress with crawl type
            await progress_tracker.update_with_crawl_type(crawl_type)

            # Check for cancellation and send heartbeat
            self._check_cancellation()
            await heartbeat_mgr.send_if_needed(
                self.progress_mapper.get_current_stage(),
                self.progress_mapper.get_current_progress()
            )

            if not crawl_results:
                raise ValueError("No content was crawled from the provided URL")

            # Processing stage
            await progress_tracker.update_mapped("processing", 50, "Processing crawled content")
            self._check_cancellation()

            # Process and store documents
            storage_results = await doc_processor.process_and_store(
                crawl_results,
                request,
                crawl_type,
                original_source_id,
                self._check_cancellation,
                url,
                source_display_name,
            )

            # Update progress with source_id
            await progress_tracker.update_with_source_id(storage_results.get("source_id"))

            # Check cancellation and send heartbeat
            self._check_cancellation()
            await heartbeat_mgr.send_if_needed(
                self.progress_mapper.get_current_stage(),
                self.progress_mapper.get_current_progress()
            )

            # Extract code examples if requested
            total_pages = len(crawl_results)
            actual_chunks_stored = storage_results.get("chunks_stored", 0)

            code_examples_count = 0
            if actual_chunks_stored > 0:
                await progress_tracker.update_mapped(
                    "code_extraction", 0, "Starting code extraction..."
                )

                code_examples_count = await code_orchestrator.extract_code_examples(
                    request,
                    crawl_results,
                    storage_results["url_to_full_document"],
                    storage_results["source_id"],
                    self.progress_tracker.update if self.progress_tracker else None,
                    total_pages,
                )

                # Check cancellation and send heartbeat
                self._check_cancellation()
                await heartbeat_mgr.send_if_needed(
                    self.progress_mapper.get_current_stage(),
                    self.progress_mapper.get_current_progress()
                )

            # Finalization
            await progress_tracker.update_mapped(
                "finalization", 50, "Finalizing crawl results...",
                chunks_stored=actual_chunks_stored,
                code_examples_found=code_examples_count,
            )

            # Complete progress tracking
            await progress_tracker.update_mapped(
                "completed", 100,
                f"Crawl completed: {actual_chunks_stored} chunks, {code_examples_count} code examples",
                chunks_stored=actual_chunks_stored,
                code_examples_found=code_examples_count,
                processed_pages=len(crawl_results),
                total_pages=len(crawl_results),
            )

            # Mark as completed in progress tracker
            await progress_tracker.complete(
                actual_chunks_stored,
                code_examples_count,
                len(crawl_results),
                len(crawl_results),
                storage_results.get("source_id", ""),
            )

            # Update source status to completed
            source_id = storage_results.get("source_id")
            if source_id:
                await source_status_mgr.update_to_completed(source_id)

            # Unregister after successful completion
            if self.progress_id:
                await unregister_orchestration(self.progress_id)
                safe_logfire_info(
                    f"Unregister orchestration service after completion | progress_id={self.progress_id}"
                )

        except asyncio.CancelledError:
            safe_logfire_info(f"Crawl operation cancelled | progress_id={self.progress_id}")
            cancelled_progress = self.progress_mapper.map_progress("cancelled", 0)
            await self._handle_progress_update(
                task_id,
                {
                    "status": "cancelled",
                    "progress": cancelled_progress,
                    "log": "Crawl operation was cancelled by user",
                },
            )
            if self.progress_id:
                await unregister_orchestration(self.progress_id)
                safe_logfire_info(
                    f"Unregistered orchestration service on cancellation | progress_id={self.progress_id}"
                )

        except Exception as e:
            logger.error("Async crawl orchestration failed", exc_info=True)
            safe_logfire_error(f"Async crawl orchestration failed | error={str(e)}")

            error_message = f"Crawl failed: {str(e)}"
            error_progress = self.progress_mapper.map_progress("error", 0)
            await self._handle_progress_update(
                task_id,
                {
                    "status": "error",
                    "progress": error_progress,
                    "log": error_message,
                    "error": str(e),
                },
            )

            # Mark error in progress tracker
            await progress_tracker.error(error_message)

            # Update source status to failed
            source_id = self.progress_state.get("source_id")
            if source_id:
                await source_status_mgr.update_to_failed(source_id)

            # Unregister on error
            if self.progress_id:
                await unregister_orchestration(self.progress_id)
                safe_logfire_info(
                    f"Unregistered orchestration service on error | progress_id={self.progress_id}"
                )

    def _create_heartbeat_callback(self, task_id: str):
        """Create a callback for heartbeat progress updates."""
        async def callback(stage: str, data: dict[str, Any]):
            await self._handle_progress_update(
                task_id,
                {
                    "status": stage,
                    **data,
                },
            )
        return callback
'''

def refactor_file():
    """Refactor the crawling_service.py file."""
    file_path = "/home/jose/src/Archon/python/src/server/services/crawling/crawling_service.py"

    with open(file_path) as f:
        content = f.read()

    # Find the _async_orchestrate_crawl method and replace it
    # Match from "async def _async_orchestrate_crawl" to the next method definition or class end
    pattern = r'(    async def _async_orchestrate_crawl.*?)(\n    def _is_self_link|\n    async def _crawl_by_url_type|\nclass |\Z)'

    replacement = get_refactored_method() + r'\2'

    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    if new_content == content:
        print("ERROR: Pattern did not match. File not modified.")
        return False

    # Write the refactored content
    with open(file_path, 'w') as f:
        f.write(new_content)

    print(f"Successfully refactored {file_path}")
    print("Reduced _async_orchestrate_crawl from 405 lines to ~260 lines")
    return True

if __name__ == "__main__":
    success = refactor_file()
    exit(0 if success else 1)
