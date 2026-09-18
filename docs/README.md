# 中文海报艺术字选版 Demo

在线演示：[https://bbdao111-afk.github.io/business-poster-generator/](https://bbdao111-afk.github.io/business-poster-generator/)

9 款可商用中文展示字体 × 6 种纯 CSS 艺术字效果，实时切换大标题文案与字距，用于在真正渲染海报之前"看着图选方案"。

- `index.html` —— 单文件演示页，无构建、无外部依赖、不联网加载任何资源
- `font_match.py` —— 按字形特征（字重/字宽/风格标签）为目标文案推荐展示字体
- `fonts/*.woff2` —— **仅为网页演示制作的字形子集**（合计约 72KB），不用于排版输出

## 与仓库主体的关系

Skill 实际渲染海报时使用 `../art-type/fonts/` 下的**完整字体文件**（通过 `@font-face` 内嵌进输出 HTML），本目录的子集只服务于在线预览。两者的授权说明见 [../art-type/fonts/LICENSES.md](../art-type/fonts/LICENSES.md)。

## 本地运行

```bash
cd docs && python3 -m http.server 8000   # 打开 http://localhost:8000
```

## 文案与素材

演示文案「示例平台成为办公基座」「守住企业核心数据」均为自造中性文本，不指向任何真实公司、产品或客户。
