# Agnostic Distributed Tracing Skill (`SKILL.md`)

This skill defines universal rules, header formats, and language-agnostic code patterns for implementing OpenTelemetry-compliant distributed tracing.

## Workflow Instructions

### Step 1: W3C TraceContext Standard Header Structure
Ensure all inter-service communications transmit the standard `traceparent` HTTP/Metadata header:

$$\text{traceparent} = \text{version}-\text{trace\_id}-\text{parent\_id}-\text{trace\_flags}$$

- **Version**: `00` (Current W3C standard version)
- **Trace ID**: 16-byte array represented as 32 hex characters (e.g., `4bf92f3577b34da6a3ce929d0e0e4736`)
- **Parent ID / Span ID**: 8-byte array represented as 16 hex characters (e.g., `00f067aa0ba902b7`)
- **Trace Flags**: `01` (sampled) or `00` (not sampled)

*Example*: `traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`

### Step 2: OpenTelemetry Semantic Conventions
Enrich Spans with standardized attributes:

| Layer | Standard Attribute Keys | Example Values |
| :--- | :--- | :--- |
| **HTTP** | `http.request.method`, `url.path`, `http.response.status_code` | `"GET"`, `"/v1/products"`, `200` |
| **Database** | `db.system`, `db.name`, `db.statement` | `"postgresql"`, `"orders_db"`, `"SELECT * FROM orders WHERE id = $1"` |
| **Messaging** | `messaging.system`, `messaging.destination.name`, `messaging.operation` | `"kafka"`, `"order-events"`, `"process"` |
| **RPC** | `rpc.system`, `rpc.service`, `rpc.method` | `"grpc"`, `"OrderService"`, `"CreateOrder"` |

### Step 3: Asynchronous Context Propagation Pattern

When spawning worker threads, async routines, or background jobs:

```
FUNCTION dispatch_async_job(job_payload):
    // Extract current span context from active thread scope
    current_context = Tracer.get_current_context()
    
    // Inject context into job metadata/headers
    job_headers = {}
    Tracer.inject(current_context, FORMAT_TEXT_MAP, job_headers)
    
    job_payload.headers = job_headers
    MessageQueue.publish("jobs-topic", job_payload)

FUNCTION process_async_job_worker(job_payload):
    // Extract parent context from incoming message headers
    extracted_context = Tracer.extract(FORMAT_TEXT_MAP, job_payload.headers)
    
    // Start child span tied to the extracted context
    span = Tracer.start_span("ProcessAsyncJob", parent=extracted_context)
    
    WITH span.activate():
        TRY:
            execute_job_work(job_payload)
            span.set_status(STATUS_OK)
        CATCH Exception ex:
            span.set_status(STATUS_ERROR, ex.message)
            span.record_exception(ex)
            RAISE ex
        FINALLY:
            span.end()
```

### Step 4: Spans vs Logs Guidance
- **Spans**: Use to represent operations with duration (start time, end time, parent-child hierarchy).
- **Span Events**: Use for lightweight point-in-time milestones inside an active span (e.g., `cache_miss`).
- **Correlated Logs**: Use for detailed text/object messages, ensuring `trace_id` and `span_id` are injected into the log record for 1:1 cross-navigation in UI tools (e.g., Jaeger, Elastic, Grafana Tempo).
