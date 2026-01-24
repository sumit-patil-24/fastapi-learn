# fastapi-learn

# 📍 Monitoring Checkpoint M2 — Prometheus Setup
## 🎯 Goal: By the end of this checkpoint, you must be able to say:
“Prometheus is running and successfully scraping metrics from my FastAPI app.”

## Prometheus has only three responsibilities:
1. Know where to scrape (targets)
2. Know how often to scrape (scrape_interval)
3. Store numbers it pulls from /metrics
It only reads text from /metrics.

## Architecture
```
FastAPI (Docker)  --->  /metrics
        ↑
Prometheus (Docker) ---- scrapes every X seconds
```
Both containers must be able to talk to each other.


##🔹 Step 1 — Create prometheus.yml

Create this file at the project root (same level as Dockerfile):

```
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: "fastapi-app"
    static_configs:
      - targets: ["fastapi-app:9000"]
```

## Explanation:

- scrape_interval: 5s
    - Prometheus will pull metrics every 5 seconds

- job_name
    - Logical name shown in Prometheus UI

- targets
    - Hostname + port of your FastAPI container
    -  fastapi-app will be the container name

## 🔹 Step 2 — Create a Docker network
```
docker network create monitoring-net
```
Containers cannot resolve each other by name without a shared network

## 🔹 Step 3 — Run FastAPI container on the network
```
docker run -d \
  --name fastapi-app \
  --network monitoring-net \
  -p 9000:9000 \
  fastapi-app
```

Verify: http://localhost:9000/metrics works

## 🔹 Step 4 — Run Prometheus container
```
docker run -d \
  --name prometheus \
  --network monitoring-net \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

## Important points:
- -v mounts your config file
- Prometheus reads config at startup
- If config is wrong → container will fail

## 🔹 Step 5 — Verify in Prometheus UI
```
http://localhost:9090
```

## Check these in order:
1. Go to Status → Targets
2. You must see:
    - Job: fastapi-app
    - State: UP