from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'uma-chave-secreta-forte'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    @app.template_filter('currency')
    def format_currency(value):
        return f'R$ {value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

    with app.app_context():
        from . import routes
        app.register_blueprint(routes.main)
        
        from . import models
        db.create_all()

    return app