#!/usr/bin/env python3
"""Corta los silencios de un vídeo y lo acelera (por defecto ×1,3) manteniendo el tono de la voz.

Detecta los silencios con ffmpeg (silencedetect), conserva los tramos con voz dejando un pequeño margen
para que los cortes no suenen bruscos, los une con un fundido de audio de 15 ms y aplica la velocidad
(vídeo con setpts, audio con atempo → la voz no se vuelve aguda).

Salidas (junto a --out):
  editado.mp4                 vídeo sin silencios y acelerado
  editado_cortes.json         tramos conservados, silencios eliminados y duración antes/después
  editado_transcripcion.json  solo si se pasa --transcripcion: tiempos de cada palabra recalculados

Uso:
  python3 recortar_video.py VIDEO.mp4 --out trabajo_reel/editado.mp4
        [--velocidad 1.3] [--umbral -32] [--min-silencio 0.35] [--margen 0.10]
        [--transcripcion trabajo_reel/transcripcion.json]
"""
import argparse
import json
import os
import re
import subprocess
import sys


def meta_video(video):
    r = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", video],
                       check=True, capture_output=True, text=True)
    info = json.loads(r.stdout)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    num, den = (v.get("avg_frame_rate") or "30/1").split("/")
    return {
        "duracion": float(info["format"]["duration"]),
        "fps": round(float(num) / float(den), 3) if float(den) else 30.0,
        "audio": any(s["codec_type"] == "audio" for s in info["streams"]),
    }


def detectar_silencios(video, umbral, minimo, duracion):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-vn",
                        "-af", f"silencedetect=noise={umbral}dB:d={minimo}", "-f", "null", "-"],
                       capture_output=True, text=True)
    silencios, inicio = [], None
    for linea in r.stderr.splitlines():
        m = re.search(r"silence_start: (-?[\d.]+)", linea)
        if m:
            inicio = max(0.0, float(m.group(1)))
        m = re.search(r"silence_end: ([\d.]+)", linea)
        if m and inicio is not None:
            silencios.append((inicio, float(m.group(1))))
            inicio = None
    if inicio is not None:  # el vídeo acaba en silencio
        silencios.append((inicio, duracion))
    return silencios


def tramos_con_voz(silencios, duracion, margen):
    """Complementario de los silencios, dejando `margen` segundos de aire a cada lado de la voz."""
    quitar = []
    for a, b in silencios:
        a2 = 0.0 if a <= 0.01 else a + margen
        b2 = duracion if b >= duracion - 0.01 else b - margen
        if b2 - a2 > 0.05:
            quitar.append((a2, b2))
    tramos, t = [], 0.0
    for a, b in quitar:
        if a - t > 0.08:
            tramos.append((round(t, 3), round(a, 3)))
        t = b
    if duracion - t > 0.08:
        tramos.append((round(t, 3), round(duracion, 3)))
    return tramos, quitar


def remapear(t, tramos, velocidad):
    """Convierte un instante del vídeo original al del vídeo editado (None si cae en un hueco eliminado)."""
    acumulado = 0.0
    for a, b in tramos:
        if t < a:
            return None
        if t <= b:
            return (acumulado + t - a) / velocidad
        acumulado += b - a
    return None


