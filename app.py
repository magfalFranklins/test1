from datetime import datetime, timezone
from dotenv import load_dotenv
from flask import Flask, request
from datetime import datetime, timezone
import psycopg2
from psycopg2 import sql
import os

CREATE_USER_TABLE = (
    "CREATE TABLE IF NOT EXISTS user_table (id SERIAL, user_name TEXT PRIMARY KEY, password TEXT, alias TEXT, school TEXT, program TEXT, birth TIMESTAMP, date TIMESTAMP, points INTEGER, achievments TEXT []);"
)

CREATE_TODOS_TABLE = (
    "CREATE TABLE IF NOT EXISTS todo_table (user_name TEXT, todo TEXT, type_of_excersice TEXT, priority INTEGER, deadline TIMESTAMP, est_time INTEGER, calender BOOL, FOREIGN KEY(user_name) REFERENCES user_table(user_name) ON DELETE CASCADE);"
)

DROP_TABLE = (
    "DROP TABLE IF EXISTS {table}"
)

INSERT_USER = "INSERT INTO user_table (user_name, password, alias, school, program, birth, date, points, achievments) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"

INSERT_TODO = "INSERT INTO todo_table (user_name, todo, type_of_excersice, priority, deadline, est_time, calender) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING user_name;"

GET_USER = """SELECT * FROM user_table WHERE id = (%s)"""

USER_LOGIN = """SELECT * FROM users_demo5 WHERE user_name = (%s)"""

url = os.environ.get("DATABASE_URL")
connection = psycopg2.connect(url)
app = Flask(__name__)

# Test
@app.get("/hello")
def home():
    return "Hello, world"

# Drop tables
@app.post("/api/drop_table")
def drop_table():
    data = request.get_json()
    table_name = data["table"] 
    with connection:
        with connection.cursor() as cursor:
            query = sql.SQL(DROP_TABLE)
            query = query.format(table=sql.Identifier(table_name))
            cursor.execute(query)
    return {"status": 'OK'}, 201

# Create empty tables in DB
@app.post("/api/create_db_tables")
def add_tables():
    data = request.get_json()
    user_table = data["user_table"] 
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_USER_TABLE)
            cursor.execute(CREATE_TODOS_TABLE)
    return {"status": "OK"}, 201

# Create new user
@app.post("/api/create_user")
def add_user():
    data = request.get_json()
    user_name = data["user_name"]
    password = data["password"]
    alias = data["alias"]
    school = data["school"]
    program = data["program"]
    birth = datetime.strptime(data["birth"], "%m-%d-%Y")
    date = datetime.now(timezone.utc)
    points = 0
    achievments = ['Går bra']   
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_USER, (user_name, password, alias, school, program, birth, date, points, achievments))
            user_id = cursor.fetchone()[0]
    return {"id": user_id, "message": f"User {user_name} with id: {user_id} created."}, 201

# Create TODO
@app.post("/api/create_todo")
def add_todo():
    data = request.get_json()
    user_name = data["user_name"]
    todo = data["todo"]
    type_of_excersice = data["type_of_excersice"]
    priority = data["priority"]
    deadline = datetime.strptime(data["deadline"], "%m-%d-%Y")
    est_time = data["est_time"]
    calender = data["calender"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_TODO, (user_name, todo, type_of_excersice, priority, deadline, est_time, calender))
            user_name = cursor.fetchone()[0]
    return {"id": user_name, "message": f"User {user_name} added TODO {todo}."}, 201


# Login to user
@app.get("/api/login")
def login():
    data = request.get_json()
    user = data["user_name"]
#    password = data["password"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(USER_LOGIN, (user,))
            name = cursor.fetchone()
    return {"name": name}, 201

@app.get("/api/user/<int:name_id>")
def get_room_all(name_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(GET_USER, (name_id,))
            name = cursor.fetchone()
        return {"id": name[0], "user_name":name[1], "password":name[2] , "alias":name[3]}