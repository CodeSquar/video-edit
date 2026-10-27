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

One request per scene line, into `assets/voice/<scene-id>.pcm`:

```bash
curl -sf https://openrouter.ai/api/v1/audio/speech \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" -H "Content-Type: application/json" \
  -d '{"model":"google/gemini-3.8-flash-lite-tts","voice":"Kore","response_format":"pcm",
       "input":"First the snowball — then the hill — then the speed.",
       "instructions":"Warm, clear, unhurried. Short pause between phrases."}' \
  -o assets/voice/s1.pcm
```

PowerShell: `curl.exe` and `$env:OPENROUTER_API_KEY`. Delivery goes in `instructions`, never in `input`.

Gemini returns only `pcm` (16-bit mono, 24 kHz). Wrap it: `ffmpeg -y -f s16le -ar 24000 -ac 1 -i assets/voice/s1.pcm assets/voice/s1.wav`, then delete the `.pcm`. Another model that returns `mp3` (e.g. MiniMax): `"response_format":"mp3"` and save `.mp3` directly.

## Place and time

1. Duration per take: `ffprobe -v error -show_entries format=duration -of csv=p=0 assets/voice/s1.wav`.
2. Scene `data-duration` = take + 0.4–0.8 s of air (more before a payoff). Trim words, never stretch motion to fill.
3. One `<audio>` per take in the root, `data-start` = its scene start (+0.2 s lead-in):
   `<audio id="vo-s1" class="clip" src="assets/voice/s1.wav" data-start="0.2" data-volume="1"></audio>`
4. Music under the voice ≈ 0.14 volume; mix with `npx hyperframes normalize-audio`.

## Check

- Each take's duration ≈ its words ÷ 2.3 s. Far off → a wrong read or spoken directions: change the text (spell it out) and regenerate that line only.
- Every scripted scene has its take; root `data-duration` covers the last take plus its air.
- You can measure the audio (`npx hyperframes audio renders/<name>.mp4 --json`), not hear it — say so.
