# Voice-off

Only when the person asked for a voiceover. The voice is the clock: write the lines, generate one take per scene, then time the scenes to the takes.

## Script

- Pace ≈ 3.3 words/s (takes at 1.2x, pauses cut). 15 s ≈ 50 words, 30 s ≈ 100, 60 s ≈ 200. ≤ ~19 words per scene. No silence between lines: the next voice starts as the last one ends.
- Write like a person: contractions, short lines mixed with longer ones. Read it aloud; if it sounds like a brochure, rewrite.
- The first line creates tension (a claim, a question, a contrast, a number). Never "Welcome to…" / "Introducing…".
- Write each line as discrete cues ("first the snowball — then the hill — then the speed"), so each on-screen piece can land when the voice names it.
- Write what the voice must say: TTS reads literally. `10x` → "ten times", `$1.9T` → "nearly two trillion dollars", `API` → "A P I", `acme.com` → "acme dot com". The screen shows the exact figure; the screen never repeats the spoken sentence word for word.
- Silent scenes are fine: leave them out of the script.
- A script the person pasted: keep their words; only split it into scene-sized lines at sentence or clause boundaries.

Put the lines in `SPEC.md` under each shot (`VO: …`), one line per scene.

## Generate (OpenRouter)

Endpoint `POST https://openrouter.ai/api/v1/audio/speech` (OpenAI-compatible, returns raw audio bytes, errors as JSON).

Default model `google/gemini-3.8-flash-lite-tts` (2026, ≈ $0.01 per minute of audio), voice `Kore`. It picks the language from the text. Another model or voice only if the person names one; list the available ones with `curl -s "https://openrouter.ai/api/v1/models?output_modalities=speech"` (`supported_voices` per model).

**Key:** use `$OPENROUTER_API_KEY` from the environment, as-is. Never read it from a file or `.env`, never print it, never write it into the project. If it is unset, stop and ask the person to set it.

### One call: `scripts/voice.py`

Write the lines to `voice.txt` in the film folder, one take per scene, `<scene-id> | <spoken text>`:

```
s1 | First the snowball — then the hill — then the speed.
s2 | Ten times faster than last year.
```

Then, from the film folder:

```bash
python <skill>/scripts/voice.py voice.txt --instructions "Energetic, quick, punchy. No pauses between phrases."
```

Delivery goes in `--instructions`, written for the film's language and accent (e.g. "Español rioplatense, con voseo, cálido…"), never in the text. The script requests every take in parallel (Gemini returns 24 kHz pcm; it wraps it to `assets/voice/<id>.wav`), trims the silence at both ends and cuts every inner pause to 0.08 s, applies **one tempo to the whole film** (`--tempo auto`: 1.2×; or a fixed `--tempo 1.1`), transcribes every take in one pass and writes `assets/voice/timings.json`. It prints per take: length, words/s, each word's time inside the take, and a suggested `scene_start` / `scene_duration` (take + `--lead 0` + `--air 0.05`) / `vo_start`, back to back, then the `const VO = {…};` line. Use those numbers; give a payoff a beat (≤ 0.2 s) by shifting the later scenes, never stretch motion to fill.

The film has a target length (the script, `motion.md`): pass `--tempo fit:45` on the first run and the tempo is picked to land it (clamped to 0.9–1.25×), so there is no second run. Wrong length afterwards: run again with `--tempo 1.1`. The takes already made are re-timed to it and the timings rebuilt; nothing is re-requested, no `ffmpeg` by hand. A `402 … in-flight` from OpenRouter means it is holding credit for the takes still in flight, not that the balance ran out; the script waits and retries those on its own.

Fix one line: edit it in `voice.txt` and run again with `--only s3`. Only that take is regenerated, at the film's tempo, and the timings are rebuilt. Existing takes are never re-requested without `--only` or `--force`.

Once `index.html` exists, any rerun also re-times the film (`scripts/retime.py`, one summary line): the VO line is rewritten, and every `data-start`/`data-duration` (scenes, voice, sfx, music, root) moves with the take it sits under. A scene ending on a cut follows that cut, so a longer take lengthens its scene. Cues written as `VO.sX + t` follow on their own. What is left by hand: for a take whose *words* changed, re-read its word times from the table and fix the `+ t` offsets of that scene only. Don't rewrite the script or shift the other scenes.

Another model that returns mp3 (e.g. MiniMax) is not covered by the script: call the endpoint with `curl` and `"response_format":"mp3"` for that case only.

## Place

One `<audio>` per take in the root, `data-start` = its `vo_start`:
`<audio id="vo-s1" class="clip" src="assets/voice/s1.wav" data-start="0.2" data-volume="1"></audio>`. Music under the voice ≈ 0.14 volume; mix with `npx hyperframes normalize-audio`.

`data-start` stays a literal number in the HTML: the render mixes audio from the attributes as written, so a value set from JS is ignored for sound. In the script, cues go through the VO line:

```js
const VO = {"s1": 0.2, "s2": 7.97};   // pasted from voice.py; retime.py keeps it current
const tl = gsap.timeline({ paused: true });
tl.fromTo("#s2-count", { opacity: 0 }, { opacity: 1, duration: 0.15 }, VO.s2 + 1.46);  // "64" at 1.46 in s2
```

## Check

- The script marks a take whose transcribed word count is far from its line (`<- word count off`): a wrong read or spoken directions. Spell it out and rerun with `--only <id>`. Takes whose transcript has digits ("1994" for five spoken words) are not flagged.
- Every scripted scene has its take; root `data-duration` covers the last take plus its air.
- You can measure the audio (SKILL.md, Render), not hear it — say so.
