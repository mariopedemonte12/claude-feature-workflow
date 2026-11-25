import json
import re
import shutil
import tempfile
import unittest
import subprocess
from pathlib import Path

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
