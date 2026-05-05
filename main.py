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

@app.get("/")
def root():
    return {"environment": APP_ENV, "PORT": APP_PORT}

@app.get("/blog/{num}")
def get_blog(num: int):
    return {"blog_id": num}

class CreateBlog(BaseModel):
    title: str
    body: str
    published: Optional[bool] = True

@app.post("/blog")
def create_blog(request: CreateBlog):
    return {
        "message": "Blog created",
        "title": request.title,
        "environment": APP_ENV
    }

@app.get("/crash")
def crash():
    import os
    os._exit(1)  # Forcefully kills the python process

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=APP_PORT)