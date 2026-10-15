# Agnostic Logging Skill (`SKILL.md`)

This skill provides step-by-step instructions, JSON schemas, and language-agnostic patterns for implementing enterprise-grade, SRE-compliant structured logging.

## Workflow Instructions

### Step 1: Enforce Structured JSON Output
- Output ALL logs as single-line JSON objects to standard output (`stdout`) or standard error (`stderr`).
- Never write directly to local log files inside containers or application pods (offload log collection, rotation, and shipping to external daemons like FluentBit, Vector, or Otel Collector).

### Step 2: Canonical JSON Log Schema
Enforce the following JSON key schema across all microservices regardless of language:

```json
{
  "timestamp": "2026-10-14T12:00:00.123Z",
  "level": "INFO",
  "service.name": "payment-service",
  "service.version": "1.4.0",
  "environment": "production",
  "message": "Payment processed successfully",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "http": {
    "method": "POST",
    "status_code": 200,
    "url.path": "/v1/payments"
  },
  "duration_ms": 142.5
}
```

### Step 3: PII & LGPD Masking Patterns
Apply regex and AST/interceptor-level redaction filters BEFORE passing data to log output functions:

- **CPF (Brazilian National ID)**: `\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b` -> `***.***.***-**`
- **Email**: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b` -> `m***e@domain.com`
- **Credit Card (Luhn-matching)**: `\b(?:\d[ -]*?){13,16}\b` -> `****-****-****-1234`
- **Authorization Headers**: `Bearer\s+[A-Za-z0-9\-\._~\+\/]+=*` -> `Bearer [REDACTED]`

### Step 4: Language-Agnostic Pseudocode Pattern

```
FUNCTION log_event(level, message, context_map):
    // 1. Extract tracing context from current execution scope
    trace_id = TracingContext.get_current_trace_id()
    span_id = TracingContext.get_current_span_id()
    
    // 2. Build base payload
    payload = {
        "timestamp": current_time_iso8601_utc(),
        "level": level,
        "service.name": CONFIG.service_name,
        "message": message,
        "trace_id": trace_id,
        "span_id": span_id
    }
    
    // 3. Merge additional contextual key-value pairs
    FOR EACH key, value IN context_map:
        IF is_sensitive_key(key) OR contains_pii(value):
            payload[key] = sanitize_or_mask(value)
        ELSE:
            payload[key] = value
            
    // 4. Emit single-line JSON to stdout
    PRINT_TO_STDOUT(serialize_json(payload))
```

### Step 5: SRE Log Budget Rules
- **Hot Loops**: Never emit `INFO` or `DEBUG` logs inside loops that execute thousands of times per second. Use aggregated counters/metrics instead.
- **Error Stack Traces**: Include full stack traces ONLY for `ERROR` and `FATAL` levels. Include `error.type`, `error.message`, and `error.stacktrace` as distinct JSON keys.
