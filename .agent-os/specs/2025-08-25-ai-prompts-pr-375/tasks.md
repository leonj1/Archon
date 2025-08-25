# Spec Tasks

## Tasks

- [ ] 1. Fix issues in archon-ui-main/Makefile (2 items)
    - [ ] 1.1 [Comment #2296441042] In archon-ui-main/Makefile around lines 152 to 171, update the test-results...
          ```
          Original AI Prompt:
          In archon-ui-main/Makefile around lines 152 to 171, update the test-results
target to read from test-results/test-results.json (matching the docker bind
mount) instead of public/test-results/test-results.json, and stop computing
"suites passed" by subtracting failed tests from total suites; instead read
suite-specific counters (e.g. data.numPassedTestSuites and
data.numFailedTestSuites, defaulting to 0) and use those to print
passed/failed/total suites so the suite summary uses the correct suite counts.
          ```
    - [ ] 1.2 [Comment #2296441043] In archon-ui-main/Makefile around lines 172 to 181, the coverage-report target...
          ```
          Original AI Prompt:
          In archon-ui-main/Makefile around lines 172 to 181, the coverage-report target
is pointing to public/test-results/coverage but coverage is written to
test-results/coverage; update all paths in this target to use
test-results/coverage (including the open/xdg-open fallback and the echo that
prints the path) so the commands and messages reference
test-results/coverage/index.html and the "No coverage report" check looks for
test-results/coverage instead of public/test-results/coverage.
          ```
    - [ ] 1.3 Verify all changes in archon-ui-main/Makefile work correctly
- [ ] 2. Fix issues in archon-ui-main/run-tests.sh (1 items)
    - [ ] 2.1 [Comment #2296693931] In archon-ui-main/run-tests.sh around lines 100 to 105, clean_up attempts to...
          ```
          Original AI Prompt:
          In archon-ui-main/run-tests.sh around lines 100 to 105, clean_up attempts to
remove containers by fixed names that are never created; either ensure the test
containers are created with --name flags or change the cleanup to target
containers by image/ancestor or label. Fix by (a) adding --name archon-ui-tests,
--name archon-ui-test-ui, --name archon-ui-lint to the docker run commands that
start the tests so those names exist, or (b) modify clean_up to docker ps -a
--filter "ancestor=archon-ui-test:latest" --format '{{.ID}}' | xargs -r docker
rm -f and similarly filter by image/tag or a consistent label used when running
containers; pick one approach and make the start and cleanup logic consistent.
          ```
    - [ ] 2.2 Verify all changes in archon-ui-main/run-tests.sh work correctly
- [ ] 3. Fix issues in archon-ui-main/test-docker-patch.js (1 items)
    - [ ] 3.1 [Comment #2296441045] In archon-ui-main/test-docker-patch.js around line 17, the file currently uses...
          ```
          Original AI Prompt:
          In archon-ui-main/test-docker-patch.js around line 17, the file currently uses
CommonJS export `module.exports = { isDocker };` which fails under the repo's
ESM `"type": "module"`; replace that line with an ESM export such as `export {
isDocker };` (or `export default isDocker;` if you prefer a default export) and
remove the CommonJS assignment so the module loads correctly under ESM.
          ```
    - [ ] 3.2 Verify all changes in archon-ui-main/test-docker-patch.js work correctly
- [ ] 4. Fix issues in docs/specs/repository-pattern-spec.md (1 items)
    - [ ] 4.1 [Comment #2296441047] `...
          ```
          Original AI Prompt:
          `
In docs/specs/repository-pattern-spec.md around lines 39 to 55 (and also apply
same change at lines ~629-649), the fenced code blocks containing the ASCII
diagram and directory tree lack a language tag which triggers markdownlint
MD040; update those backticks to include a language (e.g.,
          ```
    - [ ] 4.2 Verify all changes in docs/specs/repository-pattern-spec.md work correctly
- [ ] 5. Fix issues in python/Makefile (1 items)
    - [ ] 5.1 [Comment #2296441048] In python/Makefile around lines 36 to 40, the test-fast and test-watch targets...
          ```
          Original AI Prompt:
          In python/Makefile around lines 36 to 40, the test-fast and test-watch targets
rely on external pytest plugins (pytest-xdist for -n auto and pytest-watch for
ptw) that are not declared as dev dependencies; add pytest-xdist and
pytest-watch to your project's dev dependency manifest (either under
[tool.poetry.dev-dependencies] in python/pyproject.toml or the appropriate
python/requirements.*.txt used for dev/test extras) so CI and developer
environments install them automatically, then update lockfiles/requirements
(poetry lock or pip-compile) and rerun install to ensure make test-fast and make
test-watch work reliably.
          ```
    - [ ] 5.2 Verify all changes in python/Makefile work correctly
- [ ] 6. Fix issues in python/src/server/core/dependencies.py (6 items)
    - [ ] 6.1 [Comment #2296441049] In python/src/server/core/dependencies.py around lines 98-101, 160-163 and...
          ```
          Original AI Prompt:
          In python/src/server/core/dependencies.py around lines 98-101, 160-163 and
176-179 the logger.error calls only log the exception message; update each error
logging call to pass exc_info=True so the full stack trace is preserved in logs
(i.e., keep the existing message but add exc_info=True as an argument to each
cls._logger.error call).
          ```
    - [ ] 6.2 [Comment #2296707382] In python/src/server/core/dependencies.py around lines 8 to 13, the file...
          ```
          Original AI Prompt:
          In python/src/server/core/dependencies.py around lines 8 to 13, the file
currently imports a concrete SupabaseDatabase and lacks types needed for a
backend-agnostic, per-request, thread-safe dependency provider; replace the
concrete import with the repository interface IUnitOfWork and add imports for
AsyncGenerator (for yield-based async deps) and threading (for thread-safe lazy
init), then update any provider typing to use IUnitOfWork rather than
SupabaseDatabase and ensure the module is prepared to implement a thread-safe
lru_cache-backed initializer and async generator-based dependency.
          ```
    - [ ] 6.3 [Comment #2296707384] In python/src/server/core/dependencies.py around lines 23 to 44, replace the...
          ```
          Original AI Prompt:
          In python/src/server/core/dependencies.py around lines 23 to 44, replace the
hard-coded SupabaseDatabase initialization with a call to the project factory
using DatabaseConfig/create_database_instance, make the lazy init thread-safe by
adding a class-level threading.Lock and using double-checked locking around
instance creation, and change the method signature and stored type to return the
interface IUnitOfWork (not the concrete SupabaseDatabase). Ensure you import
DatabaseConfig, create_database_instance (or equivalent factory) and IUnitOfWork
at top, acquire the lock only when instance is None, create the instance via the
factory with config, assign it to cls._instance, and release the lock before
returning the IUnitOfWork.
          ```
    - [ ] 6.4 [Comment #2296707385] python/src/server/core/dependencies.py lines 104-126: remove the @lru_cache()...
          ```
          Original AI Prompt:
          python/src/server/core/dependencies.py lines 104-126: remove the @lru_cache()
decorator from get_database() so the function returns whatever DatabaseProvider
currently provides (allowing reset/set/overrides to work), drop the now-unused
lru_cache import, and update the function signature to the generalized database
type discussed in the earlier comment (e.g., return type -> DatabaseProtocol or
the agreed-upon abstract DB type) so the dependency reflects the generalized
interface; also apply the same removal/update to the corresponding occurrence at
line 9.
          ```
    - [ ] 6.5 [Comment #2296707387] In python/src/server/core/dependencies.py around lines 234 to 250,...
          ```
          Original AI Prompt:
          In python/src/server/core/dependencies.py around lines 234 to 250,
set_database_config currently updates _database_config but does not reset the
existing singleton provider so it keeps using old settings; modify the function
to also reset the provider (e.g., assign the module-level _database_provider
variable to None or call the provider reset function) immediately after updating
_database_config and before logging so that the next access will recreate the
provider with the new configuration.
          ```
    - [ ] 6.6 [Comment #2296735143] python/src/server/core/dependencies.py lines 11-13: the file currently imports...
          ```
          Original AI Prompt:
          python/src/server/core/dependencies.py lines 11-13: the file currently imports
SupabaseDatabase from the package-level implementations module which will break
unless that module re-exports the class; change the import to reference the
concrete module where SupabaseDatabase is defined (i.e., update the import path
to the specific implementations submodule that declares SupabaseDatabase) so the
symbol is imported directly from its defining module.
          ```
    - [ ] 6.7 Verify all changes in python/src/server/core/dependencies.py work correctly
- [ ] 7. Fix issues in python/src/server/repositories/implementations/mock_repositories.py (2 items)
    - [ ] 7.1 [Comment #2296441052] In python/src/server/repositories/implementations/mock_repositories.py around...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/mock_repositories.py around
lines 325 to 332, the code assigns result['similarity'] directly which mutates
the canonical in-memory entity; avoid side effects by creating a shallow copy
for each result before adding the similarity score (e.g., copy each dict, set
the 'similarity' on the copy, collect copies into a new list), then sort and
return the copied list limited to `limit`.
          ```
    - [ ] 7.2 [Comment #2296441053] In python/src/server/repositories/implementations/mock_repositories.py around...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/mock_repositories.py around
lines 841 to 848, the validation currently uses re.match which allows prefix
matches; change it to use re.fullmatch so the entire value must match the regex.
Replace the re.match(pattern, value) call with re.fullmatch(pattern, value) (you
can keep the inline import), so the function returns bool(re.fullmatch(pattern,
value)) when a validation_regex exists.
          ```
    - [ ] 7.3 Verify all changes in python/src/server/repositories/implementations/mock_repositories.py work correctly
- [ ] 8. Fix issues in python/src/server/repositories/implementations/supabase_database.py (4 items)
    - [ ] 8.1 [Comment #2296441054] In python/src/server/repositories/implementations/supabase_database.py around...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/supabase_database.py around
lines 28 to 36, the SupabaseDatabase class declares it implements IUnitOfWork
but does not provide the required methods (begin, is_active, savepoint,
rollback_to_savepoint, release_savepoint), causing instantiation to fail; add
these methods with interface-compatible signatures and minimal no-op semantics:
add an internal boolean (e.g., self._active) set in __init__, implement begin()
to set _active True, is_active() to return _active, implement savepoint(name) to
record a savepoint id/name in an internal stack or dict and return an
identifier, rollback_to_savepoint(name_or_id) to validate and restore internal
state minimally (no DB interaction) and release_savepoint(name_or_id) to remove
it; ensure methods match the abstract base method names and return types so the
class can be instantiated.
          ```
    - [ ] 8.2 [Comment #2296441056] In python/src/server/repositories/implementations/supabase_database.py around...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/supabase_database.py around
lines 160-181, the commit() and rollback() methods currently silently no-op;
update them to first validate the repository's active-transaction state (raise a
clear exception such as RuntimeError if no active transaction exists using the
class's existing active flag or method), then keep the Supabase-specific
behavior as no-ops: commit should do nothing after validation and rollback
should log a warning and do nothing after validation; also update the docstrings
to state that these methods will raise when no active transaction and otherwise
are no-ops for Supabase.
          ```
    - [ ] 8.3 [Comment #2296441058] In python/src/server/repositories/implementations/supabase_database.py around...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/supabase_database.py around
lines 183 to 205, the health_check method logs exceptions without stack traces;
update the exception logging to include exc_info=True (or pass the exception via
logger.exception) so the full stack trace is preserved for diagnostics, ensuring
the logger.error/logger.exception call includes exc_info=True and then return
False as before.
          ```
    - [ ] 8.4 [Comment #2296735145] In python/src/server/repositories/implementations/supabase_database.py around...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/supabase_database.py around
lines 288 to 310, the health_check method calls the synchronous Supabase client
directly which blocks the event loop; refactor to run the blocking client call
inside asyncio.to_thread and add a simple retry loop with exponential backoff
(e.g., 3 attempts, increasing sleep between attempts) so the method remains
async and resilient; ensure each attempt logs warnings on failure, returns True
on success, and logs the error and returns False after retries are exhausted,
and keep exception handling to capture and log details (use asyncio.sleep for
backoff).
          ```
    - [ ] 8.5 Verify all changes in python/src/server/repositories/implementations/supabase_database.py work correctly
- [ ] 9. Fix issues in python/src/server/repositories/implementations/supabase_repositories.py (14 items)
    - [ ] 9.1 [Comment #2296441059] In python/src/server/repositories/implementations/supabase_repositories.py...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/supabase_repositories.py
around lines 53 to 61, the method performs blocking synchronous Supabase client
calls inside an async function and lacks retries and proper stack-trace logging;
change the synchronous client call to run in a thread using asyncio.to_thread
(await asyncio.to_thread(...)) and wrap the call in a retry loop with
exponential backoff (use tenacity or a shared backoff helper) that re-raises the
final exception, and when catching log the error with full context using
logger.exception or logger.error(..., exc_info=True) so the stack trace is
preserved; apply this pattern so the function returns the fetched row or None
after exhausted retries.
          ```
    - [ ] 9.2 [Comment #2296441060] In python/src/server/repositories/implementations/supabase_repositories.py...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/supabase_repositories.py
around lines 59-60, 120-121, 253-254, 314-315, 548-549, 609-610, 763-765, and
833-834, the code calls self._logger.error(..., f"...{e}") which discards the
exception stack; replace those logger.error calls with
self._logger.exception(...) (keeping the same message string) so the full stack
trace is preserved in logs, and ensure any return/raise logic remains unchanged
after the logging call.
          ```
    - [ ] 9.3 [Comment #2296441061] In python/src/server/repositories/implementations/supabase_repositories.py...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/supabase_repositories.py
around lines 360 to 381, the metadata_filter argument is accepted by
vector_search but never forwarded to the Supabase RPC call; update the params
sent to self._client.rpc to include metadata_filter (e.g.,
params['metadata_filter'] = metadata_filter) or transform/serialize it to the
shape the RPC expects (JSON/dict), and ensure you only add it when not None; if
the RPC truly doesn't support metadata filtering, add a clear comment or log
warning stating metadata_filter is currently ignored.
          ```
    - [ ] 9.4 [Comment #2296441064] In python/src/server/repositories/implementations/supabase_repositories.py...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/supabase_repositories.py
around lines 878-921, upsert currently persists the value before any regex
validation; update it to validate the provided value against validation_regex
(when validation_regex is not None) before calling insert/update, using
re.fullmatch (or the project's regex utility) and raising the
repository/validation-specific ValidationError if it fails; place the check
after constructing setting_data and before calling
self._client.table(...).insert/update, and ensure the error is raised (not
swallowed) so the DB call never runs on invalid input.
          ```
    - [ ] 9.5 [Comment #2296441065] In python/src/server/repositories/implementations/supabase_repositories.py...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/supabase_repositories.py
around lines 922-939, the methods claim to handle encrypted values but only log
warnings and still mark values as encrypted, creating a false sense of security;
change behavior so you do not store plaintext as encrypted: either integrate the
app's encryption service/KMS (e.g., obtain encryption key from config/secret
manager and perform encryption in set_encrypted and decryption in get_decrypted)
and then call upsert/upsert result with encrypted=True, or if encryption is not
available yet, raise NotImplementedError from both set_encrypted and
get_decrypted when is_encrypted=True (and do not call upsert with
encrypted=True) so callers cannot store or retrieve values marked encrypted
until real encryption is implemented.
          ```
    - [ ] 9.6 [Comment #2296441066] In python/src/server/repositories/implementations/supabase_repositories.py...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/supabase_repositories.py
around lines 993-997, the exported_at value incorrectly uses str(UUID().hex);
replace this with a proper ISO timestamp by using datetime.now().isoformat()
(and add the required import: from datetime import datetime) so exported_at is a
valid timestamp consistent with the mock implementation; also remove any unused
UUID import if it becomes unused.
          ```
    - [ ] 9.7 [Comment #2296441067] In python/src/server/repositories/implementations/supabase_repositories.py...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/supabase_repositories.py
around lines 1107 to 1113, the get_by_project implementation currently restricts
non-closed tasks to only TaskStatus.TODO, which wrongly excludes DOING/REVIEW;
change the filter so that when include_closed is False it excludes DONE tasks
instead (e.g., set filters to express status != TaskStatus.DONE.value or include
all non-DONE statuses) so the list call returns TODO/DOING/REVIEW rather than
only TODO.
          ```
    - [ ] 9.8 [Comment #2296441068] python/src/server/repositories/implementations/supabase_repositories.py lines...
          ```
          Original AI Prompt:
          python/src/server/repositories/implementations/supabase_repositories.py lines
1588-1712: the vector_search and helper methods are added via module-level
monkey-patching which breaks readability, static analysis and typing; move
vector_search, _calculate_text_relevance and _calculate_code_relevance into the
SupabaseCodeExampleRepository class as normal methods (preserve async for
vector_search and its signature), remove the
_add_vector_search_to_code_repository wrapper and its invocation, add
appropriate type hints and self usages, update the ICodeExampleRepository
interface if vector_search belongs to the contract, and adjust/extend tests to
import the class directly (no dynamic assignment) and ensure logging/error
handling behavior and return types remain identical.
          ```
    - [ ] 9.9 [Comment #2296735146] In python/src/server/repositories/implementations/supabase_repositories.py...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/supabase_repositories.py
around lines 98 to 106, the update() method is performing a blocking call to the
Supabase client and logging exceptions without exception info; change the call
to run in the event loop (either await an async client.execute() if available or
wrap the blocking call with asyncio.to_thread / run_in_executor) so the
coroutine does not block, and update the logger.error call to include
exc_info=True (or pass the exception) so stack trace/details are captured in
logs.
          ```
    - [ ] 9.10 [Comment #2296735148] In python/src/server/repositories/implementations/supabase_repositories.py...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/supabase_repositories.py
around lines 107 to 115, the delete method performs a potentially blocking
.execute() synchronously and logs exceptions without traceback; change the call
to run in the event loop's default executor (e.g. use
asyncio.get_running_loop().run_in_executor(None, lambda:
self._client.table(self._table).delete().eq('id', str(id)).execute())) and await
its result, then return based on response.data, and when catching exceptions
call self._logger.error(f"Failed to delete source {id}", exc_info=True) to
include exception details.
          ```
    - [ ] 9.11 [Comment #2296735151] In python/src/server/repositories/implementations/supabase_repositories.py...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/supabase_repositories.py
around lines 271 to 282, the synchronous .execute() call blocks the event loop
and the current except logging does not include the full stack trace; change the
method to offload the blocking insert to a thread using asyncio.to_thread (or
loop.run_in_executor), await the result, and keep the same return behavior if
response.data exists; on error log the exception with the traceback (use
logger.exception or logger.error(..., exc_info=True)) and re-raise the original
exception (use plain raise) so the stack trace is preserved; add the necessary
asyncio import if not present.
          ```
    - [ ] 9.12 [Comment #2296735154] In python/src/server/repositories/implementations/supabase_repositories.py...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/supabase_repositories.py
around lines 754 to 762, the async function calls the blocking .execute()
directly which can block the event loop and the except block loses stack
context; wrap the blocking call in asyncio.to_thread (or loop.run_in_executor)
and await it so execution is offloaded from the event loop, and replace the
.error log with self._logger.exception("Failed to search projects by title") (or
include exc_info=True) to preserve the full stack trace; also add the required
asyncio import if missing and keep returning an empty list on failure.
          ```
    - [ ] 9.13 [Comment #2296735155] In python/src/server/repositories/implementations/supabase_repositories.py...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/supabase_repositories.py
around lines 1094 to 1101, the create method currently logs exceptions without
stack traces and runs the blocking insert synchronously; change it to offload
the blocking self._client.table(...).insert(...).execute() call to a thread
(e.g., asyncio.to_thread or loop.run_in_executor) and await the result, and when
catching exceptions use self._logger.exception(...) (or logger.error with
exc_info=True) to preserve the traceback before re-raising; finally ensure you
return response.data[0] or {} as before after the awaited call.
          ```
    - [ ] 9.14 [Comment #2296735156] In python/src/server/repositories/implementations/supabase_repositories.py...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/supabase_repositories.py
around lines 1493 to 1504, the current try/except swallows all exceptions
(losing stack traces) while building and executing the Supabase text_search
query; refactor so that query construction remains inside the function but the
call to response = search_query.execute() is not inside a broad try/except —
either remove the blanket try/except entirely or replace it with narrow,
specific exception handling for known recoverable errors, and let unexpected
exceptions propagate (or re-raise them) so stack traces are preserved instead of
returning an empty list.
          ```
    - [ ] 9.15 Verify all changes in python/src/server/repositories/implementations/supabase_repositories.py work correctly
- [ ] 10. Fix issues in python/src/server/repositories/interfaces/__init__.py (1 items)
    - [ ] 10.1 [Comment #2296441070] In python/src/server/repositories/interfaces/__init__.py around lines 63 to 96...
          ```
          Original AI Prompt:
          In python/src/server/repositories/interfaces/__init__.py around lines 63 to 96
the export and typing for the unit-of-work transaction context is inconsistent
with implementations: update the IUnitOfWork.transaction return type to
AsyncContextManager["IUnitOfWork"] (or AsyncContextManager[TUnitOfWork] with a
typevar) so the async with yields the unit-of-work instance rather than None;
ensure you keep from __future__ import annotations at top of unit_of_work.py,
import AsyncContextManager from typing, add or adjust any forward refs and
typevars as needed, then run mypy across tests and implementations to confirm no
new type errors.
          ```
    - [ ] 10.2 Verify all changes in python/src/server/repositories/interfaces/__init__.py work correctly
- [ ] 11. Fix issues in python/src/server/repositories/interfaces/knowledge_repository.py (3 items)
    - [ ] 11.1 [Comment #2296441071] In python/src/server/repositories/interfaces/knowledge_repository.py around...
          ```
          Original AI Prompt:
          In python/src/server/repositories/interfaces/knowledge_repository.py around
lines 81-100, the abstract method update_metadata claims to "merge" metadata but
implementations currently overwrite it; update the contract and implementations
to match by implementing a true merge: change the interface docstring to specify
a recursive/deep-merge policy (or explicitly state shallow merge if you prefer),
then in the Supabase implementation perform a safe DB-side JSONB merge (use
Postgres jsonb || or jsonb_build_object with a client-side computed merged dict
and an UPDATE returning the merged JSON) and in the mock implementation perform
the same merge logic in-memory (recursive dict merge that preserves existing
keys unless overwritten by provided metadata), and ensure error handling and
return values remain unchanged; alternatively, if you decide to keep replace
semantics, update the docstring here to say "replace metadata" and adjust
implementations' docstrings to match.
          ```
    - [ ] 11.2 [Comment #2296441072] In python/src/server/repositories/interfaces/knowledge_repository.py around...
          ```
          Original AI Prompt:
          In python/src/server/repositories/interfaces/knowledge_repository.py around
lines 188-211, the vector_search docstring is ambiguous about where similarity
scores should live; update the docstring to define a canonical result shape
(e.g., each result is a Dict with keys "id", "content", "metadata" where
metadata is a Dict that MUST include "similarity_score": float) and adjust the
declared return type comment to reflect that metadata.similarity_score is
required; then update all implementations (mock, Supabase repo, etc.) to
normalize their outputs to this canonical shape by moving any top-level
similarity fields or raw RPC score columns into
result["metadata"]["similarity_score"] and ensure ordering by that score before
returning, and add a short test or assertion in each implementation that
verifies metadata contains similarity_score as a float.
          ```
    - [ ] 11.3 [Comment #2296441073] In python/src/server/repositories/interfaces/knowledge_repository.py around...
          ```
          Original AI Prompt:
          In python/src/server/repositories/interfaces/knowledge_repository.py around
lines 213-241, the hybrid_search docstring promises a ValidationError if
keyword_weight + vector_weight != 1.0 but implementations don't enforce it;
update mock_repositories.py (around line 334) and supabase_repositories.py
(around line 383) to validate the two weights at the start of hybrid_search and
raise ValidationError when their sum differs from 1.0 within a small epsilon
(e.g., 1e-6); alternatively, if you prefer auto-normalization, replace the
validation with code that divides each weight by their sum and document that
behavior in the docstring—implement one consistent approach across both files
and add/update unit tests accordingly.
          ```
    - [ ] 11.4 Verify all changes in python/src/server/repositories/interfaces/knowledge_repository.py work correctly
- [ ] 12. Fix issues in python/src/server/repositories/interfaces/project_repository.py (3 items)
    - [ ] 12.1 [Comment #2296441074] In python/src/server/repositories/interfaces/project_repository.py around lines...
          ```
          Original AI Prompt:
          In python/src/server/repositories/interfaces/project_repository.py around lines
49 to 63, the get_with_tasks interface promises to "Retrieve a project with all
associated tasks included" but the SupabaseProjectRepository implementation only
returns the project; fix by ensuring the implementation returns the project dict
with a "tasks" key containing the list of associated task dicts (query tasks
table filtering by project_id and attach them to the project before returning),
or if you prefer the lighter change, update this interface docstring to say
"returns the project; tasks fetched separately" and adjust the return
typing/docs accordingly so interface and implementation match. Ensure the chosen
fix keeps the return type Optional[Dict[str, Any]] and clearly documents the
"tasks" field when present.
          ```
    - [ ] 12.2 [Comment #2296441075] In python/src/server/repositories/interfaces/project_repository.py around lines...
          ```
          Original AI Prompt:
          In python/src/server/repositories/interfaces/project_repository.py around lines
65 to 87, the abstract method update_jsonb_field documents raising
ValidationError for invalid field_name but does not enforce validation; add
explicit validation against an allowed set {'prd','docs','features','data'} at
the start of the method and raise ValidationError if field_name is not in the
set, documenting the behavior; ensure implementations of this interface either
call super validation or duplicate the same check so invalid names are rejected
before any DB operation.
          ```
    - [ ] 12.3 [Comment #2296441076] python/src/server/repositories/interfaces/project_repository.py lines 89-110:...
          ```
          Original AI Prompt:
          python/src/server/repositories/interfaces/project_repository.py lines 89-110:
the abstract method promises a merge that preserves existing JSONB content but
implementations replace or simplify; implement true read-modify-write merging in
the Supabase and Mock repository implementations: first read the existing JSONB
field for project_id, perform a deterministic merge that recursively deep-merges
dicts (keys from value overwrite or merge into nested dicts), merges arrays by
appending non-duplicates (or by a specified merge policy), handle None/missing
fields by treating them as empty structures, write the merged JSONB back inside
a transaction, return the updated record, and propagate database errors as
RepositoryError; alternatively, if you cannot implement full recursive
semantics, update this interface docstring to precisely describe the concrete
merge semantics implemented (shallow vs recursive, array policy) and ensure
implementations match that documented contract.
          ```
    - [ ] 12.4 Verify all changes in python/src/server/repositories/interfaces/project_repository.py work correctly
- [ ] 13. Fix issues in python/src/server/repositories/interfaces/unit_of_work.py (3 items)
    - [ ] 13.1 [Comment #2296441079] In python/src/server/repositories/interfaces/unit_of_work.py around lines 34 to...
          ```
          Original AI Prompt:
          In python/src/server/repositories/interfaces/unit_of_work.py around lines 34 to
58, the transaction() signature and docstring state AsyncContextManager[None]
but implementations (e.g., SupabaseDatabase.transaction) yield the unit-of-work
instance; change the type to AsyncContextManager[Self] and update the docstring
to state the context yields the unit-of-work (or a transaction-scoped UoW) so
type checkers and callers can use the yielded self; import Self (or
typing_extensions.Self for older Pythons) and update any concrete
implementations/tests to match the new return type.
          ```
    - [ ] 13.2 [Comment #2296441080] In python/src/server/repositories/interfaces/unit_of_work.py around lines...
          ```
          Original AI Prompt:
          In python/src/server/repositories/interfaces/unit_of_work.py around lines
195-207, the TransactionError constructor currently calls logger.error(...,
exc_info=original_error) which is incorrect (exc_info expects a bool or
exception tuple) and causes duplicate logging when exceptions are later handled;
remove logging from the exception constructor, simply store original_error on
self (and message via super()), and if you need traceback-aware logging do it at
the call site where the exception is caught using logger.exception(...) or
logger.error(..., exc_info=True) so the full traceback is logged exactly once.
          ```
    - [ ] 13.3 [Comment #2296735157] In python/src/server/repositories/interfaces/unit_of_work.py around lines 52–54...
          ```
          Original AI Prompt:
          In python/src/server/repositories/interfaces/unit_of_work.py around lines 52–54
(and also at 169–171 and 183–184) the docstrings reference undefined exceptions
like DatabaseError and RepositoryError; update these docstrings to either
import/define and reference centralized exception classes (e.g., add/import
DatabaseError and RepositoryError from a common exceptions module) or replace
the named types with a generic description such as "backend-specific database
error" or "repository operation error" (or point to the actual concrete
exception types implementations will raise), and make the same docstring updates
across all repository interface modules where RepositoryError appears.
          ```
    - [ ] 13.4 Verify all changes in python/src/server/repositories/interfaces/unit_of_work.py work correctly
- [ ] 14. Fix issues in python/tests/test_repository_interfaces.py (1 items)
    - [ ] 14.1 [Comment #2296735158] In python/src/server/repositories/implementations/mock_repositories.py around...
          ```
          Original AI Prompt:
          In python/src/server/repositories/implementations/mock_repositories.py around
lines 951 and 1038, the MockSourceRepository.list() and
MockVersionRepository.list() functions currently ignore
order_by/order_direction; update both to apply explicit sorting before
limit/offset by: when order_by is provided, call sorted(results, key=lambda r:
(r.get(order_by) or ''), reverse=(order_direction=='desc')) so missing or None
values are treated as empty strings and Python’s stable sort preserves insertion
order for ties; ensure sorting occurs prior to applying offset/limit and keep
behavior unchanged when order_by is falsy.
          ```
    - [ ] 14.2 Verify all changes in python/tests/test_repository_interfaces.py work correctly
- [ ] 15. Fix issues in python/tests/test_supabase_repositories.py (2 items)
    - [ ] 15.1 [Comment #2296441081] In python/tests/test_supabase_repositories.py around lines 442 to 447, the test...
          ```
          Original AI Prompt:
          In python/tests/test_supabase_repositories.py around lines 442 to 447, the test
sets mock_table.select.return_value.execute.side_effect but health_check() calls
select(...).limit(1).execute(), so the exception is never raised; update the
mock to set the side effect on the limit() call instead
(mock_table.select.return_value.limit.return_value.execute.side_effect =
Exception("Database error")) so the error is raised at the actual execute()
invoked by health_check(), leaving the insert/update/delete side-effects as-is.
          ```
    - [ ] 15.2 [Comment #2296441082] In python/tests/test_supabase_repositories.py around lines 450-460, the test...
          ```
          Original AI Prompt:
          In python/tests/test_supabase_repositories.py around lines 450-460, the test
currently asserts result in [True, False] which is non-deterministic and masks
regressions; change the test to expect False unambiguously and verify that an
error was logged: update the mock to raise on limit().execute(), call
database.health_check() inside a caplog context (or use the caplog fixture),
assert result is False, and assert caplog contains an error-level record with a
message indicating the health check/query failure.
          ```
    - [ ] 15.3 Verify all changes in python/tests/test_supabase_repositories.py work correctly

- [ ] 16. Post-implementation tasks
    - [ ] 16.1 Run full test suite
    - [ ] 16.2 Mark all resolved comments on GitHub
    - [ ] 16.3 Post summary comment on PR
