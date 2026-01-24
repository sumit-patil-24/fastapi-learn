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

## 📍 Monitoring Checkpoint M3 — Grafana
🎯 Goal: 
By the end of this checkpoint, you must be able to say: “I can visualize application metrics using Grafana dashboards.”


## 🔹 Step 1 — Run Grafana (Docker)
```
docker run -d \
  --name grafana \
  --network monitoring-net \
  -p 3000:3000 \
  grafana/grafana:9.0.0
```

Verify:
```
http://localhost:3000
```

Login:
  - user: admin
  - password: admin

## 🔹 Step 2 — Add Prometheus as Data Source

In Grafana UI:
  - Settings → Data Sources
  - Add data source → Prometheus

- URL:
```
http://prometheus:9090
```

Save & Test → must be green

---

###########
## 2️⃣ Go to Explore (not Dashboard)

Grafana left menu → Explore
  - Select Prometheus datasource
  - In query box, type:
```
up
```
Click Run query

Expected:
  - One or more green lines
  - job="fastapi" or job="prometheus"
This confirms PromQL execution.


## 🔹 Step 3 — Create Your First Dashboard:

Create panels for:

### Panel 1 — Request count

Query:
```
http_requests_total
```

### Visualization:
- Time series

---

### Panel 2 — Requests per endpoint

Query:
```
sum by (endpoint) (http_requests_total)
```

---

## Panel 3 — Latency (95th percentile)

Query:
```
histogram_quantile(
  0.95,
  sum by (le, endpoint) (http_request_latency_seconds_bucket)
)
```




# Errors:

grafana data source connection error:
  **Unknown error during query transaction. Please check JS console logs.**

## how to dubug:
# Enter the container as root
docker exec -it --user root grafana sh

# Now you can install curl
apk update && apk add curl

# Test your connection
curl http://prometheus:9090

## note: only **http://prometheus:9090** is working as URL.