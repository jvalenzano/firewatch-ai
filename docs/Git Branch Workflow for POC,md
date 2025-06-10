# 🌿 Simple Git Branch Workflow for POC Development

## 🏠 The "Workshop" Concept

Think of your code like a house with workshops:
- **`main`** = The main house (production code) 🏠
- **`poc/main`** = A separate workshop for POC experiments 🔧
- **`poc/da-2-geographic-data`** = A specific workbench in that workshop for one task 🪚

## 📅 Daily Developer Workflow (Step-by-Step)

### **Day 1: Setting Up Your Workshop**
```bash
# Start in the main house
cd ~/risenone-fire-analysis-agent
git checkout main
git pull origin main

# Create your POC workshop (one-time setup)
git checkout -b poc/main
git push -u origin poc/main

# Now you have a separate workspace for POC experiments!
```

### **Day 2: Working on POC-DA-2 (Geographic Data)**
```bash
# Go to your POC workshop
git checkout poc/main
git pull origin poc/main

# Create a workbench for geographic data task
git checkout -b poc/da-2-geographic-data
git push -u origin poc/da-2-geographic-data

# Now you're in your specific workbench!
# Check where you are
git branch
# Shows: * poc/da-2-geographic-data (you're here)
#        poc/main
#        main
```

### **During Development (Your Normal Coding)**
```bash
# Work normally - create files, edit code, etc.
mkdir -p data/zone7
echo "Zone 7 boundary data" > data/zone7/boundaries.geojson

# Save your work (same as always)
git add .
git commit -m "Add Zone 7 boundary data for POC-DA-2"
git push origin poc/da-2-geographic-data

# Your work is safely saved to YOUR workbench
```

### **When Task is Complete**
```bash
# Move your completed work from workbench to workshop
git checkout poc/main
git merge poc/da-2-geographic-data
git push origin poc/main

# Clean up your workbench (optional)
git branch -d poc/da-2-geographic-data
git push origin --delete poc/da-2-geographic-data
```

### **Starting Next Task (POC-AD-1)**
```bash
# Go back to your clean workshop
git checkout poc/main
git pull origin poc/main

# Create new workbench for next task
git checkout -b poc/ad-1-vertex-ai
git push -u origin poc/ad-1-vertex-ai

# Start working on Vertex AI setup...
```

## 🎯 What This Means for You

### **Benefits You'll Experience:**
1. **Safety**: Can't break production code (main branch)
2. **Experimentation**: Try things without fear
3. **Organization**: Each POC task in its own space
4. **Rollback**: Easy to undo if something goes wrong
5. **Parallel Work**: Could work on multiple POC tasks if needed

### **What Stays the Same:**
- ✅ **Your coding**: Write code exactly like always
- ✅ **Your commits**: `git add`, `git commit` work the same
- ✅ **Your files**: Same project structure and files

### **What Changes:**
- 🆕 **Where you work**: Different branch name
- 🆕 **Before starting**: Switch to the right workbench
- 🆕 **When done**: Merge work back to workshop

## 🔄 Simple Daily Commands

### **Morning Routine (30 seconds)**
```bash
# Check where you are
git branch

# Go to today's workbench (example: geographic data)
git checkout poc/da-2-geographic-data

# Make sure it's up to date
git pull origin poc/da-2-geographic-data
```

### **End of Day Routine (1 minute)**
```bash
# Save your work
git add .
git commit -m "Progress on POC-DA-2: Zone 7 RAWS stations mapped"
git push origin poc/da-2-geographic-data

# Update GitHub issue with progress
# (Go to issue #35 and add a comment about what you completed)
```

## 📊 Visual Representation

```
Your Computer Files:
└── risenone-fire-analysis-agent/
    ├── README.md
    ├── agent/
    ├── data/           ← Your POC work appears here
    │   └── zone7/      ← Only when on POC branches
    └── docs/

Git Branches (invisible containers):
├── main                     ← Production house
├── poc/main                 ← POC workshop (clean)
├── poc/da-2-geographic-data ← Your current workbench
└── poc/ad-1-vertex-ai       ← Future workbench
```

## 🤔 Common Questions

### **Q: What if I forget which branch I'm on?**
```bash
git branch
# Shows all branches, * marks where you are
```

### **Q: What if I start coding on the wrong branch?**
```bash
# Save your work first
git add .
git commit -m "WIP: work in progress"

# Move to correct branch
git checkout poc/da-2-geographic-data

# Bring your work with you
git cherry-pick [commit-hash]
```

### **Q: What if I mess something up?**
```bash
# Go back to clean workshop
git checkout poc/main

# Your workbench still exists, nothing lost
git checkout poc/da-2-geographic-data
```

### **Q: How do I see all my POC work together?**
```bash
# Everything you've completed is in the workshop
git checkout poc/main
ls -la
# Shows all your finished POC components
```

## 🎪 Demo Day Strategy

### **Show Stakeholders Your POC Workshop**
```bash
# Switch to your complete POC work
git checkout poc/main

# Run your demo from here
# All POC components are integrated and working
```

### **Keep Production Safe**
```bash
# Production code is untouched
git checkout main
ls -la
# Shows original project, no POC experimental code
```

## 🚀 Why This Approach Rocks for POC

1. **Confidence**: You can't break anything important
2. **Speed**: No fear means faster development
3. **Clean Demo**: Your POC workshop has only POC code
4. **Easy Cleanup**: Delete POC branches when done
5. **Professional**: Shows you understand modern development practices

## 📝 Your First Branch Command

Try this right now to see how it works:
```bash
# See where you are (probably main)
git branch

# Create your POC workshop
git checkout -b poc/main
git push -u origin poc/main

# You just created your first branch! 🎉
```

The key insight: **You're just switching between different versions of the same folder.** Each branch is like having multiple copies of your project folder, but Git manages them intelligently so you only see one at a time.