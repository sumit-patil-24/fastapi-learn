import os
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from prometheus_client import Counter, Histogram, make_asgi_app
import time

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
    start_time=time.time()      # start time

    REQUEST_COUNT.labels(method="GET", endpoint="/").inc()

    response= {"environment": APP_ENV}

    duration = time.time() - start_time # stop time

    REQUEST_LATENCY.labels(
        endpoint="/"
    ).observe(duration)

    return response

@app.get("/blog/{num}")
def get_blog(num: int):
    start_time=time.time()      # start time

    REQUEST_COUNT.labels(method="GET", endpoint="/blog").inc()
    response= {"blog_id": num}

    duration = time.time() - start_time # stop time

    REQUEST_LATENCY.labels(
        endpoint="/blog"
    ).observe(duration)

    return response


class CreateBlog(BaseModel):
    title: str
    body: str
    published: Optional[bool] = True

@app.post("/blog")
def create_blog(request: CreateBlog):
    start_time=time.time()      # start time

    REQUEST_COUNT.labels(method="POST", endpoint="/blog").inc()
    response= {
        "message": "Blog created",
        "title": request.title,
        "environment": APP_ENV
    }

    duration = time.time() - start_time # stop time

    REQUEST_LATENCY.labels(
        endpoint="/blog"
    ).observe(duration)

    return response



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
