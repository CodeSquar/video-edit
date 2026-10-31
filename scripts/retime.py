#!/usr/bin/env python3
"""Move a voiceover film's timing to new takes, without touching cues by hand.

  python retime.py [index.html] [--timings assets/voice/timings.json]

voice.py runs it on its own when index.html has a `const VO = {...};` line, so you rarely call it.

The film's script holds `const VO = {"s1": 0.2, "s2": 7.97, ...};` (each take's vo_start, printed by
voice.py) and every timeline position is written as `VO.s2 + 1.46` (word start inside the take).
Each take owns the stretch from its scene start to the next one. When the takes change, this script:
- rewrites the VO line from timings.json (so every `VO.x + …` cue follows its take);
- moves every `data-start` (sections, audio, any clip; not the root) by its stretch's shift;
- moves each `data-duration`'s end by the shift of the stretch the end falls in (an end on a cut
  follows that cut, so a scene whose take grew grows with it);
- root `data-duration` and anything that ran to the old end follow the last take.
Cues inside a take whose words changed still need their word offsets re-read from voice.py's table.
"""
import argparse, json, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
EPS = 0.05
VO_RE = re.compile(r"const VO = (\{[^}]*\});")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html", nargs="?", default="index.html")
    ap.add_argument("--timings", default="assets/voice/timings.json")
    a = ap.parse_args()
    src = open(a.html, encoding="utf-8").read()
    m = VO_RE.search(src)
    if not m:
        sys.exit(f"no `const VO = {{...}};` line in {a.html}: paste the one voice.py printed")
    old = json.loads(m.group(1))
    takes = json.load(open(a.timings, encoding="utf-8"))["takes"]
    new = {s: t["vo_start"] for s, t in takes.items()}
    lead = {s: round(t["vo_start"] - t["scene_start"], 3) for s, t in takes.items()}
    ids = [s for s in new if s in old]
    if not ids:
        sys.exit("VO line and timings.json share no take ids")
    # stretch of each take in the OLD film: [old scene start, next old scene start)
    bounds = [(old[s] - lead[s], s) for s in ids]
    shift = {s: round(new[s] - old[s], 3) for s in ids}

    def owner(t):
        """Take whose stretch holds t; a time within EPS of a take's cut belongs to the scene after it."""
        best = ids[0]
        for b, s in bounds:
            if t >= b - EPS:
                best = s
        return best

    root_m = re.search(r'data-composition-id="[^"]*"[^>]*?data-duration="([\d.]+)"', src) or \
        re.search(r'data-duration="([\d.]+)"[^>]*?data-composition-id=', src)
    old_total = float(root_m.group(1)) if root_m else None
    new_total = round(old_total + shift[ids[-1]], 2) if old_total else None
    moved = {"start": 0, "dur": 0}

    def fix_tag(tm):
        tag = tm.group(0)
        if "data-start=" not in tag and "data-duration=" not in tag:
            return tag
        if "data-composition-id=" in tag:  # root: only its length follows the last take
            if new_total is not None:
                tag = re.sub(r'data-duration="[\d.]+"', f'data-duration="{new_total:g}"', tag)
            return tag
        sm, dm = re.search(r'data-start="([\d.]+)"', tag), re.search(r'data-duration="([\d.]+)"', tag)
        if not sm:
            return tag
        st = float(sm.group(1))
        ns = round(st + shift[owner(st)], 2)
        if dm:
            end = st + float(dm.group(1))
            ran_to_end = old_total is not None and abs(end - old_total) < EPS
            ne = new_total if ran_to_end else end + shift[owner(end)]
            nd = round(max(0.05, ne - ns), 2)
            if abs(nd - float(dm.group(1))) > 0.001:
                tag = tag[:dm.start()] + f'data-duration="{nd:g}"' + tag[dm.end():]
                moved["dur"] += 1
            sm = re.search(r'data-start="([\d.]+)"', tag)
        if abs(ns - st) > 0.001:
            tag = tag[:sm.start()] + f'data-start="{ns:g}"' + tag[sm.end():]
            moved["start"] += 1
        return tag

    out = re.sub(r"<[a-zA-Z][^<>]*>", fix_tag, src)
    out = VO_RE.sub(lambda _: "const VO = " + json.dumps({s: new[s] for s in new}) + ";", out, count=1)
    open(a.html, "w", encoding="utf-8").write(out)
    shifts = " · ".join(f"{s} {shift[s]:+.2f}" for s in ids if abs(shift[s]) > 0.001) or "no shift"
    total = f"; root {old_total:g} → {new_total:g} s" if old_total is not None and new_total != old_total else ""
    print(f"retime: {shifts} | {moved['start']} starts, {moved['dur']} durations moved{total}")
    extra = [s for s in new if s not in old]
    if extra:
        print(f"retime: new takes {', '.join(extra)} have no scene yet: add them by hand")


if __name__ == "__main__":
    main()
