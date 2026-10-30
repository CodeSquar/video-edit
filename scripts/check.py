#!/usr/bin/env python3
"""`npx hyperframes check` with only what needs a decision.

  python check.py [film-dir]     (default: current folder)

Prints every error in full, each warning kind once with up to 3 places (+N more), and only a
count for infos and for warnings that one-file films raise on purpose. Exit code = check's.
"""
import collections, os, re, shutil, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
# Raised because every scene lives in one index.html, which is deliberate (SKILL.md: Build).
EXPECTED = {"nested_structure_needs_subcomposition", "composition_file_too_large", "timeline_track_too_dense"}
SHOW = 3

film = sys.argv[1] if len(sys.argv) > 1 else "."
npx = shutil.which("npx") or "npx"
r = subprocess.run([npx, "hyperframes", "check"], cwd=film, capture_output=True, text=True,
                   encoding="utf-8", errors="replace", env=dict(os.environ, HYPERFRAMES_NO_UPDATE_CHECK="1"))

blocks, section = [], ""
for line in r.stdout.splitlines():
    s = line.strip()
    if not s or s.startswith(("Report:", "Revision:", "◆")):
        continue
    if not line.startswith(" "):
        section = s
        continue
    m = re.match(r"(✗|⚠|ℹ)\s+(?:t=[\d.,\s]+s\s+)?([a-z_]+)[:\s]", s)
    if m:
        blocks.append({"sev": m.group(1), "code": m.group(2), "section": section, "lines": [s]})
    elif blocks and line.startswith("    "):
        blocks[-1]["lines"].append(s)
    elif re.match(r"\d+ error", s) or s.startswith("◇"):
        pass  # per-section summaries: replaced by the totals below

by = collections.OrderedDict()
for b in blocks:
    by.setdefault((b["sev"], b["code"]), []).append(b)

hidden, infos = collections.Counter(), collections.Counter()
for (sev, code), bs in by.items():
    if sev == "ℹ":
        infos[code] += len(bs)
        continue
    if sev == "⚠" and code in EXPECTED:
        hidden[code] += len(bs)
        continue
    shown = bs if sev == "✗" else bs[:SHOW]
    for b in shown:
        msg, rest = b["lines"][0], b["lines"][1:]
        print(f"[{b['section']}] {msg[:260]}")
        for x in rest:
            print("    " + x[:200])
    if len(bs) > len(shown):
        where = [b["lines"][1].split(" t=")[-1] if len(b["lines"]) > 1 else "?" for b in bs[len(shown):]]
        print(f"    +{len(bs) - len(shown)} more {code} (t={', '.join(w.rstrip('s') for w in where)[:160]}s)")

err = sum(len(v) for (s, _), v in by.items() if s == "✗")
warn = sum(len(v) for (s, c), v in by.items() if s == "⚠" and c not in EXPECTED)
print(f"\n{err} error(s), {warn} warning(s) to weigh"
      + (f"; hidden on purpose: {dict(hidden)}" if hidden else "")
      + (f"; infos: {dict(infos)}" if infos else ""))
print("FAILED" if r.returncode else "passed")
if r.returncode and not blocks:
    print((r.stdout + r.stderr)[-1500:])  # a crash, not findings: show the raw tail
sys.exit(r.returncode)
