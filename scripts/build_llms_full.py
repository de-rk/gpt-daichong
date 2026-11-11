#!/usr/bin/env python3
"""Generate llms-full.txt from llms.txt + site markdown sources.

Run from the repo root:  python3 scripts/build_llms_full.py
Output: llms-full.txt (single plain-text file with all page content,
URLs rewritten to absolute, front matter stripped).
"""

from pathlib import Path
import datetime
import re

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://de-rk.github.io/gpt-daichong"
OUT = ROOT / "llms-full.txt"

# (markdown 源文件, 线上 URL) —— 顺序即 llms.txt 的页面顺序
PAGES = [
    ("README.md", f"{SITE}/"),
    ("docs/chatgpt-recharge-guide.md", f"{SITE}/docs/chatgpt-recharge-guide.html"),
    ("docs/chatgpt-recharge-method.md", f"{SITE}/docs/chatgpt-recharge-method.html"),
    ("docs/chatgpt-pro-recharge-guide.md", f"{SITE}/docs/chatgpt-pro-recharge-guide.html"),
    ("docs/chatgpt-buy-guide.md", f"{SITE}/docs/chatgpt-buy-guide.html"),
    ("docs/chatgpt-pay-on-behalf.md", f"{SITE}/docs/chatgpt-pay-on-behalf.html"),
    ("docs/chatgpt-plus-codex.md", f"{SITE}/docs/chatgpt-plus-codex.html"),
    ("docs/claude-buy-guide.md", f"{SITE}/docs/claude-buy-guide.html"),
    ("docs/claude-recharge-guide.md", f"{SITE}/docs/claude-recharge-guide.html"),
    ("docs/claude-code-rmb.md", f"{SITE}/docs/claude-code-rmb.html"),
]


def strip_front_matter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip("\n")
    return text


def absolutize(text: str) -> str:
    """把站内相对链接与图片路径改成绝对 URL。"""
    text = text.replace(f"]({SITE}", "](__KEEP__")  # 防止二次拼接
    text = re.sub(r"\]\((\.\./|\./)?assets/images/", f"]({SITE}/assets/images/", text)
    text = text.replace('src="./assets/images/', f'src="{SITE}/assets/images/')
    text = re.sub(r"\]\(([a-zA-Z0-9-]+)\.md\)", f"]({SITE}/docs/\\1.html)", text)
    text = text.replace("](../README.md)", f"]({SITE}/)")
    return text.replace("](__KEEP__", f"]({SITE}")


def page_title(text: str, fallback: str) -> str:
    m = re.search(r"^title:\s*(.+)$", text, re.M)
    if m:
        return m.group(1).strip().strip("\"'")
    m = re.search(r"^#\s+(.+)$", text, re.M)
    return m.group(1).strip() if m else fallback


def drop_leading_h1(text: str) -> str:
    """去掉正文首个 H1，避免与「## 标题」重复。"""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.strip():
            if line.startswith("# "):
                lines.pop(i)
            break
    return "\n".join(lines).lstrip("\n")


def main() -> None:
    today = datetime.date.today().isoformat()
    parts = [
        "# ChatGPT / Claude 国内充值代充教程合集 2026 — Full Text",
        "",
        "> 本文件由 scripts/build_llms_full.py 自动生成，内容与线上站点一致；"
        "请勿手工编辑本文件，修改对应 markdown 源文件后重新生成。",
        f"> 站点地址: {SITE}/    生成日期: {today}",
        "",
    ]
    for md_rel, url in PAGES:
        md = ROOT / md_rel
        if not md.is_file():
            raise SystemExit(f"缺少源文件: {md_rel}")
        raw = md.read_text(encoding="utf-8")
        body = absolutize(strip_front_matter(raw))
        body = drop_leading_h1(body)
        title = page_title(raw, md.stem)
        parts += [
            "---",
            "",
            f"## {title}",
            "",
            f"URL: {url}",
            "",
            body.strip(),
            "",
        ]
    OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    size = OUT.stat().st_size
    print(f"OK: {OUT.name} ({size/1024:.0f} KB, {len(PAGES)} 页)")


if __name__ == "__main__":
    main()
