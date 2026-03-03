import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
if not OPENWEATHER_API_KEY:
    print("Error: OPENWEATHER_API_KEY is not set in environment or .env file.")

CACHE_EXPIRATION_SECONDS = 1800

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'crop recommedation.pkl')