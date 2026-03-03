import os 
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY=os.getenv("OPENWEATHER_API_KEY")
if not OPENWEATHER_API_KEY :
   print("Error: OPENWEATHER_API_KEY could not be found in the .env file.")

MODEL_PATH="models/crop recommedation.pkl"