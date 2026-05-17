import argparse
import json
from pathlib import Path


def _to_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    return [text] if text else []


def _iter_cases(case_tree):
    for module in case_tree.get("modules", []):
        m = module.get("name", "Unnamed Module")
        for scenario in module.get("scenarios", []):
            s = scenario.get("name", "Unnamed Scenario")
            for case in scenario.get("cases", []):
                yield {
                    "module": m,
                    "scenario": s,
                    "title": case.get("title", "Untitled Case"),
                    "covers": _to_list(case.get("covers")),
                }


def build_matrix(req_index, case_tree):
    reqs = req_index.get("requirements", [])
    req_ids = {r["id"] for r in reqs}
    mapping = {r["id"]: {"requirement": r["text"], "cases": []} for r in reqs}

    unknown_refs = []
    no_covers_cases = []

    for case in _iter_cases(case_tree):
        case_ref = f"{case['module']} / {case['scenario']} / {case['title']}"
        covers = case["covers"]
        if not covers:
            no_covers_cases.append(case_ref)
            continue
        for rid in covers:
            if rid not in req_ids:
                unknown_refs.append({"case": case_ref, "requirement_id": rid})
                continue
            mapping[rid]["cases"].append(case_ref)

    uncovered = [rid for rid, info in mapping.items() if len(info["cases"]) == 0]

    return {
        "summary": {
            "requirements_total": len(reqs),
            "requirements_covered": len(reqs) - len(uncovered),
            "requirements_uncovered": len(uncovered),
            "cases_without_covers": len(no_covers_cases),
            "unknown_requirement_refs": len(unknown_refs),
        },
        "mapping": mapping,
        "uncovered_requirement_ids": uncovered,
        "cases_without_covers": no_covers_cases,
        "unknown_requirement_refs": unknown_refs,
    }


def main():
    parser = argparse.ArgumentParser(description="Build requirement-to-case coverage matrix.")
    parser.add_argument("--requirements", required=True, help="requirements-index JSON path")
    parser.add_argument("--cases", required=True, help="case-tree JSON path")
    parser.add_argument("--output", required=True, help="coverage-matrix JSON output path")
    args = parser.parse_args()

    req_data = json.loads(Path(args.requirements).read_text(encoding="utf-8"))
    case_data = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    matrix = build_matrix(req_data, case_data)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding="utf-8")
    s = matrix["summary"]
    print(
        "OK: "
        f"requirements={s['requirements_total']}, "
        f"covered={s['requirements_covered']}, "
        f"uncovered={s['requirements_uncovered']}, "
        f"cases_without_covers={s['cases_without_covers']}, "
        f"unknown_refs={s['unknown_requirement_refs']} "
        f"-> {out.resolve()}"
    )


if __name__ == "__main__":
    main()
