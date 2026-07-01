import os, uuid, json as json_lib
from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
load_dotenv()

login_manager = LoginManager()
login_manager.login_view = 'main.login'

@login_manager.user_loader
def load_user(user_id):
    from models import User; return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'turf-pro-secret-key-2026')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///turf_forum.db'

    from models import db, seed_data
    db.init_app(app)
    login_manager.init_app(app)

    from routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()
        try:
            seed_data()
        except Exception as e:
            print(f"Seed warning: {e}")

    return app

# 部署用：Gunicorn 加载此模块后自动调用 create_app()
