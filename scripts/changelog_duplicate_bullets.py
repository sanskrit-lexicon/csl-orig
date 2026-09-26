"""Fail when the same changelog entry appears in more than one place.

A changelog entry describes one change, so its bullet belongs to exactly one
`## [x.y.z]` section. Nothing verified that, and it stopped being true twice in
Systema-Sanscriticum alone:

  * `a85acd81` (PR #684) inserted one bullet **52 times** in a single commit --
    once per `### Added` heading in the file, because the edit was anchored on a
    heading that repeats once per release. Repaired by PR #827.
  * `27ad957a` (PR #506) wrote the same bullet into two sections at once; it sat
    unnoticed for three weeks until this check was switched on.

Both were invisible to review: the duplicate lines are byte-identical to a
legitimate one, so no single section reads as wrong, and only a diff of the
*repair* makes them visible.

  python scripts/changelog_duplicate_bullets.py           # check (exit 1 if dupes)
  python scripts/changelog_duplicate_bullets.py --json    # machine-readable

THE UNIT OF COMPARISON IS THE ENTRY, NOT THE BULLET LINE

An entry is a top-level bullet plus its indented continuation, and the whole
block is the key. Comparing first lines alone is wrong here: several repos open
an entry with a header naming the file touched --
`- **[`build_klammerdiagramm.py`](url)** --` -- and put the substance below, so
the same script changed across five releases yields five identical first lines
and five different entries. Measured 29-07-2026, first-line comparison called
every claude-config finding (4) and the VisualDCS one (1) a duplicate; all five
were false. It costs nothing on the real cases: the Systema fan-out and the H881
duplicate were single-line entries, still caught.

WHAT IS **NOT** A DUPLICATE (measured across 79 repos, not guessed)

Running an early version org-wide flagged 13 repos, and most were false
positives. Three shapes legitimately repeat and are excluded:

  1. Placeholder bullets -- `- None`, `- (none in this release)`, `- n/a`.
     Repos that stamp one into every empty subsection carry several per release
     by design (csl-devanagari, prefaces_ieg).
  2. Nested-list labels -- a bullet whose next non-blank line is an indented
     *bullet* is a heading for a sub-list, not an entry; its text repeats across
     entries by design (RussianRamayana's `- **Созданы JSON-данные**:`).
     "Indented" alone is NOT the test: this org's changelogs routinely wrap one
     entry's prose across indented continuation lines, and the looser rule
     silenced two repos that really were duplicating entries.
  3. Anything listed in an optional `.changelog-dupe-allow` file at the repo
     root (one substring per line, `#` comments ignored) -- for genuinely
     repeating lines such as a per-release verification line stating the same
     test count in consecutive patch releases (ORS-FAQ).

There is deliberately no `--fix`. Which copy survives is decided by tag
ancestry, not position: `git log -S"<text>" -- <changelog>` finds the commit
that introduced the bullet, and `git tag --contains <sha> --sort=creatordate`
names the release that shipped it. A script that guessed would quietly delete
the real entry and keep the stray, so the report prints that recipe instead.

Scope: top-level bullets (`- ` at column 0) inside `##` sections. Indented
continuation lines are part of their parent entry.
"""

import json
import os
import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

SECTION_RE = re.compile(r'^## ')
BULLET_RE = re.compile(r'^- \S')
NESTED_BULLET_RE = re.compile(r'^[ \t]+[-*+] \S')
ALLOW_FILE = '.changelog-dupe-allow'

CHANGELOG_NAMES = ('CHANGELOG.md', 'changelog.md', 'Changelog.md')

# A bullet whose text reduces to one of these is a "nothing here" placeholder.
PLACEHOLDERS = {
    '', 'none', 'nothing', 'nothing yet', 'n/a', 'na', 'tbd', '-', '--', '—',
    'no changes', 'nothing in this release', 'none in this release',
    'nothing to report', 'initial release',
}


def _normalise(bullet):
    """Reduce a bullet to comparable prose: strip markup, punctuation, case."""
    t = bullet[2:]                                  # drop the leading "- "
    t = re.sub(r'[`*_]', '', t)                     # code/bold/italic marks
    t = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', t)  # links -> their text
    t = t.strip().strip('.:;').strip()
    t = re.sub(r'^\((.*)\)$', r'\1', t).strip()     # "(none in this release)"
    return t.lower()


def load_allowlist(repo_root):
    path = os.path.join(repo_root, ALLOW_FILE)
    if not os.path.isfile(path):
        return []
    out = []
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith('#'):
                out.append(line)
    return out


