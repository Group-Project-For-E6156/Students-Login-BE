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

@app.route("/students_upload/uni=<uni>&email=<email>&password=<password>&last_name=<last_name>&first_name=<first_name>&middle_name=<middle_name>",
           methods=["POST", "GET"])
def insert_student(uni, email, password, last_name, first_name, middle_name):
    result = StudentsResource.insert_student(uni, email, password, last_name, first_name, middle_name)
    if result:
        rsp = Response("STUDENT CREATED", status=200, content_type="text/plain")
    else:
        rsp = Response("CREATION FAILED", status=404, content_type="text/plain")

    return rsp

@app.route("/students/uni=<uni>", methods=["GET"])
@app.route("/students/email=<email>", methods=["GET"])
@app.route("/students/uni=<uni>&email=<email>", methods=["GET"])
@app.route("/students/email=<email>&uni=<uni>", methods=["GET"])
def get_student_by_uni(uni="", email=""):
    result = StudentsResource.get_by_uni_email(uni, email)

    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")
    return rsp

@app.route("/students_verification/uni=<uni>&email=<email>&token=<token>", methods=["GET"])
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2333)
