#!/usr/bin/env python3
"""Prepara un vídeo adjunto para que Claude lo "vea" y lo "escuche".

Genera en la carpeta de salida:
  meta.json            duración, resolución, fps
  fotogramas/          un fotograma cada N segundos (f_0001_t0.0.jpg …)
  hoja_contacto.jpg    todos los fotogramas en una sola imagen con su segundo
  audio.wav            audio mono 16 kHz
  transcripcion.json   palabras con tiempos  {"palabras": [{"texto", "inicio", "fin"}], "segmentos": [...]}
  transcripcion.txt    texto legible con marcas de tiempo

Transcripción (por orden de preferencia):
  1. --transcripcion FICHERO (.srt o .json ya hecho, p. ej. de ElevenLabs/CapCut): se convierte a palabras.
  2. faster-whisper local (pip install faster-whisper) con tiempos por palabra.
  Si ninguna está disponible, deja fotogramas + audio y sale con código 2 explicando qué hacer.

Uso:
  python3 analizar_video.py VIDEO.mp4 --out trabajo/ [--cada 1.5] [--modelo small] [--idioma es]
"""
import argparse
import json
import os
import re
import subprocess
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
FUENTE = os.path.join(AQUI, "..", "assets", "fonts", "BebasNeue-Regular.ttf")

# Vocabulario de la marca para que Whisper no lo destroce
GLOSARIO = (
    "GORMARAN, Gabriela Ormazabal, Vitoria-Gasteiz, Álava, Euskadi, ChatGPT, Gemini, Perplexity, "
    "Claude, Google, Instagram, WhatsApp, GEO, SEO, RADAR, RESERVAS, n8n, La Rioja Alta, Agromotor, "
    "Just Drive, Ormaran Paisajismo, Jatorki, ROAS, ROI, IA."
)


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def meta_video(video):
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", video])
    info = json.loads(r.stdout)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    w, h = int(v["width"]), int(v["height"])
    rot = 0
    for sd in v.get("side_data_list", []) or []:
        if "rotation" in sd:
            rot = int(sd["rotation"])
    rot = int(v.get("tags", {}).get("rotate", rot) or 0)
    if abs(rot) in (90, 270):
        w, h = h, w
    num, den = (v.get("avg_frame_rate") or "30/1").split("/")
    fps = float(num) / float(den) if float(den) else 30.0
    tiene_audio = any(s["codec_type"] == "audio" for s in info["streams"])
    return {
        "archivo": os.path.abspath(video),
        "duracion": float(info["format"]["duration"]),
        "ancho": w,
        "alto": h,
        "fps": round(fps, 3),
        "tiene_audio": tiene_audio,
    }


