# Agnostic Metrics Skill (`SKILL.md`)

This skill provides step-by-step guidance and language-agnostic standards for instrumenting metrics, managing label cardinality, and measuring SRE Golden Signals.

## Workflow Instructions

### Step 1: Map the Four Golden Signals

Identify and instrument the following 4 core signals for every component/service:

| Signal | Metric Type | Naming Template | Example Labels |
| :--- | :--- | :--- | :--- |
| **Latency** | Histogram | `http_request_duration_seconds` | `method="POST"`, `route="/v1/orders"`, `status="2xx"` |
| **Traffic** | Counter | `http_requests_total` | `method="POST"`, `route="/v1/orders"` |
| **Errors** | Counter | `http_requests_failed_total` | `method="POST"`, `route="/v1/orders"`, `error_type="Timeout"` |
| **Saturation** | Gauge | `app_connection_pool_active_connections` | `pool_name="primary_db"` |

### Step 2: Rules for Metric Types

1. **Counter**: Monotonically increasing value (resets to 0 on service restart). Use for request counts, error counts, task completions.
   - *Rule*: Never decrement a counter.
2. **Gauge**: Value that goes up and down. Use for memory usage, active requests, queue size, thread pool utilization.
3. **Histogram**: Measures statistical distributions of values (e.g., response times, payload sizes) in predefined buckets.
   - *Rule*: Always calculate $p50$, $p90$, $p95$, and $p99$ percentiles server-side using histogram buckets, rather than computing averages.

### Step 3: High-Cardinality Prevention Protocol

Check every label applied to every metric against this checklist:

- [ ] Does this label value have more than 100 possible discrete values?
- [ ] Is this label an ID (User ID, Order ID, Session ID, UUID, IP Address)?
- [ ] Is this label an unparameterized URI path (e.g., `/users/12345` instead of `/users/{id}`)?

If YES to any of the above, **REMOVE or PARAMETERIZE the label**.

### Step 4: Language-Agnostic Pseudocode Pattern

```
INTERFACE MetricsRegistry:
    FUNCTION create_counter(name, help_text, label_names)
    FUNCTION create_histogram(name, help_text, label_names, buckets)
    FUNCTION create_gauge(name, help_text, label_names)

// Service Initialization
GLOBAL http_requests_total = MetricsRegistry.create_counter(
    name = "http_requests_total",
    help = "Total HTTP requests received",
    labels = ["method", "route", "status_code"]
)

GLOBAL http_request_duration_seconds = MetricsRegistry.create_histogram(
    name = "http_request_duration_seconds",
    help = "HTTP request duration in seconds",
    labels = ["method", "route"],
    buckets = [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

FUNCTION handle_incoming_request(request):
    start_time = current_timestamp()
    normalized_route = sanitize_and_parameterize_path(request.path) // e.g., "/users/:id"
    
    TRY:
        response = execute_request_logic(request)
        status_code = response.status_code
        RETURN response
    CATCH Exception ex:
        status_code = 500
        RAISE ex
    FINALLY:
        elapsed_seconds = (current_timestamp() - start_time) / 1000.0
        
        // Record metrics with low-cardinality labels
        http_requests_total.inc(labels=["method": request.method, "route": normalized_route, "status": status_code])
        http_request_duration_seconds.observe(elapsed_seconds, labels=["method": request.method, "route": normalized_route])
```

### Step 5: SLI / SLO Calculation Formulae
Using these raw metrics, write PromQL / Metrics queries for SLOs:

- **Availability SLI**:
  $$\text{Availability} = \frac{\sum \text{rate}(http\_requests\_total[status=\sim"2..|3.."][5m])}{\sum \text{rate}(http\_requests\_total[5m])}$$
- **Latency SLI ($< 200\text{ms}$)**:
  $$\text{Latency Ratio} = \frac{\sum \text{rate}(http\_request\_duration\_seconds\_bucket[le="0.2"][5m])}{\sum \text{rate}(http\_request\_duration\_seconds\_count[5m])}$$
