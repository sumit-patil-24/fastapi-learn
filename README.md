* To copy a file from your current local directory to a Docker container, use the docker cp command with a relative path for the source. 
```
docker cp ./<source_file_path> <container_name_or_id>:<destination_path>
```


# 📌 Checkpoint M7 — Latency-Based Alerts (Prometheus → Alertmanager)

This checkpoint answers **one real production question**:

> “My app is UP, but users say it is SLOW — how do I detect that?”

---

## 1️⃣ What problem latency alerts solve

* `up == 1` → app is reachable
* ❌ But response time may be **too high**
* Users suffer **before** downtime happens

So we alert on **latency**, not availability.

---

## 2️⃣ Metric we already have (no new instrumentation)

From FastAPI you already exposed:

```python
REQUEST_LATENCY = Histogram(
    "http_request_latency_seconds",
    "Request latency",
    ["endpoint"]
)
```

Prometheus automatically converts this into:

* `http_request_latency_seconds_bucket`
* `http_request_latency_seconds_sum`
* `http_request_latency_seconds_count`

👉 **Latency alerts always use `_bucket`**

---

## 3️⃣ What “P95 latency” really means (simple)

**P95 = 95th percentile latency**

Meaning:

> 95% of requests are faster than this value
> 5% of requests are slower (worst users)

This is what companies alert on.

---

## 4️⃣ PromQL for P95 latency (core query)

```promql
histogram_quantile(
  0.95,
  rate(http_request_latency_seconds_bucket[1m])
)
```

### Read it in English:

* Look at latency buckets
* Over last 1 minute
* Calculate the 95th percentile

---

## 5️⃣ Latency Alert Rule (`alerts.yml`)

Add **this rule** (below your AppDown alert):

```yaml
- alert: HighRequestLatency
  expr: histogram_quantile(
          0.95,
          rate(http_request_latency_seconds_bucket[1m])
        ) > 0.5
  for: 1m
  labels:
    severity: warning
  annotations:
    summary: "High request latency detected"
    description: "P95 latency is above 500ms for 1 minute."
```

### Threshold logic

* `0.5` → 500ms
* Adjust later (this is realistic for FastAPI)


Always reload container after rule changes.

---

## 7️⃣ How to trigger this alert (important)

Generate **slow traffic**.

Example (simulate load):

```bash
while true; do curl localhost:9000/; sleep 0.1; done
```

Or add artificial delay in FastAPI (temporary):

```python
import time
time.sleep(0.8)
```

---

## 8️⃣ Verify alert lifecycle

### In Prometheus:

```bash
curl localhost:9090/api/v1/alerts
```

You should see:

* `HighRequestLatency`
* `state: pending` → then `firing`

### In Alertmanager:

```bash
curl localhost:9093/api/v2/alerts
```

If visible → pipeline works.

---

## What we are doing (1-line goal)

> When a Prometheus alert fires → a message appears in a Slack channel.

That’s it.

---

## Step 1️⃣ Create Slack Incoming Webhook (outside terminal)

You do this **once**.

1. Go to **Slack → Settings → Apps**
2. Search **“Incoming Webhooks”**
3. Add it to your workspace
4. Choose a channel (example: `#alerts`)
5. Copy the **Webhook URL**

It looks like:

```
https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXX
```

⚠️ This URL is **secret** (like a password).

---

## Step 2️⃣ Alertmanager config (`alertmanager.yml`)

Create / update this file:

```yaml
global:
  resolve_timeout: 5m

route:
  receiver: "slack-notifications"
  group_by: ["alertname"]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

receivers:
- name: "slack-notifications"
  slack_configs:
  - api_url: "PASTE_YOUR_SLACK_WEBHOOK_URL_HERE"
    channel: "#alerts"
    send_resolved: true
    title: "{{ .CommonAnnotations.summary }}"
    text: >-
      {{ range .Alerts }}
      *Alert:* {{ .Annotations.description }}
      *Status:* {{ .Status }}
      *StartsAt:* {{ .StartsAt }}
      {{ end }}
```



## Step 3️⃣ Run / Restart Alertmanager (with config mounted)

```bash
docker rm -f alertmanager

docker run -d \
  --name alertmanager \
  --network monitoring-net \
  -p 9093:9093 \
  -v $(pwd)/alertmanager.yml:/etc/alertmanager/alertmanager.yml \
  prom/alertmanager
```

Verify:

```bash
curl localhost:9093
```

---


## Step 6️⃣ Slack verification (MOST IMPORTANT)

Open Slack → `#alerts`

You should see:

* Alert name
* Description
* Status = firing

Then remove `sleep` → wait → Slack gets **RESOLVED** message.

This confirms **full alert lifecycle**.


---



## Gmail Requirements (READ CAREFULLY)

You **CANNOT** use normal Gmail password.

You must use:

### 🔐 Gmail App Password

Steps:

1. Enable **2-Step Verification**
2. Create **App Password**
3. Use that password in Alertmanager

📌 Without this → email will NEVER work.

---

## Minimal Working Email Config (Correct Way)

### alertmanager.yml (EMAIL ONLY)

```yaml
global:
  resolve_timeout: 5m
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'your-email@gmail.com'
  smtp_auth_username: 'your-email@gmail.com'
  smtp_auth_password: 'APP_PASSWORD_HERE'
  smtp_require_tls: true

route:
  receiver: email-notifications

receivers:
- name: email-notifications
  email_configs:
  - to: 'receiver-email@gmail.com'
    send_resolved: true
```

