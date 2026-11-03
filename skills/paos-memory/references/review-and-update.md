# Review and update / 审核与更新

## Review checklist

Run this before asking the user to confirm. Report pass/fail; the user decides.

1. **Stated** — `source_ref` points to the user's own words or material.
2. **Durable** — useful in a month, not one day's task status.
3. **Right page** — topic page in AI Memory; not the top level; no duplicate topic page.
4. **Not duplicate** — no existing entry already says it.
5. **Allowed** — nothing from the never-store list.
6. **Calibrated** — "mentioned once" is not written as a habit; partial facts keep their gaps (`数量和成本未提供`).
7. **Consistent** — `source_ref` matches `content`; no contradiction with other confirmed entries.

## Update patterns

### Same fact, new detail

```markdown
## MEM-20301101-002

- content: Synthetic example — holds fund AAA.
- 更新于 2030-11-05（用户确认）：also holds fund BBB; amounts not provided.
- source_ref: 用户 2030-11-01 截图；2030-11-05 主聊补充
- …
```

### Fact no longer true

Strike the old text and add the new state in the same entry when it is the
same subject:

```markdown
- content（已被取代，2030-11-08）：~~plans to open a brokerage account~~
- 更新于 2030-11-08（用户确认）：account opened.
```

### Real replacement

Create a new entry with `supersedes_id: MEM-…-002`. Leave the old entry in
place. Readers follow the newest confirmed entry.

### Conflicting records

```markdown
- 更新于 2030-11-09：dashboard says class A share, chat said class C — 待用户核对
```

Ask the user. Don't choose.

## File-protocol equivalents

- Changed decision → new `memory` proposal (optionally with `supersedes_id`)
  plus a fresh human `memory_review`. Two reviews for one proposal fail validation.
- Only confirmed, unsuperseded proposals appear in `python -m paos memories`.
- `from_agent: "human"` is a format check, not proof. Verify the user's
  approval in the actual chat.

## Mirroring

The note store is primary. When the user asks for a backup, copy finished
entries to the backup location as **new** files; existing backup files are not
edited, moved or deleted. Don't keep two writable copies of the same entry.
