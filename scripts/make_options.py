#!/usr/bin/env python3
"""生成「方案选版册」：多条大标题候选 ×（字体 × 效果）在同一主题下的渲染预览。

用于流程第二步：把候选做成**可编号的渲染卡片**交给用户选择，
避免只给文字描述。用户选定编号后，再进入第三步渲染成品。

用法:
  python3 make_options.py --output <目录> --theme light \
      --option "AI 助手-{Q4冲刺套餐}|sans|block-tech" \
      --option "{AI 助手}-Q4冲刺套餐|pangmen|dual-tone"

--option 格式: 标题文案|字体id|效果id
  标题中用 {} 标记要分色的关键词。
--theme: light（产品版浅底）或 dark（案例版深底）
--title: 方案册标题，默认「大标题方案选版」
--note:  顶部提示语

产出: <目录>/options.html — 编号卡片 + 选择提示 + 可复制的 brief 字段
依赖: 无（直接引用 art-type/fonts 下的完整字体文件）
"""
from __future__ import annotations

import argparse, html, json
from pathlib import Path
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
ART = HERE.parent / "art-type"
REGISTRY = ART / "fonts.json"

# 浅底 / 深底两套具体配色（与 render_poster.py 的 LIGHT / DARK 保持一致）
LIGHT_BG = "linear-gradient(160deg,#ffffff 0%,#f3f9fc 46%,#e5f0f7 100%)"
DARK_BG = "linear-gradient(155deg,#063f9e 0%,#00183f 38%,#000d25 100%)"

FX = {
    "plain": "color:#0c3f91",
    "gradient": ("background-image:linear-gradient(120deg,#0c3f91 10%,#00aeef 55%,#72be2d 95%);"
                 "-webkit-background-clip:text;background-clip:text;color:transparent"),
    "dual-tone": "color:#0a3a7b;text-shadow:0 2px 0 rgba(255,255,255,.78),0 -1px 1px rgba(4,34,92,.22)",
    "stroke": "paint-order:stroke fill;-webkit-text-stroke:2px #0c3f91;color:#ffffff",
    "outline-mix": "paint-order:stroke fill;-webkit-text-stroke:2.4px #0a3a7b;color:#fff;text-shadow:0 3px 0 rgba(12,63,145,.16)",
    "block-tech": ("display:inline-block;max-width:100%;transform:skewX(-7deg);"
                   "padding:9px 34px 11px 24px;margin-left:8px;"
                   "clip-path:polygon(0 0,100% 0,calc(100% - 20px) 100%,0 100%);"
                   "background:linear-gradient(96deg,#062a6b 0%,#0c3f91 44%,#0a7fd0 100%);"
                   "border-left:8px solid #72be2d;color:#fff;"
                   "text-shadow:0 2px 8px rgba(2,26,66,.42);box-shadow:0 12px 26px rgba(6,42,107,.30)"),
    "extrude": ("color:#0c3f91;text-shadow:1px 1px 0 #7a94b5,2px 2px 0 #7a94b5,3px 3px 0 #7a94b5,"
                "4px 4px 0 #7a94b5,5px 5px 0 #7a94b5,6px 6px 0 #7a94b5"),
    "tech-shadow": ("color:#f4fbff;text-shadow:0 2px 0 #b9efff,0 5px 0 #148fe8,0 8px 0 #064bba,"
                    "0 0 18px rgba(0,170,255,.42)"),
    "tech-shadow-light": ("background-image:linear-gradient(102deg,#04225c 0%,#0c3f91 38%,#0a72cf 74%,#0292dd 100%);"
                          "-webkit-background-clip:text;background-clip:text;color:transparent;"
                          "text-shadow:0 2px 0 #0a72cf,0 4px 0 #083a7d,0 9px 18px rgba(6,42,107,.30)"),
    "neon": "color:#fff;text-shadow:0 0 5px #fff,0 0 12px #00c3ff,0 0 26px #008dff,0 0 52px #0057ff",
    "skew": "display:inline-block;transform:skewX(-8deg);color:#0c3f91;text-shadow:4px 4px 0 #72be2d,7px 7px 14px rgba(9,42,88,.28)",
}

FX_HL = {
    "block-tech": "color:#7ef3b0",
    "dual-tone": "color:#4fa312",
    "outline-mix": "-webkit-text-stroke:0;color:#0a3a7b;text-shadow:none",
    "tech-shadow": "color:#00e5aa",
    "neon": "color:#00d98b",
    "skew": "color:#4fa312",
}

