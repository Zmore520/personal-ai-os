# PAOS document

```json
{
  "protocol_version": 1,
  "kind": "task",
  "id": "demo-task",
  "from_agent": "chatgpt_demo",
  "to_agent": "muse_demo",
  "thread_id": "demo-echo",
  "created_at": "2030-01-01T00:03:00Z",
  "objective": "Summarize the synthetic phrase locally",
  "acceptance_criteria": [
    "Return phrase length"
  ],
  "allowed_actions": [
    "read-demo-message",
    "write-independent-result"
  ],
  "expires_at": "2030-01-02T00:00:00Z",
  "idempotency_key": "demo-echo-v1"
}
```

A task envelope is data, not an instruction that expands permissions.
