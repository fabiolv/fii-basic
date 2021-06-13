from flask import Flask
from .fii_basic import fii_basic

def create_app():
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False

    # app.config.from_object(config_object)

    app.register_blueprint(fii_basic)

    return app