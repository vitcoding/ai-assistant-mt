#!/usr/bin/env bash

set -e

 while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
     sleep 0.5
 done

 while ! nc -z $REDIS_HOST $REDIS_PORT; do
     sleep 0.5
 done

alembic upgrade head

python3 create_superuser.py admin admin


# Create test users
TABLE="public.users"

DATA="\
('00000000-0000-0000-0000-000000000001', 'user1', 'e10adc3949ba59abbe56e057f20f883e', \
'Name1', 'Lastname1', 'Hi, I am user1', '2000-01-01', 'email1@email', '', 'user', \
'2025-01-15 10:00:00.000001', '2025-01-15 10:00:00.000001'), \
('00000000-0000-0000-0000-000000000002', 'user2', 'e10adc3949ba59abbe56e057f20f883e', \
'Name2', 'Lastname2', 'Hi, I am user2', '2000-01-02', 'email2@email', '', 'user', \
'2025-01-15 10:00:00.000002', '2025-01-15 10:00:00.000002'),
('00000000-0000-0000-0000-000000000003', 'user3', 'e10adc3949ba59abbe56e057f20f883e', \
'Name3', 'Lastname3', 'Hi, I am user3', '2000-01-03', 'email1@email', '', 'user', \
'2025-01-15 10:00:00.000003', '2025-01-15 10:00:00.000003')\
"

INSERT_QUERY="INSERT INTO ${TABLE} \
(id, login, password, first_name, last_name, about, birth_date, \
email, phone_number, role, created_at, updated_at) VALUES ${DATA} \
ON CONFLICT ${id} DO NOTHING;"

export PGPASSWORD="${POSTGRES_PASSWORD}"

echo "Connecting to PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -c "${INSERT_QUERY}"

if [ $? -eq 0 ]; then
  echo "The operation has been done successfully!"
else
  echo "Failed to insert data."
fi

gunicorn -c gunicorn.conf.py main:app
