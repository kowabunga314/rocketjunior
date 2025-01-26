#!/usr/bin/env bash

set -o errexit
set -o pipefail

cmd="$@"

export DATABASE_URL=$DATABASE_URL

function postgres_ready(){
python << END
import sys
import psycopg2
from urllib.parse import urlparse

result = urlparse("$DATABASE_URL")

username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port     = result.port

try:
    conn = psycopg2.connect(
        database=database,
        user=username,
        password=password,
        host=hostname,
        port=port,
        connect_timeout=3
    )
    cursor = conn.cursor()
    query = "SELECT * FROM pg_locks WHERE locktype = 'advisory' AND objid = '99';"
    cursor.execute(query)
    result = cursor.fetchall()
    if len(result) > 0:
        print("Database is up, but init sql is not complete.")
        raise RuntimeError()
    print("Advisory locks unlocked")
except (psycopg2.OperationalError, RuntimeError):
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
    >&2 echo "Postgres is unavailable - sleeping"
    sleep 2
done

>&2 echo "Postgres is up - continuing..."
exec "$@"