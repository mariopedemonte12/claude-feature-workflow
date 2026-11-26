import json
import re
import unittest

import test_rule_copies as base
from inc1_support import REPOSITORY, RULES_FILE, SkillsCopy

FEATURE = REPOSITORY / "skills" / "feature"
SDD = "skills/feature/workflows/sdd.md"
EDGE_CASES = "skills/feature/knowledge/edge-cases.md"
TEST_DESIGNER = "skills/feature/roles/test-designer.md"
IMPLEMENTER = "skills/feature/roles/implementer.md"
NEW_RULES = ("CS-1", "DC-1", "TX-1", "CV-1")
CONCEPT_POINTER = "`knowledge/edge-cases.md` §Before code, step 1"
DEPENDENT_POINTER = "`roles/test-designer.md` §Decisions that cases depend on"
TEXT_POINTER = "`roles/test-designer.md` §Cases that check text"
VERIFICATION_POINTER = "`roles/implementer.md` §Rules touched and verification"


def section(relative, title):
    lines = (REPOSITORY / relative).read_text(encoding="utf-8").splitlines()
    start = lines.index(f"## {title}") + 1
    taken = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        taken.append(line)
    return "\n".join(taken)


def flat(text):
    return re.sub(r"\s+", " ", re.sub(r"[*`]", "", text))


def rules():
    return {rule["id"]: rule for rule in json.loads(RULES_FILE.read_text(encoding="utf-8"))["rules"]}


def text_of(relative):
    return flat((FEATURE / relative).read_text(encoding="utf-8"))


class ConceptSearchSource(unittest.TestCase):
    def setUp(self):
        self.text = flat(section(EDGE_CASES, "Before code"))

    def test_fr12_search_by_concept_with_every_search_recorded(self):
        self.assertIn("Search by concept, not only by string", self.text)
        for word in ("synonyms", "paraphrases", "restatements", "apply it without naming it"):
            with self.subTest(word=word):
                self.assertIn(word, self.text)
        self.assertIn("Record every search run, literal and conceptual", self.text)

    def test_fr13_a_late_find_is_a_discovery_and_its_search_is_recorded(self):
        self.assertIn("recorded as a discovery against the recorded searches", self.text)
        self.assertIn("the search that found it is added to the record", self.text)

    def test_ac11_each_first_mapping_points_to_the_source(self):
        for relative in ("roles/spec-writer.md", "roles/repository-analyst.md", "roles/reviewer.md", "workflows/evo.md",
                         "protocols/executor.md", "knowledge/specification-guide.md", "templates/specification.md",
                         "templates/feature-card.md"):
            with self.subTest(file=relative):
                self.assertIn("edge-cases.md` §Before code", (FEATURE / relative).read_text(encoding="utf-8"))

    def test_ac12_the_discovery_lists_where_its_search_is_recorded(self):
        self.assertIn("Its place in the record", text_of("knowledge/specification-guide.md"))


class DependentCasesSource(unittest.TestCase):
    def setUp(self):
        self.text = flat(section(TEST_DESIGNER, "Decisions that cases depend on"))

    def test_fr19_each_case_records_what_it_depends_on(self):
        self.assertIn("Each case records the decision(s) and statement(s) it depends on", self.text)
        self.assertIn("Depends on", text_of("templates/testing-plan.md"))

    def test_fr18_resumed_at_once_before_the_next_run_and_not_when_nothing_depends(self):
        self.assertIn("resumed or relayed at once", self.text)
        self.assertIn("before the Tester's next run", self.text)
        self.assertIn("Retire or update every case that depends on it", self.text)
        self.assertIn("When no case depends on the change, you are not resumed", self.text)

    def test_ac15_the_tester_never_runs_a_superseded_case(self):
        self.assertIn("The Tester never runs a case that asserts a superseded decision", self.text)
        self.assertIn("superseded decision", text_of("roles/tester.md"))

    def test_resume_and_relay_are_pointed_to_not_restated(self):
        self.assertIn("`SKILL.md` §4, *Reusing agents*", section(TEST_DESIGNER, "Decisions that cases depend on"))
        self.assertNotRegex(self.text, r"\b[24]00k\b")

    def test_places_point_to_the_source(self):
        for relative in ("SKILL.md", "workflows/evo.md", "workflows/sdd.md", "roles/tester.md", "templates/feature-card.md"):
            with self.subTest(file=relative):
                self.assertIn("test-designer.md` §Decisions that cases depend on", (FEATURE / relative).read_text(encoding="utf-8"))


class TextCheckSource(unittest.TestCase):
    def test_fr20_ac16_text_checks_assert_presence_and_meaning(self):
        text = flat(section(TEST_DESIGNER, "Cases that check text"))
        self.assertIn("asserts the presence and the meaning of what the source requires, not its exact wording", text)
        self.assertIn("an intended rewording that keeps the rule does not fail it", text)
        self.assertIn("When the meaning changes, the case fails", text)


class VerificationSource(unittest.TestCase):
    def setUp(self):
        self.text = flat(section(IMPLEMENTER, "Rules touched and verification"))

    def test_every_copy_is_searched_and_fixed_in_the_same_round(self):
        self.assertIn("search `skills/`, `README.md` and `docs/` for all its copies".replace("`", ""), self.text)
        self.assertIn("fix them in the same round", self.text)

    def test_verification_runs_after_committing_on_a_clean_tree_as_separate_steps(self):
        self.assertIn("Commit the work first", self.text)
        self.assertIn("on a clean tree", self.text)
        self.assertIn("each as a separate step", self.text)
        self.assertIn("compare the base commit with the committed HEAD", self.text)
        for command in ("copy checker", "unit tests", "quality gate"):
            with self.subTest(command=command):
                self.assertIn(command, self.text)

    def test_briefs_and_workflows_point_to_the_source(self):
        for relative in ("SKILL.md", "workflows/direct.md", "workflows/sdd.md", "workflows/evo.md", "protocols/executor.md",
                         "protocols/gates.md", "protocols/review-cycle.md", "protocols/context-handoff.md", "templates/final-report.md"):
            with self.subTest(file=relative):
                self.assertIn("implementer.md §Rules touched and verification", text_of(relative))


