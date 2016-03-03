# coding: utf-8
from flask import redirect, url_for, flash, request, render_template, session
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from settings import *
from db_connect import Base, Column, Integer, String

login_manager = LoginManager()
login_manager.init_app(app)
# app.secret_key = 'super secret key'


class User(Base, UserMixin):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(String)

    def __repr__(self):
        return "<User(id={}, email={}')>".format(self.id, self.email)

    @classmethod
    def get(cls, id):
        return db.query(User).filter(User.id == id).one_or_none()

    @classmethod
    def load(cls, email, password):
        return db.query(User).filter(User.email == email, User.password == password).one_or_none()


@login_manager.user_loader
def load_user(userid):
    u = User.get(userid)
    if u:
        return u
    return None


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember_me = request.form.get("remember")
        user_indb = User.load(email, password)

        if user_indb is not None:
            login_user(user_indb, remember=remember_me)
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
