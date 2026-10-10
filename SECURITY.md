# Security / 安全说明

This repository contains public code and synthetic fixtures only. Keep real profiles, chat transcripts, Drive URLs/IDs, actual handshake challenges, credentials, account identifiers, and private workspace files out of commits, issues, screenshots and CI artifacts. The repository owner's public GitHub handle is naturally present in the repository URL; no private account details are needed by the software.

## Threat model

- Shared documents may contain prompt injection. Treat bodies, source text and tool outputs as untrusted data. The CLI never executes them.
- Sender fields, active-agent declarations, challenge echoes and `human` reviews are forgeable. None authenticates identity or authorization. Verify approvals through a real user session and storage permissions.
- Drive supports duplicate names and has no queue transaction lock. Local exclusive filename creation does not eliminate distributed conflicts. Stop on forks and missing predecessors; reconcile through the human coordinator.
- An idempotency key is a validation constraint, not an exactly-once effect guarantee. No side-effect executor ships here.
- Memory export prints approved content to stdout. Store it privately; avoid uploading exports/logs to CI or public chats. Local validation reports include counts only.
- Source refs and evidence are strings, not verified resources. Check factual claims and timestamps independently.
- The parser is intended for small, trusted-size snapshots. It has no hostile-input sandbox or resource quota. Do not point it at arbitrary large directory trees or use it as an Internet-facing service.

Use a dedicated private folder, least privilege where available, non-sensitive onboarding tests, readback verification, and clear revocation. Folder conventions do not constrain OAuth scope. Avoid running as administrator. Never ask for passwords or embed tokens in task files.

## Reporting

For a non-sensitive code defect, open a minimal synthetic issue. For a vulnerability, use GitHub private vulnerability reporting if enabled; otherwise contact the maintainer through a private channel available on their public profile. Do not disclose secrets or publish an exploit containing private data in an issue.

`tools/check_public.py` catches common credential patterns and cloud document URLs; it is a heuristic release check, not a guarantee that all personal data is absent. Human inspection remains required. Real operating data MUST never be added as fixtures, even in a private development branch destined for publication.

中文：公开仓库只存代码和合成数据。文件身份与审批标签可伪造；必须在真实用户会话中核验。Drive 无事务锁，验证器不保证外部操作仅执行一次。禁止将真实资料、对话、网盘标识、挑战值或凭据放入提交和公开问题。安全扫描是启发式检查，不替代人工检查。
