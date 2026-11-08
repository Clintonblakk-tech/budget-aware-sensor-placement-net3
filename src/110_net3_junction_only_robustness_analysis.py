"""
Paper 2: exact pairwise and permutation robustness analysis
Net3 junction-only budget sensitivity experiment.

Reads the verified run-level CSV and creates a NEW output folder.
It does not modify the original experiment CSVs, model files, reward histories,
or the existing asymptotic statistical-analysis outputs.

Methods:
- Overall three-group test: Kruskal-Wallis statistic with Monte Carlo
  permutation calibration (fixed group sizes; plus-one p-value).
- Pairwise tests: exhaustive exact label-permutation Mann-Whitney U tests.
  With n1=n2=10, all C(20,10)=184,756 allocations are enumerated.
  Average ranks are used, so tied detection rates are handled explicitly.
- Holm adjustment is applied separately to the three pairwise tests for
  each outcome.
- Existing asymptotic tests are included for side-by-side comparison.

Run from the project root with the project's verified Python environment.
"""

from pathlib import Path
from itertools import combinations
import math
import hashlib
import json
import sys
import platform
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import scipy
from scipy import stats
from scipy.stats import rankdata


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = (
    PROJECT_ROOT
    / "Results"
    / "NET3_JUNCTION_ONLY_BUDGET_SENSITIVITY_20261108"
)
RUN_FILE = RESULTS_DIR / "net3_junction_only_run_results.csv"

# New folder: refuses to overwrite any previous robustness output.
OUTPUT_DIR = RESULTS_DIR / "Statistical_Robustness_20261108"

BUDGETS = [3, 5, 8]
EXPECTED_RUNS_PER_BUDGET = 10
EXPECTED_TOTAL_RUNS = 30
EXPECTED_EVENTS_PER_RUN = 20

# Increase to 1,000,000 for final reporting if runtime permits.
# Fixed seed makes the Monte Carlo result reproducible.
KW_PERMUTATIONS = 500_000
PERMUTATION_SEED = 20261108


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def holm_adjust(p_values):
    p = np.asarray(p_values, dtype=float)
    m = len(p)
    order = np.argsort(p)
    adjusted = np.empty(m, dtype=float)
    running = 0.0
    for rank, idx in enumerate(order):
        candidate = (m - rank) * p[idx]
        running = max(running, candidate)
        adjusted[idx] = min(running, 1.0)
    return adjusted


def kw_h_from_rank_sums(ranked_values, sizes, tie_correction):
    n_total = len(ranked_values)
    start = 0
    term = 0.0
    for size in sizes:
        rank_sum = float(np.sum(ranked_values[start:start + size]))
        term += (rank_sum * rank_sum) / size
        start += size
    h_uncorrected = (
        12.0 / (n_total * (n_total + 1.0)) * term
        - 3.0 * (n_total + 1.0)
    )
    return h_uncorrected / tie_correction


def monte_carlo_kw(groups, n_permutations, seed):
    values = np.concatenate(groups)
    sizes = [len(g) for g in groups]
    n_total = len(values)

    # Rank the pooled observations once. Under label permutation, these
    # pooled ranks and the tie correction remain fixed.
    pooled_ranks = rankdata(values, method="average")
    _, tie_counts = np.unique(values, return_counts=True)
    tie_numerator = float(np.sum(tie_counts ** 3 - tie_counts))
    tie_correction = 1.0 - tie_numerator / (n_total ** 3 - n_total)
    observed = kw_h_from_rank_sums(
        pooled_ranks, sizes, tie_correction
    )

    rng = np.random.default_rng(seed)
    exceed = 0

    for _ in range(n_permutations):
        permuted_ranks = rng.permutation(pooled_ranks)
        stat = kw_h_from_rank_sums(
            permuted_ranks, sizes, tie_correction
        )
        if stat >= observed - 1e-12:
            exceed += 1

    # Monte Carlo randomisation p-value with plus-one correction.
    p_value = (exceed + 1) / (n_permutations + 1)
    mc_se = math.sqrt(p_value * (1.0 - p_value) / (n_permutations + 1))
    return observed, p_value, exceed, mc_se


