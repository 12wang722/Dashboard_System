import argparse
import json
from pathlib import Path


def _to_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _normalize_priority_level(case):
    raw = case.get("priority_level", "")
    raw = str(raw).strip()
    if raw in {"1", "2", "3"}:
        case["priority_level"] = raw
    else:
        case["priority_level"] = "2"
    if "priority" in case:
        case.pop("priority", None)


def normalize_case_tree(data):
    changed = 0
    for module in data.get("modules", []):
        for scenario in module.get("scenarios", []):
            for case in scenario.get("cases", []):
                for key in ("preconditions", "steps"):
                    before = case.get(key)
                    after = _to_list(before)
                    if before != after:
                        case[key] = after
                        changed += 1
                before_covers = case.get("covers")
                if before_covers is not None:
                    after_covers = _to_list(before_covers)
                    if before_covers != after_covers:
                        case["covers"] = after_covers
                        changed += 1
                before_level = case.get("priority_level", None)
                had_priority = "priority" in case
                _normalize_priority_level(case)
                if before_level != case.get("priority_level") or had_priority:
                    changed += 1
    return changed, data


def main():
    parser = argparse.ArgumentParser(
        description="Normalize case-tree JSON fields (preconditions/steps) to arrays."
    )
    parser.add_argument("--input", required=True, help="Input case-tree JSON path")
    parser.add_argument("--output", help="Output JSON path (default: overwrite input)")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path

    data = json.loads(input_path.read_text(encoding="utf-8"))
    changed, normalized = normalize_case_tree(data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OK: normalized {changed} field(s) -> {output_path.resolve()}")


if __name__ == "__main__":
    main()
