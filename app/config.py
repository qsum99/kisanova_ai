import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base config."""
    # Never hardcode the API key. It should be in a .env file.
    OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY')
    if not OPENWEATHER_API_KEY:
        print("WARNING: OPENWEATHER_API_KEY is not set in environment or .env file.")
    
    # Cache expiration time in seconds (30 minutes = 1800 seconds)
    CACHE_EXPIRATION_SECONDS = 1800
    
    # Path to the trained RandomForest model
    # Adjust this path based on where the app is being run from
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'crop recommedation.pkl')
