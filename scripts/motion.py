#!/usr/bin/env python3
"""Measure how a reference video moves, frame by frame, instead of guessing it from sparse frames.

  python motion.py ref.mp4 [--out DIR] [--only 3,7]

Every frame at native fps is diffed against the previous one on a small grid. That gives:
  - cuts, and the moments something moves (windows), with motion that runs all the time
    (footage, loops) ignored per area;
  - per window, each moving element: duration in frames/ms, onset offset (stagger), where the
    speed peaks, best-fitting GSAP ease, settle/overshoot, held frames (on twos);
  - per window, a strip: every native frame of the move, cropped to what moves, same scale,
    labelled (frame, time, pose), with a 25/50/75% guide grid, plus an onion skin of the outlines
    (cyan = first pose -> magenta = last) as the last cell.
Measured numbers are the curve; Read the strips to confirm them and to see what kind of move it is.
`--only` redraws just those windows. Writes DIR/motion.json and DIR/w-NN[-k].jpg (DIR default: next
to the video, `<name>-motion/`). Needs ffmpeg, numpy and pillow.
"""
import argparse, json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
LONG = 320       # analysis resolution (long side, px)
CELL = 8         # analysis grid cell (px at analysis resolution)
NOISE = 6        # per-pixel level change ignored (compression noise)
MAXSIDE = 1568   # strips are sized so nothing is downscaled again when Read
PER_IMG = 12     # frames per strip image
MAX_FR = 36      # frames drawn per window; longer windows are sampled evenly


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,r_frame_rate,avg_frame_rate:format=duration", "-of", "json", path],
                       capture_output=True, text=True, check=True)
    j = json.loads(r.stdout); s = j["streams"][0]
    num, den = (s.get("avg_frame_rate") or s["r_frame_rate"]).split("/")
    fps = float(num) / float(den) if float(den) else 30.0
    return s["width"], s["height"], fps, float(j["format"].get("duration", 0))


def frames(path, w, h, fmt="gray", select=None):
    vf = f"scale={w}:{h}:flags=area,format={fmt}"
    if select:
        vf = f"select='{select}'," + vf
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-vf", vf, "-vsync", "0", "-f", "rawvideo", "-"],
                         stdout=subprocess.PIPE)
    ch = 1 if fmt == "gray" else 3
    size = w * h * ch
    while True:
        b = p.stdout.read(size)
        if len(b) < size:
            break
        a = np.frombuffer(b, np.uint8)
        yield a.reshape(h, w) if ch == 1 else a.reshape(h, w, 3)
    p.wait()


# GSAP eases (power1 = quad ... power4 = quint)
def _in(name):
    k = {"power1": 2, "power2": 3, "power3": 4, "power4": 5}
    if name in k:
        return lambda t: t ** k[name]
    return {"sine": lambda t: 1 - np.cos(t * np.pi / 2),
            "expo": lambda t: np.where(t == 0, 0, 2 ** (10 * t - 10)),
            "circ": lambda t: 1 - np.sqrt(np.clip(1 - t * t, 0, 1))}[name]


def ease(name, t):
    if name == "none":
        return t
    base, kind = name.split(".")
    f = _in(base)
    if kind == "in":
        return f(t)
    if kind == "out":
        return 1 - f(1 - t)
    return np.where(t < 0.5, f(2 * t) / 2, 1 - f(2 - 2 * t) / 2)


EASES = ["none"] + [f"{b}.{k}" for b in ("sine", "power1", "power2", "power3", "power4", "expo", "circ")
                    for k in ("out", "in", "inOut")]


def fit(v):
    """v[k] = change between pose k and k+1 -> progress per pose -> ranked eases."""
    n = len(v)
    p = np.concatenate([[0], np.cumsum(v)]) / v.sum()
    t = np.arange(n + 1) / n
    res = sorted((float(np.sqrt(np.mean((ease(e, t) - p) ** 2))), e) for e in EASES)
    return res[:2], p


def spark(v):
    bars = "▁▂▃▄▅▆▇█"
    m = max(v.max(), 1e-9)
    return "".join(" " if x <= 0 else bars[min(7, int(x / m * 7.999))] for x in v)


