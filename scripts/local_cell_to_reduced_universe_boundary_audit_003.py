#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_001 = ROOT / "artifacts/json/project_creation_001.v1.json"
IN_002 = ROOT / "artifacts/json/local_cell_to_reduced_universe_derivation_002.v1.json"
PAPER_MAIN = ROOT / "paper/main.tex"
PAPER_DIR = ROOT / "paper/sections"

OUT_JSON = ROOT / "artifacts/json/local_cell_to_reduced_universe_boundary_audit_003.v1.json"
OUT_NOTE = ROOT / "notes/local_cell_to_reduced_universe_boundary_audit_003.md"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    a001 = load_json(IN_001)
    a002 = load_json(IN_002)

    main_text = PAPER_MAIN.read_text(encoding="utf-8")
    paper_text = "\n".join(
        p.read_text(encoding="utf-8")
        for p in sorted(PAPER_DIR.glob("*.tex"))
    )

    required_closed_phrases = [
        "reduced 16-candidate universe",
        "Project 22 local-cell kernel",
        "two readouts",
        "hidden diagonal",
        "[1,6,8,15]",
    ]

    required_boundary_phrases = [
        "does not yet derive the local answer-cell kernel from native G60 provenance",
        "does not derive the full role-labeled shared\\_B edge universe",
        "does not close Gap A",
    ]

    missing_closed = [p for p in required_closed_phrases if p not in paper_text]
    missing_boundary = [p for p in required_boundary_phrases if p not in paper_text]

    forbidden_unqualified = [
        "Gap A is closed",
        "closes Gap A",
        "full G60-native generator",
        "derives the local answer-cell kernel from native G60 provenance",
        "derives the full role-labeled shared\\_B edge universe",
    ]

    forbidden_hits = []
    for phrase in forbidden_unqualified:
        idx = paper_text.find(phrase)
        while idx >= 0:
            window = paper_text[max(0, idx - 60):idx + len(phrase) + 60]
            negated = (
                "does not " in window
                or "not " in window
                or "does not yet " in window
                or "not yet " in window
            )
            if not negated:
                forbidden_hits.append(phrase)
                break
            idx = paper_text.find(phrase, idx + 1)

    checks = {
        "project_creation_status_ok": a001.get("status") == "local_cell_to_reduced_universe_project_created",
        "derivation_002_theorem_pass": bool(a002.get("theorem_pass")),
        "derivation_002_candidate_count_16": a002.get("candidate_count") == 16,
        "derivation_002_diagonal_exact": a002.get("diagonal_indices") == [1, 6, 8, 15],
        "derivation_002_visible_permutation_exact": a002.get("visible_permutation") == [1, 2, 0, 3],
        "main_has_all_sections": all(
            f"\\input{{sections/{name}}}" in main_text
            for name in [
                "00_abstract",
                "01_introduction",
                "02_project22_checkpoint",
                "03_readout_product",
                "04_diagonal_selector",
                "05_reduced_universe_theorem",
                "06_boundary_and_next_problem",
                "07_conclusion",
            ]
        ),
        "required_closed_phrases_present": len(missing_closed) == 0,
        "required_boundary_phrases_present": len(missing_boundary) == 0,
        "forbidden_unqualified_claims_absent": len(forbidden_hits) == 0,
    }

    boundary_pass = all(checks.values())

    result = {
        "status": "local_cell_to_reduced_universe_boundary_audit_recorded",
        "audit_id": "003",
        "inputs": {
            "001": str(IN_001),
            "002": str(IN_002),
            "paper_main": str(PAPER_MAIN),
            "paper_sections": str(PAPER_DIR),
        },
        "checks": checks,
        "missing_closed_phrases": missing_closed,
        "missing_boundary_phrases": missing_boundary,
        "forbidden_hits": forbidden_hits,
        "boundary_pass": boundary_pass,
        "closed_statement": (
            "Project 23 derives the reduced 16-candidate universe as the product of two readouts "
            "of the Project 22 local-cell kernel, with hidden diagonal [1,6,8,15] and visible "
            "permutation [1,2,0,3]."
        ),
        "open_boundary": (
            "The derivation remains conditional on the Project 22 local-cell kernel. It does not derive "
            "that kernel from native G60 provenance, does not derive the full role-labeled shared_B edge "
            "universe, and does not close Gap A."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = []
    lines.append("# Local cell to reduced universe boundary audit 003")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Closed statement")
    lines.append("")
    lines.append(result["closed_statement"])
    lines.append("")
    lines.append("## Open boundary")
    lines.append("")
    lines.append(result["open_boundary"])
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("- boundary_pass: `" + str(boundary_pass) + "`")
    lines.append("")
    lines.append("## Missing closed phrases")
    lines.append("")
    if missing_closed:
        for p in missing_closed:
            lines.append("- `" + p + "`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Missing boundary phrases")
    lines.append("")
    if missing_boundary:
        for p in missing_boundary:
            lines.append("- `" + p + "`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Forbidden unqualified hits")
    lines.append("")
    if forbidden_hits:
        for p in forbidden_hits:
            lines.append("- `" + p + "`")
    else:
        lines.append("- none")
    lines.append("")

    OUT_NOTE.write_text("\n".join(lines), encoding="utf-8")

    print("wrote", OUT_JSON)
    print("wrote", OUT_NOTE)
    print("status", result["status"])
    print("boundary_pass", boundary_pass)
    for k, v in checks.items():
        print(k, v)


if __name__ == "__main__":
    main()
