import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from paos.core import Invalid, audit, decode, encode, write, load, queue, confirmed_memories
from paos.demo import records
from paos.__main__ import main


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.docs = {m["id"]: (copy.deepcopy(m), body) for m, body in records()}

    def invalid(self, id_, **changes):
        self.docs[id_][0].update(changes)
        with self.assertRaises(Invalid):
            # Workspace validation includes structural and semantic checks.
            for meta, body in self.docs.values():
                decode(encode(meta, body))
            audit(self.docs)

    def test_roundtrip_unicode(self):
        meta, _ = self.docs["demo-message"]
        self.assertEqual(decode(encode(meta, "你好\n```json\n{}\n```")), (meta, "你好\n```json\n{}\n```"))

    def test_full_exchange(self):
        audit(self.docs)
        self.assertEqual(confirmed_memories(self.docs)[0]["id"], "demo-memory")
        result = queue(self.docs, "muse_demo", datetime(2030, 1, 1, tzinfo=timezone.utc))
        self.assertEqual(result[0]["status"], "completed")
        self.assertFalse(result[0]["expired"])
        self.assertEqual(queue(self.docs, "other"), [])

    def test_expired_queue(self):
        self.assertTrue(queue(self.docs, "muse_demo", datetime(2031, 1, 1, tzinfo=timezone.utc))[0]["expired"])

    def test_mismatch_challenge(self):
        self.invalid("demo-receipt", challenge="wrong")

    def test_wrong_receipt_author(self):
        self.invalid("demo-receipt", from_agent="other")

    def test_dangling_reply(self):
        self.invalid("demo-receipt", reply_to="missing")

    def test_wrong_executor(self):
        self.invalid("demo-claim", from_agent="other")

    def test_completion_without_evidence(self):
        self.invalid("demo-result", evidence=[])

    def test_revision_gap(self):
        self.invalid("demo-result", revision=3)

    def test_revision_fork(self):
        extra = copy.deepcopy(self.docs["demo-claim"][0])
        extra["id"] = "duplicate-claim"
        self.docs[extra["id"]] = (extra, "")
        with self.assertRaises(Invalid):
            audit(self.docs)

    def test_terminal_reentry(self):
        extra = copy.deepcopy(self.docs["demo-result"][0])
        extra.update(id="demo-reopen", revision=3, reply_to="demo-result", status="in_progress")
        self.docs[extra["id"]] = (extra, "")
        with self.assertRaises(Invalid):
            audit(self.docs)

    def test_expired_event(self):
        self.invalid("demo-result", created_at="2031-01-01T00:00:00Z")

    def test_cross_thread(self):
        self.invalid("demo-claim", thread_id="other-thread")

    def test_ai_cannot_confirm(self):
        self.invalid("demo-review", from_agent="muse_demo")

    def test_unreviewed_memory_excluded(self):
        del self.docs["demo-review"]
        self.assertEqual(confirmed_memories(self.docs), [])

    def test_new_memory_cannot_self_confirm(self):
        self.invalid("demo-memory", status="confirmed")

    def test_conflicting_reviews(self):
        extra = copy.deepcopy(self.docs["demo-review"][0])
        extra.update(id="demo-reject", decision="rejected")
        self.docs[extra["id"]] = (extra, "")
        with self.assertRaises(Invalid):
            audit(self.docs)

    def test_review_before_proposal(self):
        self.invalid("demo-review", reviewed_at="2029-01-01T00:00:00Z")

    def test_duplicate_idempotency(self):
        extra = copy.deepcopy(self.docs["demo-task"][0])
        extra["id"] = "task-retry"
        self.docs[extra["id"]] = (extra, "")
        with self.assertRaises(Invalid):
            audit(self.docs)

    def test_path_traversal(self):
        self.invalid("demo-message", id="../escape")

    def test_timezone_required(self):
        self.invalid("demo-message", created_at="2030-01-01T00:00:00")

    def test_bool_revision(self):
        self.invalid("demo-claim", revision=True)

    def test_bool_protocol_version(self):
        self.invalid("demo-message", protocol_version=True)

    def test_invalid_list(self):
        self.invalid("demo-message", sources="not-array")

    def test_empty_acceptance(self):
        self.invalid("demo-task", acceptance_criteria=[])

    def test_duplicate_json_keys(self):
        text = encode(self.docs["demo-message"][0]).replace('"kind": "message",', '"kind": "message", "kind": "task",')
        with self.assertRaises(Invalid):
            decode(text)

    def test_cycle(self):
        self.docs["demo-message"][0]["reply_to"] = "demo-receipt"
        self.docs["demo-message"][0]["created_at"] = "2030-01-01T00:02:00Z"
        with self.assertRaises(Invalid):
            audit(self.docs)

    def test_active_registration_needs_verification(self):
        self.invalid("demo-agent", status="active")

    def test_immutable_create_and_readback(self):
        with tempfile.TemporaryDirectory() as folder:
            meta, body = self.docs["demo-message"]
            path = write(folder, meta, body)
            original = path.read_bytes()
            with self.assertRaises(FileExistsError):
                write(folder, meta, "overwrite")
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(load(folder)[meta["id"]][0], meta)

    def test_duplicate_document_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            meta, body = self.docs["demo-message"]
            path = write(folder, meta, body)
            (Path(folder) / "copy.md").write_text(path.read_text(), encoding="utf-8")
            with self.assertRaises(Invalid):
                load(folder)

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = write(folder, *self.docs["demo-message"])
            try:
                (Path(folder) / "link.md").symlink_to(path)
            except OSError as exc:
                self.skipTest(f"host lacks symlink permission: {exc}")
            with self.assertRaises(Invalid):
                load(folder)

    def test_worker_and_cli_errors(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "inbox"
            root.mkdir()
            for meta, body in self.docs.values():
                write(root, meta, body)
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(main(["validate", str(root)]), 0)
                report = Path(folder) / "report.json"
                self.assertEqual(main(["worker", str(root), "--report", str(report)]), 0)
                self.assertEqual(json.loads(report.read_text())["mode"], "validation-only")
                self.assertEqual(main(["worker", str(root), "--report", str(report)]), 2)
                self.assertEqual(main(["worker", str(root), "--report", str(root / "report.json")]), 2)
                self.assertEqual(main(["validate", str(Path(folder) / "absent")]), 2)

    def test_rejected_memory(self):
        self.docs["demo-review"][0]["decision"] = "rejected"
        audit(self.docs)
        self.assertEqual(confirmed_memories(self.docs), [])

    def test_confirmed_replacement(self):
        meta = copy.deepcopy(self.docs["demo-memory"][0])
        meta.update(id="memory-v2", supersedes_id="demo-memory", created_at="2030-01-01T00:08:00Z")
        review = copy.deepcopy(self.docs["demo-review"][0])
        review.update(id="review-v2", memory_id="memory-v2", created_at="2030-01-01T00:09:00Z", reviewed_at="2030-01-01T00:09:00Z")
        self.docs[meta["id"]] = (meta, "")
        self.assertEqual(confirmed_memories(self.docs)[0]["id"], "demo-memory")
        self.docs[review["id"]] = (review, "")
        audit(self.docs)
        self.assertEqual([m["id"] for m in confirmed_memories(self.docs)], ["memory-v2"])


if __name__ == "__main__":
    unittest.main()
