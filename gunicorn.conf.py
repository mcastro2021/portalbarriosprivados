"""
Gunicorn configuration file optimized for Render.com deployment
"""

import os
import multiprocessing

# Server socket
bind = "0.0.0.0:" + str(os.environ.get("PORT", 10000))
backlog = 2048

# Worker processes
workers = min(2, multiprocessing.cpu_count() + 1)  # Menos workers para mayor estabilidad
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 2
threads = 2  # Para manejar múltiples requests por worker

# Memory management
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "portalbarriosprivados"

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Performance tuning for Render.com
tmp_upload_dir = None
secure_scheme_headers = {"X-FORWARDED-PROTOCOL": "ssl", "X-FORWARDED-PROTO": "https", "X-FORWARDED-SSL": "on"}
forwarded_allow_ips = "*"

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """Called just after a worker has been killed by a SIGINT or SIGQUIT signal."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker is killed due to a timeout."""
    worker.log.info("Worker aborted (pid: %s)", worker.pid)
