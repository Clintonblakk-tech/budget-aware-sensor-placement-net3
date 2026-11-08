"""
Paper 2: Net3 Junction-Only Budget Sensitivity
Statistical Analysis

Input:
    net3_junction_only_run_results.csv

Outputs:
    Statistical_Analysis/
        descriptive_statistics.csv
        kruskal_wallis_results.csv
        pairwise_mann_whitney_results.csv
        statistical_analysis_report.txt

The original experimental files are read-only.
"""

from pathlib import Path
from itertools import combinations
from datetime import datetime
import platform
import sys

import numpy as np
import pandas as pd
import scipy
from scipy import stats


# ============================================================
# 1. PATHS AND CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

EXPERIMENT_DIR = (
    PROJECT_ROOT
    / "Results"
    / "NET3_JUNCTION_ONLY_BUDGET_SENSITIVITY_20261108"
)

INPUT_FILE = EXPERIMENT_DIR / "net3_junction_only_run_results.csv"

OUTPUT_DIR = EXPERIMENT_DIR / "Statistical_Analysis"

BUDGETS = [3, 5, 8]

OUTCOMES = {
    "DetectionRatePercent": "Detection rate (%)",
    "MeanDetectionTimeHours": "Mean detection time (hours)"
}

ALPHA = 0.05


# ============================================================
# 2. VALIDATE INPUT
# ============================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Required input file not found: {INPUT_FILE}"
    )

if OUTPUT_DIR.exists():
    raise FileExistsError(
        "The statistical output directory already exists. "
        "To preserve previous results, this script will not "
        "overwrite it:\n"
        f"{OUTPUT_DIR}"
    )

OUTPUT_DIR.mkdir(parents=True, exist_ok=False)

df = pd.read_csv(INPUT_FILE)

required_columns = [
    "Budget",
    "Seed",
    "DetectionRatePercent",
    "MeanDetectionTimeHours"
]

missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

df["Budget"] = pd.to_numeric(df["Budget"], errors="raise")

for col in required_columns[1:]:
    df[col] = pd.to_numeric(df[col], errors="raise")

if len(df) != 30:
    raise ValueError(
        f"Expected 30 training runs, but found {len(df)}."
    )

for budget in BUDGETS:
    group = df[df["Budget"] == budget]

    if len(group) != 10:
        raise ValueError(
            f"Budget {budget}: expected 10 runs, found {len(group)}."
        )

    if group["Seed"].nunique() != 10:
        raise ValueError(
            f"Budget {budget}: expected 10 unique seeds."
        )

if df.duplicated(subset=["Budget", "Seed"]).any():
    raise ValueError(
        "Duplicate budget-seed combinations detected."
    )

print("INPUT VALIDATION: PASSED")
print(f"Training runs: {len(df)}")
print(f"Budgets: {BUDGETS}")


# ============================================================
# 3. DESCRIPTIVE STATISTICS
# ============================================================

descriptive_rows = []

for outcome, label in OUTCOMES.items():

    for budget in BUDGETS:

        values = (
            df.loc[df["Budget"] == budget, outcome]
            .dropna()
            .to_numpy(dtype=float)
        )

        if len(values) != 10:
            raise ValueError(
                f"Unexpected number of valid observations for "
                f"{label}, budget {budget}."
            )

        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)

        descriptive_rows.append({
            "Outcome": label,
            "Budget": budget,
            "N": len(values),
            "Mean": np.mean(values),
            "SD": np.std(values, ddof=1),
            "Median": np.median(values),
            "Q1": q1,
            "Q3": q3,
            "IQR": q3 - q1,
            "Minimum": np.min(values),
            "Maximum": np.max(values)
        })

descriptive_df = pd.DataFrame(descriptive_rows)

descriptive_df.to_csv(
    OUTPUT_DIR / "descriptive_statistics.csv",
    index=False
)


# ============================================================
# 4. KRUSKAL-WALLIS TESTS
# ============================================================

kw_rows = []

for outcome, label in OUTCOMES.items():

    groups = [
        df.loc[df["Budget"] == budget, outcome]
        .dropna()
        .to_numpy(dtype=float)
        for budget in BUDGETS
    ]

    statistic, p_value = stats.kruskal(*groups)

    n_total = sum(len(group) for group in groups)
    k = len(groups)

    # Kruskal-Wallis epsilon-squared effect size
    epsilon_squared = max(
        0.0,
        (statistic - k + 1) / (n_total - k)
    )

    kw_rows.append({
        "Outcome": label,
        "Test": "Kruskal-Wallis H",
        "H_statistic": statistic,
        "Degrees_of_freedom": k - 1,
        "P_value": p_value,
        "Epsilon_squared": epsilon_squared,
        "Significant_at_0.05": p_value < ALPHA
    })

kw_df = pd.DataFrame(kw_rows)

kw_df.to_csv(
    OUTPUT_DIR / "kruskal_wallis_results.csv",
    index=False
)


# ============================================================
# 5. PAIRWISE MANN-WHITNEY U TESTS
# ============================================================

pairwise_rows = []

