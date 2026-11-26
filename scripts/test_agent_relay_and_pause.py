import json
import re
import unittest

import test_rule_copies as base
from inc1_support import REPOSITORY, RULES_FILE, SkillsCopy, recorded_pattern

FEATURE = REPOSITORY / "skills" / "feature"
SKILL = "skills/feature/SKILL.md"
HANDOFF = "skills/feature/protocols/context-handoff.md"
SDD = "skills/feature/workflows/sdd.md"
REUSE_SECTION = "4. Roles, agent types and models"
GATES_SECTION = "5. Human decision gates"
ENDING_SECTION = "7. Ending"
NEW_RULES = ("AR-1", "RY-1", "PS-1", "CU-1")
REUSE_POINTER = "`SKILL.md` §4, *Reusing agents*"
RELAY_POINTER = "`protocols/context-handoff.md` §Relay"
PAUSE_POINTER = "`SKILL.md` §7, *Pause and stop everything*"
CATCH_UP_POINTER = "`SKILL.md` §5, *Catch-up in `auto`*"


def section(relative, title):
    lines = (REPOSITORY / relative).read_text(encoding="utf-8").splitlines()
    start = lines.index(f"## {title}") + 1
    taken, in_fence = [], False
    for line in lines[start:]:
        in_fence ^= line.startswith("```")
        if line.startswith("## ") and not in_fence:
            break
        taken.append(line)
    return "\n".join(taken)


def flat(text):
    return re.sub(r"\s+", " ", re.sub(r"[*`]", "", text))


def paragraph(text, opening):
    start = text.index(opening)
    end = text.find("\n\n", start)
    return text[start:end if end != -1 else len(text)]


def rules():
    return {rule["id"]: rule for rule in json.loads(RULES_FILE.read_text(encoding="utf-8"))["rules"]}


class ReuseRuleSource(unittest.TestCase):
    def setUp(self):
        self.text = flat(section(SKILL, REUSE_SECTION))

    def test_d001a_point_follow_up_resumes_at_or_below_the_cap(self):
        self.assertIn("A point follow-up is at most 3 findings or defects in files already in the agent's context", self.text)
        self.assertIn("a point follow-up at or below its model's cap", self.text)

    def test_d001a_relay_triggers(self):
        for trigger in ("its last reported subagent_tokens is above its model's cap",
                        "the task is a fix round larger than a point follow-up, or touches files the agent did not have in its context",
                        "the task is not a point follow-up and the usage is from 100k up to the cap",
                        "a different model was decided for the task",
                        "the agent cannot be resumed"):
            with self.subTest(trigger=trigger):
                self.assertIn(trigger, self.text)

    def test_caps_are_kept_and_the_band_is_a_hypothesis(self):
        self.assertIn("The cap is 200k for sonnet and opus and 400k for haiku", self.text)
        self.assertIn("The 100k band is a hypothesis", self.text)

    def test_fr17_share_of_the_window_is_not_used(self):
        self.assertNotIn("60%", self.text)
        self.assertNotIn("close to the window limit", self.text)

    def test_fr15_ac14_model_and_usage_are_recorded_and_no_record_resumes(self):
        self.assertIn("each resumable agent's ID, its model and its last reported subagent_tokens", self.text)
        self.assertIn("An agent with no recorded subagent_tokens is resumed, and its usage is recorded from its next notification", self.text)
        agents = flat(paragraph((FEATURE / "templates" / "state.md").read_text(encoding="utf-8"), "| Agents |"))
        self.assertIn("agent ID, model and last reported subagent_tokens", agents)

    def test_fr16_the_replacement_is_logged_with_its_reason(self):
        self.assertIn("Log the replacement and its reason in delegations.md", self.text)
        self.assertIn("new, resumed or relay (with its reason)", self.text)
        self.assertIn("The new agent's brief includes the earlier agent's last report", self.text)

    def test_clean_roles_are_never_resumed(self):
        self.assertIn("Critics, verifiers and specialist auditors are never resumed", self.text)


