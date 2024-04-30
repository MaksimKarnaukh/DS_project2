from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2
import requests
from datetime import datetime
import sys

parser = reqparse.RequestParser()
parser.add_argument('username')
# parser.add_argument('activity_type')
# parser.add_argument('activity_data')
parser.add_argument('amount')

app = Flask("activity")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="activity", user="postgres", password="postgres", host="activity_persistence")
        print("DB connection succesful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")

def add_activity(username, activity_type, activity_data):
    try:
        if user_exists(username):
            cur = conn.cursor()
            cur.execute("INSERT INTO activity (username, activity_type, activity_data) VALUES (%s, %s, %s);", (username, activity_type, activity_data))
            conn.commit()
            return {"success": True}, 201
        return {"success": False}, 400
    except psycopg2.Error:
        return {"success": False}, 400
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return {"success": False}, 500

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

class AllActivity(Resource):
    def get(self):
        try:
            cur = conn.cursor()
            cur.execute(f"SELECT username, activity_type, activity_data, created_at FROM activity;")
            return cur.fetchall(), 200
        except Exception as e:
            print(e, flush=True)
            sys.stdout.flush()
            return [], 500
    
class UserFeed(Resource):
    def get(self, username):
        """get the activity feed of a user"""
        try:
            args = flask_request.args
            amount = args['amount']

            # get friends of the user
            friends = []
            if user_exists(username):
                response = requests.get(f"http://friend:5000/friends/?user={username}")
            
                if response.status_code == 200 or response.status_code == 201:
                    friends = response.json()
                    friends = [friend[0] for friend in friends]

            # get activity of the user's friends
            activities = []
            if len(friends) != 0:
                cur = conn.cursor()
                if len(friends) == 1:
                    cur.execute(f"SELECT username, activity_type, activity_data, created_at FROM activity WHERE username = '{friends[0]}' ORDER BY created_at DESC LIMIT {amount};")
                else:
                    cur.execute(f"SELECT username, activity_type, activity_data, created_at FROM activity WHERE username IN {tuple(friends)} ORDER BY created_at DESC LIMIT {amount};")
                activities = cur.fetchall()
                activities = [(username, activity_type, activity_data, created_at.strftime("%Y-%m-%d %H:%M:%S")) for username, activity_type, activity_data, created_at in activities]
            return activities, 200
        except Exception as e:
            print(e, flush=True)
            sys.stdout.flush()
            return [], 500

class LogUserActivity(Resource):
    def post(self, username):
        """log an activity of a user"""
        args = flask_request.get_json()
        activity_type = args['activity_type']
        activity_data = args['activity_data']
        return add_activity(username, activity_type, activity_data)
        
api.add_resource(AllActivity, '/activity/')
api.add_resource(UserFeed, '/activity/<string:username>/')
api.add_resource(LogUserActivity, '/activity/<string:username>/log/')


