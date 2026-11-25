#!/usr/bin/env python3
import argparse
import bisect
import fnmatch
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_RULES = Path(__file__).with_name("rule_copies.json")
EXIT_CLEAN, EXIT_FOUND, EXIT_CONFIG = 0, 1, 2
MARKUP = re.compile(r"[*`]")
WHITESPACE = re.compile(r"\s+")
HEADING = re.compile(r"^(#{1,6})\s+(.+?)(?:\s+#+)?\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
NUMBER_WORDS = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
                "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10"}


class ConfigError(Exception):
    pass


class UnreadableFile(Exception):
    pass


@dataclass(frozen=True)
class Rule:
    identifier: str
    source_path: str
    source_section: str
    fingerprints: tuple


@dataclass(frozen=True)
class FlatText:
    text: str
    line_starts: list

    def line_at(self, offset):
        return bisect.bisect_right(self.line_starts, offset)


@dataclass(frozen=True)
class Copy:
    path: str
    line: int
    rule: str
    excerpt: str
    value: str
    source_values: frozenset

    def describe(self):
        head = f"{self.path}:{self.line}: {self.rule} restated copy: \"{self.excerpt}\""
        if self.value is None:
            return head
        if self.value in self.source_values:
            return f"{head} (value {self.value}, agrees with the source)"
        source = ", ".join(sorted(self.source_values)) or "no value"
        return f"{head} (value {self.value}, DISAGREES: source says {source})"


def parse_arguments(argv):
    parser = argparse.ArgumentParser(description="Report restated copies of workflow rules outside their single source")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--rules", default=str(DEFAULT_RULES))
    parser.add_argument("paths", nargs="*", help="files or folders to scan, relative to --repo; default: the data file's scan.paths")
    return parser.parse_args(argv)


def compile_fingerprint(pattern, identifier):
    try:
        return re.compile(pattern, re.IGNORECASE)
    except re.error as error:
        raise ConfigError(f"rule {identifier}: invalid fingerprint {pattern!r}: {error}") from error


def parse_rule(raw):
    try:
        identifier, source = raw["id"], raw["source"]
        fingerprints = tuple(compile_fingerprint(pattern, identifier) for pattern in raw["fingerprints"])
        return Rule(identifier, source["file"], source["section"], fingerprints)
    except (KeyError, TypeError) as error:
        raise ConfigError(f"malformed rule entry {raw!r}: missing {error}") from error


def load_data(path):
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        scan = raw.get("scan", {})
        return [parse_rule(entry) for entry in raw["rules"]], scan.get("paths", ["."]), scan.get("exclude", [])
    except (OSError, ValueError, KeyError, AttributeError) as error:
        raise ConfigError(f"cannot load rules from {path}: {error}") from error


def read_markdown(path):
    try:
        data = path.read_bytes()
    except OSError as error:
        raise UnreadableFile(error.strerror or str(error)) from error
    if b"\0" in data:
        raise UnreadableFile("binary content")
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise UnreadableFile(f"not UTF-8 ({error.reason} at byte {error.start})") from error


def flatten(lines):
    pieces, line_starts, offset = [], [], 0
    for line in lines:
        piece = WHITESPACE.sub(" ", MARKUP.sub("", line)).strip() + " "
        line_starts.append(offset)
        pieces.append(piece)
        offset += len(piece)
    return FlatText("".join(pieces), line_starts)


def heading_of(line):
    match = HEADING.match(line)
    if not match:
        return None
    return len(match.group(1)), WHITESPACE.sub(" ", MARKUP.sub("", match.group(2))).strip().lower()


def section_span(lines, title):
    wanted, start, level, in_fence = title.strip().lower(), None, 0, False
    for number, line in enumerate(lines, start=1):
        if FENCE.match(line):
            in_fence = not in_fence
        heading = None if in_fence else heading_of(line)
        if heading and start is not None and heading[0] <= level:
            return start, number - 1
        if heading and start is None and heading[1] == wanted:
            start, level = number, heading[0]
    if start is None:
        return None
    return start, len(lines)


