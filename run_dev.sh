#!/bin/bash

# Start Redis if not already running
redis_running=$(pgrep redis-server || echo "")
if [ -z "$redis_running" ]; then
    echo "Starting Redis..."
    redis-server &
    sleep 2  # Give Redis time to start
fi

# Start Celery worker
echo "Starting Celery worker..."
celery -A app.core.celery_app worker --loglevel=info -Q celery,pr-review &
CELERY_PID=$!

# Start FastAPI application
echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Cleanup on exit
function cleanup {
    echo "Shutting down..."
    kill $CELERY_PID
    redis-cli shutdown
}

trap cleanup EXIT
#!/bin/bash

# Start Redis if not already running
redis_running=$(pgrep redis-server || echo "")
if [ -z "$redis_running" ]; then
    echo "Starting Redis..."
    redis-server &
    sleep 2  # Give Redis time to start
fi

# Start Celery worker
echo "Starting Celery worker..."
celery -A app.core.celery_app worker --loglevel=info -Q celery,pr-review &
CELERY_PID=$!

# Start FastAPI application
echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Cleanup on exit
function cleanup {
    echo "Shutting down..."
    kill $CELERY_PID
    redis-cli shutdown
}

trap cleanup EXIT
#!/bin/bash

# Start Redis if not already running
redis_running=$(pgrep redis-server || echo "")
if [ -z "$redis_running" ]; then
    echo "Starting Redis..."
    redis-server &
    sleep 2  # Give Redis time to start
fi

# Start Celery worker
echo "Starting Celery worker..."
celery -A app.core.celery_app worker --loglevel=info -Q celery,pr-review &
CELERY_PID=$!

# Start FastAPI application
echo "Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Cleanup on exit
function cleanup {
    echo "Shutting down..."
    kill $CELERY_PID
    redis-cli shutdown
}

trap cleanup EXIT
