#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE activity;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "activity" <<-EOSQL

    CREATE TYPE atype AS ENUM ('creating_playlist', 'adding_song_to_playlist', 'making_friend', 'sharing_playlist'); 
    
    CREATE TABLE activity(
        id SERIAL PRIMARY KEY,
        username TEXT NOT NULL,
        activity_type atype NOT NULL,
        activity_data TEXT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );

EOSQL
