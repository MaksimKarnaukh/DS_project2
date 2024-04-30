#!/bin/bash

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE playlist;

EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "playlist" <<-EOSQL
    CREATE TABLE playlists(
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        creator TEXT NOT NULL,
        UNIQUE (name, creator)
    );

    CREATE TABLE playlist_songs(
        id SERIAL PRIMARY KEY,
        playlist_id INTEGER NOT NULL REFERENCES playlists (id) ON DELETE CASCADE,
        artist TEXT NOT NULL,
        title TEXT NOT NULL
    );

    CREATE TABLE shared_playlists(
        username TEXT NOT NULL,
        shared_with_username TEXT NOT NULL,
        playlist_id INTEGER NOT NULL REFERENCES playlists (id),
        PRIMARY KEY (username, shared_with_username, playlist_id)
    );

EOSQL
