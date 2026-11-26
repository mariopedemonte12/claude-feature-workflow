import json
import re
import subprocess
import tarfile
import tempfile
import shutil
import unittest
from pathlib import Path

import rule_copies
import test_rule_copies as base
from inc1_support import (BASE_COMMIT, CAP_SOURCE, FEATURE_FOLDER_FILES, POINTER, REPOSITORY, REVIEWER, RULES_FILE, SDD, SkillsCopy,
                          git, recorded_pattern, rule_searches)

class SourceChangePropagates(SkillsCopy):
    def test_t_l1_02_every_stale_copy_is_reported_with_file_and_line(self):
        places = {SDD: "A fix round stays within 3 critic rounds in total.",
                  "skills/feature/protocols/executor.md": "Review runs up to three rounds.",
                  "skills/feature-kit/SKILL.md": "A cap of 3 applies."}
        lines = {path: self.append(path, text) for path, text in places.items()}
        self.edit(CAP_SOURCE, "3 critic rounds in total", "4 critic rounds in total")
        code, output, _ = self.check("skills")
        self.assertEqual(code, 1)
        for path, line in lines.items():
            self.assertRegex(output, rf"{re.escape(path)}:{line}: RC-1 .*DISAGREES: source says 4")

    def test_t_l1_03_pointers_only_report_nothing_after_the_change(self):
        self.edit(CAP_SOURCE, "3 critic rounds in total", "5 critic rounds in total")
        code, output, _ = self.check("skills")
        self.assertEqual(code, 0, output)

    def test_t_l1_04_rule_with_a_single_mention_reports_nothing_and_no_error(self):
        self.edit(REVIEWER, "report only Blocker and Major findings in that diff",
                  "report only Blocker, Major and Minor findings in that diff")
        code, output, error = self.check("skills")
        self.assertEqual((code, error), (0, ""), output)


class RestatementInjected(SkillsCopy):
    def assert_found(self, relative, text):
        exists = (self.repo / relative).exists()
        line = self.append(relative, text) if exists else self.new_file(relative, text)
        code, output, _ = self.check()
        self.assertEqual(code, 1, output)
        self.assertRegex(output, rf"{re.escape(relative)}:{line}: RC-1 ")

    def new_file(self, relative, text):
        self.put(relative, "# Notes\n\n" + text + "\n")
        return 3

    def test_t_l1_05_verbatim_in_skills(self):
        self.assert_found("skills/feature/workflows/direct.md", "the feature has had 3 critic rounds in total")

    def test_t_l1_05_paraphrased_inside_a_fingerprint(self):
        self.assert_found("skills/feature/roles/verifier.md", "Reviews stop at most three review rounds after the first.")

    def test_t_l1_05_in_readme(self):
        self.assert_found("README.md", "The loop ends after 3 critic rounds.")

    def test_t_l1_05_in_docs(self):
        self.assert_found("docs/architecture.md", "Each increment has a limit of three rounds.")

    def test_t_l1_05_in_feature_kit(self):
        self.assert_found("skills/feature-kit/SKILL.md", "Run at most 3 critic rounds per feature.")

    def test_t_l1_05_other_families_are_reported_too(self):
        self.put("docs/families.md", "# F\n\nR0: no review agent. R2 for Critical. A hard stop. DIRECT runs no critic.\n")
        _, output, _ = self.check()
        for rule in ("RL-1", "RL-2", "RL-4", "HS-2"):
            self.assertIn(f"docs/families.md:3: {rule} ", output)


class OutsideTheRecordedSearches(unittest.TestCase):
    def test_t_l1_15_wording_no_fingerprint_finds_is_found_by_the_concept_search(self):
        sentence = "The loop is capped at 3 rounds."
        self.assertIsNotNone(re.search(recorded_pattern("RC-1"), sentence, re.IGNORECASE))

    def test_t_l1_15_every_rule_records_a_concept_search(self):
        for rule, searches in rule_searches().items():
            self.assertTrue(searches and all(searches), rule)


