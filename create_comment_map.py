import json

with open('prompts_grouped.json', 'r') as f:
    grouped = json.load(f)

comment_map = {
    "pr_url": "https://github.com/coleam00/Archon/pull/375",
    "owner": "coleam00",
    "repo": "Archon", 
    "pr_number": 375,
    "task_to_comment": {},
    "resolution_commands": {
        "mark_resolved": "gh api repos/coleam00/Archon/issues/comments/{comment_id}/reactions -f content='+1'",
        "post_reply": "gh api repos/coleam00/Archon/issues/comments -f body='✅ This suggestion has been implemented in commit {commit_sha}'"
    }
}

task_num = 1
for file_path, prompts in grouped.items():
    for idx, prompt in enumerate(prompts, 1):
        task_key = f"{task_num}.{idx}"
        comment_map["task_to_comment"][task_key] = {
            "comment_id": prompt["comment_id"],
            "node_id": prompt["node_id"],
            "thread_id": None,
            "file": file_path
        }
    task_num += 1

with open('.agent-os/specs/2025-08-26-ai-prompts-pr-375/comment-map.json', 'w') as f:
    json.dump(comment_map, f, indent=2)
    
print(f"Created comment map with {len(comment_map['task_to_comment'])} task mappings")
