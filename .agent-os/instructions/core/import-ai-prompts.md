---
description: Import CodeRabbit AI prompts from GitHub PRs and create executable tasks
globs:
alwaysApply: false
version: 1.0
encoding: UTF-8
---

# Import AI Prompts Rules

## Overview

Import AI-generated code improvement prompts from GitHub pull request comments (specifically CodeRabbit reviews) and convert them into executable Agent OS tasks, with automatic comment resolution upon completion.

### Safety Features

This command includes several safety checks to prevent applying fixes to the wrong project or branch:

1. **Repository Verification**: Ensures the PR belongs to the current repository
2. **Branch Verification**: Confirms you're on the correct branch or offers to switch
3. **PR State Check**: Warns if the PR is closed or merged
4. **User Confirmation**: Requires explicit confirmation for any mismatches

These checks prevent accidentally applying fixes meant for:
- Different repositories
- Different branches
- Already merged or closed PRs

<pre_flight_check>
  EXECUTE: @.agent-os/instructions/meta/pre-flight.md
</pre_flight_check>

<process_flow>

<step number="1" name="pr_input_validation">

### Step 1: PR Input Validation

Validate and parse the GitHub PR URL or reference provided by the user, ensuring it matches the current repository and branch.

<input_formats>
  <full_url>https://github.com/{owner}/{repo}/pull/{number}</full_url>
  <cli_format>{owner}/{repo}#{number}</cli_format>
  <local_format>#{number} (if in repo directory)</local_format>
</input_formats>

<validation>
  - Extract owner, repo, and PR number
  - Verify PR exists and is accessible
  - Store PR metadata for later use
  - Verify branch compatibility (see branch_verification below)
</validation>

<repository_verification>
  # Get current repository info
  CURRENT_REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
  PR_REPO="{owner}/{repo}"
  
  # Verify we're in the correct repository
  IF current_repo != PR_REPO:
    ERROR "Repository mismatch!"
    ERROR "PR is for repository: $PR_REPO"
    ERROR "Current repository: $CURRENT_REPO"
    EXIT "Cannot apply PR from different repository"
</repository_verification>

<branch_verification>
  # Get current local branch
  CURRENT_BRANCH=$(git branch --show-current)
  
  # Get PR details including base branch
  PR_INFO=$(gh api repos/{owner}/{repo}/pulls/{number} --jq '.base.ref,.head.ref,.state')
  PR_BASE_BRANCH=$(echo "$PR_INFO" | sed -n '1p')
  PR_HEAD_BRANCH=$(echo "$PR_INFO" | sed -n '2p')
  PR_STATE=$(echo "$PR_INFO" | sed -n '3p')
  
  # Check if PR is still open
  IF PR_STATE != "open":
    WARN "PR #{number} is $PR_STATE (not open)"
    CONFIRM "Continue importing prompts from $PR_STATE PR?"
    IF no:
      EXIT "Cancelled: PR is not open"
  
  # Verify we're on the correct branch
  IF current_branch != PR_HEAD_BRANCH:
    WARN "Branch mismatch detected!"
    INFO "PR branch: $PR_HEAD_BRANCH (targeting $PR_BASE_BRANCH)"
    INFO "Current branch: $CURRENT_BRANCH"
    
    # Check if PR branch exists locally or remotely
    IF git show-ref --verify --quiet refs/heads/$PR_HEAD_BRANCH:
      ASK "Switch to PR branch '$PR_HEAD_BRANCH'? (recommended)"
      IF yes:
        git checkout $PR_HEAD_BRANCH
        git pull origin $PR_HEAD_BRANCH
    ELIF git ls-remote --heads origin $PR_HEAD_BRANCH:
      ASK "Create and checkout PR branch '$PR_HEAD_BRANCH' from remote? (recommended)"
      IF yes:
        git checkout -b $PR_HEAD_BRANCH origin/$PR_HEAD_BRANCH
    ELSE:
      WARN "PR branch '$PR_HEAD_BRANCH' not found locally or remotely"
      CONFIRM "Apply PR #{number} fixes to current branch '$CURRENT_BRANCH'?"
      IF no:
        EXIT "Cancelled: Branch mismatch"
</branch_verification>

<decision_tree>
  IF input_invalid:
    ASK user for correct PR URL
  ELIF branch_mismatch AND user_cancelled:
    EXIT with message about branch mismatch
  ELSE:
    PROCEED to fetch comments
</decision_tree>

</step>

