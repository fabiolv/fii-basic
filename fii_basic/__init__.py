from flask import Flask
from .fii_basic import fii_basic
from .fii_root import fii_root
from .fii_fnet_monthly import fii_fnet_monthly

def create_app():
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False

    # app.config.from_object(config_object)

    app.register_blueprint(fii_basic)
    app.register_blueprint(fii_root)
    app.register_blueprint(fii_fnet_monthly)

    return app