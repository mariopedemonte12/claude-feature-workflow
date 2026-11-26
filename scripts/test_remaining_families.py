import json
import re
import unittest

from inc1_support import REPOSITORY, RULES_FILE, SkillsCopy

FEATURE = REPOSITORY / "skills" / "feature"
NEW_RULES = ("WT-1", "MF-1", "SM-1", "GP-1", "HW-1", "ST-1", "PL-1")
SOURCES = {
    "WT-1": "SKILL.md", "MF-1": "SKILL.md", "SM-1": "SKILL.md", "PL-1": "SKILL.md",
    "GP-1": "protocols/gates.md", "HW-1": "protocols/context-handoff.md", "ST-1": "protocols/context-handoff.md"}


def flat(text):
    return re.sub(r"\s+", " ", re.sub(r"[*`]", "", text))


def source_text(rule):
    return flat((FEATURE / SOURCES[rule]).read_text(encoding="utf-8"))


def rules():
    return {rule["id"]: rule for rule in json.loads(RULES_FILE.read_text(encoding="utf-8"))["rules"]}


class SourcesStateTheMeaning(unittest.TestCase):
    def test_who_writes_tests(self):
        text = source_text("WT-1")
        self.assertRegex(text, r"(?i)Implementer writes production code only")
        self.assertRegex(text, r"(?i)Tester implements and runs")
        self.assertRegex(text, r"(?i)fixture or helper")
        self.assertRegex(text, r"(?i)DIRECT is the exception")

    def test_model_floors(self):
        text = source_text("MF-1")
        self.assertRegex(text, r"(?i)never use haiku for the specification")
        self.assertRegex(text, r"(?i)Critical features.{0,200}use opus")

    def test_standard_models(self):
        text = source_text("SM-1")
        self.assertRegex(text, r"(?i)Repository Analyst.{0,60}haiku")
        self.assertRegex(text, r"(?i)Clean Code Critic.{0,60}opus")

    def test_profiles_per_gate(self):
        text = source_text("GP-1")
        self.assertRegex(text, r"(?i)\| Gate \| full \| key[^|]*\| auto \|")
        self.assertRegex(text, r"(?i)\| acceptance \| stops \| stops")

    def test_handoff_only_for_a_new_agent(self):
        text = source_text("HW-1")
        self.assertRegex(text, r"(?i)written at a phase transition only when the incoming agent is new")
        self.assertRegex(text, r"(?i)Executor mode never writes one")

    def test_state_written_at_every_stop(self):
        text = source_text("ST-1")
        self.assertRegex(text, r"(?i)writes it at every stop")

    def test_parallel_launches(self):
        text = source_text("PL-1")
        self.assertRegex(text, r"(?i)never run two code-modifying agents at the same time")
        self.assertRegex(text, r"(?i)independent tasks run in parallel")


class GuardKnowsTheRules(unittest.TestCase):
    def test_every_rule_has_a_source_a_search_and_a_check(self):
        known = rules()
        for rule in NEW_RULES:
            with self.subTest(rule=rule):
                self.assertIn(rule, known)
                self.assertTrue(known[rule]["searches"])
                self.assertTrue(known[rule]["fingerprints"] or known[rule]["names"])
                self.assertTrue(known[rule]["source"]["file"].endswith(SOURCES[rule]))


class ParaphrasesAreCaught(SkillsCopy):
    def test_restated_conditions_are_reported_in_a_doc(self):
        cases = {
            "WT-1": "The Test Designer derives the cases from the spec and the Tester implements them.",
            "MF-1": "The critic must never run on haiku, whatever the task.",
            "SM-1": "The Planner runs as `Plan` · opus unless the approach is mechanical.",
            "GP-1": "| Gate | `full` | `key` | `auto` |",
            "HW-1": "A handoff is written when the incoming agent is new.",
            "ST-1": "The orchestrator rewrites state.md at every stop.",
            "PL-1": "Never run two code-modifying agents at the same time.",
        }
        for rule, text in cases.items():
            with self.subTest(rule=rule):
                self.assertTrue(self.reported(text))

    def test_a_pointer_instead_of_a_restatement_is_clean(self):
        pointers = (
            "Who writes tests: `SKILL.md` §4, *Who writes tests*.",
            "Models and floors: `SKILL.md` §4, *Model selection per delegation*.",
            "Profiles: `protocols/gates.md` §Profiles.",
            "When a handoff is written: `protocols/context-handoff.md` §Who writes it.",
            "When state.md is written: `protocols/context-handoff.md` §Resume state.",
        )
        for text in pointers:
            with self.subTest(text=text):
                self.assertFalse(self.reported(text))

    def test_a_changed_source_flags_nothing_when_copies_only_point(self):
        self.edit("skills/feature/SKILL.md", "never run two code-modifying agents", "never run three code-modifying agents")
        code, output, _ = self.check()
        self.assertEqual(code, 0, output)


if __name__ == "__main__":
    unittest.main()
