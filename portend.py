#!/usr/bin/env python3

from mysql.connector import connect, Error
from flask import Flask
from json import dumps
import os
import datetime

app = Flask(__name__)

# Connect to the database
def connectToDB():
    try:
        cn = connect(
            host = "localhost",
            user = os.environ.get("DB_USER"),
            password = os.environ.get("DB_PASS"),
            database = "portfolio"
        )
        return cn;
    except Error as e:
        print(e)

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

    print(res)

    return res


def dictListToJSON(li):
    res = ""
    # Iterate over all dictionaries in list.
    for d in li:
        fixedD = fixDict(d)
        res += dumps(fixedD)
    return res


# Endpoint that returns all posts
@app.route("/api/posts")
def allPosts():
    cnx = connectToDB()
    return dictListToJSON(fetchResults(cnx, "SELECT * FROM posts"))
    cnx.close()

