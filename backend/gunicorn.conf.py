"""
Gunicorn configuration for Video Scripts FastAPI backend.

Run with:
  gunicorn app.main:app -c gunicorn.conf.py

Or via the Procfile / Railway start command:
  gunicorn app.main:app --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
"""

import multiprocessing
import os

# ── Binding ───────────────────────────────────────────────────────────────────
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# ── Workers ───────────────────────────────────────────────────────────────────
# UvicornWorker runs an asyncio event loop per worker — required for FastAPI.
worker_class = "uvicorn.workers.UvicornWorker"

# (2 × CPU cores) + 1 is the classic formula.
# Cap at 4 on shared hosts to avoid OOM; tune upward for dedicated machines.
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)

# ── Timeouts ──────────────────────────────────────────────────────────────────
# Script/outline generation can take 60-120 s — give workers enough headroom.
timeout = 180          # worker killed if silent for this many seconds
graceful_timeout = 30  # time to finish in-flight requests on SIGTERM
keepalive = 5          # seconds to keep idle HTTP connections open

# ── Concurrency ───────────────────────────────────────────────────────────────
# Threads are not used with UvicornWorker (async handles concurrency natively).
threads = 1

# ── Logging ───────────────────────────────────────────────────────────────────
# Forward gunicorn logs to stdout so Railway/Heroku can capture them.
accesslog = "-"
errorlog = "-"
loglevel = os.environ.get("LOG_LEVEL", "info").lower()

# ── Process naming ────────────────────────────────────────────────────────────
proc_name = "video-scripts-api"

# ── Lifecycle hooks ───────────────────────────────────────────────────────────

def on_starting(server):
    server.log.info("Video Scripts API starting with %d worker(s)", workers)

def worker_exit(server, worker):
    server.log.info("Worker %d exited", worker.pid)
