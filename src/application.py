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


@app.route("/api/students/<uni>/<email>", methods=["GET"])
def get_student_by_uni(uni, email):

    result = StudentsResource.get_by_uni_email(uni, email)


    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    return rsp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2333)