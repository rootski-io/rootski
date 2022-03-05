#!/bin/sh
# wait-for-postgres-init.sh

# Checks the container logs until the database has been fully initialize
until pg_isready -U $POSTGRES_USER --host $POSTGRES_HOST -d $POSTGRES_DB; do
  >&2 echo "Postgres initialization in progress - sleeping"
  sleep 1
done

sleep 5

>&2 echo "Postgres is initialized - Ready to restore"
exec "$@"
