from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
import os

from flask_cors import CORS
#from flask_wtf import FlaskForm
#from wtforms import SubmitField

CSRF = "anijr35607yhohs535"


#class DeletePostForm(FlaskForm):
#    submit = SubmitField("Delete")


app = Flask(__name__)
CORS(app)
cors = CORS(app, resource={r"/*": {"origins": "*"}})
# Get the absolute path to the database file
db_path = os.path.join(os.getcwd(), "data", "sqlite.db")

# Configure Flask app
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////data/sqlite.db"
app.config["SECRET_KEY"] = "secret-key"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30))
    role = db.Column(db.String(30))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and check_password_hash(user.password, request.form["password"]):
            login_user(user)
            return redirect(url_for("index"))
        flash("Invalid username or password")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.before_request
def check_user_logged_in():
    if not current_user.is_authenticated and request.endpoint != "login":
        return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    posts = Post.query.all()
    return render_template("index.html", posts=posts)


@app.route("/post", methods=["GET", "POST"])
@login_required
def post():
    if request.method == "POST":
        new_post = Post(content=request.form["content"], user_id=current_user.id)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("post.html")


@app.route("/edit/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit(post_id):
    post = Post.query.get(post_id)
    if current_user.role != "admin" and current_user.id != post.user_id:
        flash("You do not have permission to edit this post")
        return redirect(url_for("index"))
    if request.method == "POST":
        post.content = request.form["content"]
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("edit.html", post=post)


@app.route("/delete/<int:post_id>/<string:csrf_token>")
@login_required
def delete(post_id, csrf_token):
    if csrf_token == CSRF:
        post = Post.query.get(post_id)
        if current_user.role != "admin" and current_user.id != post.user_id:
            flash("You do not have permission to delete this post")
            return redirect(url_for("index"))
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for("index"))


# @app.route("/delete/<int:post_id>")
# @login_required
# def delete(post_id):
#     post = Post.query.get(post_id)
#     if current_user.role != "admin" and current_user.id != post.user_id:
#         flash("You do not have permission to delete this post")
#         return redirect(url_for("index"))
#     db.session.delete(post)
#     db.session.commit()
#     return redirect(url_for("index"))


def add_initial_data():
    user = User(
        username="admin", password=generate_password_hash("admin"), role="admin"
    )
    db.session.add(user)
    db.session.commit()


if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()
    #     if not User.query.filter_by(username="admin").first():
    #         add_initial_data()
    app.run(host="0.0.0.0", debug=True)
