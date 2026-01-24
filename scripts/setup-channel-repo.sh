#!/bin/bash

# Script to create a new channel repository from template
# Usage: ./scripts/setup-channel-repo.sh channel-name

set -e

if [ -z "$1" ]; then
    echo "Error: Channel name required"
    echo "Usage: ./scripts/setup-channel-repo.sh channel-name"
    exit 1
fi

CHANNEL_NAME="$1"
REPO_NAME="project-echo-channel-${CHANNEL_NAME}"
TEMPLATE_DIR="templates/channel-repo-template"
TARGET_DIR="../${REPO_NAME}"

# Check if template exists
if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "Error: Template directory not found: $TEMPLATE_DIR"
    exit 1
fi

# Check if target directory already exists
if [ -d "$TARGET_DIR" ]; then
    echo "Error: Directory already exists: $TARGET_DIR"
    exit 1
fi

echo "Creating channel repository: $REPO_NAME"
echo ""

# Copy template
echo "Copying template..."
cp -r "$TEMPLATE_DIR" "$TARGET_DIR"

# Initialize Git repository
echo "Initializing Git repository..."
cd "$TARGET_DIR"
git init
git add .
git commit -m "Initial commit: Channel repository for $CHANNEL_NAME"

echo ""
echo "✅ Channel repository created successfully!"
echo ""
echo "Next steps:"
echo "1. Create GitHub repository: $REPO_NAME"
echo "2. Link local repo: git remote add origin https://github.com/your-username/$REPO_NAME.git"
echo "3. Push to GitHub: git push -u origin main"
echo "4. Configure channel.yaml in config/channel.yaml"
echo "5. Set up GitHub Secrets (see templates/channel-repo-template/README.md)"
echo "6. Register channel in central orchestration system"
echo ""
echo "Repository location: $TARGET_DIR"
