import argparse
import json
import re
import sys

REQUIRED = ["title", "preconditions", "steps", "expected", "type"]
ALLOWED_LEVEL = {"1", "2", "3"}
NON_FUNCTIONAL_TYPES = {"安全", "性能", "兼容", "稳定性"}
REQ_ID_PATTERN = re.compile(r"^R-\d{3,}$")


def _to_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value).strip()
    return [text] if text else []


def validate_case(case, path, errors):
    for field in REQUIRED:
        if field not in case:
            errors.append(f"{path}: missing field '{field}'")
    if "priority_level" not in case:
        errors.append(f"{path}: missing field 'priority_level'")
    raw_level = str(case.get("priority_level", "")).strip()
    if raw_level and raw_level not in ALLOWED_LEVEL:
        errors.append(f"{path}: invalid priority_level '{raw_level}', expected 1/2/3")
    if "steps" in case and (not isinstance(case["steps"], list) or len(case["steps"]) == 0):
        errors.append(f"{path}: 'steps' must be non-empty list")
    if "preconditions" in case and (not isinstance(case["preconditions"], list) or len(case["preconditions"]) == 0):
        errors.append(f"{path}: 'preconditions' must be non-empty list")
    if "steps" in case and len(case["steps"]) + 2 > 10:
        errors.append(f"{path}: child nodes exceed 10 (preconditions + steps + expected must be <= 10)")
    covers = _to_list(case.get("covers"))
    if not covers:
        errors.append(f"{path}: missing field 'covers' or covers is empty")
    else:
        for rid in covers:
            if not REQ_ID_PATTERN.match(rid):
                errors.append(f"{path}: invalid covers id '{rid}', expected format like R-001")


def main():
    parser = argparse.ArgumentParser(description="Validate test-case tree JSON")
    parser.add_argument("--input", required=True)
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    errors = []
    module_count = 0
    scenario_count = 0
    case_count = 0
    case_types = set()

    for mi, module in enumerate(data.get("modules", [])):
        module_count += 1
        for si, scenario in enumerate(module.get("scenarios", [])):
            scenario_count += 1
            cases = scenario.get("cases", [])
            if not cases:
                errors.append(f"modules[{mi}].scenarios[{si}]: no cases")
            for ci, case in enumerate(cases):
                case_count += 1
                validate_case(case, f"modules[{mi}].scenarios[{si}].cases[{ci}]", errors)
                case_types.add(str(case.get("type", "")).strip())

    print(f"summary: modules={module_count}, scenarios={scenario_count}, cases={case_count}")
    if errors:
        print("validation: FAILED")
        for err in errors:
            print(f"- {err}")
        sys.exit(1)

    print("validation: PASSED")
    covered_non_functional = sorted(case_types.intersection(NON_FUNCTIONAL_TYPES))
    if covered_non_functional:
        print(f"non-functional coverage: {', '.join(covered_non_functional)}")
    else:
        print("WARNING: non-functional coverage missing (安全/性能/兼容/稳定性). Add cases or provide explicit N/A reason.")


if __name__ == "__main__":
    main()
