from project import app
import requests, json, urllib3, time
from flask import Flask, render_template, session, Blueprint, request, redirect, url_for, flash, jsonify, render_template_string
from flask_ldap3_login import LDAP3LoginManager
from flask_login import LoginManager, login_user, UserMixin, current_user, logout_user
from flask_ldap3_login.forms import LDAPLoginForm
from .forms import MainForm

urllib3.disable_warnings()

prime_server = 'http://prime.domain.com' #prime fqdn
prime_user = 'username' #prime username
prime_passwd = 'password' #prime password
allowed_adgroup = 'CN=prime-admins,OU=Network,OU=Groups,OU=Groups,OU=Main OU,DC=main' # ldap user must be in ad group for login access
login_manager = LoginManager(app)              # Setup a Flask-Login Manager
ldap_manager = LDAP3LoginManager(app)          # Setup a LDAP3 Login Manager.

# config
items_blueprint = Blueprint('items', __name__, template_folder='templates')

# Create a dictionary to store the users in when they authenticate
# This example stores users in memory.
users = {}

# flask login
class User(UserMixin):
    def __init__(self, dn, username, data):
        self.dn = dn
        self.username = username
        self.data = data

    def __repr__(self):
        return self.dn

    def get_id(self):
        return self.dn

@login_manager.user_loader
def load_user(id):
    if id in users:
        return users[id]
    return None

@ldap_manager.save_user
def save_user(dn, username, data, memberships):
    user = User(dn, username, data)
    users[dn] = user
    return user

# defs
def ap_search(apName, apMac):
    uri = prime_server + '/webacs/api/v1/data/AccessPoints.json?ethernetMac="{}"'.format(apMac)
    r = requests.get(uri, headers={'Connection':'close'}, auth=(prime_user, prime_passwd), timeout=100, verify=False)
    time.sleep(0.5)
    return(r.json())

def ap_update(data):
    uri = prime_server + "/webacs/api/v1/op/apService/accessPoint.json"
    for d in data:
        count = int(d['apDetails']['queryResponse']['@count'])
        if count == 1:
            for a in d['apDetails']['queryResponse']['entityId']:
                apId = a['$']
            payload = {
                        "accessPoint" : {
                            "adminStatus": 1,
                            "accessPointId" : apId,
                            "name" : d['apName']
                          }
                      }
            r = requests.put(uri, data=json.dumps(payload), headers={'Content-Type': 'application/json'}, auth=(prime_user, prime_passwd), timeout=100, verify=False)
            d['status'] = r.status_code
        else:
            d['status'] = 404
    return(data)

def formatdata(data):
    aps = []
    data = data.replace(" ", "")
    for d in data.splitlines():
        if len(d) >= 1: #skip blank input lines
            ap = {}
            apName = d.split(',')[0]
            apMac = d.split(',')[1]
            ap['apName'] = apName
            ap['apMac'] = apMac
            ap['apDetails'] = ap_search(apName, apMac)
            aps.append(ap)
    return(aps)

# routes
@items_blueprint.route('/', methods=['GET', 'POST'])
def index():
    # Redirect users who are not logged in.
    if not current_user or current_user.is_anonymous:
        return redirect(url_for('login'))

    # Logout users if not member of allowed_adgroup (best practice?)
    if not allowed_adgroup in current_user.data['memberof']:
        return redirect(url_for('items.logout'))

    updateAp = None
    form = MainForm(request.form)
    if request.method == 'POST' and len(form.inputArea.data) >= 1:
        data = form.inputArea.data
        inputdata = formatdata(data)
        updateAp = ap_update(inputdata)
    return render_template('items.html', form=form, updateAp=updateAp)

@items_blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
       logout_user()
       return redirect(url_for('items.index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LDAPLoginForm()
    if form.validate_on_submit():
        login_user(form.user)  # Tell flask-login to log them in.
        return redirect(url_for('items.index'))  # Send them home
    return render_template('login.html', form=form)