def find_duplicates(text, allowlist=()):
    """-> ([(bullet, [(section, lineno), ...]), ...], skipped_counter)

    A bullet counts only if it is a real entry: not a placeholder, not the label
    of a nested list, not allow-listed.
    """
    lines = text.split('\n')
    section = None
    seen = defaultdict(list)
    skipped = defaultdict(int)

    for i, line in enumerate(lines):
        if SECTION_RE.match(line):
            section = line.strip()
            continue
        if not (section and BULLET_RE.match(line)):
            continue

        norm = _normalise(line)
        if norm in PLACEHOLDERS:
            skipped['placeholder'] += 1
            continue

        # Label of a nested list: the next non-blank line is an indented
        # *bullet*. It must NOT be enough for that line to merely be indented --
        # this org's changelogs routinely wrap one entry's prose across indented
        # continuation lines, and treating those as labels silenced two repos
        # that really were duplicating entries (claude-config 4 -> 0,
        # VisualDCS 1 -> 0). Sub-list vs. wrapped prose is the discriminator.
        nxt = next((lines[j] for j in range(i + 1, len(lines)) if lines[j].strip()), '')
        if nxt[:1] in (' ', '\t') and NESTED_BULLET_RE.match(nxt):
            skipped['nested-label'] += 1
            continue

        if any(a in line for a in allowlist):
            skipped['allowlisted'] += 1
            continue

        # Key on the WHOLE ENTRY -- the bullet line plus its indented
        # continuation -- not on the bullet line alone. Several repos here open
        # an entry with a header naming the file touched
        # (`- **[`build_klammerdiagramm.py`](url)** —`) and put the substance in
        # the lines below, so the same script changed in five releases yields
        # five identical FIRST LINES and five different entries. Comparing
        # first lines called all of those duplicates: measured 29-07-2026, that
        # was every finding in claude-config (4) and VisualDCS (1) -- false, all
        # of them. The unit that must be unique is the entry, so that is the key.
        entry = [line.rstrip()]
        for j in range(i + 1, len(lines)):
            nxt_line = lines[j]
            if not nxt_line.strip() or nxt_line.startswith('- ') or nxt_line.startswith('#'):
                break
            entry.append(nxt_line.rstrip())
        seen['\n'.join(entry)].append((section, i + 1))

    dupes = sorted(((b, h) for b, h in seen.items() if len(h) > 1),
                   key=lambda item: -len(item[1]))
    return dupes, dict(skipped)


def main():
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = next((os.path.join(repo, n) for n in CHANGELOG_NAMES
                 if os.path.isfile(os.path.join(repo, n))), None)
    if path is None:
        print('no changelog found in {0} — nothing to check'.format(repo))
        return 0

    as_json = '--json' in sys.argv
    with open(path, encoding='utf-8') as fh:
        text = fh.read()

    allowlist = load_allowlist(repo)
    dupes, skipped = find_duplicates(text, allowlist)
    name = os.path.basename(path)

    if as_json:
        print(json.dumps(
            {'file': name, 'skipped': skipped,
             'duplicates': [{'entry': b, 'bullet': b.split('\n')[0], 'count': len(h),
                             'sections': sorted(set(s for s, _ in h)),
                             'lines': [n for _, n in h]}
                            for b, h in dupes]},
            ensure_ascii=False, indent=2))
        return 1 if dupes else 0

    note = ''
    if skipped:
        note = '  (not compared: {0})'.format(
            ', '.join('{1} {0}'.format(k, v) for k, v in sorted(skipped.items())))

    if not dupes:
        print('{0}: no duplicated entries{1}'.format(name, note))
        return 0

    print('{0}: {1} entr(y/ies) duplicated, {2} copies total{3}\n'.format(
        name, len(dupes), sum(len(h) for _, h in dupes), note))
    for entry, hits in dupes:
        sections = sorted(set(s for s, _ in hits))
        head = entry.split('\n')[0]
        extra = entry.count('\n')
        print('{0}x across {1} section(s):'.format(len(hits), len(sections)))
        print('  {0}{1}'.format(head[:120], '…' if len(head) > 120 else ''))
        if extra:
            print('  (+{0} continuation line(s), identical in every copy)'.format(extra))
        for section, lineno in hits:
            print('    line {0:<6} {1}'.format(lineno, section))
        print()

    print('Each entry belongs to exactly ONE section. To find which, take the')
    print('commit that introduced it and the earliest tag containing it:')
    print('  git log -S"<distinctive words>" --oneline -- {0}'.format(name))
    print('  git tag --contains <sha> --sort=creatordate | head -1')
    print('Keep the copy in that version\'s section; delete the others.')
    print('If a line legitimately repeats, add a substring of it to {0}.'.format(ALLOW_FILE))
    return 1


if __name__ == '__main__':
    sys.exit(main())
