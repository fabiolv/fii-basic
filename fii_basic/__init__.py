from flask import Flask
from .fii_basic import fii_basic
from .fii_root import fii_root

def create_app():
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False

    # app.config.from_object(config_object)

    app.register_blueprint(fii_basic)
    app.register_blueprint(fii_root)

    return app