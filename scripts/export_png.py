#!/usr/bin/env python3
"""把渲染好的海报 HTML 导出为指定 DPI 的 PNG。

海报 CSS 里的像素尺寸按 96 DPI 书写（产品版 794×1123 ≈ A4，案例版 1080×1440）。
本脚本按 `--dpi` 计算缩放倍数，用无头 Chromium 以放大后的设备像素比截图，
得到可直接送印的高清 PNG（默认 300 DPI）。

用法:
  python3 export_png.py poster.html --output poster@300.png --dpi 300
  python3 export_png.py poster.html --output poster.png           # 96 DPI 快速预览
  python3 export_png.py poster.html --output poster.png --chrome /path/to/chrome-headless-shell

可选: --width / --height 覆盖默认画布尺寸（产品版默认 794×1123）。
"""
from __future__ import annotations

import argparse, shutil, subprocess, sys
from pathlib import Path

# 常见无头 Chromium 位置（Playwright 缓存 → 系统 Chrome → PATH）
CANDIDATES = [
    Path.home() / "Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell",
    Path.home() / "Library/Caches/ms-playwright/chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium",
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
]


def find_chrome(explicit: str | None = None) -> Path:
    if explicit:
        p = Path(explicit).expanduser()
        if p.exists():
            return p
        raise SystemExit(f"未找到指定的浏览器: {p}")
    for pat in CANDIDATES:
        hits = sorted(Path(pat.parent).glob(pat.name)) if "*" in pat.parts[-1] else [pat]
        for h in hits:
            if h.exists():
                return h
    w = shutil.which("chrome-headless-shell") or shutil.which("chromium") or shutil.which("google-chrome")
    if w:
        return Path(w)
    raise SystemExit("未找到无头 Chromium，请用 --chrome 指定，或安装 playwright 的 chromium")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html", type=Path, help="render_poster.py 生成的 HTML")
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--dpi", type=int, default=300, help="目标 DPI，默认 300（96 为快速预览）")
    ap.add_argument("--width", type=int, default=794, help="画布 CSS 宽度，产品版默认 794")
    ap.add_argument("--height", type=int, default=1123, help="画布 CSS 高度，产品版默认 1123")
    ap.add_argument("--chrome", default=None, help="无头浏览器可执行文件路径")
    ap.add_argument("--wait", type=int, default=6000, help="渲染等待毫秒，字体较大时可调高")
    a = ap.parse_args()

    src = a.html.expanduser().resolve()
    if not src.exists():
        raise SystemExit(f"找不到 HTML: {src}")
    out = a.output.expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    chrome = find_chrome(a.chrome)
    scale = max(a.dpi / 96.0, 1.0)
    px_w, px_h = round(a.width * scale), round(a.height * scale)

    cmd = [
        str(chrome),
        "--headless",
        "--no-sandbox", "--disable-gpu", "--disable-gpu-compositing",
        "--use-angle=swiftshader", "--disable-software-rasterizer",
        "--hide-scrollbars",
        f"--force-device-scale-factor={scale:.4f}",
        f"--window-size={a.width},{a.height}",
        f"--screenshot={out}",
        f"--virtual-time-budget={a.wait}",
        f"file://{src}",
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=180)
    except subprocess.CalledProcessError as ex:
        sys.stderr.write(ex.stderr.decode("utf-8", "ignore"))
        raise SystemExit("截图失败")

    if not out.exists():
        raise SystemExit("截图失败：未生成文件")

    try:
        from PIL import Image
        with Image.open(out) as im:
            print(f"{out}  ({im.width}×{im.height}px, {a.dpi} DPI, {im.width/a.width:.2f}x)")
    except Exception:
        print(f"{out}  (目标 {px_w}×{px_h}px @{a.dpi} DPI)")


if __name__ == "__main__":
    main()
