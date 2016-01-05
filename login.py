# coding: utf-8
from flask import redirect, url_for, flash, request, render_template, session
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from settings import *

login_manager = LoginManager()
login_manager.init_app(app)
# app.secret_key = 'super secret key'


class User(UserMixin):

    def __init__(self, _id, email, password):
        self.id = _id
        self.email = email
        self.password = password

    @classmethod
    def load(cls, email, password):
        return db.users.find_one({'email': email, 'password': password})

    @classmethod
    def get(cls, _id):
        return db.users.find_one(ObjectId(_id))


@login_manager.user_loader
def load_user(userid):
    u = User.get(userid)
    if u is not None:
        user = User(**u)
        return user


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember_me = request.form.get("remember")
        user_indb = User.load(email, password)

        if user_indb is not None:
            user = User(**user_indb)
            login_user(user, remember=remember_me)
            return redirect(url_for("index"))
        else:
            flash(u'Такого пользователя нет!')
    return render_template('login.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("login"))
