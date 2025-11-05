"""
Gunicorn configuration for production deployment
Optimized for handling 50+ concurrent users
"""
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # Recommended formula
worker_class = 'sync'  # Use 'gevent' or 'eventlet' for async if needed
worker_connections = 1000
max_requests = 1000  # Restart workers after this many requests (prevents memory leaks)
max_requests_jitter = 50
timeout = 120  # Timeout for workers (2 minutes)
keepalive = 5

# Logging
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'opic_portal'

# Server mechanics
daemon = False
pidfile = 'logs/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = 'ssl/key.pem'
# certfile = 'ssl/cert.pem'

# Preload app for better memory efficiency
preload_app = True

# Worker restart
graceful_timeout = 30

def on_starting(server):
    """Called just before the master process is initialized"""
    print("🚀 Starting Gunicorn server...")
    print(f"   Workers: {workers}")
    print(f"   Bind: {bind}")
    print(f"   Max Connections per Worker: {worker_connections}")

def when_ready(server):
    """Called just after the server is started"""
    print("✅ Gunicorn server is ready to handle requests")

def on_exit(server):
    """Called just before exiting Gunicorn"""
    print("👋 Gunicorn server is shutting down")

def worker_int(worker):
    """Called when a worker receives the INT or QUIT signal"""
    print(f"⚠️  Worker {worker.pid} received INT/QUIT signal")

def post_fork(server, worker):
    """Called just after a worker has been forked"""
    print(f"✅ Worker spawned (pid: {worker.pid})")
































