# Composition format

Only if a command fails and this file doesn't explain it: `npx hyperframes docs compositions`, `docs data-attributes`, `docs gsap`, `docs troubleshooting`.

## Skeleton

```html
<!-- index.html -->
<html data-composition-variables='[
  {"id":"headline","type":"string","label":"Headline","default":"…"},
  {"id":"color-ground","type":"color","label":"Background","default":"#F2EDE4"},
  {"id":"color-ink","type":"color","label":"Text","default":"#141414"},
  {"id":"color-accent","type":"color","label":"Accent","default":"#E4572E"},
  {"id":"font-display","type":"string","label":"Display font","default":"Oswald"}
]'>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="12"
       data-width="1920" data-height="1080">
    <div id="ground" style="position:absolute;inset:0;background:var(--color-ground)"></div>
    <div id="intro" data-composition-id="intro" data-composition-src="compositions/intro.html"
         data-start="0" data-duration="4" data-track-index="1" data-track-kind="graphics"
         data-width="1920" data-height="1080"></div>
    <audio id="bgm" class="clip" src="assets/bgm.mp3" data-start="0" data-duration="12"
           data-volume="0.6" data-fade-in="0.4" data-fade-out="1.5"></audio>
  </div>
  <script>window.__timelines["main"] = gsap.timeline({ paused: true });</script>
</body>
</html>
```

```html
<!-- compositions/intro.html — styles, markup and script ALL inside <template> -->
<template>
  <style>
    #root { position:absolute; inset:0; }
    #intro-title { font:900 96px/1 var(--font-display); color:var(--color-ink); }
  </style>
  <div id="root" data-composition-id="intro" data-width="1920" data-height="1080">
    <h1 id="intro-title" class="clip" data-start="0.4" data-duration="3.4" data-var-text="headline">…</h1>
  </div>
  <script>
    const tl = gsap.timeline({ paused: true });
    tl.fromTo("#intro-title",
      { opacity: 0, filter: "blur(8px)" },
      { opacity: 1, filter: "blur(0px)", duration: 0.18, ease: "power4.out" }, 0.4);
    window.__timelines["intro"] = tl;   // last line, after every tween
  </script>
</template>
```

- Host id = scene root `data-composition-id` = timeline key, or each render waits 45 s per scene and shows static frames.
- Scene root sized with `inset: 0`, styled as `#root` (not a class). Prefix ids per scene (`#intro-title`); a scene's timeline can't reach outside its file.
- A fill on the composition root is dropped with shader transitions/HDR: put the ground on a full-bleed child (as above). An untimed full-bleed child needs `position:absolute; inset:0`.
- Place tweens at absolute seconds (`tl.to(el, {...}, 2.4)`). Measure layout once before building tweens, never in `onUpdate`. Transforms on a `<span>` need `display:inline-block`. Finite repeats only: `repeat: Math.max(0, Math.floor(dur / cycle) - 1)`.
- Async build (e.g. `document.fonts.ready.then(...)`) is fine if you register the timeline at the end of the callback.

## Attributes

| Attribute | Meaning |
| --- | --- |
| `data-start`, `data-duration` | Seconds, local to the declaring file. `data-start="intro + 0.5"` = after `intro` ends (typos silently resolve to 0 — snapshot it) |
| `data-track-index` | Studio lane only; paint order is `z-index` |
| `data-track-kind` | `graphics` on scene/overlay hosts; `captions` on the one host holding all caption groups |
| `data-composition-src`, `data-variable-values` | Mount a scene file; per-mount variable values (JSON object) |
| `data-media-start` | Trim offset into the source media |
| `data-playback-rate` | Constant speed 0.1–10 (pitch preserved). Ramps: a `rate` lane in `data-automation` |
| `data-has-audio="true"` / `muted` | One of them on every timed `<video>` |
| `data-volume`, `data-fade-in`, `data-fade-out` | Gain (1 = 0 dB, max 3.98) and edge fades |
| `data-motion-blur="on"` | On the root: render-time motion blur for fast 2D movers (`data-motion-blur-shutter`, 360 = strong) |
| `data-hidden` | Hidden in preview and render |
| `data-no-timeline` | Root of a still composition (else every render waits 45 s) |
| `data-hold` | Marks a deliberate long hold for the `dead_stretch` check |

Timing facts: a clip nested in another timed element counts `data-start` from the composition and only shows while its parent shows. `<video>/<audio>` without `data-duration` play their full length; `<img>` defaults to 3 s. A host's `data-duration` is the scene's slot: a shorter scene holds its last frame.

## Variables

