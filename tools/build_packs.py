#!/usr/bin/env python3
"""Build Java + Bedrock radio packs tu songs/*.mp3 — chay tren GitHub Actions (co ffmpeg san).
Java: assets/pikaradio/sounds.json + sounds/*.ogg (stereo 44.1kHz vorbis q5, stream:true)
Bedrock: sounds/sound_definitions.json + sounds/*.ogg (tai su dung file ogg chung)
Usage: python3 tools/build_packs.py [--java-out PikaRadio-Java.zip] [--bedrock-out PikaRadio-Bedrock.mcpack]
"""
import argparse, json, os, re, shutil, subprocess, sys, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONG_DIR = os.path.join(ROOT, "songs")
NS = "pikaradio"

def slug(name):
    base = os.path.splitext(os.path.basename(name))[0].lower()
    base = re.sub(r"[^a-z0-9]+", "_", base).strip("_") or "track"
    return base[:40]

def convert(src, dst):
    # stereo, 44100Hz, vorbis q5 (~160kbps) — chuan radio NBS-nghien-cuu
    cmd = ["ffmpeg", "-y", "-i", src, "-ac", "2", "-ar", "44100",
           "-c:a", "libvorbis", "-q:a", "5", dst]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ffmpeg LOI:", r.stderr[-1500:])
        raise SystemExit(1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--java-out", default=os.path.join(ROOT, "PikaRadio-Java.zip"))
    ap.add_argument("--bedrock-out", default=os.path.join(ROOT, "PikaRadio-Bedrock.mcpack"))
    a = ap.parse_args()
    mp3s = sorted(f for f in os.listdir(SONG_DIR) if f.lower().endswith(".mp3"))
    if not mp3s:
        print("Khong co mp3 nao trong songs/ !"); raise SystemExit(1)
    print(f"Tim thay {len(mp3s)} bai: {mp3s}")
    work = os.path.join(ROOT, "_work")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(os.path.join(work, "java", f"assets/{NS}/sounds"))
    os.makedirs(os.path.join(work, "bed", "sounds/radio"))
    sounds_json = {}
    bed_defs = {}
    for i, fn in enumerate(mp3s, 1):
        key = slug(fn)
        ogg = f"{i:02d}_{key}.ogg"
        convert(os.path.join(SONG_DIR, fn), os.path.join(work, "java", f"assets/{NS}/sounds", ogg))
        shutil.copy(os.path.join(work, "java", f"assets/{NS}/sounds", ogg),
                    os.path.join(work, "bed", "sounds/radio", ogg))
        sounds_json[f"{NS}.{key}"] = {"sounds": [{NS: f"{NS}:{key}"}]}
        # sounds.json event tro toi file: sounds/<name> (khong duoi)
        sounds_json[f"{NS}.{key}"] = {"sounds": [{"name": f"{NS}:sounds/{ogg[:-4]}", "stream": True}]}
        bed_defs[f"radio.{key}"] = {"category": "music", "sounds": [{"name": f"sounds/radio/{ogg[:-4]}", "stream": True, "volume": 1.0}]}
        print(f"  [{i}] {fn} -> {ogg} ({os.path.getsize(os.path.join(work,'java',f'assets/{NS}/sounds',ogg))//1024} KB)")
    # Java pack
    with open(os.path.join(work, "java", f"assets/{NS}/sounds.json"), "w") as f:
        json.dump(sounds_json, f, indent=2)
    with open(os.path.join(work, "java", "pack.mcmeta"), "w") as f:
        json.dump({"pack": {"pack_format": 48, "description": "PikaMC Radio - nhac that trong game"}}, f)
    if os.path.exists(a.java_out): os.remove(a.java_out)
    with zipfile.ZipFile(a.java_out, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, _, fns in os.walk(os.path.join(work, "java")):
            for fn in fns:
                fp = os.path.join(dp, fn)
                z.write(fp, os.path.relpath(fp, os.path.join(work, "java")))
    # Bedrock pack
    with open(os.path.join(work, "bed", "sounds/sound_definitions.json"), "w") as f:
        json.dump({"sound_definitions": bed_defs}, f, indent=2)
    import uuid as _uuid, time as _time
    header_uuid = str(_uuid.uuid4())
    module_uuid = str(_uuid.uuid4())
    with open(os.path.join(work, "bed", "manifest.json"), "w") as f:
        json.dump({"format_version": 2, "header": {"name": "PikaMC Radio", "description": "Nhac that cho Bedrock", "uuid": header_uuid, "version": [1, 0, int(_time.time()) % 1000], "min_engine_version": [1, 20, 0]}, "modules": [{"type": "resources", "uuid": module_uuid, "version": [1, 0, 0]}]}, f)
    if os.path.exists(a.bedrock_out): os.remove(a.bedrock_out)
    with zipfile.ZipFile(a.bedrock_out, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, _, fns in os.walk(os.path.join(work, "bed")):
            for fn in fns:
                fp = os.path.join(dp, fn)
                z.write(fp, os.path.relpath(fp, os.path.join(work, "bed")))
    print("JAVA:", a.java_out, os.path.getsize(a.java_out)//1024, "KB")
    print("BEDROCK:", a.bedrock_out, os.path.getsize(a.bedrock_out)//1024, "KB")
    print("Lenh phat Java: /playsound pikaradio.<slug> music @a")
    print("Lenh phat Bedrock: /playsound radio.<slug>")

if __name__ == "__main__":
    main()
