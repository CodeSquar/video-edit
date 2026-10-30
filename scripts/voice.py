#!/usr/bin/env python3
"""Voiceover in one call: generate every take, clean it, time it.

  python voice.py LINES_FILE [--out assets/voice] [--instructions "..."] [--voice Kore]
                  [--model google/gemini-3.8-flash-lite-tts] [--tempo auto|1|1.1…]
                  [--air 0.6] [--lead 0.2] [--only s3,s5] [--force]

LINES_FILE: one take per line, `<scene-id> | <spoken text>` (blank lines and # comments skipped).
Run from the film folder. Needs $OPENROUTER_API_KEY, ffmpeg, npx hyperframes.

Steps: all takes requested in parallel (pcm 24 kHz -> wav) -> edge silence trimmed ->
one tempo for the whole film (auto: speeds up a slow read toward 2.4 words/s, max 1.2x) ->
one transcription pass over all takes joined -> assets/voice/timings.json + a table:
take length, words/s, word starts, and a suggested scene start/duration.
Existing wavs are reused unless --force or listed in --only (re-generate just those).
A new --tempo re-times the existing wavs too (by the step from the stored tempo), nothing re-requested.
"""
import argparse, concurrent.futures as cf, json, os, shutil, subprocess, sys, tempfile, time, wave

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
URL = "https://openrouter.ai/api/v1/audio/speech"
GAP = 1.5  # seconds of silence between takes in the joined transcription file


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)


