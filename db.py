import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("PASSWORD"),
        database=os.getenv("DATABASE")
    )

    return connection