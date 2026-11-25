import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("rule_copies.py")
REPOSITORY = Path(__file__).resolve().parent.parent
CAP_SOURCE = "skills/feature/protocols/review-cycle.md"

SOURCE_TEXT = """# Review

## Levels

R1 runs one critic.

## The cycle

Stop when the feature has had 3 critic rounds in total.

## Later

Something else.
"""

RULES = {
    "scan": {"paths": ["."], "exclude": ["ignored/*"]},
    "rules": [{
        "id": "CAP",
        "source": {"file": "protocols/review.md", "section": "The cycle"},
        "fingerprints": [r"\b(?P<value>\d+|three|four) critic rounds\b", r"\bcap of (?P<value>\d+)\b"],
    }],
}


def run_check(repo, *arguments, rules=None):
    command = [sys.executable, str(SCRIPT), "--repo", str(repo)]
    command += ["--rules", str(rules)] if rules else []
    completed = subprocess.run(command + list(arguments), capture_output=True, text=True, timeout=120)
    return completed.returncode, completed.stdout, completed.stderr


class ScratchRepository(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp(prefix="rule-copies-"))
        self.addCleanup(shutil.rmtree, self.repo, ignore_errors=True)
        self.rules = self.repo / "rules.json"
        self.rules.write_text(json.dumps(RULES), encoding="utf-8")
        self.write("protocols/review.md", SOURCE_TEXT)

    def write(self, relative, text):
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def check(self, *arguments):
        return run_check(self.repo, *arguments, rules=self.rules)


class SourceAndPointers(ScratchRepository):
    def test_source_alone_reports_nothing(self):
        code, output, _ = self.check()
        self.assertEqual(code, 0)
        self.assertIn("0 restated copies", output)

    def test_pointer_and_bare_name_are_not_copies(self):
        self.write("workflows/sdd.md", "Review within the round cap (`protocols/review.md` §The cycle).\n\nThe critic rounds are logged.\n")
        code, output, _ = self.check()
        self.assertEqual(code, 0, output)

    def test_value_changed_at_source_reports_disagreeing_copy(self):
        self.write("workflows/sdd.md", "Intro.\n\nA new critic, within the cap of 3 critic rounds.\n")
        self.write("protocols/review.md", SOURCE_TEXT.replace("3 critic rounds", "4 critic rounds"))
        code, output, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("workflows/sdd.md:3: CAP restated copy", output)
        self.assertIn("DISAGREES: source says 4", output)

    def test_same_file_outside_the_source_section_is_a_copy(self):
        self.write("protocols/review.md", SOURCE_TEXT.replace("Something else.", "Up to three critic rounds."))
        code, output, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("protocols/review.md:13: CAP", output)

    def test_overlapping_fingerprints_report_one_copy(self):
        self.write("notes.md", "Within the cap of 3 critic rounds.\n")
        _, output, _ = self.check()
        self.assertEqual(output.count("notes.md:1:"), 1, output)


class InjectedRestatements(ScratchRepository):
    def test_restatement_in_each_kind_of_file_is_reported_with_its_line(self):
        for relative in ("README.md", "docs/architecture.md", "skills/feature-kit/SKILL.md"):
            self.write(relative, "Title\n\nThe review stops after three critic rounds.\n")
        code, output, _ = self.check()
        self.assertEqual(code, 1)
        for relative in ("README.md", "docs/architecture.md", "skills/feature-kit/SKILL.md"):
            self.assertIn(f"{relative}:3: CAP restated copy", output)

    def test_reflowed_emphasized_and_uppercase_copy_is_reported_at_its_first_line(self):
        self.write("guide.md", "Text.\nThe review stops after **3**\n   CRITIC\nrounds.\n")
        code, output, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("guide.md:2: CAP", output)

    def test_crlf_line_endings_keep_line_numbers(self):
        (self.repo / "windows.md").write_bytes(b"One\r\nTwo\r\nCap of 3 here.\r\n")
        _, output, _ = self.check()
        self.assertIn("windows.md:3: CAP", output)

    def test_excluded_and_non_markdown_files_are_skipped(self):
        self.write("ignored/old.md", "3 critic rounds\n")
        self.write("notes.txt", "3 critic rounds\n")
        code, output, _ = self.check()
        self.assertEqual(code, 0, output)

    def test_explicit_paths_limit_the_scan(self):
        self.write("docs/a.md", "3 critic rounds\n")
        code, output, _ = self.check("protocols")
        self.assertEqual(code, 0, output)


