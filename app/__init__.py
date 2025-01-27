import os
from flask import Flask
from .routes import bp

def create_app(*args, **kwargs):
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
    app.config['SECRET_KEY'] = 'raztsook1996jeenproject'

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        print(f"Created uploads directory: {app.config['UPLOAD_FOLDER']}")

    from .routes import bp
    app.register_blueprint(bp)

    return app

