import argparse
import json
import os
import tempfile
import uuid
import zipfile
import copy
from pathlib import Path
from datetime import datetime
import re

try:
    import xmind
    from xmind.core.markerref import MarkerId
except ImportError:
    xmind = None
    MarkerId = None


def _new_id():
    return uuid.uuid4().hex[:26]


def _normalize_priority_level(raw):
    if isinstance(raw, int) and raw in {1, 2, 3}:
        return raw
    if isinstance(raw, str):
        val = raw.strip()
        mapping = {"1": 1, "2": 2, "3": 3}
        if val in mapping:
            return mapping[val]
    return 3


def _topic(title, children=None, notes=None, marker_id=None):
    node = {
        "id": _new_id(),
        "title": str(title),
        "attributedTitle": [{"text": str(title)}],
    }
    if children:
        node["children"] = {"attached": children}
    if notes:
        node["notes"] = {"plain": {"content": str(notes)}}
    if marker_id:
        node["markers"] = [{"markerId": marker_id}]
    return node


def _to_text_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    return [text] if text else []


def _expected_topic(case):
    level = _normalize_priority_level(case.get("priority_level", "3"))
    marker_id = f"priority-{level}"
    text = f"预期结果: {case.get('expected', '')}"
    return _topic(text, marker_id=marker_id)


def _steps_topic(case):
    steps = _to_text_list(case.get("steps", []))
    if not steps:
        text = "测试步骤：无"
    else:
        lines = [f"{idx}. {step}" for idx, step in enumerate(steps, start=1)]
        text = "测试步骤：\n" + "\n".join(lines)
    return _topic(text, children=[_expected_topic(case)])


def _preconditions_topic(case):
    preconditions = _to_text_list(case.get("preconditions", []))
    if not preconditions:
        text = "前置条件：无"
    else:
        text = "前置条件：" + "；".join(preconditions)
    return _topic(text)


def _case_topic(case):
    title = case.get("title", "Untitled Case")
    pre_topic = _preconditions_topic(case)
    pre_topic["children"] = {"attached": [_steps_topic(case)]}
    children = [pre_topic]

    notes = case.get("notes", "")
    note_text = f"注意事项:\n{notes}" if notes else None

    return _topic(title, children=children, notes=note_text)


def _scenario_topic(scenario):
    cases = [_case_topic(case) for case in scenario.get("cases", [])]
    return _topic(scenario.get("name", "Unnamed Scenario"), children=cases)


def _module_topic(module):
    scenarios = [_scenario_topic(s) for s in module.get("scenarios", [])]
    return _topic(module.get("name", "Unnamed Module"), children=scenarios)


def _build_content(project, modules, sheet_title):
    root = _topic(
        project,
        children=[_module_topic(module) for module in modules],
    )
    root["class"] = "topic"
    root["structureClass"] = "org.xmind.ui.logic.right"

    sheet = {
        "id": _new_id(),
        "class": "sheet",
        "title": sheet_title,
        "rootTopic": root,
        "topicOverlapping": False,
    }
    return [sheet]


def _build_content_with_template(project, modules, sheet_title, template_content):
    sheet = copy.deepcopy(template_content[0])
    sheet["title"] = sheet_title
    sheet["class"] = sheet.get("class", "sheet")
    root = sheet.get("rootTopic", {})
    root["title"] = project
    root["attributedTitle"] = [{"text": project}]
    root["children"] = {"attached": [_module_topic(module) for module in modules]}
    root["class"] = root.get("class", "topic")
    root["structureClass"] = root.get("structureClass", "org.xmind.ui.logic.right")
    sheet["rootTopic"] = root
    return [sheet]


def _validate(data):
    if not isinstance(data, dict):
        raise ValueError("Input JSON must be an object")
    if "project" not in data or "modules" not in data:
        raise ValueError("Input JSON must contain 'project' and 'modules'")


def _check_coverage_gate(coverage_path, case_tree_path):
    p = Path(coverage_path)
    if not p.exists():
        return False, f"coverage matrix not found: {p}"
    case_p = Path(case_tree_path)
    if case_p.exists() and p.stat().st_mtime < case_p.stat().st_mtime:
        return False, f"coverage matrix is stale: {p} (older than {case_p})"
    try:
        matrix = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:
        return False, f"coverage matrix parse failed: {exc}"
    summary = matrix.get("summary", {})
    uncovered = int(summary.get("requirements_uncovered", 0))
    no_covers = int(summary.get("cases_without_covers", 0))
    unknown_refs = int(summary.get("unknown_requirement_refs", 0))
    if uncovered > 0 or no_covers > 0 or unknown_refs > 0:
        return (
            False,
            "coverage gate not passed: "
            f"uncovered={uncovered}, cases_without_covers={no_covers}, unknown_refs={unknown_refs}",
        )
    return True, "coverage gate passed"


def _safe_filename(name):
    value = str(name).strip()
    value = re.sub(r'[\\/:*?"<>|]+', "_", value)
    value = re.sub(r"\s+", "_", value)
    value = value.strip(" ._")
    return value or "testcases"


def _resolve_output_path(raw_output, project):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = f"{_safe_filename(project)}_{stamp}.xmind"

    if not raw_output:
        return os.path.join("output", "xmind", base)

    output = raw_output.strip()
    if output.endswith("\\") or output.endswith("/"):
        return os.path.join(output, base)

    if os.path.isdir(output):
        return os.path.join(output, base)

    if output.lower().endswith(".xmind"):
        return output

    return os.path.join(output, base)