for outcome, label in OUTCOMES.items():

    raw_results = []

    for budget_a, budget_b in combinations(BUDGETS, 2):

        group_a = (
            df.loc[df["Budget"] == budget_a, outcome]
            .dropna()
            .to_numpy(dtype=float)
        )

        group_b = (
            df.loc[df["Budget"] == budget_b, outcome]
            .dropna()
            .to_numpy(dtype=float)
        )

        result = stats.mannwhitneyu(
            group_a,
            group_b,
            alternative="two-sided",
            method="asymptotic"
        )

        u_statistic = result.statistic
        p_value = result.pvalue

        # Rank-biserial correlation effect size
        rank_biserial = (
            (2 * u_statistic) / (len(group_a) * len(group_b))
        ) - 1

        raw_results.append({
            "Outcome": label,
            "Comparison": f"{budget_a} vs {budget_b}",
            "Budget_A": budget_a,
            "Budget_B": budget_b,
            "U_statistic": u_statistic,
            "P_value": p_value,
            "Rank_biserial_correlation": rank_biserial
        })

    # Holm multiple-comparison correction
    p_values = np.array(
        [item["P_value"] for item in raw_results]
    )

    m = len(p_values)
    order = np.argsort(p_values)

    adjusted = np.empty(m)
    running_max = 0.0

    for rank, index in enumerate(order):

        adjusted_value = (
            (m - rank) * p_values[index]
        )

        running_max = max(
            running_max,
            adjusted_value
        )

        adjusted[index] = min(1.0, running_max)

    for index, item in enumerate(raw_results):

        item["Holm_adjusted_P_value"] = adjusted[index]

        item["Significant_after_Holm"] = (
            adjusted[index] < ALPHA
        )

        pairwise_rows.append(item)


pairwise_df = pd.DataFrame(pairwise_rows)

pairwise_df.to_csv(
    OUTPUT_DIR / "pairwise_mann_whitney_results.csv",
    index=False
)


# ============================================================
# 6. GENERATE TEXT REPORT
# ============================================================

report_file = OUTPUT_DIR / "statistical_analysis_report.txt"

with open(report_file, "w", encoding="utf-8") as report:

    report.write(
        "STATISTICAL ANALYSIS REPORT\n"
        "Paper 2: Budget-Aware Explainable Deep Reinforcement "
        "Learning for Sensor Placement in Water Distribution Networks\n"
    )

    report.write("=" * 75 + "\n\n")

    report.write(
        f"Analysis date: {datetime.now().isoformat()}\n"
    )

    report.write(
        f"Input file: {INPUT_FILE}\n"
    )

    report.write(
        f"Python version: {sys.version}\n"
    )

    report.write(
        f"Platform: {platform.platform()}\n"
    )

    report.write(
        f"NumPy version: {np.__version__}\n"
    )

    report.write(
        f"Pandas version: {pd.__version__}\n"
    )

    report.write(
        f"SciPy version: {scipy.__version__}\n\n"
    )

    report.write("EXPERIMENTAL UNIT\n")
    report.write("-" * 75 + "\n")

    report.write(
        "The independent unit of replication is the trained DQN run. "
        "There are ten runs per sensor budget and thirty runs overall. "
        "The 200 contamination events evaluated per budget are not "
        "treated as 200 independent training replicates.\n\n"
    )

    report.write("DESCRIPTIVE STATISTICS\n")
    report.write("-" * 75 + "\n")

    report.write(
        descriptive_df.to_string(index=False)
    )

    report.write("\n\nKRUSKAL-WALLIS TESTS\n")
    report.write("-" * 75 + "\n")

    report.write(
        kw_df.to_string(index=False)
    )

    report.write("\n\nPAIRWISE MANN-WHITNEY TESTS\n")
    report.write("-" * 75 + "\n")

    report.write(
        pairwise_df.to_string(index=False)
    )

    report.write("\n\nSTATISTICAL INTERPRETATION\n")
    report.write("-" * 75 + "\n")

    for _, row in kw_df.iterrows():

        report.write(
            f"\n{row['Outcome']}: "
            f"Kruskal-Wallis H = {row['H_statistic']:.4f}, "
            f"df = {int(row['Degrees_of_freedom'])}, "
            f"p = {row['P_value']:.6f}.\n"
        )

        if row["P_value"] < ALPHA:
            report.write(
                "There is evidence of a difference among "
                "the budget groups.\n"
            )
        else:
            report.write(
                "There is insufficient evidence of a difference "
                "among the budget groups.\n"
            )

    report.write(
        "\nPairwise comparisons use two-sided Mann-Whitney U tests "
        "with Holm correction across the three budget comparisons "
        "within each outcome.\n"
    )

    report.write(
        "\nDetection-time results are conditional on successful "
        "detection. Events that were not detected do not contribute "
        "a detection time. This outcome must therefore be interpreted "
        "alongside detection rate.\n"
    )

    report.write(
        "\nThese tests assess differences among the three Net3 "
        "junction-only budget groups. They do not establish "
        "generalisability to other water distribution networks.\n"
    )

    report.write(
        "\nThe tests use asymptotic p-values. With ten independent "
        "training runs per group, inferential findings should be "
        "interpreted cautiously.\n"
    )

    report.write(
        "\nThis report is a derived statistical analysis of the "
        "existing experiment. It does not rerun DQN training or "
        "modify original experimental records.\n"
    )


# ============================================================
# 7. COMPLETION SUMMARY
# ============================================================

print("\nSTATISTICAL ANALYSIS COMPLETED")
print("=" * 60)

print("\nDESCRIPTIVE STATISTICS:")
print(descriptive_df.to_string(index=False))

print("\nKRUSKAL-WALLIS RESULTS:")
print(kw_df.to_string(index=False))

print("\nPAIRWISE MANN-WHITNEY RESULTS:")
print(pairwise_df.to_string(index=False))

print("\nOUTPUT FILES:")
for path in sorted(OUTPUT_DIR.iterdir()):
    print(f"{path.name} ({path.stat().st_size:,} bytes)")

print("\nSTATISTICAL ANALYSIS: COMPLETED SUCCESSFULLY")