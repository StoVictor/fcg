import os

from flask import Flask
from flask_socketio import SocketIO


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'field_capture.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    from . import main
    app.register_blueprint(main.bp)
    
    from . import room
    app.register_blueprint(room.room_bp)

    from .errors import page_not_found
    app.register_error_handler(404, page_not_found)
    from .errors import my_custom_error
    return app



app = create_app()
socketio = SocketIO(app)
