
# SLI, SLO, SLA & Alerting Philosophy


Explain SLI, SLO, SLA clearly 

Understand why alerts are tied to SLOs

Know why “zero downtime” is unrealistic

Understand error budgets

Explain why not every issue should alert


---

Companies don’t monitor systems because they love graphs.
They monitor systems because:
  - Users expect reliability

---

## 1️⃣ SLI — Service Level Indicator

### Definition
A metric that measures user experience

Examples:- 
  - Request success rate
  - Request latency
  - Availability

Examples in Prometheus:-
```
http_requests_total
http_request_latency_seconds
up
```
👉 SLI = WHAT we measure

---

## 2️⃣ SLO — Service Level Objective

### Definition
A target value for an SLI

Examples:-
  - 99.9% requests successful
  - P95 latency < 1 second
  - Service available 99.95% of time

👉 SLO = HOW GOOD is good 

---

## 3️⃣ SLA — Service Level Agreement

### Definition
A business/legal contract

Examples:
  - Refunds
  - Credits
  - Penalties

👉 SLA is NOT engineering-focused
👉 Engineers mostly care about SLOs

---

| Term | Meaning            |
| ---- | ------------------ |
| SLI  | What we measure    |
| SLO  | Target reliability |
| SLA  | Business promise   |

---

## 📊 Example (FastAPI Service)
**SLI**
  - Request latency

**SLO**
- 95% of requests must complete in under 1 second

**SLA**
- If violated → customer refund

---

## 🚨 Why Alerts Are Based on SLOs (Not Metrics)

**Bad alert**:
```
CPU usage is 80%
```

**Good alert:**
```
Users are experiencing slow responses
```

Alerts should trigger when SLO is at risk, not when a metric moves.

---

## 🧮 Error Budget (Critical Concept)

### Definition
Allowed amount of failure within SLO (without violating its Service Level Objective)

Example:
  - SLO = 99.9% availability
  - Allowed failure = 0.1%

This 0.1% is your error budget.

---

## ⚠️ Alert Fatigue (Real Industry Problem)

**Too many alerts cause:**
  - Engineers ignoring alerts
  - Slower response
  - Burnout
  - Missed real incidents

That’s why:
Fewer, meaningful alerts win

---

## 🧠 Alerting  (Golden Rules)

**Rule 1:** Alert only when human action is required
**Rule 2:** Alert when user experience is affected
**Rule 3:** Alert when SLO is at risk
**Rule 4:** Metrics explain problems — alerts notify them

---

## 📉 Example: Bad vs Good Alert
❌ Bad
```
Latency > 300ms for 10 seconds
```

✅ Good
```
P95 latency > 1s for 2 minutes
```

---

### Alerts are defined in a file, usually:
```
alerts.yml
```
And Prometheus loads it via prometheus.yml.

## 🧱 Step 1: Create alerts.yml
```
groups:
- name: fastapi-alerts
  rules:

  - alert: FastAPIInstanceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "FastAPI service is down"
      description: "FastAPI has been unreachable for more than 1 minute"
```

---

## 🧠 Understand Every Line (Important)

### `alert`

Name of the alert

### `expr`

PromQL condition

```promql
up == 0
```

Means:

> Target is unreachable

---

### `for: 1m`

Alert fires **only if condition stays true for 1 minute**

Prevents false positives.

---

### `labels`

Metadata for routing later (Alertmanager).

---

### `annotations`

Human-readable message.

---


## 🧩 Step 2: Load Alerts in Prometheus

Edit `prometheus.yml`:

```yaml
rule_files:
  - "alerts.yml"
```

Restart Prometheus.

---

## 🔍 Step 3: Verify Alerts UI

Open:

```text
http://localhost:9090/alerts
```

You should see:

* `FastAPIInstanceDown`
* Status: **inactive**

---

## 🧪 Step 4: Trigger the Alert (Practice)

1. Stop FastAPI container
2. Wait 1 minute
3. Go to Prometheus → Alerts tab

You will see:

* `pending` → `firing`

🔥 **This is real alerting**

---

## 📈 Step 5: Latency-Based Alert (Your Histogram Use)

```yaml
- alert: HighLatencyP95
  expr: |
    histogram_quantile(
      0.95,
      rate(http_request_latency_seconds_bucket[1m])
    ) > 1
  for: 2m
  labels:
    severity: warning
  annotations:
    summary: "High latency detected"
    description: "P95 latency is above 1 second for 2 minutes"
```
### `histogram_quantile(0.95, …)`

Means:

> “95% of users are slower than this”

This is **SRE-style alerting**, not beginner stuff.

---

### `rate(...[1m])`

Why?

* Histogram buckets are counters
* Counters must be converted into rates

No `rate()` → **wrong alert**

---

### `> 1`

Threshold:

* Users waiting more than **1 second**

---

### `for: 2m`

We tolerate:

* small spikes
* short bursts

Alert only if **persistent pain**

---

## 🧠 Why This Alert Is GOOD

* Uses **P95**, not average
* Uses **rate()**
* Uses **for**
* Tied to **user experience**


## Why Alerts Are NOT Business Traffic

* `/metrics` calls are:

  * machine-to-machine
  * internal
  * predictable

So:

> Never alert on `/metrics` latency or count.

Good monitoring **excludes noise**.

---


# 🔎 Verify Inside Container (Optional but Powerful)

Run:

```bash
docker exec -it prometheus sh
```

Then:

```sh
ls /etc/prometheus
```

You **must see**:

```
alerts.yml
prometheus.yml
```

If you don’t → Prometheus cannot load alerts.

---

## Docker command to run with alert rules

```
docker run -d \
  --name prometheus \
  --network monitoring-net \
  -p 9090:9090 \
  -v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml \
  -v $(pwd)/alerts.yml:/etc/prometheus/alerts.yml \
  prom/prometheus

```

---
