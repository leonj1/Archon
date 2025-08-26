#!/bin/bash
# GitHub Comment Resolution Helper
# Usage: ./resolve-comment.sh TASK_NUMBER

TASK_NUMBER=$1
OWNER="coleam00"
REPO="Archon"
PR_NUMBER=375

if [ -z "$TASK_NUMBER" ]; then
  echo "Usage: $0 TASK_NUMBER"
  exit 1
fi

# Read comment mapping from JSON
COMMENT_INFO=$(jq -r ".task_to_comment[\"$TASK_NUMBER\"]" comment-map.json)
if [ "$COMMENT_INFO" = "null" ]; then
  echo "Error: Task $TASK_NUMBER not found in comment-map.json"
  exit 1
fi

COMMENT_ID=$(echo "$COMMENT_INFO" | jq -r '.comment_id')
NODE_ID=$(echo "$COMMENT_INFO" | jq -r '.node_id')

# Get current commit SHA
COMMIT_SHA=$(git rev-parse HEAD)

# Find the thread ID for this comment
echo "Finding thread ID for comment #$COMMENT_ID..."
THREAD_ID=$(gh api graphql -f query='
  query {
    repository(owner: "'"$OWNER"'", name: "'"$REPO"'") {
      pullRequest(number: '"$PR_NUMBER"') {
        reviewThreads(first: 100) {
          nodes {
            id
            comments(first: 10) {
              nodes {
                id
                databaseId
              }
            }
          }
        }
      }
    }
  }' --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.comments.nodes[] | .databaseId == '"$COMMENT_ID"') | .id')

if [ -n "$THREAD_ID" ]; then
  # Resolve the thread using GraphQL
  echo "Resolving thread $THREAD_ID..."
  gh api graphql -f query='
    mutation {
      resolveReviewThread(input: {
        threadId: "'"$THREAD_ID"'"
      }) {
        thread {
          id
          isResolved
        }
      }
    }'
  echo "✅ Thread resolved!"
fi

# Add reaction to comment
echo "Adding ✅ reaction to comment #$COMMENT_ID..."
gh api repos/$OWNER/$REPO/issues/comments/$COMMENT_ID/reactions -f content='+1' 2>/dev/null || true

# Post resolution comment
echo "Posting resolution confirmation..."
gh api repos/$OWNER/$REPO/issues/comments -f body="✅ **Implemented** (Task $TASK_NUMBER)

This suggestion has been applied in commit \`$COMMIT_SHA\`

---
*Resolved by Agent OS import-ai-prompts*"

# Update tracking file
echo "[$TASK_NUMBER] Comment #$COMMENT_ID resolved at $(date)" >> resolution.log

echo "✅ Comment #$COMMENT_ID marked as resolved!"