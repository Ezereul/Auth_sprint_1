#!/bin/bash
# -e: выход в случае ошибки; -o: более подробный вывод
set -eo pipefail
# что-то связанное с поведением bash и glob-паттернами
shopt -s nullglob

export PATH=/app/.venv/bin:${PATH}
export PYTHONPATH=/app/.venv/bin:${PATH}

alembic upgrade head

exec gunicorn --bind 0.0.0.0:8000 src.main:app --worker-class uvicorn.workers.UvicornWorker