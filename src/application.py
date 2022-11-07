import flask
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


@app.route("/students/signup", methods=['POST'])
def query_example():
    if request.is_json:
        try:
            request_data = request.get_json()
        except ValueError:
            return Response("[SIGNUP] UNABLE TO RETRIEVE REQUEST", status=400, content_type="text/plain")
    else:
        return Response("[SIGNUP] INVALID POST FORMAT: SHOULD BE JSON", status=400, content_type="text/plain")

    if not request_data:
        rsp = Response("[SIGNUP] INVALID INPUT FOR SIGNUP SHEET", status=404, content_type="text/plain")
        return rsp
    inputs = ['uni', 'email', 'password', 'last_name', 'first_name']
    for element in inputs:
        if element not in request_data:
            rsp = Response(f"[SIGNUP] MISSING INPUT {element.upper()}", status=404, content_type="text/plain")
            return rsp

    user = request_data['uni']
    email = request_data['email']
    password = request_data['password']
    last_name = request_data['last_name']
    first_name = request_data['first_name']
    middle_name = None
    if 'middle_name' in request_data:
        middle_name = request_data['middle_name']

    duplicated = get_student_by_input(user, email)
    if duplicated.status_code == 200:
        rsp = Response("[SIGNUP] DUPLICATED REGISTRATION", status=404,
                       content_type="text/plain")
    else:
        result = StudentsResource.insert_student(user, email, password, last_name, first_name, middle_name)
        if result:
            rsp = Response("[SIGNUP] STUDENT CREATED", status=200, content_type="text/plain")
        else:
            rsp = Response("[SIGNUP] SIGNUP FAILED", status=404, content_type="text/plain")
    return rsp


@app.route("/students/account", methods=["GET"])
def get_student_by_input(uni="", email=""):
    if "uni" in request.args:
        uni = request.args["uni"]
    if "email" in request.args:
        email = request.args["email"]
    result = StudentsResource.get_by_uni_email(uni, email)

    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")
    return rsp


@app.route("/students/verification", methods=["GET"])
def update_student_status(uni="", email="", token=""):
    if "uni" in request.args:
        uni = request.args['uni']
    if 'email' in request.args:
        email = request.args['email']
    if 'token' in request.args:
        token = request.args['token']

    is_pending = StudentsResource.student_is_pending(uni, email)
    if not is_pending:
        return Response("[ACCOUNT VERIFICATION] VERIFICATION FAILED: STUDENT IS NOT PENDING VERIFICATION", status=404,
                        content_type="text/plain")

    correct_inputs = StudentsResource.verify_student_inputs(uni, email, token)
    if not correct_inputs:
        return Response("[ACCOUNT VERIFICATION] VERIFICATION FAILED: WRONG TOKEN GIVEN", status=404,
                        content_type="text/plain")

    verified = StudentsResource.update_student_status(uni, email, token)
    if verified:
        rsp = Response("[ACCOUNT VERIFICATION] STUDENT VERIFIED", status=200, content_type="text/plain")
    else:
        rsp = Response("[ACCOUNT VERIFICATION] VERIFICATION FAILED", status=404, content_type="text/plain")
    return rsp


@app.route("/students/profile/<uni>/timezone=<timezone>&major=<major>&gender=<gender>&msg=<msg>",
           methods=["POST", "GET"])
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