class RelaySource(unittest.TestCase):
    def setUp(self):
        self.text = flat(section(HANDOFF, "Relay"))

    def test_location_is_local_and_never_committed(self):
        self.assertIn("$(git rev-parse --git-common-dir)/feature-workflow/relay/<slug>/<role>.md", self.text)
        self.assertIn("never committed, and available in DIRECT", self.text)
        self.assertIn("overwrites it", self.text)

    def test_the_outgoing_agent_writes_the_notes_and_the_orchestrator_when_it_cannot(self):
        self.assertIn("resumes the outgoing agent for one turn", self.text)
        self.assertIn("writes the notes from the agent's last reports and says so", self.text)

    def test_notes_hold_exploration_only(self):
        self.assertIn("No diffs, no file contents, no logs", self.text)
        for heading in ("## Map", "## Verification", "## Decisions in force", "## Read in full"):
            self.assertIn(heading, section(HANDOFF, "Relay"))

    def test_the_incoming_agent_reads_the_notes_and_the_full_diff(self):
        self.assertIn("reads the notes and the full diff and log of the work so far", self.text)
        self.assertIn("only what the outgoing agent chose to write", self.text)

    def test_relation_to_the_handoff_is_stated_once(self):
        self.assertIn("Relation to the handoff:", self.text)
        relation = re.compile(r"Relation to the handoff")
        hits = [path for path in FEATURE.rglob("*.md") if relation.search(path.read_text(encoding="utf-8"))]
        self.assertEqual([path.name for path in hits], ["context-handoff.md"])


class PauseSource(unittest.TestCase):
    def setUp(self):
        self.text = flat(section(SKILL, ENDING_SECTION))

    def test_ac17_pause_lets_running_agents_finish_and_starts_nothing(self):
        self.assertIn("Pause: start no new delegation for the feature. The agents already running finish", self.text)
        self.assertIn("Only then write state.md with status Paused", self.text)

    def test_ac20_stop_everything_stops_at_once_and_records_ids(self):
        self.assertIn("Stop everything: stop the feature's running agents at once", self.text)
        self.assertIn("each one's ID, role and task, marked interrupted", self.text)

    def test_fr22_resume_state_and_relaunch(self):
        self.assertIn("which agents finished", self.text)
        self.assertIn("which were interrupted, and which work must be relaunched", self.text)
        self.assertIn("Nothing a running agent produced is silently lost or silently trusted", self.text)
        self.assertIn("interrupted work is relaunched, never assumed done", self.text)

    def test_state_template_has_the_stop_row(self):
        text = flat((FEATURE / "templates" / "state.md").read_text(encoding="utf-8"))
        self.assertIn("Agents at the stop | After a pause or a stop everything (SKILL.md §7, Pause and stop everything)", text)


class CatchUpSource(unittest.TestCase):
    def setUp(self):
        self.text = flat(section(SKILL, GATES_SECTION))

    def test_ac18_catch_up_at_each_transition_without_asking(self):
        self.assertIn("Catch-up in auto.", self.text)
        self.assertIn("at each phase or increment transition, without being asked", self.text)
        self.assertIn("the move into acceptance counts", self.text)
        self.assertIn("the start of the feature does not", self.text)
        self.assertIn("In key and full nothing changes", self.text)

    def test_increment_report_points_to_the_catch_up(self):
        gates = flat(section("skills/feature/protocols/gates.md", "Profiles"))
        self.assertIn("off, as in key; the report is the catch-up of SKILL.md §5, Catch-up in auto", gates)
        evo = flat((FEATURE / "workflows" / "evo.md").read_text(encoding="utf-8"))
        self.assertIn("in auto, the catch-up of SKILL.md §5, Catch-up in auto", evo)


class Pointers(unittest.TestCase):
    PLACES = {
        "protocols/agent-questions.md": [REUSE_POINTER, RELAY_POINTER],
        "protocols/multi-feature.md": [PAUSE_POINTER],
        "protocols/hierarchy.md": [PAUSE_POINTER],
        "protocols/phase-runners.md": [RELAY_POINTER, CATCH_UP_POINTER],
        "roles/implementer.md": [RELAY_POINTER],
        "workflows/sdd.md": [REUSE_POINTER],
        "workflows/evo.md": [REUSE_POINTER, CATCH_UP_POINTER],
        "templates/state.md": [REUSE_POINTER, PAUSE_POINTER],
    }

    def test_each_copy_became_a_pointer(self):
        for relative, needed in self.PLACES.items():
            text = (FEATURE / relative).read_text(encoding="utf-8")
            for pointer in needed:
                with self.subTest(file=relative, pointer=pointer):
                    self.assertIn(pointer, text)

    def test_fr24_readme_and_docs_link_without_numbers(self):
        for relative in ("README.md", "docs/architecture.md"):
            text = (REPOSITORY / relative).read_text(encoding="utf-8")
            with self.subTest(file=relative):
                self.assertNotRegex(text, r"\b[24]00k\b")
                self.assertIn("§Relay", text)
                self.assertRegex(text, r"SKILL\.md`?\)? §7")
                self.assertRegex(text, r"SKILL\.md`?\)? §5")

    def test_larger_fix_rounds_no_longer_go_to_a_handoff(self):
        for relative in ("README.md", "docs/architecture.md", "skills/feature/SKILL.md", "skills/feature/roles/implementer.md"):
            with self.subTest(file=relative):
                self.assertNotRegex((REPOSITORY / relative).read_text(encoding="utf-8"), r"new (?:agent|Implementer)[^.]{0,30}with a handoff")


