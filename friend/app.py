from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2
import requests
import sys

parser = reqparse.RequestParser()
parser.add_argument('user')
parser.add_argument('friend')

app = Flask("friend")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="friend", user="postgres", password="postgres", host="friend_persistence")
        print("DB connection succesful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")

def get_friends(user, limit=50):
    cur = conn.cursor()
    cur.execute(f"SELECT friendname FROM friend WHERE username = '{user}' LIMIT {limit};")
    return cur.fetchall(), 200

def user_exists(friendname):
    try:
        # API call to authentication microservice to check if friendname exists
        response = requests.get("http://authentication:5000/users/exist/?username=" + friendname)
        if response.status_code == 200:
            return response.json()["success"]
        return False
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return False
    
def is_already_friend(username, friendname):
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM friend WHERE username = '{username}' AND friendname = '{friendname}';")
    return bool(cur.fetchone()[0])  # Either True or False

def add_friend_log_activity(username, friendname):
    # API call to activity microservice to log adding of a friend
    activity_type = "making_friend"
    activity_data = "added " + friendname + " as a friend."
    data = {"activity_type": activity_type, "activity_data": activity_data}
    try:
        response = requests.post(f"http://activity:5000/activity/{username}/log", json=data)
        if response.status_code == 200 or response.status_code == 201:
            return response.json()["success"]
        return False
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return False

def add_friend(username, friendname):
    if user_exists(username) and user_exists(friendname) and not is_already_friend(username, friendname) and username != friendname:
        cur = conn.cursor()
        cur.execute("INSERT INTO friend (username, friendname) VALUES (%s, %s);", (username, friendname))
        conn.commit()
        log_friend_request = add_friend_log_activity(username, friendname)
        if not log_friend_request:
            print("Failed to log friend request", flush=True)
        return {"success": True}, 201
    return {"success": False}, 200

class AllFriends(Resource):
    def get(self):
        args = flask_request.args
        return get_friends(args['user'])

class AddFriend(Resource):
    def put(self):
        args = flask_request.args
        return add_friend(args['user'], args['friend'])

api.add_resource(AllFriends, '/friends/')
api.add_resource(AddFriend, '/friends/add/')

