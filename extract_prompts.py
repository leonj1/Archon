import json
import re

with open('ai_prompts.json', 'r') as f:
    comments = json.load(f)

prompts = []
for comment in comments:
    prompt_match = re.search(r'```\n(.*?)\n```', comment['body'], re.DOTALL)
    if prompt_match:
        prompt_text = prompt_match.group(1).strip()
        
        # Extract file path from prompt or comment
        file_path = comment.get('path', '')
        
        # Extract line info
        line = comment.get('line', '')
        
        prompts.append({
            'comment_id': comment['id'],
            'node_id': comment['node_id'],
            'file_path': file_path,
            'line': line,
            'prompt': prompt_text,
            'body': comment['body']
        })

# Group by file
files_map = {}
for prompt in prompts:
    file_path = prompt['file_path'] or 'unknown'
    if file_path not in files_map:
        files_map[file_path] = []
    files_map[file_path].append(prompt)

print(f"Total prompts: {len(prompts)}")
print(f"Files affected: {len(files_map)}")
for file_path, file_prompts in files_map.items():
    print(f"  {file_path}: {len(file_prompts)} prompts")

with open('prompts_grouped.json', 'w') as f:
    json.dump(files_map, f, indent=2)
