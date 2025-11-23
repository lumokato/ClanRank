from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import logging

scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Register Blueprints
    from .routes.main import main_bp
    from .routes.arena import arena_bp
    from .routes.farm import farm_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(arena_bp)
    app.register_blueprint(farm_bp)
    
    # Configure Jinja2
    app.jinja_env.block_start_string = '(%'
    app.jinja_env.block_end_string = '%)'
    app.jinja_env.variable_start_string = '(('
    app.jinja_env.variable_end_string = '))'
    app.jinja_env.comment_start_string = '(#'
    app.jinja_env.comment_end_string = '#)'
    
    return app
