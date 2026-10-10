import argparse
import json
import sys
from pathlib import Path
from .core import Invalid, load, queue, confirmed_memories, write, audit


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline Markdown handoff tools; no cloud access or task execution")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "queue", "memories", "worker"):
        command = sub.add_parser(name)
        command.add_argument("workspace", type=Path)
        if name == "queue":
            command.add_argument("--agent", required=True)
        if name == "worker":
            command.add_argument("--report", required=True, type=Path)
    create = sub.add_parser("create")
    create.add_argument("workspace", type=Path)
    create.add_argument("--metadata", required=True, type=Path)
    create.add_argument("--body", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "create":
            if not args.workspace.is_dir():
                raise Invalid("workspace must be an existing directory")
            documents = load(args.workspace)
            meta = json.loads(args.metadata.read_text(encoding="utf-8"))
            from .core import validate
            validate(meta)
            if meta["id"] in documents:
                raise Invalid("document id already exists")
            body = args.body.read_text(encoding="utf-8") if args.body else ""
            documents[meta["id"]] = (meta, body)
            audit(documents)
            print(write(args.workspace, meta, body))
            return 0
        if not args.workspace.is_dir():
            raise Invalid("workspace must be an existing directory")
        documents = load(args.workspace)
        if args.command == "validate":
            print(f"Valid: {len(documents)} documents")
        elif args.command == "queue":
            print(json.dumps(queue(documents, args.agent), ensure_ascii=False, indent=2))
        elif args.command == "memories":
            print(json.dumps(confirmed_memories(documents), ensure_ascii=False, indent=2))
        elif args.command == "worker":
            # A separate local report; never write into a synced inbox.
            report = args.report.resolve()
            if report.is_relative_to(args.workspace.resolve()):
                raise Invalid("report must be outside workspace")
            report.parent.mkdir(parents=True, exist_ok=True)
            payload = {"mode": "validation-only", "document_count": len(documents),
                       "confirmed_memory_count": len(confirmed_memories(documents))}
            with report.open("x", encoding="utf-8") as stream:
                json.dump(payload, stream, indent=2)
            print(report)
        return 0
    except (Invalid, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
