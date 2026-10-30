---
name: video-edit
description: Make, edit, animate or render a video as HTML compositions rendered frame by frame with the HyperFrames CLI (npx hyperframes), such as launch/promo films, explainers, data/chart pieces, vertical social clips, title cards, kinetic type, captions and cards over footage. Holds the render contract, the work loop (story → spec → build → check → review → render) and the motion/look taste that keeps the result from looking generated. Not for AI-generated footage.
---

# Video Edit

A video is HTML + CSS + one paused GSAP timeline per scene. The HyperFrames CLI seeks that timeline frame by frame and encodes it, so every render is identical. Run it as `npx hyperframes <cmd>` (Node 22+, FFmpeg; `npx hyperframes doctor` if Chrome is missing). Failures print a `Fix:` line. Don't read `--help` or `npx hyperframes docs` unless a command fails: the commands here are enough.

Defaults: 1920×1080, 30 fps. Build only what was asked: no voiceover, captions or new aspect ratio unless requested (images are the exception, see Project). A question or a loose idea gets an answer or a proposal, not an edit.

## Project

Everything lives under one `video/` folder at the repo root:

```
video/
  motion.md, design.md    shared style for every film
  refs/                   references, extracted frames, capture output
  films/<name>/           one HyperFrames project per film:
    index.html            root: declares variables, mounts one host per scene
    compositions/*.html   one scene each, everything inside <template>
    assets/               media, fonts (assets/fonts/*.woff2), root-relative paths
    SPEC.md               your brief
    renders/              every render output (mp4), never elsewhere
```

Preview and render use these same files: write in this format from the start, view with `npx hyperframes preview`. Never write your own player or a separate preview HTML.

New project: `HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes init video/films/<name>` (without it, init installs the full upstream skills), then delete the `CLAUDE.md` and `AGENTS.md` it writes: they send the agent to upstream skills, not this one. A website as the subject: `npx hyperframes capture <url> --json` (screenshots, copy, logos, `extracted/tokens.json`), output into `video/refs/`. Code shapes, attributes and lint fixes: `references/format.md`.

Images and b-roll: always use them without asking, unless the person or the project says otherwise. Source: a folder the person names; otherwise search with `ddgs` (`pip install ddgs`; `DDGS().images(query, max_results=10, size="Large")`; some downloads fail, keep the ones that land). Filter by the result data first (size, source), then look only at the ones you pick: no watermarks, edited variants or low resolution. Copy only the ones you use into `assets/img/`. How many, how long and how they enter is not fixed: infer it from the film's style and `video/motion.md` / `video/design.md`.

## Contract (`check` enforces most of it)

1. Timed elements: `class="clip"`, `id`, `data-start`, `data-duration` (seconds), visible over `[start, start+duration)` — land the end state *before* the end.
2. Video length = root `data-duration`. Overrun is cut; an early end holds the last frame.
3. One `gsap.timeline({ paused: true })` per composition, registered **last**: `window.__timelines["<composition-id>"] = tl`. Host id = scene root id = timeline key. Never `play()`, never nest a scene's timeline in the root's.
4. Deterministic: no `Date.now()`, unseeded `Math.random()` (use a seeded PRNG), fetches, timers, rAF, or `repeat: -1`. Everything visible is a function of timeline time.
5. Never tween `display`/`visibility`/`autoAlpha` on a `.clip` — animate a child. No CSS `transform` on something GSAP transforms; use `fromTo`, not `from`. Animate transforms, not `left/top/width/height`.
6. Never play/pause/seek media. `<video>` is `muted` or `data-has-audio="true"`; every `<audio>` has an `id`; no `crossorigin`.
7. Paint order is `z-index`, not `data-track-index`.
8. Grades/grain/blur on footage: `npx hyperframes media-treatment`, not CSS filters.
9. Copy, colours and swappable media are variables (`data-var-text`, `data-var-src`, `var(--id)`), so the video can be re-branded without code.
10. Content in the 90% action-safe box; text and captions in the 80% title-safe box.

## Work loop

