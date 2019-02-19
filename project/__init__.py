from flask import Flask


# Config
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('flask.cfg')

# Blueprints
from project.items.views import items_blueprint

# register the blueprints
app.register_blueprint(items_blueprint)
