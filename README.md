# Budget-Aware Explainable Deep Reinforcement Learning for Sensor Placement in Water Distribution Networks

## 1. Overview

This repository contains the experimental implementation, trained models, experimental results, statistical analyses, and supporting documentation for a budget-aware Deep Q-Network (DQN) approach to sensor placement in water distribution networks (WDNs).

The study investigates the effect of sensor installation budgets on contamination detection performance using the Net3 benchmark network.

**Scope note:** The packaged experiment and results described in this README document budget-aware DQN sensor placement and contamination-detection evaluation. This README does not identify a specific explainability method or report explainability outputs. The word “Explainable” in the repository title should therefore not be taken, on the evidence documented here alone, as proof that an explainability method was implemented or evaluated. Any explainability claim should be supported by the corresponding source code, outputs and methodological documentation.

Three sensor budgets are evaluated:
- 3 sensors
- 5 sensors
- 8 sensors

Candidate sensor locations are restricted to the 92 junction nodes of Net3. Tanks and reservoirs are excluded.

The repository is intended to support transparent inspection, computational reproduction, statistical evaluation, and verification of experimental evidence.

## 2. Research objectives

The experiment investigates:

1. The relationship between sensor budget and contamination detection performance.
2. Differences in detection performance across sensor budgets.
3. The effect of sensor budget on DQN training runtime.
4. Variability across ten random seeds.
5. The statistical robustness of observed differences.

## 3. Experimental design

| Parameter | Configuration |
|---|---|
| Benchmark network | Net3 |
| Network file | networks/Net3.inp |
| Total network nodes | 97 |
| Junction candidates | 92 |
| Excluded tanks | 3 |
| Excluded reservoirs | 2 |
| Sensor budgets | 3, 5, 8 |
| Baseline budget | 5 |
| Random seeds | 1–10 |
| Episodes per run | 1,000 |
| Total DQN runs | 30 |
| Coverage weight | 0.70 |
| Centrality weight | 0.30 |
| Replay buffer | Enabled |
| Target network | Enabled |
| Contamination events per placement | 20 |
| Simulation duration | 24 hours |
| Hydraulic timestep | 1 hour |
| Water-quality timestep | 1 hour |

### DQN architecture

The neural network architecture is:

`Linear(92,128) → ReLU → Linear(128,64) → ReLU → Linear(64,32) → ReLU → Linear(32,92)`

Recorded training parameters:

| Parameter | Value |
|---|---:|
| Optimizer | Adam |
| Learning rate | 0.0005 |
| Replay buffer capacity | 50,000 |
| Batch size | 64 |
| Discount factor | 0.99 |
| Initial epsilon | 1.0 |
| Minimum epsilon | 0.01 |
| Epsilon decay | 0.995 |
| Target-network synchronization | Every 100 episodes |

### Contamination simulation

The evaluation uses:

- Source type: SETPOINT
- Quality parameter: CHEMICAL
- Source concentration: 0.1 kg/m³ (100 mg/L)
- Contamination pattern: constant (`[1]`)
- Detection threshold: 0.01 kg/m³ (10 mg/L)
- Contamination source junctions: 20 (`10`, `15`, `20`, `35`, `40`, `50`, `60`, `601`, `61`, `101`, `103`, `105`, `107`, `109`, `111`, `113`, `115`, `117`, `119`, `120`)
- Report timestep: 1 hour
- Detection rule: at least one selected sensor must record a concentration strictly greater than the detection threshold.

The sanitised public reproducibility manifest is `configurations/net3_junction_only_manifest_public.txt`. It preserves the recorded experiment settings and source-file fingerprints while replacing machine-specific absolute paths with repository-relative paths. The legacy manifest copies retained in `configurations/` and `results/` have also been sanitised to prevent local filesystem paths from appearing in the current repository tree.


## 4. Repository structure

The repository is organised into the following components:

