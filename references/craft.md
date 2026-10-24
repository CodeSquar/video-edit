# Craft

Measured defaults. A reference the person gave, or a beat that breaks a rule on purpose, wins.

## Story

Skip for edits, captions/overlays on footage, and single-idea pieces (one kinetic line, a map move). With a given script, storyboard or reference film, follow theirs.

**The one thing:** what it is in one line ("You can now …" / the one idea / what changed and why) · what the viewer remembers, in their words · one viewer doing one real task, from need to result, with one real piece of data (a query, file, number) travelling through it. Every claim traces to the source; never derive claims it didn't make ("40 min → 2 min" is not "20× faster"); illustrative numbers are marked.

**Three storylines:** sketch 5+ one-liners pairing a device with a form, keep the three that differ most, one of them bold. Each gives: name · device + form · two sentences of what's seen and felt · the first 2 s exactly · beats in one line · look in one line · sound in one line. Present them in your reply as one question with options; `STORYLINES.md` only if asked. Pick for the story a stranger would follow, not the most striking frame.

| Device | Seen |
| --- | --- |
| A moment in someone's day | a person, a time stamp, the message that creates the need |
| A character does the work | a mascot or cursor carries, drags, reacts; every cut has a cause |
| Feature as the hook | the feature happening to a recognisable image in the first 0.5 s |
| Result first | the output plays, camera pulls back to where it came from |
| One object across apps | the thing being made travels into the product, which keeps working on it |
| Before and after | the old way as a scene, then the new way (new side calm, old side churns) |
| Type carries the argument | giant kinetic type and colour fields cutting on the beat |
| A number lands | one real number earned by a scene, then made physical |
| The object is the explanation | a machine/model whose working is the idea; the camera tours it |

| Form | Seen |
| --- | --- |
| One continuous take | never cuts; pushes and travels from world to world |
| Object-to-object chain | each shot ends on the thing that opens the next |
| Endless zoom | dive into a detail that is the next world |
| Flight through one world | a 3D set, map or desk; each idea a stop on the route |
| Cut on the beat | hard cuts, type and colour changing every half beat |
| Match cuts | one shape holds while everything around it changes |
| Split screen to one | several panes collapse into the one that matters |
| One frame that rebuilds | a single composition keeps rearranging itself |

**Beats** (launch ~35 s; scale it): Hook ~8% (the need, or the feature already working) → Tension ~12% (the old way failing on screen) → Reveal ~8% (product named, 20–30% in) → Proof ~40% (the real task as 3–6 verbs: paste, pick, watch it build, ship) → Payoff ~20% (the biggest moment, once, 60–80% in) → Claim ~8% (one line) → End card ~8% (mark carried in, name + CTA hold 2–3 s). In each verb beat keep only what the cursor touches and what proves the line.

**Worlds:** several worlds with their own ground, light and scale — never one dark canvas with small UI floating. Enter each through an object on screen. Keep one home stage, one carrier the eye follows, palette and type constant.

**Copy:** read the lines alone — a stranger gets it; watch the pictures alone — same story. No voiceover unless asked; then the screen never repeats the spoken sentence verbatim.

## Motion details

- Motion blur on fast moves: 6–12 px on text-sized elements, 15–20 px full-frame, along the move's axis, peaking at its fastest frame.
- Springs by damping ratio: 1.0 no bounce, 0.7–0.85 premium, 0.4–0.6 playful, <0.3 cartoon. Position/scale may bounce; opacity/colour never. Nearest built-ins: `back.out(1.4–1.7)`, `elastic.out(1, 0.5)`.
- Title entrances — vary them within a film:
  - per word: `blur(6px)→0`, opacity 0→1 in 0.13 s, 0.067 s apart, no translate;
  - per word light grey → ink, 0.07–0.1 s apart;
  - whole line blurring in 8 px → 0 in 0.13–0.2 s;
  - per letter for a name, 0.1 s apart, opacity 0.3→1 + slight blur;
  - behind the subject (between the plate and a matte of the person);
  - one word rolling through options like a slot machine, ~0.1 s a roll.
