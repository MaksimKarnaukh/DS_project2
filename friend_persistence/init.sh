#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE friend;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "friend" <<-EOSQL
    CREATE TABLE friend(
        username TEXT NOT NULL,
        friendname TEXT NOT NULL,
        PRIMARY KEY (username, friendname)
    );

EOSQL
