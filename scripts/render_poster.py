#!/usr/bin/env python3
"""Render a product or customer-case poster brief to editable HTML."""
from __future__ import annotations

import argparse, html, json, re
from pathlib import Path
from urllib.parse import quote

ART_DIR = Path(__file__).resolve().parent.parent / "art-type"
ART = json.loads((ART_DIR / "fonts.json").read_text(encoding="utf-8"))
FONTS = {f["id"]: f for f in ART["fonts"]}

LIGHT = dict(ink="#0c3f91", grad="linear-gradient(120deg,#0c3f91 10%,#00aeef 55%,#72be2d 95%)", hl="#72be2d",
             stroke="#0c3f91", fill="#ffffff", x_face="#0c3f91", x_e="#7a94b5", k_c="#0c3f91", k_s="#72be2d")
DARK = dict(ink="#ffffff", grad="linear-gradient(120deg,#6ec4ff 10%,#7ef0d0 55%,#ffd75e 95%)", hl="#00d98b",
            stroke="#56dfff", fill="#00102e", x_face="#ffffff", x_e="#0a2e5e", k_c="#ffffff", k_s="#00aeef")

def fx_css(fx: str, p: dict) -> str:
    if fx == "gradient":
        return f"background-image:{p['grad']};-webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:none;font-style:normal"
    if fx == "plain":
        return f"color:{p['ink']};text-shadow:none;font-style:normal"
    if fx == "stroke":
        return f"paint-order:stroke fill;-webkit-text-stroke:2px {p['stroke']};color:{p['fill']};text-shadow:none;font-style:normal"
    if fx == "extrude":
        layers = ",".join(f"{i}px {i}px 0 {p['x_e']}" for i in range(1, 7))
        return f"color:{p['x_face']};text-shadow:{layers},8px 9px 14px rgba(7,30,63,.28);font-style:normal"
    if fx == "tech-shadow":
        return ("color:#f4fbff;font-style:normal;"
                "text-shadow:0 2px 0 #b9efff,0 5px 0 #148fe8,0 8px 0 #064bba,"
                "0 0 18px rgba(0,170,255,.42)!important")
    if fx == "tech-shadow-light":
        # 浅底版：深蓝→青 渐变填充 + 分层挤出阴影，保证在白底上依然醒目（阴影偏移收紧，避免"重影"发虚）
        return ("font-style:normal;background-image:linear-gradient(102deg,#04225c 0%,#0c3f91 38%,#0a72cf 74%,#0292dd 100%);"
                "-webkit-background-clip:text;background-clip:text;color:transparent;"
                "text-shadow:0 2px 0 #0a72cf,0 4px 0 #083a7d,0 9px 18px rgba(6,42,107,.30)!important")
    if fx == "block-tech":
        # 斜切渐变色块 + 反白标题：颜色体系由「蓝绿色块」承载，字纯白，清晰度最高
        return ("font-style:normal;display:inline-block;max-width:100%;transform:skewX(-7deg);"
                "padding:9px 34px 11px 24px;margin-left:6px;"
                "clip-path:polygon(0 0,100% 0,calc(100% - 20px) 100%,0 100%);"
                "background:linear-gradient(96deg,#062a6b 0%,#0c3f91 44%,#0a7fd0 100%);"
                "border-left:8px solid #72be2d;color:#fff;"
                "text-shadow:0 2px 8px rgba(2,26,66,.42);box-shadow:0 12px 26px rgba(6,42,107,.30)")
    if fx == "dual-tone":
        # 双色分阶 + 压印高光：深墨蓝主词 + 品牌绿关键词，零模糊阴影
        return ("font-style:normal;color:#0a3a7b;"
                "text-shadow:0 2px 0 rgba(255,255,255,.78),0 -1px 1px rgba(4,34,92,.22)")
    if fx == "outline-mix":
        # 空心描边 + 实心关键词：描边字不参与填充，完全消除糊字
        return ("font-style:normal;paint-order:stroke fill;-webkit-text-stroke:2.4px #0a3a7b;color:#fff;"
                "text-shadow:0 3px 0 rgba(12,63,145,.16)")
    if fx == "neon":
        return "color:#fff;text-shadow:0 0 5px #fff,0 0 12px #00c3ff,0 0 26px #008dff,0 0 52px #0057ff"
    if fx == "skew":
        return (f"display:inline-block;transform:skewX(-8deg);color:{p['k_c']};"
                f"text-shadow:4px 4px 0 {p['k_s']},7px 7px 14px rgba(9,42,88,.28)")
    return f"color:{p['ink']}"

