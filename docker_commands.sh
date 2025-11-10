#!/bin/bash

alembic upgrade head && \
uvicorn src.main:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 1200 --reload
