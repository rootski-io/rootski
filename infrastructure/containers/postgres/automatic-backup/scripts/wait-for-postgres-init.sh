#!/bin/sh
# wait-for-postgres-init.sh

# Checks the container until the database has been fully initialized
until pg_isready --username ${POSTGRES_USER} --dbname ${POSTGRES_DB} --port ${POSTGRES_PORT}; do
  >&2 echo "Postgres initialization in progress - sleeping"
  sleep 1
done

sleep 3

>&2 echo "Postgres is initialized - Ready to restore"
exec "$@"