def art_css(d: dict, dark: bool) -> str:
    """@font-face + 大标题字体/效果 CSS，供 h1 与 .customer 使用。"""
    f = FONTS.get(d.get("title_font") or ART["default"]) or FONTS[ART["default"]]
    fx = d.get("title_effect") or "plain"
    fmt = "truetype" if f["file"].endswith(".ttf") else "opentype"
    src = "file://" + quote(str((ART_DIR / "fonts" / f["file"]).resolve()))
    face = f"@font-face{{font-family:'{f['family']}';src:url('{src}') format('{fmt}')}}"
    base = (f"font-family:'{f['family']}','PingFang SC','Microsoft YaHei',sans-serif;"
            f"font-weight:{f['weight']};font-style:normal;letter-spacing:{f['letter_spacing']};"
            f"text-rendering:geometricPrecision;-webkit-font-smoothing:antialiased")
    p_hl = (DARK if dark else LIGHT)["hl"]
    rule = f".poster h1.h1art,.poster .customer.h1art{{{base};{fx_css(fx, DARK if dark else LIGHT)};--hl:{p_hl}}}"
    hl_rule = ".poster h1.h1art .hl{color:var(--hl)}"
    if fx == "tech-shadow":
        hl_rule += ".poster h1.h1art .hl{color:#00e5aa;text-shadow:0 2px 0 #7effe2,0 5px 0 #00a9d6,0 8px 0 #0063ae,0 0 15px rgba(0,230,170,.38)}"
    if fx == "tech-shadow-light":
        hl_rule += (".poster h1.h1art .hl{background-image:linear-gradient(100deg,#63d23a,#0f9d18);"
                    "-webkit-background-clip:text;background-clip:text;color:transparent;"
                    "text-shadow:0 2px 0 #4fa312,0 4px 0 #2f7a08}")
    if fx == "block-tech":
        hl_rule += ".poster h1.h1art .hl{color:#7ef3b0;text-shadow:0 2px 8px rgba(2,26,66,.5)}"
    if fx == "dual-tone":
        hl_rule += ".poster h1.h1art .hl{color:#4fa312;text-shadow:0 2px 0 rgba(255,255,255,.78),0 -1px 1px rgba(4,34,92,.22)}"
    if fx == "outline-mix":
        hl_rule += ".poster h1.h1art .hl{-webkit-text-stroke:0;color:#0a3a7b;text-shadow:none}"
    if fx in {"tech-shadow", "extrude", "neon", "tech-shadow-light"}:
        rule += ".poster h1.h1art:after{content:'';display:block;height:3px;width:70%;margin:12px auto 0;background:linear-gradient(90deg,transparent,#00e9ff 22%,#00dca4 65%,transparent);box-shadow:0 0 12px #00cfff;border-radius:50%}"
    if fx == "tech-shadow":
        rule += ".poster h1.h1art{color:#f4fbff!important;text-shadow:0 2px 0 #b9efff,0 5px 0 #148fe8,0 8px 0 #064bba,0 0 18px rgba(0,170,255,.42)!important}.poster h1.h1art .hl{color:#00e5aa!important;text-shadow:0 2px 0 #7effe2,0 5px 0 #00a9d6,0 8px 0 #0063ae,0 0 15px rgba(0,230,170,.38)!important}"
    if fx == "tech-shadow-light":
        rule += (".poster h1.h1art{background-image:linear-gradient(102deg,#04225c 0%,#0c3f91 38%,#0a72cf 74%,#0292dd 100%)!important;"
                 "-webkit-background-clip:text!important;background-clip:text!important;color:transparent!important;"
                 "text-shadow:0 2px 0 #0a72cf,0 4px 0 #083a7d,0 9px 18px rgba(6,42,107,.30)!important}"
                 ".poster h1.h1art .hl{background-image:linear-gradient(100deg,#63d23a,#0f9d18)!important;-webkit-background-clip:text!important;background-clip:text!important;color:transparent!important;text-shadow:0 2px 0 #4fa312,0 4px 0 #2f7a08!important}")
    return face + rule + hl_rule

