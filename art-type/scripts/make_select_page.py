#!/usr/bin/env python3
"""大字选版页生成器：给定海报标题文案，子集化全部展示字体并输出可交互选版 HTML。

用法:
  python3 make_select_page.py "示例平台成为办公基座" --output /path/to/out

产出:
  <output>/select.html    可交互选版页（9 字体 × 6 效果，默认 优设标题黑 × 纯净大字）
  <output>/fonts/*.woff2  按文案子集化的字体

依赖: fonttools + brotli（pip install fonttools brotli）
"""
from __future__ import annotations
import argparse, json, html
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTRY = HERE.parent / "fonts.json"

def subset_font(src: Path, dst: Path, text: str):
    from fontTools import subset
    opt = subset.Options()
    opt.flavor = "woff2"
    opt.hinting = False
    opt.layout_features = ["*"]
    font = subset.load_font(str(src), opt)
    ss = subset.Subsetter(opt)
    ss.populate(text=text)
    ss.subset(font)
    subset.save_font(font, str(dst), opt)

PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>大字选版 · __TEXT__</title>
<style>
__FONTFACES__
*{box-sizing:border-box}
:root{--bg:#f6f8fa;--card:#fff;--text:#1e2b3a;--muted:#63778b;--line:#dfe7ee;--accent:#0c3f91;
 --ink:#0c3f91;--grad:linear-gradient(120deg,#0c3f91 10%,#00aeef 55%,#72be2d 95%);
 --stroke:#0c3f91;--fill:#fff;--x-face:#0c3f91;--x-e:#7a94b5;--k-c:#0c3f91;--k-s:#72be2d}
body[data-theme="dark"]{--bg:#08182f;--card:#0e2445;--text:#e8f1fa;--muted:#8fa8c4;--line:#1c3a63;
 --ink:#fff;--grad:linear-gradient(120deg,#6ec4ff 10%,#7ef0d0 55%,#ffd75e 95%);
 --stroke:#56dfff;--fill:#08182f;--x-face:#7fd4ff;--x-e:#0a2e5e;--k-c:#fff;--k-s:#00aeef}
body{margin:0;background:var(--bg);color:var(--text);font-family:'PingFang SC','Microsoft YaHei',sans-serif;transition:background .25s}
.wrap{max-width:1080px;margin:0 auto;padding:32px 26px 56px}
header h1{font-size:22px;font-weight:700;margin:0 0 6px}
header p{margin:0;color:var(--muted);font-size:13.5px;line-height:1.7}
.row{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:22px 0 12px}
.chip{padding:8px 15px;border:1px solid var(--line);border-radius:999px;background:var(--card);
 color:var(--text);font-size:13.5px;cursor:pointer;user-select:none}
.chip.on{background:var(--accent);border-color:var(--accent);color:#fff}
body[data-theme="dark"] .chip.on{background:#00aeef;border-color:#00aeef;color:#062033}
.spacer{flex:1}
.tbtn{padding:8px 15px;border:1px solid var(--line);border-radius:999px;background:var(--card);color:var(--text);font-size:13.5px;cursor:pointer}
.hero{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:46px 24px;text-align:center;position:relative;overflow:hidden}
.hero .cap{position:absolute;top:14px;left:18px;font-size:12px;color:var(--muted)}
.hero .sample{font-size:clamp(40px,8.6vw,100px);line-height:1.1;font-weight:900}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:16px;margin-top:20px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px 20px 18px;cursor:pointer;position:relative;transition:all .15s}
.card:hover{transform:translateY(-2px);border-color:var(--accent)}
.card.on{border-color:var(--accent);box-shadow:0 0 0 2px rgba(12,63,145,.18)}
.card .sample{font-size:clamp(24px,3.9vw,40px);line-height:1.16;font-weight:900;min-height:3.4em;overflow-wrap:anywhere;text-rendering:geometricPrecision;-webkit-font-smoothing:antialiased}
.card .meta{display:flex;align-items:baseline;gap:10px;margin-top:16px;padding-top:12px;border-top:1px dashed var(--line)}
.card .name{font-size:14px;font-weight:600}
.card .tag{font-size:12px;color:var(--muted)}
.badge{position:absolute;top:10px;right:10px;font-size:11px;color:#fff;background:#c0392b;padding:2px 9px;border-radius:999px}
.fx-plain{color:var(--ink)}
.fx-plain{color:var(--ink);text-shadow:none;font-style:normal}
.fx-gradient{background-image:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:none;font-style:normal}
.fx-stroke{paint-order:stroke fill;-webkit-text-stroke:2px var(--stroke);color:var(--fill);text-shadow:none;font-style:normal}
.fx-extrude{color:var(--x-face);text-shadow:1px 1px 0 var(--x-e),2px 2px 0 var(--x-e),3px 3px 0 var(--x-e),4px 4px 0 var(--x-e),5px 5px 0 var(--x-e),6px 6px 0 var(--x-e);font-style:normal}
.fx-tech-shadow{color:#f4fbff;font-style:normal;text-shadow:0 2px 0 #b9efff,0 5px 0 #148fe8,0 8px 0 #064bba,0 0 18px rgba(0,170,255,.42)}
.fx-tech-shadow .hl{color:#00e5aa}
.fx-tech-shadow-light{font-style:normal;background-image:linear-gradient(102deg,#04225c 0%,#0c3f91 38%,#0a72cf 74%,#0292dd 100%);-webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:0 2px 0 #0a72cf,0 4px 0 #083a7d,0 9px 18px rgba(6,42,107,.30)}
.fx-tech-shadow-light .hl{background-image:linear-gradient(100deg,#63d23a,#0f9d18);-webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:0 2px 0 #4fa312,0 4px 0 #2f7a08}
.fx-block-tech{font-style:normal;display:inline-block;max-width:100%;transform:skewX(-7deg);padding:6px 24px 8px 16px;clip-path:polygon(0 0,100% 0,calc(100% - 14px) 100%,0 100%);background:linear-gradient(96deg,#062a6b 0%,#0c3f91 44%,#0a7fd0 100%);border-left:7px solid #72be2d;color:#fff;text-shadow:0 2px 8px rgba(2,26,66,.42)}
.fx-block-tech .hl{color:#7ef3b0}
.fx-dual-tone{font-style:normal;color:#0a3a7b;text-shadow:0 2px 0 rgba(255,255,255,.78),0 -1px 1px rgba(4,34,92,.22)}
.fx-dual-tone .hl{color:#4fa312;text-shadow:0 2px 0 rgba(255,255,255,.78),0 -1px 1px rgba(4,34,92,.22)}
.fx-outline-mix{font-style:normal;paint-order:stroke fill;-webkit-text-stroke:2.4px #0a3a7b;color:#fff;text-shadow:0 3px 0 rgba(12,63,145,.16)}
.fx-outline-mix .hl{-webkit-text-stroke:0;color:#0a3a7b;text-shadow:none}
.fx-neon{color:#fff;text-shadow:0 0 5px #fff,0 0 12px #00c3ff,0 0 26px #008dff,0 0 52px #0057ff}
.fx-skew{display:inline-block;transform:skewX(-8deg);color:var(--k-c);text-shadow:4px 4px 0 var(--k-s),7px 7px 14px rgba(9,42,88,.28)}
footer{margin-top:30px;font-size:12px;color:var(--muted);line-height:1.9;border-top:1px solid var(--line);padding-top:14px}
.pick{margin-top:16px;background:var(--card);border:1px dashed var(--accent);border-radius:10px;padding:12px 16px;font-size:14px}
.pick b{color:var(--accent)}
</style>
</head>
<body data-theme="light">
<div class="wrap">
<header>
  <h1>海报大标题选版</h1>
  <p>文案：<b>__TEXT__</b> · 点击效果与字体卡片对比，选定后将所选组合告知助手即可继续渲染成品海报。</p>
</header>
<div class="row" id="fxTabs"></div>
<div class="row" style="margin-top:-4px"><button class="tbtn" id="themeBtn">切换 明/暗 背景</button></div>
<div class="hero"><div class="cap" id="heroCap"></div><div class="sample" id="heroSample"></div></div>
<div class="grid" id="grid"></div>
<div class="pick" id="pick"></div>
<footer>字体全部免费商用，清单与授权见 art-type/fonts/LICENSES.md。字距已按字体分别配置（超宽字体正字距防笔画粘连）。</footer>
</div>
<script>
const TEXT='__TEXT__';
const FONTS=__FONTS__;
const EFFECTS=__EFFECTS__;
let curFx='__DEFAULT_FX__',curFont='__DEFAULT__';
function rich(s){return s.replace(/\\{([^{}]+)\\}/g,'<span class="hl">$1</span>')}
const fxTabs=document.getElementById('fxTabs');
EFFECTS.forEach(fx=>{const b=document.createElement('button');b.className='chip';b.textContent=fx.name;b.dataset.fx=fx.id;
 b.onclick=()=>{curFx=fx.id;if(fx.prefer==='dark'&&document.body.dataset.theme!=='dark')setTheme('dark');render()};fxTabs.appendChild(b)});
const grid=document.getElementById('grid');
FONTS.forEach(f=>{const c=document.createElement('div');c.className='card';c.dataset.font=f.id;
 const badge=f.badge?`<span class="badge">${f.badge}</span>`:'';
 c.innerHTML=badge+`<div class="sample fx-${curFx}" style="font-family:'${f.family}';letter-spacing:${f.ls};font-weight:${f.weight}">${rich(TEXT)}</div>
 <div class="meta"><span class="name">${f.name}</span><span class="tag">${f.tag}</span></div>`;
 c.onclick=()=>{curFont=f.id;render()};grid.appendChild(c)});
document.getElementById('themeBtn').onclick=()=>setTheme(document.body.dataset.theme==='light'?'dark':'light');
function setTheme(t){document.body.dataset.theme=t;render()}
function render(){
 document.querySelectorAll('#fxTabs .chip').forEach(b=>b.classList.toggle('on',b.dataset.fx===curFx));
 document.querySelectorAll('.card').forEach(c=>{c.classList.toggle('on',c.dataset.font===curFont);
  const s=c.querySelector('.sample');s.className='sample fx-'+curFx;s.innerHTML=rich(TEXT)});
 const f=FONTS.find(x=>x.id===curFont),fx=EFFECTS.find(x=>x.id===curFx);
 const h=document.getElementById('heroSample');
 h.className='sample fx-'+curFx;h.style.fontFamily="'"+f.family+"'";h.style.letterSpacing=f.ls;h.style.fontWeight=f.weight;
 h.innerHTML=rich(TEXT);
 document.getElementById('heroCap').textContent=f.name+' × '+fx.name;
 document.getElementById('pick').innerHTML='当前选择：<b>'+f.name+'</b> × <b>'+fx.name+'</b>（brief 字段：<code>title_font="'+f.id+'", title_effect="'+fx.id+'"</code>）';
}
render();
</script>
</body>
</html>
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text", help="海报大标题文案，可用 {关键词} 标记参与分色的片段")
    ap.add_argument("--output", type=Path, required=True, help="输出目录")
    ap.add_argument("--default-fx", default=None, help="打开页面时默认选中的效果 id，默认取注册表中第一个")
    a = ap.parse_args()

    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    out = a.output.resolve(); out.mkdir(parents=True, exist_ok=True)
    (out / "fonts").mkdir(parents=True, exist_ok=True)
    default_fx = a.default_fx or (reg["effects"][0]["id"] if reg.get("effects") else "plain")

    text = a.text.strip()
    fonts_js, faces = [], []
    for f in reg["fonts"]:
        src = HERE.parent / "fonts" / f["file"]
        dst = out / "fonts" / (f["id"] + ".woff2")
        try:
            subset_font(src, dst, text)
            from fontTools.ttLib import TTFont
            cmap = TTFont(str(dst)).getBestCmap()
            if not all(ord(c) in cmap for c in text):
                print(f"[跳过] {f['name']}: 缺少文案所需字形")
                continue
        except Exception as e:
            print(f"[跳过] {f['name']}: {e}")
            continue
        faces.append(f"@font-face{{font-family:'{f['family']}';src:url('fonts/{f['id']}.woff2') format('woff2');font-display:swap}}")
        entry = {"id": f["id"], "name": f["name"], "family": f["family"], "ls": f["letter_spacing"], "weight": f["weight"], "tag": f["tag"]}
        if f["id"] == reg["default"]:
            entry["badge"] = "★ 默认推荐"
        fonts_js.append(entry)

    page = (PAGE.replace("__TEXT__", html.escape(text))
               .replace("__FONTFACES__", "\n".join(faces))
               .replace("__FONTS__", json.dumps(fonts_js, ensure_ascii=False))
               .replace("__EFFECTS__", json.dumps(reg["effects"], ensure_ascii=False))
               .replace("__DEFAULT__", reg["default"])
               .replace("__DEFAULT_FX__", default_fx))
    (out / "select.html").write_text(page, encoding="utf-8")
    print((out / "select.html").resolve())

if __name__ == "__main__":
    main()
