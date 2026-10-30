---
name: video-design
description: Genera o actualiza video/design.md (paleta, tipografía, composición, fondos, look de captions y prohibiciones visuales) a partir de videos o frames de referencia. Usar cuando el usuario pase referencias y pida definir el estilo visual de los videos de un proyecto.
---

# Video Design

Escribe `video/design.md`: cómo se ve cada frame. No define tiempos, easing, transiciones ni ritmo; eso es `video/motion.md`.

## Entrada

Referencias que pase el usuario: videos y/o frames.

- Preguntá poco: una sola ronda al inicio, máximo 3 preguntas, solo lo que no se puede medir y cambia el archivo. Colores, tamaños y márgenes se miden, no se preguntan.
  - Sin referencias: pedí 1–3 videos o frames.
  - Fuente o logo de marca que no se puede identificar o no está en `assets/fonts/`: pedí los archivos. Sin ellos, usá una parecida y anotalo.
  - Referencias con estilos distintos: preguntá cuál manda.
  - Plataforma o formato que no coincide con las referencias o el proyecto: preguntá cuál es.
  - Si también falta `video/motion.md`, una sola ronda para los dos.
  - Nunca preguntes lo que ya dicen el DESIGN.md de raíz. Sin respuesta, persona ausente o "sin paradas": seguí con lo que hay y marcá `(default)`.
- **Video**: sacá frames representativos con `ffmpeg -i ref.mp4 -vf "select='gt(scene,0.3)'" -vsync vfr f/%03d.jpg` (uno por plano) y miralos.
- **Colores**: medilos, no los adivines. `python3 -c "from PIL import Image;im=Image.open('f.jpg').convert('RGB').quantize(8);p=im.getpalette();print(['#%02x%02x%02x'%tuple(p[i*3:i*3+3]) for _,i in sorted(im.getcolors(),reverse=True)])"`
- **DESIGN.md de raíz** (web): si existe, heredá marca (colores, fuentes) referenciando sus tokens por nombre. No copies valores. Las referencias de video mandan en todo lo demás.
- Lo que no se pueda deducir lleva un default marcado `(default)`.
- Referencias con estilos distintos y sin respuesta: tomá el dominante, no mezcles.
- Si `video/design.md` existe, actualizalo y conservá lo que las referencias no contradigan.

## Reglas al escribir

- Valores concretos: hex, px sobre 1080×1920 (o el formato del proyecto), pesos y tracking. Nunca "moderno" o "limpio" sin valor.
- Cada regla sale de las referencias, del DESIGN.md de raíz o va marcada `(default)`.
- Las referencias ganan: si usan algo de la lista de prohibidos, se permite y se anota.
- Máximo ~80 líneas. Sin teoría.

## Formato de video/design.md

```md
# Design

## Mundo visual
Una frase. Ej: "Editorial oscuro: negro cálido, una sola tipografía condensada, footage con grano."

## Paleta
| Rol | Hex o token | Uso |
Fondo, texto, acento (uno solo salvo que las refs muestren más), scrim.

## Tipografía
- Familias y rol (display / caption / dato)
- Tamaños en px, peso, tracking, mayúsculas o no
- Máx palabras por línea y líneas por pantalla

## Composición
- Punto focal y alineación dominante
- Márgenes en px
- Safe zones: las de la plataforma (no escribas números salvo una excepción propia del proyecto)
- Densidad: una idea por frame (default)

## Fondos y textura
Sólido, footage, grano, viñeta. Cómo se garantiza contraste sobre footage (scrim, caja, stroke).

## Captions
Caja, stroke, sombra, posición, cómo se ve la palabra enfatizada. Su movimiento va en motion.md.

## Elementos gráficos
Íconos (librería y grosor), formas, bordes, sombras, recortes de sujeto.

## Prohibido
5–8 reglas concretas.

## Frame de referencia
1–2 frames clave descritos con posiciones, tamaños y colores.
```

## Piso de calidad

- Contraste: texto ≥4.5:1, texto grande ≥3:1, medido contra el peor frame del footage, no contra el promedio.
- Texto secundario sobre color: un tinte del color o del texto principal, nunca gris.
- Sombras con offset y blur suave. Un halo de color sin offset es decoración (glow).

## Prohibiciones por defecto

Incluilas salvo que las referencias las contradigan:

- Texto con gradiente. El énfasis va por peso, tamaño o color sólido.
- Glass o blur como decoración.
- Fondos con gradiente violeta-azul.
- Glow o halo de color detrás del texto.
- Etiqueta o "kicker" chico encima del título.
- Numeración 01 / 02 / 03 salvo que la secuencia importe.
- Escenas armadas como cards iguales de ícono + título + texto.
- Emoji o glifos unicode en lugar de íconos.
- Círculos o polígonos como máscara para recortar un sujeto. Se recorta con un matte real o no se recorta.
- Fuente del sistema o Impact/Arial Black como display, salvo que sea el look elegido.
- Modo claro u oscuro por categoría. Se elige por dónde y cómo se ve el video.

## Cierre

Guardá el archivo y respondé con la frase de Mundo visual y 3 líneas de lo que lo define. No muestres el archivo entero salvo que lo pidan.
