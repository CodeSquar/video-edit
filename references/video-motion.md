---
name: video-motion
description: Genera o actualiza video/styles/<nombre>/motion.md (tokens de tiempo y easing, ritmo, coreografía, entradas y salidas, transiciones, texto en movimiento, cámara virtual, audio y sync, prohibiciones y animatic) a partir de una descripción o de videos o frames de referencia. Usar cuando el usuario pase referencias y pida definir el motion o el estilo de movimiento de los videos de un proyecto.
---

# Video Motion

Escribe `video/styles/<nombre>/motion.md`: cómo se mueve el video. No define colores, fuentes ni layout; eso es el `design.md` del mismo estilo. Si una regla depende de algo visual, referenciá design.md en vez de copiar valores.

## Entrada

- **Carpeta**: escribí en `video/styles/<nombre>/`; los videos de referencia y todo lo que se extrae de ellos van en su `refs/`. Actualizando, el estilo que se nombra (o el que elige la regla de estilo de SKILL.md). Nuevo, el nombre que dé el usuario o uno corto y descriptivo del estilo (`cortes-secos`, no `nuevo` ni `default`).
Lo que pase el usuario: una descripción del estilo y/o referencias (videos, preferido, o frames). Lo que describe manda; las referencias completan el resto.

- Preguntá poco: una sola ronda al inicio, máximo 3 preguntas, solo lo que no se puede medir y cambia el archivo. Timing, easing y cortes se miden, no se preguntan.
  - Sin descripción ni referencias: pedí 1–3 videos (no frames).
  - Referencias con estilos distintos: preguntá cuál manda.
  - Plataforma o formato que no coincide con las referencias o el proyecto: preguntá cuál es.
  - Si también falta el `design.md` del estilo, una sola ronda para los dos.
  - Nunca preguntes lo que ya dice el DESIGN.md de raíz. Sin respuesta, persona ausente o "sin paradas": seguí con lo que hay.
- **Video**: el motion se mide, no se adivina.
  - fps y duración: `ffprobe`.
  - Cortes: `ffmpeg -i ref.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep pts_time` → duración media de plano.
  - Frames: `ffmpeg -i ref.mp4 -vf fps=4 video/styles/<nombre>/refs/frames/%03d.jpg`; mirá secuencias consecutivas para entradas, salidas, easing y texto. Subí a `fps=12` solo en tramos cortos que lo necesiten.
  - Audio: no se escucha, se mide. `ffmpeg -i ref.mp4 -vn video/styles/<nombre>/refs/ref.wav` y `npx hyperframes audio video/styles/<nombre>/refs/ref.wav --only onsets --json`; cruzá los onsets con los frames para ver qué acción dispara cada sonido. El tipo de sonido se infiere de la acción y va `(inferido)`.
- **Solo frames**: deducí lo que se ve (densidad, motion blur, cómo aparece el texto). Lo que no se puede ver se infiere de lo que sí se ve y se marca `(inferido)`. Si no hay de dónde inferirlo, escribí "Sin regla: se decide por video"; nunca rellenes con un valor genérico.
- Referencias con estilos distintos y sin respuesta: tomá el dominante, no mezcles.
- Si el `motion.md` del estilo existe, actualizalo y conservá lo que las referencias no contradigan.

## Reglas al escribir

