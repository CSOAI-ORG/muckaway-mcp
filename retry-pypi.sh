#!/bin/bash
# Retry PyPI upload after "Too many new projects created" rate limit clears.
# PyPI new-project rate limits can take 1-24 hours to reset.
# Run this script periodically until it succeeds.

cd "$(dirname "$0")"

while true; do
  echo "Attempting PyPI upload at $(date)..."
  if python3.11 -m twine upload dist/*; then
    echo "SUCCESS! Published to https://pypi.org/project/muckaway-mcp/"
    break
  fi
  echo "Failed. Waiting 1 hour before retry..."
  sleep 3600
done