Declare `[{id, type, label, default}]` on `<html>`. Types: `string` (`maxLength`), `number` (`min/max/step/unit`), `color`, `boolean`, `enum` (`options: [{value,label}]`). Bind with `data-var-text`, `data-var-src` (keep a real fallback `src`), `var(--id)`; in script, `window.__hyperframes.getVariables()` once at init. Batch renders: `npx hyperframes render --batch rows.json --output "renders/{name}.mp4"`.

## Fonts

Bundled (resolve by name): Inter, Montserrat, Outfit, Nunito, Oswald, League Gothic, Archivo Black, Space Mono, IBM Plex Mono, JetBrains Mono, EB Garamond, Playfair Display, Source Code Pro, Noto Sans JP, Roboto, Open Sans, Lato, Poppins. Anything else: `@font-face { src: url('assets/fonts/x.woff2') }` in the file that uses it (lint: `font_family_without_font_face`). Use only weights the font ships. Fit text to a width: `window.__hyperframes.fitTextFontSize(text, { fontFamily, fontWeight, maxWidth })` → `{ fontSize }`.

## Adding media (write what a Studio drop writes)

- `id`, `class="clip"`, `data-start` (never a silent 0), `data-track-index`; video with sound `playsinline data-has-audio="true"`, silent `muted playsinline`; audio `data-volume="1"`.
- Full frame: `position:absolute; left:0; top:0; width/height = canvas; object-fit:contain`.
- Time a `<video>` **or** its wrapper, never both. Punch-ins/Ken Burns: tween `scale`/`x`/`y` on a wrapper *inside* the clip; crops/reveals: `clip-path` on an inner wrapper.
- Raise the root `data-duration` to cover the new clip. Clamp ends to the file's `ffprobe` length or the render ends in black.
- Footage with keyframes >1 s apart freezes on seek: re-encode with `ffmpeg -g <fps>`.
- Video facts: full-screen linear gradients on dark grounds band under H.264 (use radial or solid + local glow); an accent below ~15% opacity vanishes in compression.

## Other runtimes

| Runtime | How |
| --- | --- |
| CSS `@keyframes` | Auto-detected; finite iterations, `animation-fill-mode: both`, `data-start` on the element |
| WAAPI | `el.animate(…, { fill: "both" })` then `pause()`; use `delay` for timing |
| Lottie | `autoplay: false`, set `loop`, push instance to `window.__hfLottie` |
| Canvas / Three.js / p5 | Draw from time in an `hf-seek` listener; set `data-duration` on the root |
| Charts/maps libs | Drive from a GSAP tween's `onUpdate`, never the library's own transitions |

```js
function renderAt(t) { /* draw from state derived from t alone */ }
window.addEventListener("hf-seek", (e) => {
  renderAt(e.detail.time);           // async GPU/decode work: e.detail.waitUntil(promise)
});
renderAt(0);
```

Simulations: simulate once at load into arrays, look up state at `t`. Heavy setup registers a `window.__hf.buildReady["<key>"]` promise.

## Lint errors you'll meet first

| Rule | Fix |
| --- | --- |
| `video_missing_muted` | `data-has-audio="true"` or `muted` |
| `gsap_css_transform_conflict` | Start state inside `fromTo`, not CSS `transform` |
| `gsap_animates_clip_element` | Animate a child of the `.clip` (or only its opacity) |
| `video_nested_in_timed_element` | Time the video or its wrapper, not both |
| `media_missing_id`, `media_crossorigin_breaks_preview` | `id` on every `<audio>`; drop `crossorigin` |
| `gsap_timeline_registered_before_async_build` | Register at the end of the async callback |
| `standalone_composition_wrapped_in_template` | Only scene files use `<template>` |
| `subcomposition_root_styled_by_class` | Style the scene root as `#root` |
| `clip_ends_past_root_duration` | Raise root `data-duration` |
| `sweep_static` / `missing_data_no_timeline` | Spread the motion, or mark a still composition `data-no-timeline` |

Layout audit opt-outs, narrowest first: `data-layout-allow-overflow` (decorative wrapper only), `data-layout-bleed="true"` (one intentional crop), `data-layout-allow-overlap`, `data-layout-allow-occlusion`, `data-layout-ignore`.

## Common faults

| Symptom | Cause |
| --- | --- |
| Blank/frozen scene | Timeline registered before async build; `visibility` tweened on a `.clip`; host id ≠ timeline key |
| Drift between renders | Layout measured in `onUpdate`/rAF/clock; two timelines on one property |
| Jump at a cut | Outgoing/incoming states differ at the seam — snapshot just before and after |
| Ease off at a handoff | Speeds don't match — mirror the ease (`power3.in` out, `power3.out` in) |
| White flash at a seam | Nothing opaque behind the scenes — paint the stage ground |