def extraer_fotogramas(video, out, cada, meta):
    carpeta = os.path.join(out, "fotogramas")
    os.makedirs(carpeta, exist_ok=True)
    for f in os.listdir(carpeta):
        os.remove(os.path.join(carpeta, f))
    run([
        "ffmpeg", "-y", "-v", "error", "-i", video,
        "-vf", f"fps=1/{cada},scale=360:-2",
        "-q:v", "3", os.path.join(carpeta, "f_%04d.jpg"),
    ])
    nombres = sorted(os.listdir(carpeta))
    for i, n in enumerate(nombres):
        t = round(i * cada, 1)
        os.rename(os.path.join(carpeta, n), os.path.join(carpeta, f"f_{i + 1:04d}_t{t}.jpg"))
    # Hoja de contacto con el segundo de cada fotograma
    cols = 6
    filas = max(1, -(-len(nombres) // cols))
    marca = f"%{{eif\\:n*{int(cada)}\\:d}}" if float(cada).is_integer() else f"%{{expr\\:n*{cada}}}"
    texto = (
        f"drawtext=fontfile='{FUENTE}':text='{marca} s':"
        "x=8:y=8:fontsize=28:fontcolor=white:box=1:boxcolor=0x26212E@0.8:boxborderw=6"
    )
    run([
        "ffmpeg", "-y", "-v", "error", "-i", video,
        "-vf", f"fps=1/{cada},scale=240:-2,{texto},tile={cols}x{filas}:padding=4:color=0x26212E",
        "-frames:v", "1", "-q:v", "3", os.path.join(out, "hoja_contacto.jpg"),
    ])
    return len(nombres)


def extraer_audio(video, out):
    destino = os.path.join(out, "audio.wav")
    run(["ffmpeg", "-y", "-v", "error", "-i", video, "-vn", "-ac", "1", "-ar", "16000", destino])
    return destino


def _seg(ts):
    h, m, s = ts.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def palabras_desde_srt(ruta):
    """Reparte el tiempo de cada bloque SRT entre sus palabras según su longitud."""
    bloques = re.split(r"\n\s*\n", open(ruta, encoding="utf-8-sig").read().strip())
    palabras, segmentos = [], []
    for b in bloques:
        lineas = [l for l in b.strip().splitlines() if l.strip()]
        idx = next((i for i, l in enumerate(lineas) if "-->" in l), None)
        if idx is None:
            continue
        a, z = [_seg(x.strip().split()[0]) for x in lineas[idx].split("-->")]
        texto = " ".join(lineas[idx + 1:]).strip()
        texto = re.sub(r"<[^>]+>", "", texto)
        trozos = texto.split()
        if not trozos:
            continue
        segmentos.append({"texto": texto, "inicio": a, "fin": z})
        total = sum(len(p) + 1 for p in trozos)
        t = a
        for p in trozos:
            d = (z - a) * (len(p) + 1) / total
            palabras.append({"texto": p, "inicio": round(t, 3), "fin": round(t + d, 3)})
            t += d
    return palabras, segmentos


def palabras_desde_json(ruta):
    d = json.load(open(ruta, encoding="utf-8"))
    if isinstance(d, dict) and "palabras" in d:
        return d["palabras"], d.get("segmentos", [])
    # Formatos habituales: {"words":[{"text"|"word","start","end"}]}
    lista = d.get("words") if isinstance(d, dict) else d
    palabras = []
    for w in lista or []:
        texto = (w.get("text") or w.get("word") or w.get("texto") or "").strip()
        if not texto or w.get("type") in ("spacing", "audio_event"):
            continue
        palabras.append({
            "texto": texto,
            "inicio": float(w.get("start", w.get("inicio", 0))),
            "fin": float(w.get("end", w.get("fin", 0))),
        })
    return palabras, []


def transcribir_whisper(audio, modelo, idioma):
    from faster_whisper import WhisperModel  # import tardío: es opcional

    m = WhisperModel(modelo, device="auto", compute_type="int8")
    segs, _ = m.transcribe(
        audio, language=idioma, word_timestamps=True, vad_filter=True,
        initial_prompt=GLOSARIO,
    )
    palabras, segmentos = [], []
    for s in segs:
        segmentos.append({"texto": s.text.strip(), "inicio": round(s.start, 3), "fin": round(s.end, 3)})
        for w in s.words or []:
            if w.word.strip():
                palabras.append({"texto": w.word.strip(), "inicio": round(w.start, 3), "fin": round(w.end, 3)})
    return palabras, segmentos


def guardar_transcripcion(out, palabras, segmentos, origen):
    json.dump(
        {"origen": origen, "palabras": palabras, "segmentos": segmentos},
        open(os.path.join(out, "transcripcion.json"), "w", encoding="utf-8"),
        ensure_ascii=False, indent=1,
    )
    with open(os.path.join(out, "transcripcion.txt"), "w", encoding="utf-8") as f:
        if segmentos:
            for s in segmentos:
                f.write(f"[{s['inicio']:6.2f} – {s['fin']:6.2f}] {s['texto']}\n")
        else:
            for p in palabras:
                f.write(f"[{p['inicio']:6.2f}] {p['texto']}\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--out", default="trabajo_reel")
    ap.add_argument("--cada", type=float, default=1.0, help="segundos entre fotogramas")
    ap.add_argument("--modelo", default="small", help="modelo faster-whisper (tiny/base/small/medium/large-v3)")
    ap.add_argument("--idioma", default="es")
    ap.add_argument("--transcripcion", help=".srt o .json ya existente (se convierte a palabras con tiempos)")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    meta = meta_video(a.video)
    json.dump(meta, open(os.path.join(a.out, "meta.json"), "w"), indent=1)
    n = extraer_fotogramas(a.video, a.out, a.cada, meta)
    print(f"✔ {n} fotogramas en {a.out}/fotogramas y hoja_contacto.jpg")
    print(f"✔ {meta['ancho']}x{meta['alto']} · {meta['duracion']:.1f} s · {meta['fps']} fps")

    if not meta["tiene_audio"] and not a.transcripcion:
        print("⚠ El vídeo no tiene audio: no hay nada que transcribir (los subtítulos saldrán vacíos).")
        guardar_transcripcion(a.out, [], [], "sin_audio")
        return 0

    if a.transcripcion:
        if a.transcripcion.lower().endswith(".srt"):
            palabras, segmentos = palabras_desde_srt(a.transcripcion)
        else:
            palabras, segmentos = palabras_desde_json(a.transcripcion)
        guardar_transcripcion(a.out, palabras, segmentos, os.path.basename(a.transcripcion))
        print(f"✔ Transcripción importada: {len(palabras)} palabras")
        return 0

    audio = extraer_audio(a.video, a.out)
    print(f"✔ Audio en {audio}")
    try:
        palabras, segmentos = transcribir_whisper(audio, a.modelo, a.idioma)
    except Exception as e:  # sin librería, sin red para el modelo, etc.
        print(
            "✖ No se pudo transcribir con faster-whisper: " + str(e).splitlines()[0] + "\n"
            "  Alternativas: (1) pip install faster-whisper y repetir (descarga el modelo la 1ª vez);\n"
            "  (2) transcribir audio.wav con ElevenLabs u otra herramienta y repetir con --transcripcion fichero.json/.srt;\n"
            "  (3) exportar los subtítulos automáticos de CapCut/Edits en .srt y usar --transcripcion."
        )
        return 2
    guardar_transcripcion(a.out, palabras, segmentos, f"faster-whisper:{a.modelo}")
    print(f"✔ Transcripción: {len(palabras)} palabras → {a.out}/transcripcion.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
