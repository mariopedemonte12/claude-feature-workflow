import json
import unittest

from test_rule_copies import REPOSITORY, ScratchRepository, run_check


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


class RealTreeHasNoRestatedCopies(unittest.TestCase):
    def test_skills_readme_and_docs_have_no_restated_copy(self):
        code, output, _ = run_check(REPOSITORY)
        self.assertEqual(code, 0, output)
        self.assertIn("0 restated copies", output)


if __name__ == "__main__":
    unittest.main()