def e(v): return html.escape(str(v or ""))
def rich(v):
    """标题文案渲染：{片段} 转为高亮 span，换行转为 <br>。"""
    s = re.sub(r"\{([^{}]+)\}", r'<span class="hl">\1</span>', e(v))
    return s.replace("\n", "<br>")
def url(v):
    if not v: return ""
    s = str(v)
    return s if s.startswith(("data:", "http://", "https://", "file://")) else "file://" + quote(str(Path(s).expanduser().resolve()))

BASE = "*{box-sizing:border-box}html,body{margin:0;background:#111;font-family:'PingFang SC','Microsoft YaHei',sans-serif}.poster{position:relative;overflow:hidden}.logo{max-height:56px;max-width:240px;object-fit:contain}"

def product(d):
    metrics = "".join(f'<div class="metric"><b>{e(x.get("value"))}</b><span>{e(x.get("label"))}</span><small>{e(x.get("note"))}</small></div>' for x in d.get("metrics",[])[:4])
    groups = d.get("metric_groups") or []
    if groups:
        cards = []
        for g in groups[:2]:
            rows = []
            for i, it in enumerate(g.get("items", [])[:2]):
                if i:
                    rows.append('<i class="msplit"></i>')
                rows.append(f'<div class="mrow"><b>{e(it.get("value"))}</b><span>{e(it.get("label"))}</span></div>')
            cap = f'<em class="cap">{e(g.get("cap"))}</em>' if g.get("cap") else ''
            cards.append(f'<div class="mgroup">{cap}{"".join(rows)}</div>')
        metrics_html = f'<div class="metrics2">{"".join(cards)}</div>'
    else:
        metrics_html = f'<div class="metrics">{metrics}</div>'
    highlights = "".join(f"<li>{e(x)}</li>" for x in d.get("highlights",[])[:4])

    def sec(x, i):
        pts = "".join(f"<li>{e(p)}</li>" for p in x.get("points", [])[:3])
        inner = f'<ul class="pts">{pts}</ul>' if pts else f'<p>{e(x.get("body"))}</p>'
        return f'<section><b class="num">{i:02d}</b><h2>{e(x.get("title"))}</h2>{inner}</section>'

    sections = "".join(sec(x, i) for i, x in enumerate(d.get("sections", [])[:4], 1))
    pkg = d.get("package_table")
    if pkg:
        cols = pkg.get("columns") or ["组成", "套餐物料", "关键能力"]
        head = "".join(f"<span>{e(c)}</span>" for c in cols[:3])
        rows = []
        for i, r in enumerate(pkg.get("rows", [])[:3], 1):
            pts = "".join(f"<li>{e(p)}</li>" for p in r.get("points", [])[:4])
            rows.append(f'<div class="pkg-r">'
                        f'<div class="pkg-c1"><b class="pn"><i>{i:02d}</i>{e(r.get("name"))}</b></div>'
                        f'<div class="pkg-c2">{e(r.get("material"))}</div>'
                        f'<div class="pkg-c3"><ul class="pkg-pts">{pts}</ul></div></div>')
        foot = f'<div class="pkg-f">{e(pkg.get("footer"))}</div>' if pkg.get("footer") else ''
        pkg_html = (f'<div class="pkg-title">{e(pkg.get("title") or "套餐内容")}</div>'
                    f'<div class="pkg"><div class="pkg-h">{head}</div>{"".join(rows)}{foot}</div>')
    else:
        pkg_html = ""
    logo, hero = url(d.get("logo")), url(d.get("hero_image"))
    company_logo = url(d.get("company_logo"))
    product_screens = url(d.get("product_screens"))
    screens = d.get("screens") or []
    css = BASE + art_css(d, dark=False) + """
.poster{width:794px;height:1123px;padding:56px 40px 0;color:#18344f;background:linear-gradient(160deg,#ffffff 0%,#f3f9fc 46%,#e5f0f7 100%);display:flex;flex-direction:column}
.poster:before{content:'';position:absolute;z-index:0;left:-5%;top:-42px;width:110%;height:98px;background:linear-gradient(96deg,#062a6b,#0c3f91 44%,#0a72cf);transform:rotate(2deg);border-bottom:8px solid #72be2d}
.poster .bg-grid{position:absolute;z-index:0;inset:0;opacity:.75;background-image:linear-gradient(rgba(12,63,145,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(12,63,145,.05) 1px,transparent 1px);background-size:28px 28px;-webkit-mask-image:linear-gradient(#000 55%,transparent 88%);mask-image:linear-gradient(#000 55%,transparent 88%)}
.content{position:relative;z-index:2;flex:1;display:flex;flex-direction:column;min-height:0}
.brand{height:52px;display:flex;align-items:center;justify-content:space-between}
.brand img{max-height:46px;max-width:330px;object-fit:contain;background:#fff;padding:5px 12px;border-radius:6px;box-shadow:0 6px 18px rgba(12,63,145,.16)}
.brand-text{font-weight:900;color:#0c3f91;font-size:22px}.brand-badge{font-size:13px;font-weight:900;color:#fff;letter-spacing:.06em;background:linear-gradient(100deg,#0a72cf,#00aeef);padding:7px 14px;border-radius:20px;box-shadow:0 6px 16px rgba(10,114,207,.32)}
h1{font-size:50px;line-height:1.04;margin:8px 0 0;max-width:660px}.poster h1.h1art:after{width:196px;margin:12px 0 0;background:linear-gradient(90deg,#72be2d,#00aeef 62%,transparent);box-shadow:none;border-radius:0}
.subtitle{font-size:25px;font-weight:900;color:#0c3f91;margin:12px 0 10px;border-bottom:3px solid #72be2d;padding-bottom:8px;letter-spacing:.01em}.subtitle .hl{color:#e8442f}
.intro{font-size:15.5px;line-height:1.5;margin:0 0 11px;max-width:706px;color:#2c4a66}
.highlights{margin:0 0 13px;padding:0;list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:7px 16px}.highlights li:before{content:'✓';color:#72be2d;font-weight:900;margin-right:7px}.highlights li{font-size:14.5px;font-weight:700;color:#1c4265}
.metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:9px;margin:0 0 14px}.metric{background:#fff;border-top:4px solid #0c3f91;padding:12px 9px;box-shadow:0 8px 22px rgba(23,59,92,.11);border-radius:0 0 7px 7px}.metric b{display:block;font-size:26px;line-height:1.05;color:#0a72cf;letter-spacing:-.01em}.metric span{display:block;font-size:13px;font-weight:900;margin-top:5px;color:#18344f}.metric small{display:block;font-size:11px;margin-top:3px;color:#63778b;line-height:1.3}
.metrics2{display:grid;grid-template-columns:1fr 1fr;gap:13px;margin:0 0 15px}
.mgroup{position:relative;overflow:hidden;border-radius:10px;padding:19px 15px 15px;display:flex;align-items:center;gap:0;box-shadow:0 12px 26px rgba(23,59,92,.22)}
.mgroup:nth-child(1){background:linear-gradient(122deg,#08306f 0%,#0c55a8 56%,#0891c8 100%)}
.mgroup:nth-child(2){background:linear-gradient(122deg,#3f8a10 0%,#5cae24 58%,#78cc3c 100%)}
.mgroup:before{content:'';position:absolute;right:-26px;top:-34px;width:118px;height:118px;border-radius:50%;background:rgba(255,255,255,.11)}
.mgroup:after{content:'';position:absolute;right:26px;bottom:-46px;width:74px;height:74px;border-radius:50%;background:rgba(255,255,255,.08)}
.mgroup .cap{position:absolute;z-index:2;left:15px;top:7px;font-style:normal;font-size:10.5px;font-weight:900;letter-spacing:.1em;color:rgba(255,255,255,.72)}
.mrow{position:relative;z-index:1;flex:1 1 0;min-width:0;padding-top:6px}
.mrow b{display:block;font-size:28px;line-height:1;color:#fff;letter-spacing:-.02em;font-weight:900}
.mrow span{display:block;font-size:12.5px;font-weight:700;margin-top:6px;color:rgba(255,255,255,.86);letter-spacing:.01em;white-space:nowrap}
.msplit{position:relative;z-index:1;flex:0 0 auto;width:1px;margin:6px 13px 0;align-self:stretch;background:rgba(255,255,255,.34)}
.strip{margin:0 0 15px}.product-strip-label{color:#0c3f91;font-size:15px;font-weight:900;margin:0 0 9px;border-left:6px solid #72be2d;padding-left:9px;letter-spacing:.01em}
.screens{display:grid;grid-template-columns:repeat(4,1fr);gap:9px}.screens figure{margin:0;background:#fff;border:1px solid #9ccce9;border-radius:8px;overflow:hidden;box-shadow:0 8px 20px rgba(23,59,92,.11)}.screens img{display:block;width:100%;height:auto}.screens figcaption{background:linear-gradient(96deg,#72be2d,#4fa312);color:#fff;font-size:12px;font-weight:900;text-align:center;padding:6px 2px;letter-spacing:.01em}
.product-screens{display:block;width:100%;height:auto;border:1px solid #9ccce9;border-radius:8px;background:#fff;box-shadow:0 8px 20px rgba(23,59,92,.10)}
.pkg-title{color:#0c3f91;font-size:15px;font-weight:900;margin:0 0 9px;border-left:6px solid #72be2d;padding-left:9px;letter-spacing:.01em}
.pkg{flex:1;display:grid;grid-template-rows:auto 1fr 1fr auto;border:1px solid #c3d6e2;border-radius:9px;overflow:hidden;background:#fff;box-shadow:0 10px 24px rgba(23,59,92,.09)}
.pkg-h{display:grid;grid-template-columns:130px 176px 1fr;gap:11px;padding:9px 13px;background:linear-gradient(96deg,#08306f,#0c55a8 70%,#0891c8);color:#fff;font-size:12.5px;font-weight:900;letter-spacing:.03em}
.pkg-r{display:grid;grid-template-columns:130px 176px 1fr;gap:11px;padding:13px;border-top:1px solid #dae5ed;align-items:stretch}
.pkg-c1{display:flex;align-items:flex-start}.pn{font-size:17px;font-weight:900;color:#0c3f91;line-height:1.3;letter-spacing:.01em}.pn i{display:block;font-style:normal;font-size:11px;font-weight:900;letter-spacing:.08em;color:#fff;background:#0c55a8;width:30px;height:18px;line-height:18px;text-align:center;border-radius:9px;margin-bottom:6px}
.pkg-c2{font-size:13px;font-weight:700;color:#1c4265;line-height:1.6;display:flex;align-items:center}
.pkg-c3{display:flex;align-items:center}.pkg-pts{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:7px;width:100%}.pkg-pts li{position:relative;padding-left:15px;font-size:14px;line-height:1.5;color:#31556f}.pkg-pts li:before{content:'';position:absolute;left:1px;top:9px;width:5px;height:5px;background:#72be2d;border-radius:50%}
.pkg-f{padding:8px 13px;background:#f1f8fc;border-top:1px solid #dae5ed;font-size:10.5px;line-height:1.45;color:#4d6d88;letter-spacing:.01em}
.sections{flex:1;display:grid;grid-template-columns:1fr 1fr;grid-auto-rows:1fr;gap:10px;min-height:0}.sections section{position:relative;background:#fff;border:1px solid #c3d6e2;border-left:5px solid #72be2d;padding:15px 16px 14px;display:flex;flex-direction:column;gap:8px;border-radius:0 8px 8px 0;box-shadow:0 8px 20px rgba(23,59,92,.07)}.sections .num{position:absolute;right:14px;top:10px;font-size:27px;font-weight:900;color:#e3eef5;letter-spacing:-.02em}.sections h2{margin:0;font-size:18px;color:#0c3f91;letter-spacing:.01em}.sections p{margin:0;font-size:14.5px;line-height:1.55;color:#31556f}.pts{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:6px;flex:1;justify-content:center}.pts li{position:relative;padding-left:16px;font-size:14px;line-height:1.5;color:#31556f}.pts li:before{content:'';position:absolute;left:2px;top:8px;width:6px;height:6px;background:#0a72cf;border-radius:50%}
.cta{position:relative;z-index:2;margin:16px -40px 0;padding:15px 40px 17px;background:linear-gradient(96deg,#062a6b,#0c3f91 46%,#0a72cf);color:#fff;border-top:7px solid #72be2d;display:flex;flex-direction:column;gap:5px}
.cta-main{font-size:17px;font-weight:900;letter-spacing:.02em}.cta-note{font-size:11px;line-height:1.45;color:#bcd8ee}
.cta-legal{margin-top:1px;font-size:10.5px;line-height:1.4;color:#93bcdf;text-align:right;letter-spacing:.01em}
.hero{position:absolute;right:25px;top:78px;width:245px;height:190px;object-fit:contain;opacity:.15}
"""
    brand = f'<img class="logo" src="{logo}">' if logo else f'<span class="brand-text">{e(d.get("brand"))}</span>'
    company_tag = f'<img class="logo" src="{company_logo}">' if company_logo else brand
    badge = f'<span class="brand-badge">{e(d.get("badge") or "Q4 冲刺套餐")}</span>'
    hero_tag = f'<img class="hero" src="{hero}">' if hero else ""
    if screens:
        cells = "".join(f'<figure><img src="{url(s.get("img"))}"><figcaption>{e(s.get("label"))}</figcaption></figure>' for s in screens[:4])
        screens_tag = (f'<div class="strip"><div class="product-strip-label">{e(d.get("screens_label") or "产品界面实拍")}</div>'
                       f'<div class="screens">{cells}</div></div>')
    elif product_screens:
        screens_tag = (f'<div class="strip"><div class="product-strip-label">{e(d.get("screens_label") or "产品能力一览")}</div>'
                       f'<img class="product-screens" src="{product_screens}"></div>')
    else:
        screens_tag = ''
    cta_main = e(d.get("cta") or "Q4 冲刺 · AI 桌面云能力限时下放")
    legal = f'<span class="cta-legal">{e(d.get("price_note"))}</span>' if d.get("price_note") else ''
    cta = f'<div class="cta"><span class="cta-main">{cta_main}</span><span class="cta-note">{e(d.get("source_note"))}</span>{legal}</div>'
    body = (f'<div class="poster"><div class="bg-grid"></div><div class="content">'
            f'<div class="brand">{company_tag}{badge}</div>'
            f'<h1 class="h1art">{rich(d.get("title"))}</h1>'
            f'<div class="subtitle">{rich(d.get("subtitle"))}</div>'
            f'<p class="intro">{e(d.get("intro"))}</p><ul class="highlights">{highlights}</ul>'
            f'{metrics_html}{screens_tag}{pkg_html}'
            f'{"" if pkg_html else f"<div class=sections>{sections}</div>"}'
            f'</div>{hero_tag}{cta}</div>')
    return css, body