def components(mask):
    """8-connected components of a small boolean grid (after a 1-cell dilation)."""
    d = mask.copy()
    d[1:] |= mask[:-1]; d[:-1] |= mask[1:]; d[:, 1:] |= mask[:, :-1]; d[:, :-1] |= mask[:, 1:]
    lab = np.zeros(mask.shape, int); n = 0
    for y, x in zip(*np.nonzero(d)):
        if lab[y, x]:
            continue
        n += 1; stack = [(y, x)]; lab[y, x] = n
        while stack:
            cy, cx = stack.pop()
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = cy + dy, cx + dx
                    if 0 <= yy < d.shape[0] and 0 <= xx < d.shape[1] and d[yy, xx] and not lab[yy, xx]:
                        lab[yy, xx] = n; stack.append((yy, xx))
    return [(lab == i) & mask for i in range(1, n + 1)]


def sharp(g):
    g = g.astype(np.float32)
    if min(g.shape) < 3:
        return 0.0
    lap = -4 * g[1:-1, 1:-1] + g[:-2, 1:-1] + g[2:, 1:-1] + g[1:-1, :-2] + g[1:-1, 2:]
    return float(lap.var())


def measure(v, first, fps, rel=0.05):
    """v[i] = change of one element between frame first+i-1 and first+i."""
    nz = np.nonzero(v >= rel * v.max())[0]
    vv = v[nz[0]:nz[-1] + 1]
    n = len(vv)
    held = int((vv == 0).sum())
    twos = n >= 6 and held >= 0.3 * n
    core = vv[vv > 0]
    pk = int(np.argmax(core))
    settle = False
    for k in range(pk + 1, len(core)):
        if core[k] < 0.25 * core[pk] and (core[k + 1:] > 0.15 * core[pk]).any():
            settle = True; break
    el = {"frames": [int(first + nz[0]), int(first + nz[-1])], "n": n, "ms": round(n / fps * 1000),
          "peak_at": round(float((vv * (np.arange(n) + 0.5)).sum() / vv.sum() / n), 2),
          "speed": spark(vv), "held_frames": held, "on_twos": bool(twos), "settle": settle}
    if n >= 4:
        (b1, b2), prog = fit(core if twos else vv)
        el["fit"] = [[b1[1], round(b1[0], 3)], [b2[1], round(b2[0], 3)]]
        el["progress"] = [round(float(x), 2) for x in prog]
    return el


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("--out"); ap.add_argument("--only")
    a = ap.parse_args()
    W, H, fps, dur = probe(a.video)
    out = a.out or os.path.splitext(a.video)[0] + "-motion"
    os.makedirs(out, exist_ok=True)
    sc = LONG / max(W, H)
    w = max(CELL, round(W * sc / CELL) * CELL); h = max(CELL, round(H * sc / CELL) * CELL)
    gy, gx = h // CELL, w // CELL
    sx, sy = W / w, H / h  # analysis px -> source px

    # pass 1: per-cell change energy for every native frame
    E, C, prev = [], [], None
    for f in frames(a.video, w, h):
        f = f.astype(np.int16)
        if prev is None:
            E.append(np.zeros((gy, gx), np.float32)); C.append(0.0)
        else:
            d = np.abs(f - prev); d[d < NOISE] = 0
            E.append(d.reshape(gy, CELL, gx, CELL).sum((1, 3)).astype(np.float32))
            C.append(float((d > 0).mean()))
        prev = f
    E = np.array(E); C = np.array(C); N = len(E)
    if N < 3:
        sys.exit("video too short")
    tot = E.sum((1, 2)) / (w * h)

    # cuts: a one-frame spike over a large area
    cuts = [i for i in range(1, N) if C[i] > 0.25 and tot[i] > 3 * max(tot[i - 1], tot[i + 1] if i + 1 < N else 0, 0.3)]
    E[cuts] = 0
    # per-cell threshold: ignore motion that runs all the time there (footage, loops)
    base = CELL * CELL * 2.0
    med = np.median(E, 0)
    thr = np.maximum(base, 3 * med)
    A = E > thr
    cont = float((med > base).mean())
    act = A.any((1, 2))

    # windows: runs of active frames, gaps <= 2 merged (held frames), split at cuts
    wins, i = [], 0
    cutset = set(cuts)
    while i < N:
        if not act[i]:
            i += 1; continue
        j = i
        while True:
            k = j + 1
            while k < N and not act[k] and k - j <= 2 and k not in cutset:
                k += 1
            if k < N and act[k] and k not in cutset and k - j <= 3:
                j = k
            else:
                break
        if j > i:  # at least 2 frames of change
            wins.append((i, j))
        i = j + 1

    only = {int(x) for x in a.only.split(",")} if a.only else None
    report = {"video": a.video, "size": [W, H], "fps": round(fps, 3), "frames": N, "duration": round(dur, 3),
              "cuts_s": [round(c / fps, 3) for c in cuts], "continuous_motion_area": round(cont, 3), "windows": []}

    for wi, (s0, e0) in enumerate(wins, 1):
        Em = np.where(A[s0:e0 + 1], E[s0:e0 + 1], 0)
        U = Em.sum(0) > 0
        comps = []
        for m in components(U):
            v = (Em * m).sum((1, 2))
            comps.append((v.sum(), m, v))
        comps.sort(key=lambda c: -c[0])
        comps = [c for c in comps if c[0] >= 0.05 * comps[0][0]][:6]
        els = []
        for _, m, v in comps:
            ys, xs = np.nonzero(m)
            box = [int(xs.min() * CELL * sx), int(ys.min() * CELL * sy),
                   int((xs.max() + 1) * CELL * sx), int((ys.max() + 1) * CELL * sy)]
            el = {"box": box, "area": round((box[2] - box[0]) * (box[3] - box[1]) / (W * H), 3), "_m": m}
            el.update(measure(v, s0, fps))
            els.append(el)
        els.sort(key=lambda el: (el["frames"][0], -el["area"]))
        t0 = min(el["frames"][0] for el in els)
        for k, el in enumerate(els):
            el["id"] = "ABCDEF"[k]; el["onset_f"] = el["frames"][0] - t0
        ux0 = min(el["box"][0] for el in els); uy0 = min(el["box"][1] for el in els)
        ux1 = max(el["box"][2] for el in els); uy1 = max(el["box"][3] for el in els)
        pad = int(0.04 * max(W, H))
        crop = [max(0, ux0 - pad), max(0, uy0 - pad), min(W, ux1 + pad), min(H, uy1 + pad)]
        report["windows"].append({"id": wi, "frames": [s0 - 1, e0], "s": [round((s0 - 1) / fps, 3), round(e0 / fps, 3)],
                                  "crop": crop, "elements": els, "strips": []})

    # pass 2: full-resolution frames of each window -> strips
    todo = [wd for wd in report["windows"] if only is None or wd["id"] in only]
    need = {}
    for wd in todo:
        a0, b0 = max(0, wd["frames"][0] - 1), min(N - 1, wd["frames"][1] + 1)
        idx = list(range(a0, b0 + 1))
        if len(idx) > MAX_FR:
            idx = sorted(set(np.linspace(a0, b0, MAX_FR).round().astype(int).tolist()))
        wd["_idx"] = idx
        for k in idx:
            need.setdefault(k, []).append(wd)
    got = {}
    if need:
        order = sorted(need)
        # ranges keep the select expression short
        rng, st = [], order[0]
        for p, q in zip(order, order[1:] + [None]):
            if q != p + 1:
                rng.append(f"between(n\\,{st}\\,{p})"); st = q
        for k, fr in zip(order, frames(a.video, W, H, "rgb24", "+".join(rng))):
            for wd in need[k]:
                x0, y0, x1, y1 = wd["crop"]
                got[(wd["id"], k)] = fr[y0:y1, x0:x1].copy()

    font = ImageFont.load_default(size=20)
    for wd in todo:
        idx = [k for k in wd.pop("_idx") if (wd["id"], k) in got]
        if not idx:
            continue
        crops = [got[(wd["id"], k)] for k in idx]
        x0, y0 = wd["crop"][:2]
        # full-resolution re-measure: the slow tail of a curve is lost at analysis size
        if len(idx) == idx[-1] - idx[0] + 1:
            g = [c.astype(np.float32).mean(2) for c in crops]
            yy = ((np.arange(crops[0].shape[0]) + y0) / sy // CELL).astype(int).clip(0, gy - 1)
            xx = ((np.arange(crops[0].shape[1]) + x0) / sx // CELL).astype(int).clip(0, gx - 1)
            for el in wd["elements"]:
                mk = el["_m"][np.ix_(yy, xx)]
                v = np.array([0.0] + [float(np.where(mk & (np.abs(b - a_) >= NOISE), np.abs(b - a_), 0).sum())
                                      for a_, b in zip(g, g[1:])])
                if v.max() > 0:
                    el.update(measure(v, idx[0], fps, 0.01))
        # onion skin: outlines of what differs from the first pose, cyan -> magenta
        base = crops[0].astype(np.int16)
        on = (crops[0] * 0.45).astype(np.uint8)
        for j, c in enumerate(crops[1:], 1):
            m = np.abs(c.astype(np.int16) - base).max(2) > 30
            edge = m & ~(np.roll(m, 1, 0) & np.roll(m, -1, 0) & np.roll(m, 1, 1) & np.roll(m, -1, 1))
            edge |= np.roll(edge, 1, 0) | np.roll(edge, 1, 1)
            t = j / max(1, len(crops) - 1)
            on[edge] = (int(255 * t), int(255 * (1 - t)), 255)
        cells = [(c, f"f{k} {k / fps:.3f}s p{k - wd['frames'][0]}") for c, k in zip(crops, idx)]
        chunks = [cells[i:i + PER_IMG] for i in range(0, len(cells), PER_IMG)]
        chunks[-1].append((on, "onion  cyan=first > magenta=last"))
        ch_, cw_ = crops[0].shape[:2]
        for ci, chunk in enumerate(chunks):
            n = len(chunk); best = None
            for cols in range(1, n + 1):
                rows = math.ceil(n / cols)
                s = min(MAXSIDE / (cols * cw_), (MAXSIDE - rows * 26) / (rows * ch_))
                if best is None or s > best[0]:
                    best = (s, cols, rows)
            s, cols, rows = best
            s = min(s, 1.0) if max(cw_, ch_) > 300 else s
            cw, chh = max(1, int(cw_ * s)), max(1, int(ch_ * s))
            img = Image.new("RGB", (cols * cw, rows * (chh + 26)), "white")
            d = ImageDraw.Draw(img)
            for j, (c, lab) in enumerate(chunk):
                x, y = (j % cols) * cw, (j // cols) * (chh + 26)
                img.paste(Image.fromarray(c).resize((cw, chh), Image.LANCZOS), (x, y))
                for fr in (0.25, 0.5, 0.75):
                    d.line((x + cw * fr, y, x + cw * fr, y + chh), fill=(0, 210, 0), width=1)
                    d.line((x, y + chh * fr, x + cw, y + chh * fr), fill=(0, 210, 0), width=1)
                d.rectangle((x, y, x + cw - 1, y + chh - 1), outline=(0, 0, 0))
                d.text((x + 4, y + chh + 2), lab, fill="black", font=font)
            p = os.path.join(out, f"w-{wd['id']:02d}" + (f"-{ci + 1}" if len(chunks) > 1 else "") + ".jpg")
            img.save(p, quality=92); wd["strips"].append(p)

    for wd in report["windows"]:
        t0 = min(el["frames"][0] for el in wd["elements"])
        for el in wd["elements"]:
            el.pop("_m", None); el["onset_f"] = el["frames"][0] - t0
    json.dump(report, open(os.path.join(out, "motion.json"), "w"), indent=1)

    # report
    print(f"{W}x{H} {fps:.3f} fps {N} frames {dur:.2f}s | cuts {len(cuts)}: "
          + " ".join(f"{c / fps:.2f}" for c in cuts))
    sh = np.diff([0] + cuts + [N]) / fps
    print(f"shots: mean {sh.mean():.2f}s range {sh.min():.2f}-{sh.max():.2f}s | moving {act.mean():.0%} of frames"
          + (f" | continuous motion ignored in {cont:.0%} of the frame (footage/loops)" if cont > 0.02 else ""))
    print("per element: frames s-e, n frames (ms), onset offset, peak_at (0.5 = symmetric, <0.4 decelerates,"
          " >0.6 accelerates), speed per frame, best eases (rmse), flags")
    for wd in report["windows"]:
        if only and wd["id"] not in only:
            continue
        print(f"#{wd['id']:02d} {wd['s'][0]:.3f}-{wd['s'][1]:.3f}s f{wd['frames'][0]}-{wd['frames'][1]}"
              f" crop {wd['crop']}" + (f"  {', '.join(wd['strips'])}" if wd["strips"] else ""))
        for el in wd["elements"]:
            fl = [x for x, on in (("ON TWOS", el["on_twos"]), ("settle/overshoot: fit ignores it, see strip (back.out/elastic.out?)", el["settle"])) if on]
            if el["area"] > 0.8:
                fl.append("full frame (camera/transition)")
            ft = " | ".join(f"{e} {r}" for e, r in el.get("fit", [])) or "too short for a curve"
            print(f"  {el['id']} f{el['frames'][0]}-{el['frames'][1]} {el['n']}f ({el['ms']}ms) +{el['onset_f']}f"
                  f" box {el['box']} peak_at {el['peak_at']} {el['speed']}  {ft}" + (f"  [{', '.join(fl)}]" if fl else ""))
    strips = [p for wd in report["windows"] for p in wd["strips"]]
    if strips:
        print(f"strips ({len(strips)}, Read them in one message): " + ", ".join(strips))
    print("json: " + os.path.join(out, "motion.json"))


if __name__ == "__main__":
    main()
