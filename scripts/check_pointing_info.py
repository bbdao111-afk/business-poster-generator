#!/usr/bin/env python3
"""零指向检查（发布门禁）。

判定分两级：
  error（阻断发布）——真实 PII/密钥、内网域名、真实编号值，以及**自定义禁词表**命中
                     （你所在组织的公司名/品牌/产品名/客户名，机器无法自动识别，必须由你提供）；
  warn （默认不阻断）——"接口人""发文编号""仅限内部公开"这类**规则说明文字本身**会包含的词。
  行尾加 `pointing:allow` 可豁免单行。

用法：
  python3 scripts/check_pointing_info.py                       # 扫整个仓库
  python3 scripts/check_pointing_info.py --terms my-org.txt    # 用你的禁词表做硬门禁
  python3 scripts/check_pointing_info.py --strict              # warn 也阻断
  python3 scripts/check_pointing_info.py --format github       # CI 注解输出

退出码：0 通过；1 存在 error。
"""
from __future__ import annotations

import argparse, json, re, sys
from pathlib import Path

TEXT_EXT = {".md", ".json", ".py", ".yaml", ".yml", ".toml", ".txt", ".html", ".css",
            ".js", ".ts", ".sh", ".csv", ".ini", ".cfg"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "out", ".workbuddy"}
SELF_EXCLUDE = {Path(__file__).name}
WAIVER = "pointing:allow"

# (规则名, 编译后正则, 级别)
PATTERNS: list[tuple[str, re.Pattern, str]] = [
    ("邮箱", re.compile(r"[\w.+-]+@[A-Za-z][\w-]*(?:\.[\w-]+)*\.[A-Za-z]{2,}"), "error"),
    ("中国大陆手机号", re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), "error"),
    ("座机分机", re.compile(r"(?<!\d)0\d{2,3}-\d{7,8}(?!\d)"), "error"),
    ("内网域名", re.compile(r"\b[\w-]+\.(?:corp|internal|intranet|lan)\b", re.I), "error"),
    ("真实编号值", re.compile(r"(?:发文|工单|合同|报价)编号\s*[:：]?\s*[A-Z]{2,}\d{5,}", re.I), "error"),
    ("密钥/令牌", re.compile(r"sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9._-]{24,}", re.I), "error"),
    ("即时通讯账号", re.compile(r"(?:微信号?|QQ号?|钉钉|飞书|企业微信)\s*[:：]\s*[A-Za-z0-9_-]{4,}"), "error"),
    ("接口人字段", re.compile(r"接口人\s*[:：]\s*\S"), "warn"),
    ("联系人字段", re.compile(r"(?:联系人|责任人|对接人)\s*[:：]\s*[一-龥]{2,4}"), "warn"),
    ("内部标记词", re.compile(r"仅限内部|内部公开|内部资料|不得外传|confidential"), "warn"),
    ("内部流程词", re.compile(r"发文编号|接口人|OA\s*路径"), "warn"),
]

# 中性占位词：文档与示例里合法出现，不作为禁词
ALLOW_DEFAULT = {"示例科技", "DEMOTECH", "示例制造", "示例客户", "示例平台", "示例模块",
                 "示例品牌", "示例数据", "示例内容", "示例界面", "内部报价系统", "内部系统路径"}
EXAMPLE_MAIL = re.compile(r"(?:example|demo|test|localhost|your-?\w*)\.[A-Za-z]{2,}", re.I)


def load_terms(paths: list[str]) -> list[str]:
    terms: list[str] = []
    for raw in paths:
        p = Path(raw).expanduser()
        if not p.exists():
            sys.exit(f"词表文件不存在：{p}")
        terms += [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines()
                  if ln.strip() and not ln.lstrip().startswith("#")]
    return terms


def scan_file(path: Path, terms: list[str], allow: set[str]) -> list[dict]:
    findings: list[dict] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (UnicodeDecodeError, OSError):
        return findings
    for name, pat, level in PATTERNS:
        for i, line in enumerate(lines, 1):
            if WAIVER in line:
                continue
            m = pat.search(line)
            if not m:
                continue
            if name == "邮箱" and EXAMPLE_MAIL.search(m.group(0)):
                continue
            findings.append({"file": str(path), "line": i, "rule": name, "level": level,
                             "text": line.strip()[:150]})
    allow_lower = {a.lower() for a in allow}
    for t in terms:
        if t.lower() in allow_lower:
            continue
        pat = re.compile(re.escape(t), re.I)
        for i, line in enumerate(lines, 1):
            if WAIVER in line:
                continue
            if pat.search(line):
                findings.append({"file": str(path), "line": i, "rule": f"自定义禁词「{t}」",
                                 "level": "error", "text": line.strip()[:150]})
    return findings


def iter_targets(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    out: list[Path] = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in TEXT_EXT or p.name in SELF_EXCLUDE:
            continue
        if SKIP_DIRS & set(p.parts):
            continue
        out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="零指向发布门禁")
    ap.add_argument("targets", nargs="*", default=["."], help="要扫描的文件或目录（默认整个仓库）")
    ap.add_argument("--terms", action="append", default=[], help="自定义禁词表，可多次传入")
    ap.add_argument("--allow", action="append", default=[], help="追加白名单词")
    ap.add_argument("--strict", action="store_true", help="warn 也视为阻断")
    ap.add_argument("--format", choices=["text", "github", "json"], default="text")
    args = ap.parse_args()

    terms = load_terms(args.terms)
    allow = ALLOW_DEFAULT | set(args.allow)
    findings: list[dict] = []
    scanned = 0
    for target in args.targets:
        for f in iter_targets(Path(target).expanduser().resolve()):
            scanned += 1
            findings += scan_file(f, terms, allow)

    errors = [x for x in findings if x["level"] == "error"]
    warns = [x for x in findings if x["level"] == "warn"]
    blocking = errors + (warns if args.strict else [])

    if args.format == "json":
        print(json.dumps({"scanned": scanned, "errors": errors, "warnings": warns},
                         ensure_ascii=False, indent=2))
    elif args.format == "github":
        for x in errors:
            print(f"::error file={x['file']},line={x['line']}::[{x['rule']}] {x['text']}")
        for x in warns:
            print(f"::warning file={x['file']},line={x['line']}::[{x['rule']}] {x['text']}")
        print(f"::notice::扫描 {scanned} 个文件：error {len(errors)}，warn {len(warns)}")
    else:
        for x in findings:
            tag = "!!" if x["level"] == "error" else "~ "
            print(f"{tag} {x['file']}:{x['line']}  [{x['rule']}]  {x['text']}")
        verdict = "禁止对外发布：按 references/desensitize.md 脱敏后重跑。" if blocking else "通过。"
        print(f"\n扫描 {scanned} 个文件；error {len(errors)}，warn {len(warns)}。{verdict}")
    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
