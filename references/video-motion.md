---
name: video-motion
description: Genera o actualiza video/motion.md (ritmo, timing, easing, transiciones, texto en movimiento y prohibiciones) a partir de videos o frames de referencia. Usar cuando el usuario pase referencias y pida definir el motion o el estilo de movimiento de los videos de un proyecto.
---

# Video Motion

Escribe `video/motion.md`: cómo se mueve el video. No define colores, fuentes ni layout; eso es `video/design.md`. Si una regla depende de algo visual, referenciá design.md en vez de copiar valores.

## Entrada

Referencias que pase el usuario: videos (preferido) y/o frames.

- Preguntá poco: una sola ronda al inicio, máximo 3 preguntas, solo lo que no se puede medir y cambia el archivo. Timing, easing y cortes se miden, no se preguntan.
  - Sin referencias: pedí 1–3 videos (no frames).
  - Referencias con estilos distintos: preguntá cuál manda.
  - Plataforma o formato que no coincide con las referencias o el proyecto: preguntá cuál es.
  - Si también falta `video/design.md`, una sola ronda para los dos.
  - Nunca preguntes lo que ya dice el DESIGN.md de raíz. Sin respuesta, persona ausente o "sin paradas": seguí con lo que hay.
- **Video**: el motion se mide, no se adivina.
  - fps y duración: `ffprobe`.
  - Cortes: `ffmpeg -i ref.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep pts_time` → duración media de plano.
  - Frames: `ffmpeg -i ref.mp4 -vf fps=4 f/%03d.jpg`; mirá secuencias consecutivas para entradas, salidas, easing y texto. Subí a `fps=12` solo en tramos cortos que lo necesiten.
- **Solo frames**: deducí lo que se ve (densidad, motion blur, cómo aparece el texto). Lo que no se puede ver se infiere de lo que sí se ve y se marca con su origen: `(inferido: <evidencia>)`. Si no hay de dónde inferirlo, se omite; nunca rellenes con un valor genérico.
- Referencias con estilos distintos y sin respuesta: tomá el dominante, no mezcles.
- Si `video/motion.md` existe, actualizalo y conservá lo que las referencias no contradigan.

## Reglas al escribir

- Valores concretos: ms o frames, curvas `cubic-bezier` o nombres GSAP (`power3.out`). Nunca "suave" o "dinámico" sin número.
- Cada regla sale de las referencias o va marcada `(inferido: …)`. Sin evidencia, no hay regla.
- Máximo ~80 líneas. Sin teoría.

## Formato de video/motion.md

```md
# Motion

## Personalidad
Una frase. Ej: "Seco y editorial: cortes rápidos, entradas cortas, nada rebota."

## Formato
- Plataforma: TikTok, Reels, Shorts, YouTube (una o varias)
- Aspect ratio, fps, duración típica
- Hook: qué pasa en 0–3s

## Ritmo
- Duración media de plano/beat
- Sincronía: cortes en beat, en palabra o libres
- Hold mínimo para que algo se lea

## Entradas y salidas
| Elemento | Entrada | Duración | Curva | Salida |
Texto, imágenes/footage, UI, overlays. Stagger entre elementos.

## Transiciones
2–3 permitidas y cuándo usar cada una. Por defecto: corte seco.

## Texto en movimiento
Palabra a palabra o bloque, palabras por vez, cómo se marca el énfasis con movimiento (el color lo define design.md).

## Movimiento continuo
Qué se mueve durante los holds (ej: push-in 3% por plano) o "nada".

## Prohibido
5–8 reglas concretas.

## Ejemplo
Un video de 15s descrito plano a plano con tiempos.
```

## Prohibiciones por defecto

Incluilas salvo que las referencias las contradigan:

- Efecto typewriter.
- Bounce o elastic.
- Glow pulsante.
- Primer frame vacío o hook después de 1s.
- Todo entrando con el mismo fade-up.
- Todos los elementos animando a la vez.
- Rotaciones 3D o zooms sin motivo.

Si las referencias se ven hechas a mano, agregá "motion en dos" (cada pose se sostiene 2 frames a 24fps).

## Cierre

Guardá el archivo y respondé con la frase de Personalidad y 3 líneas de lo que lo define. No muestres el archivo entero salvo que lo pidan.
