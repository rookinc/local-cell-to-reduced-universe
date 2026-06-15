#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IN_003 = ROOT / "source/project22_artifacts/json/lift_twist_two_readout_universe_003.v1.json"
IN_004 = ROOT / "source/project22_artifacts/json/lift_twist_readout_order_rule_004.v1.json"
IN_011 = ROOT / "source/project22_artifacts/json/lift_twist_local_answer_cell_generator_theorem_011.v1.json"
IN_014 = ROOT / "source/project22_artifacts/json/local_cell_theorem_boundary_audit_014.v1.json"

OUT_JSON = ROOT / "artifacts/json/local_cell_to_reduced_universe_derivation_002.v1.json"
OUT_CSV = ROOT / "artifacts/csv/local_cell_to_reduced_universe_derivation_002.v1.csv"
OUT_NOTE = ROOT / "notes/local_cell_to_reduced_universe_derivation_002.md"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def state_key_for_c(row):
    shell_order = {"ordinary": 0, "branch": 1}
    return (shell_order[row["shell"]], int(row["rank"]))


def state_key_for_anchor(row):
    # Lift & Twist anchor readout:
    # first branch rank wraps to front,
    # ordinary ranks follow,
    # remaining branch rank stays terminal.
    if row["shell"] == "branch" and int(row["rank"]) == 0:
        return (0, 0)
    if row["shell"] == "ordinary":
        return (1, int(row["rank"]))
    return (2, int(row["rank"]))


