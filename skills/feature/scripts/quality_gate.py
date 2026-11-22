#!/usr/bin/env python3
import argparse
import ast
import fnmatch
import io
import json
import re
import shutil
import subprocess
import sys
import tokenize
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_LIMITS = {"fileLines": 400, "functionLines": 30, "parameters": 4, "cyclomaticComplexity": 10}

HASH_COMMENT = r"^#"
C_COMMENT = r"^(//|/\*|\*(\s|/|$))"
DASH_COMMENT = r"^--"
MARKUP_COMMENT = r"^<!--"
PYTHON_SUFFIXES = (".py", ".pyi")

COMMENT_SYNTAX = {
    **{ext: [HASH_COMMENT] for ext in PYTHON_SUFFIXES},
    **{ext: [HASH_COMMENT] for ext in (".rb", ".sh", ".bash", ".zsh", ".ex", ".exs", ".pl", ".r", ".jl", ".nim")},
    **{ext: [C_COMMENT] for ext in (
        ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts", ".java", ".kt", ".kts", ".scala",
        ".go", ".rs", ".c", ".h", ".cc", ".cpp", ".hpp", ".cs", ".swift", ".dart", ".php", ".m", ".groovy",
        ".css", ".scss", ".less",
    )},
    **{ext: [DASH_COMMENT, C_COMMENT] for ext in (".sql",)},
    **{ext: [DASH_COMMENT] for ext in (".lua", ".hs", ".elm")},
    **{ext: [C_COMMENT, MARKUP_COMMENT] for ext in (".vue", ".svelte", ".astro")},
    **{ext: [MARKUP_COMMENT] for ext in (".html", ".htm")},
}

TOOL_DIRECTIVES = [
    r"^#!", r"eslint-(disable|enable)", r"@ts-(expect-error|ignore|nocheck)", r"\bnoqa\b", r"type:\s*ignore",
    r"\b(pyright|mypy|pylint|rubocop|swiftlint|stylelint-disable|biome-ignore)\b", r"\bnolint\b",
    r"prettier-ignore", r"(istanbul|c8|v8) ignore", r"ast-grep-ignore", r"nosemgrep", r"-\*-\s*coding",
    r"SPDX-License-Identifier", r"^//go:", r"frozen_string_literal:", r"webpackChunkName", r"@vite-ignore",
    r"NOSONAR", r"@jsx", r"#\s*(region|endregion)\b",
]

SHORTCUT_MARKER = r"shortcut:"
COMPLETE_SHORTCUT = r"shortcut:\s*[^,]*\S[^,]*,\s*\S"
HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
LIZARD_WARNING = re.compile(r"^(?P<path>.+?):(?P<line>\d+): warning: (?P<name>.+?) has (?P<metrics>.+)$")
LIZARD_LENGTH = re.compile(r"(\d+) length")


@dataclass
class Violation:
    check: str
    location: str
    detail: str


@dataclass
class GateResult:
    files: list = field(default_factory=list)
    violations: list = field(default_factory=list)
    notes: list = field(default_factory=list)
    shortcuts: list = field(default_factory=list)
    not_checked: list = field(default_factory=list)
    project_checks: list = field(default_factory=list)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Feature workflow quality gate")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--base", default="HEAD")
    parser.add_argument("--config")
    return parser.parse_args()


def run_git(repo, *arguments):
    completed = subprocess.run(["git", "-C", str(repo), *arguments], capture_output=True, text=True)
    return completed.stdout if completed.returncode == 0 else None


def registry_directory(repo):
    versioned = repo / ".quality"
    if versioned.is_dir():
        return versioned
    common = run_git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
    return Path(common.strip()) / "quality" if common else versioned


def load_config(repo, explicit_path):
    path = Path(explicit_path) if explicit_path else registry_directory(repo) / "config.json"
    if not path.is_file():
        return {"limits": dict(DEFAULT_LIMITS), "exclude": [], "allowedCommentPatterns": [], "checks": [], "allowDocstrings": False}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        "limits": {**DEFAULT_LIMITS, **raw.get("limits", {})},
        "exclude": raw.get("exclude", []),
        "allowedCommentPatterns": raw.get("allowedCommentPatterns", []),
        "checks": raw.get("checks", []),
        "allowDocstrings": raw.get("allowDocstrings", False),
    }


def is_excluded(path, patterns):
    candidates = [pattern.removeprefix("**/") for pattern in patterns] + patterns
    return any(fnmatch.fnmatch(path, pattern) for pattern in candidates)


