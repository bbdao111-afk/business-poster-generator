# 输入与输出规范

## 产品海报 JSON

```json
{
  "type": "product",
  "brand": "品牌名",
  "company_logo": "/绝对路径/公司logo.png",
  "badge": "Q4 冲刺套餐",
  "title": "产品或方案名",
  "subtitle": "{1000点} AI 授权，{5万元} 封顶",
  "intro": "关键销售结论",
  "highlights": ["价值点一", "价值点二", "价值点三", "价值点四"],
  "metrics": [{"value": "33%", "label": "性能提升", "note": "相对某基准"}],
  "metric_groups": [{"items": [{"value": "1000点", "label": "AI 助手授权"}, {"value": "5万元", "label": "Q4套餐封顶价"}]}],
  "screens_label": "产品界面实拍：…",
  "screens": [{"img": "/绝对路径/界面1.png", "label": "AI 智能问答"}],
  "sections": [{"title": "核心能力", "body": "说明文字", "points": ["要点一", "要点二", "要点三"]}],
  "package_table": {
    "title": "套餐包含 · 两大组成",
    "columns": ["组成", "套餐物料", "关键能力"],
    "rows": [{"name": "AI智能体引擎", "material": "物料名 ＋ 基础运维服务（1年）", "points": ["要点一", "要点二", "要点三"]}],
    "footer": "两款物料均含 1 年基础运维服务与软件升级授权"
  },
  "cta": "Q4 冲刺 · 能力限时下放",
  "source_note": "上市时间/退市时间/口径说明",
  "price_note": "（价格为总代价，最终报价以内部报价系统为准）",
  "logo": "/绝对路径/logo.png",
  "hero_image": "/绝对路径/product.png",
  "title_font": "youshe",
  "title_effect": "tech-shadow-light"
}
```

字段说明：`company_logo` 固定在左上角（白底胶囊），是公司侧唯一品牌元素，优先级高于 `logo`；`screens` 与 `sections[].points` 是本版式“充实饱满”的关键——4 栏界面实拍 + 2×2 要点卡会把纵向空间填满。`screens` 与 `product_screens`（单张拼图）二选一，前者优先。`metric_groups` 与 `metrics` 二选一：需要把 4 个数字收成 2 张“一句话卡”时用 `metric_groups`（每卡 2 组值/标签，虚线分隔），否则用 `metrics`。`highlights` 建议给 4 条以填满 2×2 网格。`package_table` 与 `sections` 二选一，前者优先——一个套餐含多款物料时用表格讲清型号/物料/能力对应关系。

## 客户案例海报：输入要求

用户提供的素材按此约定接收，缺项先问再渲染，不凭空补造：

| 素材 | 必选 | 说明 |
|---|---|---|
| 案例客户 Logo | 是 | `customer_logo`，透明底 PNG 优先；不得伪造或改色 |
| 背景图片 | 是 | `hero_image`，客户实景或行业场景图；缺失时向用户索取 |
| 案例介绍 | 是 | 项目背景、方案与成效原文；据此提炼 `customer`、`customer_position`、`solutions`、`results`、`summary` |
| 海报大标题 | 否 | `campaign`，两行以内；未提供时从案例介绍中提炼，并明确标注为营销改写 |

供应商 Logo、二维码按有则用之、无则占位的原则处理。

**`results` 为可选字段**（最多 3 条，`value`/`label`/`note`）：只在有可核验数字时提供，缺省时案例版不渲染成果带；提供时每条必须带 `note` 写明来源、口径或比较基准，不得留空或写"效果显著"。

## 大标题字体与效果（两类海报通用）

brief JSON 可选字段，配合「大字选版」流程使用（详见 [艺术字规则层](art-type.md)）：

```json
"title_font": "youshe",
"title_effect": "plain"
```

- `title_font`：展示字体 id，默认 `youshe`（优设标题黑）。候选：youshe / pangmen / douyu / sans / smiley / wenkai / zcool / serif / mashan。
- `title_effect`：大标题效果 id，默认 `plain`（纯净大字）。候选：plain / gradient / dual-tone / stroke / outline-mix / block-tech / extrude / tech-shadow / tech-shadow-light / neon / skew。

| 背景 | 推荐效果 | 说明 |
| --- | --- | --- |
| 浅色底（产品版） | **`block-tech`** | 斜切深蓝渐变块 + 纯白反白字 + 左绿边条；颜色由色块承载，是清晰度与版面焦点最强的一种 |
| 浅色底（产品版，不要色块） | `dual-tone` | 主词墨蓝 #0A3A7B + `{}` 关键词品牌绿，白/暗双向 1px 压印高光，零模糊阴影 |
| 浅色底（要渐变科技感） | `tech-shadow-light` | 深蓝→青渐变填充 + 硬边挤出阴影；细笔画字会糊，建议配粗壮字体 |
| 浅色底（潮流场合） | `outline-mix` | 主体空心描边 + 关键词实心；远看偏弱，不适合信息型海报 |
| 深色底（客户案例版） | `tech-shadow` | 浅色填充 + 多色下方阴影 + 关键词高亮 + 标题速度线 |

**标题里的 `{}` 是分色入口**：`{Q4冲刺套餐}` 会被转成 `.hl`，上面每个效果都给了 `.hl` 一套独立配色。换字体、换效果、换配色三者互不影响。

## 客户案例海报 JSON

```json
{
  "type": "case",
  "brand": "供应商品牌",
  "campaign": "守住企业核心数据\n护航 AI 产业链拔节生长",
  "customer": "客户简称",
  "customer_position": "行业定位",
  "solutions": [{"name": "桌面云", "value": "核心设计数据集中管控，实现安全协作"}],
  "results": [{"value": "1200+", "label": "研发终端统一承载", "note": "口径与统计区间"}],
  "summary": "挑战、方案与结果摘要",
  "vendor_logo": "/绝对路径/vendor-logo.png",
  "customer_logo": "/绝对路径/customer-logo.png",
  "hero_image": "/绝对路径/customer-site.jpg",
  "qr_image": "/绝对路径/qr.png"
}
```

## 使用渲染器

```bash
python3 scripts/render_poster.py brief.json --output poster.html
```

所有图片路径转换为 HTML 可加载的绝对 `file://` 地址。渲染器只负责稳定模板；生成前仍需根据对应规范完成事实核验和内容压缩。

建议交付 `brief.json`、`poster.html`、`poster.png` 和 `source-note.md`。PNG 导出视口：产品 794×1123（A4 预览，可按倍数提升），案例 1080×1440。印刷输出按 300 DPI 重新导出并保留 3mm 出血。