def main():
    a003 = load_json(IN_003)
    a004 = load_json(IN_004)
    a011 = load_json(IN_011)
    a014 = load_json(IN_014)

    if not a011.get("theorem_pass"):
        raise SystemExit("Project22 011 theorem_pass is not true")
    if not a014.get("boundary_pass"):
        raise SystemExit("Project22 014 boundary_pass is not true")

    local_rows = list(a011["generated_rows"])

    c_readout = sorted(local_rows, key=state_key_for_c)
    anchor_readout = sorted(local_rows, key=state_key_for_anchor)

    c_order = [r["state"] for r in c_readout]
    anchor_order = [r["state"] for r in anchor_readout]

    candidates = []
    for c_index, c in enumerate(c_readout):
        for a_index, a in enumerate(anchor_readout):
            candidate_index = 4 * c_index + a_index
            hidden_diagonal = c["state"] == a["state"]
            candidates.append({
                "candidate_index": candidate_index,
                "c_index": c_index,
                "anchor_index": a_index,
                "c_state": c["state"],
                "anchor_state": a["state"],
                "hidden_diagonal": hidden_diagonal,
                "c_key": c["c_key"],
                "anchor_key": a["anchor_key"],
                "c_path": c["c_path"],
                "anchor_residues": a["anchor_residues"],
                "c_anchor_overlap": sorted(set(c["c_values"]).intersection(a["anchor_residues"])),
            })

    generated_indices = sorted(x["candidate_index"] for x in candidates)
    diagonal_indices = sorted(x["candidate_index"] for x in candidates if x["hidden_diagonal"])

    visible_permutation = []
    for c in c_readout:
        anchor_index = next(i for i, a in enumerate(anchor_readout) if a["state"] == c["state"])
        visible_permutation.append(anchor_index)

    expected_indices = list(range(16))
    expected_diagonal = [1, 6, 8, 15]
    expected_permutation = [1, 2, 0, 3]

    checks = {
        "project22_011_theorem_pass": bool(a011.get("theorem_pass")),
        "project22_014_boundary_pass": bool(a014.get("boundary_pass")),
        "c_order_matches_project22_003": c_order == a003["c_readout_order"],
        "anchor_order_matches_project22_003": anchor_order == a003["anchor_readout_order"],
        "derived_c_order_matches_project22_004": c_order == a004["derived_c_order"],
        "derived_anchor_order_matches_project22_004": anchor_order == a004["derived_anchor_order"],
        "candidate_count_is_16": len(candidates) == 16,
        "candidate_indices_are_0_to_15": generated_indices == expected_indices,
        "diagonal_indices_match_expected": diagonal_indices == expected_diagonal,
        "visible_permutation_matches_expected": visible_permutation == expected_permutation,
        "project22_003_diagonal_matches": diagonal_indices == a003["hidden_diagonal_indices"],
        "project22_003_actual_selected_matches": diagonal_indices == a003["actual_selected_indices"],
    }

    theorem_pass = all(checks.values())

    result = {
        "status": "local_cell_to_reduced_universe_derivation_recorded",
        "audit_id": "002",
        "inputs": {
            "project22_003": str(IN_003),
            "project22_004": str(IN_004),
            "project22_011": str(IN_011),
            "project22_014": str(IN_014),
        },
        "c_readout_order": c_order,
        "anchor_readout_order": anchor_order,
        "candidate_count": len(candidates),
        "candidate_indices": generated_indices,
        "visible_permutation": visible_permutation,
        "diagonal_indices": diagonal_indices,
        "expected_diagonal_indices": expected_diagonal,
        "expected_visible_permutation": expected_permutation,
        "candidates": candidates,
        "checks": checks,
        "theorem_pass": theorem_pass,
        "claim": (
            "The Project 22 local answer-cell kernel generates the reduced 16-candidate universe as "
            "the product of two readouts. The C readout orders states O0,O1,B0,B1. The anchor readout "
            "orders the same states B0,O0,O1,B1. Their product contains candidates 0..15, and the hidden "
            "identity diagonal selects exactly [1,6,8,15], appearing visibly as [1,2,0,3]."
        ),
        "boundary": (
            "This derives the reduced 16-candidate universe from the copied Project 22 local-cell kernel. "
            "It does not derive that local-cell kernel from native G60 provenance, does not derive the full "
            "role-labeled shared_B edge universe, and does not close Gap A."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_NOTE.parent.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "candidate_index",
            "c_index",
            "anchor_index",
            "c_state",
            "anchor_state",
            "hidden_diagonal",
            "c_key",
            "anchor_key",
            "overlap",
        ])
        for row in candidates:
            w.writerow([
                row["candidate_index"],
                row["c_index"],
                row["anchor_index"],
                row["c_state"],
                row["anchor_state"],
                "1" if row["hidden_diagonal"] else "0",
                row["c_key"],
                row["anchor_key"],
                " ".join(str(x) for x in row["c_anchor_overlap"]) or "none",
            ])

    lines = []
    lines.append("# Local cell to reduced universe derivation 002")
    lines.append("")
    lines.append("Status: " + result["status"])
    lines.append("")
    lines.append("## Claim")
    lines.append("")
    lines.append(result["claim"])
    lines.append("")
    lines.append("## Readouts")
    lines.append("")
    lines.append("- C readout order: `" + str(c_order) + "`")
    lines.append("- anchor readout order: `" + str(anchor_order) + "`")
    lines.append("")
    lines.append("## Derived universe")
    lines.append("")
    lines.append("- candidate_count: `" + str(len(candidates)) + "`")
    lines.append("- candidate_indices: `" + str(generated_indices) + "`")
    lines.append("- visible_permutation: `" + str(visible_permutation) + "`")
    lines.append("- diagonal_indices: `" + str(diagonal_indices) + "`")
    lines.append("")
    lines.append("## Candidate table")
    lines.append("")
    lines.append("| candidate | C state | anchor state | diagonal | overlap |")
    lines.append("|---:|---|---|---:|---|")
    for row in candidates:
        overlap = " ".join(str(x) for x in row["c_anchor_overlap"]) or "none"
        lines.append(
            "| " + str(row["candidate_index"])
            + " | " + row["c_state"]
            + " | " + row["anchor_state"]
            + " | " + ("1" if row["hidden_diagonal"] else "0")
            + " | " + overlap
            + " |"
        )
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    for k, v in checks.items():
        lines.append("- " + k + ": `" + str(v) + "`")
    lines.append("- theorem_pass: `" + str(theorem_pass) + "`")
    lines.append("")
    lines.append("## Boundary")
    lines.append("")
    lines.append(result["boundary"])
    lines.append("")

    OUT_NOTE.write_text("\n".join(lines), encoding="utf-8")

    print("wrote", OUT_JSON)
    print("wrote", OUT_CSV)
    print("wrote", OUT_NOTE)
    print("status", result["status"])
    print("theorem_pass", theorem_pass)
    print("c_readout_order", c_order)
    print("anchor_readout_order", anchor_order)
    print("candidate_count", len(candidates))
    print("visible_permutation", visible_permutation)
    print("diagonal_indices", diagonal_indices)


if __name__ == "__main__":
    main()
