#!/usr/bin/env python
import json
import os
from os import listdir
from os.path import isfile, join
from unicodedata import name

import flask_login
import requests
from flask import (
    Flask,
    Response,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import LoginManager, UserMixin, login_user
from oauthlib.oauth2 import WebApplicationClient

# configuration

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
REDIRECT_URI = os.environ.get("REDIRECT_URI", None)
LOGIN_URI = os.environ.get("LOGIN_URI", None)
GOOGLE_DISCOVERY_URL = os.environ.get("GOOGLE_DISCOVERY_URL", None)

VIDEO_FOLDER = "videos/"

# add classes
class User(UserMixin):
    def __init__(self, id, name, email):
        self.name = name
        self.id = id
        self.email = email
        self.oath_passed = False

        def is_active(self):
            return True

        def is_anonymous(self):
            return False

        def is_authenticated(self):
            return self.oath_passed


users = {}

# flask config
client = WebApplicationClient(GOOGLE_CLIENT_ID)
login_manager = LoginManager()
app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
login_manager.init_app(app)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@login_manager.unauthorized_handler
def unauthorized():
    return '<a class="button" href="{}">Google Login</a>'.format(LOGIN_URI)
    # return "You must be logged in to access this content.", 403


@login_manager.user_loader
def load_user(user_id):
    if user_id not in users:
        return

    user = User(id=user_id, name="", email="")
    return user


@app.route("/login")
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=REDIRECT_URI,
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    code = request.args.get("code")
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=REDIRECT_URI,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    user = User(id=unique_id, name=users_name, email=users_email)
    user.oath_passed = True

    flask_login.login_user(user)

    return "Logged"


def update_files():
    filenames = [f for f in listdir(VIDEO_FOLDER) if isfile(join(VIDEO_FOLDER, f))]
    return filenames


@app.route("/videos/<path:path>")
@flask_login.login_required
def send_video(path):
    return send_from_directory("videos", path)


@app.route("/<id>/<timestamp>")
@flask_login.login_required
def show_video(id, timestamp):
    filenames = update_files()
    filenames = [name.split(".mp4")[0] for name in filenames]
    video_name = str(id)
    timestamp = (int(float(timestamp)) * 60) + int(str(float(timestamp)).split(".")[1])
    print(filenames)
    if video_name not in filenames:
        return Response("Not Found")

    output_file = video_name + ".mp4"
    anon_video = video_name + "_anomaly.mp4"
    obj_video = video_name + "_objects.mp4"

    return render_template(
        "video_player.html",
        raw_video=output_file,
        anon_video=anon_video,
        obj_video=obj_video,
        timestamp=timestamp,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
