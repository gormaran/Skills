---
name: gormaran-viral-reels
description: >
  Genera reels virales Y con intención comercial para la cuenta de Instagram @gormaran_ia_marketing de
  GORMARAN Marketing Agency (gormaran-marketing.com, agencia de marketing digital con IA en Vitoria-Gasteiz).
  Investiga referentes y tendencias del nicho, elige objetivo, escribe ganchos, guion con texto en pantalla
  y planos, caption y un CTA de palabra clave (RADAR, GEO o RESERVAS) sincronizado con el workflow de n8n
  «GORMARAN · Alternativa ManyChat», que entrega el recurso por DM tras seguir la cuenta. Úsala cuando el
  usuario diga "hazme un reel", "guion para reel", "ideas de reels", "reel viral", "reel para captar
  clientes", "contenido para Instagram", "calendario de reels", "analiza este reel", "por qué no funcionó
  mi reel" o pegue un enlace de un reel para modelarlo. También edita vídeos que el usuario adjunte como
  archivo: los "ve" (fotogramas) y "escucha" (transcripción con tiempos), propone mejoras y entrega el reel
  con subtítulos Bebas Neue tamaño 12 animados palabra por palabra y motion graphics acordes a lo que se dice
  ("subtitula este vídeo", "edita mi reel", "ponle subtítulos y gráficos", "monta este vídeo").
user-invokable: true
argument-hint: "[tema o idea | vídeo adjunto] [objetivo: guardar|compartir|seguir|lead] [opcional: RADAR|GEO|RESERVAS] [opcional: URL de un reel a modelar] [opcional: nº de reels]"
license: MIT
metadata:
  author: GORMARAN Marketing Agency
  version: "2.0.0"
  category: content
  language: es
---

# GORMARAN · Reels virales con intención comercial

Fábrica de reels para **@gormaran_ia_marketing**, la cuenta de **GORMARAN Marketing Agency**
(gormaran-marketing.com). Cada reel persigue dos cosas a la vez: **alcance** (que Instagram lo enseñe a
quien no te sigue) y **negocio**: que el espectador comente una palabra clave, **te siga** (el workflow lo
exige) y reciba un recurso que le acerca al **diagnóstico gratuito de 30 min** con Gabriela.

> Principio rector: **el reel fabrica la emoción; el DM entrega el valor; el diagnóstico cierra.**
> La viralidad se diseña (objetivo → emoción → gancho → retención → palabra clave), no se espera.

Antes de escribir nada, carga el contexto:
- [references/marca-gormaran.md](references/marca-gormaran.md) — servicios, pruebas reales, audiencia, pilares y voz.
- [references/n8n-palabras-clave.md](references/n8n-palabras-clave.md) — **las únicas palabras clave válidas** y cómo funciona el embudo de DMs.
- [references/referentes-nicho.md](references/referentes-nicho.md) — creadores de referencia y qué modelar (técnica, nunca palabras).
- [references/algoritmo-instagram.md](references/algoritmo-instagram.md) — señales que mueven el alcance de Reels.
- [references/ganchos.md](references/ganchos.md) — banco de ganchos por objetivo y por palabra clave.
- [references/formatos.md](references/formatos.md) — formatos probados con estructura y tiempos.
- [templates/guion-reel.md](templates/guion-reel.md) — plantilla exacta de entrega.
- [references/motion-graphics.md](references/motion-graphics.md) — estilo de subtítulos, qué gráfico usar según lo que se dice y formato del plan (solo para el modo vídeo).

