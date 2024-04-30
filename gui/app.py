from flask import Flask, render_template, redirect, request, url_for
import requests
import sys

app = Flask(__name__)


# The Username & Password of the currently logged-in User
username, password = None, None

session_data = dict()

def save_to_session(key, value):
    session_data[key] = value

def load_from_session(key):
    return session_data.pop(key) if key in session_data else None  # Pop to ensure that it is only used once


@app.route("/")
def feed():
    # ================================
    # FEATURE 9 (feed)
    #
    # Get the feed of the last N activities of your friends.
    # ================================

    global username

    N = 10

    feed = []
    if username is not None:
        try:
            response = requests.get(f"http://activity:5000/activity/{username}/?amount={N}")
            if response.status_code == 200 or response.status_code == 201:
                temp_list = response.json()
                feed = [[item[3], item[2], item[0]] for item in temp_list] # list of [created_at, activity_data, username]
        except Exception as e:
            print(e, flush=True)
            sys.stdout.flush()

    return render_template('feed.html', username=username, password=password, feed=feed)


@app.route("/catalogue")
def catalogue():
    try:
        songs = requests.get("http://songs:5000/songs").json()
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()
        songs = []

    return render_template('catalogue.html', username=username, password=password, songs=songs)


@app.route("/login")
def login_page():

    success = load_from_session('success')
    return render_template('login.html', username=username, password=password, success=success)


@app.route("/login", methods=['POST'])
def actual_login():
    req_username, req_password = request.form['username'], request.form['password']

    # ================================
    # FEATURE 2 (login)
    #
    # send the username and password to the microservice
    # microservice returns True if correct combination, False if otherwise.
    # Also pay attention to the status code returned by the microservice.
    # ================================
    success = False
    try:
        data = {'username': req_username, 'password': req_password}
        response = requests.post("http://authentication:5000/login", json=data, headers={'Content-Type': 'application/json'})

        if (response.status_code == 200 or response.status_code == 201) and response.json()["success"] == True:
            success = True
            global username, password
            username = req_username
            password = req_password

    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()

    save_to_session('success', success)
    return redirect('/login')


@app.route("/register")
def register_page():
    success = load_from_session('success')
    return render_template('register.html', username=username, password=password, success=success)


@app.route("/register", methods=['POST'])
def actual_register():

    req_username, req_password = request.form['username'], request.form['password']

    # ================================
    # FEATURE 1 (register)
    #
    # send the username and password to the microservice
    # microservice returns True if registration is successful, False if otherwise.
    #
    # Registration is successful if a user with the same username doesn't exist yet.
    # ================================
    success = False
    try:
        data = {'username': req_username, 'password': req_password}
        response = requests.post("http://authentication:5000/register", json=data, headers={'Content-Type': 'application/json'})

        if (response.status_code == 200 or response.status_code == 201) and response.json()["success"] == True:
            success = True
            global username, password
            username = req_username
            password = req_password

    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()

    save_to_session('success', success)
    return redirect('/register')


@app.route("/friends")
def friends():
    success = load_from_session('success')

    global username

    # ================================
    # FEATURE 4
    #
    # Get a list of friends for the currently logged-in user
    # ================================

    friend_list = []
    if username is not None:
        try:
            response = requests.get(f"http://friend:5000/friends/?user={username}")
            if (response.status_code == 200 or response.status_code == 201):
                temp_list = response.json()
                friend_list = [item[0] for item in temp_list]
        except Exception as e:
            print(e, flush=True)
            sys.stdout.flush()

    return render_template('friends.html', username=username, password=password, success=success, friend_list=friend_list)


@app.route("/add_friend", methods=['POST'])
def add_friend():

    # ==============================
    # FEATURE 3
    #
    # send the username of the current user and the username of the added friend to the microservice
    # microservice returns True if the friend request is successful (the friend exists & is not already friends), False if otherwise
    # ==============================

    global username
    req_username = request.form['username']

    success = False 
    if username is not None:
        try:
            response = requests.put(f"http://friend:5000/friends/add/?user={username}&friend={req_username}")
            if (response.status_code == 200 or response.status_code == 201) and response.json()["success"] == True:
                success = True
        except Exception as e:
            print(e, flush=True)
            sys.stdout.flush()

    save_to_session('success', success)

    return redirect('/friends')


@app.route('/playlists')
def playlists():
    global username

    my_playlists = []
    shared_with_me = []

    if username is not None:
        # ================================
        # FEATURE 5.1
        #
        # Get all playlists you created and all playlist that are shared with you. (list of id, title pairs)
        # ================================
        try:
            response = requests.get(f"http://playlist:5000/playlists/{username}/created")
            if (response.status_code == 200 or response.status_code == 201):
                temp_list = response.json()
                my_playlists = [(item[0], item[1]) for item in temp_list]
            response = requests.get(f"http://playlist:5000/playlists/{username}/sharedwith")
            if (response.status_code == 200 or response.status_code == 201):
                temp_list = response.json()
                shared_with_me = [(item[0], item[1]) for item in temp_list]
        except Exception as e:
            print(e, flush=True)
            sys.stdout.flush()

    return render_template('playlists.html', username=username, password=password, my_playlists=my_playlists, shared_with_me=shared_with_me)


@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    # ================================
    # FEATURE 5
    #
    # Create a playlist by sending the owner and the title to the microservice.
    # ================================
    global username
    title = request.form['title']

    if username is not None:
        try:
            data = {'owner': username, 'title': title}
            response = requests.post("http://playlist:5000/playlists", json=data, headers={'Content-Type': 'application/json'})
            if response.status_code == 200 or response.status_code == 201:
                pass
        except Exception as e:
            print(e, flush=True)
            sys.stdout.flush()
    
    return redirect('/playlists')


@app.route('/playlists/<int:playlist_id>')
def a_playlist(playlist_id):
    # ================================
    # FEATURE 7
    #
    # List all songs within a playlist
    # ================================
    songs = []
    try:
        response = requests.get(f"http://playlist:5000/playlists/{playlist_id}/songs")
        if response.status_code == 200:
            songs = response.json()
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()

    return render_template('a_playlist.html', username=username, password=password, songs=songs, playlist_id=playlist_id)


@app.route('/add_song_to/<int:playlist_id>', methods=["POST"])
def add_song_to_playlist(playlist_id):
    # ================================
    # FEATURE 6
    #
    # Add a song (represented by a title & artist) to a playlist (represented by an id)
    # ================================
    title, artist = request.form['title'], request.form['artist']

    try:
        response = requests.put(f"http://playlist:5000/playlists/{playlist_id}/songs/?title={title}&artist={artist}&playlist_id={playlist_id}")
        if response.status_code == 200 or response.status_code == 201:
            pass
    except Exception as e:
        print(e, flush=True)
        sys.stdout.flush()

    return redirect(f'/playlists/{playlist_id}')


@app.route('/invite_user_to/<int:playlist_id>', methods=["POST"])
def invite_user_to_playlist(playlist_id):
    # ================================
    # FEATURE 8
    #
    # Share a playlist (represented by an id) with a user.
    # ================================
    recipient = request.form['user']
    global username
    if username is not None:
        try:
            data = {'owner': username, 'recipient': recipient}
            response = requests.post(f"http://playlist:5000/playlists/{playlist_id}/share/", json=data, headers={'Content-Type': 'application/json'})
            if response.status_code == 200 or response.status_code == 201:
                pass
        except Exception as e:
            print(e, flush=True)
            sys.stdout.flush()

    return redirect(f'/playlists/{playlist_id}')


@app.route("/logout")
def logout():
    global username, password

    username = None
    password = None
    return redirect('/')
