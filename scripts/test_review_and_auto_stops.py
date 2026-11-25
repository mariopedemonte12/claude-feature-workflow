import json
import re
import unittest

from inc1_support import REPOSITORY, RULES_FILE, SkillsCopy, recorded_pattern

FEATURE = REPOSITORY / "skills" / "feature"
REVIEW_CYCLE = "skills/feature/protocols/review-cycle.md"
GATES = "skills/feature/protocols/gates.md"
CAP_POINTER = "`protocols/review-cycle.md` §R2 · The cycle"
AUTO_POINTER = "`protocols/gates.md` §When a gate is off"
NEW_RULES = ("RC-2", "RC-3", "AU-1")


def section(relative, title):
    text = (REPOSITORY / relative).read_text(encoding="utf-8")
    match = re.search(rf"^## {re.escape(title)}\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    return match.group(1)


def flat(text):
    return re.sub(r"\s+", " ", re.sub(r"[*`]", "", text))


class CapStopSource(unittest.TestCase):
    def setUp(self):
        self.cycle = flat(section(REVIEW_CYCLE, "R2 · The cycle"))

    def test_ac7_cap_with_blocker_or_major_open_stops_and_lists_the_findings(self):
        self.assertIn("Cap reached with a Blocker or Major open.", self.cycle)
        self.assertIn("the feature stops (a hard stop: protocols/gates.md §Hard stops)", self.cycle)
        self.assertIn("listing each open finding", self.cycle)

    def test_ac22_open_counts_findings_of_every_round(self):
        self.assertIn("every Blocker and Major finding of every round", self.cycle)
        for closed_by in ("a later critic round reviewed the fix", "the verifier refuted it", "the programmer accepted it"):
            self.assertIn(closed_by, self.cycle)
        self.assertIn("a finding fixed after the last round is still open", self.cycle)

    def test_ac8_cap_with_nothing_open_continues(self):
        self.assertIn("With none open, the loop stops and the feature continues", self.cycle)

    def test_the_cap_value_is_unchanged(self):
        self.assertIn("has had 3 critic rounds in total", self.cycle)

    def test_ac9_unreviewed_commits_are_listed_with_their_hashes_before_acceptance(self):
        self.assertIn("the fixes of that round included", self.cycle)
        self.assertIn("with its hash as unreviewed in the final report", self.cycle)
        self.assertIn("the message that presents acceptance", self.cycle)
        self.assertIn("never presented as reviewed", self.cycle)

    def test_ac10_every_review_path_is_named(self):
        for path in ("SDD", "EVO and Hybrid (per increment)", "both executor modes", "DIRECT when the programmer asks for a critic"):
            self.assertIn(path, self.cycle)


class CapStopIsAHardStop(unittest.TestCase):
    BASELINE_STOPS = ("integration:", "cleanup:", "installing", "migration", "breaking a public interface",
                      "contradicts the programmer's words", "Blocker found by a security audit", "criticality check")

    def setUp(self):
        self.stops = flat(section(GATES, "Hard stops"))

    def test_inv1_every_existing_hard_stop_is_kept(self):
        for stop in self.BASELINE_STOPS:
            self.assertIn(stop, self.stops)

    def test_defects_off_points_to_the_cap_stop(self):
        profiles = flat(section(GATES, "Profiles"))
        self.assertIn("still open when the round cap is reached, which stop the feature (protocols/review-cycle.md §R2 · The cycle)", profiles)

    def test_the_cap_stop_is_listed_as_a_pointer(self):
        self.assertIn("cap reached with a Blocker or Major open (protocols/review-cycle.md §R2 · The cycle)", self.stops)


class ReviewPathsPoint(unittest.TestCase):
    PLACES = {
        "workflows/sdd.md": ["stop when the round cap is reached with a Blocker or Major open",
                             "listed as unreviewed (protocols/review-cycle.md §R2 · The cycle)"],
        "workflows/evo.md": ["the stop when it is reached with a Blocker or Major open (protocols/review-cycle.md §R2 · The cycle)",
                             "increment's last critic round, listed as unreviewed"],
        "workflows/direct.md": ["the stop at the cap follow protocols/review-cycle.md §R2 · The cycle",
                                "listed as unreviewed (protocols/review-cycle.md §R2 · The cycle)"],
        "protocols/executor.md": ["the stop when it is reached with a Blocker or Major open: §R2 · The cycle",
                                  "with the round cap and its stop (protocols/review-cycle.md §R2 · The cycle)",
                                  "listed as unreviewed (protocols/review-cycle.md §R2 · The cycle)"],
        "templates/final-report.md": ["marked unreviewed (protocols/review-cycle.md §R2 · The cycle)"],
        "templates/feature-card.md": ["marked unreviewed (protocols/review-cycle.md §R2 · The cycle)"],
    }

    def test_ac10_each_review_path_points_to_the_cap_and_its_stop(self):
        for relative, needed in self.PLACES.items():
            text = flat((FEATURE / relative).read_text(encoding="utf-8"))
            for phrase in needed:
                with self.subTest(file=relative, phrase=phrase):
                    self.assertIn(phrase, text)

    def test_executor_no_longer_restates_the_round_count(self):
        text = (FEATURE / "protocols" / "executor.md").read_text(encoding="utf-8")
        self.assertNotRegex(text, r"up to \d+ rounds")


class AutoStopSource(unittest.TestCase):
    def setUp(self):
        self.off = section(GATES, "When a gate is off")
        self.steps = re.findall(r"^\d+\. \*\*(.+?)\*\*", self.off, re.MULTILINE)

    def test_d001_the_stop_is_the_step_before_deciding(self):
        self.assertEqual(len(self.steps), 5, self.steps)
        self.assertIn("a choice between rules the author wrote goes to the programmer", self.steps[0])
        self.assertTrue(self.steps[1].startswith("Decide as the gate would have asked"))

    def test_ac5_it_stops_in_the_decision_format_without_a_decided_by_agent_record(self):
        text = flat(self.off)
        self.assertIn("In auto,", text)
        self.assertIn("stop the feature, record it as Pending and present it in the decision format", text)
        self.assertIn("No Decided by agent record is written for it", text)

    def test_fr6_defines_a_rule_the_author_wrote(self):
        text = flat(self.off)
        self.assertIn("its docs, specifications and conventions, the intent record, or an earlier decision", text)
        self.assertIn("choosing which of two or more such rules prevails", text)

    def test_ac21_code_behavior_stays_a_discovery(self):
        self.assertIn("a conflict between code and a written rule stays a discovery", flat(self.off))

    def test_ac6_other_decisions_keep_the_off_gate_steps(self):
        self.assertIn("Every other decision follows steps 2–5", flat(self.off))

    def test_fr8_key_is_not_reached(self):
        self.assertNotIn("`key`", self.off)

    def test_auto_stop_is_not_a_hard_stop(self):
        self.assertNotIn("author wrote", section(GATES, "Hard stops"))

    def test_questions_in_auto_point_to_the_step(self):
        self.assertIn("a choice between rules the author wrote (§When a gate is off, step 1)", flat(section(GATES, "Questions")))


class NewRulesRecorded(unittest.TestCase):
    def setUp(self):
        self.rules = {rule["id"]: rule for rule in json.loads(RULES_FILE.read_text(encoding="utf-8"))["rules"]}

    def test_each_new_rule_has_a_source_fingerprints_and_a_concept_search(self):
        for identifier in NEW_RULES:
            with self.subTest(rule=identifier):
                rule = self.rules[identifier]
                self.assertTrue(rule["fingerprints"] and rule["searches"] and rule["source"]["section"])
                re.compile(recorded_pattern(identifier))

    def test_the_fingerprints_find_the_wording_of_their_own_source(self):
        for identifier in NEW_RULES:
            rule = self.rules[identifier]
            source = flat(section(rule["source"]["file"], rule["source"]["section"]))
            found = [pattern for pattern in rule["fingerprints"] if re.search(pattern, source, re.IGNORECASE)]
            with self.subTest(rule=identifier):
                self.assertGreaterEqual(len(found), 2, found)


class RestatementsReported(SkillsCopy):
    COPIES = {
        "RC-2": ["A finding is open unless the verifier refuted it.",
                 "Count every Major from any round when the cap ends the loop.",
                 "When the cap is reached with a Major still open, ask the programmer.",
                 "A finding fixed after the last round is still open.",
                 "A finding is open unless the programmer accepted it.",
                 "A later round reviewed its fix."],
        "RC-3": ["List the last round's commits, the fixes of that round included.",
                 "A commit is never presented as reviewed.",
                 "Mark those commits unreviewed.",
                 "List the commits after the last round with their hashes before acceptance.",
                 "Those commits were not reviewed."],
        "AU-1": ["The existing behavior of code is not a rule.",
                 "A choice between rules the author wrote stops the feature.",
                 "In auto, two authored rules in conflict go to the programmer.",
                 "A written rule is the project's docs, the intent record, or an earlier decision.",
                 "In auto, when two written rules contradict each other, stop and ask the programmer."],
    }

    def test_negative_each_restatement_in_another_file_is_reported(self):
        for identifier, texts in self.COPIES.items():
            for text in texts:
                with self.subTest(rule=identifier, text=text):
                    line = self.append("skills/feature/workflows/sdd.md", text)
                    code, output, _ = self.check("skills")
                    self.edit("skills/feature/workflows/sdd.md", "\n\n" + text + "\n", "\n")
                    self.assertEqual(code, 1, output)
                    self.assertIn(f"skills/feature/workflows/sdd.md:{line}: {identifier} ", output)

    def test_named_next_to_its_pointer_is_not_a_copy(self):
        accepted = [f"Stop when the cap is reached with a Blocker open ({CAP_POINTER}).",
                    f"Commits after the last round are listed as unreviewed ({CAP_POINTER}).",
                    f"A choice between rules the author wrote is handled as {AUTO_POINTER} says."]
        for text in accepted:
            with self.subTest(text=text):
                self.assertFalse(self.reported(text))

    def test_not_reviewed_about_something_other_than_commits_is_not_a_copy(self):
        self.assertFalse(self.reported("The spec was not reviewed by the planner."))

    def test_named_far_from_its_pointer_is_a_copy(self):
        text = f"Commits are marked unreviewed{' and so on' * 10} ({CAP_POINTER})."
        self.assertTrue(self.reported(text))

    def test_pointer_to_another_gates_section_does_not_cover_the_auto_stop(self):
        self.assertTrue(self.reported("A choice between rules the author wrote (`protocols/gates.md` §Hard stops)."))

    def test_moving_the_auto_stop_out_of_its_section_reports_it(self):
        self.edit(GATES, "## When a gate is off\n", "## When a gate is off\n\nSee below.\n\n## Off gates\n")
        code, output, _ = self.check("skills")
        self.assertEqual(code, 1, output)
        self.assertIn(f"{GATES}:", output)
        self.assertIn(" AU-1 ", output)


if __name__ == "__main__":
    unittest.main()
