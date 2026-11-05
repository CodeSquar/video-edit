---
name: video-design
description: Genera o actualiza video/styles/<nombre>/design.md (paleta, tipografía, grilla, tratamiento de imagen, texto sobre imagen, elementos gráficos, prohibiciones y style frames) a partir de una descripción o de videos o frames de referencia. Usar cuando el usuario pase referencias y pida definir el estilo visual de los videos de un proyecto.
---

# Video Design

Escribe `video/styles/<nombre>/design.md`: cómo se ve cada frame. No define tiempos, easing, transiciones ni ritmo; eso es el `motion.md` del mismo estilo.

## Entrada

- **Carpeta**: escribí en `video/styles/<nombre>/`; los videos de referencia y todo lo que se extrae de ellos van en su `refs/`. Actualizando, el estilo que se nombra (o el que elige la regla de estilo de SKILL.md). Nuevo, el nombre que dé el usuario o uno corto y descriptivo del estilo (`cortes-secos`, no `nuevo` ni `default`).
Lo que pase el usuario: una descripción del estilo y/o referencias (videos o frames). Lo que describe manda; las referencias completan el resto.

- Preguntá poco: una sola ronda al inicio, máximo 3 preguntas, solo lo que no se puede medir y cambia el archivo. Colores, tamaños y márgenes se miden, no se preguntan.
  - Sin descripción ni referencias: pedí 1–3 videos o frames.
  - Fuente o logo de marca que no se puede identificar o no está en `assets/fonts/`: pedí los archivos. Sin ellos, usá una parecida y anotalo.
  - Referencias con estilos distintos: preguntá cuál manda.
  - Plataforma o formato que no coincide con las referencias o el proyecto: preguntá cuál es.
  - Si también falta el `motion.md` del estilo, una sola ronda para los dos.
  - Nunca preguntes lo que ya dice el DESIGN.md de raíz. Sin respuesta, persona ausente o "sin paradas": seguí con lo que hay.
- **Video**: sacá frames representativos con `ffmpeg -i ref.mp4 -vf "select='gt(scene,0.3)'" -vsync vfr video/styles/<nombre>/refs/frames/%03d.jpg` (uno por plano) y miralos.
- **Colores**: medilos, no los adivines. `python3 -c "from PIL import Image;im=Image.open('video/styles/<nombre>/refs/frames/001.jpg').convert('RGB').quantize(8);p=im.getpalette();print(['#%02x%02x%02x'%tuple(p[i*3:i*3+3]) for _,i in sorted(im.getcolors(),reverse=True)])"`
- **DESIGN.md de raíz** (web): si existe, heredá marca (colores, fuentes) referenciando sus tokens por nombre. No copies valores. Las referencias de video mandan en todo lo demás.
- Lo que no se ve directo se infiere de lo que sí se ve y se marca `(inferido)`. Si no hay de dónde inferirlo, escribí "Sin regla: se decide por video"; nunca rellenes con un valor genérico.
- Referencias con estilos distintos y sin respuesta: tomá el dominante, no mezcles.
- Si el `design.md` del estilo existe, actualizalo y conservá lo que las referencias no contradigan.

## Reglas al escribir

- **Gramática, no contenido.** El archivo vale para cualquier video del proyecto, sea cual sea el tema. Nunca nombres el tema de la ref, sus marcas, productos, objetos, set, personas ni palabras o frases dichas. Escribí el rol: "mano con celular" → "b-roll de manos con el objeto del tema"; "rojo Netflix" → "color real de la marca citada"; "recargo" → "palabra negativa"; "ladrillo, lámpara" → "set cálido con luz tungsteno".
- Test por regla: si en un video sobre otro tema deja de tener sentido, está describiendo la ref. Abstraela o borrala.
- Excepción: lo que es del proyecto y no de la ref (marca y fuentes del DESIGN.md de raíz, o el set propio si el usuario dice que las refs son sus videos).
- La evidencia y las mediciones van en tu respuesta, no en el archivo. Escribí la regla resultante ("plano medio 1.5 s, rango 0.4–3.5 s"), no la medición ("23 cortes en 34.9 s"). Los cambios que pidió el usuario se escriben como el valor final, sin "reemplaza X".
- Valores concretos: hex, px sobre la resolución en la que se van a hacer los videos (la del proyecto o la de la skill), pesos y tracking. Nunca "moderno" o "limpio" sin valor.
- Cada regla sale de la descripción, de las referencias, del DESIGN.md de raíz o va marcada `(inferido)`. Una descripción vaga ("limpio") se traduce a valores y se marca `(inferido)`.
- Tratamiento de imagen describe el material, no cómo filmarlo: no hay cámara. El footage lo trae el usuario o se busca; las reglas dicen cómo tiene que verse y qué se le aplica.
- Las referencias ganan: si usan algo de la lista de prohibidos, se permite y se anota.
- Máximo ~80 líneas. Sin teoría.

## Formato de design.md

```md
# Design

## Mundo visual
Una frase sobre el tratamiento (medio, luz, textura, tono). Ni el tema ni lo que se muestra.

## Formato
Resolución y aspect. Safe zones: las de la skill para la plataforma; solo anotá una excepción propia del proyecto.

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
5–8 reglas concretas.

## Style frames
2–3 frames clave con placeholders (`[sujeto]`, `[palabra clave]`, `[marca]`, `[prueba]`), con posiciones, tamaños y colores. Nada de la ref.
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

Antes de guardar, buscá en el archivo nombres propios, marcas, objetos concretos y palabras entre comillas que vengan de la ref, y reemplazalos por su rol.

Guardá el archivo y respondé con la frase de Mundo visual y 3 líneas de lo que lo define. No muestres el archivo entero salvo que lo pidan.
