# Estilos

Escribe o actualiza los dos archivos de un estilo en `video/styles/<nombre>/`:
- `design.md`: cómo se ve cada frame (paleta, tipografía, grilla, tratamiento de imagen, texto sobre imagen, elementos gráficos, style frames). Sin tiempos, easing, transiciones ni ritmo.
- `motion.md`: cuándo y cómo se mueve (tokens de tiempo y easing, ritmo, coreografía, entradas y salidas, transiciones, texto en movimiento, cámara virtual, audio y sync, animatic). Sin colores, fuentes ni layout: si una regla depende de algo visual, referenciá design.md en vez de copiar valores.

Si faltan los dos, una sola pasada para ambos.

## Entrada

- **Carpeta**: los videos de referencia y todo lo que se extrae de ellos van en `video/styles/<nombre>/refs/`. Actualizando, el estilo que se nombra (o el que elige la regla de estilo de SKILL.md). Nuevo, el nombre que dé el usuario o uno corto y descriptivo (`cortes-secos`, no `nuevo` ni `default`).
- Lo que pase el usuario: una descripción del estilo y/o referencias (videos, preferido, o frames). Lo que describe manda; las referencias completan el resto.
- Preguntá poco: una sola ronda al inicio, máximo 3 preguntas, solo lo que no se puede medir y cambia el archivo. Colores, tamaños, márgenes, timing, easing y cortes se miden, no se preguntan.
  - Sin descripción ni referencias: pedí 1–3 videos (para motion, no alcanza con frames).
  - Fuente o logo de marca que no se puede identificar o no está en `assets/fonts/`: pedí los archivos. Sin ellos, usá una parecida y anotalo.
  - Referencias con estilos distintos: preguntá cuál manda. Sin respuesta: tomá el dominante, no mezcles.
  - Plataforma o formato que no coincide con las referencias o el proyecto: preguntá cuál es.
  - Nunca preguntes lo que ya dice el DESIGN.md de raíz. Sin respuesta, persona ausente o "sin paradas": seguí con lo que hay.
- **Frames de design**: uno por plano, `ffmpeg -i ref.mp4 -vf "select='gt(scene,0.3)'" -vsync vfr video/styles/<nombre>/refs/frames/%03d.jpg`, y miralos.
- **Colores**: medilos, no los adivines. `python3 -c "from PIL import Image;im=Image.open('video/styles/<nombre>/refs/frames/001.jpg').convert('RGB').quantize(8);p=im.getpalette();print(['#%02x%02x%02x'%tuple(p[i*3:i*3+3]) for _,i in sorted(im.getcolors(),reverse=True)])"`
- **Motion**: se mide, no se adivina.
  - fps y duración: `ffprobe`.
  - Cortes: `ffmpeg -i ref.mp4 -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep pts_time` → duración media de plano.
  - Frames: `ffmpeg -i ref.mp4 -vf fps=4 video/styles/<nombre>/refs/frames/m%03d.jpg`; mirá secuencias consecutivas para entradas, salidas, easing y texto. Subí a `fps=12` solo en tramos cortos que lo necesiten.
  - Audio: no se escucha, se mide. `ffmpeg -i ref.mp4 -vn video/styles/<nombre>/refs/ref.wav` y `npx hyperframes audio video/styles/<nombre>/refs/ref.wav --only onsets --json`; cruzá los onsets con los frames para ver qué acción dispara cada sonido. El tipo de sonido se infiere de la acción y va `(inferido)`.
- **DESIGN.md de raíz** (web): si existe, heredá marca (colores, fuentes) referenciando sus tokens por nombre. No copies valores. Las referencias de video mandan en todo lo demás.
- Lo que no se ve directo se infiere de lo que sí se ve y se marca `(inferido)`. Si no hay de dónde inferirlo, escribí "Sin regla: se decide por video"; nunca rellenes con un valor genérico.
- Si el archivo existe, actualizalo y conservá lo que las referencias no contradigan.

## Reglas al escribir

