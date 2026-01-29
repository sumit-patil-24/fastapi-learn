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


## 🔹 Step 1 — Create prometheus.yml

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

```
sum by (endpoint) (http_requests_total)
```

---

## Panel 3 — Latency (95th percentile)

```
histogram_quantile(0.95, rate(http_request_latency_seconds_bucket[1m]))

```
Mental picture:
  - 100 requests come in
  - 95 finished faster than this number
  - 5 were slower

📌 Grafana graph meaning:
  - Smooth line → stable service
  - Sudden jump → CPU, DB, network, or code issue


---


# Queries

## Verify Data Is Coming (Sanity Check)

### Before dashboards, always verify raw data.

## Step 1: Open Grafana
  - Go to Explore
  - Select Prometheus datasource

## Step 2: Run these queries one by one
1️ Is Prometheus scraping anything?
```
up
```
Expected:
  - Value = 1 for your FastAPI target
  - If 0 → service is down or scrape config wrong

This is always the first query in real life.

---

## Request Count Panel (Traffic)
We now visualize how many requests your app is handling.

## Metric used
```
http_requests_total
```
But raw counters are useless → we use rate.


## Correct query
```
rate(http_requests_total[1m])
```
This means:
  - “Requests per second”
  - Calculated over last 1 minute

## Add labels (better)
```
rate(http_requests_total{endpoint="/"}[1m])
```

## 📌 Create Panel
  - Panel type: Time series
  - Title: HTTP Requests/sec
  - Unit: req/s
✅ Checkpoint rule:
If traffic spikes, graph must spike.

---

## Request Latency Panel (Performance)
Now we measure how slow or fast your app is.

## Metric used
```
http_request_latency_seconds_bucket
```
This is a Histogram, so we use histogram_quantile.

### Correct query (P95 latency)
```
histogram_quantile(
  0.95,
  rate(http_request_latency_seconds_bucket[1m])
)
```

Meaning:
  - 95% of requests finish under this time
  - This is industry standard

## For specific endpoint
```
histogram_quantile(
  0.95,
  rate(http_request_latency_seconds_bucket{endpoint="/"}[1m])
)
```
## 📌 Create Panel
  - Panel type: Time series
  - Title: P95 Request Latency
  - Unit: seconds
✅ If latency suddenly jumps → something is wrong.

---

## Single Value Health Panel
```
sum(rate(http_requests_total[1m]))
```
### Panel settings
  - Panel type: Stat
  - Title: Total Requests/sec
  - Unit: req/s

# P95 latency means that 95% of all user requests are faster than a specific value, while the slowest 5% take longer.

---


## Errors:

grafana data source connection error:
  **Unknown error during query transaction. Please check JS console logs.**

## how to dubug:
### Enter the container as root
```
docker exec -it --user root grafana sh
```

### Now you can install curl
```
apk update && apk add curl
```

### Test your connection
```
curl http://prometheus:9090
```


### note: only **http://prometheus:9090** is working as URL.

### for some of our queries rate() requires continuous changes over time.
- Generate continuous traffic
```
while true; do
  curl http://localhost:9000/ > /dev/null
  sleep 0.2
done
```
after it **rate(http_request_latency_seconds_bucket[1m])**
will work