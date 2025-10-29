# REDLINE Gunicorn Configuration for Production
# Optimized for Docker deployment with 4 workers and gevent async workers

import multiprocessing
import os

# Server socket
bind = os.environ.get('GUNICORN_BIND', "0.0.0.0:8080")
backlog = 2048

# Worker processes
workers = int(os.environ.get('GUNICORN_WORKERS', 4))  # 2 * cores + 1
worker_class = os.environ.get('GUNICORN_WORKER_CLASS', 'gevent')  # Async workers
worker_connections = 1000
max_requests = 1000  # Prevent memory leaks
max_requests_jitter = 50

# Worker timeout and graceful restart
timeout = 120
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = os.environ.get('GUNICORN_ACCESS_LOG', '-')  # stdout
errorlog = os.environ.get('GUNICORN_ERROR_LOG', '-')  # stderr
loglevel = os.environ.get('GUNICORN_LOG_LEVEL', 'info')

# Process naming
proc_name = 'redline-web'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = os.environ.get('GUNICORN_USER', 'appuser')
group = os.environ.get('GUNICORN_GROUP', 'appuser')
tmp_upload_dir = None

# SSL (if enabled)
keyfile = os.environ.get('SSL_KEYFILE', None)
certfile = os.environ.get('SSL_CERTFILE', None)

# Performance tuning
worker_tmp_dir = '/dev/shm'  # Use shared memory for worker temp files

# Preload application for better memory sharing
preload_app = False  # Set to True if app is thread-safe, False for gevent

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Server is ready. Spawning worker")

def worker_int(worker):
    """Called after each worker is killed."""
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized")

def worker_exit(server, worker):
    """Called just after a worker has been exited, in the master process."""
    server.log.info("Worker exited (pid: %s)", worker.pid)

def nworkers_changed(server, new_value, old_value):
    """Called just after num_workers has been changed."""
    server.log.info("Workers changed from %s to %s", old_value, new_value)

def on_exit(server):
    """Called just before performing master exit."""
    server.log.info("Master process shutting down")

# Access log format
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Capture output from stdout/stderr for logging
capture_output = True
enable_stdio_inheritance = False

# Limit request line size
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Buffer sizes
buffer_size = 8192

# Send files directly from disk if possible
sendfile = True