def case(d):
    solutions = "".join(f'<div class="solution"><b>{e(x.get("name"))}</b><span>{e(x.get("value"))}</span></div>' for x in d.get("solutions",[])[:2])
    results = d.get("results") or []
    results_html = "".join(
        f'<div class="result"><b>{e(x.get("value"))}</b><span>{e(x.get("label"))}</span>'
        f'<small>{e(x.get("note"))}</small></div>' for x in results[:3])
    results_block = (f'<div class="results">{results_html}</div>' if results_html else "")
    customer_logo, vendor_logo, hero, qr = map(url, [d.get("customer_logo"),d.get("vendor_logo"),d.get("hero_image"),d.get("qr_image")])
    css = BASE + art_css(d, dark=True) + """
.poster{width:1080px;height:1440px;padding:54px 52px;color:white;background:#001337;isolation:isolate}.poster:before{content:'';position:absolute;inset:0;z-index:-4;background:radial-gradient(ellipse at 15% 12%,#0754c5 0,transparent 38%),radial-gradient(ellipse at 85% 42%,#063d96 0,transparent 34%),linear-gradient(155deg,#063f9e 0,#00183f 38%,#000d25 100%)}.poster:after{content:'';position:absolute;left:-8%;right:-8%;top:245px;height:270px;z-index:-3;background:radial-gradient(ellipse at 52% 50%,rgba(0,174,255,.28),transparent 58%),linear-gradient(164deg,transparent 35%,rgba(0,188,255,.12) 48%,transparent 57%);transform:rotate(-7deg)}.content{position:relative;z-index:4}.brands{height:86px;display:flex;align-items:center;gap:20px}.brands img{max-height:60px;max-width:250px;object-fit:contain;background:#fff;padding:7px 12px;border-radius:6px}.divider{height:55px;width:2px;background:#9bb8dc}.brand-text{font-weight:800;font-size:28px}
.poster .tech-grid{position:absolute;z-index:-2;left:-5%;right:-5%;top:430px;height:610px;opacity:.32;background:repeating-linear-gradient(8deg,transparent 0 9px,rgba(72,183,255,.22) 10px,transparent 11px),repeating-linear-gradient(98deg,transparent 0 13px,rgba(72,183,255,.16) 14px,transparent 15px);transform:perspective(500px) rotateX(48deg) scale(1.25)}.poster .energy-line{position:absolute;z-index:1;left:7%;right:7%;top:370px;height:120px;border-top:2px solid rgba(0,218,255,.8);border-radius:50%;transform:rotate(-7deg);box-shadow:0 -7px 18px rgba(0,174,255,.6),0 -18px 32px rgba(0,174,255,.22)}.poster .energy-line:after{content:'';position:absolute;left:18%;right:22%;top:18px;height:1px;background:#00e6ff;box-shadow:0 0 13px 4px rgba(0,219,255,.7)}.poster .energy-line:before{content:'';position:absolute;left:61%;top:9px;width:9px;height:9px;background:#d8ffff;border:2px solid #00dfff;border-radius:50%;box-shadow:0 0 8px 4px #00cfff,180px 38px 0 -2px #baffff,180px 38px 0 0 #00dfff,180px 38px 10px 3px #00cfff}
h1{margin:28px auto 58px;text-align:center;font-size:70px;line-height:1.15;letter-spacing:inherit}.poster h1.h1art{font-style:normal;text-shadow:0 2px 0 #b9efff,0 5px 0 #148fe8,0 8px 0 #064bba,0 0 18px rgba(0,170,255,.48)}.poster h1.h1art .hl{color:#00e5aa;text-shadow:0 2px 0 #7effe2,0 5px 0 #00a9d6,0 8px 0 #0063ae,0 0 15px rgba(0,230,170,.42)}.poster h1.h1art:after{content:'';display:block;height:3px;width:70%;margin:12px auto 0;background:linear-gradient(90deg,transparent,#00e9ff 22%,#00dca4 65%,transparent);box-shadow:0 0 12px #00cfff;border-radius:50%}.solutions{display:flex;justify-content:center;gap:28px;min-height:155px}.solution{width:46%;padding:32px 18px 18px;text-align:center;background:linear-gradient(135deg,rgba(5,71,160,.88),rgba(2,26,78,.88));border:2px solid #00aefc;box-shadow:0 0 18px #008cff inset,0 0 14px #008cff;position:relative;min-height:142px;border-radius:8px}.solution:after{content:'';position:absolute;inset:0;border:1px solid rgba(115,226,255,.45);border-radius:8px;pointer-events:none}.solution b{position:absolute;top:-22px;left:50%;transform:translateX(-50%);min-width:170px;padding:8px 24px;background:#057bdd;clip-path:polygon(12% 0,88% 0,100% 50%,88% 100%,12% 100%,0 50%);font-size:24px;line-height:1.1}.solution span{font-size:22px;line-height:1.35;display:block;padding-top:4px}
.hero{position:absolute;z-index:0;left:0;top:470px;width:100%;height:570px;object-fit:cover;filter:saturate(.86) contrast(1.08)}.hero-shade{position:absolute;z-index:1;left:0;right:0;top:440px;height:640px;background:radial-gradient(ellipse at 50% 34%,transparent 0 32%,rgba(0,13,42,.12) 58%,rgba(0,12,38,.72) 100%),linear-gradient(#00183f 0%,transparent 18%,transparent 65%,#00225e 100%)}.hero-light{position:absolute;z-index:1;left:8%;right:8%;top:570px;height:270px;background:radial-gradient(ellipse,rgba(0,205,255,.28),transparent 65%);mix-blend-mode:screen;pointer-events:none}.story{position:absolute;z-index:3;left:50px;right:50px;bottom:48px;min-height:390px;padding:30px 40px;background:linear-gradient(135deg,rgba(8,65,145,.92),rgba(2,31,91,.93));border:2px solid #18a9ff;box-shadow:0 0 22px #008cff inset,0 0 16px #008cff;clip-path:polygon(2% 0,98% 0,100% 7%,100% 100%,0 100%,0 7%)}.story:before{content:'';position:absolute;inset:7px;z-index:-1;border:1px solid rgba(91,223,255,.45);clip-path:polygon(2% 0,98% 0,100% 7%,100% 100%,0 100%,0 7%)}
.results{position:absolute;z-index:2;left:52px;right:52px;top:712px;display:flex;gap:22px}.result{flex:1 1 0;min-width:0;padding:20px 22px 18px;background:linear-gradient(150deg,rgba(3,32,84,.9),rgba(0,12,38,.94));border:2px solid rgba(0,200,255,.72);box-shadow:0 0 16px rgba(0,140,255,.55),0 0 22px rgba(0,140,255,.22) inset;clip-path:polygon(0 0,100% 0,100% 78%,94% 100%,0 100%);display:flex;flex-direction:column;gap:2px}.result b{font-size:52px;line-height:1;font-weight:900;color:#fff;text-shadow:0 0 14px rgba(0,220,255,.75)}.result span{font-size:23px;font-weight:700;color:#00e5aa;margin-top:6px}.result small{font-size:16px;color:#8fb6dd;line-height:1.35}.customer{font-size:70px;line-height:1;font-weight:900;margin-bottom:22px}.customer:after{content:'';display:block;width:180px;height:12px;margin-top:-5px;background:linear-gradient(90deg,#00d98b,transparent)}.position{font-size:31px;color:#00d98b;font-weight:800;padding-bottom:18px;border-bottom:1px dashed #12a7e4}.summary{max-width:730px;font-size:25px;line-height:1.65;margin:20px 0 0}.qr{position:absolute;width:170px;height:170px;right:36px;bottom:36px;background:white;padding:10px;border:4px solid #56dfff}.qr-placeholder{position:absolute;right:36px;bottom:36px;width:170px;height:170px;border:3px dashed #56dfff;display:grid;place-items:center;text-align:center;color:#7feaff}
"""
    left = f'<img src="{customer_logo}">' if customer_logo else f'<span class="brand-text">{e(d.get("customer"))}</span>'
    right = f'<img src="{vendor_logo}">' if vendor_logo else f'<span class="brand-text">{e(d.get("brand"))}</span>'
    hero_tag = f'<img class="hero" src="{hero}">' if hero else ""
    qr_tag = f'<img class="qr" src="{qr}">' if qr else '<div class="qr-placeholder">二维码<br>待提供</div>'
    campaign = rich(d.get("campaign"))
    body = f'<div class="poster"><div class="tech-grid"></div><div class="energy-line"></div><div class="content"><div class="brands">{left}<i class="divider"></i>{right}</div><h1 class="h1art">{campaign}</h1><div class="solutions">{solutions}</div></div>{hero_tag}<div class="hero-shade"></div><div class="hero-light"></div>{results_block}<div class="story"><div class="customer h1art">{e(d.get("customer"))}</div><div class="position">{e(d.get("customer_position"))}</div><p class="summary">{e(d.get("summary"))}</p>{qr_tag}</div></div>'
    return css, body

def main():
    p=argparse.ArgumentParser(); p.add_argument("brief",type=Path); p.add_argument("--output",type=Path,required=True); a=p.parse_args()
    d=json.loads(a.brief.read_text(encoding="utf-8"))
    if d.get("type") not in {"product","case"}: raise SystemExit("brief.type must be 'product' or 'case'")
    css,body=product(d) if d["type"]=="product" else case(d)
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><style>{css}</style></head><body>{body}</body></html>',encoding="utf-8"); print(a.output.resolve())
if __name__=="__main__": main()
