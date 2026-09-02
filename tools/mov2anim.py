#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从带 alpha 的 mov 按动作切段，导出透明 APNG 动画（dsh-mood-pet-widget）。

用法:
  python tools/mov2anim.py            # 全套动作
"""
import os
import subprocess
import tempfile

import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MOV = r'D:\Code\bilibili-gb\成步堂_抠像.mov'
OUT_DIR = os.path.join(ROOT, 'assets', 'clips')
TMP = os.path.join(tempfile.gettempdir(), 'dshw_anim')

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
# 输出帧参数
WIDTH = 240
FPS = 15


def ffmpeg_exe():
    return imageio_ffmpeg.get_ffmpeg_exe()


def extract_alpha_frames(name, start, end, fps=FPS, width=WIDTH):
    """用 ffmpeg 从 mov 切一段，导出带 alpha 的 PNG 帧序列。"""
    d = os.path.join(TMP, name)
    os.makedirs(d, exist_ok=True)
    # 清空旧帧
    for f in os.listdir(d):
        if f.endswith('.png'):
            os.remove(os.path.join(d, f))
    ff = ffmpeg_exe()
    # -ss/-t 先定位再解码（关键帧准确），保留 alpha（prores yuva444 -> png RGBA）
    cmd = [
        ff, '-hide_banner', '-loglevel', 'error', '-y',
        '-ss', str(start), '-t', str(end - start),
        '-i', MOV,
        '-vf', f'scale={width}:-1:flags=lanczos',
        '-vsync', '0',
        os.path.join(d, 'f%04d.png'),
    ]
    subprocess.run(cmd, check=True)
    frames = sorted(os.listdir(d))
    for f in list(frames):
        full = os.path.join(d, f)
        if not os.path.exists(full):
            frames.remove(f)
    return d, len([f for f in os.listdir(d) if f.endswith('.png')])


def build_apng(name, start, end, fps=FPS, width=WIDTH):
    from PIL import Image
    d, count = extract_alpha_frames(name, start, end, fps, width)
    if count < 2:
        print(f'  [skip] {name}: 只有 {count} 帧')
        return None
    files = sorted(os.listdir(d))
    files = [f for f in files if f.endswith('.png')]
    imgs = [Image.open(os.path.join(d, f)).convert('RGBA') for f in files]
    out = os.path.join(OUT_DIR, name + '.png')  # APNG 用 .png 扩展名，浏览器识别
    imgs[0].save(
        out, format='PNG', save_all=True, append_images=imgs[1:],
        duration=int(1000 / fps), loop=0, disposal=2, blend=0, optimize=False,
    )
    size = os.path.getsize(out) / 1024.0
    print(f'  [ok] {name}.png (APNG)  {size:.1f} KB  frames={count}  t={start}s-{end}s')
    return out


def main():
    os.makedirs(TMP, exist_ok=True)
    print(f'输出目录: {OUT_DIR}')
    for name, start, end in SEGMENTS:
        try:
            build_apng(name, start, end)
        except Exception as e:
            print(f'  [err] {name}: {e}')


if __name__ == '__main__':
    main()
