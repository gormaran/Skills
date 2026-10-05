# Skills de GORMARAN

Skills de Claude para GORMARAN Marketing Agency (gormaran-marketing.com).

## gormaran-viral-reels

Genera reels virales y con intención comercial para **@gormaran_ia_marketing** (GORMARAN Marketing Agency,
gormaran-marketing.com): investiga el nicho, elige objetivo (guardar / compartir / seguir / lead), escribe
10 ganchos, guion con texto en pantalla y planos, caption y un CTA de palabra clave **sincronizado con el
workflow de n8n «GORMARAN · Alternativa ManyChat»** (RADAR, GEO, RESERVAS → seguir + LISTO → recurso por DM
→ diagnóstico gratuito).

```
gormaran-viral-reels/
├── SKILL.md                         # flujo completo (pasos 0–9)
├── references/
│   ├── marca-gormaran.md            # servicios, casos reales, audiencia, pilares, voz
│   ├── n8n-palabras-clave.md        # palabras clave válidas, embudo de DMs y medición en n8n
│   ├── referentes-nicho.md          # creadores de referencia y qué modelar
│   ├── algoritmo-instagram.md       # señales de alcance 2026
│   ├── ganchos.md                   # banco de ganchos + "Ganadores propios"
│   └── formatos.md                  # 10 formatos con estructura y tiempos
└── templates/
    └── guion-reel.md                # plantilla de entrega
```

### Instalación

**Claude Code:** copia la carpeta a `~/.claude/skills/` (o a `.claude/skills/` del proyecto):
```bash
cp -r gormaran-viral-reels ~/.claude/skills/
```

**Claude.ai / app:** comprime la carpeta `gormaran-viral-reels` en un .zip y súbela en
*Ajustes → Capacidades → Skills*.

### Uso
```
/gormaran-viral-reels reel sobre si ChatGPT recomienda restaurantes de Vitoria, objetivo lead, GEO
/gormaran-viral-reels 5 reels para esta semana
/gormaran-viral-reels analiza este reel y haz mi versión: https://www.instagram.com/reel/...
```
O simplemente: "Hazme un reel viral para captar restaurantes con la demo de RESERVAS".

### Sincronización con n8n
Las únicas palabras clave válidas son las que lee el workflow `6gOWd8mbWXO-bUTlfn0Vt`: hoy **RADAR**, **GEO**
y **RESERVAS**. Si la sesión tiene acceso a n8n, la skill lee el workflow antes de escribir cada CTA y mide
los resultados en la tabla `ig_recursos_instagram`. Para añadir una palabra nueva, primero se añade al workflow
(ver `references/n8n-palabras-clave.md`) y luego se usa en los reels.