- **Solo lo propio del estilo.** Contract, Taste, BANNED y safe zones de SKILL.md ya aplican a todo video: no los copies. Si el estilo endurece una regla o habilita un BANNED que usan sus refs, escribí solo esa diferencia.
- **Cada regla en su archivo**: lo que se ve en design.md, lo que se mueve o suena en motion.md. Nunca la misma regla en los dos.
- **Gramática, no contenido.** El archivo vale para cualquier video del proyecto, sea cual sea el tema. Nunca nombres el tema de la ref, sus marcas, productos, objetos, set, personas ni palabras o frases dichas. Escribí el rol: "mano con celular" → "b-roll de manos con el objeto del tema"; "rojo Netflix" → "color real de la marca citada"; "recargo" → "palabra negativa"; "ladrillo, lámpara" → "set cálido con luz tungsteno".
- Test por regla: si en un video sobre otro tema deja de tener sentido, está describiendo la ref. Abstraela o borrala.
- Excepción: lo que es del proyecto y no de la ref (marca y fuentes del DESIGN.md de raíz, o el set propio si el usuario dice que las refs son sus videos).
- La evidencia y las mediciones van en tu respuesta, no en el archivo. Escribí la regla resultante ("plano medio 1.5 s, rango 0.4–3.5 s"), no la medición ("23 cortes en 34.9 s"). Los cambios que pidió el usuario se escriben como el valor final, sin "reemplaza X".
- Valores concretos: hex, px sobre la resolución de los videos (la del proyecto o la de la skill), pesos, tracking, ms o frames, curvas `cubic-bezier` o nombres GSAP (`power3.out`). Nunca "moderno", "limpio", "suave" o "dinámico" sin valor; una descripción vaga se traduce a valores y se marca `(inferido)`.
- Cada regla sale de la descripción, de las referencias, del DESIGN.md de raíz o va marcada `(inferido)`.
- Las referencias ganan: si usan algo de BANNED, se permite y se anota.
- design.md: tratamiento de imagen describe el material, no cómo filmarlo (no hay cámara). Máximo ~80 líneas.
- motion.md: **tokens primero** (tiempos y curvas se definen una vez con nombre; las demás secciones los usan por nombre). **Cámara es solo la virtual** (reencuadre digital, parallax, cámara 3D); el movimiento propio del footage no se define. **Sonido por función y carácter, nunca por archivo** (tipo, carácter y acción que lo dispara; el archivo se elige al construir, solo de la librería de la skill, y si ninguno encaja ese cue va sin sonido). Si las refs se ven hechas a mano, agregá "motion en dos" (cada pose se sostiene 2 frames a 24 fps). Máximo ~100 líneas.
- Sin teoría.

## Formato de design.md

```md
# Design

## Mundo visual
Una frase sobre el tratamiento (medio, luz, textura, tono). Ni el tema ni lo que se muestra.

## Formato
Resolución y aspect. Safe zones: las de SKILL.md; solo anotá una excepción propia del proyecto, sin repetir sus números.

## Paleta
| Rol | Hex o token | Uso |
Fondo, texto, acento (uno solo salvo que las refs muestren más), scrim.
Proporción de uso (ej. 70 fondo / 20 texto / 10 acento) y combinaciones que no van.

## Tipografía
| Rol | Familia | Tamaño px | Peso | Tracking | Interlineado | Caja |
4–6 roles (display, título, cuerpo, caption, dato). Máx palabras por línea y líneas por pantalla.

## Grilla y layout
- Márgenes, columnas y unidad de espaciado (ej. 8 px)
- Alineación dominante y punto focal
- Layouts recurrentes (pantalla completa, split, tarjeta…) con sus posiciones
- Densidad: una idea por frame, salvo que las refs muestren más

## Tratamiento de imagen
- Técnica: footage, 2D plano (HTML/CSS/SVG), ilustración, collage, 3D
- Footage e imágenes: luz, grade y profundidad de campo que tienen que tener o que se les aplica
- 3D: luz, materiales y lente virtual
- Textura: grano, viñeta, ruido, o "ninguna"
- Contraste sobre imagen: scrim, caja, sombra o stroke

## Texto sobre imagen
Captions, títulos, lower thirds: caja, stroke, sombra, posición y cómo se ve el énfasis. Su movimiento va en motion.md.

## Elementos gráficos
Íconos (librería y grosor), formas, bordes, radios, sombras, recortes de sujeto, logos.

## Prohibido
Hasta 8 reglas propias del estilo. BANNED de SKILL.md ya aplica: no lo repitas.

## Style frames
2–3 frames clave con placeholders (`[sujeto]`, `[palabra clave]`, `[marca]`, `[prueba]`), con posiciones, tamaños y colores. Nada de la ref. El del gancho respeta el frame 0 de SKILL.md (Story).
```


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
Hasta 8 reglas propias del estilo. BANNED de SKILL.md ya aplica: no lo repitas.

## Animatic
15 s plano a plano con roles en vez de contenido: `0–1.5 s: [b-roll del tema] + título gancho con [marca] en caja`.
```


## Cierre

Antes de guardar, buscá en cada archivo nombres propios, marcas, objetos concretos y palabras entre comillas que vengan de la ref, y reemplazalos por su rol; y cualquier regla que ya esté en SKILL.md o en el otro archivo del estilo, y borrala.

Guardá y respondé, por archivo, con su frase de Mundo visual o Personalidad y 3 líneas de lo que lo define. No muestres el archivo entero salvo que lo pidan.