class PointersAndBareNames(SkillsCopy):
    def test_t_l1_06_not_reported(self):
        accepted = [
            "Review levels: see `protocols/review-cycle.md` §Review levels.",
            "The round cap: `protocols/review-cycle.md` §R2 · The cycle.",
            f"Integration is a hard stop ({POINTER}).",
            f"Integration is a hard stop, one of those listed in {POINTER}.",
            f"Some of the hard stops (see {POINTER}) apply here.",
            "The default review level is chosen by the programmer (R1 for example).",
            "Review rounds are logged in rounds.md.",
        ]
        for text in accepted:
            with self.subTest(text=text):
                self.assertFalse(self.reported(text))

    def test_t_l1_06_pointer_variants_by_case_wrap_and_emphasis(self):
        variants = ["Integration is a HARD STOP (`protocols/gates.md` §HARD STOPS).",
                    "Integration is a hard\nstop (`protocols/gates.md`\n§Hard stops).",
                    f"Integration is a **hard stop** ({POINTER})."]
        for text in variants:
            with self.subTest(text=text):
                self.assertFalse(self.reported(text))

    def test_td_1_pointer_before_the_mention_is_not_a_copy(self):
        self.assertFalse(self.reported(f"Per {POINTER}, integration is a hard stop."))

    def test_td_1_bare_path_pointer_is_not_a_copy(self):
        self.assertFalse(self.reported("The hard stops are listed in `protocols/gates.md`."))

    def test_td_2_levels_named_next_to_a_pointer_are_not_a_copy(self):
        self.assertFalse(self.reported("Run the critic (R1/R2) as `protocols/review-cycle.md` §Review levels says."))


class PointerWindowBoundaries(SkillsCopy):
    def test_t_l1_06_a_pointer_wrapped_inside_the_same_block_counts(self):
        wrapped = [
            "Integration is a hard\nstop (`protocols/gates.md`\n§Hard stops).",
            "Integration is a hard stop\n(`protocols/gates.md` §Hard stops).",
            "- Integration is a hard stop\n  (`protocols/gates.md` §Hard stops).",
            "1. Integration is a hard stop\n   (`protocols/gates.md` §Hard stops).",
            "> Integration is a hard stop\n> (`protocols/gates.md` §Hard stops).",
            "| a | hard stop (`protocols/gates.md` §Hard stops) | b |",
            "At R1 or R2\n(`protocols/review-cycle.md` §Review levels) a critic runs.",
        ]
        for text in wrapped:
            with self.subTest(text=text):
                self.assertFalse(self.reported(text))

    def test_t_l1_06_a_pointer_in_another_block_does_not_count(self):
        separate = [
            "Integration is a hard stop.\n\nSee `protocols/gates.md` §Hard stops.",
            "- Integration is a hard stop\n- `protocols/gates.md` §Hard stops",
            "| a | hard stop | `protocols/gates.md` §Hard stops |",
            "## Hard stop\n`protocols/gates.md` §Hard stops",
        ]
        for text in separate:
            with self.subTest(text=text):
                self.assertTrue(self.reported(text))

    def test_t_l1_06_a_pointer_to_another_section_of_gates_does_not_count(self):
        for section in ("Profiles", "Questions"):
            with self.subTest(section=section):
                self.assertTrue(self.reported(f"Per `protocols/gates.md` §{section}, a hard stop is relevant."))


class RecallOfFingerprints(SkillsCopy):
    def test_td_3_review_rounds_with_a_number_is_a_cap_copy(self):
        self.assertTrue(self.reported("After 3 review rounds the feature stops."))

    def test_td_3_limited_to_a_number_of_critic_rounds_is_a_cap_copy(self):
        self.assertTrue(self.reported("Critic rounds are limited to 3."))


class VerdictInvariance(SkillsCopy):
    COPY = "up to 3 critic rounds"

    def variants(self):
        return {
            "rewrap each word": "\n".join(self.COPY.split()),
            "upper case": self.COPY.upper(),
            "bold": "up to 3 **critic** rounds",
            "backticks": "`up to 3 critic rounds`",
            "bullet": "- " + self.COPY,
            "bullet wrapped": "- up to 3\n  critic rounds",
            "table cell": f"| a | {self.COPY} |",
            "no-break space": self.COPY.replace(" ", " "),
            "tab": self.COPY.replace(" ", "\t"),
            "link text": f"[{self.COPY}](a.md)",
            "extra spaces": self.COPY.replace(" ", "   "),
        }

    def test_t_l1_12_every_variant_of_a_copy_is_reported(self):
        for name, text in self.variants().items():
            with self.subTest(variant=name):
                self.assertTrue(self.reported(text))

    def test_t_l1_12_crlf_wrapped_copy_is_reported(self):
        self.put("docs/crlf.md", "up to 3\r\ncritic\r\nrounds\r\n")
        _, output, _ = self.check("docs")
        self.assertIn("docs/crlf.md:1: RC-1", output)

    def test_t_l1_12_a_copy_split_by_a_blank_line_is_not_one_sentence(self):
        self.assertFalse(self.reported("up to 3 critic\n\nrounds"))

    def test_td_4_copy_wrapped_inside_a_blockquote_is_reported(self):
        self.assertTrue(self.reported("> up to 3 critic\n> rounds"))

    def test_td_4_copy_in_underscore_emphasis_is_reported(self):
        self.assertTrue(self.reported("__3 critic rounds__"))


