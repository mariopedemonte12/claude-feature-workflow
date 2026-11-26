#!/usr/bin/env python3
import argparse
import bisect
import fnmatch
import json
import os
import re
import stat
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_RULES = Path(__file__).with_name("rule_copies.json")
EXIT_CLEAN, EXIT_FOUND, EXIT_CONFIG = 0, 1, 2
EXIT_CODES = (f"exit codes: {EXIT_CLEAN} no copy found and every file read; "
              f"{EXIT_FOUND} restated copies found or a file could not be read (both are listed); "
              f"{EXIT_CONFIG} configuration error in the rules file or a missing source section")
POINTER_WINDOW = 60
POINTER_MAX_LENGTH = 200
MARKUP = re.compile(r"[*`]|(?<!\w)_+|_+(?!\w)|</?(?:b|i|em|strong|code|u|s|mark)>", re.IGNORECASE)
BLOCKQUOTE = re.compile(r"^\s*(?:>\s?)+")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
TABLE_CELL = re.compile(r"\|")
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
    names: tuple
    pointer: re.Pattern | None


@dataclass(frozen=True)
class FlatText:
    text: str
    line_starts: tuple
    barriers: tuple

    def line_at(self, offset):
        return bisect.bisect_right(self.line_starts, offset)

    def region_around(self, start, end):
        before = bisect.bisect_right(self.barriers, start)
        after = bisect.bisect_left(self.barriers, end)
        low = self.barriers[before - 1] if before else 0
        high = self.barriers[after] if after < len(self.barriers) else len(self.text)
        return low, high


@dataclass(frozen=True)
class Copy:
    path: str
    line: int
    rule: str
    excerpt: str
    value: str | None
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
    parser = argparse.ArgumentParser(description="Report restated copies of workflow rules outside their single source",
                                     epilog=EXIT_CODES)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--rules", default=str(DEFAULT_RULES))
    parser.add_argument("paths", nargs="*", help="files or folders to scan, relative to --repo; default: the data file's scan.paths")
    return parser.parse_args(argv)


def string_list(value, what, allow_empty=True):
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ConfigError(f"{what} must be a list of strings, got {value!r}")
    if not value and not allow_empty:
        raise ConfigError(f"{what} must not be empty")
    return value


def compile_pattern(pattern, identifier):
    if not isinstance(pattern, str):
        raise ConfigError(f"rule {identifier}: a pattern must be a string, got {pattern!r}")
    try:
        return re.compile(pattern, re.IGNORECASE)
    except re.error as error:
        raise ConfigError(f"rule {identifier}: invalid fingerprint {pattern!r}: {error}") from error


def parse_rule(raw):
    try:
        identifier, source = raw["id"], raw["source"]
        patterns = string_list(raw["fingerprints"], f"rule {identifier}: fingerprints")
        names = string_list(raw.get("names", []), f"rule {identifier}: names")
        if not patterns and not names:
            raise ConfigError(f"rule {identifier}: fingerprints and names must not be empty together")
        pointer = compile_pattern(raw["pointer"], identifier) if "pointer" in raw else None
        rule = Rule(identifier, source["file"], source["section"],
                    tuple(compile_pattern(pattern, identifier) for pattern in patterns),
                    tuple(compile_pattern(pattern, identifier) for pattern in names), pointer)
    except (KeyError, TypeError) as error:
        raise ConfigError(f"malformed rule entry {raw!r}: missing {error}") from error
    if not all(isinstance(field, str) and field for field in (rule.identifier, rule.source_path, rule.source_section)):
        raise ConfigError(f"rule {identifier!r}: id, source.file and source.section must be non-empty strings")
    return rule


def parse_rules(entries):
    if not isinstance(entries, list) or not entries or not all(isinstance(entry, dict) for entry in entries):
        raise ConfigError(f"rules must be a non-empty list of objects, got {entries!r}")
    rules = [parse_rule(entry) for entry in entries]
    identifiers = [rule.identifier for rule in rules]
    duplicated = sorted({identifier for identifier in identifiers if identifiers.count(identifier) > 1})
    if duplicated:
        raise ConfigError(f"duplicated rule ids: {', '.join(duplicated)}")
    return rules


