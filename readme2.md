
# 📌 Checkpoint M6 — Alertmanager

## 🔔 What is Alertmanager?

**Alertmanager is responsible for alert delivery and control**, not detection.

It decides:

* **Who** should be notified
* **How** they should be notified (Slack, Email, Pager, etc.)
* **Whether** similar alerts should be grouped
* **Whether** alerts should be silenced or muted

---

## ⚠️ Responsibility Separation (Very Important)

> **Prometheus and Alertmanager have strictly separate responsibilities**

### Prometheus

* Scrapes metrics
* Evaluates alert rules
* Decides *when* an alert fires

### Alertmanager

* Receives alerts from Prometheus
* Routes alerts
* Sends notifications

### Key Rules

* ❌ **Prometheus never sends emails or Slack messages**
* ❌ **Alertmanager never queries metrics**

---

## 🔄 Monitoring & Alert Flow

```
FastAPI Application
        ↓
   /metrics endpoint
        ↓
Prometheus (scrape + alert rules)
        ↓
Alertmanager (route + notify)
        ↓
Human (Slack / Email / Pager)
```

---

## ❗ Important Clarification

### Alertmanager does NOT automatically receive alerts

Alertmanager **does nothing by itself**.

Prometheus must be **explicitly configured** to send alerts to Alertmanager.

That is why **Alertmanager is useless when running alone**.

---

## 🔗 Prometheus → Alertmanager Wiring

Prometheus must be told where Alertmanager is running.

Add this to `prometheus.yml`:

```yaml
alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### 📌 Notes

* `alertmanager` is the **Docker container name**
* Docker DNS automatically resolves container names
* Both containers **must be on the same Docker network**

---

## 🌐 Network Requirement

> **Prometheus and Alertmanager must be attached to the same Docker network**

Example:

```
monitoring-net
```

Otherwise:

* Prometheus cannot reach Alertmanager
* Alerts will never be delivered

---

## 📝 Alertmanager Configuration (`alertmanager.yml`)

We start with the **simplest possible configuration**.

```yaml
global:
  resolve_timeout: 5m

route:
  receiver: "default-receiver"

receivers:
  - name: "default-receiver"
```

### What this config does:

* Accepts incoming alerts
* Routes all alerts to one default receiver
* No Slack / Email yet (added in later checkpoints)

---

## ▶️ Running Alertmanager with Docker

```bash
docker run -d \
  --name alertmanager \
  --network monitoring-net \
  -p 9093:9093 \
  -v $(pwd)/alertmanager.yml:/etc/alertmanager/alertmanager.yml \
  prom/alertmanager
```

### Explanation:

* `--network monitoring-net` → same network as Prometheus
* `-p 9093:9093` → expose Alertmanager UI
* `-v ...alertmanager.yml` → mount config file
* `prom/alertmanager` → official image


---

## What part you didn’t understand (I’ll restate it simply)

You didn’t understand **this flow** 👇

```
FastAPI DOWN
   ↓
up == 0
   ↓
Prometheus fires alert
   ↓
Prometheus sends alert to Alertmanager
   ↓
Alertmanager shows FIRING
```

So let’s rebuild this **step by step**, like a real-world analogy.

---

# 🧠 First: What is `up`? (most important)

Prometheus automatically creates a metric called:

```
up
```

You **did not create it**.
Prometheus creates it for **every scrape target**.

### Meaning of `up`

For every target Prometheus scrapes:

* `up = 1` → target is reachable
* `up = 0` → target is unreachable

That’s it. Nothing more.

---

## In your case

You have this in `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: "fastapi"
    static_configs:
      - targets: ["fastapi-app:9000"]
```

So Prometheus is doing this repeatedly:

> “Can I reach `fastapi-app:9000/metrics`?”

* Yes → `up{job="fastapi"} = 1`
* No  → `up{job="fastapi"} = 0`

---

# 🔔 What is an alert rule then?

An alert rule is **just a condition on metrics**.

Example (very simple English):

> “If FastAPI is down for 10 seconds, raise an alert.”

That becomes this rule:

```yaml
alert: FastAPIAppDown
expr: up{job="fastapi"} == 0
for: 10s
```

Let’s decode line by line.

---

## Line-by-line explanation

### 1️⃣ `alert: FastAPIAppDown`

This is just the **name** of the alert.
Like a variable name.

---

### 2️⃣ `expr: up{job="fastapi"} == 0`

This is the **condition**.

Read it like English:

> “For the job called fastapi, if `up` equals zero”

That means:

* Prometheus cannot reach FastAPI

---

### 3️⃣ `for: 10s`

This avoids **false alerts**.

It means:

> “Don’t alert immediately.
> Only alert if this condition stays true for 10 seconds.”

So:

* FastAPI down for 2s → ignore
* FastAPI down for 10s → ALERT 🚨

---

# 🔗 Now the MOST confusing part (but important)

## “Prometheus fires alert” — what does that mean?

It does **NOT** mean email
It does **NOT** mean Slack
It does **NOT** mean notification

It means:

> Prometheus internally marks the alert as **FIRING**

You can see this inside Prometheus itself.

---

## How to see firing alerts (no browser needed)

This command asks Prometheus:

> “Which alerts are firing right now?”

```bash
curl localhost:9090/api/v1/alerts
```

If FastAPI is stopped, you’ll see:

```json
{
  "alertname": "FastAPIAppDown",
  "state": "firing"
}
```

At this point:

* Alert exists
* Alert is active
* BUT nobody is notified yet

---

# 📬 Where does Alertmanager come in?

Prometheus **does not send notifications**.

Prometheus only:

* evaluates rules
* decides alert states

Alertmanager:

* receives alerts
* groups them
* sends notifications

So Prometheus **pushes** alerts to Alertmanager.

That’s why this block exists in `prometheus.yml`:

```yaml
alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

This literally means:

> “Hey Prometheus, whenever an alert fires, send it to Alertmanager running at `alertmanager:9093`”

---

## How do we check if Alertmanager received it?

We ask Alertmanager directly:

```bash
curl localhost:9093/api/v2/alerts
```

If wiring is correct, you’ll see the same alert there.

---

# 🔁 Complete flow (now rewritten very simply)

1. Prometheus scrapes FastAPI
2. FastAPI stops
3. `up == 0`
4. Alert rule condition becomes true
5. After 10s → alert becomes FIRING
6. Prometheus sends alert to Alertmanager
7. Alertmanager stores it (and later sends notifications)

---
