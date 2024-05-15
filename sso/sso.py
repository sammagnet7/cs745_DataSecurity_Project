import os
import pathlib

import requests
from flask import (
    Flask,
    session,
    abort,
    redirect,
    request,
    render_template,
    url_for,
    flash,
)
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

app = Flask("Google Login App")
app.secret_key = "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"  # make sure this matches with that's in client_secret.json
CSRF = "anijr35607yhohs535"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # to allow Http traffic for local dev
CORS(app)
cors = CORS(app, resource={r"/*": {"origins": "*"}})
# Get the absolute path to the database file
db_path = os.path.join(os.getcwd(), "data", "sqlite.db")

# Configure Flask app
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////data/sqlite.db"
app.config["SECRET_KEY"] = "secret-key"
db = SQLAlchemy(app)
GOOGLE_CLIENT_ID = (
    "353277935247-geh4ha6o0uf823vpub47nf8plib9lmck.apps.googleusercontent.com"
)
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ],
    redirect_uri="http://fakedomain.com:5000/callback",
)


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    print(authorization_url)
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    print(session)
    print(request)
    # if not session["state"] == request.args["state"]:
    #    abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token, request=token_request, audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/protected_area")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/")
def index():
    return "<a href='/login'><button>Login</button></a>"


@app.route("/protected_area")
@login_is_required
def protected_area():
    return render_template("index.html", name=session["name"], posts=[])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
