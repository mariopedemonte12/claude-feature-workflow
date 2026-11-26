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


class NamesNextToFingerprints(ScratchRepository):
    def test_name_overlapping_a_fingerprint_does_not_hide_it(self):
        rules = {"scan": {"paths": ["."], "exclude": []}, "rules": [{
            "id": "LV", "source": {"file": "protocols/review.md", "section": "Levels"},
            "fingerprints": [r"\br2 critic\b"], "names": [r"\br1/r2\b"],
            "pointer": r"protocols/review\.md"}]}
        self.rules.write_text(json.dumps(rules), encoding="utf-8")
        self.write("notes.md", "R1/R2 critic runs on every change.\n")
        code, output, _ = self.check()
        self.assertEqual(code, 1, output)
        self.assertIn("notes.md:1: LV restated copy", output)
        self.assertIn("r2 critic", output.lower())


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


class RuleFileValidation(ScratchRepository):
    def assert_configuration_error(self, mutate, message):
        broken = json.loads(json.dumps(RULES))
        mutate(broken)
        self.rules.write_text(json.dumps(broken), encoding="utf-8")
        code, _, error = self.check()
        self.assertEqual(code, 2, error)
        self.assertIn(message, error)

    def test_fingerprints_given_as_a_string(self):
        self.assert_configuration_error(lambda data: data["rules"][0].update(fingerprints="abc"), "must be a list of strings")

    def test_empty_fingerprints(self):
        self.assert_configuration_error(lambda data: data["rules"][0].update(fingerprints=[]), "must not be empty")

    def test_scan_paths_given_as_a_string(self):
        self.assert_configuration_error(lambda data: data["scan"].update(paths="protocols"), "scan.paths must be a list")

    def test_duplicated_rule_ids(self):
        self.assert_configuration_error(lambda data: data["rules"].append(dict(data["rules"][0])), "duplicated rule ids: CAP")

    def test_no_rules(self):
        self.assert_configuration_error(lambda data: data.update(rules=[]), "non-empty list")


class MarkupAndLines(ScratchRepository):
    def test_html_emphasis_copy_is_reported(self):
        self.write("notes.md", "Up to <b>3</b> critic rounds.\n")
        code, output, _ = self.check()
        self.assertEqual(code, 1)
        self.assertIn("notes.md:1: CAP", output)

    def test_snake_case_names_are_kept(self):
        self.write("notes.md", "The cap_of_3 setting.\n")
        code, output, _ = self.check()
        self.assertEqual(code, 0, output)

    def test_form_feed_does_not_shift_line_numbers(self):
        (self.repo / "paged.md").write_bytes(b"One\x0cstill one\nCap of 3 here.\n")
        _, output, _ = self.check()
        self.assertIn("paged.md:2: CAP", output)


POINTER_RULES = {
    "scan": {"paths": ["."]},
    "rules": [{
        "id": "STOP",
        "source": {"file": "protocols/gates.md", "section": "Hard stops"},
        "fingerprints": [],
        "names": [r"(?<!§)(?<!§ )\bhard[- ]stops?\b"],
        "pointer": r"protocols/gates\.md ?§ ?hard stops|protocols/gates\.md(?! ?§)|§ ?hard stops",
    }],
}


class PointerWindow(ScratchRepository):
    def setUp(self):
        super().setUp()
        self.rules.write_text(json.dumps(POINTER_RULES), encoding="utf-8")
        self.write("protocols/gates.md", "# Gates\n\n## Hard stops\n\nIntegration.\n")

    def reported(self, line):
        self.write("probe.md", line + "\n")
        code, output, _ = self.check()
        return code == 1 and "probe.md:1: STOP" in output

    @staticmethod
    def gap(characters):
        return " " + "x" * (characters - 2) + " "

    def test_pointer_after_within_sixty_characters(self):
        self.assertFalse(self.reported("a hard stop" + self.gap(60) + "§Hard stops"))

    def test_pointer_after_beyond_sixty_characters(self):
        self.assertTrue(self.reported("a hard stop" + self.gap(61) + "§Hard stops"))

    def test_pointer_before_within_sixty_characters(self):
        self.assertFalse(self.reported("protocols/gates.md" + self.gap(60) + "hard stop here"))

    def test_pointer_before_beyond_sixty_characters(self):
        self.assertTrue(self.reported("protocols/gates.md" + self.gap(61) + "hard stop here"))

    def test_spaced_section_sign_is_a_pointer_not_a_copy(self):
        self.assertFalse(self.reported("Integration (`gates.md` § Hard stops) stops."))

    def test_mention_without_pointer(self):
        self.assertTrue(self.reported("Integration is a hard stop."))


