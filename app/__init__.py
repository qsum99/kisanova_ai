import os
from flask import Flask

def create_app():
    """
    Creates and configures the Flask application.
    """
    # Calculate absolute path for template directory (assuming frontend/templates is in the project root)
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    template_dir = os.path.join(base_dir, 'frontend', 'templates')
    
    app = Flask(__name__, template_folder=template_dir)
    
    # Load configuration
    from app import config
    app.config.from_mapping(
        OPENWEATHER_API_KEY=config.OPENWEATHER_API_KEY,
        CACHE_EXPIRATION_SECONDS=config.CACHE_EXPIRATION_SECONDS,
        MODEL_PATH=config.MODEL_PATH
    )
    
    # Register blueprints safely inside context
    with app.app_context():
        from app.routes.crop_routes import crop_routes
        app.register_blueprint(crop_routes, url_prefix='/api')
    
    # Simple health check endpoint
    @app.route('/health')
    def health_check():
        return {"status": "ok", "message": "Crop Recommendation API is running."}
        
    return app
