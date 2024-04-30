# DS_Assignment2

The goal of the assignment is twofold:

• First, you should decompose a problem in microservices, i.e., you should
provide a description of the functionality that each microservice has, which
data storage it uses and the communications between microservices.

• Secondly, you should implement a part of the problem using the Docker/PodMan
toolbox.


<p>&nbsp;</p>

To run the application, execute the run.sh script in the root folder.

---

<p>&nbsp;</p>

## **Microservices (part 1):**

1.  **authentication**
    - ### **features implemented:**
        1. A user can create a profile (Register).
        2. The site can verify username & password combinations (Login)
    - ### **databases:**
        - authentication database (authentication_persistance)
            - TABLE authentication(username: TEXT PK, password: TEXT)
    - ### **communication with other microservices:**
        - in relation with friend and playlist microservices, but no requests to other microservices
    - ### **feature grouping explanation:**
        - Both features, and only these two features, handle user authentication on the website. The authentication microservice keeps track of the registered users and handles the login.

2. ### **friend**
    - ### **features implemented:**
        3. A user has the ability to add other users as friends.
        4. The user can view a list of all its friends.
    - ### **databases:**
        - friend database (friend_persistance)
            - TABLE friend(username: TEXT PK, friendname: TEXT PK)
    - ### **communication with other microservices:**
        - communicates with authentication (check if user exists) and activity microservice (logging of friend request).
    - ### **feature grouping explanation:**
        - Both features, and only these two features, primarily handle friend relations. The friend microservice keeps track of friendships.

3. ### **playlist**
    - ### **features implemented:**
        5. The user can create playlists.
        6. The user can add songs to a playlist.
        7. The user can view all songs in a playlist.
        8. The user can share a playlist with another user
    - ### **databases:**
        - playlist database (playlist_persistance)
            - TABLE playlists(id: SERIAL PK, name, creator)
            - TABLE playlist_songs(id: SERIAL PK, playlist_id: INTEGER RF playlists(id), artist: TEXT, title: TEXT)
            - TABLE shared_playlists(username: TEXT PK, shared_with_username: TEXT PK, playlist_id INTEGER PK RF playlists(id))
    - ### **communication with other microservices:**
        - communicates with authentication (check if user exists), songs (check if song exists in song database) and activity microservice (logging of playlist creation, sharing or song addition).
    - ### **feature grouping explanation:**
        - All the four features, and these features in particular, handle everything related to playlists. The playlist microservice handles the creation of, song addition to, the viewing of and the sharing of playlists.

4. ### **activity**
    - ### **features implemented:**
        9. Each user has a feed that lists the last N activities of its friends. (sorted by time) Activities are : creating a playlist, adding a song to a playlist, making a friend and sharing a playlist with a friend.
    - ### **databases:**
        - activity database (activity_persistance)
            - TABLE activity(id: SERIAL PK, username: TEXT, activity_type ENUM(...), activity_data: TEXT, created_at: TIMESTAMP)
    - ### **communication with other microservices:**
        - communicates with authentication (check if user exists) and friend microservice (getting all friends of a user).
    - ### **feature grouping explanation:**
        - This feature requires a feed (activity) micro service that handles the logging of the events described in the feature. The feed should be a standalone microservice, not attached to others as that would be disorganized and messy. Besides, the big social media sites also do this.

5. ### **songs**
    - ### **features implemented:**
        - Not in assignment.
    - ### **databases:**
        - songs database (songs_persistance)
            - TABLE songs(artist: TEXT PK, title: TEXT PK)
    - ### **communication with other microservices:**
        - None.
    - ### **feature grouping explanation:**
        - None.

---

## **Features (part 2):**

## (API manual:)

<p>&nbsp;</p>

## authentication microservice:

<p>&nbsp;</p>

### AllUsersResource GET Method

**Description:**

This method retrieves all users in the user database (= authentication database) (limit=1000).

**Request:**
- Endpoint: `/users/`
- HTTP Method: GET
- Parameters: None