def remapear_transcripcion(ruta, tramos, velocidad, destino):
    d = json.load(open(ruta, encoding="utf-8"))
    total = sum(b - a for a, b in tramos) / velocidad
    nuevas = []
    for p in d.get("palabras", []):
        i, f = remapear(p["inicio"], tramos, velocidad), remapear(p["fin"], tramos, velocidad)
        if i is None and f is None:
            continue  # la palabra estaba en un tramo eliminado (ruido/respiración)
        if i is None:
            i = max(0.0, f - 0.15)
        if f is None or f <= i:
            f = min(total, i + max(0.08, (p["fin"] - p["inicio"]) / velocidad))
        nuevas.append(dict(p, inicio=round(i, 3), fin=round(f, 3)))
    segs = []
    for s in d.get("segmentos", []):
        i, f = remapear(s["inicio"], tramos, velocidad), remapear(s["fin"], tramos, velocidad)
        if i is not None or f is not None:
            segs.append(dict(s, inicio=round(i if i is not None else 0, 3), fin=round(f if f is not None else total, 3)))
    d.update(palabras=nuevas, segmentos=segs, origen=f"{d.get('origen', '')} · recortado ×{velocidad}")
    json.dump(d, open(destino, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return len(nuevas)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--out", default="trabajo_reel/editado.mp4")
    ap.add_argument("--velocidad", type=float, default=1.3, help="factor de velocidad (1.3 = 30 %% más rápido)")
    ap.add_argument("--umbral", type=float, default=-32, help="dB por debajo de los cuales se considera silencio")
    ap.add_argument("--min-silencio", type=float, default=0.35, help="duración mínima de un silencio para cortarlo (s)")
    ap.add_argument("--margen", type=float, default=0.10, help="aire que se deja antes/después de la voz (s)")
    ap.add_argument("--transcripcion", help="transcripcion.json del vídeo original para recalcular sus tiempos")
    ap.add_argument("--sin-cortes", action="store_true", help="solo cambiar la velocidad")
    a = ap.parse_args()

    if not 0.5 <= a.velocidad <= 2.0:
        sys.exit("La velocidad debe estar entre 0,5 y 2,0")
    meta = meta_video(a.video)
    dur = meta["duracion"]
    if not meta["audio"] or a.sin_cortes:
        silencios, tramos, quitados = [], [(0.0, dur)], []
        if not meta["audio"]:
            print("⚠ El vídeo no tiene audio: solo se aplica la velocidad.")
    else:
        silencios = detectar_silencios(a.video, a.umbral, a.min_silencio, dur)
        tramos, quitados = tramos_con_voz(silencios, dur, a.margen)
        if not tramos:
            sys.exit("✖ Todo el vídeo parece silencio. Prueba con un --umbral más bajo (p. ej. -40).")

    base = os.path.splitext(os.path.abspath(a.out))[0]
    os.makedirs(os.path.dirname(base), exist_ok=True)

    partes, entradas = [], []
    fade = 0.015
    for i, (x, y) in enumerate(tramos):
        partes.append(f"[0:v]trim=start={x}:end={y},setpts=PTS-STARTPTS[v{i}]")
        if meta["audio"]:
            largo = y - x
            partes.append(f"[0:a]atrim=start={x}:end={y},asetpts=PTS-STARTPTS,"
                          f"afade=t=in:d={fade},afade=t=out:st={max(0, largo - fade):.3f}:d={fade}[a{i}]")
            entradas.append(f"[v{i}][a{i}]")
        else:
            entradas.append(f"[v{i}]")
    n = len(tramos)
    if meta["audio"]:
        partes.append(f"{''.join(entradas)}concat=n={n}:v=1:a=1[vc][ac]")
        partes.append(f"[vc]setpts=PTS/{a.velocidad}[vo]")
        # atempo admite 0.5–2.0 en una sola etapa: suficiente para el rango permitido
        partes.append(f"[ac]atempo={a.velocidad}[ao]")
        mapas = ["-map", "[vo]", "-map", "[ao]", "-c:a", "aac", "-b:a", "192k"]
    else:
        partes.append(f"{''.join(entradas)}concat=n={n}:v=1:a=0[vc]")
        partes.append(f"[vc]setpts=PTS/{a.velocidad}[vo]")
        mapas = ["-map", "[vo]"]

    script = base + "_filtro.txt"
    open(script, "w").write(";\n".join(partes))
    cmd = ["ffmpeg", "-y", "-v", "error", "-stats", "-i", a.video, "-filter_complex_script", script,
           *mapas, "-r", str(meta["fps"]), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", base + ".mp4"]
    subprocess.run(cmd, check=True)
    os.remove(script)

    conservado = sum(y - x for x, y in tramos)
    final = conservado / a.velocidad
    info = {
        "original": a.video, "editado": base + ".mp4", "velocidad": a.velocidad,
        "umbral_db": a.umbral, "min_silencio": a.min_silencio, "margen": a.margen,
        "duracion_original": round(dur, 2), "duracion_sin_silencios": round(conservado, 2),
        "duracion_final": round(final, 2), "silencios_eliminados": len(quitados),
        "tramos_conservados": tramos, "tramos_eliminados": [(round(x, 3), round(y, 3)) for x, y in quitados],
    }
    json.dump(info, open(base + "_cortes.json", "w", encoding="utf-8"), indent=1)
    print(f"✔ {len(quitados)} silencios cortados · {dur:.1f} s → {conservado:.1f} s → ×{a.velocidad} = {final:.1f} s")
    print(f"✔ Vídeo editado: {base}.mp4")

    if a.transcripcion:
        k = remapear_transcripcion(a.transcripcion, tramos, a.velocidad, base + "_transcripcion.json")
        print(f"✔ Transcripción recalculada ({k} palabras): {base}_transcripcion.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