<step number="2" name="fetch_pr_comments">

### Step 2: Fetch PR Comments

Use GitHub CLI to retrieve all comments from the PR, focusing on CodeRabbit AI review comments.

<github_cli_commands>
  # Fetch PR comments with full body content
  gh api repos/{owner}/{repo}/pulls/{number}/comments --paginate > pr_comments.json
  
  # Also fetch issue comments (some bots post here)
  gh api repos/{owner}/{repo}/issues/{number}/comments --paginate > issue_comments.json
</github_cli_commands>

<comment_filtering>
  - Filter for comments by 'coderabbitai' user
  - Look for "🤖 Prompt for AI Agents" marker
  - Extract comment ID for later resolution
</comment_filtering>

</step>

<step number="3" name="extract_ai_prompts">

### Step 3: Extract AI Prompts

Parse comments to extract structured AI prompts with their metadata.

<prompt_structure>
  <marker>🤖 Prompt for AI Agents</marker>
  <format>
    ```
    [PROMPT_CONTENT]
    ```
  </format>
</prompt_structure>

<extraction_logic>
  FOR each comment:
    IF contains "🤖 Prompt for AI Agents":
      EXTRACT prompt text from code block
      EXTRACT file path and line numbers
      EXTRACT comment ID
      STORE in prompts array
</extraction_logic>

<prompt_parsing>
  - File path: Extract from prompt text
  - Line range: Parse "around lines X-Y" pattern
  - Action: Identify the required change
  - Rationale: Capture the reasoning
</prompt_parsing>

</step>

<step number="4" subagent="date-checker" name="date_determination">

### Step 4: Date Determination

Use the date-checker subagent to determine the current date for folder naming.

<subagent_output>
  The date-checker subagent will provide the current date in YYYY-MM-DD format for use in folder naming.
</subagent_output>

</step>

<step number="5" subagent="file-creator" name="create_spec_folder">

### Step 5: Create Spec Folder

Use the file-creator subagent to create the spec folder structure.

<folder_naming>
  <format>YYYY-MM-DD-ai-prompts-pr-{number}</format>
  <location>.agent-os/specs/</location>
  <example>2025-01-25-ai-prompts-pr-116</example>
</folder_naming>

</step>

<step number="6" subagent="file-creator" name="create_spec_md">

### Step 6: Create spec.md

Use the file-creator subagent to create the spec document summarizing the imported prompts.

<file_template>
  # Spec Requirements Document

  > Spec: AI Prompts from PR #{number}
  > Created: [CURRENT_DATE]
  > Source: {owner}/{repo}#{number}

  ## Overview

  Code improvements identified by CodeRabbit AI review on PR #{number}: {pr_title}

  ## User Stories

  ### Automated Code Review Resolution

  As a developer, I want to resolve all AI-identified code issues, so that the codebase maintains high quality standards.

  This spec addresses {prompt_count} code improvement suggestions from the automated review.

  ## Spec Scope

  {FOR each unique file affected:}
  1. **{file_path}** - Address {count} improvement suggestions
  {END FOR}

  ## Out of Scope

  - Feature additions beyond the AI suggestions
  - Refactoring outside the identified areas
  - Changes to unrelated files

  ## Expected Deliverable

  1. All {prompt_count} AI prompts resolved and implemented
  2. Each resolved comment marked as completed on GitHub
  3. Code changes pass all existing tests
</file_template>

</step>

<step number="7" subagent="file-creator" name="create_spec_lite">

### Step 7: Create spec-lite.md

Use the file-creator subagent to create a condensed spec summary.

<file_template>
  # Spec Summary (Lite)

  Resolve {prompt_count} AI-identified code improvements from PR #{number} CodeRabbit review. Implement suggested fixes for {unique_file_count} files and mark GitHub comments as resolved upon completion.
</file_template>

</step>

<step number="8" subagent="file-creator" name="create_tasks_md">

### Step 8: Create tasks.md

Use the file-creator subagent to create the tasks file with each AI prompt as an executable task.

<task_organization>
  - Group prompts by file
  - Each file becomes a major task
  - Each prompt becomes a subtask
  - Include comment ID for resolution tracking
</task_organization>