def load_data(path):
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        scan = raw.get("scan", {})
        paths = string_list(scan.get("paths", ["."]), "scan.paths")
        exclude = string_list(scan.get("exclude", []), "scan.exclude")
        return parse_rules(raw["rules"]), paths, exclude
    except (OSError, ValueError, KeyError, AttributeError) as error:
        raise ConfigError(f"cannot load rules from {path}: {error}") from error


def read_markdown(path):
    try:
        if not stat.S_ISREG(os.stat(path).st_mode):
            raise UnreadableFile("not a regular file")
        data = path.read_bytes()
    except OSError as error:
        raise UnreadableFile(error.strerror or str(error)) from error
    if b"\0" in data:
        raise UnreadableFile("binary content")
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise UnreadableFile(f"not UTF-8 ({error.reason} at byte {error.start})") from error


def markdown_lines(path):
    return read_markdown(path).replace("\r\n", "\n").replace("\r", "\n").split("\n")


def line_barriers(line, piece, offset):
    content = BLOCKQUOTE.sub("", line)
    if LIST_ITEM.match(content):
        yield offset
    elif not content.strip() or HEADING.match(content):
        yield from (offset, offset + len(piece))
    yield from (offset + cell.start() for cell in TABLE_CELL.finditer(piece))


def flatten(lines):
    pieces, line_starts, barriers, offset = [], [], [], 0
    for line in lines:
        piece = WHITESPACE.sub(" ", MARKUP.sub("", BLOCKQUOTE.sub("", line))).strip() + " "
        line_starts.append(offset)
        barriers.extend(line_barriers(line, piece, offset))
        pieces.append(piece)
        offset += len(piece)
    return FlatText("".join(pieces), tuple(line_starts), tuple(sorted(set(barriers))))


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


def non_overlapping(matches):
    covered_until = -1
    for match in sorted(matches, key=lambda match: (match.start(), -match.end())):
        if match.start() >= covered_until:
            covered_until = match.end()
            yield match


def fingerprint_matches(flat, rule):
    found = list(non_overlapping(match for fingerprint in rule.fingerprints for match in fingerprint.finditer(flat.text)))
    names = (match for name in rule.names for match in name.finditer(flat.text))
    names = [match for match in non_overlapping(names)
             if not any(match.start() < kept.end() and kept.start() < match.end() for kept in found)]
    yield from sorted(found + names, key=lambda match: match.start())


def source_values(repo, rule):
    try:
        lines = markdown_lines(repo / rule.source_path)
    except UnreadableFile as error:
        raise ConfigError(f"rule {rule.identifier}: source {rule.source_path} unreadable: {error}") from error
    span = section_span(lines, rule.source_section)
    if span is None:
        raise ConfigError(f"rule {rule.identifier}: section '{rule.source_section}' not found in {rule.source_path}")
    flat = flatten(lines[span[0] - 1:span[1]])
    values = {normalized_value(match) for match in fingerprint_matches(flat, rule)} - {None}
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
        elif target.exists() or target.is_symlink():
            found.add(target)
        else:
            unreadable.append((path, "not found"))
    relatives = sorted(relative_to_repo(file, repo) for file in found)
    return [relative for relative in relatives if not is_excluded(relative, exclude)], unreadable


def is_named_next_to_pointer(flat, rule, match):
    if rule.pointer is None or match.re not in rule.names:
        return False
    low, high = flat.region_around(match.start(), match.end())
    window_start, window_end = match.start() - POINTER_WINDOW, match.end() + POINTER_WINDOW
    search_start, search_end = max(low, window_start - POINTER_MAX_LENGTH), min(high, window_end + POINTER_MAX_LENGTH)
    return any(pointer.end() >= window_start and pointer.start() <= window_end
               for pointer in rule.pointer.finditer(flat.text, search_start, search_end))


def copies_in_file(relative, lines, rules, sources):
    flat = flatten(lines)
    for rule in rules:
        (start, end), values = sources[rule.identifier]
        own_source = relative == rule.source_path
        for match in fingerprint_matches(flat, rule):
            line = flat.line_at(match.start())
            if not (own_source and start <= line <= end) and not is_named_next_to_pointer(flat, rule, match):
                yield Copy(relative, line, rule.identifier, match.group(0).strip(), normalized_value(match), values)


def scan(repo, rules, relatives):
    sources = {rule.identifier: source_values(repo, rule) for rule in rules}
    copies, unreadable = [], []
    for relative in relatives:
        try:
            lines = markdown_lines(repo / relative)
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
