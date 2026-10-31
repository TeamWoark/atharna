#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
استخراج إطارات من فيديوهات الفريق وربطها بشريط التمرير في الموقع.

طريقة الاستخدام:
   1) ضع ملفات الفيديو في مجلد  sources/
   2) شغّل:   python3 tools/frames.py
   3) سيستخرج إطارات إلى  assets/  ويحدّث مصفوفة SLIDES في index.html تلقائيًا.

خيارات:
   python3 tools/frames.py --per-video 3        # عدد الإطارات لكل فيديو
   python3 tools/frames.py --width 1280         # عرض الإطار
   python3 tools/frames.py --no-update          # استخراج فقط بدون تعديل الموقع
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "sources")
OUT = os.path.join(ROOT, "assets")
INDEX = os.path.join(ROOT, "index.html")
VIDEO_EXT = (".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm")


def ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        sys.exit("لم يتم العثور على ffmpeg. ثبّته أو نفّذ: pip install imageio-ffmpeg")


def duration(exe: str, path: str) -> float:
    proc = subprocess.run([exe, "-i", path], capture_output=True, text=True)
    out = proc.stderr
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+)\.(\d+)", out)
    if not m:
        return 0.0
    h, mi, s, cs = m.groups()
    return int(h) * 3600 + int(mi) * 60 + int(s) + int(cs) / 100.0


def grab(exe: str, path: str, t: float, dest: str, width: int) -> bool:
    cmd = [
        exe, "-y", "-ss", f"{t:.2f}", "-i", path,
        "-frames:v", "1", "-vf", f"scale={width}:-2:flags=lanczos",
        "-q:v", "4", dest,
    ]
    return subprocess.run(cmd, capture_output=True).returncode == 0 and os.path.exists(dest)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-video", type=int, default=2)
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--no-update", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(SRC):
        sys.exit(f"ضع الفيديوهات في المجلد: {SRC}")

    videos = sorted(
        os.path.join(SRC, f) for f in os.listdir(SRC) if f.lower().endswith(VIDEO_EXT)
    )
    if not videos:
        sys.exit(f"لا توجد فيديوهات في {SRC} (الامتدادات المدعومة: {', '.join(VIDEO_EXT)})")

    os.makedirs(OUT, exist_ok=True)
    exe = ffmpeg()
    made = []

    for vi, vid in enumerate(videos, start=1):
        dur = duration(exe, vid) or 1.0
        for k in range(args.per_video):
            # نتجنب أول ثانية وآخر ثانية (انتقالات/شاشة سوداء)
            t = dur * (k + 1) / (args.per_video + 1)
            t = max(1.0, min(t, max(1.0, dur - 1.0)))
            dest = os.path.join(OUT, f"frame-{vi:02d}-{k + 1:02d}.jpg")
            if grab(exe, vid, t, dest, args.width):
                made.append({
                    "file": os.path.relpath(dest, ROOT),
                    "source": os.path.basename(vid),
                    "time": t,
                })
                print(f"✔ {dest}  ({t:.1f}s)")
            else:
                print(f"✘ فشل استخراج إطار من {vid} عند {t:.1f}s")

    meta = os.path.join(OUT, "frames.json")
    with open(meta, "w", encoding="utf-8") as fh:
        json.dump(made, fh, ensure_ascii=False, indent=2)
    print(f"\nتم إنشاء {len(made)} إطارًا. البيانات في {meta}")

    if args.no_update or not made:
        return

    # تحديث مصفوفة SLIDES في index.html: نضع الصور في أول الشرائح على الترتيب
    with open(INDEX, encoding="utf-8") as fh:
        html = fh.read()

    for i, item in enumerate(made):
        # نستبدل قيمة img في الشريحة رقم i
        pattern = re.compile(r"(const SLIDES = \[)(.*?)(\n\];)", re.S)
        m = pattern.search(html)
        if not m:
            print("⚠ لم أجد مصفوفة SLIDES في index.html — عدّل الصور يدويًا.")
            return
        block = m.group(2)
        entries = re.findall(r"\{tc:.*?\}", block, re.S)
        if i >= len(entries):
            break
        old = entries[i]
        new = re.sub(r"img:'[^']*'", f"img:'{item['file']}'", old)
        block = block.replace(old, new, 1)
        html = html[:m.start(2)] + block + html[m.end(2):]

    with open(INDEX, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("تم تحديث شريط التمرير في index.html بالصور الجديدة.")


if __name__ == "__main__":
    main()
