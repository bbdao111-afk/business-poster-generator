#!/usr/bin/env python3
"""标题字体反查：从既有海报里识别大标题用的是哪款字体。

原理：裁出标题文字 → 二值化取字形掩码 → 用候选字体渲染同文案并扫描倾斜角 → 按 IoU 相似度排序。

用法:
  python3 match_font.py <海报图片> --text "标题文案" [--box L,T,R,B] [--json]

  --box 可选，指定标题所在的像素区域（默认自动扫描上半部分最高的白色文字带）
  --json 输出机器可读结果

示例:
  python3 match_font.py ../../目标-案例宣传/image\\ 6.jpg --text "守住企业核心数据"

依赖: pillow, numpy
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_FONT_DIR = HERE.parent / "fonts"
REGISTRY = HERE.parent / "fonts.json"

def extract_mask(img, box, white_min=170):
    import numpy as np
    from PIL import Image
    im = img.convert("RGB")
    crop = im.crop(box) if box else im.crop((0, 0, im.width, int(im.height * 0.40)))
    a = np.array(crop)
    mask = (a[:, :, 0] > white_min) & (a[:, :, 1] > white_min) & (a[:, :, 2] > white_min)
    rows = mask.sum(axis=1)
    if rows.max() == 0:
        sys.exit("未在指定区域找到白色文字，请用 --box 指定标题区域")
    bands, start, prev = [], None, None
    for r in np.where(rows > max(20, rows.max() * 0.1))[0]:
        if start is None:
            start = prev = r
        elif r - prev <= 4:
            prev = r
        else:
            bands.append((start, prev)); start = prev = r
    bands.append((start, prev))
    b0, b1 = max(bands, key=lambda b: b[1] - b[0])
    m = mask[b0:b1 + 1]
    cols = np.where(m.sum(axis=0) > 0)[0]
    m = m[:, cols[0]:cols[-1] + 1]
    return Image.fromarray((m * 255).astype("uint8"))

def render(font_path, text, size=300, shear=0.0):
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    font = ImageFont.truetype(str(font_path), size)
    img = Image.new("L", (size * len(text) + 200, size * 2), 0)
    ImageDraw.Draw(img).text((100, size * 0.4), text, font=font, fill=255)
    if shear:
        img = img.transform(img.size, Image.AFFINE, (1, shear, 0, 0, 1, 0))
    arr = np.array(img) > 128
    ys, xs = np.where(arr)
    if len(ys) == 0:
        return None
    arr = arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    return Image.fromarray((arr * 255).astype("uint8"))

def iou(target_img, cand_img):
    import numpy as np
    from PIL import Image
    T = np.array(target_img) > 128
    h = target_img.size[1]
    w = max(1, int(cand_img.size[0] * h / cand_img.size[1]))
    C = np.array(cand_img.resize((w, h), Image.LANCZOS)) > 128
    W = max(C.shape[1], T.shape[1])
    def put(mask, width, xoff=0):
        out = np.zeros((T.shape[0], width), bool)
        sx, dx = max(0, -xoff), max(0, xoff)
        w2 = min(mask.shape[1] - sx, width - dx)
        if w2 > 0:
            out[:, dx:dx + w2] = mask[:, sx:sx + w2]
        return out
    Tc, best = put(T, W), 0.0
    span = max(2, int(W * 0.03))
    for xoff in range(-span, span + 1, 2):
        Cc = put(C, W, xoff)
        best = max(best, (Tc & Cc).sum() / max(1, (Tc | Cc).sum()))
    return best

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image", type=Path)
    ap.add_argument("--text", required=True, help="标题文案（第一行）")
    ap.add_argument("--box", help="标题区域 L,T,R,B（像素）")
    ap.add_argument("--font-dir", type=Path, default=DEFAULT_FONT_DIR)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    from PIL import Image
    box = tuple(int(x) for x in a.box.split(",")) if a.box else None
    target = extract_mask(Image.open(a.image), box)

    names = {}
    if REGISTRY.exists():
        reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
        names = {f["file"]: f["name"] for f in reg["fonts"]}

    results = []
    for fp in sorted(a.font_dir.glob("*")):
        if fp.suffix.lower() not in {".ttf", ".otf", ".ttc"}:
            continue
        best, best_s = 0.0, 0.0
        for s in [round(x * 0.02, 2) for x in range(0, 11)]:
            img = render(fp, a.text, shear=s)
            if img is None:
                continue
            v = iou(target, img)
            if v > best:
                best, best_s = v, s
        if best:
            results.append({"file": fp.name, "name": names.get(fp.name, fp.stem), "iou": round(best, 3), "shear": best_s})
    results.sort(key=lambda r: -r["iou"])

    if a.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"标题区掩码: {target.size[0]}x{target.size[1]}  文案: {a.text}\n")
        print(f'{"字体":<22}{"IoU":<8}{"建议斜切"}')
        for r in results:
            bar = "█" * int(r["iou"] * 40)
            print(f'{r["name"]:<22}{r["iou"]:<8.3f}{r["shear"]:<8.2f}{bar}')
        if results:
            top = results[0]
            print(f'\n最接近: {top["name"]}（IoU {top["iou"]}，斜切 {top["shear"]}）')
            print('若需更高还原度，对该字体补 skewX 或用 --box 缩小标题区域后重测。')

if __name__ == "__main__":
    main()