**Response:**

HTTP Status Code: 200 OK

Response Body:
```
The response body contains a list of list(user)
```
---
### UserExists GET Method

**Description:**

This method checks whether a user exists.

**Request:**
- Endpoint: `/users/exist/`
- HTTP Method: GET
- Parameters:
    * username : string (required) username of the user

**Response:**

HTTP Status Code: 200 OK

Response Body:
```
The response body contains a JSON object with the following properties:
    success: bool
```
---
### LoginUser POST Method

**Description:**

This method handles the login of a user with a given username and password.

**Request:**
- Endpoint: `/login/`
- HTTP Method: POST
- Parameters (in json):
    * username : string (required) username of the user
    * password : string (required) password of the user

**Response:**

HTTP Status Code: 200 OK

Response Body:
```
The response body contains a JSON object with the following properties:
    success: bool
```
---
### RegisterUser POST Method

**Description:**

This method handles the registration of a user with a given username and password.

**Request:**
- Endpoint: `/register/`
- HTTP Method: POST
- Parameters (in json):
    * username : string (required) username of the user
    * password : string (required) password of the user

**Response:**

HTTP Status Code: 201 Created

Response Body:
```
The response body contains a JSON object with the following properties:
    success: bool
```
---
<p>&nbsp;</p>

## friend microservice:

<p>&nbsp;</p>

### AllFriends GET Method

**Description:**

This method returns all friends of a user.

**Request:**
- Endpoint: `/friends/`
- HTTP Method: GET
- Parameters:
    * user : string (required) username of the user

**Response:**

HTTP Status Code: 200 OK

Response Body:
```
The response body contains a list of lists of users
```
---
### AddFriend PUT Method

**Description:**

This method adds a user as a friend.

**Request:**
- Endpoint: `/friends/add/`
- HTTP Method: PUT
- Parameters:
    * user : string (required) username of the user
    * friend : string (required) username of the friend

**Response:**

HTTP Status Code: 201 Created

Response Body:
```
The response body contains a JSON object with the following properties:
    success: bool
```
---
<p>&nbsp;</p>

## playlist microservice:

<p>&nbsp;</p>

### AllPlaylists GET Method

**Description:**

This method returns all playlists (limit=20) that exist.

**Request:**
- Endpoint: `/playlists/`
- HTTP Method: GET
- Parameters: None

**Response:**

HTTP Status Code: 200 OK

Response Body:
```
The response body contains a list of list(playlist_id, name, creator)
```
---
### AllPlaylists POST Method

**Description:**

This method handles the creation of a playlist by a user.

**Request:**
- Endpoint: `/playlists/`
- HTTP Method: POST
- Parameters (in json):
    * title : string (required) title of the playlist
    * owner : string (required) user that creates the playlist

**Response:**

HTTP Status Code: 201 Created

Response Body:
```
The response body contains a JSON object with the following properties:
    success: bool
```
---
### Playlist GET Method

**Description:**

This method returns the playlist with id=playlist_id.

**Request:**
- Endpoint: `/playlists/<int:playlist_id>/`
- HTTP Method: GET
- Parameters: 
    * playlist_id : int (required) playlist id

**Response:**

HTTP Status Code: 200 OK

Response Body:
```
The response body contains a list of list(playlist_id, name, creator)
```
---
### AllUserPlaylists GET Method

**Description:**

This method returns all the user's playlists.

**Request:**
- Endpoint: `/playlists/<string:username>/`
- HTTP Method: GET
- Parameters: 
    * username : string (required) username of the user

**Response:**

HTTP Status Code: 200 OK

Response Body:
```
The response body contains a list of list(playlist_id, name, creator)
```
---
### CreatedPlaylists GET Method

**Description:**

This method returns all the playlists that the user created himself.

**Request:**
- Endpoint: `/playlists/<string:username>/created/`
- HTTP Method: GET
- Parameters: 
    * username : string (required) username of the user

