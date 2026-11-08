# \# Experimental Scope and Limitations

#

# \## 1. Purpose

#

# This document defines the experimental scope, methodological boundaries, and limitations of the budget-aware Deep Q-Network (DQN) sensor-placement experiment conducted using the Net3 water distribution network benchmark.

#

# It establishes the conditions under which the experimental findings should be interpreted and identifies areas requiring further investigation.

#

# \## 2. Experimental Scope

#

# \### 2.1 Benchmark Network

#

# The experiment uses the Net3 water distribution network benchmark.

#

# The findings demonstrate the behaviour of the implemented sensor-placement approach under the evaluated Net3 configuration. They should not automatically be generalised to other benchmark networks or operational water distribution systems.

#

# \### 2.2 Sensor Candidate Locations

#

# The experiment uses a junction-only candidate sensor set.

#

# Tanks, reservoirs, and other non-junction locations are excluded from the evaluated candidate set.

#

# \### 2.3 Sensor Budgets

#

# Three sensor budgets were evaluated:

#

# \- Budget 3: maximum of three sensors.

# \- Budget 5: maximum of five sensors.

# \- Budget 8: maximum of eight sensors.

#

# The five-sensor configuration serves as the reference budget for expressing nominal budget percentages.

#

# \### 2.4 Training Design

#

# The experiment comprises:

#

# \- Three sensor-budget configurations.

# \- Ten trained runs per budget.

# \- 1,000 DQN training episodes per run.

# \- Thirty trained runs in total.

#

# \### 2.5 Contamination Event Evaluation

#

# Each trained sensor placement was evaluated against twenty contamination events.

#

# This produces 200 event evaluations per budget and 600 event evaluations overall.

#

# Event-level observations are nested within their corresponding trained runs. They are not 600 independent training replicates.

#

# The trained run is the experimental unit for statistical comparisons between budgets.

#

# \## 3. Outcome Measures

#

# The principal experimental outcomes include:

#

# \- Detection rate.

# \- Mean detection time.

# \- Training reward.

# \- Training runtime.

# \- Contamination-evaluation runtime.

# \- Event detection and evaluation errors.

#

# Detection time is conditional on successful detection. Undetected events have no first-detection time and are represented by blank detection-time values in the event-level results.

#

# \## 4. Statistical Scope

#

# The statistical analysis uses ten run-level observations per budget.

#

# The repository includes:

#

# \- Descriptive statistics.

# \- Kruskal-Wallis tests.

# \- Pairwise Mann-Whitney comparisons.

# \- Holm-adjusted significance tests.

# \- Overall permutation tests.

# \- Exact pairwise permutation tests.

# \- Tie and distribution diagnostics.

#

# Permutation-based analyses provide additional robustness checks using the retained run-level observations.

#

# The statistical analyses do not treat the 600 contamination-event evaluations as independent training replicates.

#

# The findings describe differences among the evaluated budget configurations. They do not establish equivalent effects across other networks, contamination scenarios, or operating conditions.

#

# \## 5. Experimental Limitations

#

# \### 5.1 Network Generalisability

#

# Only the Net3 benchmark network was evaluated. Additional benchmark networks and operational water distribution systems would be needed to establish broader generalisability.

#

# \### 5.2 Candidate-Set Restriction

#

# Sensor locations were restricted to junctions. The experiment does not establish the performance of alternative candidate sets involving tanks, reservoirs, or other network components.

#

# \### 5.3 Budget Coverage

#

# Only budgets of 3, 5, and 8 were investigated. Other sensor budgets may produce different performance characteristics.

#

# \### 5.4 Training Variability

#

# Ten independent trained runs were conducted per budget. A larger number of independent runs could provide additional evidence about training stability and variability.

#

# \### 5.5 Contamination Scenario Coverage

#

# Twenty contamination events were evaluated per trained placement. The results do not establish performance under every possible contamination location, source strength, duration, or operational condition.

#

# \### 5.6 Simulation-Based Evaluation

#

# The experiment uses a benchmark-network simulation workflow. Simulation performance does not independently establish equivalent performance in a physically deployed water distribution system.

#

# Field validation remains necessary before making practical deployment claims.

#

# \### 5.7 Statistical Interpretation

#

# The experiment contains thirty trained runs and six hundred nested event evaluations.

#

# Statistical comparisons between budgets use run-level observations rather than treating individual contamination events as independent training replicates.

#

# The statistical conclusions are therefore limited to the retained run-level observations and the specified experimental design.

#

# \## 6. Reproducibility Boundaries

#

# The repository preserves the experimental scripts, configuration evidence, run-level results, event-level results, statistical outputs, and supporting documentation collected for this experiment.

#

# The original Net3 INP benchmark file is included in the repository, with its SHA-256 fingerprint documented in the experiment manifest.

#

# Reproduction should follow the documented software environment and experimental protocol.

#

# The original raw EPANET water-quality trajectories and all event-specific generated input files were not retained as a complete archive. Consequently, the preserved outputs support inspection and analysis of the reported results but do not provide every intermediate simulation state.

#

# Differences in software versions, operating systems, computational hardware, numerical libraries, and simulation execution may influence runtime measurements and potentially numerical outcomes.

#

# Identical runtime measurements across computing environments are not guaranteed.

#

# \## 7. Interpretation of Findings

#

# The experiment provides evidence about the relationship between sensor budget and the performance of the evaluated DQN-based sensor-placement approach on the Net3 junction-only configuration.

#

# The findings are limited to:

#

# \- The Net3 benchmark network.

# \- Junction-only candidate locations.

# \- Sensor budgets of 3, 5, and 8.

# \- Ten trained runs per budget.

# \- The specified DQN training and evaluation protocol.

# \- Twenty contamination events per trained placement.

#

# Broader claims require additional experimental validation across networks, sensor budgets, contamination scenarios, and operational conditions.

#

# \## 8. Future Research Directions

#

# Future investigations could include:

#

# \- Evaluation on additional benchmark water distribution networks.

# \- Investigation of a wider range of sensor budgets.

# \- Evaluation of alternative sensor candidate-location strategies.

# \- Increased numbers of independent training runs.

# \- Expanded contamination scenarios.

# \- Assessment under different hydraulic and operational conditions.

# \- Validation using real-world water distribution system data.

# \- Investigation of alternative optimisation and reinforcement learning approaches.

#

# \## 9. Concluding Statement

#

# This repository provides a documented experimental record of budget-aware DQN sensor placement under a defined Net3 junction-only simulation configuration.

#

# Its purpose is to make the experimental procedures, datasets, statistical analyses, and methodological limitations transparent, allowing other researchers to inspect, reproduce, evaluate, and extend the work without overstating the scope of the reported findings.
