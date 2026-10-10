# Personal AI OS

**A user-controlled file bridge for asynchronous collaboration between consumer AI assistants.**

[中文](README.zh-CN.md) · [Protocol](docs/PROTOCOL.md) · [Architecture](docs/ARCHITECTURE.md) · [Security](SECURITY.md)

ChatGPT and Meta Muse can exchange independent Markdown messages through a private Google Drive workspace when the user has an available, authorized connector, or through manual file transfer. The user reviews shared memory and approves external actions. This repository provides the format, offline tools, and a reproducible synthetic demo.

This is an unofficial community project, not an operating system or an integration endorsed by OpenAI, Meta, or Google. Product names identify possible participants; availability and permissions vary by account.

## What ships in v0.1

| Capability | Status |
|---|---|
| Immutable Markdown messages and linked receipts | Implemented locally |
| Challenge echo, references, task revisions and conflict validation | Implemented |
| Assigned task queue and expiration display | Implemented; no task execution |
| Pending memory proposals and human review records | Implemented; identity is not authenticated |
| Windows 11 optional validation Worker | Implemented as an offline, one-shot CLI |
| Google Drive transport | User-managed connector/manual upload; no OAuth client in this repo |
| Native automatic ChatGPT ↔ Muse connection | Not implemented |
| Real-time Drive listener, waking another AI, native internal memory sync | Not implemented |
| Muse scheduled polling | Account-specific experiment, not verified by this software |

The motivating private experiment reported user-triggered reading, independent file creation, and readback. Private records are deliberately excluded. Those reports do not prove always-on operation or general availability. The public demo simulates both participants without contacting either service.

## Run the offline demo

Requires Python 3.10+. Runtime uses only the standard library. From a downloaded or cloned copy of this repository:

```sh
python -m paos.demo workspace/demo
python -m paos validate workspace/demo
python -m paos queue workspace/demo --agent muse_demo
python -m paos memories workspace/demo
python -m unittest discover -s tests -v
```

On Windows, use `py -3` instead of `python` if needed. The generator requires a new directory and produces eight fictional documents: registration, message, receipt, task, claim, completion, memory proposal, and human review. Timestamps are intentionally in 2030; queue output marks them expired after that date.

Optional installation: `python -m pip install .` exposes the equivalent `paos` command. Distribution name is `personal-ai-os-filebridge`; repository name is `personal-ai-os`. No PyPI release is claimed.

## Use with Google Drive

1. Create a private, dedicated workspace with only non-sensitive test material. Keep this public source repository separate from your working data.
2. Register each participant as pending. Independently check its actual connector permissions and supported read/write operations. If no connector exists, use manual file transfer and record that limitation.
3. Send a fresh non-secret challenge in a message. Request a new receipt with reversed sender/recipient and the exact challenge. Read back both files and verify the original was unchanged. A challenge echo proves possession of text, not account identity.
4. After user approval, record the agent as active. Assign one executor per task. Upload each message/event as a new file; never overwrite another participant's file.
5. Download a complete snapshot into a separate local folder and validate it. Missing predecessors fail validation. Compare file bytes or hashes after upload; Drive can contain multiple files with the same name, so inspect document IDs as well.
6. Keep memory pending until the user authors a separate review record. Use `memories` to export only confirmed, unsuperseded proposals.

The CLI does not upload files, authorize connectors, or send messages. To create an envelope from JSON metadata and an optional text body:

```sh
python -m paos create workspace/demo --metadata new-message.json --body message.txt
```

See [the onboarding prompt](docs/ONBOARDING.md), [protocol fields](docs/PROTOCOL.md), and [Windows instructions](docs/WINDOWS_WORKER.md). Use the existing synthetic Markdown files as templates; replace IDs and timestamps, and omit fictional challenge values from real tests.

## Design choices and limits

Each record has a unique ID, author, recipient, thread, and timestamp. Tasks remain immutable; the assigned executor emits separate events. Validation rejects forks and missing revisions rather than guessing which writer won. Local exclusive creation prevents overwriting a filename, but snapshots and Drive synchronization do not provide distributed locking. Use a transactional queue before enabling concurrent workers or external side effects.

Allowed-action strings and `human` author labels are declarations. They are not authentication, a permission boundary, or proof of approval. A malicious writer can forge them. Validate provenance through the user's actual product session and access controls. This code never executes document content.

## Contribute

Read [CONTRIBUTING.md](CONTRIBUTING.md), run the tests, and keep all fixtures synthetic. Future adapters must document actual authentication, revocation, conflict handling, and evidence of readback. Priorities: schema export, connector-specific manual recipes, and authenticated review provenance. Automatic execution requires a separate threat model and transaction design.

MIT licensed. See [LICENSE](LICENSE). Conceptual inspiration includes shared-blackboard systems and [agent-handoff-kit](https://github.com/jimozo/agent-handoff-kit); no third-party implementation has been copied or security-audited here.
