import json
import re

with open('prompts_grouped.json', 'r') as f:
    grouped = json.load(f)

tasks_content = """# Spec Tasks

## Tasks

"""

task_num = 1
total_subtasks = 0

# Sort files for consistent ordering
sorted_files = sorted(grouped.items())

for file_path, prompts in sorted_files:
    file_name = file_path if file_path != 'unknown' else 'Various files'
    tasks_content += f"- [ ] {task_num}. Fix issues in {file_name} ({len(prompts)} items)\n"
    
    for idx, prompt in enumerate(prompts, 1):
        # Extract a brief description from the prompt
        prompt_text = prompt['prompt']
        lines = prompt_text.split('\n')
        brief = lines[0][:100] + "..." if len(lines[0]) > 100 else lines[0]
        
        comment_id = prompt['comment_id']
        
        tasks_content += f"""  - [ ] {task_num}.{idx} [Comment #{comment_id}] {brief}
        ```
        Original AI Prompt:
        {prompt_text}
        ```
        
        **Post-Completion Action:**
        ```bash
        # Auto-resolve GitHub comment after implementing this fix
        ./.agent-os/specs/2025-08-26-ai-prompts-pr-375/resolve-comment.sh {task_num}.{idx}
        ```
"""
        total_subtasks += 1
    
    # Add verification task
    tasks_content += f"  - [ ] {task_num}.{len(prompts)+1} Verify all changes in {file_name} work correctly\n"
    tasks_content += "\n"
    task_num += 1

# Add final tasks
tasks_content += f"""- [ ] {task_num}. Post-implementation tasks
  - [ ] {task_num}.1 Run full test suite
  - [ ] {task_num}.2 Verify all comments marked as resolved
  - [ ] {task_num}.3 Post summary comment on PR with stats

## Summary

- Total tasks: {task_num}
- Total AI suggestions to implement: {total_subtasks}
- Files to modify: {len(grouped)}
"""

with open('.agent-os/specs/2025-08-26-ai-prompts-pr-375/tasks.md', 'w') as f:
    f.write(tasks_content)
    
print(f"Created tasks.md with {task_num} main tasks and {total_subtasks} AI suggestions")
