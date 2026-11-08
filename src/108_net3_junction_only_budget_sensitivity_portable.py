"""
108_net3_junction_only_budget_sensitivity.py

Junction-only Net3 budget-sensitivity experiment for Paper 2.

This is a NEW experiment script. It does not modify or overwrite:
- 107_net3_budget_sensitivity_corrected.py
- historical NET3_BUDGET_SENSITIVITY_CORRECTED outputs
- NET3_100MG_L_REEVALUATION_20261107 outputs
- the junction-only smoke-test outputs

Protocol:
- Net3; junction-only DQN candidate set (expected 92 junctions)
- sensor budgets 3, 5, 8
- seeds 1-10; 1,000 episodes per run
- coverage weight 0.70; centrality weight 0.30
- replay buffer and target network enabled
- 20 contamination events per trained placement
- 100 mg/L source = 0.1 kg/m^3 in WNTR's internal concentration units
- 10 mg/L detection threshold = 0.01 kg/m^3
- 24-hour CHEMICAL EPANET quality simulation; 1-hour time steps

IMPORTANT:
The script refuses to start if its dated output directory already exists.
It records run-level and event-level errors rather than silently dropping them.
It does not start automatically when imported.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time
import ast
import platform
import traceback
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import wntr
import torch

# ---------------------------------------------------------------------
# PATHS AND IMPORTS
# ---------------------------------------------------------------------

SCRIPT_PATH = Path(__file__).resolve()
SCRIPT_DIR = SCRIPT_PATH.parent
PROJECT_ROOT = SCRIPT_PATH.parents[1]

if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from dqn_engine_junction_only import run_dqn  # noqa: E402


# ---------------------------------------------------------------------
# EXPERIMENT CONFIGURATION
# ---------------------------------------------------------------------

NETWORK_NAME = "Net3_JunctionOnly"
NETWORK_FILE = PROJECT_ROOT / "networks" / "Net3.inp"

SEEDS = list(range(1, 11))
EPISODES = 1000

BASELINE_BUDGET = 5
BUDGETS = [3, 5, 8]

INJECTIONS_PER_RUN = 20
CONTAMINATION_CONCENTRATION_KG_M3 = 0.1  # 100 mg/L
DETECTION_THRESHOLD_KG_M3 = 0.01         # 10 mg/L

SIMULATION_DURATION_SECONDS = 24 * 3600
HYDRAULIC_TIMESTEP_SECONDS = 3600
QUALITY_TIMESTEP_SECONDS = 3600
REPORT_TIMESTEP_SECONDS = 3600

COVERAGE_WEIGHT = 0.70
CENTRALITY_WEIGHT = 0.30
REPLAY_BUFFER = True
TARGET_NETWORK = True

EXPECTED_JUNCTIONS = 92
EXPECTED_TANKS = 3
EXPECTED_RESERVOIRS = 2

OUTPUT_DIR = PROJECT_ROOT / "results" / "reproduction_runs" / "NET3_JUNCTION_ONLY_BUDGET_SENSITIVITY_20261108"

RUN_RESULTS_FILE = OUTPUT_DIR / "net3_junction_only_run_results.csv"
EVENT_RESULTS_FILE = OUTPUT_DIR / "net3_junction_only_event_results.csv"
SUMMARY_FILE = OUTPUT_DIR / "net3_junction_only_summary.csv"
MANIFEST_FILE = OUTPUT_DIR / "net3_junction_only_manifest.txt"


# ---------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_sensors(value):
    if isinstance(value, (list, tuple, np.ndarray)):
        return [str(x) for x in value]

    if isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, (list, tuple, np.ndarray)):
                return [str(x) for x in parsed]
        except Exception:
            pass

        return [
            item.strip().strip("'\"")
            for item in value.strip("[]").split(",")
            if item.strip()
        ]

    return []


def save_progress(runs, events):
    pd.DataFrame(runs).to_csv(RUN_RESULTS_FILE, index=False)
    pd.DataFrame(events).to_csv(EVENT_RESULTS_FILE, index=False)


def write_manifest(network, engine_path: Path):
    source_nodes = list(network.junction_name_list[:INJECTIONS_PER_RUN])

    lines = [
        "NET3 JUNCTION-ONLY BUDGET-SENSITIVITY EXPERIMENT",
        "Paper: Budget-Aware Explainable Deep Reinforcement Learning for Sensor Placement in Water Distribution Networks",
        f"Created: {datetime.now().astimezone().isoformat()}",
        f"Project root: {PROJECT_ROOT}",
        f"Network file: {NETWORK_FILE}",
        f"Network SHA256: {sha256_file(NETWORK_FILE)}",
        f"Junction-only DQN engine: {engine_path}",
        f"Engine SHA256: {sha256_file(engine_path)}",
        f"Experiment script: {SCRIPT_PATH}",
        f"Experiment script SHA256: {sha256_file(SCRIPT_PATH)}",
        "",
        f"Network: {NETWORK_NAME}",
        f"Total graph nodes: {network.to_graph().number_of_nodes()}",
        f"Junction candidates: {len(network.junction_name_list)}",
        f"Tanks excluded from candidate set: {len(network.tank_name_list)}",
        f"Reservoirs excluded from candidate set: {len(network.reservoir_name_list)}",
        "Candidate eligibility: junctions only (WaterNetworkModel.junction_name_list)",
        f"Budgets: {BUDGETS}",
        f"Baseline budget: {BASELINE_BUDGET}",
        f"Seeds: {SEEDS}",
        f"Episodes per run: {EPISODES}",
        f"Total planned DQN runs: {len(BUDGETS) * len(SEEDS)}",
        f"Coverage weight: {COVERAGE_WEIGHT}",
        f"Centrality weight: {CENTRALITY_WEIGHT}",
        f"Replay buffer: {REPLAY_BUFFER}",
        f"Target network: {TARGET_NETWORK}",
        "DQN architecture: Linear(92,128)-ReLU-Linear(128,64)-ReLU-Linear(64,32)-ReLU-Linear(32,92)",
        "Optimizer: Adam; learning rate: 0.0005",
        "Replay buffer capacity: 50000; batch size: 64",
        "Discount factor: 0.99",
        "Epsilon: 1.0 to 0.01; decay: 0.995",
        "Target network synchronization: every 100 episodes",
        "",
        f"Contamination events per trained placement: {INJECTIONS_PER_RUN}",
        f"Contamination source concentration: {CONTAMINATION_CONCENTRATION_KG_M3} kg/m^3 (= 100 mg/L)",
        f"Detection threshold: {DETECTION_THRESHOLD_KG_M3} kg/m^3 (= 10 mg/L)",
        "Source type: SETPOINT",
        "Contamination pattern: [1] (constant)",
        f"Source junctions: {source_nodes}",
        "Quality parameter: CHEMICAL",
        f"Simulation duration: {SIMULATION_DURATION_SECONDS / 3600:.1f} hours",
        f"Hydraulic timestep: {HYDRAULIC_TIMESTEP_SECONDS / 3600:.1f} hour",
        f"Quality timestep: {QUALITY_TIMESTEP_SECONDS / 3600:.1f} hour",
        f"Report timestep: {REPORT_TIMESTEP_SECONDS / 3600:.1f} hour",
        "Detection rule: any selected sensor concentration strictly greater than threshold",
        "",
        f"Python: {platform.python_version()}",
        f"WNTR: {wntr.__version__}",
        f"PyTorch: {torch.__version__}",
        f"NumPy: {np.__version__}",
        f"Pandas: {pd.__version__}",
        "",
        "Output policy: dated, dedicated directory; script refuses to run if it already exists.",
        "Historical experiment files and prior reevaluation outputs are not modified.",
    ]

    MANIFEST_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def evaluate_contamination(budget, seed, sensors, source_nodes):
    """Evaluate one trained placement over the 20 fixed Net3 junction sources."""
    start = time.time()
    records = []

    for event_no, source_node in enumerate(source_nodes, 1):
        event_start = time.time()
        detected = False
        first_detection_index = np.nan
        first_detection_hours = np.nan
        max_sensor_quality = 0.0
        error = ""

        try:
            wn = wntr.network.WaterNetworkModel(str(NETWORK_FILE))

            wn.options.time.duration = SIMULATION_DURATION_SECONDS
            wn.options.time.hydraulic_timestep = HYDRAULIC_TIMESTEP_SECONDS
            wn.options.time.quality_timestep = QUALITY_TIMESTEP_SECONDS
            wn.options.time.report_timestep = REPORT_TIMESTEP_SECONDS

            wn.options.quality.parameter = "CHEMICAL"
            try:
                wn.options.quality.chemical_name = "Contaminant"
            except Exception:
                pass

            pattern_name = "ContamPattern"
            wn.add_pattern(pattern_name, [1])

            wn.add_source(
                "ContaminationSource",
                source_node,
                "SETPOINT",
                CONTAMINATION_CONCENTRATION_KG_M3,
                pattern_name,
            )

            simulator = wntr.sim.EpanetSimulator(wn)
            result = simulator.run_sim()
            quality = result.node["quality"]

            sensor_series = []
            for sensor in sensors:
                if sensor not in quality.columns:
                    continue

                values = quality[sensor].values.astype(float)
                finite_values = values[np.isfinite(values)]

                if len(finite_values):
                    max_sensor_quality = max(
                        max_sensor_quality,
                        float(np.max(finite_values)),
                    )

                positive = np.where(values > DETECTION_THRESHOLD_KG_M3)[0]
                if len(positive):
                    sensor_series.append((int(positive[0]), sensor))

            if sensor_series:
                sensor_series.sort(key=lambda item: item[0])
                first_detection_index = sensor_series[0][0]
                detected = True
                first_detection_hours = (
                    float(first_detection_index)
                    * REPORT_TIMESTEP_SECONDS
                    / 3600.0
                )

        except Exception as exc:
            error = repr(exc)

        records.append(
            {
                "Network": "Net3",
                "CandidateSet": "Junction-only",
                "Budget": budget,
                "Seed": seed,
                "EventNumber": event_no,
                "SourceNode": str(source_node),
                "Detected": int(detected),
                "FirstDetectionIndex": first_detection_index,
                "FirstDetectionTimeHours": first_detection_hours,
                "MaxSensorQuality_kg_m3": max_sensor_quality,
                "SourceConcentration_kg_m3": CONTAMINATION_CONCENTRATION_KG_M3,
                "DetectionThreshold_kg_m3": DETECTION_THRESHOLD_KG_M3,
                "EventRuntimeSeconds": time.time() - event_start,
                "Error": error,
            }
        )

    return records, time.time() - start


# ---------------------------------------------------------------------
# EXPERIMENT
# ---------------------------------------------------------------------

def main():
    print("=" * 88)
    print("NET3 JUNCTION-ONLY BUDGET-SENSITIVITY EXPERIMENT")
    print("=" * 88)

    # Fail-safe: never reuse or overwrite a previous output directory.
    if OUTPUT_DIR.exists():
        raise SystemExit(
            "STOP: output directory already exists; no experiment was started:\n"
            f"{OUTPUT_DIR}"
        )

    if not NETWORK_FILE.is_file():
        raise FileNotFoundError(f"Net3 network file not found: {NETWORK_FILE}")

    engine_path = SCRIPT_DIR / "dqn_engine_junction_only.py"
    if not engine_path.is_file():
        raise FileNotFoundError(f"Junction-only DQN engine not found: {engine_path}")

    # Preflight the actual network and eligibility pool before creating outputs.
    network = wntr.network.WaterNetworkModel(str(NETWORK_FILE))
    graph = network.to_graph()
    junctions = set(network.junction_name_list)
    tanks = set(network.tank_name_list)
    reservoirs = set(network.reservoir_name_list)

    if len(junctions) != EXPECTED_JUNCTIONS:
        raise RuntimeError(
            f"Expected {EXPECTED_JUNCTIONS} Net3 junctions; found {len(junctions)}."
        )
    if len(tanks) != EXPECTED_TANKS:
        raise RuntimeError(
            f"Expected {EXPECTED_TANKS} Net3 tanks; found {len(tanks)}."
        )
    if len(reservoirs) != EXPECTED_RESERVOIRS:
        raise RuntimeError(
            f"Expected {EXPECTED_RESERVOIRS} Net3 reservoirs; found {len(reservoirs)}."
        )
    if junctions.intersection(tanks | reservoirs):
        raise RuntimeError("Node-type overlap detected in Net3 candidate preflight.")
    if not junctions.issubset(set(graph.nodes())):
        raise RuntimeError("One or more junctions are absent from the Net3 graph.")

    print(f"Network file       : {NETWORK_FILE}")
    print(f"Graph nodes        : {graph.number_of_nodes()}")
    print(f"Junctions eligible : {len(junctions)}")
    print(f"Tanks excluded     : {len(tanks)}")
    print(f"Reservoirs excluded: {len(reservoirs)}")
    print(f"Budgets            : {BUDGETS}")
    print(f"Seeds              : {SEEDS}")
    print(f"Episodes           : {EPISODES}")
    print(f"Planned DQN runs   : {len(BUDGETS) * len(SEEDS)}")
    print(f"Output directory   : {OUTPUT_DIR}")
    print("=" * 88)

    # Create a fresh, unique output directory only after preflight succeeds.
    OUTPUT_DIR.mkdir(parents=True, exist_ok=False)
    write_manifest(network, engine_path)

    # The DQN engine writes model and reward files to its current directory.
    # Change to this dedicated folder so all outputs stay isolated.
    original_cwd = Path.cwd()
    os.chdir(OUTPUT_DIR)

    runs = []
    events = []
    total = len(BUDGETS) * len(SEEDS)
    counter = 0
    source_nodes = list(network.junction_name_list[:INJECTIONS_PER_RUN])

    try:
        for budget in BUDGETS:
            for seed in SEEDS:
                counter += 1
                print()
                print("-" * 80)
                print(
                    f"[{counter}/{total}] Net3 junction-only | "
                    f"budget={budget} | seed={seed}"
                )

                start = time.time()
                try:
                    result = run_dqn(
                        network_name=NETWORK_NAME,
                        network_file=str(NETWORK_FILE),
                        sensor_budget=budget,
                        seed=seed,
                        episodes=EPISODES,
                        coverage_weight=COVERAGE_WEIGHT,
                        centrality_weight=CENTRALITY_WEIGHT,
                        replay_buffer=REPLAY_BUFFER,
                        target_network=TARGET_NETWORK,
                    )

                    measured_runtime = time.time() - start
                    best_reward, final_reward, engine_runtime, sensor_value = result
                    sensors = parse_sensors(sensor_value)

                    # Enforce both the requested budget and junction eligibility.
                    if len(sensors) != budget:
                        raise RuntimeError(
                            f"DQN returned {len(sensors)} sensors for budget {budget}."
                        )
                    invalid_sensors = set(sensors) - junctions
                    if invalid_sensors:
                        raise RuntimeError(
                            f"Non-junction sensor(s) returned: {sorted(invalid_sensors)}"
                        )
                    if len(set(sensors)) != len(sensors):
                        raise RuntimeError("DQN returned duplicate sensor locations.")

                    reward_filename = (
                        f"reward_history_{NETWORK_NAME}_budget_{budget}_seed_{seed}.csv"
                    )
                    model_filename = (
                        f"best_dqn_{NETWORK_NAME}_budget_{budget}_seed_{seed}.pth"
                    )
                    if not Path(reward_filename).is_file():
                        raise FileNotFoundError(
                            f"Expected reward history was not created: {reward_filename}"
                        )
                    if not Path(model_filename).is_file():
                        raise FileNotFoundError(
                            f"Expected model weights were not created: {model_filename}"
                        )

                    print(f"Best reward : {best_reward}")
                    print(f"Final reward: {final_reward}")
                    print(f"Runtime     : {engine_runtime:.3f} s")
                    print(f"Sensors     : {sensors}")
                    print("Candidate validation: PASSED")

                except Exception as exc:
                    error_text = repr(exc)
                    print(f"TRAINING / VALIDATION ERROR: {error_text}")

                    runs.append(
                        {
                            "Network": "Net3",
                            "CandidateSet": "Junction-only",
                            "Budget": budget,
                            "NominalBudgetPercent": 100.0 * budget / BASELINE_BUDGET,
                            "Seed": seed,
                            "Episodes": EPISODES,
                            "BestReward": np.nan,
                            "FinalReward": np.nan,
                            "TrainingRuntimeEngineSeconds": np.nan,
                            "TrainingRuntimeMeasuredSeconds": time.time() - start,
                            "Sensors": "",
                            "SensorCount": 0,
                            "DetectedEvents": np.nan,
                            "TotalEvents": INJECTIONS_PER_RUN,
                            "DetectionRatePercent": np.nan,
                            "MeanDetectionIndex": np.nan,
                            "MeanDetectionTimeHours": np.nan,
                            "EventErrorCount": np.nan,
                            "ContaminationEvaluationRuntimeSeconds": np.nan,
                            "TrainingStatus": "FAILED",
                            "TrainingError": error_text,
                            "RewardHistoryFile": "",
                            "ModelWeightsFile": "",
                        }
                    )
                    save_progress(runs, events)
                    continue

                # Evaluate the trained junction-only placement using 20 events.
                event_records, contamination_runtime = evaluate_contamination(
                    budget, seed, sensors, source_nodes
                )
                events.extend(event_records)
                event_df = pd.DataFrame(event_records)

                detected = int(event_df["Detected"].sum())
                event_error_count = int((event_df["Error"] != "").sum())
                rate = 100.0 * detected / len(event_df) if len(event_df) else np.nan

                detected_indices = (
                    event_df.loc[event_df["Detected"] == 1, "FirstDetectionIndex"]
                    .dropna()
                )
                detected_times = (
                    event_df.loc[event_df["Detected"] == 1, "FirstDetectionTimeHours"]
                    .dropna()
                )

                mean_index = (
                    float(detected_indices.mean()) if len(detected_indices) else np.nan
                )
                mean_time = (
                    float(detected_times.mean()) if len(detected_times) else np.nan
                )

                reward_filename = (
                    f"reward_history_{NETWORK_NAME}_budget_{budget}_seed_{seed}.csv"
                )
                model_filename = (
                    f"best_dqn_{NETWORK_NAME}_budget_{budget}_seed_{seed}.pth"
                )

                runs.append(
                    {
                        "Network": "Net3",
                        "CandidateSet": "Junction-only",
                        "Budget": budget,
                        "NominalBudgetPercent": 100.0 * budget / BASELINE_BUDGET,
                        "Seed": seed,
                        "Episodes": EPISODES,
                        "BestReward": float(best_reward),
                        "FinalReward": float(final_reward),
                        "TrainingRuntimeEngineSeconds": float(engine_runtime),
                        "TrainingRuntimeMeasuredSeconds": float(measured_runtime),
                        "Sensors": str(sensors),
                        "SensorCount": len(sensors),
                        "DetectedEvents": detected,
                        "TotalEvents": len(event_df),
                        "DetectionRatePercent": rate,
                        "MeanDetectionIndex": mean_index,
                        "MeanDetectionTimeHours": mean_time,
                        "EventErrorCount": event_error_count,
                        "ContaminationEvaluationRuntimeSeconds": float(contamination_runtime),
                        "TrainingStatus": "COMPLETED",
                        "TrainingError": "",
                        "RewardHistoryFile": reward_filename,
                        "ModelWeightsFile": model_filename,
                    }
                )

                print(f"Contamination detection: {detected}/{len(event_df)} ({rate:.2f}%)")
                print(f"Event errors            : {event_error_count}")
                print(f"Mean detection time     : {mean_time} h")
                print(f"Contamination runtime   : {contamination_runtime:.3f} s")

                # Persist after each completed run; retain partial progress.
                save_progress(runs, events)

    finally:
        os.chdir(original_cwd)

    # -----------------------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------------------

    run_df = pd.DataFrame(runs)
    event_df = pd.DataFrame(events)

    if len(run_df):
        successful = run_df[run_df["TrainingStatus"] == "COMPLETED"]

        if len(successful):
            summary = (
                successful.groupby("Budget", as_index=False)
                .agg(
                    Runs=("Seed", "count"),
                    MeanBestReward=("BestReward", "mean"),
                    SDBestReward=("BestReward", "std"),
                    MeanFinalReward=("FinalReward", "mean"),
                    SDFinalReward=("FinalReward", "std"),
                    MeanTrainingRuntimeSeconds=("TrainingRuntimeEngineSeconds", "mean"),
                    SDTrainingRuntimeSeconds=("TrainingRuntimeEngineSeconds", "std"),
                    MeanDetectionRatePercent=("DetectionRatePercent", "mean"),
                    SDDetectionRatePercent=("DetectionRatePercent", "std"),
                    MeanDetectionIndex=("MeanDetectionIndex", "mean"),
                    SDDetectionIndex=("MeanDetectionIndex", "std"),
                    MeanDetectionTimeHours=("MeanDetectionTimeHours", "mean"),
                    SDDetectionTimeHours=("MeanDetectionTimeHours", "std"),
                    TotalDetectedEvents=("DetectedEvents", "sum"),
                    TotalEvents=("TotalEvents", "sum"),
                    TotalEventErrors=("EventErrorCount", "sum"),
                    MeanContaminationRuntimeSeconds=(
                        "ContaminationEvaluationRuntimeSeconds", "mean"
                    ),
                    SDContaminationRuntimeSeconds=(
                        "ContaminationEvaluationRuntimeSeconds", "std"
                    ),
                )
            )
            summary.insert(
                1,
                "NominalBudgetPercent",
                summary["Budget"] / BASELINE_BUDGET * 100.0,
            )
        else:
            summary = pd.DataFrame()
    else:
        summary = pd.DataFrame()

    run_df.to_csv(RUN_RESULTS_FILE, index=False)
    event_df.to_csv(EVENT_RESULTS_FILE, index=False)
    summary.to_csv(SUMMARY_FILE, index=False)

    print()
    print("=" * 88)
    print("NET3 JUNCTION-ONLY EXPERIMENT FINISHED")
    print("=" * 88)
    print(f"Run results   : {RUN_RESULTS_FILE}")
    print(f"Event results : {EVENT_RESULTS_FILE}")
    print(f"Summary       : {SUMMARY_FILE}")
    print(f"Manifest      : {MANIFEST_FILE}")
    print()
    print("SUMMARY")
    print(summary.to_string(index=False) if len(summary) else "No successful runs.")
    print()
    print("Check completion counts and event errors before interpreting results.")
    print("Detection uses sensor quality > 0.01 kg/m^3 (10 mg/L).")
    print("Source concentration is 0.1 kg/m^3 (100 mg/L).")


def cli_main():
    global OUTPUT_DIR, RUN_RESULTS_FILE, EVENT_RESULTS_FILE
    global SUMMARY_FILE, MANIFEST_FILE
    parser = argparse.ArgumentParser(
        description="Net3 junction-only budget-sensitivity experiment."
    )
    parser.add_argument(
        "--confirm-run",
        action="store_true",
        help="Explicitly authorise all 30 DQN training runs."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_DIR,
        help="Dedicated output directory for this reproduction run."
    )

    args = parser.parse_args()

    if not args.confirm_run:
        parser.print_help()
        print("\nNo experiment started. Use --confirm-run to authorise training.")
        return

    OUTPUT_DIR = args.output.expanduser().resolve()
    RUN_RESULTS_FILE = OUTPUT_DIR / "net3_junction_only_run_results.csv"
    EVENT_RESULTS_FILE = OUTPUT_DIR / "net3_junction_only_event_results.csv"
    SUMMARY_FILE = OUTPUT_DIR / "net3_junction_only_summary.csv"
    MANIFEST_FILE = OUTPUT_DIR / "net3_junction_only_manifest.txt"

    main()


if __name__ == "__main__":
    cli_main()
