#!/usr/bin/env bash
set -euo pipefail

"$BROWSER" "http://localhost:8501" &
"$BROWSER" "http://localhost:8000/docs" &
"$BROWSER" "http://localhost:8000/redoc" &

echo "✅ Opened browser tabs for manual verification"
