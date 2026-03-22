#!/usr/bin/env bash
set -euo pipefail

# Start the development server using the project-local `uv` runner
# which will invoke `uvicorn` inside the managed environment.
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
