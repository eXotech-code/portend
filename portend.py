#!/usr/bin/env python3

from mysql.connector import connect, Error
from flask import Flask, request, abort
from json import dumps
import os
import sys
import datetime
import traceback

app = Flask(__name__)

# Connect to the database
def connectToDB():
    try:
        cn = connect(
            host = "db",
            user = os.environ.get("DB_USER"),
            password = os.environ.get("DB_PASS"),
            database = "portfolio",
            autocommit = True
        )
        return cn;
    except Error:
        traceback.print_exc()
        sys.exit(1)

# Fetches results of a passed query.
def fetchResults(query):
    # Initialize a new connection.
    cnx = connectToDB()

    try:
        # Fetch everything as a dict to preserve column names.
        with cnx.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            return cursor.fetchall()
    except Error:
        traceback.print_exc()

# Utitlity function that updates one cell with
# specified data and returns the contents of updated cell.
# Conditions is a string of what goes after WHERE statement.
def updateRow(table, column, data, conditions):
    cnx = connectToDB()

    query = f"UPDATE {table} SET {column}={data} WHERE {conditions}"

    try:
        with cnx.cursor() as cursor:
            cursor.execute(query)
            return fetchResults(f"SELECT {column} FROM {table} WHERE {conditions}")
    except Error:
        traceback.print_exc()


# If one of the dictionaries in list contains a datetime.datetime object
# it creates a new list of dicts but with those objects converted to strings.
def fixDict(d):
    # Resulting fixed dict
    res = {}

    # If something inside the dict is in datetime format, extract it to string.
    for key in d:
        if type(d[key]) is datetime.datetime:
            res[key] = datetime.datetime.strftime(d[key], "%B %-d, %Y at %H:%M")
        else:
            # If it is just a normal value...
            res[key] = d[key]

    return res

def dictListToJSON(li):
    listJSON = []

    # Iterate over all dictionaries in list.
    for d in li:
        fixedD = fixDict(d)

        listJSON.append(fixedD)

    return dumps(listJSON)

# Check if username-password combination got from request matches any user
# profiles already present in the database.
def passwordMatch(username, password):
    # Fetch user if his/her username is and password combination is correct.
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    user = fetchResults(query) # fetchResult returns a list. So in this case it contains one entry.

    # If the user has been found.
    if user:
        return True

    return False

# Generate a token in a form of UUID1 for a new login session.
# and assign it to user.
def newToken(username):
    return updateRow("users", "token", "UUID()", f"username='{username}'")


#### ENDPOINTS ####

pQuery = "SELECT * FROM posts" # Standard query used to retrieve posts

# Endpoint that returns all posts
@app.route("/api/posts")
def allPosts():
    return dictListToJSON(fetchResults(pQuery))
    cnx.close()

# Endpoint that returns a specified amount of posts
@app.route("/api/posts/<int:posts_amount>")
def postsLimited(posts_amount):
    # Limit amount of posts returned.
    res = fetchResults(pQuery + " LIMIT " + str(posts_amount))

    # If client is asking for more posts than is currently available,
    # return the rest as empty objects.
    if len(res) < posts_amount:
        for i in range(len(res), posts_amount):
            res.append({
                "id": i+1, # Because it started with 1 instead of 0.
                "title": "ERROR: Resource not available",
                "date": datetime.datetime(1970, 1, 1, 0, 0),
                "description": """The requested resource could not be found in the database.
                                  This happens when there's not enough content in the database or
                                  the request contains errors.""",
                "hero_id": None
            })

    return dictListToJSON(res)

@app.route("/api/admin/auth", methods=["POST"])
def authorize():
    if passwordMatch(request.form['username'], request.form['password']):
        print("Password matches!")
        token = newToken(request.form['username']) # Generate a new token and store it into the database.

        if token is not None:
            return token[0] # Send token to client.
        else:
            abort(401)
    else:
        abort(401) # Return 401 if the username-password combination is invalid.