**Response:**

HTTP Status Code: 200 OK

Response Body:
```
The response body contains a list of list(playlist_id, name, creator)
```
---
### SharedPlaylists GET Method

**Description:**

This method returns all the playlists that are shared with the user.

**Request:**
- Endpoint: `/playlists/<string:username>/sharedwith/`
- HTTP Method: GET
- Parameters: 
    * username : string (required) username of the user

**Response:**

HTTP Status Code: 200 OK

Response Body:
```
The response body contains a list of list(playlist_id, name, creator)
```
---
### PlaylistSongs GET Method

**Description:**

This method returns all the playlists that are shared with the user.

**Request:**
- Endpoint: `/playlists/<int:playlist_id>/songs/`
- HTTP Method: GET
- Parameters: 
    * playlist_id : int (required) playlist id

**Response:**

HTTP Status Code: 200 OK

Response Body:
```
The response body contains a list of list(title, artist)
```
---
### SharePlaylist POST Method

**Description:**

This method handles the sharing of a playlist with another user.

**Request:**
- Endpoint: `/playlists/<int:playlist_id>/share/`
- HTTP Method: POST
- Parameters (in json): 
    * owner : string (required) username of the sharer
    * recipient : string (required) username of the recipient

**Response:**

HTTP Status Code: 201 Created

Response Body:
```
The response body contains a JSON object with the following properties:
    success: bool
```
---
<p>&nbsp;</p>

## activity microservice:

<p>&nbsp;</p>

### AllActivity GET Method

**Description:**

This method retrieves all activities.

**Request:**
- Endpoint: `/activity/`
- HTTP Method: GET
- Parameters (): None

**Response:**

HTTP Status Code: 200 OK

Response Body:
```
The response body contains a list of list(username, activity_type, activity_data, created_at)
```
---
### UserFeed GET Method

**Description:**

This method retrieves the user's feed (his friends' activities) (limit='amount' parameter).

**Request:**
- Endpoint: `/activity/<string:username>/`
- HTTP Method: GET
- Parameters ():
    * username : string (required) username of the user
    * amount : int (required) amount of feed items

**Response:**

HTTP Status Code: 200 OK

Response Body:
```
The response body contains a list of list(username, activity_type, activity_data, created_at)
```
---
### LogUserActivity POST Method

**Description:**

This method logs the users activity (creating/sharing/adding song to a playlist or adding a friend).

**Request:**
- Endpoint: `/activity/<string:username>/log/`
- HTTP Method: POST
- Parameters ():
    * username : string (required) username of the user
    * activity_type : string (required) type of activity
    * activity_data : string (required) activity description

**Response:**

HTTP Status Code: 201 Created

Response Body:
```
The response body contains a JSON object with the following properties:
    success: bool
```
---
<p>&nbsp;</p>

## songs microservice:

<p>&nbsp;</p>

### AllSongsResource GET Method

**Description:**

This method retrieves all the songs in the songs database (limit=1000).

**Request:**
- Endpoint: `/songs/`
- HTTP Method: GET
- Parameters (): None

**Response:**

HTTP Status Code: 200 OK

Response Body:
```
The response body contains a list of list(title, artist)
```
### SongExists GET Method

**Description:**

This method retrieves all the songs in the songs database (limit=1000).

**Request:**
- Endpoint: `/songs/exist/`
- HTTP Method: GET
- Parameters (): 
    * title : string (required) title of the song
    * artist : string (required) artist of the song

**Response:**

HTTP Status Code: 200 OK

Response Body:
```
The response body contains a boolean value
```
### AddSong PUT Method

**Description:**

This method retrieves adds a song to the songs database.

**Request:**
- Endpoint: `/songs/add/`
- HTTP Method: PUT
- Parameters (): 
    * title : string (required) title of the song
    * artist : string (required) artist of the song

**Response:**

HTTP Status Code: 200 OK

Response Body:
```
The response body contains a boolean value
```
---