class RulesRecorded(unittest.TestCase):
    def test_each_new_rule_has_a_source_fingerprints_and_a_concept_search(self):
        for identifier in NEW_RULES:
            rule = rules()[identifier]
            with self.subTest(rule=identifier):
                self.assertTrue(rule["fingerprints"] and rule["searches"] and rule["source"]["section"])

    def test_the_fingerprints_find_the_wording_of_their_own_source(self):
        for identifier in NEW_RULES:
            rule = rules()[identifier]
            source = flat(section(rule["source"]["file"], rule["source"]["section"]))
            found = [pattern for pattern in rule["fingerprints"] + rule["names"] if re.search(pattern, source, re.IGNORECASE)]
            with self.subTest(rule=identifier):
                self.assertGreaterEqual(len(found), 3, found)


class Restatements(SkillsCopy):
    PARAPHRASES = {
        "CS-1": ["Search for the meaning of the rule too.",
                 "Check synonyms and the places where the rule applies.",
                 "List the places that apply it without naming it.",
                 "Search not only by the exact wording.",
                 "Literal strings are not enough.",
                 "The search that found it is recorded for reuse.",
                 "A mapping with only literal searches is incomplete."],
        "DC-1": ["Retire or update every case that depends on it.",
                 "If no case depends on it, skip the Test Designer.",
                 "The Tester never runs a case that asserts a superseded decision.",
                 "Each case records the decision it depends on.",
                 "The dependent cases are retired at once.",
                 "The Test Designer is resumed at once when a decision changes.",
                 "A superseded decision reaches a case the Tester must not run."],
        "TX-1": ["Assert the presence and the meaning.",
                 "Check the meaning, not the exact wording.",
                 "A rewording does not fail the case.",
                 "Brittle text checks break on edits.",
                 "Prose checks compare meaning."],
        "CV-1": ["Search the repo for all its copies.",
                 "Find every copy of the rule.",
                 "Each copy is fixed in the same round.",
                 "Fix them in the same round.",
                 "Some tests compare the base commit with the committed HEAD.",
                 "Running on uncommitted changes proves nothing.",
                 "Run each as separate steps on a clean tree.",
                 "Verify on a clean tree, as separate steps."],
    }
    NAMED = {"CS-1": "Searched by concept.",
             "DC-1": "Done before the Tester's next run.",
             "TX-1": "Text checks need care.",
             "CV-1": "Run it after committing."}

    def test_negative_each_fingerprint_has_a_paraphrase_it_finds(self):
        recorded = rules()
        for identifier, texts in self.PARAPHRASES.items():
            patterns = recorded[identifier]["fingerprints"]
            self.assertEqual(len(texts), len(patterns), identifier)
            for pattern, text in zip(patterns, texts):
                with self.subTest(rule=identifier, text=text):
                    self.assertRegex(flat(text), re.compile(pattern, re.IGNORECASE))

    def test_negative_each_paraphrase_appended_to_a_scratch_copy_is_reported(self):
        cases = [(identifier, text) for identifier, texts in self.PARAPHRASES.items() for text in texts]
        cases += list(self.NAMED.items())
        for identifier, text in cases:
            with self.subTest(rule=identifier, text=text):
                line = self.append(SDD, text)
                code, output, _ = self.check("skills")
                self.edit(SDD, "\n\n" + text + "\n", "\n")
                self.assertEqual(code, 1, output)
                self.assertIn(f"{SDD}:{line}: {identifier} ", output)

    def test_named_next_to_its_pointer_is_not_a_copy(self):
        accepted = [f"Searched by concept ({CONCEPT_POINTER}).",
                    f"Done before the Tester's next run ({DEPENDENT_POINTER}).",
                    f"Text checks follow {TEXT_POINTER}.",
                    f"Run it after committing ({VERIFICATION_POINTER}).",
                    f"On a clean tree, as {VERIFICATION_POINTER} says."]
        for text in accepted:
            with self.subTest(text=text):
                self.assertFalse(self.reported(text))

    def test_pointer_to_another_section_does_not_cover_the_name(self):
        self.assertTrue(self.reported("Run it after committing (`protocols/gates.md` §Hard stops)."))

    def test_unrelated_wording_is_not_a_copy(self):
        for text in ("Search the logs for errors.",
                     "Commit the work with a clear message.",
                     "The Test Designer designs the cases.",
                     "Run the unit tests of the module.",
                     "A synonym list for the glossary."):
            with self.subTest(text=text):
                self.assertFalse(self.reported(text))


class CurrentTree(unittest.TestCase):
    def test_no_copy_of_the_new_rules_anywhere(self):
        code, output, _ = base.run_check(REPOSITORY)
        reported = [line for line in output.splitlines() if any(f" {rule} " in line for rule in NEW_RULES)]
        self.assertEqual(reported, [])

    def test_skills_tree_is_clean(self):
        code, output, _ = base.run_check(REPOSITORY, "skills")
        self.assertEqual(code, 0, output)


if __name__ == "__main__":
    unittest.main()
