# Sincronización con n8n · «GORMARAN · Alternativa ManyChat»

Los CTA de los reels **tienen que coincidir** con lo que el workflow de n8n sabe leer. Si un reel pide una
palabra que el workflow no reconoce, el comentario se ignora y el lead se pierde.

## Datos del workflow
| Campo | Valor |
|---|---|
| Nombre | `GORMARAN · Alternativa ManyChat` |
| ID | `6gOWd8mbWXO-bUTlfn0Vt` (instancia `gormaran.app.n8n.cloud`) |
| Disparador | Webhook de Instagram (`/webhook/instagram-webhook`): **comentarios** en publicaciones/reels y **DMs** (las respuestas a historias llegan como DM) |
| Estado de cada usuario | Data table `ig_recursos_instagram` (ID `MmGJr9D4sEfsDxPn`): `ig_id`, `recurso`, `estado` (`pendiente` / `entregado`), `origen` (`comentario` / `dm`), `texto`, `actualizado` |
| Dónde viven las palabras | Nodo **«Interpretar evento»** → objeto `RECURSOS` · Mensajes de entrega en **«Preparar comprobación»** → `ENTREGA` · Lista que se ofrece si escriben LISTO sin palabra: nodo **«Preguntar qué recurso»** |

## Palabras clave activas (a 5-oct-2026)
| Recurso | Palabras que lo activan | Se entrega |
|---|---|---|
| `radar` | **RADAR** | Suscripción a la newsletter Radar GORMARAN + podcast en Spotify |
| `geo` | **GEO**, AUDITORIA | Formulario de la auditoría GEO gratuita (nota 0–100 + 3 acciones) |
| `reservas` | **RESERVAS**, RESERVA | Demo de reservas automáticas por WhatsApp (formulario de la web con UTM `reels_reservas`) |
| *(confirmación)* | LISTO, LISTA, HECHO, YA TE SIGO, TE SIGO, YA ESTA, DONE | Dispara la comprobación de seguimiento |

En los reels usa siempre la forma principal en MAYÚSCULAS: **RADAR**, **GEO**, **RESERVAS**.

## Cómo funciona el embudo (lo que vive el usuario)
1. Comenta **GEO** en el reel (o lo escribe por DM, o responde a una historia con GEO).
2. Recibe un **DM privado**: "Te envío tu auditoría GEO gratuita encantada. Solo un paso: sígueme en Instagram y respóndeme por aquí con la palabra LISTO."
3. Escribe **LISTO** → el workflow comprueba en la API de Instagram si sigue a la cuenta.
4. Si sigue → recibe el enlace y queda `entregado`. Si no → se le pide que siga y vuelva a escribir LISTO.

Consecuencias para el guion:
- **Cada reel de lead también es un reel de "seguir"** (hay follow-gate). Dilo con honestidad en el caption: "te llega por DM; solo tienes que seguirme".
- El workflow **no responde en público** al comentario. Gabriela puede contestar a mano (sin enlace) para sumar interacción: "¡Te lo he mandado por DM! 📩".
- La detección es por **palabra completa**, sin distinguir mayúsculas ni tildes: "geo", "GEO!", "#geo", "Auditoría" funcionan; "geolocalización" **no**. No pidas variantes ("comenta GEO2026", "GEO-VITORIA").
- **Una palabra por reel.** Si un usuario pide dos recursos seguidos, su fila guarda solo el último.
- Las historias son un segundo canal gratuito: "Responde a esta historia con RADAR".

## Regla de sincronización para la skill
1. **Antes de escribir el CTA**, si la herramienta de n8n está disponible, lee el workflow (`get_workflow_details` con ID `6gOWd8mbWXO-bUTlfn0Vt`) y extrae las claves y `palabras` del objeto `RECURSOS` del nodo «Interpretar evento». Esa lista manda sobre esta tabla.
2. Si no hay acceso a n8n, usa solo las palabras de la tabla de arriba.
3. **Nunca inventes una palabra nueva en un reel.** Si un tema necesita un recurso distinto (p. ej. DIAGNOSTICO, PROMPTS), entrégalo como **propuesta** con los tres cambios necesarios en el workflow y deja claro que hay que añadirlo **antes** de publicar:
   - en «Interpretar evento» → `RECURSOS.<id> = { palabras: [...], nombre: '...' }`
   - en «Preparar comprobación» → `NOMBRES.<id>` y `ENTREGA.<id>` con el mensaje y enlace
   - en «Preguntar qué recurso» → añadir la palabra a la lista que se ofrece
   No modifiques el workflow por tu cuenta: el workflow está en producción y solo se cambia si Gabriela lo pide.

## Medir qué reel convierte (bucle de mejora)
Si hay acceso a n8n, lee `ig_recursos_instagram` (proyecto `JTak9jzBnnTuI4Hr`) y calcula por recurso y por semana:
- **Peticiones** = filas con ese `recurso` (cada fila es un usuario; se sobrescribe si pide otro recurso).
- **Entregados** = `estado = entregado` → personas que **siguieron** y recibieron el enlace.
- **Tasa follow-gate** = entregados / peticiones. Si es < 50 %, el DM o el reel no dejan claro que hay que seguir y escribir LISTO.
- `origen` = `comentario` vs `dm` → qué CTA funciona mejor (comentar en el reel o escribir por DM/historia).
Cruza las fechas de `createdAt` con la fecha de publicación de cada reel para atribuir leads a reels.
