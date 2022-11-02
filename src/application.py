from flask import Flask, Response, request
from datetime import datetime
from students_resource import StudentsResource
import json
from flask_cors import CORS

# Create the Flask application object.
app = Flask(__name__)
CORS(app)


@app.get("/api/health")
def get_health():
    t = str(datetime.now())
    msg = {
        "name": "Students-login-Backend",
        "health": "Good",
        "at time": t
    }
    result = Response(json.dumps(msg), status=200, content_type="application/json")
    return result


@app.route(
    "/students/upload/uni=<uni>&email=<email>&password=<password>&last_name=<last_name>&first_name=<first_name>&middle_name=<middle_name>",
    methods=["POST", "GET"])
@app.route("/students/upload/uni=<uni>&email=<email>&password=<password>&last_name=<last_name>&first_name=<first_name>",
           methods=["POST", "GET"])
def insert_student(uni, email, password, last_name, first_name, middle_name=""):
    duplicated = get_student_by_input(uni, email)
    print(duplicated, duplicated.status_code, duplicated.data)
    if duplicated.status_code == 200:
        rsp = Response("DUPLICATED REGISTRATION", status=404,
                       content_type="text/plain")
    else:
        result = StudentsResource.insert_student(uni, email, password, last_name, first_name, middle_name)
        if result:
            rsp = Response("STUDENT CREATED", status=200, content_type="text/plain")
        else:
            rsp = Response("CREATION FAILED", status=404, content_type="text/plain")
    print(rsp, rsp.data)
    return rsp


@app.route("/students/uni=<uni>", methods=["GET"])
@app.route("/students/email=<email>", methods=["GET"])
@app.route("/students/uni=<uni>&email=<email>", methods=["GET"])
def get_student_by_input(uni="", email=""):
    result = StudentsResource.get_by_uni_email(uni, email)

    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")
    return rsp


@app.route("/students/verification/uni=<uni>&email=<email>&token=<token>", methods=["GET"])
def update_student_status(uni, email, token):
    is_pending = StudentsResource.student_is_pending(uni, email)
    if not is_pending:
        return Response("VERIFICATION FAILED: STUDENT IS NOT PENDING VERIFICATION", status=200,
                        content_type="text/plain")

    correct_inputs = StudentsResource.verify_student_inputs(uni, email, token)
    if not correct_inputs:
        return Response("VERIFICATION FAILED: WRONG TOKEN GIVEN", status=200,
                        content_type="text/plain")

    verified = StudentsResource.update_student_status(uni, email, token)
    if verified:
        rsp = Response("STUDENT VERIFIED", status=200, content_type="text/plain")
    else:
        rsp = Response("VERIFICATION FAILED", status=404, content_type="text/plain")
    return rsp


@app.route("/students/profile/<uni>/timezone=<timezone>&major=<major>&gender=<gender>&msg=<msg>", methods=["POST", "GET"])
@app.route("/students/profile/<uni>/timezone=<timezone>&major=<major>&gender=<gender>", methods=["POST", "GET"])
def update_profile(uni, timezone, major, gender, msg=""):
    result = StudentsResource.update_profile(uni, timezone, major, gender, msg)
    if result:
        rsp = Response("PROFILE UPDATED", status=200, content_type="text/plain")
    else:
        rsp = Response("NOT FOUND", status=400, content_type="text/plain")
    return rsp


@app.route("/students/profile/<uni>", methods=["GET"])
def get_profile_by_uni(uni):
    result = StudentsResource.get_profile(uni)
    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=400, content_type="text/plain")
    return rsp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2333)
