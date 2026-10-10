"""Strict JSON metadata in Markdown; no task text is executed."""
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

ID = re.compile(r"^[a-z][a-z0-9_-]{0,79}$")
KINDS = {"message", "receipt", "task", "task_event", "memory", "memory_review", "agent"}
TRANSITIONS = {
    "pending": {"in_progress", "cancelled"},
    "in_progress": {"blocked", "completed", "cancelled"},
    "blocked": {"in_progress", "cancelled"},
    "completed": set(), "cancelled": set(),
}


class Invalid(ValueError):
    """A document or workspace violates protocol v1."""


def timestamp(value):
    if not isinstance(value, str):
        raise Invalid("timestamp must be a string")
    try:
        date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise Invalid("invalid ISO timestamp") from exc
    if date.tzinfo is None:
        raise Invalid("timestamp requires timezone")
    return date


def validate(meta):
    if not isinstance(meta, dict) or type(meta.get("protocol_version")) is not int or meta.get("protocol_version") != 1:
        raise Invalid("protocol_version must be 1")
    if meta.get("kind") not in KINDS:
        raise Invalid("unknown document kind")
    for key in ("id", "from_agent", "to_agent", "thread_id"):
        if not isinstance(meta.get(key), str) or not ID.fullmatch(meta[key]):
            raise Invalid(f"invalid {key}")
    timestamp(meta.get("created_at"))
    for key in ("reply_to", "task_id", "memory_id", "supersedes_id"):
        if key in meta and (not isinstance(meta[key], str) or not ID.fullmatch(meta[key])):
            raise Invalid(f"invalid {key}")
    kind = meta["kind"]
    required = {
        "message": ["sources"], "receipt": ["reply_to", "read_status", "sources"],
        "task": ["objective", "acceptance_criteria", "allowed_actions", "expires_at", "idempotency_key"],
        "task_event": ["task_id", "reply_to", "revision", "status", "evidence"],
        "memory": ["content", "sources", "status"],
        "memory_review": ["memory_id", "decision", "reviewed_by", "reviewed_at"],
        "agent": ["agent_id", "status", "capabilities", "transport", "verified_at"],
    }[kind]
    for key in required:
        if key not in meta:
            raise Invalid(f"missing {key}")
    for key in ("sources", "acceptance_criteria", "allowed_actions", "evidence", "capabilities"):
        if key in meta and (not isinstance(meta[key], list) or
                           any(not isinstance(x, str) or not x.strip() for x in meta[key])):
            raise Invalid(f"{key} must be an array of nonempty strings")
    for key in ("objective", "content", "idempotency_key", "reviewed_by", "transport"):
        if key in meta and (not isinstance(meta[key], str) or not meta[key].strip()):
            raise Invalid(f"{key} must be nonempty text")
    if kind == "task":
        if not meta["acceptance_criteria"]:
            raise Invalid("task requires acceptance criteria")
        if timestamp(meta["expires_at"]) <= timestamp(meta["created_at"]):
            raise Invalid("expiry must follow creation")
    if kind == "task_event":
        if type(meta["revision"]) is not int or meta["revision"] < 1:
            raise Invalid("revision must be a positive integer")
        if meta["status"] not in TRANSITIONS:
            raise Invalid("invalid task status")
        if meta["status"] == "completed" and not meta["evidence"]:
            raise Invalid("completion requires evidence")
        if meta["status"] == "blocked" and not meta.get("error"):
            raise Invalid("blocked event requires error")
    if kind == "receipt" and meta["read_status"] not in {"success", "failed"}:
        raise Invalid("invalid read_status")
    if kind == "memory" and meta["status"] != "pending":
        raise Invalid("new memories must be pending")
    if kind == "memory_review":
        if meta["decision"] not in {"confirmed", "rejected"} or meta["from_agent"] != "human":
            raise Invalid("memory review requires human author and decision")
        timestamp(meta["reviewed_at"])
    if kind == "agent":
        if not isinstance(meta["agent_id"], str) or not ID.fullmatch(meta["agent_id"]):
            raise Invalid("invalid agent_id")
        if meta["status"] not in {"pending", "active", "revoked"}:
            raise Invalid("invalid agent status")
        if meta["verified_at"] is not None:
            timestamp(meta["verified_at"])
        if meta["status"] == "active" and (meta["verified_at"] is None or not meta.get("approved_by")):
            raise Invalid("active agent requires verification and approval record")
    return meta


def decode(text):
    prefix = "# PAOS document\n\n```json\n"
    if not text.startswith(prefix) or "\n```\n" not in text[len(prefix):]:
        raise Invalid("expected canonical PAOS Markdown envelope")
    header, body = text[len(prefix):].split("\n```\n", 1)
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise Invalid(f"duplicate JSON key: {key}")
            result[key] = value
        return result
    try:
        meta = json.loads(header, object_pairs_hook=pairs)
    except json.JSONDecodeError as exc:
        raise Invalid("invalid JSON metadata") from exc
    return validate(meta), body.lstrip("\n")


def encode(meta, body=""):
    validate(meta)
    return "# PAOS document\n\n```json\n" + json.dumps(meta, ensure_ascii=False, indent=2) + "\n```\n\n" + body