- Exit lines with a blur-out + fade of 0.13–0.25 s, word by word, or with the scene's move.
- Rhythm: montages cut every 0.13–0.8 s; a demo holds one framing 7–10 s while the UI acts; shots average 1.8–3 s with motion inside.
- Cuts land on the fastest frame of a move. A click into a new screen is a match cut on the click's rebound; the new screen arrives slightly large and settles.
- Causal chains: click → squash → release → flight → impact → recoil → reveal. The effect starts on the causing frame, not "shortly after". Big things rebound slower than small ones.
- Sustained motion that works: the product UI acting, footage playing, a character acting, staged reveals on narration beats, a mapped camera path, a slow background orbit (3–5°/s).

| Feedback | Change |
| --- | --- |
| "too fast" | slow every zoom and pan to 0.7×, nothing else |
| "speed it up" | speed content and shorten the beat equally; later beats move up |
| "the titles move" | land them, then dead still until they leave |
| "feels like slides" | enter the next scene through an object on screen; cut a move mid-flight |

## Transitions

| Transition | Build |
| --- | --- |
| Zoom through a button | camera tracks to it with blur (0.6 s), then it scales ~8% → ~250% of frame in 0.35 s, strong ease-in; its fill becomes the next frame |
| Object becomes the world | a card grows past the frame in 0.65 s ease-in-out, radius shrinking; surroundings blur ~15 px and fade in 0.3 s; new content fades in while it grows |
| Morph | one container widens into the next (~110 → ~880 px in 0.2 s `power3.out`) with horizontal blur 12 → 0 |
| Carry across | the result shrinks 1 → 0.6, blur peaking 6 px mid-move, lands inside the next app as it builds around it |
| Colour flood | hero stays, ground changes colour in ~0.4 s `power2.inOut` |
| Whip | 0.13–0.3 s directional smear; arrival lands blurred, sharpens in ~0.13 s |
| Iris from the click | `clip-path: circle()` opens from the click point in 0.15 s |
| Dip cut | outgoing darkens ~40% for 3 frames, then hard cut |
| Blur swap on one stage | out: opacity → 0 + ~8 px blur in 0.13–0.2 s; in: blur → 0 in 0.13 s; ground never cuts |

Z rule: growing = push forward, shrinking = pull back. A shrinking exit answered by a grow-from-small entry is a mirrored vector — the most common seam error. Never ping-pong directions on consecutive seams.

## Film types

- **Launch/promo (20–45 s):** real UI, never a mockup — the person's recordings/screenshots, Figma frames, `capture`. Rebuild only the piece the beat uses at 1.6–2× real size (text ≥26 px after any push); never a small window in an empty canvas, never product UI tilted in 3D. Camera cycles window → pane → punch-in on one control (0.4–0.6 s moves, then hold while the UI acts). Containers morph instead of cutting. Cursor 4–7% of frame, enters from off-screen, its click causes the next thing on the same frame. End card: mark lands in the last 5–10%, lockup 15–30% of width, performed (clicked, carried, wiped) not faded; CTA holds 1.5–3 s.
- **Explainer (30–90 s):** start where the viewer is (a person, a situation, a question); the device enters as the answer; return to the person at the end. One diagram that grows a part per beat, each part appearing when named; continuous morphs over cuts; one worked example. Labels sit on the part, no legends. End on the idea in one line.
- **Data:** one number at a time, the biggest thing on screen, `font-variant-numeric: tabular-nums`, count-up 1.2–1.6 s then hold, source line on screen. Charts build in reading order: axis → reference line → data drawing in → one annotation on the point that matters. Highlight one series, grey the rest. Tells: KPI grids, dashboards, pies, everything counting at once.
- **Vertical 9:16 (1080×1920):** recompose, don't squeeze. Nothing in the top 168 px; words and product in 168–1330 px; below 1330 only texture; nothing under the right action rail. Frame 0 = hook (face, result, or bold line). Type ×1.35, ≤5 English words per claim line. Shots 1–2 s, new beat every 2–4 s, captions for muted viewing.
- **Music:** song sections are chapters (`npx hyperframes audio <track> --only sections,onsets,moments --json`). Slower shots in verses, one picture per strong beat in the chorus, held image on a breakdown. Each lyric line gets a picture of what it means (1.4–4 s). Tells: one treatment >6 s, a waveform as the main picture, cutting on every beat.
- **Kinetic type:** 3–7 words per scene. Highlighter across lines: tween a custom property on a `background-size` band with `box-decoration-break: clone`.

