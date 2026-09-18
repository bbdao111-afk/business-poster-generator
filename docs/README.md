# 中文海报艺术字选版 Demo

在线演示：[https://bbdao111-afk.github.io/business-poster-generator/](https://bbdao111-afk.github.io/business-poster-generator/)

页面分三段：

1. **两种输出风格对比** —— 产品宣传版（浅底 794×1123）与客户案例版（深底 1080×1440）实拍缩略图，两张都由 Skill 从示例 brief 直接渲染。
2. **路由判定器** —— 勾选你手上实际有的素材，按 `SKILL.md` 路由段的权重打分，实时给出会被导向哪一版；分差 ≤1 时明确提示"禁止自行选择，必须出编号选项让用户挑"。点风格卡片会把下方选版区切成该风格的默认主题与推荐组合。
3. **字体 × 效果选版** —— 9 款可商用中文展示字体 × 6 种纯 CSS 艺术字效果，实时切换大标题文案与字距。

支持深链分享状态：`?sigs=0,4`（预勾选信号）、`?style=case`（直接指定风格）。

- `index.html` —— 单文件演示页，无构建、无外部依赖、不联网加载任何资源
- `font_match.py` —— 按字形特征（字重/字宽/风格标签）为目标文案推荐展示字体
- `img/style-*.jpg` —— 两种风格的成品缩略图
- `fonts/*.woff2` —— **仅为网页演示制作的字形子集**（合计约 72KB），不用于排版输出

## 与仓库主体的关系

Skill 实际渲染海报时使用 `../art-type/fonts/` 下的**完整字体文件**（通过 `@font-face` 内嵌进输出 HTML），本目录的子集只服务于在线预览。两者的授权说明见 [../art-type/fonts/LICENSES.md](../art-type/fonts/LICENSES.md)。

## 本地运行

```bash
cd docs && python3 -m http.server 8000   # 打开 http://localhost:8000
```

## 文案与素材

演示文案「示例平台成为办公基座」「守住企业核心数据」均为自造中性文本，不指向任何真实公司、产品或客户。
