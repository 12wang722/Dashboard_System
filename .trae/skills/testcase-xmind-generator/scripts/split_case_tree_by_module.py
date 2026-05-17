import argparse
import json
import re
from pathlib import Path


def _safe_name(name):
    value = str(name).strip()
    value = re.sub(r'[\\/:*?"<>|]+', "_", value)
    value = re.sub(r"\s+", "_", value)
    value = value.strip("._ ")
    return value or "module"


def main():
    parser = argparse.ArgumentParser(
        description="Split case-tree JSON into per-module case-tree files."
    )
    parser.add_argument("--input", required=True, help="Input case-tree JSON")
    parser.add_argument("--output-dir", required=True, help="Output directory for module case-tree files")
    args = parser.parse_args()

    src = Path(args.input)
    out_dir = Path(args.output_dir)
    data = json.loads(src.read_text(encoding="utf-8"))

    project = data.get("project", "Project")
    modules = data.get("modules", [])
    out_dir.mkdir(parents=True, exist_ok=True)

    generated = []
    for idx, module in enumerate(modules, start=1):
        module_name = module.get("name", f"Module-{idx}")
        filename = f"{idx:02d}_{_safe_name(module_name)}.json"
        out_path = out_dir / filename
        per_module = {
            "project": project,
            "modules": [module],
        }
        out_path.write_text(json.dumps(per_module, ensure_ascii=False, indent=2), encoding="utf-8")
        generated.append(out_path)

    print(f"OK: split into {len(generated)} file(s) under {out_dir.resolve()}")
    for p in generated:
        print(f"- {p.resolve()}")


if __name__ == "__main__":
    main()
