import json
import re
import shutil
import tempfile
import unittest
import subprocess
from pathlib import Path

import rule_copies
import test_rule_copies as base

REPOSITORY = base.REPOSITORY
RULES_FILE = REPOSITORY / "scripts" / "rule_copies.json"
BASE_COMMIT = "206cadc"
CAP_SOURCE = base.CAP_SOURCE
REVIEWER = "skills/feature/roles/reviewer.md"
SDD = "skills/feature/workflows/sdd.md"
POINTER = "`protocols/gates.md` §Hard stops"
RUN_TIME_BOUND_SECONDS = 60
FEATURE_FOLDER_FILES = {"specification.md", "intent.md"}


def git(*arguments):
    completed = subprocess.run(["git", "-C", str(REPOSITORY), *arguments], capture_output=True, text=True)
    return completed.returncode, completed.stdout


def rule_searches():
    return {rule["id"]: rule["searches"] for rule in json.loads(RULES_FILE.read_text(encoding="utf-8"))["rules"]}


def recorded_pattern(rule):
    return re.search(r"'([^']+)'", rule_searches()[rule][0]).group(1)


def section(relative, title):
    lines = rule_copies.markdown_lines(REPOSITORY / relative)
    start, end = rule_copies.section_span(lines, title)
    return "\n".join(lines[start:end])


def flat(text):
    return re.sub(r"\s+", " ", re.sub(r"[*`]", "", text))


def rules():
    return {rule["id"]: rule for rule in json.loads(RULES_FILE.read_text(encoding="utf-8"))["rules"]}


def new_rules_recorded(identifiers, minimum_fingerprints):
    class NewRulesRecorded(unittest.TestCase):
        def setUp(self):
            self.rules = rules()

        def test_each_new_rule_has_a_source_fingerprints_and_a_concept_search(self):
            for identifier in identifiers:
                with self.subTest(rule=identifier):
                    rule = self.rules[identifier]
                    self.assertTrue(rule["fingerprints"] and rule["searches"] and rule["source"]["section"])
                    re.compile(recorded_pattern(identifier))

        def test_the_fingerprints_find_the_wording_of_their_own_source(self):
            for identifier in identifiers:
                rule = self.rules[identifier]
                source = flat(section(rule["source"]["file"], rule["source"]["section"]))
                found = [pattern for pattern in rule["fingerprints"] if re.search(pattern, source, re.IGNORECASE)]
                with self.subTest(rule=identifier):
                    self.assertGreaterEqual(len(found), minimum_fingerprints, found)

    return NewRulesRecorded


class SkillsCopy(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp(prefix="inc1-"))
        self.addCleanup(shutil.rmtree, self.repo, ignore_errors=True)
        shutil.copytree(REPOSITORY / "skills", self.repo / "skills")
        (self.repo / "docs").mkdir()
        (self.repo / "README.md").write_text("# Readme\n", encoding="utf-8")

    def edit(self, relative, old, new):
        path = self.repo / relative
        text = path.read_text(encoding="utf-8")
        self.assertEqual(text.count(old), 1, f"{old!r} in {relative}")
        path.write_text(text.replace(old, new), encoding="utf-8")

    def append(self, relative, text):
        path = self.repo / relative
        existing = path.read_text(encoding="utf-8").rstrip("\n")
        path.write_text(existing + "\n\n" + text + "\n", encoding="utf-8")
        return len(existing.splitlines()) + 2

    def put(self, relative, text):
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def check(self, *paths):
        return base.run_check(self.repo, *paths)

    def reported(self, text):
        self.put("docs/probe.md", "# Probe\n\n" + text + "\n")
        code, output, _ = self.check("docs/probe.md")
        return code == 1 and "docs/probe.md:" in output
