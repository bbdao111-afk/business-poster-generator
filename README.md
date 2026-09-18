# 商业海报生成器 · business-poster-generator

[![零指向发布门禁](https://github.com/bbdao111-afk/business-poster-generator/actions/workflows/pointing-check.yml/badge.svg)](https://github.com/bbdao111-afk/business-poster-generator/actions/workflows/pointing-check.yml)
![License](https://img.shields.io/badge/License-MIT-green) ![字体](https://img.shields.io/badge/%E5%AD%97%E4%BD%93-OFL%20%2B%20%E5%85%8D%E8%B4%B9%E5%95%86%E7%94%A8-blue)

一个**路由式（rule-routed）海报生成 Skill**：把产品彩页、方案 PDF/Word 或客户案例材料，经过「素材收集 → 方案选版 → 成品输出」三道硬门禁，转成可编辑 HTML 与 300 DPI 印刷级 PNG。

适用于中文 B2B 科技、云计算、IT 基础设施与企业服务营销场景。**不适合**纯艺术海报或一次性活动海报。

> 核心设计：所有关键中文文案、数字、Logo、二维码**必须由排版层渲染**，不交给图片模型生成——这是中文海报能被验收的前提。

## 为什么要"路由式"

一次性出图的工具在真实业务里通常不可用：素材不全、数据口径错、审美不符。本 Skill 把它拆成可中断、可回退的流程，并把规则外置成 `references/` 规范层，按需加载：

| 触发条件 | 路由到的规则 |
|---|---|
| 推进流程、门禁话术、质检清单 | [references/workflow.md](references/workflow.md) |
| 输入是彩页 / 方案书 / 参数表 | [references/product-poster.md](references/product-poster.md) |
| 输入是客户案例 / 成功故事 | [references/case-poster.md](references/case-poster.md) |
| 准备渲染数据（brief JSON） | [references/input-output.md](references/input-output.md) |
| 处理大标题字体、字距、效果 | [references/art-type.md](references/art-type.md) |
| 科技背景、标题光效、切角卡片 | [references/tech-poster-fx.md](references/tech-poster-fx.md) |

## 三道门禁

1. **素材收集与核验** → 先输出必选/可选素材清单并停下，缺项不动手。
2. **方案选版（强制等待选择）** → 同时给出可编号的 3–5 条主标题文案、`字体 × 效果 × 配色` 选版页、版式与背景方向。**未收到明确编号选择，绝不渲染成品。**
3. **成品输出** → 渲染 HTML + 导出 PNG，并按「最低质检」逐条核对后交付。

回退规则：改文案/换截图 → 原地重出；改字体/效果/版式 → 回第二步；改主题/换客户/换素材 → 回第一步。

## 安装

```bash
# 作为 Codex / Claude 技能使用
git clone https://github.com/<your-name>/business-poster-generator.git \
  ~/.codex/skills/business-poster-generator

# 可选：导出 PNG 需要无头 Chromium
pip install playwright && playwright install chromium
```

`SKILL.md` 位于仓库根目录，clone 后即为一个可直接加载的 skill。

## 手动使用（不经过 agent）

```bash
cd ~/.codex/skills/business-poster-generator

# 1) 字体 × 效果 选版页
python3 art-type/scripts/make_select_page.py "护航{AI算力}产业链生长" \
  --output ./out --default-fx block-tech

# 2) 多方案选版册（文案|字体|效果）
python3 scripts/make_options.py --output ./out --theme light \
  --option "文案A|sans|block-tech" \
  --option "文案B|pangmen|dual-tone"

# 3) 渲染成品 HTML
python3 scripts/render_poster.py assets/product-example.json --output ./out/poster.html

# 4) 导出 300 DPI PNG（印刷级）
python3 scripts/export_png.py ./out/poster.html --output ./out/poster@300.png --dpi 300
```

输入是一个 `brief.json`，字段与约束见 [references/input-output.md](references/input-output.md)；可直接参考
[assets/product-example.json](assets/product-example.json)（产品版）与 [assets/case-example.json](assets/case-example.json)（案例版）。

## 中文展示字体

`art-type/fonts/` 打包 9 款**可商用**展示字体，`@font-face` 内嵌进输出文件，不依赖系统字体：

优设标题黑、庞门正道标题体、斗鱼追光体 2.0、思源黑体 Heavy、思源宋体 Heavy、得意黑、霞鹜文楷、站酷庆科黄油体、马善政楷体。

效果库共 11 种（纯净大字 / 渐变填充 / 双色分阶压印 / 双层描边 / 空心描边混排 / 斜切渐变块反白 / 立体挤出 / 科技主题阴影（暗底、浅底）/ 霓虹发光 / 斜切冲击）。

授权全文与来源见 [art-type/fonts/LICENSES.md](art-type/fonts/LICENSES.md)。 redistributing 前请逐条核对上游许可证。

## 内容底线

- 区分「原文事实 / 可计算事实 / 营销改写 / 缺失项」，**不补造**客户名称、百分比、排名、型号、认证、部署规模。
- 数据口径与原始材料逐字核对；内部信息（接口人、内部系统路径、发文编号、"仅限内部公开"标记）一律不进海报。<!-- pointing:allow -->
- 低清或缺失素材用明确占位，不伪造客户 Logo 与二维码。

## 零指向发布门禁（可执行，不是口号）

本仓库所有示例、截图、Logo 均为**合成内容**（`示例科技 DEMOTECH` / `示例制造` / `AI 助手`），不含任何真实厂商、产品、客户或内部流程信息。为了让这条规则不被后来者破坏，它被做成了脚本 + CI：

```bash
# 复制禁词表模板，逐行填入你公司的真实名称（机器猜不出来，必须你填）
cp assets/pointing-terms.example.txt ./pointing-terms.txt

# 发布前扫描：命中即非 0 退出，禁止 push
python3 scripts/check_pointing_info.py --terms ./pointing-terms.txt .
```

- **error（阻断）**：邮箱、手机号、座机、内网域名、真实编号值、密钥令牌、IM 账号，以及自定义禁词命中。
- **warn（不阻断）**：`接口人`、`发文编号` 这类词——规范正文要描述规则，绕不开；确属说明文字的行尾加 `pointing:allow` 豁免。
- 存在 `pointing-terms.txt` 时，[GitHub Actions](.github/workflows/pointing-check.yml) 会自动带上它，并顺带跑示例渲染冒烟测试。

**关键边界**：真实交付海报**绝不脱敏**（产品名、客户名、数据口径是事实本身，替换等于造假）；只有对外公开的 Skill、示例、截图、模板必须零指向。完整规则见 [references/desensitize.md](references/desensitize.md)。

## 目录结构

```
.
├── SKILL.md                  # 技能入口：三步门禁 + 路由表 + 质检清单
├── 使用说明.md               # 面向使用者的完整输入清单与请求模板
├── agents/openai.yaml        # Agent 接口元数据
├── references/               # 规则层（按需加载）：workflow / product / case / input-output / art-type / tech-poster-fx / desensitize
├── scripts/                  # make_options · render_poster · export_png · check_pointing_info
├── art-type/                 # 字体层：fonts.json + 选版脚本 + 9 款字体 + LICENSES.md
├── assets/                   # 中性示例 brief + 全合成演示截图/Logo + 禁词表模板
└── .github/workflows/        # 零指向门禁 CI + 渲染冒烟测试
```

## 示例数据说明

`assets/demo/` 下的界面截图与 Logo 由脚本**程序化合成**，`assets/*.json` 的文案与指标均为自造样例，不代表任何真实客户成果、产品界面或厂商口径。若你替换为自己公司的素材，请自行确认授权与合规，并在再次公开前跑一遍零指向门禁。

## License

MIT（代码与文档）。字体文件遵循各自的许可证（SIL OFL 1.1 或发布方免费商用条款），详见 `art-type/fonts/LICENSES.md`。
