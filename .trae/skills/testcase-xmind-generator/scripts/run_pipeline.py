import argparse
import subprocess
import sys
from pathlib import Path


def _run(cmd):
    print(">>", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr.strip(), file=sys.stderr)
        raise SystemExit(result.returncode)


def main():
    parser = argparse.ArgumentParser(
        description="Run quality validation and coverage checks for testcase-xmind case trees."
    )
    parser.add_argument("--requirements-index", required=True, help="Requirements index JSON path")
    parser.add_argument("--case-tree", required=True, help="Case-tree JSON path")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    py = sys.executable

    coverage = Path("output/coverage/coverage-matrix.json")

    _run([py, str(script_dir / "normalize_case_tree.py"), "--input", args.case_tree])
    _run([py, str(script_dir / "quality_gate.py"), "--input", args.case_tree])
    _run(
        [
            py,
            str(script_dir / "build_coverage_matrix.py"),
            "--requirements",
            args.requirements_index,
            "--cases",
            args.case_tree,
            "--output",
            str(coverage),
        ]
    )
    _run([py, str(script_dir / "coverage_gate.py"), "--input", str(coverage)])


if __name__ == "__main__":
    main()
