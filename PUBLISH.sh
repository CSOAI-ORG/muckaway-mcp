#!/bin/bash
# PyPI upload script for muckaway-mcp
# Run this to publish to PyPI after code review

set -e

cd "$(dirname "$0")"

echo "Building package..."
python3.11 -m build

echo "Uploading to PyPI..."
python3.11 -m twine upload dist/*

echo "Done! Verify at: https://pypi.org/project/muckaway-mcp/"
