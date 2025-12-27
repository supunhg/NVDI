#!/bin/bash
# Build nvdi as a standalone binary using PyInstaller
# Author: Supun Hewagamage (@supunhg)

set -e

echo "🔨 Building nvdi standalone binary..."
echo ""

# Activate venv
source .venv/bin/activate

# Install PyInstaller if not present
if ! pip show pyinstaller > /dev/null 2>&1; then
    echo "📦 Installing PyInstaller..."
    pip install -r build-requirements.txt
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ nvdi.spec

# Create the binary
echo "🚀 Creating binary with PyInstaller..."
pyinstaller \
    --onefile \
    --name nvdi \
    --clean \
    --noconfirm \
    --hidden-import nvdi_cli.commands.get \
    --hidden-import nvdi_cli.commands.search \
    --hidden-import nvdi_cli.commands.analyze \
    --hidden-import nvdi_cli.commands.monitor \
    --hidden-import nvdi_cli.commands.export \
    --hidden-import nvdi_cli.commands.stats \
    --hidden-import nvdi_cli.commands.compare \
    --hidden-import nvdi_cli.commands.db \
    --hidden-import aiosqlite \
    --hidden-import diskcache \
    --collect-data rich \
    nvdi_cli/main.py

# Test the binary
echo ""
echo "✅ Build complete!"
echo ""
echo "Binary location: dist/nvdi"
echo "Size: $(du -h dist/nvdi | cut -f1)"
echo ""
echo "Testing binary..."
./dist/nvdi --help > /dev/null && echo "✓ Binary works!" || echo "✗ Binary test failed"
echo ""
echo "To install system-wide:"
echo "  sudo cp dist/nvdi /usr/local/bin/"
echo ""
echo "Or use directly:"
echo "  ./dist/nvdi --help"
