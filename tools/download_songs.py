#!/usr/bin/env python3
"""Download the curated playlist from YouTube using yt-dlp into PackRadio/songs/
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SONG_DIR = os.path.join(ROOT, "songs")
os.makedirs(SONG_DIR, exist_ok=True)

PLAYLIST = [
    {"num": "01", "name": "dieu_toa_x_2_phut_hon_speedup", "url": "https://youtu.be/z3-VwURaDi4"},
    {"num": "02", "name": "nhat_than_vo_duyen_tuy_am_mix", "url": "https://youtu.be/ClsozT7Ky9U"},
    {"num": "03", "name": "tinh_ve_ban_hi_khang", "url": "https://youtu.be/gQjjdbta0v8"},
    {"num": "04", "name": "cho_chut_x_noi_nay_co_anh_mix", "url": "https://youtu.be/mVB_8oBqgcU"},
    {"num": "05", "name": "cuoi_di_x_vay_cuoi_x_gedl_mix", "url": "https://youtu.be/07U4H4m6rQc"},
    {"num": "06", "name": "fly_away_thefatrat_speedup", "url": "https://youtu.be/-YJZKrcr9YY"},
    {"num": "07", "name": "see_tinh_hoang_thuy_linh_speedup", "url": "https://youtu.be/iZUgSbYhKzs"}
]

def main():
    print("🚀 [PackRadio Downloader] Đang tải danh sách 7 bài hát đã chọn lọc...")
    for item in PLAYLIST:
        out_tmpl = os.path.join(SONG_DIR, f"{item['num']}_{item['name']}.%(ext)s")
        target_file = os.path.join(SONG_DIR, f"{item['num']}_{item['name']}.mp3")
        if os.path.exists(target_file):
            print(f"✅ Đã có sẵn: {target_file}")
            continue
        print(f"⬇️ Đang tải: {item['num']} - {item['name']} ({item['url']})...")
        cmd = [
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "-o", out_tmpl,
            item["url"]
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            print(f"  ✓ Tải thành công: {target_file}")
        else:
            print(f"  ❌ Lỗi tải {item['name']}: {r.stderr[-500:]}")

if __name__ == "__main__":
    main()
