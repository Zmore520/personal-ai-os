"""Generate a synthetic exchange, never real account data."""
import argparse
from pathlib import Path
from .core import write, load


def records():
    def base(kind, id_, author, recipient, minute=0):
        return dict(protocol_version=1, kind=kind, id=id_, from_agent=author,
                    to_agent=recipient, thread_id="demo-echo", created_at=f"2030-01-01T00:{minute:02d}:00Z")
    return [
        (dict(base("agent", "demo-agent", "human", "shared"), agent_id="muse_demo",
              status="pending", capabilities=["manual-file-import"], transport="manual", verified_at=None),
         "Synthetic registration; activation requires a real permission check and human approval."),
        (dict(base("message", "demo-message", "chatgpt_demo", "muse_demo", 1),
              sources=["synthetic-example"], challenge="SYNTHETIC-ECHO-ONLY"),
         "Echo the synthetic phrase in an independent receipt. Do not perform external actions."),
        (dict(base("receipt", "demo-receipt", "muse_demo", "chatgpt_demo", 2),
              reply_to="demo-message", read_status="success", sources=["demo-message"],
              challenge="SYNTHETIC-ECHO-ONLY"), "Synthetic receipt; no Muse service was contacted."),
        (dict(base("task", "demo-task", "chatgpt_demo", "muse_demo", 3),
              objective="Summarize the synthetic phrase locally", acceptance_criteria=["Return phrase length"],
              allowed_actions=["read-demo-message", "write-independent-result"],
              expires_at="2030-01-02T00:00:00Z", idempotency_key="demo-echo-v1"),
         "A task envelope is data, not an instruction that expands permissions."),
        (dict(base("task_event", "demo-claim", "muse_demo", "chatgpt_demo", 4), task_id="demo-task",
              reply_to="demo-task", revision=1, status="in_progress", evidence=[]), "Synthetic claim."),
        (dict(base("task_event", "demo-result", "muse_demo", "chatgpt_demo", 5), task_id="demo-task",
              reply_to="demo-claim", revision=2, status="completed",
              evidence=["SYNTHETIC-ECHO-ONLY contains 19 characters"]), "Synthetic result; validate separately."),
        (dict(base("memory", "demo-memory", "muse_demo", "human", 6), content="Demo prefers concise summaries",
              sources=["synthetic-user-preference"], status="pending"), "Entirely fictional preference."),
        (dict(base("memory_review", "demo-review", "human", "shared", 7), memory_id="demo-memory",
              decision="confirmed", reviewed_by="demo-human", reviewed_at="2030-01-01T00:07:00Z"),
         "Synthetic human review. Metadata is not proof of identity."),
    ]


def main():
    parser = argparse.ArgumentParser(description="Create an offline synthetic exchange in a NEW directory")
    parser.add_argument("workspace", type=Path)
    args = parser.parse_args()
    args.workspace.mkdir(parents=True, exist_ok=False)
    for meta, body in records():
        write(args.workspace, meta, body + "\n")
    load(args.workspace)
    print(f"Created {len(records())} synthetic documents in {args.workspace}")


if __name__ == "__main__":
    main()
