from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2
import requests
import sys

parser = reqparse.RequestParser()
parser.add_argument('playlist_id')

parser.add_argument('owner')
parser.add_argument('title')
parser.add_argument('artist')

parser.add_argument('recipient')

app = Flask("playlist")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="playlist", user="postgres", password="postgres", host="playlist_persistence")
        print("DB connection succesful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")

def all_playlists(limit=20):
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT id, name, creator FROM playlists LIMIT {limit};")
        return cur.fetchall(), 200
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return [], 500

def playlist_exists(title, owner, id=None):
    try:
        if id is None:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM playlists WHERE name = %s AND creator = %s;", (title, owner))
            return bool(cur.fetchone()[0]) # Either True or False
        else:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM playlists WHERE id = %s;", (id,))
            return bool(cur.fetchone()[0]) # Either True or False
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return False

def create_playlist_log_activity(playlist_title, owner):
    # API call to activity microservice to log sharing of a playlist
    activity_type = "creating_playlist"
    activity_data = "created playlist '" + playlist_title + "'."
    data = {"activity_type": activity_type, "activity_data": activity_data}
    try:
        response = requests.post(f"http://activity:5000/activity/{owner}/log", json=data)
        if response.status_code == 200 or response.status_code == 201:
            return response.json()["success"]
        return False
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return False

def create_playlist(title, owner):  
    try:
        if playlist_exists(title, owner):
            return {"success": False}, 409
        else:
            cur = conn.cursor()
            cur.execute("INSERT INTO playlists (name, creator) VALUES (%s, %s)", (title, owner))
            conn.commit()
            log_playlist_creation = create_playlist_log_activity(title, owner)
            if not log_playlist_creation:
                print("Failed to log playlist creation", flush=True)
            return {"success": True}, 201
        
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return {"success": False}, 500
    
def song_exists_in_playlist(playlist_id, artist, title):
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM playlist_songs WHERE playlist_id = %s AND artist = %s AND title = %s;", (playlist_id, artist, title))
        return bool(cur.fetchone()[0]) # Either True or False
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return False

def add_song_to_playlist_log_activity(playlist_id, artist, title):
    # API call to activity microservice to log sharing of a playlist
    playlist_title, playlist_owner = get_playlist_by_id(playlist_id)
    activity_type = "adding_song_to_playlist"
    activity_data = "added " + title + " by " + artist + " to playlist '" + playlist_title + "'."
    data = {"activity_type": activity_type, "activity_data": activity_data}
    try:
        response = requests.post(f"http://activity:5000/activity/{playlist_owner}/log", json=data)
        if response.status_code == 200 or response.status_code == 201:
            return response.json()["success"]
        return False
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return False

def song_exists(artist, title):
    try:
        # API call to song microservice to check if song exists
        response = requests.get("http://songs:5000/songs/exist/?artist=" + artist + "&title=" + title)
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        return False
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return False

def add_song_to_playlist(playlist_id, artist, title):
    try:
        if song_exists_in_playlist(playlist_id, artist, title):
            return {"success": False}, 409
        else:
            if song_exists(artist, title):
                cur = conn.cursor()
                cur.execute("INSERT INTO playlist_songs (playlist_id, artist, title) VALUES (%s, %s, %s);", (playlist_id, artist, title))
                conn.commit()
                log_playlist_song_addition = add_song_to_playlist_log_activity(playlist_id, artist, title)
                if not log_playlist_song_addition:
                    print("Failed to log playlist song addition", flush=True)
                return {"success": True}, 201
            return {"success": False}, 200
        
    except Exception as e:
        print(e, flush=True)
        return {"success": False}, 500
    
def user_exists(username):
    try:
        # API call to authentication microservice to check if user exists
        response = requests.get("http://authentication:5000/users/exist/?username=" + username)
        if response.status_code == 200 or response.status_code == 201:
            return response.json()["success"]
        return False
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return False
    
def playlist_shared_with_user(playlist_id, username, recipient):
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM shared_playlists WHERE username = %s AND shared_with_username = %s AND playlist_id = %s;", (username, recipient, playlist_id))
        return bool(cur.fetchone()[0]) # Either True or False
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return False

def share_playlist_log_activity(playlist_id, username, recipient):
    # API call to activity microservice to log sharing of a playlist
    playlist_title: str = get_playlist_by_id(playlist_id)[0]
    activity_type = "sharing_playlist"
    activity_data = "shared playlist '" + playlist_title + "' with " + recipient + "."
    try:
        data = {"activity_type": activity_type, "activity_data": activity_data}
        response = requests.post(f"http://activity:5000/activity/{username}/log", json=data)
        if response.status_code == 200 or response.status_code == 201:
            return response.json()["success"]
        return False
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return False
    
