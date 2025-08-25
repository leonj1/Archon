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

<pre_flight_check>
  EXECUTE: @.agent-os/instructions/meta/pre-flight.md
</pre_flight_check>

<process_flow>

<step number="1" name="pr_input_validation">

### Step 1: PR Input Validation

Validate and parse the GitHub PR URL or reference provided by the user.

<input_formats>
  <full_url>https://github.com/{owner}/{repo}/pull/{number}</full_url>
  <cli_format>{owner}/{repo}#{number}</cli_format>
  <local_format>#{number} (if in repo directory)</local_format>
</input_formats>

<validation>
  - Extract owner, repo, and PR number
  - Verify PR exists and is accessible
  - Store PR metadata for later use
</validation>

<decision_tree>
  IF input_invalid:
    ASK user for correct PR URL
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
    {END FOR}
    - [ ] {task_number}.{last_subtask} Verify all changes in {file_path} work correctly
  {END FOR}

  - [ ] {final_task_number}. Post-implementation tasks
    - [ ] {final_task_number}.1 Run full test suite
    - [ ] {final_task_number}.2 Mark all resolved comments on GitHub
    - [ ] {final_task_number}.3 Post summary comment on PR
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

<step number="10" name="prepare_execution">

### Step 10: Prepare for Execution

Present summary to user and provide guidance for task execution.

<summary_presentation>
  I've successfully imported {prompt_count} AI prompts from PR #{number} and created:

  - Spec Requirements: @.agent-os/specs/{folder_name}/spec.md
  - Task List: @.agent-os/specs/{folder_name}/tasks.md
  - Comment Mapping: @.agent-os/specs/{folder_name}/comment-map.json

  The tasks are organized by affected files with {file_count} major tasks.

  To execute these tasks, run: `/execute-tasks`

  Each completed task will automatically:
  1. Implement the suggested code change
  2. Mark the corresponding GitHub comment as resolved
  3. Post a completion reply to the comment
</summary_presentation>

</step>

</process_flow>

## Post-Execution Integration

<comment_resolution_workflow>
  AFTER each task completion:
    1. READ comment-map.json for task-to-comment mapping
    2. EXECUTE GitHub CLI to add reaction:
       gh api repos/{owner}/{repo}/issues/comments/{comment_id}/reactions -f content='+1'
    3. OPTIONALLY post completion reply:
       gh api repos/{owner}/{repo}/issues/comments -f body='✅ Implemented in [commit]'
    4. UPDATE comment-map.json with resolution status
</comment_resolution_workflow>

<completion_summary>
  AFTER all tasks complete:
    1. Generate summary of all resolved prompts
    2. Post summary comment on PR
    3. Report completion statistics
</completion_summary>

<post_flight_check>
  EXECUTE: @.agent-os/instructions/meta/post-flight.md
</post_flight_check>