# Reproducibility Protocol

## 1. Experiment identification

This protocol documents the Net3 junction-only budget-sensitivity
experiment for the manuscript:

"Budget-Aware Explainable Deep Reinforcement Learning for Sensor
Placement in Water Distribution Networks."

The experiment evaluates DQN-based sensor placement under sensor
budgets of 3, 5 and 8.

## 2. Network preparation

The benchmark network is Net3, supplied in EPANET INP format.

The network contains 97 graph nodes:
- 92 junctions;
- 3 tanks;
- 2 reservoirs.

Only junctions are eligible for sensor placement. Candidate nodes
are obtained from the WNTR WaterNetworkModel.junction_name_list.

The network fingerprint is recorded in the sanitised public manifest:
configurations/net3_junction_only_manifest_public.txt

Network SHA-256:
d95b068194ba747605bea851d608333e577ac667658aaa1680cf1c07e43faf53

## 3. DQN training

The junction-only DQN engine is:
src/dqn_engine_junction_only.py

The experiment execution script is:
src/108_net3_junction_only_budget_sensitivity.py

The experiment evaluates three sensor budgets:
- 3 sensors;
- 5 sensors;
- 8 sensors.

The baseline budget is 5 sensors.

Ten random seeds are used for each budget (seeds 1 to 10),
giving 30 DQN training runs.

Each run uses 1,000 training episodes.

The DQN architecture is:
Linear(92,128)-ReLU-Linear(128,64)-ReLU-
Linear(64,32)-ReLU-Linear(32,92).

Recorded training parameters:
- Optimizer: Adam
- Learning rate: 0.0005
- Discount factor: 0.99
- Replay buffer: enabled
- Replay buffer capacity: 50,000
- Batch size: 64
- Target network: enabled
- Target network synchronization: every 100 episodes
- Initial epsilon: 1.0
- Minimum epsilon: 0.01
- Epsilon decay: 0.995
- Coverage weight: 0.70
- Centrality weight: 0.30

## 4. Contamination event simulation

Each trained sensor placement is evaluated against 20 contamination
events.

The experiment therefore contains 600 event evaluations:
30 trained placements multiplied by 20 events.

The contamination configuration is:
- Source type: SETPOINT
- Source concentration: 0.1 kg/m^3 (100 mg/L)
- Contamination pattern: constant ([1])
- Detection threshold: 0.01 kg/m^3 (10 mg/L)
- Quality parameter: CHEMICAL

The 20 source junctions are:

10, 15, 20, 35, 40, 50, 60, 601, 61, 101,
103, 105, 107, 109, 111, 113, 115, 117, 119, 120.

## 5. EPANET simulation

Water distribution network simulations are performed through
WNTR's EPANET simulator interface:

wntr.sim.EpanetSimulator

The recorded EPANET engine version is 2.2. This version was identified from the EPANET simulation report generated during the experiment; it is not inferred from the Net3 `.inp` file. WNTR 1.5.0 invoked the engine through `wntr.sim.EpanetSimulator`.

The official U.S. EPA EPANET 2.2 source and release archive is available at:
https://github.com/USEPA/EPANET2.2

The EPANET 2.2 User Manual is available at:
https://usepa.github.io/EPANET2.2/

Simulation settings:
- Duration: 24 hours
- Hydraulic timestep: 1 hour
- Water-quality timestep: 1 hour
- Report timestep: 1 hour

The detection rule is that at least one selected sensor must record
a concentration strictly greater than the detection threshold.

## 6. Experimental outputs

The repository preserves:

- Run-level results;
- Event-level results;
- Summary results;
- DQN model checkpoints;
- Reward histories;
- Experiment manifest;
- Experiment audit record.

The original output directory contained 30 model checkpoints and
30 reward-history CSV files. Each reward-history file contains
1,000 training episodes.

## 7. Statistical analysis

The original statistical analysis is provided in:

src/109_net3_junction_only_statistical_analysis.py

Its outputs are preserved in:

results/statistical_analysis/

The analysis treats the trained run as the unit of replication,
with ten runs per sensor budget.

The 20 contamination events evaluated for each trained placement
are nested evaluations and are not treated as independent DQN
training replicates.

Detection time is evaluated conditionally on successful detection.

## 8. Statistical robustness analysis

The additional robustness analysis is provided in:

src/110_net3_junction_only_robustness_analysis.py

Its outputs are preserved in:

results/statistical_robustness/

The analysis includes:
- Monte Carlo permutation tests for overall Kruskal-Wallis statistics;
- Exhaustive exact permutation tests for pairwise comparisons;
- Holm adjustment of pairwise p-values;
- Tie and distribution diagnostics;
- Effect-size reporting.

The overall permutation analysis used 500,000 Monte Carlo
permutations with random seed 20261108 and plus-one correction.

The pairwise exact permutation analysis evaluated all
184,756 allocations of ten observations from twenty observations
for each comparison.

These statistical analyses operate on the retained experimental
run-level results. They do not represent independent reruns of
DQN training or EPANET simulations.

## 9. Provenance and integrity

The sanitised public manifest records the network, engine and
experiment-script SHA-256 fingerprints. Machine-specific absolute
paths have been replaced with repository-relative paths.

The repository preparation process additionally verified copied
files against their original counterparts.

The original experiment outputs are retained separately from
the repository copies.

## 10. Reproduction limitations

The repository documents the recorded experiment and preserves
its outputs. Exact reproduction on another computer may depend on
operating-system configuration, package availability, EPANET
runtime installation and access to the original Net3 INP file.

The original raw EPANET water-quality trajectories and all
event-specific generated input files were not retained as a
complete archive. Consequently, the preserved run-level and
event-level outputs support result inspection, but do not by
themselves provide every intermediate simulation state.

The experiment manifest and audit record should be consulted
before attempting a reproduction.
