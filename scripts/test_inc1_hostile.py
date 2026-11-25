import os
import subprocess
import sys
import time
import unittest

import test_rule_copies as base
from inc1_support import RUN_TIME_BOUND_SECONDS, SkillsCopy

class HostileFiles(SkillsCopy):
    def run_timed(self, *paths):
        started = time.monotonic()
        result = self.check(*paths)
        return result, time.monotonic() - started

    def test_t_l1_11_unreadable_files_never_make_the_run_clean(self):
        self.put("docs/ok.md", "# Fine\n")
        (self.repo / "docs" / "utf16.md").write_bytes("# T\n".encode("utf-16"))
        os.symlink("/nonexistent/target", self.repo / "docs" / "dangling.md")
        (self.repo / "docs" / "latin.md").write_bytes(b"caf\xe9 \xff\xfe")
        (code, output, _), _ = self.run_timed("docs")
        self.assertEqual(code, 1)
        for name in ("utf16.md", "dangling.md", "latin.md"):
            self.assertRegex(output, rf"docs/{name}: UNREADABLE")

    def test_t_l1_11_a_copy_next_to_an_unreadable_file_is_still_reported(self):
        self.put("docs/copy.md", "up to 3 critic rounds\n")
        (self.repo / "docs" / "bad.md").write_bytes(b"\xff\xfe\x00")
        _, output, _ = self.check("docs")
        self.assertIn("docs/copy.md:1: RC-1", output)
        self.assertIn("docs/bad.md: UNREADABLE", output)

    def test_t_l1_11_file_with_bom_keeps_line_numbers(self):
        (self.repo / "docs" / "bom.md").write_bytes("﻿# T\n\nup to 3 critic rounds\n".encode("utf-8"))
        _, output, _ = self.check("docs")
        self.assertIn("docs/bom.md:3: RC-1", output)

    @unittest.skipIf(os.geteuid() == 0, "root reads every file")
    def test_t_l1_11_permission_denied_is_unreadable(self):
        path = self.repo / "docs" / "locked.md"
        path.write_text("x\n", encoding="utf-8")
        path.chmod(0)
        self.addCleanup(path.chmod, 0o600)
        code, output, _ = self.check("docs")
        self.assertEqual(code, 1)
        self.assertIn("docs/locked.md: UNREADABLE", output)

    def test_t_l1_11_large_and_table_heavy_files_finish_within_the_bound(self):
        self.put("docs/table.md", "| a | b | c |\n|---|---|---|\n" * 100000)
        self.put("docs/line.md", "x " * 2000000)
        self.put("docs/repeat.md", "hard " * 100000 + "a raise by " * 50000)
        (code, _, _), seconds = self.run_timed("docs")
        self.assertEqual(code, 0)
        self.assertLess(seconds, RUN_TIME_BOUND_SECONDS)

    def test_t_l1_11_hard_stop_repeated_many_times_is_reported_once_each(self):
        self.put("docs/many.md", "hard stop. " * 20000)
        (code, output, _), seconds = self.run_timed("docs")
        self.assertEqual(code, 1)
        self.assertIn("20000 restated copies", output)
        self.assertLess(seconds, RUN_TIME_BOUND_SECONDS)

    @unittest.expectedFailure
    def test_td_5_a_fifo_named_like_markdown_does_not_hang(self):
        os.mkfifo(self.repo / "docs" / "pipe.md")
        command = [sys.executable, str(base.SCRIPT), "--repo", str(self.repo), "docs"]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=10)
        self.assertEqual(completed.returncode, 1)


class RunTime(SkillsCopy):
    def scale(self, factor):
        for path in (self.repo / "skills").rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            path.write_text("\n".join([text] * factor), encoding="utf-8")

    def seconds(self):
        started = time.monotonic()
        base.run_check(self.repo, "skills")
        return time.monotonic() - started

    def test_t_l1_13_repo_and_ten_times_the_text_finish_within_the_bound(self):
        normal = self.seconds()
        self.scale(10)
        scaled = self.seconds()
        print(f"\nT-L1-13 skills: {normal:.2f} s, 10x text: {scaled:.2f} s", file=sys.stderr)
        self.assertLess(scaled, RUN_TIME_BOUND_SECONDS)

if __name__ == "__main__":
    unittest.main()
