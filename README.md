![](https://i.imgur.com/wTxzpbn.png)

# prime-renameAP
### What does it do?
##### Introduction
Search and rename multiple accesspoints in Cisco Prime Infrastructure (tested with PI 3.4.1).  
Upon execution the script will loop each row and search Cisco Prime for the mac-adress provided. In this case, accesspoint with mac-adress 00:00:00:00:00:01 will be renamed Main_AP01.

##### LDAP
Yep, LDAP is integrated. To be able to login, the ldap user must be member of the group specified in `project/item/views.py`. The LDAP connection settings can be found in `instance/flask.cfg`.

####

### Why?
Most Cisco Prime Infrastructures are set up to automatically detect new accesspoints being plugged into the network. When Prime detects a new accesspoint being plugged in, it receives a name in the webgui (AP000000000001) for later placement in the building/floor planning view.

This script will change the AP name so it's easier to find and monitor... obviously.

## Installation
```
git clone git@github.com:dunderrrrrr/prime-renameap.git
mkvirtualenv --python=/usr/bin/python3 prime-renameAP
pip install -r requirements.txt
mkdir instance
nano instance/flask.cfg
```
Place this in instance/flask.cfg. Make sure to get all settings right.
```
import os

# grab the folder of the top-level directory of this project
BASEDIR = os.path.abspath(os.path.dirname(__file__))
TOP_LEVEL_DIR = os.path.abspath(os.curdir)

# Update later by using a random number generator and moving
SECRET_KEY = 'secret_key'
WTF_CSRF_ENABLED = True
DEBUG = True

LDAP_HOST = 'ldap.host'
LDAP_BASE_DN = 'OU=Main OU,DC=main,DC=x'
LDAP_USER_DN = ''
LDAP_GROUP_DN = ''
LDAP_USER_RDN_ATTR = 'cn'
LDAP_USER_LOGIN_ATTR = 'sAMAccountName'
LDAP_BIND_USER_DN = 'CN=adaccountusername,OU=Users,OU=Accounts,OU=Others,OU=Main OU,DC=main'
LDAP_BIND_USER_PASSWORD = ''
LDAP_USER_SEARCH_SCOPE = 'SUBTREE'
```
Change prime settings in
```
project/item/views.py
```
Start FLASK and grab a coffee.
```
export FLASK_APP=run.py
export FLASK_DEBUG=True
flask run
```