### **Explanatory notes:**

All of the endpoints (per microservice) are documented above. Below are the specific endpoints for the required features in the project to give a clear overview.

Endpoints:

- **authentication**: resource(RegisterUser, `/register/`)

    * feature: 1. A user can create a profile (Register).

- **authentication**: resource(LoginUser, `/login/`)

    * feature: 2. The site can verify username & password combinations (Login)

- **friend**: resource(AddFriend, `/friends/add/`)

    * feature: 3. A user has the ability to add other users as friends.

- **friend**: resource(AllFriends, `/friends/`)

    * feature: 4. The user can view a list of all its friends.

- **playlist**: resource(AllPlaylists, `/playlists/`)

    * feature: 5. The user can create playlists.

- **playlist**: resource(PlaylistSongs, `/playlists/<int:playlist_id>/songs/`) (PUT)

    * feature: 6. The user can add songs to a playlist.

- **playlist**: resource(PlaylistSongs, `/playlists/<int:playlist_id>/songs/`) (GET)

    * feature: 7. The user can view all songs in a playlist.

- **playlist**: resource(SharePlaylist, `/playlists/<int:playlist_id>/share/`)

    * feature: 8. The user can share a playlist with another user.

- **activity**: resource(UserFeed, `/activity/<string:username>/`)

    * feature: 9. Each user has a feed that lists the last N activities of its friends. (sorted by time) Activities are : creating a playlist, adding a song to a playlist, making a friend and sharing a playlist with a friend.

<p>&nbsp;</p>

Everything was made as simple as possible so that users of the api can easily navigate through it. For the authentication microservice, we have `/register` and `/login` because it's easy, and data can be passed in json format since both endpoints use POST requests (to not show username & password in url). `/users/exist/` together with a username query parameter checks if a user exists. Removing the last part of the url, we get `/users/`, which returns all users in the user database.

For the friend microservice, we have `/friends/add/` which takes two query parameters: user and friend. This is an easy and short way to do this. Removing the last part of the url, we get `/friends/`, which returns a user's friends (we pass the username as a query parameter 'user').

For the playlist microservice, we have `/playlists/`, where the GET method returns all playlists ever created and the POST method allows a user to create a playlist by passing 'title' and 'owner' in a json dictonary. Next, to keep it RESTful, `/playlists/<int:playlist_id>/` returns us the playlist with id=playlist_id. To get a user's playlists, we simply add a username url parameter to the base playlists url making it: `/playlists/<string:username>/`, which gives us the playlists that are created by and shared with the user. For the separate cases, we can use: `/playlists/<string:username>/created/` and `/playlists/<string:username>/sharedwith/` respectively. Finally, to get all songs in a playlist (GET) or to add a song to a playlist (PUT, which uses query parameters: 'artist' and 'title'), we can build upon our url endpoint in the beginning, namely we use `/playlists/<int:playlist_id>/songs/` (is good since `/playlists/<int:playlist_id>/` is defined already). To share a playlist we subsequently have `/playlists/<int:playlist_id>/share/`, which uses query parameters: 'owner' and 'recipient'. I implemented it so that the recipient can then add songs to that playlist, but he/she cannot share it with another user.

For the activity microservice, which handles the user feed, we begin with `/activity/`, which returns all activities. To get a certain user's feed, we can use `/activity/<string:username>/` with an amount parameter to limit the amount of feed items. Finally, `/activity/<string:username>/log/` is used to log user activity (creating/sharing/adding song to a playlist or adding a friend) with a POST request where we pass the activity type ('activity_type') and activity data ('activity_data') in a json map. This log request is made after the corresponding request in the (other) (corresponding) microservice each time, and not in the 'central' gui service, because then we don't need to check if the microservice is down before we log the activity, but it's done automatically in the microservice itself (or not if it's down).

The 'hacking' the URL can be done in any endpoint above, and there will always be a correct response and result. The order in which I did my explanation and the endpoints can be used to verify this.