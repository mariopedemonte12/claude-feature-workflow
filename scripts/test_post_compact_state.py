import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "skills" / "feature" / "scripts" / "post_compact_state.py"
MEMORY = "# memory\n\n## Project\n- Stack: x\n\n## Portfolio\n| Feature |\n| alpha |\n\n## Notes\nNOTES-ONLY\n"


def run_hook(stdin_text):
    completed = subprocess.run([sys.executable, str(SCRIPT)], input=stdin_text, capture_output=True, text=True, timeout=60)
    return completed.returncode, completed.stdout, completed.stderr


class GitRepository(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp(prefix="post-compact-")).resolve()
        self.addCleanup(shutil.rmtree, self.repo, ignore_errors=True)
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        self.directory = self.repo / ".git" / "feature-workflow"
        (self.directory / "claims").mkdir(parents=True)

    def write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def claim(self, slug, status="Active", folder=None):
        folder = folder or self.repo / "features" / slug
        self.write(self.directory / "claims" / f"{slug}.json",
                   json.dumps({"slug": slug, "status": status, "featureFolder": str(folder)}))
        return folder

    def event(self, **fields):
        return json.dumps({"hook_event_name": "SessionStart", "source": "compact", "cwd": str(self.repo), **fields})

    def context(self, **fields):
        code, output, _ = run_hook(self.event(**fields))
        self.assertEqual(code, 0)
        if not output:
            return None
        return json.loads(output)["hookSpecificOutput"]["additionalContext"]


class InjectedState(GitRepository):
    def test_output_has_the_contract_the_hook_runner_reads(self):
        self.write(self.directory / "memory.md", MEMORY)
        _, output, _ = run_hook(self.event())
        specific = json.loads(output)["hookSpecificOutput"]
        self.assertEqual(specific["hookEventName"], "SessionStart")

    def test_state_of_each_active_claim_and_the_portfolio_only(self):
        self.write(self.directory / "memory.md", MEMORY)
        self.write(self.claim("alpha") / "state.md", "STATE-ALPHA\n")
        self.write(self.claim("beta") / "state.md", "STATE-BETA\n")
        context = self.context()
        for text in ("| alpha |", "STATE-ALPHA", "STATE-BETA"):
            self.assertIn(text, context)
        self.assertNotIn("Stack: x", context)
        self.assertNotIn("NOTES-ONLY", context)

    def test_paused_and_done_claims_are_skipped(self):
        self.write(self.claim("old", "Done") / "state.md", "STATE-OLD\n")
        self.write(self.claim("rest", "Paused") / "state.md", "STATE-REST\n")
        self.write(self.claim("live") / "state.md", "STATE-LIVE\n")
        context = self.context()
        self.assertIn("STATE-LIVE", context)
        self.assertNotIn("STATE-OLD", context)
        self.assertNotIn("STATE-REST", context)

    def test_card_state_section_replaces_a_missing_state_file(self):
        card = "# Feature\n\n## Cases\nCASES-ONLY\n\n## State\nCARD-STATE\n\n## Result\nRESULT-ONLY\n"
        self.write(self.claim("solo") / "feature.md", card)
        context = self.context()
        self.assertIn("CARD-STATE", context)
        self.assertNotIn("CASES-ONLY", context)
        self.assertNotIn("RESULT-ONLY", context)

    def test_oversized_state_is_cut_and_names_the_file(self):
        folder = self.claim("big")
        self.write(folder / "state.md", "x" * 20000)
        context = self.context()
        self.assertIn("[cut at 6000 characters", context)
        self.assertIn(str(folder / "state.md"), context)
        self.assertLess(len(context), 7000)

    def test_runs_from_a_linked_worktree(self):
        subprocess.run(["git", "-C", str(self.repo), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "i"], check=True)
        linked = self.repo.parent / (self.repo.name + "-linked")
        self.addCleanup(shutil.rmtree, linked, ignore_errors=True)
        subprocess.run(["git", "-C", str(self.repo), "worktree", "add", "-q", str(linked)], check=True)
        self.write(self.claim("alpha") / "state.md", "STATE-ALPHA\n")
        self.assertIn("STATE-ALPHA", self.context(cwd=str(linked)))


class SilentWhenThereIsNothing(GitRepository):
    def assertSilent(self, stdin_text):
        code, output, error = run_hook(stdin_text)
        self.assertEqual((code, output, error), (0, "", ""))

    def test_no_memory_and_no_claims(self):
        self.assertSilent(self.event())

    def test_not_a_git_repository(self):
        plain = Path(tempfile.mkdtemp(prefix="plain-"))
        self.addCleanup(shutil.rmtree, plain, ignore_errors=True)
        self.assertSilent(json.dumps({"source": "compact", "cwd": str(plain)}))

    def test_other_sources_do_nothing(self):
        self.write(self.claim("alpha") / "state.md", "STATE-ALPHA\n")
        self.assertSilent(self.event(source="startup"))

    def test_bad_input_does_not_fail(self):
        for text in ("", "not json", "[1, 2]", "null"):
            code, _, error = run_hook(text)
            self.assertEqual((code, error), (0, ""))

    def test_corrupt_claims_and_missing_folders_are_skipped(self):
        self.write(self.directory / "claims" / "bad.json", "{not json")
        self.write(self.directory / "claims" / "list.json", "[1]")
        self.write(self.directory / "claims" / "nofolder.json", json.dumps({"status": "Active"}))
        self.claim("gone")
        self.write(self.claim("live") / "state.md", "STATE-LIVE\n")
        self.assertIn("STATE-LIVE", self.context())

    def test_binary_state_file_is_skipped(self):
        folder = self.claim("binary")
        folder.mkdir(parents=True)
        (folder / "state.md").write_bytes(b"\xff\xfe\x00\x80")
        self.assertSilent(self.event())


if __name__ == "__main__":
    unittest.main()
