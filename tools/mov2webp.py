#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从带 alpha 的 mov 按动作切段，导出透明动画 WebP（浏览器 <img> 直接支持）。

用法:
  python tools/mov2webp.py                  # 全套动作
  python tools/mov2webp.py --name 01_站立说话
"""
import os
import sys
import subprocess
import tempfile
import argparse

import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MOV = r'D:\Code\bilibili-gb\成步堂_抠像.mov'
OUT_DIR = os.path.join(ROOT, 'assets', 'clips')
TMP = os.path.join(tempfile.gettempdir(), 'dshw_webp')

# 动作切段：(输出名, 起始秒, 结束秒)
SEGMENTS = [
    ('01_站立说话',  0.0, 3.0),
    ('02_拍桌喊话',  3.0, 6.3),
    ('03_手指前指控诉', 6.3, 9.2),
    ('04_双手扶腰说话', 9.2, 12.5),
    ('05_托腮思考一', 12.5, 15.2),
    ('06_举纸展示一', 15.2, 19.2),
    ('07_托腮思考二', 19.2, 23.3),
    ('08_举纸展示二', 23.3, 24.7),
    ('09_特写反应镜头', 24.7, 29.0),
]

# 输出参数
WIDTH = 320
FPS = 25          # 保持原始帧率（画质优先）
QUALITY = 90
METHOD = 6


def ffmpeg_exe():
    return imageio_ffmpeg.get_ffmpeg_exe()


def extract_alpha_frames(name, start, end, fps=FPS, width=WIDTH):
    """从 mov 切一段，导出带 alpha 的 PNG 帧序列。"""
    d = os.path.join(TMP, name)
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(d):
        if f.endswith('.png'):
            os.remove(os.path.join(d, f))
    ff = ffmpeg_exe()
    # 关键：-ss 定位，-t 时长，导出保留 prores 的 yuva444 alpha 到 PNG
    cmd = [
        ff, '-hide_banner', '-loglevel', 'error', '-y',
        '-ss', str(start), '-t', str(end - start),
        '-i', MOV,
        '-vf', f'scale={width}:-1:flags=lanczos,fps={fps}',
        '-vsync', '0',
        os.path.join(d, 'f%04d.png'),
    ]
    subprocess.run(cmd, check=True)
    files = [f for f in sorted(os.listdir(d)) if f.endswith('.png')]
    return d, files


def build_webp(name, start, end, fps=FPS, width=WIDTH, quality=QUALITY, method=METHOD):
    from PIL import Image
    d, files = extract_alpha_frames(name, start, end, fps, width)
    if len(files) < 2:
        print(f'  [skip] {name}: 只有 {len(files)} 帧')
        return None
    imgs = [Image.open(os.path.join(d, f)).convert('RGBA') for f in files]
    out = os.path.join(OUT_DIR, name + '.webp')
    duration = int(1000 / fps)
    imgs[0].save(
        out, format='WEBP', save_all=True, append_images=imgs[1:],
        duration=duration, loop=0, lossless=False, quality=quality, method=method,
    )
    size = os.path.getsize(out) / 1024.0
    print(f'  [ok] {name}.webp  {size:.1f} KB  frames={len(files)}  t={start}s-{end}s')
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', help='只转指定名称（不含扩展名）')
    args = ap.parse_args()
    os.makedirs(TMP, exist_ok=True)
    targets = [seg for seg in SEGMENTS if seg[0] == args.name] if args.name else SEGMENTS
    print(f'输出目录: {OUT_DIR}')
    print(f'参数: width={WIDTH} fps={FPS} quality={QUALITY}')
    for name, start, end in targets:
        try:
            build_webp(name, start, end)
        except Exception as e:
            print(f'  [err] {name}: {e}')


if __name__ == '__main__':
    main()
