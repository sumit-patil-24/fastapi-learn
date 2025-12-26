from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os


APP_ENV = os.getenv("APP_ENV", "development")

app = FastAPI()

@app.get("/")
def root():
    return {"environment": APP_ENV}

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

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