- `configurations/` — experimental configuration and manifest.
- `networks/` — Net3 EPANET network input file.
- `src/` — original and portable experiment and analysis scripts.
- `results/models/` — 30 trained DQN model files.
- `results/reward_histories/` — episode-level training histories.
- `results/statistical_analysis/` — conventional statistical outputs.
- `results/statistical_robustness/` — permutation and robustness outputs.
- `documentation/` — data dictionary, limitations, reproducibility protocol and software environment.
- `checksums/` — SHA256 integrity register.
- `requirements.txt` — recorded Python dependencies.

The original research scripts are preserved separately from their portable copies. The portable copies use repository-relative paths.


## 5. Experimental results

The packaged experiment contains 30 successful DQN training runs, covering three sensor budgets and ten random seeds per budget.

### 5.1 Contamination detection performance

| Sensor budget | Mean detection rate | Standard deviation | Detected events |
|---|---:|---:|---:|
| 3 sensors | 75.5% | 14.99 | 151/200 |
| 5 sensors | 83.0% | 2.58 | 166/200 |
| 8 sensors | 86.5% | 4.12 | 173/200 |

Overall experimental outcomes:

- Successful training runs: 30/30.
- Contamination event evaluations: 600.
- Detected events: 490.
- Undetected events: 110.
- Event simulation errors: 0.
- Overall detection rate: 81.67%.

### 5.2 Training runtime

| Sensor budget | Mean training runtime |
|---|---:|
| 3 sensors | 13.60 seconds |
| 5 sensors | 25.84 seconds |
| 8 sensors | 40.52 seconds |

The mean detection rate increased with sensor budget. The five-sensor configuration exhibited the lowest detection-rate variability among the three configurations.

These findings are specific to the Net3 junction-only experiment. Reward magnitudes across different budgets should be interpreted cautiously because the number of installed sensors differs.


## 6. Statistical analysis

The repository contains two complementary statistical analysis workflows.

### 6.1 Conventional statistical analysis

The conventional analysis includes:

- Descriptive statistics.
- Kruskal–Wallis tests.
- Pairwise Mann–Whitney comparisons.

The outputs are stored in:

`results/statistical_analysis/`

### 6.2 Permutation and robustness analysis

The robustness analysis includes:

- Monte Carlo permutation calibration of the overall Kruskal–Wallis statistic.
- Exhaustive exact pairwise label-permutation tests.
- Holm adjustment of pairwise p-values.
- Comparison with asymptotic statistical tests.
- Tie and distribution diagnostics.

The outputs are stored in:

`results/statistical_robustness/`

The statistical comparisons use ten run-level observations per sensor budget. The 600 contamination event evaluations are nested within the 30 training runs and must not be treated as 600 independent training runs.


## 7. Software environment

The recorded experimental environment is:

| Component | Version |
|---|---|
| Python | 3.12.10 |
| WNTR | 1.5.0 |
| EPANET engine | 2.2 |
| PyTorch | 2.15.0+cpu |
| NumPy | 2.5.4 |
| Pandas | 3.1.0 |
| SciPy | 1.18.1 |
| NetworkX | 3.7 |

The direct Python dependency specifications are provided in `requirements.txt`. EPANET 2.2 is the hydraulic and water-quality simulation engine recorded by the EPANET simulation report generated during the experiment. WNTR 1.5.0 invoked the engine through `wntr.sim.EpanetSimulator`; EPANET is therefore a separate runtime component and is not installed by the Python requirements file.

