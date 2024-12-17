#!/bin/bash

echo "Run wait-for-it"

HOST="$1"
PORT="$2"
shift 2

TIMEOUT=30
while ! nc -z "$HOST" "$PORT"; do
  echo "Waiting for $HOST:$PORT..."
  sleep 1
  TIMEOUT=$((TIMEOUT-1))
  if [ "$TIMEOUT" -le 0 ]; then
    echo "Timeout waiting for $HOST:$PORT"
    exit 1
  fi
done

echo "$HOST:$PORT started"
exec "$@"
