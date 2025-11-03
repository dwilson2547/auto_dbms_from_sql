#!/bin/bash

docker run -d \
  --name postgres_auto_dbms \
  -e POSTGRES_USER=pguser \
  -e POSTGRES_PASSWORD=pgpass \
  -e POSTGRES_DB=auto_dbms \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v pgdata:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:latest