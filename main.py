import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from prometheus_client import Counter, Histogram, make_asgi_app

# --------------------
# Configuration
# --------------------
APP_ENV = os.getenv("APP_ENV", "development")

# --------------------
# Metrics (ADD HERE)
# --------------------
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint"]
)

REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "Request latency",
    ["endpoint"]
)

# --------------------
# FastAPI App
# --------------------
app = FastAPI()

# --------------------
# Routes
# --------------------
@app.get("/")
def root():
    REQUEST_COUNT.labels(method="GET", endpoint="/").inc()
    return {"environment": APP_ENV}

@app.get("/blog/{num}")
def get_blog(num: int):
    REQUEST_COUNT.labels(method="GET", endpoint="/blog").inc()
    return {"blog_id": num}

class CreateBlog(BaseModel):
    title: str
    body: str
    published: Optional[bool] = True

@app.post("/blog")
def create_blog(request: CreateBlog):
    REQUEST_COUNT.labels(method="POST", endpoint="/blog").inc()
    return {
        "message": "Blog created",
        "title": request.title,
        "environment": APP_ENV
    }

# --------------------
# Metrics Endpoint
# --------------------
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# --------------------
# App Runner
# --------------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9000)
