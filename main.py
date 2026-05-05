from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Now os.getenv will look into your .env file
APP_ENV = os.getenv("APP_ENV", "development")
APP_PORT = int(os.getenv("APP_PORT", 9000))

app = FastAPI()

# ... (rest of your routes stay the same)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=APP_PORT)