class NewRulesRecorded(unittest.TestCase):
    def setUp(self):
        self.rules = rules()

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
                self.assertGreaterEqual(len(found), 3, found)


class Restatements(SkillsCopy):
    PARAPHRASES = {
        "AR-1": ["Resume an agent only below 200k for sonnet.",
                 "Caps: opus 200k, haiku 400k.",
                 "Each model has a cap of 300k.",
                 "Over 120k tokens, relay the agent.",
                 "Replace the agent when it is past 150k.",
                 "The 100k band is a guess.",
                 "A point follow-up means up to three findings.",
                 "Send at most 3 defects to an agent that has them in context.",
                 "Replace the agent when subagent_tokens exceeds the limit.",
                 "An agent is resumed only while its context is small."],
        "RY-1": ["Resume the old agent for one final turn.",
                 "The notes contain only what the agent chose to write.",
                 "Keep no diffs, no contents.",
                 "If it cannot answer, the orchestrator writes the notes itself.",
                 "The new agent reads the notes plus the whole diff."],
        "PS-1": ["On pause, start no new agents.",
                 "When paused, no new delegation is started.",
                 "Let running agents complete before pausing.",
                 "Stop every running agent at once.",
                 "Interrupted work is never assumed done.",
                 "Partial output is never silently lost."],
        "CU-1": ["The move into acceptance counts as a transition.",
                 "The start of the feature does not get one.",
                 "Send a catch-up without being asked.",
                 "Without asking, the programmer gets a catch-up."],
    }
    NAMED = {"AR-1": "Mind the token cap.",
             "RY-1": "Write relay notes first.",
             "PS-1": "To stop everything, record the IDs.",
             "CU-1": "A catch-up goes out at each phase transition."}

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
        accepted = [f"Stay under the model's cap ({REUSE_POINTER}).",
                    f"Write relay notes ({RELAY_POINTER}).",
                    f"To stop everything, see {PAUSE_POINTER}.",
                    f"A catch-up at each phase transition ({CATCH_UP_POINTER}).",
                    "A catch-up at each increment ([`SKILL.md`](skills/feature/SKILL.md) §5)."]
        for text in accepted:
            with self.subTest(text=text):
                self.assertFalse(self.reported(text))

    def test_pointer_to_another_section_does_not_cover_the_name(self):
        self.assertTrue(self.reported("To stop everything, see `SKILL.md` §5."))
        self.assertTrue(self.reported("Write relay notes (`protocols/gates.md` §Hard stops)."))

    def test_named_far_from_its_pointer_is_a_copy(self):
        self.assertTrue(self.reported(f"Write relay notes{' and so on' * 10} ({RELAY_POINTER})."))

    def test_unrelated_wording_is_not_a_copy(self):
        for text in ("Stop the increment at once when a discovery blocks it.",
                     "A catch-up the programmer asks for.",
                     "The orchestrator relays the questions.",
                     "Pausing features is the programmer's decision.",
                     "Run at most 3 checks per file."):
            with self.subTest(text=text):
                self.assertFalse(self.reported(text))

    def test_moving_the_relay_out_of_its_section_reports_it(self):
        self.edit(HANDOFF, "## Relay\n", "## Relay\n\nSee below.\n\n## Replacements\n")
        code, output, _ = self.check("skills")
        self.assertEqual(code, 1, output)
        self.assertIn(f"{HANDOFF}:", output)
        self.assertIn(" RY-1 ", output)


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