def write(root, meta, body=""):
    """Exclusive creation, never replace another document. Local FS only."""
    content = encode(meta, body)
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    path = root / (meta["id"] + ".md")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    return path


def load(root):
    documents = {}
    for path in sorted(Path(root).rglob("*.md")):
        if path.is_symlink():
            raise Invalid(f"symlink document forbidden: {path.name}")
        try:
            meta, body = decode(path.read_text(encoding="utf-8"))
        except Invalid as exc:
            raise Invalid(f"{path.name}: {exc}") from exc
        if meta["id"] in documents:
            raise Invalid(f"duplicate document id: {meta['id']}")
        documents[meta["id"]] = (meta, body)
    audit(documents)
    return documents


def audit(documents):
    """Validate references and deterministic, single-writer task event chains."""
    def target(meta, key, kind=None):
        ref = documents.get(meta[key])
        if ref is None or (kind and ref[0]["kind"] != kind):
            raise Invalid(f"{meta['id']}: dangling or wrong-kind {key}")
        return ref[0]
    keys = set()
    for meta, _ in documents.values():
        if "reply_to" in meta:
            parent = target(meta, "reply_to")
            if parent["thread_id"] != meta["thread_id"]:
                raise Invalid("reply crosses threads")
            if timestamp(meta["created_at"]) < timestamp(parent["created_at"]):
                raise Invalid("reply predates parent")
            seen = {meta["id"]}
            cursor = parent
            while True:
                if cursor["id"] in seen:
                    raise Invalid("reply cycle")
                seen.add(cursor["id"])
                if "reply_to" not in cursor:
                    break
                cursor = target(cursor, "reply_to")
        if meta["kind"] == "receipt":
            parent = target(meta, "reply_to")
            if meta["from_agent"] != parent["to_agent"] or meta["to_agent"] != parent["from_agent"]:
                raise Invalid("receipt must reverse sender and recipient")
            if "challenge" in parent and meta.get("challenge") != parent["challenge"]:
                raise Invalid("challenge mismatch")
        if meta["kind"] == "task":
            if meta["idempotency_key"] in keys:
                raise Invalid("duplicate task idempotency key")
            keys.add(meta["idempotency_key"])
        if meta["kind"] == "task_event":
            task = target(meta, "task_id", "task")
            if meta["from_agent"] != task["to_agent"] or meta["to_agent"] != task["from_agent"]:
                raise Invalid("task event author must be assigned executor")
            if meta["thread_id"] != task["thread_id"]:
                raise Invalid("task event crosses threads")
            if timestamp(meta["created_at"]) > timestamp(task["expires_at"]):
                raise Invalid("event after task expiry")
        if meta["kind"] == "memory_review":
            memory = target(meta, "memory_id", "memory")
            if meta["thread_id"] != memory["thread_id"]:
                raise Invalid("review crosses threads")
            if timestamp(meta["reviewed_at"]) < timestamp(memory["created_at"]):
                raise Invalid("review predates proposal")
        if meta["kind"] == "memory" and "supersedes_id" in meta:
            previous = target(meta, "supersedes_id", "memory")
            if timestamp(meta["created_at"]) <= timestamp(previous["created_at"]):
                raise Invalid("replacement must follow original memory")
    for task, _ in documents.values():
        if task["kind"] != "task":
            continue
        status, previous = "pending", task["id"]
        events = sorted((m for m, _ in documents.values() if m["kind"] == "task_event" and
                         m["task_id"] == task["id"]), key=lambda m: m["revision"])
        for revision, event in enumerate(events, 1):
            if event["revision"] != revision or event["reply_to"] != previous:
                raise Invalid("task fork, missing revision, or broken event chain")
            if event["status"] not in TRANSITIONS[status]:
                raise Invalid(f"illegal transition {status} -> {event['status']}")
            status, previous = event["status"], event["id"]
    reviewed = set()
    for meta, _ in documents.values():
        if meta["kind"] == "memory_review":
            if meta["memory_id"] in reviewed:
                raise Invalid("conflicting memory reviews; propose a new version")
            reviewed.add(meta["memory_id"])


def queue(documents, agent, now=None):
    now = now or datetime.now(timezone.utc)
    rows = []
    for task, _ in documents.values():
        if task["kind"] != "task" or task["to_agent"] != agent:
            continue
        events = [m for m, _ in documents.values() if m["kind"] == "task_event" and m["task_id"] == task["id"]]
        status = max(events, key=lambda m: m["revision"])["status"] if events else "pending"
        rows.append({"task_id": task["id"], "status": status,
                     "expired": timestamp(task["expires_at"]) <= now, "objective": task["objective"]})
    return sorted(rows, key=lambda row: row["task_id"])


def confirmed_memories(documents):
    approved = {m["memory_id"] for m, _ in documents.values()
                if m["kind"] == "memory_review" and m["decision"] == "confirmed"}
    replaced = {m["supersedes_id"] for m, _ in documents.values()
                if m["kind"] == "memory" and m["id"] in approved and "supersedes_id" in m}
    return [m for m, _ in documents.values() if m["kind"] == "memory" and
            m["id"] in approved and m["id"] not in replaced]
