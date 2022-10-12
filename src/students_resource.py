import pymysql
import os


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
