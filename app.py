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
parser = argparse.ArgumentParser(description="FuchiCorp Webplarform Application.")
parser.add_argument("--debug", action='store_true',
                        help="Run Application on developer mode.")

args = parser.parse_args()
def app_set_up():
    """

        If parse --debug argument to the application.
        Applicaion will run on debug mode and local mode.
        It's useful when you are developing application on localhost

        config-file: /Users/fsadykov/backup/databases/config.cfg

    """
    if args.debug:

        ## To testing I create my own config make sure you have configured ~/.kube/config
        app.config.from_pyfile('/Users/fsadykov/backup/databases/config.cfg')

    else:

        ## To different enviroments enable this
        app.config.from_pyfile('config.cfg')
        os.system('sh bash/bin/getServiceAccountConfig.sh')

# app.config.from_pyfile('/Users/fsadykov/backup/databases/config.cfg')
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


class pynoteDeleteView(BaseView):
    @expose('/', methods=('GET', 'POST'))
    def index(self):
        form = PyNoteDelete()
        if is_form_submitted():
            pynote = Pynote.query.filter_by(username=form.username.data, server_name=form.pynote.data).first()
            if pynote:
                try:
                    delete_pynote(form.username.data)
                    message = f'PyNote for {pynote.username} has been deleted.'
                except:
                    message = f'Deleting was not success for user {pynote.username}'
                return self.render('admin/delete_pynote.html', message=message, form=form)
            else:
                message = f'PyNote for {form.username.data} not found.'
                return self.render('admin/delete_pynote.html', message=message, form=form)
        return self.render('admin/delete_pynote.html', form=form)

class MyModelView(ModelView):
    def is_accessible(self):
        if current_user.role == "Admin":
            return True
        else:
            return False
    def inaccessible_callback(self, name, **kwargs):
        return "<h2>Sorry you do not have permission for this page <h2>"

class MyAdminIndex(AdminIndexView):
    def is_accessible(self):
        if current_user.role == "Admin":
            return True
        else:
            return False
    def inaccessible_callback(self, name, **kwargs):
        return "<h2 style='color: red;'>Sorry you do not have permission for this page<h2>"



def generate_templates(username, password, enviroment):
    templates = {}
    template_port = available_port()
    if env == 'master':
        host = 'academy.fuchicorp.com'
    else:
        host = f'{enviroment}.academy.fuchicorp.com'
    ingress_name  = f'{enviroment}-pynote-ingress'
    namespace     = f'{enviroment}-students'
    templates['pynotelink'] = f'/pynote/{username}'
    templates['path'] = {'path': f'/pynote/{username}', 'backend': {'serviceName': username, 'servicePort': template_port}}
    templates['port'] = template_port
    with open('kubernetes/pynote-pod.yaml' ) as file:
        pod = yaml.load(file, Loader=yaml.FullLoader)
        pod['metadata']['name']              = username
        pod['metadata']['labels']['run']     = username
        pod['spec']['containers'][0]['name'] = username
        pod['spec']['containers'][0]['args'] = [ f"--username={username}", f"--password={password}"]
        templates['pod'] = pod

    with open('kubernetes/pynote-service.yaml') as file:
        service = yaml.load(file, Loader=yaml.FullLoader)
        service['metadata']['labels']['run'] = username
        service['spec']['ports'][0]['port']  = template_port
        service['spec']['selector']['run']   = username
        service['metadata']['name']          = username
        templates['service']                 = service

    with open('kubernetes/pynote-ingress.yaml') as file:
        ingress = yaml.load(file, Loader=yaml.FullLoader)
        ingress['spec']['rules'][0]['host']  = host
        ingress['spec']['rules'][0]['http']['paths'].append(templates['path'])
        ingress['metadata']['name']          = ingress_name
        ingress['metadata']['namespace']     = namespace
        templates['ingress']                 = ingress
    return templates

def existing_ingess(ingerssname, namespace):
    total = []
    ingressList = kube.list_namespaced_ingress(namespace).items
    for item in ingressList:
        if item.metadata.name == ingerssname:
            return item
    else:
        return False

def create_pynote(username, password):
    ## Loading the kubernetes objects
    config.load_kube_config()
    kube           = client.ExtensionsV1beta1Api()
    api            = core_v1_api.CoreV1Api()
    pynote_name    = username.lower()
    pynote_pass    = password
    ingress_name   = f'{enviroment}-pynote-ingress'
    namespace      = f'{enviroment}-students'
    deployment     = generate_templates(pynote_name, pynote_pass, enviroment)
    pod            = api.create_namespaced_pod(body=deployment['pod'], namespace=namespace)
    service        = api.create_namespaced_service(body=deployment['service'], namespace=namespace)
    exist_ingress  = existing_ingess(ingress_name, namespace)
    if exist_ingress:
        exist_ingress.spec.rules[0].http.paths.append(deployment['path'])
        kube.replace_namespaced_ingress(exist_ingress.metadata.name, namespace, body=exist_ingress)
    else:
        kube.create_namespaced_ingress(namespace, body=deployment['ingress'])
    return deployment

def delete_pynote(username):
    ## Loading the kubernetes objects
    config.load_kube_config()
    kube          = client.ExtensionsV1beta1Api()
    api           = core_v1_api.CoreV1Api()
    pynote_name    = username.lower()
    ingress_name   = f'{enviroment}-pynote-ingress'
    namespace     = f'{enviroment}-students'
    # needs to add deletion for pod and service
    exist_ingress  = existing_ingess(ingress_name, namespace)
    try:
        api.delete_namespaced_pod(pynote_name, namespace)
        print(f'Deleted a pod {pynote_name}')
        api.delete_namespaced_service(pynote_name, namespace)
        print(f'Deleted a service {pynote_name}')
    except:
        print('Trying to delete service and pod was not success')
    if exist_ingress:
        if 1 < len(exist_ingress.spec.rules[0].http.paths):
            for i in exist_ingress.spec.rules[0].http.paths:
                if username in i.path:
                    exist_ingress.spec.rules[0].http.paths.remove(i)
            exist_ingress.metadata.resource_version = ''
            kube.patch_namespaced_ingress(exist_ingress.metadata.name, namespace, body=exist_ingress)
        else:
            kube.delete_namespaced_ingress(ingress_name, namespace)
    pynote_to_delete = Pynote.query.filter_by(username=username).first()
    db.session.delete(pynote_to_delete)
    db.session.commit()

### Api Block starts from here ####

@app.route('/api/example-users', methods=['GET', 'POST'])
@login_required
def example():
    with open('api/examples/example.json') as file:
        data = json.load(file)
    return jsonify(data)

@app.route('/api/users', methods=['GET'])
def api_users():
    with open('api/examples/example.json') as file:
        data = json.load(file)
    return jsonify(data)


### Api Block ends from here ####
admin = Admin(app, index_view=MyAdminIndex())
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Pynote, db.session))
admin.add_view(MyModelView(Message, db.session))
admin.add_view(pynoteDeleteView(name='Delete Pynote', endpoint='pynote-delete'))

if __name__ == '__main__':
    db.create_all()
    app.run(port=5000, host='0.0.0.0')