**Dos modos:**
- **A · Idear y guionizar** (no hay vídeo): pasos 0–9.
- **B · Editar un vídeo adjunto** (el usuario sube un archivo de vídeo): ve directamente a la sección
  [Modo B](#modo-b--editar-un-vídeo-adjunto) y usa los pasos 1, 3, 4 y 6 para evaluar el contenido y elegir el CTA.

---

## Paso 0 — Recoge los datos (pregunta solo lo que falte)

| Dato | Por defecto si no lo dan |
|---|---|
| Tema / idea | Propón 5 ideas, una por pilar de [marca-gormaran.md](references/marca-gormaran.md), y deja elegir |
| Objetivo | Rota según el mix semanal (Paso 6) |
| Palabra clave | La del pilar del tema (GEO, RESERVAS o RADAR) |
| Reel de referencia | Ninguno → propón 3 formatos de [formatos.md](references/formatos.md) |
| Sector al que habla | El del caso real más parecido (hostelería, bodegas, automoción, paisajismo, servicios con cita) |
| Formato de grabación | Gabriela a cámara + pantalla grabada (ChatGPT/Gemini/Perplexity, WhatsApp, Google) |
| Nº de reels | 1 (si piden lote, 3–7 con ángulos y palabras clave repartidos) |

## Paso 1 — Sincroniza las palabras clave con n8n (siempre)

1. Si la herramienta de n8n está disponible, lee el workflow `6gOWd8mbWXO-bUTlfn0Vt` («GORMARAN · Alternativa ManyChat») y extrae las palabras del objeto `RECURSOS` del nodo «Interpretar evento». Esa lista es la verdad.
2. Si no hay acceso, usa las de [n8n-palabras-clave.md](references/n8n-palabras-clave.md): **RADAR**, **GEO**, **RESERVAS**.
3. **Prohibido inventar palabras.** Si el tema pide otro recurso, entrégalo como propuesta de cambio del workflow (ver el archivo de n8n) y usa mientras tanto la palabra existente más cercana.

## Paso 2 — Investiga el nicho (5 minutos)

El 80 % de los reels virales de IA hablan de **una herramienta concreta, un creador concreto o una mecánica
de formato concreta**. Las opiniones genéricas sobre "la IA en el marketing" no se mueven.

1. Busca qué se mueve **esta semana**: lanzamientos y cambios en ChatGPT, Gemini, Perplexity, Google (AI Overviews / AI Mode), Meta/WhatsApp Business, Instagram; noticias que afecten a pymes.
2. Tradúcelo a un pilar de GORMARAN: ¿afecta a que te encuentren (GEO), a cómo atiendes y reservas (RESERVAS) o es noticia para estar al día (RADAR)?
3. Cruza con [referentes-nicho.md](references/referentes-nicho.md) para elegir técnica.
4. Herramientas opcionales si están conectadas (nunca inventes datos):
   - **Instagram propio** (Meta, `ads_get_ig_media`): últimos reels para no repetir y detectar ganadores.
   - **Biblioteca de anuncios de Meta** (`ads_library_search`, país `ES`; "agencia marketing IA", "chatbot WhatsApp", "reservas WhatsApp", "posicionamiento ChatGPT"): ángulos que la competencia paga durante semanas = ángulos que convierten.
   - **Workflows de GORMARAN**: «Vigilancia SEO + GEO semanal» y «Producción de contenido semanal» detectan huecos de contenido; «Radar: Newsletter + Podcast» resume las noticias de la semana. Úsalos como fuente de temas si están disponibles.
   - **Higgsfield `virality_predictor`**: puntúa el guion/vídeo final antes de publicar.
5. Devuelve en 5 líneas: tendencia · por qué le importa a una pyme · ángulo GORMARAN · formato · palabra clave · fuente(s).

### Paso 2b — Desmontaje de un reel de referencia
Si hay URL, transcripción o capturas: **gancho** (texto + frase + por qué funciona) · **beats** con tiempos · **ritmo** · **técnica visual** · **2–3 movimientos reutilizables** · **remake GORMARAN** en una línea. Se modela la estructura; nunca el guion, la voz ni el caption de otro (Instagram penaliza el contenido no original).

## Paso 3 — Elige UN objetivo

| Objetivo | Emoción | Mecánica | Ejemplo GORMARAN |
|---|---|---|---|
| **GUARDAR** | alivio + miedo a olvidarlo | sistema numerado que se monta en pantalla | "3 cosas que mira ChatGPT antes de recomendar un negocio. Guárdalo." |
| **COMPARTIR** | asombro / indignación / estatus | "casi nadie sabe esto", resultado primero | "Le pregunté a ChatGPT por el mejor taller de Vitoria y se inventó uno. Mándaselo a tu mecánico." |
| **SEGUIR** | FOMO + aspiración | brecha "tú a mano vs. ellos automatizados", serie | "Día 2 dejando que un chatbot lleve las reservas de un restaurante." |
| **LEAD** | ganas + curiosidad terminal | recurso con nombre retenido tras palabra clave | "Comenta GEO y te digo qué nota te pone la IA de 0 a 100." |

- Por el follow-gate de n8n, **todo reel de LEAD suma seguidores**: es el objetivo con más retorno por reel.
- Un objetivo y un CTA por reel. Emoción de alta activación > consejo tranquilo. Señal de identidad: compartirlo debe hacer quedar bien a quien lo envía.

## Paso 4 — Ganchos (los primeros 1,5 s deciden todo)

Escribe **10 ganchos** con ángulos distintos de [ganchos.md](references/ganchos.md) y marca los 3 que testearías primero (Trial Reels), con una línea de por qué.

- **El frame 0 es el gancho:** algo ya en pantalla y en movimiento (una respuesta de ChatGPT escribiéndose, un WhatsApp entrando a las 3:12, una nota 23/100). Nada de logos, fundidos ni "Hola, soy Gabriela".
- **Funciona sin sonido:** texto en pantalla de 3–7 palabras.
- **Abre un hueco, no des un dato.** Números concretos > vaguedades.
- < 12 palabras habladas, tuteo, lenguaje de calle.
- Rota el ángulo cada publicación (contrario, resultado primero, prueba en directo, POV, numerado, error, caso local).

## Paso 5 — Guion (retención hasta el final)

Duración por defecto **25–45 s** (~70–120 palabras habladas):

| Tramo | Tiempo | Función |
|---|---|---|
| GANCHO | 0–3 s | Para el scroll + promete el premio |
| TENSIÓN | 3–8 s | Coste concreto ("cada reserva que no contestas a las 23:00 es una mesa vacía") |
| VALOR | 8–30 s | 3 beats con visual propio; re-enganche en ~4, ~9 y ~15 s ("pero lo grave es lo tercero…") |
| PREMIO | 30–38 s | Se paga lo prometido. **Nunca antes.** |
| CTA | últimos 3–5 s | "Comenta **[PALABRA]** y te lo mando por DM" + tarjeta final con la palabra grande |

- **Promete → retén → escala → paga.** Numera los beats para que se vea la meta. Lo mejor, al final. Promete, nunca mientas.
- **Cada frase lleva un visual** (pantalla real, móvil, cliente, gráfico). Nada estático.
- **Prueba social de verdad:** usa solo las cifras de [marca-gormaran.md](references/marca-gormaran.md). Ningún precio de GORMARAN.
- Lee el guion en voz alta y **recorta un 20 %**.

## Paso 6 — Capa comercial (embudo sincronizado)

```
Reel ──► comenta PALABRA ──► DM automático (n8n): "sígueme y escribe LISTO"
     ──► te sigue + LISTO ──► recibe el recurso ──► formulario/lead ──► diagnóstico gratuito 30 min
```

1. **CTA hablado y en pantalla:** "Comenta **GEO** y te mando tu auditoría por DM." (una sola palabra, en MAYÚSCULAS, sin variantes).
2. **Caption:** palabra clave en la **primera línea** + honestidad sobre el paso de seguir: "Te llega por DM; solo tienes que seguirme 🙌".
3. **Respuesta pública** (la hace Gabriela a mano, el workflow no la hace): corta y sin enlace — "¡Te lo he mandado por DM! 📩".
4. **Historias de apoyo** (mismo día): "Responde a esta historia con **GEO**" (llega como DM y el workflow la procesa igual).
5. **Etapa del embudo:** TOFU (alcance, RADAR) · MOFU (prueba/caso, GEO o RESERVAS) · BOFU (diagnóstico). Para BOFU, como no hay palabra DIAGNOSTICO en n8n, usa GEO o RESERVAS (sus entregas llevan al formulario) o "enlace en la bio → diagnóstico gratuito"; si se quiere una palabra propia, propón el cambio del workflow.

## Paso 7 — Mix semanal (5 reels)

| Pilar | Reels | Objetivo | Palabra |
|---|---|---|---|
| GEO: ¿te recomienda ChatGPT? | 2 | Compartir → Lead | GEO |
| WhatsApp que trabaja solo | 1 | Lead | RESERVAS |
| Noticia IA + marketing para tu negocio | 1 | Compartir / Seguir | RADAR |
| Caso real con números u opinión anti-humo | 1 | Lead (MOFU/BOFU) | GEO o RESERVAS |

Regla 4:1 — por cada reel de venta directa del diagnóstico, cuatro que aporten. Repite en serie lo que gane.

## Paso 8 — Entrega

Usa **exactamente** [templates/guion-reel.md](templates/guion-reel.md). En lotes: una ficha por reel + tabla resumen (título · pilar · objetivo · etapa · palabra clave · formato · día).

Checklist (si algo falla, corrige antes de entregar):
- [ ] Palabra clave **existe en el workflow de n8n** (RADAR / GEO / RESERVAS u otra leída del workflow).
- [ ] Un solo objetivo y un solo CTA.
- [ ] Gancho entendible sin sonido en < 1,5 s.
- [ ] Premio prometido y pagado al final.
- [ ] Cada línea con visual; nada estático.
- [ ] Solo cifras reales de GORMARAN; sin precios; permiso de clientes si salen.
- [ ] Estructura modelada, palabras propias.
- [ ] Suena a Gabriela.

## Modo B — Editar un vídeo adjunto

Claude no reproduce vídeo, así que lo "ve" por fotogramas y lo "escucha" por su transcripción con tiempos
por palabra. Requisitos: `ffmpeg` (con libass) y Python 3; para transcribir en local, `pip install faster-whisper`.

**B1. Localiza el archivo.** En Claude.ai los adjuntos están en `/mnt/user-data/uploads/`; en Claude Code,
usa la ruta que dé el usuario. Trabaja en una carpeta propia (p. ej. `trabajo_reel/`).

**B2. Analiza (ver + escuchar)** — los scripts están en la carpeta `scripts/` de esta skill:
```bash
python3 scripts/analizar_video.py VIDEO.mp4 --out trabajo_reel --cada 1
```
- Abre `trabajo_reel/hoja_contacto.jpg` (todos los fotogramas con su segundo) y los fotogramas sueltos que
  necesites de `trabajo_reel/fotogramas/`. Anota: dónde está la cara, qué se ve en pantalla, cambios de plano.
- Lee `trabajo_reel/transcripcion.txt`.
- Si no se puede transcribir en local (sin faster-whisper o sin red para descargar el modelo), transcribe
  `audio.wav` con la herramienta disponible (p. ej. ElevenLabs `creative_transcribe_audio`) o pide al usuario
  el `.srt` de CapCut/Edits, y repite con `--transcripcion fichero.srt|.json`.

**B3. Corrige la transcripción.** Revisa `transcripcion.json` y corrige nombres y términos (GORMARAN, Gabriela
Ormazabal, Vitoria-Gasteiz, ChatGPT, GEO, RESERVAS, RADAR, clientes…), sin tocar los tiempos. Los subtítulos
son lo primero que se lee: cero faltas.

**B4. Diagnóstico rápido del vídeo** (antes de editar, en 5 líneas): ¿el gancho para el scroll en 1,5 s?
¿hay premio al final? ¿el CTA usa una palabra de n8n? ¿qué sobra (silencios, repeticiones)? Si el gancho o el
CTA fallan, propón cómo arreglarlo con gráficos (título de gancho, tarjeta CTA) y sugiere recortes; recortar
o regrabar lo decide el usuario.

**B5. Plan de motion graphics.** Escribe `trabajo_reel/plan_mg.json` siguiendo
[motion-graphics.md](references/motion-graphics.md): cada gráfico nace de algo que **se dice** (cifra →
contador, enumeración → lista, concepto → palabra clave, "mira esto" → círculo + flecha + zoom, CTA → tarjeta
con RADAR/GEO/RESERVAS). Usa los fotogramas para no tapar la cara ni lo importante.

**B6. Previsualiza y revisa:**
```bash
python3 scripts/render_reel.py VIDEO.mp4 --palabras trabajo_reel/transcripcion.json \
  --plan trabajo_reel/plan_mg.json --out trabajo_reel/reel_final.mp4 --preview 0.8,3.5,6.2,9.0
```
Abre los PNG de `trabajo_reel/reel_final_preview/`, corrige el plan y repite hasta que esté limpio.

**B7. Render final:** el mismo comando sin `--preview`. Subtítulos por defecto: **Bebas Neue, tamaño 12,
palabra por palabra** (`--modo una` para una palabra cada vez; `--tamano N` solo si el usuario lo pide).

**B8. Entrega:** el `reel_final.mp4`, el `.ass` (editable) y, con la plantilla, el **caption** con la palabra
clave en la primera línea, la respuesta pública y la historia de apoyo (Paso 6).

## Paso 9 — Aprende (bucle de mejora)

A las 48–72 h:
1. **Instagram:** retención 3 s, % visto, envíos, guardados, comentarios.
2. **n8n:** lee la tabla `ig_recursos_instagram` y calcula peticiones, entregados y tasa follow-gate por palabra clave y por reel (ver [n8n-palabras-clave.md](references/n8n-palabras-clave.md)).

| Síntoma | Causa probable | Arreglo |
|---|---|---|
| < 60 % de retención a 3 s | Gancho lento o débil | Frame 0 con movimiento; claim en 1,2–1,6 s |
| Caída a mitad | Bucle cerrado pronto / beat sin visual | Premio al final, re-enganche |
| Muchas vistas, pocos envíos | Sin identidad/emoción | Ángulo "casi nadie sabe" o indignación local |
| Muchas vistas, pocos comentarios con palabra | CTA débil o recurso poco deseable | Palabra en pantalla grande + promesa concreta ("tu nota de 0 a 100") |
| Muchas peticiones, pocos `entregado` | La gente no sigue o no escribe LISTO | Avisar en el reel/caption: "sígueme y escribe LISTO" |
| Muchos entregados, pocos diagnósticos | Recurso desconectado del servicio | Reels MOFU con caso real que lleven al diagnóstico |

Guarda ganchos y formatos ganadores en `references/ganchos.md` → "Ganadores propios".

---

**No negociables:** subtítulos sin faltas y sincronizados palabra a palabra; honestidad (datos reales, todo "te lo mando" se manda), sincronía con n8n (ninguna palabra inventada), originalidad (técnica sí, palabras ajenas no), identidad + emoción.

*Metodología adaptada del enfoque "objetivo → emoción → gancho → embudo" de los skills abiertos de Ootto (MIT, github.com/Ootto-AI/claude-content-skills) y del artículo "Make viral Instagram Reels with Claude", ajustada al español, a GORMARAN Marketing Agency y a su embudo de n8n.*
