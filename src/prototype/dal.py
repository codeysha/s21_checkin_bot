import mysql.connector
from mysql.connector import Error
import datetime


def db_connect():
    connection = None
    try:
        config = {
            "user": "checkinbot",
            "password": "botpassword",
            "host": "5.23.55.31",
            "port": 3306,
            "database": "checkin_bot_db"
        }
        connection = mysql.connector.connect(**config)
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection


def get_all_users():
    db = db_connect();
    cursor = db.cursor(prepared=True)
    query = 'SELECT * FROM users'
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        print(f"The error '{e}' occurred")


def get_user_by_id(user_id):
    db = db_connect();
    cursor = db.cursor(buffered=True, dictionary=True)
    query = """SELECT * FROM users WHERE telegram_id = %s"""
    parameter = (user_id,)
    try:
        cursor.execute(query, parameter)
        rs = cursor.fetchone()
        if not rs:
            rs = 0
        return rs
        cursor.close()
        db.close()
        return rs
    except Error as e:
        print(f"The error '{e}' occurred")


def save_access_code(code, email):
    exp_dt = datetime.datetime.now() + datetime.timedelta(minutes=2)
    db = db_connect();
    cursor = db.cursor(buffered=True)
    query = """INSERT INTO access_codes (code, expired_dt, email) VALUES(%s, %s, %s)"""
    parameter = (code, exp_dt.__str__(), email)
    try:
        cursor.execute(query, parameter)
        access_code_no = cursor.lastrowid
        db.commit()
        cursor.close()
        db.close()
        print(f"access code saved to db with 3 min expired datetime row id: {access_code_no}")
    except Error as e:
        print(f"The error '{e}' occurred")


def find_access_code(entered_code):
    db = db_connect();
    cursor = db.cursor(buffered=True, dictionary=True)
    query = """SELECT * FROM access_codes WHERE code = %s AND expired_dt > %s LIMIT 1"""
    parameter = (entered_code, datetime.datetime.now().__str__())
    try:
        cursor.execute(query, parameter)
        rs = cursor.fetchone()
        if not rs:
            rs = 0
        return rs
    except Error as e:
        print(f"The error '{e}' occurred")


def save_user(user_id, email):
    role = get_role_from_email(email)
    db = db_connect();
    cursor = db.cursor(buffered=True)
    query = """INSERT INTO users (email, telegram_id, role) VALUES(%s, %s, %s)"""
    parameter = (email, user_id, role)
    try:
        cursor.execute(query, parameter)
        row_no = cursor.lastrowid
        db.commit()
        cursor.close()
        db.close()
        print(f"access code saved to db with 3 min expired datetime row id: {row_no}")
    except Error as e:
        print(f"The error '{e}' occurred")


def get_role_from_email(email):
    if "@" not in email:
        return 0
    res = email.split('@')[1]
    if res == 'student.21-school.ru':
        return 'student'
    elif res == '21-school.ru':
        return 'adm'
    else:
        return 0


def save_event(data, quiz_id):
    db = db_connect();
    cursor = db.cursor(buffered=True)
    query = """
    INSERT INTO events 
        (type, city, event_name, description, lon, lat, event_date, start_time, end_time, quiz_id) 
    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
    parameter = (
        data['type'],
        data['city'],
        data['event_name'],
        data['description'],
        data['longitude'],
        data['latitude'],
        data['date'],
        data['time_start'],
        data['time_finish'],
        quiz_id,
    )
    try:
        cursor.execute(query, parameter)
        row_no = cursor.lastrowid
        db.commit()
        cursor.close()
        db.close()
        print(f"event add to db, row id: {row_no}")
    except Error as e:
        print(f"The error '{e}' occurred")


def get_all_events():
    db = db_connect();
    cursor = db.cursor(prepared=True)
    query = 'SELECT * FROM events'
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        print(f"The error '{e}' occurred")