<file_template>
  # Spec Tasks

  ## Tasks

  {FOR each file with prompts:}
  - [ ] {task_number}. Fix issues in {file_path} ({prompt_count} items)
    {FOR each prompt in file:}
    - [ ] {task_number}.{subtask_number} [Comment #{comment_id}] {brief_description}
          ```
          Original AI Prompt:
          {full_prompt_text}
          ```
          
          **Post-Completion Action:**
          ```bash
          # Auto-resolve GitHub comment after implementing this fix
          gh api repos/{owner}/{repo}/issues/comments/{comment_id}/reactions -f content='+1'
          gh api repos/{owner}/{repo}/issues/comments -f body="✅ Implemented: {brief_description} in commit \$(git rev-parse HEAD)"
          ```
    {END FOR}
    - [ ] {task_number}.{last_subtask} Verify all changes in {file_path} work correctly
  {END FOR}

  - [ ] {final_task_number}. Post-implementation tasks
    - [ ] {final_task_number}.1 Run full test suite
    - [ ] {final_task_number}.2 Verify all comments marked as resolved
    - [ ] {final_task_number}.3 Post summary comment on PR with stats
</file_template>

</step>

<step number="9" subagent="file-creator" name="create_comment_map">

### Step 9: Create Comment Mapping

Use the file-creator subagent to create a JSON file mapping tasks to GitHub comment IDs.

<file_location>.agent-os/specs/YYYY-MM-DD-ai-prompts-pr-{number}/comment-map.json</file_location>

<file_template>
  {
    "pr_url": "{full_pr_url}",
    "owner": "{owner}",
    "repo": "{repo}",
    "pr_number": {number},
    "task_to_comment": {
      "1.1": {comment_id_1},
      "1.2": {comment_id_2},
      "2.1": {comment_id_3},
      ...
    },
    "resolution_commands": {
      "mark_resolved": "gh api repos/{owner}/{repo}/issues/comments/{comment_id}/reactions -f content='+1'",
      "post_reply": "gh api repos/{owner}/{repo}/issues/comments -f body='✅ This suggestion has been implemented in commit {commit_sha}'"
    }
  }
</file_template>

</step>

<step number="10" subagent="file-creator" name="create_resolution_script">

### Step 10: Create Resolution Script

Use the file-creator subagent to create a helper script for comment resolution.

<file_location>.agent-os/specs/YYYY-MM-DD-ai-prompts-pr-{number}/resolve-comment.sh</file_location>

<file_template>
  #!/bin/bash
  # GitHub Comment Resolution Helper
  # Usage: ./resolve-comment.sh TASK_NUMBER COMMENT_ID
  
  TASK_NUMBER=$1
  COMMENT_ID=$2
  OWNER="{owner}"
  REPO="{repo}"
  PR_NUMBER={number}
  
  if [ -z "$COMMENT_ID" ]; then
    echo "Usage: $0 TASK_NUMBER COMMENT_ID"
    exit 1
  fi
  
  # Get current commit SHA
  COMMIT_SHA=$(git rev-parse HEAD)
  
  # Add reaction to comment
  echo "Adding ✅ reaction to comment #$COMMENT_ID..."
  gh api repos/$OWNER/$REPO/issues/comments/$COMMENT_ID/reactions -f content='+1'
  
  # Post resolution comment
  echo "Posting resolution confirmation..."
  gh api repos/$OWNER/$REPO/issues/comments -f body="✅ **Implemented** (Task $TASK_NUMBER)
  
  This suggestion has been applied in commit \`$COMMIT_SHA\`
  
  ---
  *Resolved by Agent OS import-ai-prompts*"
  
  # Update tracking file
  echo "[$TASK_NUMBER] Comment #$COMMENT_ID resolved at $(date)" >> resolution.log
  
  echo "✅ Comment #$COMMENT_ID marked as resolved!"
</file_template>

<make_executable>
  chmod +x .agent-os/specs/YYYY-MM-DD-ai-prompts-pr-{number}/resolve-comment.sh
</make_executable>

</step>

<step number="11" name="prepare_execution">

### Step 11: Prepare for Execution

Present summary to user and provide guidance for task execution with real-time resolution.

<summary_presentation>
  I've successfully imported {prompt_count} AI prompts from PR #{number} and created:

  📁 **Spec Files Created:**
  - Spec Requirements: `@.agent-os/specs/{folder_name}/spec.md`
  - Task List: `@.agent-os/specs/{folder_name}/tasks.md`
  - Comment Mapping: `@.agent-os/specs/{folder_name}/comment-map.json`
  - Resolution Script: `@.agent-os/specs/{folder_name}/resolve-comment.sh`

  📊 **Task Summary:**
  - Total AI suggestions: {prompt_count}
  - Files to modify: {file_count}
  - GitHub comments to resolve: {prompt_count}

  🚀 **To execute these tasks:**
  ```
  /execute-tasks
  ```

  ✅ **Automatic Resolution:**
  Each completed task will automatically:
  1. Implement the suggested code change
  2. Mark the GitHub comment as resolved with a ✅ reaction
  3. Post a confirmation comment with the commit SHA
  4. Update the resolution log

  📈 **Progress Tracking:**
  - Real-time updates will be posted to PR #{number}
  - Resolution status tracked in `resolution.log`
  - Final summary posted after all tasks complete

  💡 **Manual Resolution (if needed):**
  ```bash
  # To manually resolve a comment:
  ./.agent-os/specs/{folder_name}/resolve-comment.sh TASK_NUMBER COMMENT_ID
  ```
</summary_presentation>

</step>

</process_flow>

## Post-Execution Integration

<task_execution_hook>
  INTEGRATE with /execute-tasks command:
    - Each task includes comment ID in its metadata
    - After EACH individual task completion, trigger resolution
    - Track resolution status in real-time
</task_execution_hook>

<comment_resolution_workflow>
  IMMEDIATELY AFTER each task completion (not batched):
    1. READ comment-map.json for task-to-comment mapping
    2. GET comment_id for completed task (e.g., task "1.1" -> comment_id)
    3. CAPTURE git commit SHA if changes were made:
       COMMIT_SHA=$(git rev-parse HEAD)
    
    4. RESOLVE the GitHub conversation thread:
       # Mark the conversation as resolved
       gh api graphql -f query='
         mutation {
           resolveReviewThread(input: {
             threadId: "{thread_id}",
             clientMutationId: "agent-os-resolution"
           }) {
             thread {
               isResolved
             }
           }
         }'
    
    5. POST implementation confirmation:
       gh api repos/{owner}/{repo}/issues/comments \
         -f body="✅ **Implemented**: This suggestion has been applied in commit \`$COMMIT_SHA\`
         
         The code has been updated as requested:
         - Task {task_number}.{subtask_number} completed
         - Changes verified and tested
         
         cc @coderabbitai - suggestion implemented successfully"
    
    6. ADD reaction to original comment:
       gh api repos/{owner}/{repo}/issues/comments/{comment_id}/reactions \
         -f content='+1'
    
    7. UPDATE comment-map.json with resolution status:
       {
         "task_to_comment": {
           "1.1": {
             "comment_id": {comment_id_1},
             "status": "resolved",
             "resolved_at": "{timestamp}",
             "commit_sha": "{commit_sha}"
           }
         }
       }
    
    8. LOG resolution:
       echo "✅ Resolved GitHub comment #{comment_id} for task {task_number}.{subtask_number}"
</comment_resolution_workflow>

<resolution_error_handling>
  IF resolution fails:
    - LOG warning but continue with next task
    - Track failed resolutions for manual review
    - Include in final summary report
  
  Common resolution issues:
    - Comment already deleted
    - Insufficient permissions
    - Network/API errors
    - Thread already resolved
</resolution_error_handling>

<completion_summary>
  AFTER all tasks complete:
    1. Generate summary of all resolved prompts
    2. Count successful vs failed resolutions
    3. Post comprehensive summary comment on PR:
       
       gh api repos/{owner}/{repo}/issues/{pr_number}/comments \
         -f body="## 🤖 Agent OS: CodeRabbit Suggestions Implementation Summary
         
         Successfully implemented **{resolved_count}/{total_count}** AI suggestions from this PR review.
         
         ### ✅ Resolved Comments
         {FOR each resolved comment:}
         - Comment #{comment_id}: {brief_description} (commit: \`{commit_sha}\`)
         {END FOR}
         
         ### ⚠️ Pending Items (if any)
         {FOR each unresolved:}
         - Comment #{comment_id}: {reason}
         {END FOR}
         
         ### 📊 Statistics
         - Total suggestions processed: {total_count}
         - Successfully implemented: {resolved_count}
         - Execution time: {duration}
         - Files modified: {file_count}
         
         All resolved conversations have been marked as resolved in the PR review thread.
         
         ---
         *Automated by Agent OS import-ai-prompts*"
    
    4. Report completion statistics to console
    5. Suggest next steps (commit, push, etc.)
</completion_summary>

<post_flight_check>
  EXECUTE: @.agent-os/instructions/meta/post-flight.md
</post_flight_check>