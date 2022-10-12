import pymysql
import os
import uuid


class StudentsResource:

    def __init__(self):
        pass

    @staticmethod
    def _get_connection():
        usr = os.environ.get("DBUSER")
        pw = os.environ.get("DBPW")
        h = os.environ.get("DBHOST")

        conn = pymysql.connect(
            user=usr,
            password=pw,
            host=h,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return conn

    @staticmethod
    def insert_student(uni, email, password, last_name, first_name, middle_name):
        if not (uni and email and last_name and first_name):
            return False
        conn = StudentsResource._get_connection()
        cur = conn.cursor()

        # generate a new token
        token = uuid.uuid4()
        if middle_name == "":
            sql = """
            INSERT INTO students_login_db.students(uni, last_name, first_name, email, password, status) 
            values (%s, %s, %s, %s, %s, %s);
            """
            cur.execute(sql, args=(uni, last_name, first_name, email, password, token))
        else:
            sql = """
            INSERT INTO students_login_db.students(uni, last_name, first_name, middle_name, email, password, status) 
            values (%s, %s, %s, %s, %s, %s, %s);
            """
            cur.execute(sql, args=(uni, last_name, first_name, middle_name, email, password, token))
        result = cur.rowcount
        return True if result == 1 else False

    @staticmethod
    def get_by_uni_email(uni="", email=""):
        # check if uni and email are both empty
        if uni == "" and email == "":
            return None
        sql = "SELECT * FROM students_login_db.students WHERE uni=%s or email=%s"
        conn = StudentsResource._get_connection()
        cur = conn.cursor()
        res = cur.execute(sql, args=(uni, email))
        result = cur.fetchone()

        return result

    @staticmethod
    def student_is_pending(uni, email):
        # check if uni and email are correct and student is in pending status
        if not uni or not email:
            return False
        sql = "SELECT status FROM students_login_db.students WHERE uni=%s or email = %s"
        conn = StudentsResource._get_connection()
        cur = conn.cursor()
        res = cur.execute(sql, args=(uni, email))
        result = cur.fetchone()
        return True if result['status'] != 'Verified' else False

    @staticmethod
    def verify_student_inputs(uni, email, token):
        # check if uni and email and token are correct
        if not uni or not email or not token:
            return False
        sql = "SELECT * FROM students_login_db.students WHERE uni=%s or email = %s and status = %s"
        conn = StudentsResource._get_connection()
        cur = conn.cursor()
        res = cur.execute(sql, args=(uni, email, token))
        result = cur.rowcount
        return True if result == 1 else False

    @staticmethod
    def update_student_status(uni, email, token):
        if not uni or not email or not token:
            return False
        sql = "UPDATE students_login_db.students SET status = 'Verified' WHERE uni=%s and email=%s and status = %s"
        conn = StudentsResource._get_connection()
        cur = conn.cursor()
        res = cur.execute(sql, args=(uni, email, token))
        result = cur.rowcount
        return True if result == 1 else False
