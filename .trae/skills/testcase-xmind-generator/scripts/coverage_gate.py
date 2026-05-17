import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Fail if requirement coverage is incomplete.")
    parser.add_argument("--input", required=True, help="coverage-matrix JSON path")
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    summary = data.get("summary", {})
    uncovered = data.get("uncovered_requirement_ids", [])
    no_covers_cases = data.get("cases_without_covers", [])
    unknown_refs = data.get("unknown_requirement_refs", [])

    print(
        "coverage: "
        f"requirements={summary.get('requirements_total', 0)}, "
        f"covered={summary.get('requirements_covered', 0)}, "
        f"uncovered={summary.get('requirements_uncovered', 0)}, "
        f"cases_without_covers={summary.get('cases_without_covers', 0)}, "
        f"unknown_refs={summary.get('unknown_requirement_refs', 0)}"
    )

    errors = []
    if uncovered:
        errors.append(f"uncovered requirements: {', '.join(uncovered[:20])}")
    if no_covers_cases:
        errors.append(f"cases without covers: {len(no_covers_cases)}")
    if unknown_refs:
        errors.append(f"unknown requirement refs: {len(unknown_refs)}")

    if errors:
        print("coverage gate: FAILED")
        for err in errors:
            print(f"- {err}")
        sys.exit(1)

    print("coverage gate: PASSED")


if __name__ == "__main__":
    main()