def is_playlist_owner(playlist_id, username):
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM playlists WHERE id = %s AND creator = %s;", (playlist_id, username))
        return bool(cur.fetchone()[0]) # Either True or False
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return False

def share_playlist(playlist_id, username, recipient):
    try:
        if playlist_exists("", "", id=playlist_id) and user_exists(username) and user_exists(recipient) and not playlist_shared_with_user(playlist_id, username, recipient) and username != recipient and is_playlist_owner(playlist_id, username):
            cur = conn.cursor()
            cur.execute("INSERT INTO shared_playlists (username, shared_with_username, playlist_id) VALUES (%s, %s, %s);", (username, recipient, playlist_id))
            conn.commit()
            log_playlist_sharing = share_playlist_log_activity(playlist_id, username, recipient)
            if not log_playlist_sharing:
                print("Failed to log playlist sharing", flush=True)
            return {"success": True}, 201
        else:
            print("Cannot share playlist.", flush=True)
            sys.stdout.flush()
            return {"success": False}, 409
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return {"success": False}, 500
    
def get_playlist_id(title, owner):
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM playlists WHERE name = %s AND creator = %s;", (title, owner))
        return cur.fetchone()[0]
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return None

def get_playlist_by_id(playlist_id):
    try:
        cur = conn.cursor()
        cur.execute("SELECT name, creator FROM playlists WHERE id = %s;", (playlist_id,))
        return cur.fetchone()
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return []
    
class AllPlaylists(Resource):
    def get(self):
        """Get all playlists"""
        return all_playlists()
        
    def post(self):
        """Creating a playlist"""
        args = flask_request.get_json()
        return create_playlist(args['title'], args['owner'])
    
class Playlist(Resource):
    def get(self, playlist_id):
        """Get a playlist with id=playlist_id"""
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT id, name, creator FROM playlists WHERE id = {playlist_id};")
            return cur.fetchall(), 200
        except Exception as e:
            print(e, flush=True)
            sys.stdout.flush()
            return [], 500


class AllUserPlaylists(Resource):
    def get(self, username):
        """Get all playlists created by a user and shared with a user"""
        try:
            if user_exists(username):
                cur = conn.cursor()
                cur.execute("SELECT id, name, creator FROM playlists WHERE creator = %s OR id IN (SELECT playlist_id FROM shared_playlists WHERE shared_with_username = %s);", (username, username))
                return cur.fetchall(), 200
            return [], 404
        except Exception as e:
            print(e, flush=True)
            sys.stdout.flush()
            return [], 500
    
class CreatedPlaylists(Resource):
    def get(self, username):
        """Get all playlists created by a user"""
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name, creator FROM playlists WHERE creator = %s;", (username,))
            return cur.fetchall(), 200
        except Exception as e:
            print(e, flush=True)
            sys.stdout.flush()
            return [], 500
    
class SharedPlaylists(Resource):
    def get(self, username):
        """Get all playlists shared with a user"""
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name, creator FROM playlists WHERE id IN (SELECT playlist_id FROM shared_playlists WHERE shared_with_username = %s);", (username,))
            return cur.fetchall(), 200
        except Exception as e:
            print(e, flush=True)
            sys.stdout.flush()
            return [], 500

class PlaylistSongs(Resource):
    def get(self, playlist_id):
        """Get all songs in a playlist"""
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT title, artist FROM playlist_songs WHERE playlist_id = {playlist_id};")
            return cur.fetchall(), 200
        except Exception as e:
            print(e, flush=True)
            sys.stdout.flush()
            return [], 500
    
    def put(self, playlist_id):
        """Adding a song to a playlist"""
        args = flask_request.args
        return add_song_to_playlist(playlist_id, args['artist'], args['title'])
    
class SharePlaylist(Resource):
    def post(self, playlist_id):
        """Share a playlist with another user"""
        args = flask_request.get_json()
        return share_playlist(playlist_id, args['owner'], args['recipient'])

api.add_resource(AllPlaylists, '/playlists/')
api.add_resource(Playlist, '/playlists/<int:playlist_id>/')

api.add_resource(AllUserPlaylists, '/playlists/<string:username>/')
api.add_resource(CreatedPlaylists, '/playlists/<string:username>/created/')
api.add_resource(SharedPlaylists, '/playlists/<string:username>/sharedwith/')

api.add_resource(PlaylistSongs, '/playlists/<int:playlist_id>/songs/')
api.add_resource(SharePlaylist, '/playlists/<int:playlist_id>/share/')

