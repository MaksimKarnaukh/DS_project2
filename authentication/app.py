from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2
import sys

parser = reqparse.RequestParser()
parser.add_argument('username', type=str, required=True, help='No username provided', location='json')
parser.add_argument('password', type=str, required=True, help='No password provided', location='json')

app = Flask("authentication")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="authentication", user="postgres", password="postgres", host="authentication_persistence")
        print("DB connection succesful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")

def user_login_exists(username, password):
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM authentication WHERE username = %s AND password = %s;", (username, password))
        return {"success": bool(cur.fetchone()[0])}, 200  # Either True or False
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return {"success": False}, 500

def username_exists(username):
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM authentication WHERE username = %s;", (username,))
        row_count = bool(cur.fetchone()[0]) # Either True or False
        return {"success": row_count}, 200  
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return {"success": False}, 500

def register_user(username, password):
    try:
        if username_exists(username)[0]["success"]:
            return {"success": False}, 409
        
        cur = conn.cursor()
        cur.execute("INSERT INTO authentication (username, password) VALUES (%s, %s);", (username, password))
        conn.commit()
        return {"success": True}, 201
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return {"success": False}, 500
    
def all_users(limit=1000):
    try:
        cur = conn.cursor()
        cur.execute(f"SELECT username FROM authentication LIMIT {limit};")
        return cur.fetchall(), 200
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        return [], 500
    
class AllUsersResource(Resource):
    def get(self):
        return all_users()

class UserExists(Resource):
    def get(self):
        args = flask_request.args
        return username_exists(args['username'])

class LoginUser(Resource):
    def post(self):
        request_data = flask_request.get_json()
        return user_login_exists(request_data['username'], request_data['password'])

class RegisterUser(Resource):
    def post(self):
        request_data = flask_request.get_json()
        return register_user(request_data['username'], request_data['password'])

api.add_resource(AllUsersResource, '/users/')
api.add_resource(UserExists, '/users/exist/')
api.add_resource(LoginUser, '/login/')
api.add_resource(RegisterUser, '/register/')
