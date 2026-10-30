# Voice-off

Only when the person asked for a voiceover. The voice is the clock: write the lines, generate one take per scene, then time the scenes to the takes.

## Script

- Pace ≈ 2.2–2.5 words/s. 15 s ≈ 35 words, 30 s ≈ 70, 60 s ≈ 140. ≤ ~19 words per scene. The script should feel shorter than the film; silence between lines is a feature.
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
python <skill>/scripts/voice.py voice.txt --instructions "Warm, clear, unhurried. Short pause between phrases."
```

Delivery goes in `--instructions`, written for the film's language and accent (e.g. "Español rioplatense, con voseo, cálido…"), never in the text. The script requests every take in parallel (Gemini returns 24 kHz pcm; it wraps it to `assets/voice/<id>.wav`), trims the silence at both ends, applies **one tempo to the whole film** (`--tempo auto`: a read slower than 2.2 words/s is sped up toward 2.4, at most 1.2×; or a fixed `--tempo 1.1`), transcribes every take in one pass and writes `assets/voice/timings.json`. It prints per take: length, words/s, each word's start, and a suggested `scene_start` / `scene_duration` (take + `--lead 0.2` + `--air 0.6`) / `vo_start`, back to back. Use those numbers; give a payoff more air by shifting the later scenes, never stretch motion to fill.

Fix one line: edit it in `voice.txt` and run again with `--only s3`. Only that take is regenerated, at the film's tempo, and the timings are rebuilt. Existing takes are never re-requested without `--only` or `--force`.

Another model that returns mp3 (e.g. MiniMax) is not covered by the script: call the endpoint with `curl` and `"response_format":"mp3"` for that case only.

## Place

One `<audio>` per take in the root, `data-start` = its `vo_start`:
`<audio id="vo-s1" class="clip" src="assets/voice/s1.wav" data-start="0.2" data-volume="1"></audio>`. Music under the voice ≈ 0.14 volume; mix with `npx hyperframes normalize-audio`.

## Check

- The script marks a take whose transcribed word count is far from its line (`<- word count off`): a wrong read or spoken directions. Spell it out and rerun with `--only <id>`. Transcripts write numbers as digits ("85" for "eighty-five"); that alone is not a wrong read.
- Every scripted scene has its take; root `data-duration` covers the last take plus its air.
- You can measure the audio (SKILL.md, Render), not hear it — say so.
