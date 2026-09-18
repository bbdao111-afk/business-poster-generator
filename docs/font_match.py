#!/usr/bin/env python3
"""Font matcher: compare poster title glyph against candidate fonts by IoU."""
from PIL import Image, ImageDraw, ImageFont
import numpy as np, os, sys

PY_ROOT = '/Users/dinger/aiclaude/生成海报的SKill'
SRC = f'{PY_ROOT}/art-type-demo/src'
TEXT = '守住企业核心数据'

# 1. extract target title mask (line 1, white text) — 按 1080x1440 原图坐标精确裁切
im = Image.open(f'{PY_ROOT}/目标-案例宣传/image 6.jpg').convert('RGB')
crop = im.crop((150, 165, 960, 290))   # 第一行「守住企业核心数据」
a = np.array(crop)
white = (a[:,:,0]>170)&(a[:,:,1]>170)&(a[:,:,2]>170)
rows = white.sum(axis=1)
th = max(20, rows.max()*0.1)
band_rows = np.where(rows>th)[0]
bands, start, prev = [], None, None
for r in band_rows:
    if start is None: start=prev=r
    elif r-prev<=4: prev=r
    else: bands.append((start,prev)); start=prev=r
bands.append((start,prev))
b0, b1 = max(bands, key=lambda b: b[1]-b[0])
m = white[b0:b1+1]
cols = np.where(m.sum(axis=0)>0)[0]
m = m[:, cols[0]:cols[-1]+1]
target = Image.fromarray((m*255).astype(np.uint8))
m = white[b0:b1+1]
cols = np.where(m.sum(axis=0)>0)[0]
m = m[:, cols[0]:cols[-1]+1]
target = Image.fromarray((m*255).astype(np.uint8))
T = np.array(target)>0
print(f'目标标题区: 行 {b0}-{b1}, bbox {target.size[0]}x{target.size[1]}, 宽高比 {target.size[0]/target.size[1]:.2f}')

# 2. candidates
FONTS = [
    ('得意黑 Oblique',      f'{SRC}/SmileySans-Oblique.ttf', True),
    ('斗鱼追光体 2.0',      f'{SRC}/douyu-zgt.ttf',          True),
    ('庞门正道标题体',      f'{SRC}/pangmen.ttf',            False),
    ('站酷高端黑',          f'{SRC}/gaoduanhei.ttf',         False),
    ('优设标题黑',          f'{SRC}/youshe.ttf',             False),
    ('阿里妈妈数黑体',      f'{SRC}/alimama-shuhei.ttf',     False),
    ('锐字真言体',          f'{SRC}/ruizi.ttf',              False),
    ('思源黑体 Heavy(基线)', f'{SRC}/SourceHanSansSC-Heavy.otf', False),
    ('站酷庆科黄油体(对照)', f'{SRC}/zcool.ttf',             False),
]

def render(path, size=300, shear=0.0):
    font = ImageFont.truetype(path, size)
    img = Image.new('L', (size*len(TEXT)+200, size*2), 0)
    d = ImageDraw.Draw(img)
    d.text((100, size*0.4), TEXT, font=font, fill=255)
    if shear:
        img = img.transform(img.size, Image.AFFINE, (1, shear, 0, 0, 1, 0))
    arr = np.array(img)>128
    ys, xs = np.where(arr)
    arr = arr[ys.min():ys.max()+1, xs.min():xs.max()+1]
    return Image.fromarray((arr*255).astype(np.uint8))

def iou(cand_img):
    ch = target.size[1]
    w = max(1, int(cand_img.size[0]*ch/cand_img.size[1]))
    c = cand_img.resize((w, ch), Image.LANCZOS)
    C = np.array(c)>128
    W = max(C.shape[1], T.shape[1])
    def put(mask, width, xoff=0):
        out = np.zeros((T.shape[0], width), bool)
        src_x = max(0, -xoff); dst_x = max(0, xoff)
        w2 = min(mask.shape[1]-src_x, width-dst_x)
        if w2 > 0:
            out[:, dst_x:dst_x+w2] = mask[:, src_x:src_x+w2]
        return out
    best = 0
    Tc = put(T, W)
    for xoff in range(-int(W*0.05), int(W*0.05)+1, 2):
        Cc = put(C, W, xoff)
        inter = (Tc & Cc).sum(); union = (Tc | Cc).sum()
        best = max(best, inter/max(1,union))
    return best

results = []
for name, path, native_slant in FONTS:
    if not os.path.exists(path): continue
    shears = [0.0, 0.06, 0.09, 0.12, 0.15, 0.18] if not native_slant else [0.0, 0.03, 0.06, 0.09]
    best, best_s = 0, 0
    ar = 0
    for s in shears:
        img = render(path, shear=s)
        v = iou(img)
        if v > best: best, best_s, ar = v, s, img.size[0]/img.size[1]
    results.append((best, name, best_s, ar))

print(f'\n{"字体":<18}{"最佳IoU":<10}{"需补斜切":<10}{"宽高比":<8}')
for v, name, s, ar in sorted(results, reverse=True):
    print(f'{name:<18}{v:.3f}      {s:.2f}      {ar:.2f}')
