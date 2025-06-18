#!/bin/bash

echo "🚀 Preparing for Phase II Branch Creation"
echo "========================================"

# 1. Check current branch
echo "📍 Current branch:"
git branch --show-current

# 2. Show uncommitted changes
echo -e "\n📝 Uncommitted changes (excluding venv):"
git status --porcelain | grep -v venv | head -10

# 3. Recommendations
echo -e "\n📋 Recommended actions:"
echo "1. Commit the Recovery Roadmap (optional):"
echo "   git add 'Recovery Roadmap.md'"
echo "   git commit -m 'docs: Add Phase I recovery analysis'"
echo ""
echo "2. Commit the Agent ID corrections:"
echo "   git add docs/GOOGLE_ADK_CONTEXT.md docs/project-development/poc-phase/status-reports/PROJECT_COMPLETE.md"
echo "   git commit -m 'fix: Correct agent ID references to 6609146802375491584'"
echo ""
echo "3. Create and switch to Phase II branch:"
echo "   git checkout -b phase-ii-fire-science"
echo ""
echo "4. Push the new branch:"
echo "   git push -u origin phase-ii-fire-science"
echo ""
echo "Note: The .cursor/scratchpad.md changes can remain uncommitted as a working document" 