#!/usr/bin/env python3
"""Quema en el vídeo subtítulos palabra por palabra (Bebas Neue) y motion graphics.

Entradas:
  VIDEO                 vídeo original
  --palabras  JSON      transcripcion.json de analizar_video.py (corregida por Claude)
  --plan      JSON      plan de motion graphics (ver references/motion-graphics.md)
  --estilo    JSON      opcional; sobrescribe ESTILO_POR_DEFECTO

Salidas:
  --out salida.mp4      vídeo final (H.264 + audio original)
  --preview 1.2,4,9.5   en lugar del vídeo, PNGs de esos segundos en <out>_preview/ para revisar
  Siempre deja junto a la salida el .ass generado (editable en Aegisub).

Unidades: tamaños y posiciones se expresan sobre un lienzo de 360 de ancho (puntos de pantalla de
móvil; 1 punto = 3 px en un vídeo de 1080 px). Así "tamaño 12" significa lo mismo en cualquier
resolución. Las posiciones x/y del plan van de 0 a 1 (fracción del ancho/alto).
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FUENTES = os.path.abspath(os.path.join(AQUI, "..", "assets", "fonts"))

ESTILO_POR_DEFECTO = {
    "fuente": "Bebas Neue",
    "tamano": 12,                 # tamaño de los subtítulos (lienzo de 360 de ancho)
    "color_texto": "#FFFFFF",
    "color_activo": "#FF5757",    # coral GORMARAN: palabra que se está diciendo
    "color_enfasis": "#FF5757",   # palabras clave/números se quedan en coral
    "color_oscuro": "#26212E",    # morado oscuro GORMARAN: contornos y tarjetas
    "color_claro": "#FFFFFF",
    "contorno": 1.0,              # grosor del contorno de los subtítulos
    "sombra": 0.6,
    "posicion_y": 0.70,           # altura de los subtítulos (0 arriba, 1 abajo); fuera del 15 % inferior
    "modo": "acumulado",          # "acumulado": la frase se va revelando palabra a palabra · "una": una palabra cada vez
    "max_palabras": 3,
    "max_caracteres": 18,
    "pausa_corte": 0.45,          # una pausa mayor que esta abre frase nueva
    "mayusculas": True,
    "animacion_ms": 160,          # duración del "pop" de cada palabra
    "barra_progreso": False,
}

PALABRAS_VALIDAS_CTA = ["RADAR", "GEO", "RESERVAS"]  # sincronizar con n8n (references/n8n-palabras-clave.md)


# ───────────────────────── utilidades ASS ─────────────────────────

def c(hex_color):
    h = hex_color.lstrip("#")
    return f"&H{h[4:6]}{h[2:4]}{h[0:2]}&".upper()


def ts(t):
    t = max(0.0, t)
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def esc(texto):
    return texto.replace("\\", "\\\\").replace("{", "(").replace("}", ")").replace("\n", "\\N")


def dlg(capa, a, z, texto, estilo="MG"):
    return f"Dialogue: {capa},{ts(a)},{ts(z)},{estilo},,0,0,0,,{texto}"


def rect(w, h, r=0):
    """Rectángulo (opcionalmente redondeado) como dibujo ASS con origen en la esquina."""
    if r <= 0:
        return f"m 0 0 l {w:.1f} 0 {w:.1f} {h:.1f} 0 {h:.1f}"
    k = r * 0.5523
    return (
        f"m {r:.1f} 0 l {w - r:.1f} 0 b {w - r + k:.1f} 0 {w:.1f} {r - k:.1f} {w:.1f} {r:.1f} "
        f"l {w:.1f} {h - r:.1f} b {w:.1f} {h - r + k:.1f} {w - r + k:.1f} {h:.1f} {w - r:.1f} {h:.1f} "
        f"l {r:.1f} {h:.1f} b {r - k:.1f} {h:.1f} 0 {h - r + k:.1f} 0 {h - r:.1f} "
        f"l 0 {r:.1f} b 0 {r - k:.1f} {r - k:.1f} 0 {r:.1f} 0"
    )


def circulo(rad):
    k = rad * 0.5523
    d = 2 * rad
    return (
        f"m {rad:.1f} 0 b {rad + k:.1f} 0 {d:.1f} {rad - k:.1f} {d:.1f} {rad:.1f} "
        f"b {d:.1f} {rad + k:.1f} {rad + k:.1f} {d:.1f} {rad:.1f} {d:.1f} "
        f"b {rad - k:.1f} {d:.1f} 0 {rad + k:.1f} 0 {rad:.1f} "
        f"b 0 {rad - k:.1f} {rad - k:.1f} 0 {rad:.1f} 0"
    )


def ancho_texto(texto, tam):
    """Estimación del ancho de Bebas Neue (fuente condensada ≈ 0.42 em por carácter)."""
    return max(1, len(texto)) * tam * 0.42


# ───────────────────────── subtítulos palabra a palabra ─────────────────────────

def limpiar(p, mayus):
    t = p.strip()
    return t.upper() if mayus else t


def unir_signos(palabras):
    """Pega a la palabra anterior los tokens sueltos como "%", "€", "?" para que no salgan solos."""
    out = []
    for p in palabras:
        if out and re.fullmatch(r"[%€$?!.,:;…»)\]]+", p["texto"]):
            out[-1] = dict(out[-1], texto=out[-1]["texto"] + ("" if p["texto"][0] in ".,:;…?!»)]" else " ") + p["texto"],
                           fin=p["fin"])
        else:
            out.append(p)
    return out


def es_enfasis(texto, enfasis):
    base = re.sub(r"[^\wñáéíóúü%€+]", "", texto.lower())
    if re.search(r"\d", base) or "%" in base or "€" in base:
        return True
    return base in enfasis


def agrupar(palabras, e):
    grupos, actual = [], []
    for i, p in enumerate(palabras):
        if actual:
            prev = actual[-1]
            chars = sum(len(x["texto"]) + 1 for x in actual) + len(p["texto"])
            corte = (
                len(actual) >= e["max_palabras"]
                or chars > e["max_caracteres"]
                or p["inicio"] - prev["fin"] > e["pausa_corte"]
                or re.search(r"[.!?…:;,]$", prev["texto"])
            )
            if corte:
                grupos.append(actual)
                actual = []
        actual.append(p)
    if actual:
        grupos.append(actual)
    return grupos


def subtitulos(palabras, e, enfasis, W, H, duracion):
    lineas = []
    if not palabras:
        return lineas
    palabras = unir_signos([dict(p, texto=limpiar(p["texto"], e["mayusculas"])) for p in palabras if p["texto"].strip()])
    x, y = W / 2, H * e["posicion_y"]
    pos = f"\\an5\\pos({x:.1f},{y:.1f})"
    ms = int(e["animacion_ms"])
    pop = f"\\fscy55\\alpha&H60&\\t(0,{ms // 2},\\fscy118\\alpha&H00&)\\t({ms // 2},{ms},\\fscy100)"
    blanco, activo, enf = c(e["color_texto"]), c(e["color_activo"]), c(e["color_enfasis"])

    if e["modo"] == "una":
        for i, p in enumerate(palabras):
            fin = palabras[i + 1]["inicio"] if i + 1 < len(palabras) else p["fin"] + 0.3
            fin = min(fin, p["fin"] + 0.6)
            col = enf if es_enfasis(p["texto"], enfasis) else blanco
            pop_una = f"\\fscx70\\fscy70\\t(0,{ms // 2},\\fscx112\\fscy112)\\t({ms // 2},{ms},\\fscx100\\fscy100)"
            lineas.append(dlg(5, p["inicio"], max(fin, p["inicio"] + 0.12),
                              f"{{{pos}\\c{col}{pop_una}}}{esc(p['texto'])}", "Sub"))
        return lineas

    grupos = agrupar(palabras, e)
    for gi, g in enumerate(grupos):
        siguiente = grupos[gi + 1][0]["inicio"] if gi + 1 < len(grupos) else duracion
        fin_grupo = min(siguiente, g[-1]["fin"] + 0.35)
        for i, p in enumerate(g):
            a = p["inicio"]
            z = g[i + 1]["inicio"] if i + 1 < len(g) else fin_grupo
            if z - a < 0.04:
                continue
            trozos = []
            for j, q in enumerate(g):
                t = esc(q["texto"])
                if j < i:
                    col = enf if es_enfasis(q["texto"], enfasis) else blanco
                    trozos.append(f"{{\\alpha&H00&\\fscy100\\c{col}}}{t}")
                elif j == i:
                    trozos.append(f"{{\\c{activo}{pop}}}{t}")
                else:
                    trozos.append(f"{{\\alpha&HFF&\\fscy100}}{t}")
            lineas.append(dlg(5, a, z, f"{{{pos}}}" + " ".join(trozos), "Sub"))
    return lineas


# ───────────────────────── motion graphics ─────────────────────────

POSICIONES = {"arriba": 0.20, "centro": 0.45, "abajo": 0.62}


def py(el, H, defecto="centro"):
    if "y" in el:
        return float(el["y"]) * H
    return POSICIONES.get(el.get("posicion", defecto), POSICIONES[defecto]) * H


def mg_titulo(el, e, W, H):
    a, z = el["inicio"], el["fin"]
    tam = el.get("tamano", 22)
    texto = esc(el["texto"].upper())
    y = py(el, H, "arriba")
    w = ancho_texto(el["texto"], tam) + 20
    h = tam * 1.25
    fondo = c(el.get("color", e["color_activo"]))
    move = f"\\move({W / 2:.1f},{y - 12:.1f},{W / 2:.1f},{y:.1f},0,180)"
    return [
        dlg(10, a, z, f"{{\\an5{move}\\p1\\bord0\\shad0\\c{fondo}\\fad(120,150)}}{rect(w, h, 6)}"),
        dlg(11, a, z, f"{{\\an5{move}\\fs{tam}\\c{c(e['color_claro'])}\\bord0\\shad0\\fad(120,150)}}{texto}"),
    ]


def mg_palabra_clave(el, e, W, H):
    a, z = el["inicio"], el["fin"]
    tam = el.get("tamano", 44)
    x = float(el.get("x", 0.5)) * W
    y = py(el, H, "centro")
    col = c(el.get("color", e["color_activo"]))
    anim = "\\fscx30\\fscy30\\t(0,140,\\fscx112\\fscy112)\\t(140,240,\\fscx100\\fscy100)"
    return [dlg(12, a, z, f"{{\\an5\\pos({x:.1f},{y:.1f})\\fs{tam}\\c{col}\\3c{c(e['color_oscuro'])}"
                          f"\\bord2.2\\shad1{anim}\\fad(0,150)}}{esc(el['texto'].upper())}")]


def mg_contador(el, e, W, H):
    a, z = el["inicio"], el["fin"]
    desde, hasta = float(el.get("desde", 0)), float(el["hasta"])
    dur = float(el.get("duracion", 0.9))
    dec = int(el.get("decimales", 0))
    pre, suf = el.get("prefijo", ""), el.get("sufijo", "")
    tam = el.get("tamano", 52)
    x, y = float(el.get("x", 0.5)) * W, py(el, H, "centro")
    estilo = (f"\\an5\\pos({x:.1f},{y:.1f})\\fs{tam}\\c{c(el.get('color', e['color_activo']))}"
              f"\\3c{c(e['color_oscuro'])}\\bord2.2\\shad1")
    lineas = []
    pasos = max(2, int(dur * 25))
    for k in range(pasos):
        t0 = a + dur * k / pasos
        t1 = a + dur * (k + 1) / pasos
        f = 1 - (1 - (k + 1) / pasos) ** 3  # ease-out
        v = desde + (hasta - desde) * f
        num = f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
        lineas.append(dlg(12, t0, min(t1, z), f"{{{estilo}}}{esc(pre + num + suf)}"))
    final = f"{hasta:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    lineas.append(dlg(12, a + dur, z, f"{{{estilo}\\t(0,120,\\fscx110\\fscy110)\\t(120,220,\\fscx100\\fscy100)"
                                      f"\\fad(0,150)}}{esc(pre + final + suf)}"))
    if el.get("etiqueta"):
        lineas.append(dlg(12, a, z, f"{{\\an5\\pos({x:.1f},{y + tam * 0.75:.1f})\\fs{tam * 0.32:.1f}"
                                    f"\\c{c(e['color_claro'])}\\3c{c(e['color_oscuro'])}\\bord1.2\\shad0"
                                    f"\\fad(200,150)}}{esc(el['etiqueta'].upper())}"))
    return lineas


def mg_lista(el, e, W, H):
    items, tiempos, z = el["items"], el["tiempos"], el["fin"]
    tam = el.get("tamano", 18)
    x0 = float(el.get("x", 0.10)) * W
    y0 = py(el, H, "arriba")
    paso = tam * 1.55
    lineas = []
    for i, (texto, t) in enumerate(zip(items, tiempos)):
        y = y0 + i * paso
        r = tam * 0.62
        mv = f"\\move({x0 - 20:.1f},{y:.1f},{x0:.1f},{y:.1f},0,200)"
        lineas.append(dlg(10, t, z, f"{{\\an5{mv}\\p1\\bord0\\shad0\\c{c(e['color_activo'])}\\fad(150,150)}}"
                                    f"{circulo(r)}"))
        lineas.append(dlg(11, t, z, f"{{\\an5{mv}\\fs{tam * 0.9:.1f}\\c{c(e['color_claro'])}\\bord0\\shad0"
                                    f"\\fad(150,150)}}{i + 1}"))
        mv2 = f"\\move({x0 + r + 6 - 20:.1f},{y:.1f},{x0 + r + 6:.1f},{y:.1f},0,200)"
        lineas.append(dlg(11, t, z, f"{{\\an4{mv2}\\fs{tam}\\c{c(e['color_claro'])}\\3c{c(e['color_oscuro'])}"
                                    f"\\bord1.4\\shad0.6\\fad(150,150)}}{esc(texto.upper())}"))
    return lineas


def mg_rotulo(el, e, W, H):
    a, z = el["inicio"], el["fin"]
    tam = el.get("tamano", 16)
    y = py(el, H, "abajo") if ("y" in el or "posicion" in el) else H * 0.56
    x = W * 0.06
    t1, t2 = esc(el["titulo"].upper()), esc(el.get("subtitulo", "").upper())
    w = max(ancho_texto(el["titulo"], tam), ancho_texto(el.get("subtitulo", ""), tam * 0.7)) + 22
    h = tam * 2.3
    def mv(dx, yy):
        return f"\\move({x - 40 + dx:.1f},{yy:.1f},{x + dx:.1f},{yy:.1f},0,250)"

    return [
        dlg(10, a, z, f"{{\\an4{mv(0, y)}\\p1\\bord0\\shad0\\c{c(e['color_oscuro'])}\\1a&H20&\\fad(150,200)}}"
                      f"{rect(w, h, 4)}"),
        dlg(10, a, z, f"{{\\an4{mv(0, y)}\\p1\\bord0\\shad0\\c{c(e['color_activo'])}\\fad(150,200)}}{rect(4, h)}"),
        dlg(11, a, z, f"{{\\an4{mv(12, y)}\\fs{tam}\\c{c(e['color_claro'])}\\bord0\\shad0\\fad(150,200)\\fsp0.5}}"
                      f"{t1}\\N{{\\fs{tam * 0.7:.1f}\\c{c(e['color_activo'])}}}{t2}"),
    ]


def mg_flecha(el, e, W, H):
    a, z = el["inicio"], el["fin"]
    x, y = float(el["x"]) * W, float(el["y"]) * H
    s = float(el.get("tamano", 22))
    # \frz positivo gira en sentido antihorario; la forma base apunta hacia abajo
    giro = {"abajo": 0, "derecha": 90, "arriba": 180, "izquierda": -90}.get(el.get("direccion", "abajo"), 0)
    vx, vy = {"abajo": (0, 1), "derecha": (1, 0), "arriba": (0, -1), "izquierda": (-1, 0)}.get(
        el.get("direccion", "abajo"), (0, 1))
    dx, dy = -vx * 10, -vy * 10  # arranca 10 puntos por detrás y avanza hacia la punta
    # flecha apuntando hacia abajo con la punta en (0,0)
    forma = (f"m 0 0 l {-s * 0.55:.1f} {-s * 0.55:.1f} l {-s * 0.2:.1f} {-s * 0.55:.1f} "
             f"l {-s * 0.2:.1f} {-s * 1.3:.1f} l {s * 0.2:.1f} {-s * 1.3:.1f} l {s * 0.2:.1f} {-s * 0.55:.1f} "
             f"l {s * 0.55:.1f} {-s * 0.55:.1f}")
    lineas = []
    # rebote: 3 ciclos de ida y vuelta
    dur = z - a
    ciclos = max(1, int(dur / 0.5))
    for k in range(ciclos):
        t0, t1 = a + k * dur / ciclos, a + (k + 1) * dur / ciclos
        lineas.append(dlg(13, t0, t1, f"{{\\an7\\move({x + dx:.1f},{y + dy:.1f},{x:.1f},{y:.1f})\\frz{giro}"
                                      f"\\org({x:.1f},{y:.1f})\\p1\\c{c(e['color_activo'])}\\3c{c(e['color_oscuro'])}"
                                      f"\\bord1.2\\shad0}}{forma}"))
    return lineas


def mg_circulo(el, e, W, H):
    a, z = el["inicio"], el["fin"]
    x, y = float(el["x"]) * W, float(el["y"]) * H
    r = float(el.get("radio", 0.12)) * W
    anim = "\\fscx0\\fscy0\\t(0,200,\\fscx108\\fscy108)\\t(200,300,\\fscx100\\fscy100)"
    return [dlg(13, a, z, f"{{\\an5\\pos({x:.1f},{y:.1f})\\p1\\1a&HFF&\\3c{c(e['color_activo'])}\\bord2.4\\shad0"
                          f"{anim}\\fad(0,150)}}{circulo(r)}")]


def mg_flash(el, e, W, H):
    a = el["inicio"]
    z = a + float(el.get("duracion", 0.18))
    return [dlg(20, a, z, f"{{\\an7\\pos(0,0)\\p1\\bord0\\shad0\\c{c(el.get('color', '#FFFFFF'))}"
                          f"\\1a&H40&\\t(\\1a&HFF&)}}{rect(W, H)}")]


def mg_cta(el, e, W, H):
    a, z = el["inicio"], el["fin"]
    palabra = el["palabra"].upper()
    y = py(el, H, "centro")
    w, h = W * 0.78, 118
    pop = "\\fscx40\\fscy40\\t(0,160,\\fscx106\\fscy106)\\t(160,260,\\fscx100\\fscy100)"
    lat = "\\t(400,700,\\fscx108\\fscy108)\\t(700,1000,\\fscx100\\fscy100)\\t(1000,1300,\\fscx108\\fscy108)\\t(1300,1600,\\fscx100\\fscy100)"
    return [
        dlg(14, a, z, f"{{\\an5\\pos({W / 2:.1f},{y:.1f})\\p1\\bord0\\shad0\\c{c(e['color_oscuro'])}\\1a&H18&{pop}"
                      f"\\fad(0,200)}}{rect(w, h, 14)}"),
        dlg(15, a, z, f"{{\\an5\\pos({W / 2:.1f},{y - 36:.1f})\\fs18\\c{c(e['color_claro'])}\\bord0\\shad0{pop}"
                      f"\\fad(0,200)}}{esc(el.get('texto', 'COMENTA').upper())}"),
        dlg(15, a, z, f"{{\\an5\\pos({W / 2:.1f},{y + 2:.1f})\\fs50\\c{c(e['color_activo'])}\\bord0\\shad0{pop}"
                      f"{lat}\\fad(0,200)}}{esc(palabra)}"),
        dlg(15, a, z, f"{{\\an5\\pos({W / 2:.1f},{y + 40:.1f})\\fs14\\c{c(e['color_claro'])}\\bord0\\shad0{pop}"
                      f"\\fad(0,200)}}{esc(el.get('subtexto', 'Y TE LO MANDO POR DM').upper())}"),
    ]


def mg_barra(e, W, H, duracion):
    h = 3
    return [dlg(30, 0, duracion, f"{{\\an7\\pos(0,0)\\p1\\bord0\\shad0\\c{c(e['color_activo'])}"
                                  f"\\clip(0,0,0,{h})\\t(0,{int(duracion * 1000)},\\clip(0,0,{W},{h}))}}{rect(W, h)}")]


TIPOS = {
    "titulo": mg_titulo, "palabra_clave": mg_palabra_clave, "contador": mg_contador, "lista": mg_lista,
    "rotulo": mg_rotulo, "flecha": mg_flecha, "circulo": mg_circulo, "flash": mg_flash, "cta": mg_cta,
}


# ───────────────────────── composición ─────────────────────────

def construir_ass(meta, palabras, plan, e, palabras_cta):
    W = 360
    H = round(360 * meta["alto"] / meta["ancho"])
    dur = meta["duracion"]
    enfasis = {re.sub(r"[^\wñáéíóúü%€+]", "", x.lower()) for x in plan.get("enfasis", [])}
    avisos = []
    lineas = subtitulos(palabras, e, enfasis, W, H, dur)
    for el in plan.get("elementos", []):
        tipo = el.get("tipo")
        if tipo in ("zoom", "barra_progreso"):
            continue
        if tipo not in TIPOS:
            avisos.append(f"tipo desconocido ignorado: {tipo}")
            continue
        if tipo == "cta" and el.get("palabra", "").upper() not in palabras_cta:
            avisos.append(f"⚠ CTA con palabra '{el.get('palabra')}' que no está en n8n ({', '.join(palabras_cta)})")
        for k in ("inicio", "fin"):
            if k in el and el[k] > dur + 0.01:
                avisos.append(f"⚠ {tipo}: {k}={el[k]} supera la duración ({dur:.2f} s); se recorta")
                el[k] = dur
        lineas += TIPOS[tipo](el, e, W, H)
    if e.get("barra_progreso") or any(x.get("tipo") == "barra_progreso" for x in plan.get("elementos", [])):
        lineas += mg_barra(e, W, H, dur)

    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{e['fuente']},{e['tamano']},{c(e['color_texto'])},{c(e['color_activo'])},{c(e['color_oscuro'])},&H80000000&,0,0,0,0,100,100,0.6,0,1,{e['contorno']},{e['sombra']},5,10,10,10,1
Style: MG,{e['fuente']},20,{c(e['color_claro'])},{c(e['color_activo'])},{c(e['color_oscuro'])},&H80000000&,0,0,0,0,100,100,0.4,0,1,0,0,5,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    return cab + "\n".join(lineas) + "\n", avisos


def filtro_zoom(plan, meta):
    zooms = [z for z in plan.get("elementos", []) if z.get("tipo") == "zoom"]
    if not zooms:
        return None
    partes = []
    for z in zooms:
        a, b, f = float(z["inicio"]), float(z["fin"]), float(z.get("factor", 1.15))
        r = float(z.get("rampa", 0.25))
        partes.append(f"{f - 1:.3f}*min(1,max(0,(it-{a:.3f})/{r}))*min(1,max(0,({b:.3f}-it)/{r}))")
    expr = "1+" + "+".join(partes)
    w, h = meta["ancho"] - meta["ancho"] % 2, meta["alto"] - meta["alto"] % 2
    return (f"zoompan=z='{expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:"
            f"s={w}x{h}:fps={meta['fps']}")


def meta_video(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", video],
                       check=True, capture_output=True, text=True)
    info = json.loads(r.stdout)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    w, h = int(v["width"]), int(v["height"])
    rot = int(v.get("tags", {}).get("rotate", 0) or 0)
    for sd in v.get("side_data_list", []) or []:
        rot = int(sd.get("rotation", rot))
    if abs(rot) in (90, 270):
        w, h = h, w
    num, den = (v.get("avg_frame_rate") or "30/1").split("/")
    fps = float(num) / float(den) if float(den) else 30.0
    return {"ancho": w, "alto": h, "fps": round(fps, 3), "duracion": float(info["format"]["duration"]),
            "audio": any(s["codec_type"] == "audio" for s in info["streams"])}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--palabras", help="transcripcion.json")
    ap.add_argument("--plan", help="plan de motion graphics .json")
    ap.add_argument("--estilo", help="estilo .json (sobrescribe valores por defecto)")
    ap.add_argument("--tamano", type=float, help="tamaño de subtítulos (por defecto 12)")
    ap.add_argument("--modo", choices=["acumulado", "una"])
    ap.add_argument("--out", default="reel_final.mp4")
    ap.add_argument("--preview", help="segundos separados por comas: genera PNGs en vez del vídeo")
    ap.add_argument("--palabras-cta", default=",".join(PALABRAS_VALIDAS_CTA))
    a = ap.parse_args()

    e = dict(ESTILO_POR_DEFECTO)
    if a.estilo:
        e.update(json.load(open(a.estilo, encoding="utf-8")))
    if a.tamano:
        e["tamano"] = a.tamano
    if a.modo:
        e["modo"] = a.modo
    meta = meta_video(a.video)
    palabras = json.load(open(a.palabras, encoding="utf-8"))["palabras"] if a.palabras else []
    plan = json.load(open(a.plan, encoding="utf-8")) if a.plan else {}
    palabras_cta = [p.strip().upper() for p in a.palabras_cta.split(",") if p.strip()]

    ass, avisos = construir_ass(meta, palabras, plan, e, palabras_cta)
    base = os.path.splitext(os.path.abspath(a.out))[0]
    os.makedirs(os.path.dirname(base), exist_ok=True)
    ruta_ass = base + ".ass"
    open(ruta_ass, "w", encoding="utf-8").write(ass)
    for av in avisos:
        print(av)
    print(f"✔ Subtítulos y gráficos: {ruta_ass}")

    filtros = []
    z = filtro_zoom(plan, meta)
    if z:
        filtros.append(z)
    filtros.append(f"ass='{ruta_ass}':fontsdir='{FUENTES}'")
    vf = ",".join(filtros)

    if a.preview:
        carpeta = base + "_preview"
        os.makedirs(carpeta, exist_ok=True)
        for t in [float(x) for x in a.preview.split(",") if x.strip()]:
            png = os.path.join(carpeta, f"t{t:05.2f}.png")
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a.video, "-vf", vf, "-ss", str(t),
                            "-frames:v", "1", png], check=True)
            print(f"✔ preview {png}")
        return 0

    cmd = ["ffmpeg", "-y", "-v", "error", "-stats", "-i", a.video, "-vf", vf,
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    cmd += ["-c:a", "aac", "-b:a", "192k"] if meta["audio"] else ["-an"]
    subprocess.run(cmd + [a.out], check=True)
    print(f"✔ Vídeo final: {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