The official U.S. EPA EPANET 2.2 source and release archive is available from the [USEPA/EPANET2.2 repository](https://github.com/USEPA/EPANET2.2). The [EPANET 2.2 User Manual](https://usepa.github.io/EPANET2.2/) documents installation and simulation behaviour. The experiment's version record is based on its generated simulation report, not inferred from the `.inp` network file.

Additional environment information is available in:

`documentation/software_environment.md`

These versions describe the recorded experimental environment. Package availability and compatibility should be checked before installation on another operating system.

## 8. Installation

Clone or download the repository and open a terminal in its root directory.

### 8.1 Create a virtual environment

```bash
python -m venv .venv
```

### 8.2 Activate the environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux or macOS:

```bash
source .venv/bin/activate
```

### 8.3 Install dependencies

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

Install the recorded dependencies, including the CPU PyTorch build:

```bash
python -m pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt
```

The dependency versions represent the recorded experimental environment. Researchers should verify package availability and compatibility with their operating system and Python version before installation.
## 9. Running the experiment

The portable experiment script is located in `src/`.

**Important: displaying help does not start training. The complete experiment is deliberately protected by an explicit confirmation flag.** Do not add `--confirm-run` unless you intend to execute all 30 DQN training runs.

From the repository root, first inspect the available options:

```bash
python src/108_net3_junction_only_budget_sensitivity_portable.py --help
```

To start the complete Net3 junction-only budget-sensitivity experiment, explicitly authorise it:

```bash
python src/108_net3_junction_only_budget_sensitivity_portable.py --confirm-run
```

The experiment uses sensor budgets of 3, 5 and 8, with 10 random seeds and 1,000 training episodes per run (30 DQN training runs in total).

### 9.1 Output location and protection against overwriting

The default output directory is:

```text
results/reproduction_runs/NET3_JUNCTION_ONLY_BUDGET_SENSITIVITY_20261108/
```

The script refuses to write to an output directory that already exists. It does not overwrite existing experiment outputs. For a later reproduction, choose a new, previously unused output directory. For example:

```bash
python src/108_net3_junction_only_budget_sensitivity_portable.py --confirm-run --output "results/reproduction_runs/NET3_REPRODUCTION_NEW"
```

Replace `NET3_REPRODUCTION_NEW` with a unique directory name before running. The `--confirm-run` flag starts the full experiment; the `--output` option only changes where its new outputs are written.

Running the complete experiment requires 30 DQN training runs and contamination simulations. Execution time depends on the available hardware and software environment.
## 10. Statistical analysis

The repository includes a portable statistical-analysis script:

```bash
python src/109_net3_junction_only_statistical_analysis_portable.py
```

By default, the script analyses the packaged run-level results in `results/net3_junction_only_run_results.csv` and writes its outputs to `results/reproduction_statistical_analysis_20261108/`.

### 10.1 Analyse results from a new reproduction run

To analyse results generated by a new experiment execution, provide the input CSV and a separate output directory:

```bash
python src/109_net3_junction_only_statistical_analysis_portable.py --input "results/reproduction_runs/NET3_JUNCTION_ONLY_BUDGET_SENSITIVITY_20261108/net3_junction_only_run_results.csv" --output "results/reproduction_statistical_analysis_new"
```

The statistical-analysis script operates on existing run-level results. It does not retrain the DQN or rerun contamination simulations.

Statistical outputs should be interpreted alongside the data dictionary and the documented analysis protocol.
## 11. Statistical robustness analysis

The repository provides a separate portable script for permutation-based statistical robustness analysis:

```bash
python src/110_net3_junction_only_robustness_analysis_portable.py
```

By default, the script analyses the packaged run-level results and writes its outputs to `results/reproduction_statistical_robustness_20261108/`.

### 11.1 Analyse results from a new reproduction run

To analyse a new experiment run, specify its run-level CSV and a separate output directory:

```bash
python src/110_net3_junction_only_robustness_analysis_portable.py --input "results/reproduction_runs/NET3_JUNCTION_ONLY_BUDGET_SENSITIVITY_20261108/net3_junction_only_run_results.csv" --output "results/reproduction_statistical_robustness_new"
```

The robustness analysis includes permutation-based comparisons and multiple-comparison adjustment. The documented analysis distinguishes run-level observations from individual contamination-event records.

This script analyses existing results. It does not retrain the DQN or rerun contamination simulations.
## 12. Experimental provenance and integrity

The repository preserves the evidence required to trace the Net3 junction-only budget-sensitivity experiment.

The provenance record includes:

- The sanitised public reproducibility manifest, with repository-relative paths rather than machine-specific absolute paths.

- The original Net3 EPANET network file in `networks/Net3.inp`.
- The sanitised public experimental configuration manifest in `configurations/`.
- Original experiment and analysis scripts.
- Portable copies of the experiment and analysis scripts.
- Trained DQN models in `results/models/`.
- Episode-level reward histories in `results/reward_histories/`.
- Run-level and contamination-event-level result CSV files.
- Statistical analysis and robustness outputs.
- The experimental audit record.
- SHA256 checksums for registered repository files.

### 12.1 File integrity verification

The checksum register is stored at:

```text
checksums/SHA256SUMS.txt
```

SHA256 checksums provide a means of detecting changes to registered files. They support file-integrity verification but do not, by themselves, establish independent experimental reproduction.

### 12.2 Preservation of historical evidence

Original research scripts, experimental results and configuration records are preserved separately from portable reproduction copies. The portable scripts are intended to support execution from the repository structure without modifying the historical experiment evidence.

Researchers should retain the original configuration and record any changes made during subsequent experiments.
## 13. Reproducibility and interpretation

The repository provides the experimental configuration, network input, source scripts, trained models, reward histories, result datasets and analysis outputs needed to inspect the reported Net3 junction-only experiment.

The portable scripts provide a structured route for executing the experiment and analysing its outputs from the repository directory.

The packaged results document the reported experimental findings. Their presence, together with successful checksum verification, does not constitute independent reproduction on a separate computer.

### 13.1 Independent reproduction

Researchers seeking to independently reproduce the experiment should:

1. Set up the documented Python environment.
2. Verify the integrity of the repository files using the SHA256 register.
3. Inspect `configurations/net3_junction_only_manifest_public.txt` and the software configuration.
4. Execute the portable experiment script in a suitable environment.
5. Compare newly generated run-level and event-level results with the packaged evidence.
6. Record hardware, operating system, software versions and any numerical differences.

Results may vary across hardware and software environments. Any deviations from the documented experimental configuration should be reported.
## 14. Limitations and scope

The findings and experimental evidence in this repository should be interpreted within the scope of the implemented Net3 junction-only experiment.

The principal scope limitations are:

- The evaluation uses the Net3 water distribution network.
- Sensor candidates are restricted to the 92 junction nodes; tanks and reservoirs are excluded.
- The budget-sensitivity experiment evaluates sensor budgets of 3, 5 and 8.
- The reported training evaluation uses 10 random seeds and 1,000 episodes per run.
- Contamination detection is evaluated using the documented source locations, concentration settings, simulation duration and detection threshold.
- The reported results do not establish generalisation to every water distribution network or operating condition.

### 14.1 Statistical interpretation

The experiment contains 30 training runs and 600 contamination-event evaluations. Event-level observations are nested within training runs and should not be treated as 600 independent experimental runs.

Detection time is evaluated conditionally on successful detection. Undetected events therefore do not have a detection-time value.

Further evaluation on additional networks, operating conditions and sensor-budget configurations would be necessary to establish broader generalisability.

Additional methodological details are provided in `documentation/limitations_and_scope.md` and `documentation/data_dictionary.md`.

## 15. Citation and licensing

If you use this repository, its software, or its associated experimental outputs, please cite the work using the metadata provided in `CITATION.cff`.

The citation metadata currently identifies the following authors:

- Clinton Jengoa Blakk
- Nnamdi Nwulu
- Esther Titilayo Akinlabi

The repository includes an MIT license for the original research code. The license for the Net3 benchmark network file and any third-party materials may be governed by separate terms. Users should check the applicable terms for those materials rather than assuming that the repository's MIT license covers every included file.

No DOI or publication identifier is asserted here. Add one to the citation metadata when a persistent identifier has been formally assigned.
