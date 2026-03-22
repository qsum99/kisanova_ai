import os
from flask import Flask

def create_app():
    """
    Creates and configures the Flask application.
    """
    # Calculate absolute path for template and static directories
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(base_dir, 'frontend', 'templates')
    static_dir = os.path.join(base_dir, 'frontend', 'static')
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    
    # Secret key for session management
    app.secret_key = os.environ.get('SECRET_KEY', 'farmer-ai-dev-secret-key-2026')
    
    # Load configuration
    from app import config
    app.config.from_mapping(
        OPENWEATHER_API_KEY=config.OPENWEATHER_API_KEY,
        CACHE_EXPIRATION_SECONDS=config.CACHE_EXPIRATION_SECONDS,
        MODEL_PATH=config.MODEL_PATH
    )
    
    # Initialize DB (creates sqlite DB and tables if they don't exist)
    from app.utils.database import init_db
    init_db()
    
    # Register blueprints safely inside context
    with app.app_context():
        from app.routes.crop_routes import crop_routes
        from app.routes.disease_routes import disease_routes
        from app.routes.price_routes import price_routes
        from app.routes.auth_routes import auth_routes
        from app.routes.robust_routes import robust_routes
        app.register_blueprint(crop_routes, url_prefix='/api')
        app.register_blueprint(disease_routes, url_prefix='/api')
        app.register_blueprint(price_routes, url_prefix='/api')
        app.register_blueprint(auth_routes, url_prefix='/api')
        app.register_blueprint(robust_routes, url_prefix='/api')
    
    # Simple health check endpoint
    @app.route('/health')
    def health_check():
        return {"status": "ok", "message": "Farmer AI API is running."}
        
    return app