class HostileFiles(ScratchRepository):
    def test_empty_file_is_clean(self):
        self.write("empty.md", "")
        code, _, _ = self.check()
        self.assertEqual(code, 0)

    def test_non_utf8_file_is_reported_unreadable(self):
        (self.repo / "latin.md").write_bytes("cap of 3 caf\xe9".encode("latin-1"))
        code, output, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("latin.md: UNREADABLE (not UTF-8", output)

    def test_binary_file_is_reported_unreadable(self):
        (self.repo / "blob.md").write_bytes(b"\x00\x01cap of 3")
        code, output, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("blob.md: UNREADABLE (binary content)", output)

    @unittest.skipUnless(hasattr(os, "symlink"), "needs symlinks")
    def test_symlink_loops_do_not_hang(self):
        os.symlink(self.repo / "loop.md", self.repo / "loop.md")
        os.symlink(self.repo, self.repo / "protocols" / "back")
        code, output, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("loop.md: UNREADABLE", output)

    def test_very_long_line_is_scanned(self):
        self.write("long.md", "word " * 200000 + "cap of 3\n")
        code, output, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("long.md:1: CAP", output)

    @unittest.skipIf(os.name != "posix" or os.geteuid() == 0, "needs POSIX permissions and a non-root user")
    def test_unlistable_folder_is_reported_unreadable(self):
        locked = self.write("locked/inner.md", "cap of 3\n").parent
        locked.chmod(0)
        self.addCleanup(locked.chmod, 0o755)
        code, output, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("locked: UNREADABLE", output)

    def test_missing_path_is_reported_not_clean(self):
        code, output, _ = self.check("nowhere")
        self.assertEqual(code, 1)
        self.assertIn("nowhere: UNREADABLE (not found)", output)


class ConfigurationErrors(ScratchRepository):
    def test_missing_source_section_is_a_configuration_error(self):
        self.write("protocols/review.md", "# Review\n\nNo cycle here.\n")
        code, _, error = self.check()
        self.assertEqual(code, 2)
        self.assertIn("section 'The cycle' not found", error)

    def test_heading_inside_a_code_fence_does_not_end_the_section(self):
        fenced = SOURCE_TEXT.replace("Stop when", "```\n# not a heading\n```\nStop when")
        self.write("protocols/review.md", fenced)
        code, output, _ = self.check()
        self.assertEqual(code, 0, output)

    def test_invalid_rules_file_is_a_configuration_error(self):
        self.rules.write_text("{not json", encoding="utf-8")
        code, _, error = self.check()
        self.assertEqual(code, 2)
        self.assertIn("cannot load rules", error)

    def test_invalid_fingerprint_is_a_configuration_error(self):
        broken = json.loads(json.dumps(RULES))
        broken["rules"][0]["fingerprints"] = ["(unclosed"]
        self.rules.write_text(json.dumps(broken), encoding="utf-8")
        code, _, error = self.check()
        self.assertEqual(code, 2)
        self.assertIn("invalid fingerprint", error)


class RepositoryRules(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp(prefix="rule-copies-repo-"))
        self.addCleanup(shutil.rmtree, self.repo, ignore_errors=True)
        shutil.copytree(REPOSITORY / "skills", self.repo / "skills")

    def edit(self, relative, old, new):
        path = self.repo / relative
        text = path.read_text(encoding="utf-8")
        self.assertEqual(text.count(old), 1, f"{old!r} in {relative}")
        path.write_text(text.replace(old, new), encoding="utf-8")

    def test_skills_have_no_copies_of_the_consolidated_rules(self):
        code, output, _ = run_check(self.repo, "skills")
        self.assertEqual(code, 0, output)

    def test_changing_the_cap_at_its_source_reports_nothing_when_only_pointers_exist(self):
        self.edit(CAP_SOURCE, "3 critic rounds in total", "4 critic rounds in total")
        code, output, _ = run_check(self.repo, "skills")
        self.assertEqual(code, 0, output)

    def test_changed_cap_reports_an_older_copy_as_disagreeing(self):
        self.edit(CAP_SOURCE, "3 critic rounds in total", "4 critic rounds in total")
        self.edit("skills/feature/workflows/sdd.md", "within the round cap (", "within the cap of 3 critic rounds (")
        code, output, _ = run_check(self.repo, "skills")
        self.assertEqual(code, 1)
        self.assertRegex(output, r"skills/feature/workflows/sdd\.md:\d+: RC-1 .*DISAGREES: source says 4")

    def test_hard_stop_named_without_a_pointer_is_reported(self):
        self.edit("skills/feature/workflows/direct.md", "(hard stop: `protocols/gates.md` §Hard stops)", "(hard stop)")
        code, output, _ = run_check(self.repo, "skills")
        self.assertEqual(code, 1)
        self.assertIn("skills/feature/workflows/direct.md", output)
        self.assertIn("HS-2", output)

    def test_hard_stop_condition_restated_is_reported(self):
        self.edit("skills/feature/protocols/multi-feature.md", "integration is a hard stop (`protocols/gates.md` §Hard stops).",
                  "integration stops the feature in every profile.")
        code, output, _ = run_check(self.repo, "skills")
        self.assertEqual(code, 1)
        self.assertIn("HS-1", output)


if __name__ == "__main__":
    unittest.main()