FX_NAME = {
    "plain": "纯净大字", "gradient": "渐变填充", "dual-tone": "双色分阶压印",
    "stroke": "双层描边", "outline-mix": "空心描边混排", "block-tech": "斜切渐变块反白",
    "extrude": "立体挤出", "tech-shadow": "科技主题阴影", "tech-shadow-light": "科技主题阴影（浅底）",
    "neon": "霓虹发光", "skew": "斜切冲击",
}


def rich(s: str) -> str:
    out = html.escape(s)
    out = out.replace("{", "\x01").replace("}", "\x02")
    return out.replace("\x01", '<span class="hl">').replace("\x02", "</span>")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--theme", choices=["light", "dark"], default="light")
    ap.add_argument("--option", action="append", required=True,
                    help='文案|字体id|效果id，可重复；文案中用 {} 标记分色关键词')
    ap.add_argument("--title", default="大标题方案选版")
    ap.add_argument("--note", default="请回复编号确认；未确认前不会生成成品海报。")
    a = ap.parse_args()

    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    fonts = {f["id"]: f for f in reg["fonts"]}
    out = a.output.resolve()
    out.mkdir(parents=True, exist_ok=True)

    faces, cards = [], []
    for i, spec in enumerate(a.option, 1):
        parts = spec.split("|")
        if len(parts) != 3:
            raise SystemExit(f"--option 格式应为 文案|字体id|效果id，收到：{spec}")
        text, fid, fxid = parts[0], parts[1], parts[2]
        f = fonts.get(fid)
        if not f:
            raise SystemExit(f"未知字体 id: {fid}（可选：{', '.join(fonts)}）")
        if fxid not in FX:
            raise SystemExit(f"未知效果 id: {fxid}（可选：{', '.join(FX)}）")

        src = (ART / "fonts" / f["file"]).resolve()
        fmt = "truetype" if f["file"].endswith(".ttf") else "opentype"
        faces.append(f"@font-face{{font-family:'{f['family']}';src:url('file://{quote(str(src))}') format('{fmt}')}}")
        style = (f"font-family:'{f['family']}';letter-spacing:{f['letter_spacing']};"
                 f"font-weight:{f['weight']}")
        hl = FX_HL.get(fxid, "color:#72be2d")
        cards.append(f'''<div class="card">
  <div class="idx"><b>{i:02d}</b><span>{f['name']} × {FX_NAME.get(fxid, fxid)}</span></div>
  <style>.opt{i} .t{{{FX[fxid]}}}.opt{i} .t .hl{{{hl}}}</style>
  <div class="cell opt{i}"><span class="t" style="{style}">{rich(text)}</span></div>
  <div class="meta">
    <code>title</code> = {html.escape(text)}<br>
    <code>title_font</code> = "{fid}"　<code>title_effect</code> = "{fxid}"
  </div>
</div>''')

    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><style>
{"".join(faces)}
*{{box-sizing:border-box}}html,body{{margin:0}}
body{{width:1000px;background:#fff;font-family:'PingFang SC','Microsoft YaHei',sans-serif;padding:24px 26px 28px}}
h1{{font-size:19px;margin:0 0 4px;color:#0c3f91}}
p.note{{margin:0 0 18px;font-size:12.5px;color:#63778b;line-height:1.6}}
.card{{border:1px solid #dbe6ee;border-radius:10px;padding:14px 16px 12px;margin-bottom:13px;background:#fff}}
.idx{{display:flex;align-items:baseline;gap:11px;margin-bottom:9px}}
.idx b{{font-size:19px;color:#0c3f91}}.idx span{{font-size:12.5px;color:#7d93a6;font-weight:600}}
.cell{{border-radius:9px;padding:13px 18px;min-height:82px;display:flex;align-items:center;overflow:hidden;
 background:{LIGHT_BG if a.theme == "light" else DARK_BG}}}
.t{{font-size:50px;line-height:1.06;white-space:nowrap;text-rendering:geometricPrecision;-webkit-font-smoothing:antialiased}}
.meta{{margin-top:10px;font-size:11.5px;line-height:1.7;color:#4d6d88;background:#f4f8fb;border-radius:6px;padding:7px 10px}}
code{{background:#e6eef5;border-radius:3px;padding:1px 5px;font-size:11px}}
footer{{margin-top:22px;font-size:12px;color:#63778b;line-height:1.8;border-top:1px solid #dbe6ee;padding-top:12px}}
</style></head><body>
<h1>{html.escape(a.title)}</h1>
<p class="note">{html.escape(a.note)}</p>
{"".join(cards)}
<footer>主题：{'浅底（产品版）' if a.theme == 'light' else '深底（案例版）'}　·　
标题里的 {{}} 为分色关键词　·　
需要横向比较 9 款字体 × 11 种效果时，另跑 <code>art-type/scripts/make_select_page.py</code></footer>
</body></html>'''
    target = out / "options.html"
    target.write_text(page, encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
