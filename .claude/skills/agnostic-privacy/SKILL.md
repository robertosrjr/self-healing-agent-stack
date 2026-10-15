# Agnostic LGPD & Privacy SRE Skill (`SKILL.md`)

This skill provides step-by-step rules, audit checklists, and code-level sanitization specifications to enforce LGPD and GDPR compliance within SRE workflows.

## Workflow Instructions

### Step 1: Map LGPD Legal Principles to SRE Operational Practices

| LGPD Article / Principle | SRE Engineering Requirement | Implementation Rule |
| :--- | :--- | :--- |
| **Art. 6º, III - Minimização (Minimization)** | Collect only essential telemetry | Do not log full HTTP request/response bodies by default. Log only sanitized headers and metadata. |
| **Art. 6º, VII - Segurança (Security)** | Protect telemetry in transit & at rest | Enforce TLS 1.3 for telemetry exporters (OTLP over gRPC/HTTPS) and AES-256 for log storage. |
| **Art. 6º, X - Responsabilização (Accountability)** | Immutable audit trail for ops access | Enforce Zero-Touch production access; record all Breakglass emergency SSH/Kubernetes exec sessions. |
| **Art. 16 - Eliminação de Dados (Data Deletion)** | Enforce log lifecycle & TTL policies | Set log index retention to 30-90 days max, with automatic purge policies. |

### Step 2: Language-Agnostic PII Scrubbing Processor Pattern

Implement a middleware/interceptor at the logging and tracing pipeline level:

```
CLASS TelemetryPrivacyFilter:
    DATA_PATTERNS = [
        {"name": "CPF", "regex": "\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b", "replacement": "[MASKED_CPF]"},
        {"name": "EMAIL", "regex": "\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "replacement": "[MASKED_EMAIL]"},
        {"name": "CREDIT_CARD", "regex": "\b(?:\d[ -]*?){13,16}\b", "replacement": "[MASKED_CARD]"},
        {"name": "BEARER_TOKEN", "regex": "Bearer\s+[A-Za-z0-9\-\._~\+\/]+=*", "replacement": "Bearer [REDACTED]"}
    ]

    FUNCTION sanitize_string(input_text):
        IF input_text IS NULL OR input_text IS EMPTY:
            RETURN input_text
            
        sanitized = input_text
        FOR EACH pattern IN DATA_PATTERNS:
            sanitized = regex_replace(sanitized, pattern.regex, pattern.replacement)
        RETURN sanitized

    FUNCTION process_log_record(log_record):
        log_record.message = sanitize_string(log_record.message)
        
        FOR EACH key, val IN log_record.attributes:
            IF val IS STRING:
                log_record.attributes[key] = sanitize_string(val)
                
        RETURN log_record
```

### Step 3: Staging & Postmortem Sanitization Checklist

Before exporting production telemetry or snapshots for debugging or postmortems:

- [ ] Has the dataset passed through an anonymization or pseudonymization pipeline?
- [ ] Are all real user identifiers replaced with UUIDs or deterministic hashes (HMAC with secret salt)?
- [ ] Are raw production database dumps strictly prohibited in dev/staging environments?
- [ ] Is the postmortem document free of raw customer details, containing only technical metrics and trace IDs?
