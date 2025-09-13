#!/bin/sh
set -e

host="${MYSQL_HOST:-mysql-flask}"
port="${MYSQL_PORT:-3306}"

echo "Waiting for MySQL at ${host}:${port}..."
while ! nc -z "$host" "$port"; do
  sleep 0.5
done

echo "MySQL is up - initializing DB"
python -c "from app import init_db; init_db()"

exec "$@"