1. **Existing project?** `npx hyperframes timeline --json` shows what plays when. Build on what is there.
2. **Story** (anything over ~15 s that tells something): write **three storylines** in words only — each a different world, device and form (`references/craft.md` §Story). Recommend one first. If the person is there, stop until they pick; if they said "no stops", build your pick.
3. **Spec** (new films over ~15 s; skip for edits and short pieces): write `SPEC.md` — every adjective turned into a number (template below). Build from it, check against it.
4. **Build**: write the whole first pass, then fix with `lint`/`check`. Don't plan every coordinate up front.
5. **Check**: `HYPERFRAMES_NO_UPDATE_CHECK=1 npx hyperframes check 2>/dev/null` (PowerShell: `2>$null`). Never `--json`; stderr is only progress lines. Non-zero exit = failed. Fix every error, weigh every warning (`line_unread`, `dead_stretch`, `text_below_floor`, `first_frame_empty`, `film_silent`).
6. **Look** (new films only; skip for small edits or if the person says no review): `npx hyperframes snapshot --review` (scene starts/mids, every cut ±0.2 s, phone width). For one move: `snapshot --range A,B --frames 8`, `--at t1,t2`, `keyframes --json --selector '#id'`. Read the PNGs — that is how you see the video. Then run the **Review** below.
7. **Preview**: `npx hyperframes preview --background`; give the URL and wait for approval, unless they asked for the file.
8. **Render**: `npx hyperframes render --quality delivery --output renders/<name>.mp4` (`draft` while iterating), always into the project's `renders/`. Confirm `ffprobe` duration = root `data-duration`; look at decoded frames. Sound: `npx hyperframes audio renders/<name>.mp4 --json` (you can measure it, not hear it — say so).

Timeline edits without hand-editing: `npx hyperframes timeline move|trim|split|set|duplicate|delete <#ref> … --plan --json`, then without `--plan`.

## SPEC.md

Adjectives are where the default look hides. Every one you turn into a number is a decision taken back.

```
GOAL:    what the viewer feels or does at the end, one sentence
OUTPUT:  W x H, fps
TIME:    seconds x fps = frames; BPM and frames-per-beat if music
LOOK:    ground (hex + texture %), ink, ONE accent and where it may appear;
         display face + weight + px + tracking; body face the same;
         the medium (paper+ink, photographs, product UI, glass, clay, 3D) with numbers;
         shadow offset/blur/opacity, grain %, vignette %
OBJECTS: each thing the viewer must recognise, with the material/details that make it read
MOTION:  eases by role (enter, move, exit, camera); springs as damping; durations in frames
SHOTS:   per shot: frame range, the ONE hero move, what is read (and for how long),
         the sound, how it hands off to the next shot
BANNED:  the defaults below + anything this film must not become
QA:      frames to check and what each must show
```

| Word | Becomes |
| --- | --- |
| premium | a material with numbers: satin paper 2% grain, product on a seamless sweep with 0.55 contact shadow |
| modern | a camera + type system: 30-frame push on one ease, display at 9% frame height, −2% tracking |
| clean | a grid + a ration: 12 cols, 96 px margins, accent on one word per shot |
| dynamic | cuts on the beat, layout change every bar, one hero move per shot |
| playful | springs at damping 0.45–0.6 on position/scale (never opacity/colour), 10–30% exaggeration |
| cinematic | 35 mm framing, key upper-left, rim from behind, 6% vignette |

**Look source, in order:** the project's `DESIGN.md`/`frame.md` (hex and fonts verbatim) → the real brand (`capture`) → a reference the person gave (take its grammar, not its content) → the subject's own world. A look holds when it is the rules of one **medium** (e.g. risograph: flat paper + fibre noise, ink A for all text, one fluorescent ink B, 3 px misregistration, halftone instead of gradients) — and motion comes from that medium too (printed, cut, pressed, refracted), not from fades.

## Taste: the rules that matter most

**Composition**
- The hero fills ≥40% of the frame's height or width. A small thing in an empty middle is never a shot — push in, crop, or give it a world.
- One hero move per shot. Secondary moves travel 50–70% as far and start 100–200 ms later; the rest holds still.
- Something new every 2–4 s. Readable text ≥28 px at 1080 (2.6% of the short side), held 0.5 s + 0.3 s per word; the last line ≥2 s. Too many words: cut words, never shrink type.
- Titles: ≤6 words a line, one line at a time, 4–9% of frame height, one accent word that carries meaning. A landed title is **dead still**.

