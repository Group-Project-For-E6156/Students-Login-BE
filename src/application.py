from flask import Flask, Response, request, jsonify
from datetime import datetime, timedelta
from students_resource import StudentsResource
import json
from flask_cors import CORS
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Create the Flask application object.
app = Flask(__name__)
# NEVER HARDCODE YOUR CONFIGURATION IN YOUR CODE
# TODO: INSTEAD CREATE A .env FILE AND STORE IN IT
app.config['SECRET_KEY'] = 'longer-secret-is-better'
CORS(app)


# decorator for verifying the JWT
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header!!
        if 'access-token' in request.headers:
            token = request.headers['access-token']
        if not token:
            return Response("TOKEN IS MISSING", status=401, content_type="text/plain")

        try:
            # decoding the payload to fetch the stored details
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            current_user = StudentsResource.get_by_uni_email(data['uni'])
        except:
            return Response("TOKEN IS INVALID", status=401, content_type="text/plain")
        # returns the current logged-in users contex to the routes
        return f(current_user, *args, **kwargs)

    return decorated


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
def signup():
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

    uni = request_data['uni']
    email = request_data['email']
    password = request_data['password']
    last_name = request_data['last_name']
    first_name = request_data['first_name']
    middle_name = None
    if 'middle_name' in request_data:
        middle_name = request_data['middle_name']

    user = StudentsResource.get_by_uni_email(uni, email)
    if user:
        rsp = Response("[SIGNUP] USER ALREADY EXISTS, PLEASE LOG IN", status=404, content_type="text/plain")
    else:
        password = generate_password_hash(password)
        result = StudentsResource.insert_student(uni, email, password, last_name, first_name, middle_name)
        if result:
            rsp = Response("[SIGNUP] STUDENT CREATED", status=200, content_type="text/plain")
        else:
            rsp = Response("[SIGNUP] SIGNUP FAILED", status=404, content_type="text/plain")
    return rsp


@app.route("/students/login", methods=['POST'])
def login():
    request_data = request.get_json()
    if 'uni' not in request_data or 'password' not in request_data:
        return Response("[LOGIN] LOGIN FAILED: MISSING UNI OR PASSWORD", status=400, content_type="text/plain")
    uni = request_data['uni']
    password = request_data['password']
    # if not auth or not auth.get('uni') or not auth.get('password'):

    user = StudentsResource.get_by_uni_email(uni)
    if not user:
        return Response("[LOGIN] LOGIN FAILED: USER DOES NOT EXIST", status=404, content_type="text/plain")

    if check_password_hash(user.get('password'), password):
        # verify uni and pwd, if valid, generate jwt token
        exp = datetime.utcnow() + timedelta(minutes=30)
        token = jwt.encode({
            'uni': user.get('uni'),
            'exp': exp
        }, app.config['SECRET_KEY'],
            algorithm="HS256")
        return Response(json.dumps({'token': token, 'uni': uni}), status=200, content_type="application.json")
    else:
        return Response("[LOGIN] LOGIN FAILED: WRONG PASSWORD", status=401, content_type="text/plain")


@app.route("/students/account", methods=["GET"])
@token_required
def get_student_by_input(current_user, uni="", email=""):
    print("current user is: " + str(current_user))
    print(uni)
    if "uni" in request.args:
        uni = request.args["uni"]
    if "email" in request.args:
        email = request.args["email"]
    result = StudentsResource.get_by_uni_email(uni, email)

    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=401, content_type="text/plain")
    return rsp


# TODO: do we need verification???
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


@app.route("/students/profile", methods=["POST"])
@token_required
def update_profile(current_user):
    uni = current_user['uni']
    if request.is_json:
        try:
            request_data = request.get_json()
        except ValueError:
            return Response("[UPDATE PROFILE] UNABLE TO RETRIEVE REQUEST", status=400, content_type="text/plain")
    else:
        return Response("[UPDATE PROFILE] INVALID POST FORMAT: SHOULD BE JSON", status=400, content_type="text/plain")

    if not request_data:
        return Response("[UPDATE PROFILE] INVALID INPUT", status=404, content_type="text/plain")
    inputs = ['timezone', 'major', 'gender', 'message']
    for element in inputs:
        if element not in request_data:
            return Response(f"[UPDATE PROFILE] MISSING INPUT {element.upper()}", status=400, content_type="text/plain")

    user = StudentsResource.get_by_uni_email(uni)

    if user:
        message = request_data['message'] if 'message' in request_data else ""
        result = StudentsResource.update_profile(uni, request_data['timezone'], request_data['major'],
                                                 request_data['gender'], message)
        if result:
            rsp = Response("[UPDATE PROFILE] PROFILE UPDATED", status=200, content_type="text/plain")
        else:
            rsp = Response("[UPDATE PROFILE] PROFILE UPDATE FAILED", status=404, content_type="text/plain")
    else:
        rsp = Response("[UPDATE PROFILE] USER DOES NOT EXISTS", status=404, content_type="text/plain")

    return rsp


@app.route("/students/profile", methods=["GET"])
@token_required
def get_profile_by_uni(current_user):
    uni = current_user['uni']
    result = StudentsResource.get_profile(uni)
    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")
    return rsp


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2333)