class FinalTree(unittest.TestCase):
    def changed_skill_files(self):
        code, output = git("diff", "--name-only", BASE_COMMIT, "HEAD", "--", "skills")
        if code != 0:
            self.skipTest(f"{BASE_COMMIT} is not available")
        return [line for line in output.splitlines() if line.endswith(".md") and (REPOSITORY / line).exists()]

    def test_t_l1_07_files_changed_since_the_base_have_no_copies(self):
        files = self.changed_skill_files()
        self.assertTrue(files)
        code, output, _ = base.run_check(REPOSITORY, *files)
        self.assertEqual(code, 0, output)

    def test_t_l1_07_the_whole_skills_tree_has_no_copies(self):
        code, output, _ = base.run_check(REPOSITORY, "skills")
        self.assertEqual(code, 0, output)


class BaselinePower(unittest.TestCase):
    KNOWN_PLACES = [
        ("skills/feature/protocols/gates.md", [3, 30, 31, 32, 33, 48]),
        ("skills/feature/protocols/decisions.md", [19]),
        ("skills/feature/protocols/executor.md", [43, 45]),
        ("skills/feature/workflows/evo.md", [3, 59, 61]),
        ("skills/feature/workflows/sdd.md", [3, 35, 36, 54, 56, 58]),
        ("skills/feature/protocols/review-cycle.md", [11, 23, 48]),
        ("skills/feature/protocols/phase-runners.md", [31, 75]),
    ]

    def setUp(self):
        self.repo = Path(tempfile.mkdtemp(prefix="inc1-base-"))
        self.addCleanup(shutil.rmtree, self.repo, ignore_errors=True)
        archive = subprocess.run(["git", "-C", str(REPOSITORY), "archive", BASE_COMMIT, "skills"], capture_output=True)
        if archive.returncode != 0:
            self.skipTest(f"{BASE_COMMIT} is not available")
        archive_path = self.repo / "base.tar"
        archive_path.write_bytes(archive.stdout)
        with tarfile.open(archive_path) as bundle:
            bundle.extractall(self.repo, filter="data")
        self.rules = self.repo / "rules.json"
        self.rules.write_text(json.dumps(self.rules_with_a_source_in_the_baseline()), encoding="utf-8")

    def rules_with_a_source_in_the_baseline(self):
        data = json.loads(RULES_FILE.read_text(encoding="utf-8"))
        data["rules"] = [rule for rule in data["rules"] if self.has_source(rule["source"])]
        return data

    def has_source(self, source, root=None):
        path = (root or self.repo) / source["file"]
        return path.exists() and rule_copies.section_span(rule_copies.markdown_lines(path), source["section"]) is not None

    def test_only_rules_with_sections_added_later_lack_a_source_in_the_baseline(self):
        rules = json.loads(RULES_FILE.read_text(encoding="utf-8"))["rules"]
        dropped = {rule["id"] for rule in rules if not self.has_source(rule["source"])}
        present_now = {rule["id"] for rule in rules if self.has_source(rule["source"], REPOSITORY)}
        self.assertLessEqual(dropped, present_now)
        self.assertIn("RY-1", dropped)

    def check(self, *paths):
        return base.run_check(self.repo, *paths, rules=self.rules)

    def test_t_l1_09_the_known_copies_of_the_baseline_are_found(self):
        code, output, _ = self.check("skills")
        self.assertEqual(code, 1)
        missing = [f"{path}:{line}" for path, lines in self.KNOWN_PLACES for line in lines
                   if f"{path}:{line}: " not in output]
        self.assertEqual(missing, [])

    def test_t_l1_09_the_baseline_reports_a_copy_of_each_rule_family(self):
        _, output, _ = self.check("skills")
        for rule in ("RC-1", "RL-1", "RL-2", "RL-3", "RL-4", "RL-5", "RL-6", "HS-1", "HS-2"):
            self.assertIn(f": {rule} restated copy", output)

    def test_t_l1_09_a_paraphrase_the_fingerprints_miss_is_left_to_the_concept_search(self):
        text = "below R2 there is no verifier and no multi-round cycle"
        (self.repo / "docs").mkdir()
        (self.repo / "docs" / "executor.md").write_text(text + "\n", encoding="utf-8")
        _, output, _ = self.check("docs")
        self.assertIn("0 restated copies", output)
        self.assertIsNotNone(re.search(recorded_pattern("RL-2"), text.replace("R2", "R2 ")))