**Motion**
- Ease by role: arrivals on a long tail (`expo.out`, `power4.out`); camera moves and colour floods both ways (`power2.inOut`); exits and zoom-throughs accelerate (`power3.in`). The same `power2.out` 0.5 s on everything is the "generated" look. Linear only for rotation/progress.
- Arrive slow, leave clean: exits 40–50% shorter than entrances, one motion, never slide-stop-leave. Fast moves 0.3–0.6 s with motion blur.
- Overlap: next element starts when the previous is 30–50% done. Stagger: letters 1 frame, words 60–120 ms, list items 40–80 ms.
- **Vector law at cuts:** the exit decides the entry — same axis, same direction (on Z: same sign of scale change), matched speed via mirrored eases (`power4.in` out → `power4.out` in), cut mid-motion on both sides. Pick one dominant direction for the film; spend other directions only with a visible cause.
- Every cut has a cause on screen: the clicked thing becomes the next shot. 3–5 transition kinds per film, ≤⅓ hard cuts between beats, worlds never crossfade. Catalog: `references/craft.md` §Transitions.
- Pause 0.3–0.75 s before the payoff; the payoff plays at normal speed.
- Pause the film at any second: something meaningful is mid-flight (a reveal landing, the camera travelling, the UI acting) — never idle wobble.

**Story** (any film that tells something)
- One thing to remember, one viewer doing one real task, one real piece of data travelling from hook to payoff.
- Frame 0 is the thumbnail: never black, never a logo alone. The first 2 s are the densest.
- Real UI and real numbers from the source, never a mockup or an invented stat; a missing screen is a labelled placeholder.
- The brand mark lands once, with weight, on a built end card — never docked in a corner.
- Copy bans: "Introducing" as the first line, "unlock", "seamless", "supercharge", "game-changer", "revolutionize", "effortless", unmeasured "in seconds".

**Sound:** a film over ~15 s gets a music bed and few, exact effects on visible actions (click on a real click, whoosh on a cut, pop on a landing, one riser into the payoff), each peaking one frame after its picture, rotated takes. Mix ≈ −14 to −16 LUFS, peaks ≤ −1 dBTP (`npx hyperframes normalize-audio`). No music source → deliver silent and say so.

## BANNED by default

Allowed only when the brand or the person's reference uses it, and only as they do:

- dark/navy void ground with small elements floating in the middle;
- glow, bloom, neon, lens flares, orbs, rings, decorative particles;
- purple/blue gradients, mesh gradients, glass cards;
- cream paper + serif display + italic accent word + "01 / 02" labels + mono caps labels + pill chips;
- everything centred; everything fading in at once; every element fading and sliding up;
- text that moves while read; titles drifting or scaling after they land; breathing/floating/pulsing loops on titles or UI; bounce on UI; click rings;
- corner labels, frame borders, corner brackets, HUD readouts as decoration;
- three cards in a row, KPI grids, a title over a dimmed screenshot, bullet slides, icons in circles;
- typing into a prompt box as the opener; the logo docked in a corner;
- Inter / Space Grotesk / Instrument Serif / Geist / JetBrains Mono as the *default* choice (fine when the brand uses them).

After each render, name every default it used anyway (listed or not), add it to `SPEC.md` BANNED (when there is one) and fix it. The list grows per film.

## Review (after `check` passes, before replying or rendering)

Be a harsh motion director, not a proud author.
1. Describe each beat frame in one sentence as a stranger would, naming every object. An object you'd have to explain is a P0.
2. Read the beat frames in order: does each cause the next? With the words covered, do the pictures still tell it? Compare each with its SHOT line.
3. Check: subject/ground separation, one focal point, crops and edge text, collisions at seams, reads shorter than their words, pops with no move, jumps at cuts, everything on one curve, the BANNED list, legibility at 360 px.
4. Notes as `t=4.2s · where · problem → exact change · what stays`. **P0** breaks the read/contract, **P1** weakens it, **P2** polish. Fix all P0, worthwhile P1 — text, then timing, then detail. Re-snapshot only what changed. Never score out of 10. Busy film: remove a third of the motion.
5. In your reply, a short delivery note: creative calls made, storylines not built, what was measured vs only looked at, the weakest shot, warnings kept on purpose. `REVIEW.md` only if asked.

## Read when needed

| Need | Read |
| --- | --- |
| Writing HTML: skeleton, attributes, variables, fonts, media, lint fixes, other runtimes (canvas/Three/Lottie) | `references/format.md` |
| Storylines, beats per film type, transitions catalog, captions, cards over footage, music timing, data/explainer/vertical/launch specifics | `references/craft.md` |
| Voiceover: script, generating takes (OpenRouter TTS), timing scenes to the voice | `references/voice-off.md` |
| `video/motion.md` (how the project's videos move) or `video/design.md` (how each frame looks) is missing, or the person asks to rewrite/change it. Otherwise just read the existing files and follow them | `references/video-motion.md` / `references/video-design.md` |
