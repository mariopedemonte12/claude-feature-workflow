# Seed catalog: general

Applies to every project. Seed IDs are renumbered as `AP-NNN` when adopted. "Detect" says how the entry can be automated.

| Seed | Smell | Why it hurts | Instead | Detect |
| --- | --- | --- | --- | --- |
| G-01 | God module or class: one unit owns several unrelated concerns | Every change touches it; conflicts and regressions concentrate there | Split by responsibility (one reason to change each) | File-length limit as a signal; manual |
| G-02 | Long function mixing levels of abstraction | Hard to read, test and reuse in parts | Orchestrating function calling named steps | Function-length and complexity limits (lizard) |
| G-03 | Explanatory comments instead of expressive code | Comments drift from the code and lie | Extract and name; record the why in decisions or commits | Quality gate comment check; ast-grep `kind: comment` |
| G-04 | Vague names (`data`, `info`, `manager`, `helper`, `utils`, `handle`, `process`) | The reader must open the code to know what it does | Declarative domain names | ast-grep or linter naming rules on identifiers |
| G-05 | Magic numbers and strings carrying domain meaning | The meaning and every copy must be found by hand | Named constants or types | Linter rule (e.g. no-magic-numbers); manual |
| G-06 | Boolean flag parameter that switches behavior | Two functions hidden in one; call sites unreadable (`send(true)`) | Two functions, or an options object with named fields | ast-grep on boolean literals in call arguments |
| G-07 | Long parameter list | Argument order errors; signals a missing concept | Parameter object or a smaller responsibility | lizard parameter count |
| G-08 | Deep nesting | Paths are hard to follow and to test | Guard clauses, early returns, extracted predicates | Complexity limit; manual for depth |
| G-09 | Duplicated logic that must change together | Fixes land in one copy only | One shared function, once a second real use exists | jscpd or similar duplication tool; manual |
| G-10 | Speculative generality: interface with one implementation, factory with one product, unused options or config | Code to read and maintain for a need that does not exist | Concrete code; abstract when the second case arrives | Manual |
| G-11 | Primitive obsession: domain concepts as raw strings or numbers (money as float, ids as plain strings mixed up) | Invalid values pass silently; rules are scattered | Small value types with validation at creation | Manual; type-checker rules where available |
| G-12 | Swallowed errors (empty catch, ignored error return) | Failures become silent data loss | Handle, propagate or report with context | Linter (empty catch, errcheck); ast-grep |
| G-13 | Hidden global mutable state (module-level singletons used for state) | Order-dependent behavior; tests interfere | Pass dependencies in; scope state to its owner | ast-grep on module-level mutable assignments; manual |
| G-14 | Feature envy: a function mostly uses another module's data | Logic lives far from the data it depends on | Move the behavior next to the data | Manual |
| G-15 | Shotgun surgery: one change needs edits in many unrelated files | Missed edits become bugs | Co-locate what changes together | Manual (diff spread in review) |
| G-16 | Dead code: unused functions, exports, branches, flags | Misleads readers; keeps obsolete paths alive | Delete it | Linter unused rules; knip, vulture, deadcode tools |
| G-17 | Shortcut marker without an upgrade trigger | Deferred work becomes permanent unnoticed | `shortcut: <limit>, <when to upgrade>` | Quality gate |
