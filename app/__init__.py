import os
from flask import Flask
from app.extensions import db, migrate, login_manager, bcrypt
from app.models.user import User

def create_app(config_name='development'):
    """Application Factory do Flask"""
    app = Flask(__name__)
    
    # Carregar configuração baseado na string
    from app.config import config
    app.config.from_object(config[config_name])
    
    # Inicializar extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    # Configuração do LoginManager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Registrar Blueprints (Controllers)
    from app.controllers.main_controller import bp as main_bp
    from app.controllers.user_controller import bp as user_bp
    from app.controllers.auth_controller import bp as auth_bp
    from app.controllers.work_order_controller import bp as work_order_bp
    from app.controllers.report_controller import bp as report_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(work_order_bp)
    app.register_blueprint(report_bp)
    
    # Inicializar comandos CLI
    from app import cli
    cli.init_app(app)
    
    return app
