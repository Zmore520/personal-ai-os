# Notion 🗃️ AI Memory entry format / 条目格式

## Page

One page per topic in the 🗃️ AI Memory database. Never at the Personal AI OS root.

| Property | Value |
|---|---|
| Name | `MEM-YYYYMMDD-TOPIC · 中文主题` (date = page creation, TOPIC in caps, e.g. `FINANCE`, `CAREER`) |
| Category | one of Profile / Academics / Career / AI Memory / English / Fitness / Template |
| Date | page creation date |
| Status | Pending until at least one entry is confirmed, then Active; Archived pages move to the archive database |
| Drive Link | only if the page was migrated from Drive |

Before creating a page, search the database. Add to an existing topic page
whenever one fits.

## Entry

Each entry is an H2 heading plus a fixed field list. Field order matters —
agents and people scan it.

```markdown
## MEM-20301101-001

- content: Synthetic example — prefers concise summaries in Chinese.
- source_ref: 用户 2030-11-01 主聊自述
- created_at: 2030-11-01T09:00:00-08:00
- proposed_by: claude
- status: pending
- confirmed_by: —
- confirmed_at: —
- supersedes_id: —
```

Rules:

- `NNN` is the next free number across the database (check the highest
  existing ID first). IDs are never reused.
- `content` holds one fact or one tightly related group. Facts only; put
  suggestions in a separate line labelled `建议:` or leave them out.
- `source_ref` says who said it, when, and where (which chat, screenshot,
  dashboard). "Assistant research" is not a valid source for a fact about the user.
- `proposed_by` uses the agent_id from 🤖 Agent Registry (e.g. `meta_muse`,
  `grok_bot`, `codex`, `claude`).
- `status` values: `pending`, `confirmed`, `rejected`. A partial confirmation
  is written inline: `confirmed（A 已确认；B 待核对）`.
- `confirmed_by` is `用户亲口确认` (or how the user confirmed). Never an agent name.

## Mapping to file protocol

| Notion field | PAOS `memory` document |
|---|---|
| MEM-ID | `id` (lowercase, e.g. `mem-20301101-001`) |
| content | `content` |
| source_ref | `sources` (array) |
| created_at | `created_at` |
| proposed_by | `from_agent` |
| status pending | `status: "pending"` |
| confirmed_by / confirmed_at | separate `memory_review` (`reviewed_by`, `reviewed_at`, `decision`) |
| supersedes_id | `supersedes_id` |