def _legacy_marker_id(level):
    mapping = {
        1: MarkerId.priority1,
        2: MarkerId.priority2,
        3: MarkerId.priority3,
    }
    return mapping[level]


def _build_legacy_entries(data, sheet_title):
    if xmind is None:
        return {}

    fd, temp_path = tempfile.mkstemp(suffix=".xmind")
    os.close(fd)
    try:
        with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED):
            pass
        workbook = xmind.load(temp_path)
        sheet = workbook.getPrimarySheet()
        sheet.setTitle(sheet_title)
        root = sheet.getRootTopic()
        root.setTitle(str(data["project"]))

        for module in data.get("modules", []):
            module_topic = root.addSubTopic()
            module_topic.setTitle(str(module.get("name", "Unnamed Module")))
            for scenario in module.get("scenarios", []):
                scenario_topic = module_topic.addSubTopic()
                scenario_topic.setTitle(str(scenario.get("name", "Unnamed Scenario")))
                for case in scenario.get("cases", []):
                    case_topic = scenario_topic.addSubTopic()
                    case_topic.setTitle(str(case.get("title", "Untitled Case")))

                    notes = case.get("notes", "")
                    if notes:
                        case_topic.setPlainNotes("注意事项:\n" + str(notes))

                    preconditions = _to_text_list(case.get("preconditions", []))
                    pre_text = "前置条件：无" if not preconditions else "前置条件：" + "；".join(preconditions)
                    pre_topic = case_topic.addSubTopic()
                    pre_topic.setTitle(pre_text)

                    steps = _to_text_list(case.get("steps", []))
                    if not steps:
                        steps_text = "测试步骤：无"
                    else:
                        lines = [f"{idx}. {step}" for idx, step in enumerate(steps, start=1)]
                        steps_text = "测试步骤：\n" + "\n".join(lines)
                    steps_topic = pre_topic.addSubTopic()
                    steps_topic.setTitle(steps_text)
                    expected_topic = steps_topic.addSubTopic()
                    expected_topic.setTitle(f"预期结果: {case.get('expected', '')}")
                    level = _normalize_priority_level(case.get("priority_level", "3"))
                    expected_topic.addMarker(_legacy_marker_id(level))

        xmind.save(workbook, temp_path)
        with zipfile.ZipFile(temp_path, "r") as zf:
            entries = {}
            for name in ("content.xml", "styles.xml", "comments.xml"):
                if name in zf.namelist():
                    entries[name] = zf.read(name)
            return entries
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def export_xmind(data, output_path, sheet_title):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    project = str(data["project"])
    modules = data.get("modules", [])

    passthrough_entries = {}
    metadata = {
        "dataStructureVersion": "2",
        "layoutEngineVersion": "3",
        "creator": {"name": "Codex testcase-xmind-generator", "version": "1.0"},
    }
    manifest = {"file-entries": {"content.json": {}, "metadata.json": {}}}

    template_path = os.environ.get("XMIND_TEMPLATE_PATH", "").strip()
    if not template_path:
        script_dir = Path(__file__).resolve().parent
        skill_template = script_dir.parent / "assets" / "xmind-template.xmind"
        if skill_template.exists():
            template_path = str(skill_template)

    content = _build_content(project=project, modules=modules, sheet_title=sheet_title)

    if template_path and os.path.exists(template_path):
        with zipfile.ZipFile(template_path, "r") as zf:
            names = zf.namelist()
            template_content = None
            if "content.json" in names:
                template_content = json.loads(zf.read("content.json").decode("utf-8"))
            if template_content:
                content = _build_content_with_template(
                    project=project, modules=modules, sheet_title=sheet_title, template_content=template_content
                )
            if "metadata.json" in names:
                metadata = json.loads(zf.read("metadata.json").decode("utf-8"))
            if "manifest.json" in names:
                manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
            for name in names:
                if name in {"content.json", "metadata.json", "manifest.json", "content.xml", "styles.xml", "comments.xml"}:
                    continue
                passthrough_entries[name] = zf.read(name)

    file_entries = manifest.get("file-entries", {})
    file_entries["content.json"] = {}
    file_entries["metadata.json"] = {}
    for name in passthrough_entries:
        file_entries.setdefault(name, {})
    manifest["file-entries"] = file_entries

    legacy_entries = _build_legacy_entries(data, sheet_title)

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("content.json", json.dumps(content, ensure_ascii=False, separators=(",", ":")))
        zf.writestr("metadata.json", json.dumps(metadata, ensure_ascii=False, separators=(",", ":")))
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, separators=(",", ":")))
        for name, raw in passthrough_entries.items():
            zf.writestr(name, raw)
        for name, raw in legacy_entries.items():
            zf.writestr(name, raw)


def main():
    parser = argparse.ArgumentParser(description="Export test-case JSON tree to XMind (JSON format)")
    parser.add_argument("--input", required=True, help="Input case-tree JSON file")
    parser.add_argument("--output", required=False, help="Output .xmind file path or output directory")
    parser.add_argument("--sheet", default="Test Cases", help="XMind sheet title")
    parser.add_argument(
        "--coverage",
        default="output/coverage/coverage-matrix.json",
        help="Coverage matrix JSON path; checked for warning only, does not block export.",
    )
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    _validate(data)
    passed, message = _check_coverage_gate(args.coverage, args.input)
    if not passed:
        print(f"WARN: {message}. Continue export for module/batch output.")
    output_path = _resolve_output_path(args.output, data.get("project", "testcases"))
    export_xmind(data, output_path, args.sheet)
    print(f"OK: generated {os.path.abspath(output_path)}")


if __name__ == "__main__":
    main()