class Description(unittest.TestCase):
    def test_t_l1_08_help_runs_and_the_entry_names_the_script_and_the_searches(self):
        code, output, _ = base.run_check(REPOSITORY, "--help")
        self.assertEqual(code, 0)
        self.assertIn("usage", output)
        entry = (REPOSITORY / ".quality" / "anti-patterns.md").read_text(encoding="utf-8")
        for needed in ("AP-001", "scripts/rule_copies.py", "rule_copies.json", "searches"):
            self.assertIn(needed, entry)

    def test_t_l1_08_the_gate_registry_runs_the_check_and_its_tests(self):
        config = json.loads((REPOSITORY / ".quality" / "config.json").read_text(encoding="utf-8"))
        commands = " ".join(check["command"] for check in config["checks"])
        self.assertIn("scripts/rule_copies.py skills", commands)
        self.assertIn("unittest discover -s scripts", commands)


class PointersResolve(unittest.TestCase):
    PATHED = re.compile(r"`([\w./-]+\.md)`(?: step \d+)? §([^`,;()\n]+?)(?=[,;)`]|\s\(|\.\s|\.$|$)")

    def added_lines(self):
        code, output = git("diff", "-U0", BASE_COMMIT, "HEAD", "--", "skills")
        if code != 0:
            self.skipTest(f"{BASE_COMMIT} is not available")
        return [line[1:] for line in output.splitlines() if line.startswith("+") and not line.startswith("+++")]

    def labels(self, path):
        text = path.read_text(encoding="utf-8")
        headings = re.findall(r"^#{1,6}\s+(.+?)\s*$", text, re.MULTILINE)
        bold = re.findall(r"\*\*([^*]+?)[.:]?\*\*", text)
        return [re.sub(r"[*`]", "", label).lower() for label in headings + bold]

    def resolve(self, relative):
        for root in ("skills/feature", "skills/feature-kit"):
            if (REPOSITORY / root / relative).exists():
                return REPOSITORY / root / relative
        return None

    def resolves(self, match):
        if match.group(1) in FEATURE_FOLDER_FILES:
            return True
        path = self.resolve(match.group(1))
        wanted = re.sub(r"[*`]", "", match.group(2)).strip().lower()
        if path is not None and re.fullmatch(r"\d+(\.\d+)*", wanted):
            return True
        return path is not None and any(wanted.startswith(label) or label.startswith(wanted) for label in self.labels(path))

    def test_a_parenthetical_after_the_section_is_not_part_of_it(self):
        cases = {"`SKILL.md` §4 (roles, models)": ("4", True),
                 "`protocols/gates.md` §Hard stops (integration)": ("Hard stops", True),
                 "`protocols/gates.md` §No such section (x)": ("No such section", False)}
        for text, (section, resolves) in cases.items():
            with self.subTest(text=text):
                match = self.PATHED.search(text)
                self.assertEqual(match.group(2), section)
                self.assertEqual(self.resolves(match), resolves)

    def test_t_88_every_path_and_section_pointer_added_by_the_diff_resolves(self):
        pointers = [match for line in self.added_lines() for match in self.PATHED.finditer(line)]
        self.assertGreater(len(pointers), 20)
        self.assertEqual([match.group(0) for match in pointers if not self.resolves(match)], [])

if __name__ == "__main__":
    unittest.main()
