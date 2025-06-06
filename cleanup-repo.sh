#!/bin/bash
# cleanup-repo.sh - Repository cleanup for RisenOne Fire Analysis Agent
# Removes cache files, duplicates, and organizes structure

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() { echo -e "${BLUE}📋 $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

echo "🧹 RisenOne Repository Cleanup Starting..."
echo "================================================"

# Verify we're in the right directory
if [[ ! -f "README.md" ]] || [[ ! -d "agent" ]] || [[ ! -d "docs" ]]; then
    print_error "Must run from risenone-fire-analysis-agent root directory"
    exit 1
fi

print_step "Step 1: Cleaning Python Cache Files..."

# Add cache files to .gitignore if not already there
if ! grep -q "__pycache__" .gitignore; then
    echo "" >> .gitignore
    echo "# Python cache files" >> .gitignore
    echo "__pycache__/" >> .gitignore
    echo "*.pyc" >> .gitignore
    echo "*.pyo" >> .gitignore
    echo "*.pyd" >> .gitignore
    print_success "Added Python cache patterns to .gitignore"
else
    print_success "Python cache patterns already in .gitignore"
fi

# Remove existing cache files and directories
print_step "Removing existing cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true
cache_count=$(find . -name "__pycache__" 2>/dev/null | wc -l)
print_success "Removed Python cache files (found $cache_count __pycache__ dirs)"

print_step "Step 2: Removing Empty/Unnecessary Directories..."

# Remove empty directories
declare -a empty_dirs=(
    "docs/api"
    "docs/architecture/static" 
    "docs/internal/architecture-decisions"
    "docs/internal/dev-guides"
    "docs/internal/meeting-transcripts"
    "scripts"
    "developer/handoff"
)

for dir in "${empty_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        if [[ -z "$(ls -A "$dir")" ]]; then
            rmdir "$dir"
            print_success "Removed empty directory: $dir"
        else
            print_warning "Directory not empty, skipping: $dir"
        fi
    fi
done

print_step "Step 3: Removing Duplicate/Unnecessary Files..."

# Remove duplicate and unnecessary files
declare -a unnecessary_files=(
    "agent/QUICK_START.md"
    "agent/agent.py.backup"
    "agent/data_science/utils/data/test.csv"
    "agent/data_science/utils/data/train.csv"
)

for file in "${unnecessary_files[@]}"; do
    if [[ -f "$file" ]]; then
        rm "$file"
        print_success "Removed: $file"
    fi
done

print_step "Step 4: Creating Fire Data Structure..."

# Create fire data placeholder structure
mkdir -p agent/data_science/utils/data/fire_data

cat > agent/data_science/utils/data/fire_data/README.md << 'EOF'
# Fire Analysis Data

This directory will contain fire-related datasets for the RisenOne Fire Analysis Agent:

## Planned Data Sources:
- **Weather Stations**: Temperature, humidity, wind speed/direction, precipitation
- **Fire Danger Indices**: Current fire detection, danger ratings, fuel moisture
- **Field Observations**: Scientist-collected vegetation, soil, fuel load data
- **Historical Data**: Fire spread patterns, weather correlations, seasonal trends

## Data Format:
CSV files with standardized schemas for integration with BigQuery ML models.

## Usage:
Data files will be loaded via `agent/data_science/utils/create_bq_table.py` for BigQuery integration.
EOF

print_success "Created fire data structure with README"

print_step "Step 5: Cleaning .gitignore duplicates..."

# Remove duplicate entries from .gitignore
sort .gitignore | uniq > .gitignore.tmp && mv .gitignore.tmp .gitignore
print_success "Cleaned duplicate .gitignore entries"

print_step "Step 6: Verification..."

# Verify essential files exist
essential_files=(
    "README.md"
    "LICENSE" 
    "agent/.env"
    "agent/pyproject.toml"
    "docs/architecture/index.html"
    "docs/internal/handoffs/template.md"
    "deployment/deploy.py"
)

missing_files=()
for file in "${essential_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        missing_files+=("$file")
    fi
done

if [[ ${#missing_files[@]} -eq 0 ]]; then
    print_success "All essential files present"
else
    print_warning "Missing files: ${missing_files[*]}"
fi

# Verify no cache files remain
remaining_cache=$(find . -name "__pycache__" -o -name "*.pyc" | wc -l)
if [[ $remaining_cache -eq 0 ]]; then
    print_success "No Python cache files remaining"
else
    print_warning "$remaining_cache cache files still present"
fi

print_step "Step 7: Final Structure Overview..."

echo ""
echo "📁 Clean Repository Structure:"
tree -I '__pycache__|*.pyc|.git' -L 3 2>/dev/null || {
    echo "📁 Structure (tree not available):"
    find . -type d -not -path './.git*' -not -name '__pycache__' | head -20 | sort
}

echo ""
print_success "Repository cleanup completed!"
echo "================================================"
echo ""
echo "✅ Summary of changes:"
echo "   • Removed Python cache files (__pycache__, *.pyc)"
echo "   • Removed duplicate/unnecessary files"
echo "   • Cleaned empty directories"
echo "   • Created fire data structure"
echo "   • Updated .gitignore"
echo ""
echo "🎯 Repository is now clean and ready for:"
echo "   • Git commit and push"
echo "   • GitHub repository creation"
echo "   • Professional handoff"
echo ""
echo "💡 Next step: git status (should show clean changes)"