def exact_pairwise_mw(x, y):
    """
    Exhaustive two-sided permutation test of the Mann-Whitney U statistic.
    All allocations of the pooled observations to groups of the observed
    sizes are enumerated. Average ranks correctly accommodate ties.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    n1, n2 = len(x), len(y)
    pooled = np.concatenate([x, y])
    ranks = rankdata(pooled, method="average")
    observed_rank_sum = float(ranks[:n1].sum())
    observed_u = observed_rank_sum - n1 * (n1 + 1) / 2.0
    center = n1 * n2 / 2.0
    observed_distance = abs(observed_u - center)

    total = math.comb(n1 + n2, n1)
    extreme = 0

    # Ranks are fixed for the pooled observations; enumerate every assignment.
    all_indices = range(n1 + n2)
    for selected in combinations(all_indices, n1):
        rank_sum = float(ranks[list(selected)].sum())
        u = rank_sum - n1 * (n1 + 1) / 2.0
        if abs(u - center) >= observed_distance - 1e-12:
            extreme += 1

    p_exact = extreme / total
    rank_biserial = (2.0 * observed_u / (n1 * n2)) - 1.0

    # Conventional asymptotic two-sided Mann-Whitney result for comparison.
    asym = stats.mannwhitneyu(
        x, y, alternative="two-sided", method="asymptotic"
    )

    return {
        "N1": n1,
        "N2": n2,
        "U": observed_u,
        "ExactExtremeAllocations": extreme,
        "ExactTotalAllocations": total,
        "ExactPermutationP": p_exact,
        "AsymptoticP": float(asym.pvalue),
        "RankBiserial": rank_biserial,
        "MeanDifference_Group1MinusGroup2": float(np.mean(x) - np.mean(y)),
        "MedianDifference_Group1MinusGroup2": float(np.median(x) - np.median(y)),
        "UniqueValuesPooled": int(len(np.unique(pooled))),
        "TieCountExcess": int(len(pooled) - len(np.unique(pooled))),
    }


def main():
    if not RUN_FILE.is_file():
        raise FileNotFoundError(
            f"Required input not found:\n{RUN_FILE}\n"
            "Do not use a historical or unrestricted experiment CSV."
        )
    if OUTPUT_DIR.exists():
        raise FileExistsError(
            f"Output folder already exists; refusing to overwrite:\n{OUTPUT_DIR}\n"
            "Choose a new dated OUTPUT_DIR in this script if a rerun is required."
        )

    runs = pd.read_csv(RUN_FILE)

    required = {
        "Network", "CandidateSet", "Budget", "Seed", "Episodes",
        "DetectionRatePercent", "MeanDetectionTimeHours",
        "DetectedEvents", "TotalEvents", "TrainingStatus",
        "TrainingError", "EventErrorCount",
    }
    missing = required - set(runs.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    runs["Budget"] = pd.to_numeric(runs["Budget"], errors="raise").astype(int)
    runs["Seed"] = pd.to_numeric(runs["Seed"], errors="raise").astype(int)
    runs["DetectionRatePercent"] = pd.to_numeric(
        runs["DetectionRatePercent"], errors="raise"
    )
    runs["MeanDetectionTimeHours"] = pd.to_numeric(
        runs["MeanDetectionTimeHours"], errors="coerce"
    )
    runs["DetectedEvents"] = pd.to_numeric(
        runs["DetectedEvents"], errors="raise"
    ).astype(int)
    runs["TotalEvents"] = pd.to_numeric(
        runs["TotalEvents"], errors="raise"
    ).astype(int)
    runs["EventErrorCount"] = pd.to_numeric(
        runs["EventErrorCount"], errors="raise"
    ).astype(int)

    if len(runs) != EXPECTED_TOTAL_RUNS:
        raise ValueError(f"Expected 30 run rows; found {len(runs)}.")
    if set(runs["Budget"]) != set(BUDGETS):
        raise ValueError(f"Unexpected budgets: {sorted(runs['Budget'].unique())}")
    if runs.duplicated(["Budget", "Seed"]).any():
        raise ValueError("Duplicate Budget/Seed run rows found.")
    if not (runs["Network"] == "Net3").all():
        raise ValueError("Non-Net3 records detected.")
    if not (runs["CandidateSet"] == "Junction-only").all():
        raise ValueError("CandidateSet is not uniformly Junction-only.")
    if not (runs["TrainingStatus"] == "COMPLETED").all():
        raise ValueError("At least one training run is not COMPLETED.")
    if runs["TrainingError"].fillna("").astype(str).str.strip().ne("").any():
        raise ValueError("TrainingError contains a non-empty value.")
    if (runs["EventErrorCount"] != 0).any():
        raise ValueError("EventErrorCount is not zero for every run.")
    if (runs["TotalEvents"] != EXPECTED_EVENTS_PER_RUN).any():
        raise ValueError("At least one run does not have exactly 20 events.")
    if not runs["MeanDetectionTimeHours"].notna().all():
        raise ValueError(
            "At least one run has no mean detection time; inspect whether "
            "a run had zero detected events before testing detection time."
        )

    for budget in BUDGETS:
        group = runs.loc[runs["Budget"] == budget]
        if len(group) != EXPECTED_RUNS_PER_BUDGET:
            raise ValueError(
                f"Budget {budget}: expected 10 runs; found {len(group)}."
            )
        if set(group["Seed"]) != set(range(1, 11)):
            raise ValueError(f"Budget {budget}: expected seed labels 1-10.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=False)

    # Preserve input-level run values in output for audit traceability.
    runs.sort_values(["Budget", "Seed"]).to_csv(
        OUTPUT_DIR / "input_run_level_values.csv", index=False
    )

    outcomes = {
        "DetectionRatePercent": "Detection rate (%)",
        "MeanDetectionTimeHours": "Run-level mean detection time (h)",
    }

    overall_rows = []
    pairwise_rows = []

    for outcome_index, (column, label) in enumerate(outcomes.items()):
        groups = [
            runs.loc[runs["Budget"] == b, column].to_numpy(dtype=float)
            for b in BUDGETS
        ]

        asym_kw = stats.kruskal(*groups)
        observed_h, perm_p, exceed, mc_se = monte_carlo_kw(
            groups,
            KW_PERMUTATIONS,
            PERMUTATION_SEED + outcome_index,
        )
        n = sum(len(g) for g in groups)
        k = len(groups)
        epsilon_sq = max(0.0, (observed_h - k + 1) / (n - k))

        overall_rows.append({
            "Outcome": label,
            "NPerBudget": EXPECTED_RUNS_PER_BUDGET,
            "TotalRuns": EXPECTED_TOTAL_RUNS,
            "KruskalWallisH": observed_h,
            "AsymptoticP": float(asym_kw.pvalue),
            "PermutationP": perm_p,
            "PermutationCount": KW_PERMUTATIONS,
            "PermutationExtremeCount": exceed,
            "MonteCarloSE": mc_se,
            "EpsilonSquared": epsilon_sq,
        })

        raw_pairwise = []
        for b1, b2 in [(3, 5), (3, 8), (5, 8)]:
            x = runs.loc[runs["Budget"] == b1, column].to_numpy(dtype=float)
            y = runs.loc[runs["Budget"] == b2, column].to_numpy(dtype=float)
            result = exact_pairwise_mw(x, y)
            raw_pairwise.append((b1, b2, result))

        adjusted = holm_adjust(
            [item[2]["ExactPermutationP"] for item in raw_pairwise]
        )
        asym_adjusted = holm_adjust(
            [item[2]["AsymptoticP"] for item in raw_pairwise]
        )

        for (b1, b2, result), p_holm, p_asym_holm in zip(
            raw_pairwise, adjusted, asym_adjusted
        ):
            pairwise_rows.append({
                "Outcome": label,
                "Comparison": f"{b1} vs {b2}",
                **result,
                "ExactHolmAdjustedP": float(p_holm),
                "AsymptoticHolmAdjustedP": float(p_asym_holm),
                "ExactSignificantAt005": bool(p_holm < 0.05),
                "AsymptoticSignificantAt005": bool(p_asym_holm < 0.05),
            })

    overall_df = pd.DataFrame(overall_rows)
    pairwise_df = pd.DataFrame(pairwise_rows)

    overall_df.to_csv(OUTPUT_DIR / "overall_permutation_tests.csv", index=False)
    pairwise_df.to_csv(OUTPUT_DIR / "pairwise_exact_permutation_tests.csv", index=False)

    # Outcome distribution and tie diagnostics.
    diagnostic_rows = []
    for column, label in outcomes.items():
        for budget in BUDGETS:
            values = runs.loc[runs["Budget"] == budget, column].to_numpy(float)
            unique, counts = np.unique(values, return_counts=True)
            diagnostic_rows.append({
                "Outcome": label,
                "Budget": budget,
                "N": len(values),
                "UniqueValues": len(unique),
                "TieGroups": int(np.sum(counts > 1)),
                "MaximumTieMultiplicity": int(counts.max()),
                "Mean": float(np.mean(values)),
                "SD": float(np.std(values, ddof=1)),
                "Median": float(np.median(values)),
                "Minimum": float(np.min(values)),
                "Maximum": float(np.max(values)),
            })
    pd.DataFrame(diagnostic_rows).to_csv(
        OUTPUT_DIR / "tie_and_distribution_diagnostics.csv", index=False
    )

    report = []
    report.append("PAPER 2 — NET3 JUNCTION-ONLY STATISTICAL ROBUSTNESS CHECK")
    report.append("=" * 68)
    report.append(f"Input: {RUN_FILE}")
    report.append(f"Input SHA-256: {sha256(RUN_FILE)}")
    report.append(f"Output: {OUTPUT_DIR}")
    report.append(f"Generated UTC: {datetime.now(timezone.utc).isoformat()}")
    report.append(f"Python: {sys.version}")
    report.append(f"Platform: {platform.platform()}")
    report.append(f"NumPy: {np.__version__}")
    report.append(f"Pandas: {pd.__version__}")
    report.append(f"SciPy: {scipy.__version__}")
    report.append(f"KW Monte Carlo permutations: {KW_PERMUTATIONS}")
    report.append(f"Permutation RNG seed: {PERMUTATION_SEED}")
    report.append("")
    report.append("VALIDATION: PASSED")
    report.append("30 completed Net3 junction-only runs; 10 per budget.")
    report.append("Seeds 1–10 represented in each budget group.")
    report.append("20 events per run; zero recorded training/event errors.")
    report.append("Original experiment data were read only.")
    report.append("")
    report.append("OVERALL TESTS")
    report.append(overall_df.to_string(index=False))
    report.append("")
    report.append("PAIRWISE EXHAUSTIVE EXACT PERMUTATION TESTS")
    report.append(pairwise_df.to_string(index=False))
    report.append("")
    report.append("INTERPRETATION NOTES")
    report.append(
        "- Overall Kruskal-Wallis p-values are Monte Carlo permutation "
        "estimates with fixed group sizes and plus-one correction."
    )
    report.append(
        "- Pairwise p-values enumerate all 184,756 label allocations for "
        "each 10-versus-10 comparison; average ranks accommodate ties."
    )
    report.append(
        "- Holm adjustment is applied separately to the three pairwise "
        "comparisons for each outcome."
    )
    report.append(
        "- Permutation inference requires exchangeability of run-level "
        "observations under the null. Matching seed labels alone do not "
        "establish paired/common-random-number design."
    )
    report.append(
        "- Detection time remains conditional on detected events and must "
        "be interpreted jointly with detection rate."
    )
    report.append(
        "- These are sensitivity analyses on the retained 30 runs, not "
        "independent replication of the DQN training or EPANET simulations."
    )
    report.append(
        "- With n=10 per group, p-values should be accompanied by effect "
        "sizes and descriptive distributions; do not treat a threshold "
        "crossing as proof of a large or operationally important effect."
    )

    report_path = OUTPUT_DIR / "robustness_analysis_report.txt"
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    # Hash all generated outputs except the manifest itself.
    output_hashes = []
    for path in sorted(OUTPUT_DIR.iterdir()):
        if path.is_file() and path.name != "robustness_manifest.txt":
            output_hashes.append(f"{sha256(path)}  {path.name}")

    manifest = [
        "Paper 2 Net3 junction-only statistical robustness manifest",
        f"Input file: {RUN_FILE}",
        f"Input SHA-256: {sha256(RUN_FILE)}",
        f"Permutation count: {KW_PERMUTATIONS}",
        f"Permutation seed: {PERMUTATION_SEED}",
        "Pairwise exact allocations per comparison: 184756",
        "",
        "Output SHA-256 values:",
        *output_hashes,
    ]
    (OUTPUT_DIR / "robustness_manifest.txt").write_text(
        "\n".join(manifest) + "\n", encoding="utf-8"
    )

    print("\nROBUSTNESS ANALYSIS COMPLETED")
    print(f"Input: {RUN_FILE}")
    print(f"Output folder: {OUTPUT_DIR}")
    print("\nOVERALL TESTS")
    print(overall_df.to_string(index=False))
    print("\nPAIRWISE EXACT TESTS")
    print(pairwise_df[[
        "Outcome", "Comparison", "U", "ExactPermutationP",
        "ExactHolmAdjustedP", "AsymptoticHolmAdjustedP",
        "ExactSignificantAt005", "AsymptoticSignificantAt005"
    ]].to_string(index=False))
    print("\nFiles created:")
    for path in sorted(OUTPUT_DIR.iterdir()):
        print(f"  {path.name} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
