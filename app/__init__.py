import os
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
    app.config['SECRET_KEY'] = 'raztsook1996jeenproject'

    # ודא שתיקיית UPLOADS קיימת
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        print(f"Created uploads directory: {app.config['UPLOAD_FOLDER']}")

    # רישום ה-Blueprint
    from .routes import bp
    app.register_blueprint(bp)

    return app