def changed_code_files(repo, base, exclude):
    tracked = run_git(repo, "diff", "--name-only", "--diff-filter=ACMR", base) or ""
    untracked = run_git(repo, "ls-files", "--others", "--exclude-standard") or ""
    paths = sorted(set(tracked.splitlines()) | set(untracked.splitlines()))
    return [
        path for path in paths
        if Path(path).suffix.lower() in COMMENT_SYNTAX and not is_excluded(path, exclude) and (repo / path).is_file()
    ]


def added_lines_from_diff(diff_text):
    added, next_line = {}, 0
    for raw_line in diff_text.splitlines():
        header = HUNK_HEADER.match(raw_line)
        if header:
            next_line = int(header.group(1))
        elif raw_line.startswith("+") and not raw_line.startswith("+++"):
            added[next_line] = raw_line[1:]
            next_line += 1
        elif not raw_line.startswith("-"):
            next_line += 1
    return added


def added_lines(repo, base, path):
    if run_git(repo, "ls-files", "--error-unmatch", path) is None:
        text = (repo / path).read_text(encoding="utf-8", errors="replace")
        return dict(enumerate(text.splitlines(), start=1))
    return added_lines_from_diff(run_git(repo, "diff", "-U0", base, "--", path) or "")


def line_count(text):
    return len(text.splitlines()) if text is not None else None


def check_file_length(repo, base, path, limit, result):
    current = line_count((repo / path).read_text(encoding="utf-8", errors="replace"))
    previous = line_count(run_git(repo, "show", f"{base}:{path}"))
    if current <= limit:
        return
    if previous is not None and current <= previous:
        result.notes.append(f"`{path}` has {current} lines (limit {limit}); already over the limit at base and did not grow.")
        return
    if previous is not None and previous > limit:
        result.notes.append(f"`{path}` grew from {previous} to {current} lines; already over the limit ({limit}) at base. A fact to report: the project's structure puts this code here.")
        return
    origin = "new file" if previous is None else f"grew from {previous}"
    result.violations.append(Violation("file length", path, f"{current} lines > {limit} ({origin})"))


def comment_patterns_for(path):
    return COMMENT_SYNTAX[Path(path).suffix.lower()]


def is_comment(content, patterns):
    return any(re.match(pattern, content) for pattern in patterns)


def is_tool_directive(content, extra_patterns):
    return any(re.search(pattern, content) for pattern in TOOL_DIRECTIVES + extra_patterns)


def classify_comment(location, content, extra_patterns, result):
    if re.search(SHORTCUT_MARKER, content):
        result.shortcuts.append((location, content))
        if not re.search(COMPLETE_SHORTCUT, content):
            result.violations.append(Violation("shortcut marker", location, "missing `<limit>, <when to upgrade>`"))
        return
    if not is_tool_directive(content, extra_patterns):
        result.violations.append(Violation("comment", location, f"`{content[:80]}`"))


def python_comments(text):
    comments = {}
    for token in tokenize.generate_tokens(io.StringIO(text).readline):
        if token.type == tokenize.COMMENT:
            comments[token.start[0]] = token.string
    return comments