class RepositoryRules(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp(prefix="rule-copies-repo-"))
        self.addCleanup(shutil.rmtree, self.repo, ignore_errors=True)
        shutil.copytree(REPOSITORY / "skills", self.repo / "skills")

    def set_cap_at_source(self, value):
        path = self.repo / CAP_SOURCE
        text = path.read_text(encoding="utf-8")
        self.assertEqual(text.count("3 critic rounds in total"), 1)
        path.write_text(text.replace("3 critic rounds in total", f"{value} critic rounds in total"), encoding="utf-8")

    def append(self, relative, line):
        path = self.repo / relative
        lines = path.read_text(encoding="utf-8").rstrip("\n").split("\n") + ["", line]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return len(lines)

    def test_skills_have_no_copies_of_the_consolidated_rules(self):
        code, output, _ = run_check(self.repo, "skills")
        self.assertEqual(code, 0, output)

    def test_changing_the_cap_at_its_source_reports_nothing_when_only_pointers_exist(self):
        self.set_cap_at_source(4)
        code, output, _ = run_check(self.repo, "skills")
        self.assertEqual(code, 0, output)

    def test_changed_cap_reports_an_older_copy_as_disagreeing(self):
        self.set_cap_at_source(4)
        line = self.append("skills/feature/workflows/sdd.md", "A new critic, within the cap of 3 critic rounds.")
        code, output, _ = run_check(self.repo, "skills")
        self.assertEqual(code, 1)
        self.assertIn(f"skills/feature/workflows/sdd.md:{line}: RC-1", output)
        self.assertIn("DISAGREES: source says 4", output)

    def test_hard_stop_named_without_a_pointer_is_reported(self):
        line = self.append("skills/feature/workflows/direct.md", "Integration is a hard stop.")
        code, output, _ = run_check(self.repo, "skills")
        self.assertEqual(code, 1)
        self.assertIn(f"skills/feature/workflows/direct.md:{line}: HS-2", output)

    def test_hard_stop_condition_restated_is_reported(self):
        line = self.append("skills/feature/protocols/multi-feature.md", "Integration stops the feature in every profile.")
        code, output, _ = run_check(self.repo, "skills")
        self.assertEqual(code, 1)
        self.assertIn(f"skills/feature/protocols/multi-feature.md:{line}: HS-1", output)



class PointerScopeReproductions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = Path(tempfile.mkdtemp(prefix="rule-copies-scope-"))
        shutil.copytree(REPOSITORY / "skills", cls.repo / "skills")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.repo, ignore_errors=True)

    def copies(self, text):
        (self.repo / "skills" / "probe.md").write_text(text + "\n", encoding="utf-8")
        _, output, _ = run_check(self.repo, "skills")
        return [line for line in output.splitlines() if line.startswith("skills/probe.md:")]

    def test_level_contents_next_to_the_section_pointer_are_copies(self):
        found = self.copies("R0: no critic. R1: one critic. R2: the full cycle (`protocols/review-cycle.md` §Review levels).")
        self.assertEqual(len([line for line in found if "RL-2" in line]), 2, found)

    def test_level_contents_next_to_another_review_cycle_pointer_are_copies(self):
        found = self.copies("R1: one critic (`protocols/review-cycle.md` §R2 · The cycle).")
        self.assertTrue(any("RL-2" in line for line in found), found)

    def test_level_names_next_to_the_pointer_are_not_copies(self):
        self.assertEqual(self.copies("Run the critic (R1 or R2) as `protocols/review-cycle.md` §Review levels says."), [])

    def test_hard_stop_pointing_to_another_section_of_gates_is_a_copy(self):
        found = self.copies("Merging a branch is a hard stop (`protocols/gates.md` §Profiles).")
        self.assertTrue(any("HS-2" in line for line in found), found)

    def test_hard_stop_with_the_hard_stops_pointer_is_not_a_copy(self):
        self.assertEqual(self.copies("Merging is a hard stop (`protocols/gates.md` §Hard stops)."), [])

    def test_bare_path_in_the_previous_section_does_not_count(self):
        found = self.copies("See `protocols/gates.md`.\n\n## Integration\n\nEvery push is a hard stop.")
        self.assertTrue(any("probe.md:5: HS-2" in line for line in found), found)

    def test_pointer_in_the_previous_paragraph_does_not_count(self):
        found = self.copies("See `protocols/gates.md` §Hard stops.\n\nEvery push is a hard stop.")
        self.assertTrue(any("probe.md:3: HS-2" in line for line in found), found)

    def test_pointer_in_a_neighbouring_table_cell_does_not_count(self):
        found = self.copies("| Event | Source |\n| --- | --- |\n| a push is a hard stop | `protocols/gates.md` §Hard stops |")
        self.assertTrue(any("probe.md:3: HS-2" in line for line in found), found)

    def test_pointer_in_the_same_table_cell_counts(self):
        self.assertEqual(self.copies("| Event | Note |\n| --- | --- |\n| a hard stop (`protocols/gates.md` §Hard stops) | x |"), [])

    def test_pointer_in_a_neighbouring_list_item_does_not_count(self):
        found = self.copies("- See `protocols/gates.md` §Hard stops.\n- Every push is a hard stop.")
        self.assertTrue(any("probe.md:2: HS-2" in line for line in found), found)

    def test_pointer_in_the_same_wrapped_list_item_counts(self):
        self.assertEqual(self.copies("- Every push is a hard stop\n  (`protocols/gates.md` §Hard stops)."), [])


if __name__ == "__main__":
    unittest.main()
