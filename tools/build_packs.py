#!/usr/bin/env python3
"""Build Java + Bedrock radio packs tu songs/*.mp3 — Thuat toan V2 Ultra-Compression.
Java: assets/pikaradio/sounds.json + sounds/*.ogg (mono 32kHz vorbis 32kbps, stream:true, no video)
Bedrock: sounds/sound_definitions.json + sounds/*.ogg (tai su dung file ogg chung)
Usage: python3 tools/build_packs.py [--java-out PikaRadio-Java.zip] [--bedrock-out PikaRadio-Bedrock.mcpack] [--bitrate 32k] [--stereo]
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, time, uuid, zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONG_DIR = os.path.join(ROOT, "songs")
NS = "pikaradio"

def slug(name):
    base = os.path.splitext(os.path.basename(name))[0].lower()
    base = re.sub(r"[^a-z0-9]+", "_", base).strip("_") or "track"
    return base[:40]

def convert(src, dst, bitrate="32k", sample_rate=32000, mono=True):
    # V2 Ultra-Compression Algorithm:
    # -vn: strip 100% video/thumbnail/cover art (tiet kiem 300KB-500KB moi bai)
    # -map_metadata -1: xoa sach moi metadata
    # -ac 1: Mono 1-channel (don toan bo bit vao vocal ca si, giam 50% dung luong)
    # -ar 32000: 32kHz (tai tao hoan hao dải âm toi 16kHz, tron tria giong hat)
    # -c:a libvorbis -b:a 32k: chuan Ogg Vorbis tuong thich 100% Minecraft
    channels = ["-ac", "1"] if mono else ["-ac", "2"]
    cmd = [
        "ffmpeg", "-y", "-i", src,
        "-vn", "-map_metadata", "-1",
        *channels,
        "-ar", str(sample_rate),
        "-c:a", "libvorbis",
        "-b:a", bitrate,
        dst
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ffmpeg LOI:", r.stderr[-1500:])
        raise SystemExit(1)

def get_sha1(filepath):
    h = hashlib.sha1()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def get_duration(filepath):
    cmd = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", filepath]
    r = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except:
        return 0.0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--java-out", default=os.path.join(ROOT, "PikaRadio-Java.zip"))
    ap.add_argument("--bedrock-out", default=os.path.join(ROOT, "PikaRadio-Bedrock.mcpack"))
    ap.add_argument("--bitrate", default="32k", help="Bitrate Vorbis (default: 32k)")
    ap.add_argument("--sample-rate", type=int, default=32000, help="Sample rate Hz (default: 32000)")
    ap.add_argument("--stereo", action="store_true", help="Keep stereo (default is Mono)")
    a = ap.parse_args()

    mono = not a.stereo
    mp3s = sorted(f for f in os.listdir(SONG_DIR) if f.lower().endswith((".mp3", ".wav", ".m4a", ".ogg")))
    if not mp3s:
        print("Khong co file nhac nao trong songs/ !"); raise SystemExit(1)
    
    print(f"🚀 [V2 Ultra-Compression] Tim thay {len(mp3s)} bai nhac trong songs/:")
    for f in mp3s:
        print(f"  - {f}")

    work = os.path.join(ROOT, "_work")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(os.path.join(work, "java", f"assets/{NS}/sounds"))
    os.makedirs(os.path.join(work, "bed", "sounds/radio"))
    
    sounds_json = {}
    bed_defs = {}
    total_raw_sz = 0
    total_ogg_sz = 0
    track_info = []

    for i, fn in enumerate(mp3s, 1):
        key = slug(fn)
        ogg = f"{i:02d}_{key}.ogg"
        src_path = os.path.join(SONG_DIR, fn)
        dst_java = os.path.join(work, "java", f"assets/{NS}/sounds", ogg)
        dst_bed = os.path.join(work, "bed", "sounds/radio", ogg)

        raw_sz = os.path.getsize(src_path)
        total_raw_sz += raw_sz

        convert(src_path, dst_java, bitrate=a.bitrate, sample_rate=a.sample_rate, mono=mono)
        shutil.copy(dst_java, dst_bed)

        ogg_sz = os.path.getsize(dst_java)
        total_ogg_sz += ogg_sz
        dur = get_duration(dst_java)

        sounds_json[f"{NS}.{key}"] = {"sounds": [{"name": f"{NS}:sounds/{ogg[:-4]}", "stream": True}]}
        bed_defs[f"radio.{key}"] = {"category": "music", "sounds": [{"name": f"sounds/radio/{ogg[:-4]}", "stream": True, "volume": 1.0}]}

        track_info.append({
            "index": i,
            "filename": fn,
            "key_java": f"{NS}.{key}",
            "key_bedrock": f"radio.{key}",
            "ogg": ogg,
            "duration": dur,
            "size_kb": ogg_sz // 1024
        })
        print(f"  [{i:02d}] {fn[:35]:35s} -> {ogg_sz//1024:5d} KB (goc {raw_sz//1024:5d} KB) | {dur:.1f}s")

    # Java pack
    with open(os.path.join(work, "java", f"assets/{NS}/sounds.json"), "w", encoding="utf-8") as f:
        json.dump(sounds_json, f, indent=2, ensure_ascii=False)
    with open(os.path.join(work, "java", "pack.mcmeta"), "w", encoding="utf-8") as f:
        json.dump({"pack": {"pack_format": 48, "description": "PikaMC Radio V2 - Nhac that trong game"}}, f, indent=2)
    
    if os.path.exists(a.java_out): os.remove(a.java_out)
    with zipfile.ZipFile(a.java_out, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, _, fns in os.walk(os.path.join(work, "java")):
            for fn in fns:
                fp = os.path.join(dp, fn)
                z.write(fp, os.path.relpath(fp, os.path.join(work, "java")))
    
    # Bedrock pack
    with open(os.path.join(work, "bed", "sounds/sound_definitions.json"), "w", encoding="utf-8") as f:
        json.dump({"sound_definitions": bed_defs}, f, indent=2, ensure_ascii=False)
    
    header_uuid = str(uuid.uuid4())
    module_uuid = str(uuid.uuid4())
    version_patch = int(time.time()) % 1000
    with open(os.path.join(work, "bed", "manifest.json"), "w", encoding="utf-8") as f:
        json.dump({
            "format_version": 2,
            "header": {
                "name": "PikaMC Radio V2",
                "description": "Nhac that cho Bedrock (Ultra-Compressed V2)",
                "uuid": header_uuid,
                "version": [2, 0, version_patch],
                "min_engine_version": [1, 20, 0]
            },
            "modules": [{
                "type": "resources",
                "uuid": module_uuid,
                "version": [2, 0, version_patch]
            }]
        }, f, indent=2)
    
    if os.path.exists(a.bedrock_out): os.remove(a.bedrock_out)
    with zipfile.ZipFile(a.bedrock_out, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, _, fns in os.walk(os.path.join(work, "bed")):
            for fn in fns:
                fp = os.path.join(dp, fn)
                z.write(fp, os.path.relpath(fp, os.path.join(work, "bed")))
    
    sha1_java = get_sha1(a.java_out)
    with open(a.java_out + ".sha1", "w") as f:
        f.write(sha1_java + "\n")

    # Output Track info JSON for Skript / Bot
    with open(os.path.join(ROOT, "tracks_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(track_info, f, indent=2, ensure_ascii=False)

    java_sz = os.path.getsize(a.java_out)
    bed_sz = os.path.getsize(a.bedrock_out)

    print("\n" + "="*60)
    print("🎉 [HOÀN TẤT ĐÓNG GÓI PACK RADIO V2]")
    print(f"📦 JAVA PACK    : {a.java_out} ({java_sz / (1024*1024):.2f} MB)")
    print(f"🔑 JAVA SHA1    : {sha1_java}")
    print(f"📱 BEDROCK PACK : {a.bedrock_out} ({bed_sz / (1024*1024):.2f} MB)")
    print(f"📉 TỔNG GỐC     : {total_raw_sz / (1024*1024):.2f} MB ➔ SAU NÉN: {total_ogg_sz / (1024*1024):.2f} MB")
    print(f"⚡ TIẾT KIỆM    : {(1.0 - (total_ogg_sz / total_raw_sz)) * 100:.1f}% dung lượng!")
    print("="*60)

if __name__ == "__main__":
    main()
