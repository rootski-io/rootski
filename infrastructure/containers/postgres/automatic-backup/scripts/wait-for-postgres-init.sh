#!/bin/sh
# wait-for-postgres-init.sh

# Checks the container logs until the database has been fully initialize
until psql -lw -U $POSTGRES_USER --host $POSTGRES_HOST -d $POSTGRES_DB | grep $POSTGRES_DB; do
  >&2 echo "Postgres initialization in progress - sleeping"
  sleep 3
done

>&2 echo "Postgres is initialized - Ready to restore"
exec "$@"