def normalized_value(match):
    if "value" not in match.re.groupindex or match.group("value") is None:
        return None
    value = match.group("value").lower()
    return NUMBER_WORDS.get(value, value)


def fingerprint_matches(flat, rule):
    matches = sorted((match for fingerprint in rule.fingerprints for match in fingerprint.finditer(flat.text)),
                     key=lambda match: (match.start(), -match.end()))
    covered_until = -1
    for match in matches:
        if match.start() >= covered_until:
            covered_until = match.end()
            yield flat.line_at(match.start()), match.group(0).strip(), normalized_value(match)


def source_values(repo, rule):
    try:
        lines = read_markdown(repo / rule.source_path).splitlines()
    except UnreadableFile as error:
        raise ConfigError(f"rule {rule.identifier}: source {rule.source_path} unreadable: {error}") from error
    span = section_span(lines, rule.source_section)
    if span is None:
        raise ConfigError(f"rule {rule.identifier}: section '{rule.source_section}' not found in {rule.source_path}")
    flat = flatten(lines[span[0] - 1:span[1]])
    values = {value for _, _, value in fingerprint_matches(flat, rule) if value is not None}
    return span, frozenset(values)


def is_excluded(relative, patterns):
    return any(fnmatch.fnmatch(relative, pattern) for pattern in patterns)


def relative_to_repo(path, repo):
    return Path(os.path.relpath(path, repo)).as_posix()


def markdown_files(repo, paths, exclude):
    found, unreadable = set(), []
    for path in paths:
        target = repo / path
        if target.is_dir():
            walk_errors = []
            for folder, _, names in os.walk(target, onerror=walk_errors.append):
                found.update(Path(folder) / name for name in names if name.endswith(".md"))
            unreadable += [(relative_to_repo(error.filename, repo), error.strerror) for error in walk_errors]
        elif target.is_file() or target.is_symlink():
            found.add(target)
        else:
            unreadable.append((path, "not found"))
    relatives = sorted(relative_to_repo(file, repo) for file in found)
    return [relative for relative in relatives if not is_excluded(relative, exclude)], unreadable


def copies_in_file(relative, lines, rules, sources):
    flat = flatten(lines)
    for rule in rules:
        (start, end), values = sources[rule.identifier]
        own_source = relative == rule.source_path
        for line, excerpt, value in fingerprint_matches(flat, rule):
            if not (own_source and start <= line <= end):
                yield Copy(relative, line, rule.identifier, excerpt, value, values)


def scan(repo, rules, relatives):
    sources = {rule.identifier: source_values(repo, rule) for rule in rules}
    copies, unreadable = [], []
    for relative in relatives:
        try:
            lines = read_markdown(repo / relative).splitlines()
        except UnreadableFile as error:
            unreadable.append((relative, str(error)))
            continue
        copies.extend(copies_in_file(relative, lines, rules, sources))
    return sorted(copies, key=lambda copy: (copy.path, copy.line, copy.rule)), unreadable


def report(copies, unreadable, scanned):
    for copy in copies:
        print(copy.describe())
    for relative, reason in unreadable:
        print(f"{relative}: UNREADABLE ({reason}); not checked")
    print(f"{len(copies)} restated copies in {scanned} files scanned; {len(unreadable)} unreadable")


def main(argv=None):
    arguments = parse_arguments(sys.argv[1:] if argv is None else argv)
    repo = Path(arguments.repo).resolve()
    try:
        rules, default_paths, exclude = load_data(arguments.rules)
        relatives, unlisted = markdown_files(repo, arguments.paths or default_paths, exclude)
        copies, unreadable = scan(repo, rules, relatives)
    except ConfigError as error:
        print(f"rule_copies: {error}", file=sys.stderr)
        return EXIT_CONFIG
    unreadable += unlisted
    report(copies, unreadable, len(relatives))
    return EXIT_FOUND if copies or unreadable else EXIT_CLEAN


if __name__ == "__main__":
    sys.exit(main())
