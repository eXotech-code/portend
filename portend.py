#!/usr/bin/env python3

from mysql.connector import connect, Error
from flask import Flask
from json import dumps
import os
import sys
import datetime

app = Flask(__name__)

# Connect to the database
def connectToDB():
    try:
        cn = connect(
            host = "db",
            user = os.environ.get("DB_USER"),
            password = os.environ.get("DB_PASS"),
            database = "portfolio"
        )
        return cn;
    except Error as e:
        print(e)
        sys.exit(1)

def fetchResults(connection, query):
    try:
        # Fetch everything as a dict to preserve column names
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
    except Error as e:
        print(e)

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

#### ENDPOINTS ####

pQuery = "SELECT * FROM posts" # Standard query used to retrieve posts

# Endpoint that returns all posts
@app.route("/api/posts")
def allPosts():
    cnx = connectToDB()
    return dictListToJSON(fetchResults(cnx, pQuery))
    cnx.close()

# Endpoint that returns a specified amount of posts
@app.route("/api/posts/<int:posts_amount>")
def postsLimited(posts_amount):
    cnx = connectToDB()

    # Limit amount of posts returned.
    res = fetchResults(cnx, pQuery + " LIMIT " + str(posts_amount))

    # If client is asking for more posts than is currently available,
    # return the rest as empty objects.
    if len(res) < posts_amount:
        for i in range(len(res), posts_amount):
            res.append({
                "id": i,
                "title": "ERROR: Resource not available",
                "date": datetime.datetime(1970, 1, 1, 0, 0),
                "description": """The requested resource could not be found in the database.
                                  This happens when there's not enough content in the database or
                                  the request contains errors.""",
                "hero_id": None
            })

    return dictListToJSON(res)