- **Gramática, no contenido.** El archivo vale para cualquier video del proyecto, sea cual sea el tema. Nunca nombres el tema de la ref, sus marcas, productos, objetos, set, personas ni palabras o frases dichas. Escribí el rol: "mano con celular" → "b-roll de manos con el objeto del tema"; "rojo Netflix" → "color real de la marca citada"; "recargo" → "palabra negativa"; "ladrillo, lámpara" → "set cálido con luz tungsteno".
- Test por regla: si en un video sobre otro tema deja de tener sentido, está describiendo la ref. Abstraela o borrala.
- Excepción: lo que es del proyecto y no de la ref (marca y fuentes del DESIGN.md de raíz, o el set propio si el usuario dice que las refs son sus videos).
- La evidencia y las mediciones van en tu respuesta, no en el archivo. Escribí la regla resultante ("plano medio 1.5 s, rango 0.4–3.5 s"), no la medición ("23 cortes en 34.9 s"). Los cambios que pidió el usuario se escriben como el valor final, sin "reemplaza X".
- Valores concretos: ms o frames, curvas `cubic-bezier` o nombres GSAP (`power3.out`). Nunca "suave" o "dinámico" sin número.
- Cada regla sale de la descripción, de las referencias o va marcada `(inferido)`. Una descripción vaga ("dinámico") se traduce a valores y se marca `(inferido)`.
- **Tokens primero.** Tiempos y curvas se definen una vez como tokens con nombre; las demás secciones los usan por nombre, no repiten números.
- **Cámara es solo la virtual**: lo que la composición controla (reencuadre digital sobre footage o imágenes, parallax de capas, cámara 3D). El movimiento propio del footage no se define acá.
- **Sonido por función y carácter, nunca por archivo.** Escribí tipo genérico (acento corto, golpe, build, textura, música de fondo), carácter (seco, grave, brillante) y la acción que lo dispara. Nunca nombres de archivo, marcas ni fuentes de sonido. El archivo se elige al construir, solo de la librería de la skill; si ninguno encaja, ese cue va sin sonido.
- Máximo ~100 líneas (las tablas suman). Sin teoría.

## Formato de motion.md

```md
# Motion

## Personalidad
Una frase + 2–3 principios (ej. "rápido pero legible").

## Formato
fps y plataforma(s).

## Tokens de tiempo
| Token | Frames | Uso |
3–5 (ej. corte, micro, corto, medio, largo).

## Tokens de easing
| Token | Curva | Uso |
3–4 (entrada, salida, movimiento, constante). Curvas `cubic-bezier` o GSAP.

## Ritmo
- Duración media de plano/beat y rango
- Sincronía: cortes en beat, en palabra o libres
- Hold mínimo para que algo se lea

## Coreografía
Orden de entrada (qué va primero), stagger en frames, un protagonista por vez, qué espera a qué.

## Entradas y salidas
| Elemento | Entrada | Tiempo | Easing | Salida |
Texto, imágenes/footage, UI, overlays. Tiempo y easing por token.

## Transiciones
2–3 permitidas y cuándo usar cada una. Por defecto: corte seco.

## Texto en movimiento
Palabra a palabra o bloque, palabras por vez, cómo se marca el énfasis con movimiento (el color lo define design.md).

## Cámara
Reencuadre digital, parallax o cámara 3D: movimiento, distancia, token. Si nada: "fija".

## Audio y sync
| Acción en pantalla | Tipo de sonido | Carácter | Volumen relativo |
Más: qué marca el reloj (voz, beat o libre) y la música bajo la voz.

## Movimiento continuo
Qué se mueve durante los holds y loops, o "nada".

## Prohibido
5–8 reglas concretas.

## Animatic
15 s plano a plano con roles en vez de contenido: `0–1.5 s: [b-roll del tema] + título gancho con [marca] en caja; sin caption`.
```

## Prohibiciones por defecto

Incluilas salvo que las referencias las contradigan:

- Efecto typewriter.
- Bounce o elastic.
- Glow pulsante.
- Primer frame vacío o hook después de 1s.
- Captions de la voz en el frame del gancho (arrancan en el primer corte).
- Todo entrando con el mismo fade-up.
- Todos los elementos animando a la vez.
- Rotaciones 3D o zooms sin motivo.

Si las referencias se ven hechas a mano, agregá "motion en dos" (cada pose se sostiene 2 frames a 24fps).

## Cierre

Antes de guardar, buscá en el archivo nombres propios, marcas, objetos concretos y palabras entre comillas que vengan de la ref, y reemplazalos por su rol.

Guardá el archivo y respondé con la frase de Personalidad y 3 líneas de lo que lo define. No muestres el archivo entero salvo que lo pidan.