def dur(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def tts(text, args, pcm):
    """curl, not urllib: Python's certificate store on some machines rejects valid hosts."""
    body = pcm + ".json"
    with open(body, "w", encoding="utf-8") as f:
        json.dump({"model": args.model, "voice": args.voice, "response_format": "pcm",
                   "input": text, "instructions": args.instructions}, f, ensure_ascii=False)
    hdr = pcm + ".hdr"  # the key goes through a file so it never shows in a process list
    with open(hdr, "w") as f:
        f.write("Authorization: Bearer " + os.environ["OPENROUTER_API_KEY"] + "\nContent-Type: application/json\n")
    last = ""
    try:
        for attempt in range(4):
            r = run(["curl", "-sS", "-m", "120", "-o", pcm, "-w", "%{http_code}", "-H", "@" + hdr,
                     "--data-binary", "@" + body, URL])
            code, head = r.stdout.strip(), open(pcm, "rb").read(300) if os.path.exists(pcm) else b""
            if code == "200" and head[:1] != b"{":
                return
            last = f"HTTP {code} {r.stderr.strip()} {head.decode('utf-8', 'replace')}"
            if code == "402" and b"in-flight" in head:
                # OpenRouter holds credit for every request in flight; it frees as the other takes land
                time.sleep(3 * (attempt + 1))
            elif attempt:  # one retry for a network hiccup
                break
        raise RuntimeError(last)
    finally:
        for p in (body, hdr):
            if os.path.exists(p):
                os.remove(p)


def make_take(sid, text, out, args):
    pcm, wav = os.path.join(out, sid + ".pcm"), os.path.join(out, sid + ".wav")
    try:
        tts(text, args, pcm)
    except Exception:
        if os.path.exists(pcm):
            os.remove(pcm)
        raise
    trim = "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"
    r = run(["ffmpeg", "-loglevel", "error", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", pcm, "-af", trim, wav])
    os.remove(pcm)
    if r.returncode:
        raise RuntimeError(r.stderr[-300:])


def transcribe(ids, out):
    """One parakeet pass over every take joined with GAP s of silence, split back per take."""
    tmp = tempfile.mkdtemp()
    joined = os.path.join(tmp, "all.wav")
    cmd, offsets, t = ["ffmpeg", "-loglevel", "error", "-y"], {}, 0.0
    for sid in ids:
        p = os.path.join(out, sid + ".wav")
        cmd += ["-i", p, "-f", "lavfi", "-t", str(GAP), "-i", "anullsrc=r=24000:cl=mono"]
        offsets[sid] = (t, t + dur(p))
        t += dur(p) + GAP
    cmd += ["-filter_complex", f"concat=n={2 * len(ids)}:v=0:a=1", "-ar", "24000", "-ac", "1", joined]
    r = run(cmd)
    if r.returncode:
        raise RuntimeError(r.stderr[-300:])
    npx = shutil.which("npx") or "npx"
    env = dict(os.environ, HYPERFRAMES_NO_UPDATE_CHECK="1")
    r = run([npx, "hyperframes", "transcribe", joined, "--json"], env=env, cwd=tmp)
    words = []
    for line in (r.stderr + "\n" + r.stdout).splitlines():  # the "words" event is on stderr
        if '"type":"words"' in line:
            words = json.loads(line)["words"]
    shutil.rmtree(tmp, ignore_errors=True)
    per = {sid: [] for sid in ids}
    for w in words:
        for sid, (a, b) in offsets.items():
            if a - GAP / 2 <= w["start"] < b + GAP / 2:  # the first word is often stamped early
                per[sid].append({"text": w["text"], "start": round(max(0, w["start"] - a), 2),
                                 "end": round(min(b, w["end"]) - a, 2)})
                break
    return per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lines")
    ap.add_argument("--out", default="assets/voice")
    ap.add_argument("--voice", default="Kore")
    ap.add_argument("--model", default="google/gemini-3.8-flash-lite-tts")
    ap.add_argument("--instructions", default="Warm, clear, unhurried. Short pause between phrases.")
    ap.add_argument("--tempo", default="auto")
    ap.add_argument("--air", type=float, default=0.6, help="silence after each take inside its scene")
    ap.add_argument("--lead", type=float, default=0.2, help="voice starts this long after its scene")
    ap.add_argument("--only", default="", help="comma list of ids to (re)generate")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    lines = []
    for raw in open(args.lines, encoding="utf-8"):
        raw = raw.strip()
        if raw and not raw.startswith("#"):
            sid, text = (p.strip() for p in raw.split("|", 1))
            lines.append((sid, text))
    os.makedirs(args.out, exist_ok=True)
    only = set(filter(None, args.only.split(",")))
    todo = [(s, t) for s, t in lines
            if args.force or s in only or not os.path.exists(os.path.join(args.out, s + ".wav"))]
    if todo:
        if not os.environ.get("OPENROUTER_API_KEY"):
            sys.exit("OPENROUTER_API_KEY is not set: ask the person to set it (never read it from a file).")
        with cf.ThreadPoolExecutor(8) as ex:
            futs = {ex.submit(make_take, s, t, args.out, args): s for s, t in todo}
            for f in cf.as_completed(futs):
                if f.exception():
                    sys.exit(f"take {futs[f]} failed: {f.exception()}")

    ids = [s for s, _ in lines]
    nwords = {s: len(t.split()) for s, t in lines}
    total_w, total_d = sum(nwords.values()), sum(dur(os.path.join(args.out, s + ".wav")) for s in ids)
    tpath = os.path.join(args.out, "timings.json")
    prev = json.load(open(tpath, encoding="utf-8")).get("tempo") if os.path.exists(tpath) else None
    if args.tempo != "auto":
        tempo = float(args.tempo)
    elif prev and not args.force:
        tempo = prev  # re-generated takes match the ones already sped up
    else:
        wps = total_w / total_d
        tempo = round(min(1.2, 2.4 / wps), 2) if wps < 2.2 else 1.0
    film_tempo = tempo
    new = {s for s, _ in todo}
    for s in ids:  # new takes are raw; existing ones are already at the stored tempo
        step = tempo if s in new else tempo / (prev or 1.0)
        if abs(step - 1) > 0.005:
            p = os.path.join(args.out, s + ".wav")
            run(["ffmpeg", "-loglevel", "error", "-y", "-i", p, "-af", f"atempo={step:.4f}", p + ".t.wav"])
            os.replace(p + ".t.wav", p)

    words = transcribe(ids, args.out)
    timings, t = {}, 0.0
    print(f"tempo {film_tempo}x ({len(todo)} new take(s)); start = scene start, vo = voice data-start\n")
    for s in ids:
        d = round(dur(os.path.join(args.out, s + ".wav")), 2)
        scene = round(args.lead + d + args.air, 2)
        digits = any(c.isdigit() for w in words[s] for c in w["text"])  # "1994" for five spoken words
        flag = "  <- word count off: wrong read? spell it out and --only " + s \
            if words[s] and not digits and abs(len(words[s]) - nwords[s]) > max(2, 0.25 * nwords[s]) else ""
        timings[s] = {"file": f"{args.out}/{s}.wav", "duration": d, "words": words[s],
                      "scene_start": round(t, 2), "scene_duration": scene, "vo_start": round(t + args.lead, 2)}
        print(f"{s:5} take {d:5.2f}s {nwords[s] / d:4.1f} w/s | start {t:6.2f} dur {scene:5.2f} vo {t + args.lead:6.2f}{flag}")
        print("      " + " ".join(f"{w['text']}@{w['start']:.2f}" for w in words[s]))
        t += scene
    print(f"\ntotal {t:.2f}s (root data-duration if scenes run back to back)")
    with open(tpath, "w", encoding="utf-8") as f:
        json.dump({"tempo": film_tempo, "takes": timings}, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
