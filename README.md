# Skills de GORMARAN

Skills de Claude para GORMARAN Marketing Agency (gormaran-marketing.com).

## gormaran-viral-reels

Genera reels virales y con intención comercial para **@gormaran_ia_marketing** (GORMARAN Marketing Agency,
gormaran-marketing.com): investiga el nicho, elige objetivo (guardar / compartir / seguir / lead), escribe
10 ganchos, guion con texto en pantalla y planos, caption y un CTA de palabra clave **sincronizado con el
workflow de n8n «GORMARAN · Alternativa ManyChat»** (RADAR, GEO, RESERVAS → seguir + LISTO → recurso por DM
→ diagnóstico gratuito).

También **edita vídeos adjuntos**: **corta los silencios y acelera ×1,3**, los analiza (fotogramas + transcripción con tiempos), propone mejoras y
renderiza el reel con subtítulos **Bebas Neue tamaño 12 animados palabra por palabra** y **motion graphics**
(títulos, contadores, listas, rótulos, flechas, círculos, zooms, flashes y tarjeta CTA) según lo que se dice,
con los colores de GORMARAN (coral `#FF5757`, morado oscuro `#26212E`).

```
gormaran-viral-reels/
├── SKILL.md                         # flujo completo (pasos 0–9)
├── references/
│   ├── marca-gormaran.md            # servicios, casos reales, audiencia, pilares, voz
│   ├── n8n-palabras-clave.md        # palabras clave válidas, embudo de DMs y medición en n8n
│   ├── referentes-nicho.md          # creadores de referencia y qué modelar
│   ├── algoritmo-instagram.md       # señales de alcance 2026
│   ├── ganchos.md                   # banco de ganchos + "Ganadores propios"
│   ├── formatos.md                  # 10 formatos con estructura y tiempos
│   └── motion-graphics.md           # estilo de subtítulos, catálogo de gráficos y formato del plan
├── scripts/
│   ├── recortar_video.py            # corta silencios + velocidad ×1,3 (voz sin pitar) + recalcula tiempos
│   ├── analizar_video.py            # fotogramas + hoja de contacto + audio + transcripción por palabra
│   └── render_reel.py               # subtítulos palabra a palabra + motion graphics + zoom → mp4
├── assets/fonts/                    # Bebas Neue (licencia SIL OFL)
└── templates/
    └── guion-reel.md                # plantilla de entrega
```

## Cómo se usa

Hay dos formas. **Para editar vídeos, la recomendada es VS Code (Claude Code)**: trabaja con los archivos de
tu ordenador, sin límite de subida, y deja el vídeo final en tu carpeta.

### Opción A · VS Code con Claude Code (recomendada para vídeos)

**Una sola vez:**
1. Instala la extensión **Claude Code** en VS Code e inicia sesión.
2. Instala las herramientas de vídeo:
   - Mac: `brew install ffmpeg` y `pip3 install faster-whisper`
   - Windows: `winget install Gyan.FFmpeg`, instala Python desde python.org y `pip install faster-whisper`
3. Instala la skill para tu usuario (queda disponible en cualquier carpeta):
   ```bash
   git clone -b claude/viral-reels-skill-ti8bd8 https://github.com/gormaran/skills.git gormaran-skills
   mkdir -p ~/.claude/skills && cp -r gormaran-skills/gormaran-viral-reels ~/.claude/skills/
   ```
   (Cuando la rama se fusione en `main`, basta con `git clone https://github.com/gormaran/skills.git`.)
4. Opcional: conecta tu servidor MCP de **n8n** en Claude Code para que la skill lea las palabras clave del
   workflow en directo y mida los leads. Sin él usa RADAR, GEO y RESERVAS.

**Cada vez que quieras editar un reel:**
1. Crea una carpeta (p. ej. `Reels/`), mete dentro el vídeo en bruto y ábrela en VS Code.
2. Abre el panel de Claude Code y escribe, por ejemplo:
   ```
   /gormaran-viral-reels edita @brutos/video_geo.mp4 con subtítulos y motion graphics, CTA GEO
   ```
   (con `@` eliges el archivo; también vale escribir la ruta).
3. Claude te pedirá permiso para ejecutar los scripts. Verás: los silencios cortados y la duración final,
   el diagnóstico del vídeo, el plan de gráficos y unas capturas de prueba para revisar.
4. Pide cambios en lenguaje normal ("el contador más arriba", "quita la flecha", "subtítulos más grandes").
5. El resultado queda en `trabajo_reel/reel_final.mp4` dentro de tu carpeta, listo para subir a Instagram,
   junto con el caption.

### Opción B · Claude.ai (web, escritorio o móvil)

1. Comprime la carpeta `gormaran-viral-reels` en un `.zip`.
2. En Claude.ai: **Ajustes → Capacidades**, activa la ejecución de código y creación de archivos y sube el `.zip`
   en **Skills**.
3. En un chat nuevo, **adjunta el vídeo** y escribe: "Edita este vídeo con la skill gormaran-viral-reels, CTA GEO".
4. Descarga el vídeo final que te devuelve.

Limitaciones: hay un límite de tamaño de archivo al adjuntar, el entorno de Claude.ai puede no tener red para
descargar el modelo de transcripción (en ese caso adjunta también el `.srt` de CapCut/Edits) y no tendrá
acceso a tu n8n. Para guiones e ideas (sin vídeo) funciona igual de bien.

### ¿Y esta sesión de Claude Code en la web?
Sirve para mantener y mejorar la skill (este repositorio), no para editar tus vídeos: aquí no puedes
adjuntar vídeos cómodamente y el vídeo final se quedaría en un servidor temporal.

### Uso
```
/gormaran-viral-reels reel sobre si ChatGPT recomienda restaurantes de Vitoria, objetivo lead, GEO
/gormaran-viral-reels 5 reels para esta semana
/gormaran-viral-reels analiza este reel y haz mi versión: https://www.instagram.com/reel/...
/gormaran-viral-reels edita este vídeo con subtítulos y motion graphics, CTA GEO   (+ vídeo adjunto)
```
O simplemente: "Hazme un reel viral para captar restaurantes con la demo de RESERVAS".

### Sincronización con n8n
Las únicas palabras clave válidas son las que lee el workflow `6gOWd8mbWXO-bUTlfn0Vt`: hoy **RADAR**, **GEO**
y **RESERVAS**. Si la sesión tiene acceso a n8n, la skill lee el workflow antes de escribir cada CTA y mide
los resultados en la tabla `ig_recursos_instagram`. Para añadir una palabra nueva, primero se añade al workflow
(ver `references/n8n-palabras-clave.md`) y luego se usa en los reels.
