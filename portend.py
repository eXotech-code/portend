#!/usr/bin/env python3

from mysql.connector import connect, Error
import os

# Try connecting to the database
try:
    with connect(
        host = "localhost",
        user = os.environ.get("DB_USER"),
        password = os.environ.get("DB_PASS"),
    ) as connection:
        print(connection)
except Error as e:
    print(e)
