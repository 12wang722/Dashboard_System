import argparse
import json
import re
from pathlib import Path

STRUCTURE_EXACT_NOISE = {
    "需求描述",
    "验收标准",
    "目录",
    "目次",
    "修订记录",
    "版本记录",
    "变更记录",
    "审批记录",
    "发布记录",
    "术语定义",
    "附录",
}

STRUCTURE_KEYWORD_NOISE = (
    "文档编号",
    "文档名称",
    "编写人",
    "审核人",
    "批准人",
    "发布日期",
    "生效日期",
    "页码",
    "copyright",
    "版权所有",
)

STRUCTURE_PATTERNS = [
    re.compile(r"^#?\s*source\s*:", re.IGNORECASE),
    re.compile(r"^第\s*[0-9一二三四五六七八九十]+\s*[章节篇]\b"),
    re.compile(r"^[0-9]+(\.[0-9]+)*\s*$"),
    re.compile(r"^[-=*_]{3,}$"),
    re.compile(r"^\|?[:\-\s|]+\|?$"),
    re.compile(r"^表\s*[0-9一二三四五六七八九十]+[:：]"),
    re.compile(r"^图\s*[0-9一二三四五六七八九十]+[:：]"),
    re.compile(r"^第\s*[0-9]+\s*页(\s*/\s*共?\s*[0-9]+\s*页)?$"),
]

REQUIREMENT_VERB_PATTERN = re.compile(
    r"(支持|应当|应该|应|必须|可以|可|需|需要|禁止|不允许|允许|校验|校验|显示|返回|提交|查询|新增|新建|编辑|删除|导入|导出|登录|登出|保存|同步|推送)"
)


def _clean_line(line):
    text = line.strip()
    text = re.sub(r"^#+\s*", "", text)
    text = re.sub(r"^[\-\*\u2022]+\s*", "", text)
    text = re.sub(r"^\d+(\.\d+)*[、\.\s]+", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _is_structure_noise(line):
    if not line:
        return True
    if line in STRUCTURE_EXACT_NOISE:
        return True
    lowered = line.lower()
    if any(keyword in lowered for keyword in STRUCTURE_KEYWORD_NOISE):
        return True
    if line.endswith("：") or line.endswith(":"):
        return True
    if all(ch in "-=*_:.|/\\()[]{} " for ch in line):
        return True
    for pattern in STRUCTURE_PATTERNS:
        if pattern.match(line):
            return True
    # Short noun-like headings (e.g. "功能范围", "页面说明") should not become requirement items.
    if len(line) <= 12 and " " not in line and not REQUIREMENT_VERB_PATTERN.search(line):
        if re.fullmatch(r"[\u4e00-\u9fffA-Za-z0-9]+", line):
            return True
    return False


def _is_candidate(line):
    if not line:
        return False
    if len(line) < 4:
        return False
    if _is_structure_noise(line):
        return False
    return True


def build_index(text):
    items = []
    seen = set()
    for i, raw in enumerate(text.splitlines(), start=1):
        cleaned = _clean_line(raw)
        if not _is_candidate(cleaned):
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        items.append(
            {
                "id": f"R-{len(items)+1:03d}",
                "text": cleaned,
                "line": i,
            }
        )
    return {"requirements": items}


def main():
    parser = argparse.ArgumentParser(description="Build requirements index from normalized requirement text.")
    parser.add_argument("--input", required=True, help="Path to normalized requirement text file")
    parser.add_argument("--output", required=True, help="Output requirements-index JSON path")
    args = parser.parse_args()

    src = Path(args.input)
    out = Path(args.output)
    data = build_index(src.read_text(encoding="utf-8"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: requirements={len(data['requirements'])} -> {out.resolve()}")


if __name__ == "__main__":
    main()
