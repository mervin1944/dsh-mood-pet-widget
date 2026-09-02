#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
webm -> gif 转换工具（dsh-mood-pet-widget）
用 imageio-ffmpeg 自带的 ffmpeg 二进制，不依赖系统安装。
参数可调以控制体积/质量：
  --width   输出 GIF 宽度 px（默认 240，成步堂角色够用）
  --fps     帧率（默认 15）
  --colors  调色板颜色数（默认 128，越低越小）
用法:
  python tools/webm2gif.py                        # 转全部 9 个
  python tools/webm2gif.py --name 01_站立说话      # 只转一个
"""
import os
import sys
import argparse
import subprocess
import tempfile

import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC_DIR = os.path.join(ROOT, 'assets', 'clips')
OUT_DIR = SRC_DIR  # 输出到同一目录，格式 .gif，与 .webm 共存

ALL = [
    '01_站立说话', '02_拍桌喊话', '03_手指前指控诉', '04_双手扶腰说话',
    '05_托腮思考一', '06_举纸展示一', '07_托腮思考二', '08_举纸展示二',
    '09_特写反应镜头',
]


def ffmpeg_exe():
    return imageio_ffmpeg.get_ffmpeg_exe()


def convert(name, width, fps, colors):
    src = os.path.join(SRC_DIR, name + '.webm')
    out = os.path.join(OUT_DIR, name + '.gif')
    if not os.path.exists(src):
        print('  [skip] 不存在: ' + src)
        return None
    ff = ffmpeg_exe()
    # 两遍法：先出调色板（提升质量），再合成 gif
    palette = os.path.join(tempfile.gettempdir(), 'dshw_palette.png')
    # 第一遍：生成调色板
    pal_cmd = [
        ff, '-hide_banner', '-loglevel', 'error', '-y',
        '-i', src,
        '-vf', f'fps={fps},scale={width}:-1:flags=lanczos,palettegen=stats_mode=diff',
        palette,
    ]
    subprocess.run(pal_cmd, check=True)
    # 第二遍：合成 gif
    gif_cmd = [
        ff, '-hide_banner', '-loglevel', 'error', '-y',
        '-i', src,
        '-i', palette,
        '-lavfi', f'fps={fps},scale={width}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3',
        '-loop', '0',
        out,
    ]
    subprocess.run(gif_cmd, check=True)
    size = os.path.getsize(out) / 1024.0
    print(f'  [ok] {name}.gif  {size:.1f} KB  (w={width}, fps={fps}, colors={colors})')
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', help='只转指定名称（不含扩展名）')
    ap.add_argument('--width', type=int, default=240)
    ap.add_argument('--fps', type=int, default=15)
    ap.add_argument('--colors', type=int, default=128)
    args = ap.parse_args()

    targets = [args.name] if args.name else ALL
    print(f'源目录: {SRC_DIR}')
    print(f'转换 {len(targets)} 个 -> GIF (width={args.width}, fps={args.fps})')
    for name in targets:
        try:
            convert(name, args.width, args.fps, args.colors)
        except Exception as e:
            print(f'  [err] {name}: {e}')


if __name__ == '__main__':
    main()
