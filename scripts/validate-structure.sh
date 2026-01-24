#!/bin/bash

# Script to validate project structure matches architecture
# Usage: ./scripts/validate-structure.sh

set -e

echo "Validating Project Echo repository structure..."
echo ""

ERRORS=0

# Check central repo structure
check_dir() {
    if [ ! -d "$1" ]; then
        echo "❌ Missing directory: $1"
        ERRORS=$((ERRORS + 1))
    else
        echo "✅ Found: $1"
    fi
}

# Check required files
check_file() {
    if [ ! -f "$1" ]; then
        echo "❌ Missing file: $1"
        ERRORS=$((ERRORS + 1))
    else
        echo "✅ Found: $1"
    fi
}

echo "=== Central Repository Structure ==="
check_dir "backend"
check_dir "backend/src"
check_dir "backend/src/routes"
check_dir "backend/src/services"
check_dir "backend/src/repositories"
check_dir "backend/src/models"
check_dir "backend/src/schemas"
check_dir "backend/src/middleware"
check_dir "backend/src/utils"
check_dir "backend/tests"
check_dir "backend/alembic"

check_dir "frontend"
check_dir "frontend/src"
check_dir "frontend/src/components"
check_dir "frontend/src/components/atoms"
check_dir "frontend/src/components/molecules"
check_dir "frontend/src/components/organisms"
check_dir "frontend/src/components/templates"
check_dir "frontend/src/pages"
check_dir "frontend/src/hooks"
check_dir "frontend/src/services"
check_dir "frontend/src/stores"
check_dir "frontend/src/types"
check_dir "frontend/src/utils"
check_dir "frontend/src/styles"
check_dir "frontend/public"

check_dir "shared"
check_dir "shared/src"
check_dir "shared/src/scraping"
check_dir "shared/src/transformation"
check_dir "shared/src/publication"
check_dir "shared/src/common"

check_dir "templates"
check_dir "templates/channel-repo-template"
check_dir "templates/channel-repo-template/.github/workflows"
check_dir "templates/channel-repo-template/config"
check_dir "templates/channel-repo-template/scripts"

check_dir "docs"
check_dir "scripts"
check_dir ".github/workflows"

echo ""
echo "=== Required Files ==="
check_file "README.md"
check_file ".gitignore"
check_file ".editorconfig"
check_file "frontend/package.json"
check_file "frontend/vite.config.ts"
check_file "frontend/tsconfig.json"
check_file "frontend/public/index.html"
check_file "backend/.env.example"
check_file "frontend/.env.example"
check_file "shared/setup.py"
check_file "templates/channel-repo-template/README.md"
check_file "templates/channel-repo-template/config/channel.yaml"
check_file "templates/channel-repo-template/.github/workflows/process-video.yaml"
check_file "scripts/setup-channel-repo.sh"
check_file "docs/MULTI-REPO-ARCHITECTURE.md"
check_file "docs/GIT-WORKFLOW.md"

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "✅ All structure checks passed!"
    exit 0
else
    echo "❌ Found $ERRORS errors in structure"
    exit 1
fi
