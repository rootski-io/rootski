#!/bin/sh
# startup-script.sh

# Creates a .pgpass file for running psql commands without having to prompt for a password
echo "Creating .pgpass file"
touch .pgpass
echo "$POSTGRES_HOST:$POSTGRES_PORT:$POSTGRES_DB:$POSTGRES_USER:$POSTGRES_PASSWORD" > .pgpass
chmod 600 .pgpass
export PGPASSFILE=".pgpass"

# Checks the postgres db repeatedly until it finds the rootski_db (technically $POSTGRES_DB) db
echo "Running /scripts/wait-for-postgres-init.sh"
bash scripts/wait-for-postgres-init.sh

# Restores the database from the latest S3 backup
echo "Running python3 -m backup_or_restore.py restore-from-most-recent"
python3 backup_or_restore.py restore-from-most-recent

# Backs up the database to S3 regularly according to the $BACKUP_INTERVAL
echo "Running python3 -m backup_or_restore.py backup-on-interval"
python3 backup_or_restore.py backup-on-interval
