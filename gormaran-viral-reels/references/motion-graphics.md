# Subtítulos y motion graphics · estilo GORMARAN

Lo que hace `scripts/render_reel.py` y cómo escribir el **plan de motion graphics** a partir de lo que se
dice y se ve en el vídeo.

## Estilo fijo de los subtítulos
| Propiedad | Valor |
|---|---|
| Tipografía | **Bebas Neue** (incluida en `assets/fonts/`, licencia OFL) |
| Tamaño | **12** |
| Animación | **Palabra por palabra**: cada palabra aparece en el momento exacto en que se dice, con un "pop" vertical de 160 ms |
| Modo por defecto | `acumulado`: frase de hasta 3 palabras que se va revelando; la palabra que suena va en coral y las dichas en blanco. Alternativa: `una` (una sola palabra en pantalla cada vez) |
| Colores | Texto `#FFFFFF` · palabra activa y énfasis `#FF5757` (coral GORMARAN) · contorno `#26212E` |
| Posición | 70 % de la altura (fuera del 15 % inferior que tapa la interfaz de Instagram) |
| Énfasis automático | Números, %, € y las palabras de `enfasis` del plan se quedan en coral |

**Unidades.** Todo se mide sobre un lienzo de **360 de ancho** (puntos de pantalla de móvil; 1 punto = 3 px
en un vídeo de 1080 px), así que el tamaño 12 se ve igual en 720p, 1080p o 4K. El tamaño se cambia con
`--tamano N` o en `estilo.json` (`{"tamano": 16}`), sin tocar el código.

## Del guion al gráfico: qué poner según lo que se dice
Lee la transcripción y los fotogramas, y aplica esta tabla. Regla de oro: **un gráfico refuerza una idea,
no decora**. Máximo un elemento grande en pantalla a la vez y nada encima de la cara.

| Si en el vídeo… | Usa | Ejemplo |
|---|---|---|
| Primeros 0–3 s (gancho) | `titulo` arriba + `zoom` suave (1,10–1,15) | "¿SALES EN CHATGPT?" |
| Se dice una **cifra** o porcentaje | `contador` (cuenta hasta el número) + `etiqueta` | +40 % · TRÁFICO ORGÁNICO |
| Se **enumeran** pasos o motivos | `lista` con un `tiempo` por ítem, cuando se nombra cada uno | 1 RESEÑAS · 2 DATOS · 3 CONTENIDO |
| Se nombra un **concepto o herramienta clave** | `palabra_clave` (grande, 0,8–1,5 s) | "GEO", "WHATSAPP", "CHATGPT" |
| Se **señala algo en pantalla** (captura, móvil, web) | `circulo` sobre la zona + `flecha` apuntándola + `zoom` | la respuesta de ChatGPT |
| Gabriela aparece por primera vez o habla con autoridad | `rotulo` (nombre + cargo) | GABRIELA ORMAZABAL · GORMARAN MARKETING AGENCY |
| **Cambio de tema** o de bloque | `flash` (0,15–0,2 s) | entre problema y solución |
| Frase contundente / remate | `zoom` de golpe (factor 1,2, rampa 0,08) | "Y eso te cuesta clientes." |
| Llamada a la acción final | `cta` con la palabra de n8n (RADAR / GEO / RESERVAS) | COMENTA · GEO · Y TE LO MANDO POR DM |
| Todo el reel (opcional) | `barra_progreso` arriba | retiene en reels > 30 s |

Ritmo recomendado: un estímulo visual nuevo cada **2–4 s** (palabra clave, zoom, contador, flash…), sin
amontonar. Los subtítulos ya cuentan como movimiento continuo.

## Formato del plan (`plan_mg.json`)
Tiempos en segundos del vídeo. Posiciones `x`/`y` de 0 a 1 (fracción del ancho/alto) o `posicion`:
`arriba` (20 %), `centro` (45 %), `abajo` (62 %).

```json
{
  "enfasis": ["chatgpt", "vitoria", "geo"],
  "elementos": [
    {"tipo": "titulo", "texto": "¿Sales en ChatGPT?", "inicio": 0.3, "fin": 2.5, "posicion": "arriba"},
    {"tipo": "zoom", "inicio": 0.3, "fin": 1.6, "factor": 1.12, "rampa": 0.25},
    {"tipo": "rotulo", "titulo": "Gabriela Ormazabal", "subtitulo": "GORMARAN Marketing Agency", "inicio": 2.7, "fin": 5.0},
    {"tipo": "circulo", "x": 0.5, "y": 0.35, "radio": 0.14, "inicio": 3.2, "fin": 5.0},
    {"tipo": "flecha", "x": 0.75, "y": 0.28, "direccion": "izquierda", "inicio": 3.2, "fin": 5.0},
    {"tipo": "flash", "inicio": 5.45, "duracion": 0.18},
    {"tipo": "contador", "desde": 0, "hasta": 40, "prefijo": "+", "sufijo": " %", "etiqueta": "Tráfico orgánico",
     "inicio": 5.5, "fin": 8.4, "posicion": "arriba", "duracion": 0.9},
    {"tipo": "lista", "items": ["Reseñas", "Datos coherentes", "Contenido citado"], "tiempos": [6.0, 6.6, 7.2],
     "fin": 8.4, "y": 0.40},
    {"tipo": "palabra_clave", "texto": "GEO", "inicio": 8.0, "fin": 9.0, "posicion": "centro"},
    {"tipo": "cta", "palabra": "GEO", "texto": "Comenta", "subtexto": "y te mando tu auditoría por DM",
     "inicio": 8.7, "fin": 12.0},
    {"tipo": "barra_progreso"}
  ]
}
```

Campos opcionales comunes: `tamano` (en puntos del lienzo de 360), `color` (hex). Por defecto: título 22,
palabra clave 44, contador 52, lista 18, rótulo 16, CTA 50 (palabra).

### Catálogo
| Tipo | Campos obligatorios | Animación |
|---|---|---|
| `titulo` | texto, inicio, fin | Caja coral redondeada que baja y aparece |
| `palabra_clave` | texto, inicio, fin | Pop de escala 30 → 112 → 100 % |
| `contador` | hasta, inicio, fin | Cuenta con ease-out y rebote al llegar |
| `lista` | items, tiempos, fin | Cada ítem entra desde la izquierda con su número en círculo coral |
| `rotulo` | titulo, inicio, fin | Tercio inferior oscuro con barra coral, entra desde la izquierda |
| `flecha` | x, y (punta), inicio, fin | Rebota hacia la punta; `direccion`: abajo / arriba / izquierda / derecha |
| `circulo` | x, y (centro), inicio, fin | Anillo coral que crece desde 0 |
| `flash` | inicio | Destello blanco que se desvanece |
| `zoom` | inicio, fin | Acercamiento suave del vídeo (`factor`, `rampa`); va por debajo de los gráficos |
| `cta` | palabra, inicio, fin | Tarjeta oscura con la palabra en coral que late; avisa si la palabra no está en n8n |
| `barra_progreso` | — | Barra coral arriba que se llena durante todo el vídeo |

## Revisión visual obligatoria
1. Antes del render final, genera previews en los momentos clave:
   `--preview 0.8,3.5,6.2,9.0` → PNGs en `<salida>_preview/`. Ábrelos y comprueba que nada tapa la cara, el texto
   de la pantalla grabada ni los subtítulos, y que los tiempos cuadran con lo que se dice.
2. Ajusta el plan y repite hasta que esté limpio. Solo entonces renderiza el vídeo.
3. El `.ass` generado junto al vídeo se puede retocar a mano en Aegisub si hace falta un ajuste fino.
