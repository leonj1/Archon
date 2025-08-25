#!/bin/bash
# GitHub Comment Resolution Helper
# Usage: ./resolve-comment.sh TASK_NUMBER COMMENT_ID

TASK_NUMBER=$1
COMMENT_ID=$2
OWNER="coleam00"
REPO="Archon"
PR_NUMBER=375

if [ -z "$COMMENT_ID" ]; then
  echo "Usage: $0 TASK_NUMBER COMMENT_ID"
  exit 1
fi

# Get current commit SHA
COMMIT_SHA=$(git rev-parse HEAD)

# Add reaction to comment
echo "Adding ✅ reaction to comment #$COMMENT_ID..."
gh api repos/$OWNER/$REPO/pulls/$PR_NUMBER/comments/$COMMENT_ID/reactions -f content='+1'

# Post resolution comment
echo "Posting resolution confirmation..."
gh api repos/$OWNER/$REPO/pulls/comments -f body="✅ **Implemented** (Task $TASK_NUMBER)

This suggestion has been applied in commit \`$COMMIT_SHA\`

---
*Resolved by Agent OS import-ai-prompts*"

# Update tracking file
echo "[$TASK_NUMBER] Comment #$COMMENT_ID resolved at $(date)" >> resolution.log

echo "✅ Comment #$COMMENT_ID marked as resolved!"
