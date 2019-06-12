from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, redirect, url_for, request, jsonify, json, session
from flask_admin import Admin, AdminIndexView, BaseView, expose, helpers
from flask_admin.helpers  import is_form_submitted
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from kubernetes.client.apis import core_v1_api
from flask_sqlalchemy  import SQLAlchemy
from kubernetes  import client, config
from os import path
import subprocess
import argparse
import smtplib
import random
import yaml
import time
import os


app = Flask(__name__)
parser = argparse.ArgumentParser(description="FuchiCorp Api Application.")
parser.add_argument("--debug",  help="Run Application on developer mode.")

args = parser.parse_args()
def app_set_up():
    """

        If parse --debug argument to the application.
        Applicaion will run on debug mode and local mode.
        It's useful when you are developing application on localhost

        config-file: /Users/abdugofir/backup/databases/config.cfg

    """
    if args.debug == 'abdugofir':
        ## To testing I create my own config make sure you have configured ~/.kube/config
        app.config.from_pyfile('/Users/abdugofir/backup/databases/config.cfg')

    elif args.debug == 'fsadykov':
        ## To testing I create my own config make sure you have configured ~/.kube/config
        app.config.from_pyfile('/Users/fsadykov/backup/databases/config.cfg')

    else:

        ## To different enviroments enable this
        app.config.from_pyfile('config.cfg')
        os.system('sh bash/bin/getServiceAccountConfig.sh')

# app.config.from_pyfile('/Users/abdugofir/backup/databases/config.cfg')
app_set_up()
db = SQLAlchemy(app)

env = app.config.get('BRANCH_NAME')
if env == 'master':
    enviroment = 'prod'
else:
    enviroment = env

## Loading the Kubernetes configuration
config.load_kube_config()
kube = client.ExtensionsV1beta1Api()
api = core_v1_api.CoreV1Api()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50))
    message = db.Column(db.String(500))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(15))
    lastname = db.Column(db.String(15))
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    status = db.Column(db.String(5))
    role = db.Column(db.String(20))
    def __repr__(self):
        return '<User %r>' % self.username

class Pynote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_name = db.Column(db.String(50))
    username = db.Column(db.String(50))
    password = db.Column(db.String(50))
    pynotelink = db.Column(db.String(50), unique=True)
    port = db.Column(db.Integer, unique=True)
    def __repr__(self):
        return '<User %r>' % self.username



### Api Block starts from here ####


@app.route('/api/users', methods=['GET'])
def api_users():
    with open('api/examples/example.json') as file:
        data = json.load(file)
    return jsonify(data)


if __name__ == '__main__':
    db.create_all()
    app.run(port=5000, host='0.0.0.0')
