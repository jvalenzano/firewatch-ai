# GitHub Enterprise CLI Commands for TechTrend
# Enterprise GitHub: github.techtrend.us
# User: jvalenzano
# Repository: USDA-AI-Innovation-Hub/risen-one-science-research-agent

# 1. REPOSITORY SETUP
#    Clone the repository
git clone https://github.techtrend.us/USDA-AI-Innovation-Hub/risen-one-science-research-agent.git
cd risen-one-science-research-agent

#    Verify you're in the right repo
git remote get-url origin
# Should show: https://github.techtrend.us/USDA-AI-Innovation-Hub/risen-one-science-research-agent.git

# 2. REPOSITORY OPERATIONS (with correct org/repo path)
#    View repository information
gh repo view --hostname github.techtrend.us USDA-AI-Innovation-Hub/risen-one-science-research-agent

#    List all issues in the repository
gh issue list --hostname github.techtrend.us

#    View specific issue
gh issue view POC-DA-1 --hostname github.techtrend.us

#    Create an issue manually
gh issue create --hostname github.techtrend.us \
    --title "Test Issue" \
    --body "This is a test issue" \
    --label "test"

#    List issues by milestone
gh issue list --hostname github.techtrend.us --milestone "Discovery & Architecture"

#    List issues by label
gh issue list --hostname github.techtrend.us --label "ADK-Core"

#    Assign issue to yourself
gh issue edit POC-DA-1 --hostname github.techtrend.us --add-assignee jvalenzano

#    Add labels to existing issue
gh issue edit POC-DA-1 --hostname github.techtrend.us --add-label "in-progress"

#    Close completed issue
gh issue close POC-DA-1 --hostname github.techtrend.us --comment "Task completed successfully"

# 6. LABELS AND MILESTONES
#    List all labels
gh label list --hostname github.techtrend.us

#    Create a new label
gh label create "priority-high" --hostname github.techtrend.us --color "FF0000" --description "High priority tasks"

#    List all milestones
gh api --hostname github.techtrend.us repos/:owner/:repo/milestones

# 7. BULK OPERATIONS
#    Export all issues to view structure
gh issue list --hostname github.techtrend.us --json number,title,labels,milestone,assignees --jq '.'

#    Count issues by status
gh issue list --hostname github.techtrend.us --state all --json state --jq 'group_by(.state) | map({state: .[0].state, count: length})'

# 8. PROJECT BOARDS (if using GitHub Projects)
#    List available projects
gh project list --hostname github.techtrend.us

# 9. TROUBLESHOOTING
#    If you get permission errors, check:
gh auth refresh --hostname github.techtrend.us --scopes repo

#    View current token permissions
gh auth token --hostname github.techtrend.us

#    Clear and re-authenticate if needed
gh auth logout --hostname github.techtrend.us
gh auth login --hostname github.techtrend.us

# 10. SCRIPT EXECUTION
#     Run the POC issue creation script
chmod +x create_poc_issues.sh
./create_poc_issues.sh

#     Verify issues were created
gh issue list --hostname github.techtrend.us --label "ADK-Core"
