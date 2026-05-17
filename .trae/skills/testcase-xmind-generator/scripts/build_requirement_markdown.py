import argparse
import re
from pathlib import Path


def _read_text(path: Path) -> str:
    encodings = ["utf-8", "utf-8-sig", "gbk", "gb18030", "latin-1"]
    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"cannot decode text file: {path}")


def _extract_sources(text: str):
    return [item.strip() for item in re.findall(r"^# Source:\s*(.+?)\s*$", text, flags=re.MULTILINE) if item.strip()]


def _default_title(input_path: Path, sources):
    if sources:
        first = Path(sources[0])
        return first.stem
    return input_path.stem


def main():
    parser = argparse.ArgumentParser(description="Build a structured markdown requirement draft from normalized text.")
    parser.add_argument("--input", required=True, help="Normalized requirements text path.")
    parser.add_argument("--output", required=True, help="Output markdown path.")
    parser.add_argument("--title", help="Document title.")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    text = _read_text(input_path).strip()
    sources = _extract_sources(text)
    title = (args.title or _default_title(input_path, sources)).strip() or "需求整理"

    lines = [
        f"# {title}",
        "",
        "## 输入来源",
    ]
    if sources:
        lines.extend([f"- {item}" for item in sources])
    else:
        lines.append(f"- {input_path}")

    lines.extend(
        [
            "",
            "## 需求整理说明",
            "- 本文档由技能流程自动生成骨架，后续必须结合 OCR 结果与图片视觉理解补全。",
            "- 若输入包含图片，不能只保留 OCR 原文，必须补充图片中的页面结构、标注、变更意图与业务规则理解。",
            "",
            "## 功能点",
            "",
            "## 业务规则",
            "",
            "## 状态与流程",
            "",
            "## 异常与边界",
            "",
            "## 非功能与兼容性",
            "",
            "## 待确认问题",
            "",
            "## OCR原文",
            "",
            text,
            "",
        ]
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"OK: requirement markdown -> {output_path.resolve()}")


if __name__ == "__main__":
    main()