## Music and timing

- `npx hyperframes beats <track>`: frames per beat = fps × 60 / BPM. Compute each beat from its index and round — never add a rounded beat repeatedly (drifts). Trust beats only where `bpmConfidence` is high; on calm music cut on phrase/energy changes.
- A move that must land on a hit starts 40–190 ms early; reactions start 0–45 ms after. The hit itself is a 0 ms `tl.set` — easing a hit kills it.
- Enter the track at its strongest bar, not a quiet intro; end on a bar line with a short fade under the end card. Library loops (15–30 s): 0.4 s fade-in, 1.5 s fade-out.
- Narrated: the voice is the clock. TTS ≈ 2.2 words/s; ≤ ~19 words (9 s) per scene. Reveal each piece when the voice names it, across the back half of the scene. Trim the script, never stretch the motion. Music under voice ≈ 0.14 volume.
- Effects 3–6 dB over the bed; a bed with energy under 150 Hz vanishes on phone speakers.

## Captions

- Words: `npx hyperframes transcribe <file> --model small.en --json` (English) or `--model small --language <code>` (default model *translates* to English). Read the transcript: drop words inside a final silence (whisper invents "Thank you."), drop `♪`/`�` tokens; >20% garbage = failed.
- Groups: 2–3 words high energy, 3–5 conversational, 4–6 calm; break at sentence end, a ≥150 ms pause, or the limit. One group visible at a time; first caption 0.1–0.3 s in, not at 0.
- Hard-kill every group: `tl.to(g,{opacity:0,duration:0.12,ease:"power2.in"},end-0.12); tl.set(g,{opacity:0,visibility:"hidden"},end);`
- Size with `fitTextFontSize` (maxWidth 1600 landscape / 900 portrait, base 78, min 42). Full-width absolute container with centred text — never `left:50%; translateX(-50%)`. `overflow: visible`. Landscape 80–120 px from bottom; portrait ~600–700 px from bottom; never over the face.
- Fade the group or its words, not both. Over footage brightness (0–255): <60 `screen`, 60–180 `overlay`, >180 normal opaque; plain subtitles over >60 get a text-sized 30–40% scrim, never a full-width bar.
- Text behind the speaker: video → captions → cutout from `npx hyperframes remove-background` by `z-index`; `data-layout-allow-occlusion` on the cutout; the word reads best 30–55% covered.
- Ready-made styles: `npx hyperframes catalog --tag caption-style --json`.

## Cards over talking-head footage (1920×1080 / 1080×1920)

| Layout | Landscape x,y,w×h | Portrait |
| --- | --- | --- |
| Split, video beside card | 960,0,960×1080 | 0,960,1080×960 |
| Stack, video above | 14,14,1892×548 | 0,0,1080×844 |
| PiP 16:9 source | 1432,28,460×258 | 690,28,360×203 |

- Lower third = bottom 30%; side panel = right 42% (landscape) / bottom 40% (portrait). Overlay scenes need a transparent root.
- Cards in 0.4 s `power2.out`, out 0.35 s `power2.in`; information on screen within ~2.5 s, then hold so any paused frame reads as a finished poster. A static card dies after ~8 s; >15 s needs a staged reveal. Density: one card per 6–8 s under a minute, 8–12 s up to 3 min.
- Glass over bright footage: dark scrim (`rgba(0,0,0,.55)`→`.72`) + base `rgba(15,16,22,.78)` with `backdrop-filter: blur(22px)`.
- Talking heads: punch-ins on emphasis (wrapper transform), B-roll cut on the sentence, re-frame (0.5–0.7 s) only between cards.

## Reuse

Before hand-writing a named effect, transition, caption style or chart: `npx hyperframes catalog --query "<thing>" --json` (tags: `transition`, `camera`, `caption-style`, `motion-primitive`), then `npx hyperframes add <name>`. Installed items are source you restyle with the film's variables.