def python_docstring_spans(text):
    holders = (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
    spans = {}
    for node in ast.walk(ast.parse(text)):
        first = node.body[0] if isinstance(node, holders) and node.body else None
        if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
            spans[first.lineno] = range(first.lineno, first.end_lineno + 1)
    return spans


def check_python_comments(repo, path, lines, config, result):
    text = (repo / path).read_text(encoding="utf-8", errors="replace")
    try:
        comments, docstrings = python_comments(text), python_docstring_spans(text)
    except (SyntaxError, tokenize.TokenError):
        result.notes.append(f"`{path}` does not parse; its comments were checked by pattern only.")
        return check_pattern_comments(path, lines, config["allowedCommentPatterns"], result)
    for number, content in sorted(comments.items()):
        if number in lines:
            classify_comment(f"{path}:{number}", content.strip(), config["allowedCommentPatterns"], result)
    if config["allowDocstrings"]:
        return
    for start, span in sorted(docstrings.items()):
        if any(number in lines for number in span):
            result.violations.append(Violation("docstring", f"{path}:{start}", "docstrings are off for this project (`allowDocstrings`)"))


def check_pattern_comments(path, lines, extra_patterns, result):
    patterns = comment_patterns_for(path)
    for number, raw in sorted(lines.items()):
        content = raw.strip()
        if content and is_comment(content, patterns):
            classify_comment(f"{path}:{number}", content, extra_patterns, result)


def check_comments(repo, path, lines, config, result):
    if Path(path).suffix.lower() in PYTHON_SUFFIXES:
        return check_python_comments(repo, path, lines, config, result)
    return check_pattern_comments(path, lines, config["allowedCommentPatterns"], result)


def lizard_command(limits, paths):
    return [
        "lizard", "--warnings_only",
        "-L", str(limits["functionLines"]),
        "-a", str(limits["parameters"]),
        "-C", str(limits["cyclomaticComplexity"]),
        *paths,
    ]


def function_span(line, metrics):
    length = LIZARD_LENGTH.search(metrics)
    return range(line, line + (int(length.group(1)) if length else 1))


def touches_added_lines(span, added):
    return any(number in added for number in span)


def check_functions(repo, paths, added_by_path, limits, result):
    if shutil.which("lizard") is None:
        result.not_checked.append("Function length, parameters and complexity: `lizard` is not installed; the Critic checks them manually.")
        return
    completed = subprocess.run(lizard_command(limits, paths), cwd=repo, capture_output=True, text=True)
    for raw_line in completed.stdout.splitlines():
        warning = LIZARD_WARNING.match(raw_line.strip())
        if warning:
            record_function_warning(warning, added_by_path, result)


def record_function_warning(warning, added_by_path, result):
    path, line = warning.group("path").removeprefix("./"), int(warning.group("line"))
    span = function_span(line, warning.group("metrics"))
    if touches_added_lines(span, added_by_path.get(path, {})):
        location = f"{path}:{line}"
        result.violations.append(Violation("function size", location, f"{warning.group('name')}: {warning.group('metrics')}"))


def run_project_check(repo, check):
    name = check.get("name", check["command"])
    try:
        completed = subprocess.run(check["command"], shell=True, cwd=repo, capture_output=True, text=True, timeout=900)
    except subprocess.TimeoutExpired:
        return {"name": name, "passed": False, "covers": check.get("covers", []), "output": ["timed out after 900 s"]}
    output = (completed.stdout + completed.stderr).strip().splitlines()[-20:]
    return {"name": name, "passed": completed.returncode == 0,
            "covers": check.get("covers", []), "output": output}


def run_project_checks(repo, checks, result):
    for check in checks:
        outcome = run_project_check(repo, check)
        result.project_checks.append(outcome)
        if not outcome["passed"]:
            result.violations.append(Violation("project check", outcome["name"], "non-zero exit; see output below"))


def evaluate(repo, base, config):
    result = GateResult()
    result.files = changed_code_files(repo, base, config["exclude"])
    added_by_path = {path: added_lines(repo, base, path) for path in result.files}
    for path in result.files:
        check_file_length(repo, base, path, config["limits"]["fileLines"], result)
        check_comments(repo, path, added_by_path[path], config, result)
    if result.files:
        check_functions(repo, result.files, added_by_path, config["limits"], result)
    run_project_checks(repo, config["checks"], result)
    result.not_checked.append("Trailing comments after code are detected in Python only; elsewhere an ast-grep `kind: comment` rule detects them exactly.")
    result.not_checked.append("Nesting depth, naming and single responsibility: manual review.")
    return result


def render_violations(violations):
    if not violations:
        return ["## Violations (0)", "", "None."]
    rows = [f"| {item.check} | `{item.location}` | {item.detail} |" for item in violations]
    return [f"## Violations ({len(violations)})", "", "| Check | Location | Detail |", "| --- | --- | --- |", *rows]


def render_project_checks(project_checks):
    if not project_checks:
        return ["## Project checks", "", "None configured in the registry's `config.json`."]
    lines = ["## Project checks", ""]
    for outcome in project_checks:
        status = "passed" if outcome["passed"] else "FAILED"
        covers = ", ".join(outcome["covers"]) or "-"
        lines += [f"- **{outcome['name']}**: {status} (covers {covers})"]
        lines += [f"    {line}" for line in outcome["output"]] if not outcome["passed"] else []
    return lines


def render(repo, base, result):
    header = ["# Quality gate", "", f"Repository `{repo}` · base `{base}` · {len(result.files)} changed code files", ""]
    shortcuts = [f"- `{location}` {content}" for location, content in result.shortcuts] or ["None."]
    sections = [
        render_violations(result.violations), [""],
        [f"## Shortcut markers added ({len(result.shortcuts)})", "", *shortcuts, ""],
        render_project_checks(result.project_checks), [""],
        ["## Notes", "", *([f"- {note}" for note in result.notes] or ["None."]), ""],
        ["## Not checked", "", *[f"- {item}" for item in result.not_checked]],
    ]
    return "\n".join(header + [line for section in sections for line in section])


def main():
    arguments = parse_arguments()
    repo = Path(arguments.repo).resolve()
    if run_git(repo, "rev-parse", "--verify", f"{arguments.base}^{{commit}}") is None:
        print(f"quality gate: `{arguments.base}` is not a commit in {repo}", file=sys.stderr)
        return 2
    result = evaluate(repo, arguments.base, load_config(repo, arguments.config))
    print(render(repo, arguments.base, result))
    return 1 if result.violations else 0


if __name__ == "__main__":
    sys.exit(main())
