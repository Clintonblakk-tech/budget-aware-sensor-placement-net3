# Experimental Scope and Limitations

## 1. Purpose

This document defines the experimental scope, methodological boundaries, and limitations of the budget-aware sensor placement experiment.

## 2. Experimental Scope

### 2.1 Benchmark Network

The experiment uses the Net3 water distribution network benchmark.

The findings demonstrate the behaviour of the implemented sensor placement approach under the evaluated Net3 configuration. They should not automatically be generalised to other networks.

### 2.2 Sensor Candidate Locations

The experiment uses a junction-only candidate sensor set.

Tanks, reservoirs, and other non-junction locations are outside the evaluated candidate set.

### 2.3 Sensor Budgets

Three sensor budgets were evaluated:

- Budget 3: maximum of three sensors.
- Budget 5: maximum of five sensors.
- Budget 8: maximum of eight sensors.

### 2.4 Training Design

The experiment comprises:

- Three sensor budget configurations.
- Ten trained runs per budget.
- 1,000 DQN training episodes per run.
- Thirty trained runs in total.

### 2.5 Contamination Event Evaluation

Each trained sensor placement was evaluated against twenty contamination events.

This produces 200 event evaluations per budget and 600 event evaluations overall.

Event-level observations are nested within their corresponding trained runs. They are not 600 independent training replicates.

The trained run is the experimental unit for comparisons between budgets.

## 3. Outcome Measures

The principal outcomes include:

1. Detection rate.
2. Mean detection time.
3. Training reward.
4. Training runtime.
5. Contamination evaluation runtime.
6. Event detection and evaluation errors.

Detection time is conditional on successful detection. Undetected events have no first-detection time.

## 4. Statistical Scope

The statistical analysis uses ten run-level observations per budget.

The repository includes:

- Descriptive statistics.
- Kruskal-Wallis tests.
- Pairwise Mann-Whitney comparisons.
- Holm-adjusted significance tests.
- Overall permutation tests.
- Exact pairwise permutation tests.
- Tie and distribution diagnostics.

Permutation-based analyses provide additional robustness checks on the retained observations.

The findings describe differences among the evaluated budget configurations and do not establish equivalent effects across other networks or operating conditions.

## 5. Experimental Limitations

### 5.1 Network Generalisability

Only the Net3 benchmark network was evaluated. Additional benchmark networks and operational water distribution systems would be needed to establish broader generalisability.

### 5.2 Candidate-Set Restriction

Sensor locations were restricted to junctions. The experiment does not establish the performance of alternative candidate sets involving tanks, reservoirs, or other network components.

### 5.3 Budget Coverage

Only budgets of 3, 5, and 8 were investigated. Other budgets may produce different performance characteristics.

### 5.4 Training Variability

Ten independent trained runs were conducted per budget. A larger number of runs could provide additional evidence about training stability.

### 5.5 Contamination Scenario Coverage

Twenty contamination events were evaluated per trained placement. The results do not establish performance under every possible contamination location, source strength, duration, or operational condition.

### 5.6 Simulation-Based Evaluation

The experiment uses a benchmark-network simulation workflow. Simulation performance does not independently establish equivalent performance in a physically deployed water distribution system.

Field validation remains necessary before making practical deployment claims.

### 5.7 Statistical Interpretation

The experiment contains thirty trained runs and six hundred nested event evaluations.

Statistical comparisons between budgets use run-level observations rather than treating individual contamination events as independent training replicates.

## 6. Reproducibility Boundaries

The repository preserves the experimental scripts, configuration evidence, run-level results, event-level results, statistical outputs, and supporting documentation collected for this experiment.

Reproduction should follow the documented software environment and experimental protocol.

Differences in software versions, operating systems, computational hardware, numerical libraries, and simulation execution may influence runtime measurements and potentially numerical outcomes.

Identical runtime measurements across computing environments are not guaranteed.

## 7. Interpretation of Findings

The experiment provides evidence about the relationship between sensor budget and the performance of the evaluated DQN-based sensor placement approach on the Net3 junction-only configuration.

The findings are limited to:

- Net3 benchmark network.
- Junction-only candidate locations.
- Sensor budgets of 3, 5, and 8.
- Ten trained runs per budget.
- The specified training and evaluation protocol.
- Twenty contamination events per trained placement.

Broader claims require additional experimental validation.

## 8. Future Research Directions

Future investigations could include:

1. Evaluation on additional benchmark water distribution networks.
2. Investigation of a wider range of sensor budgets.
3. Evaluation of alternative sensor candidate-location strategies.
4. Increased numbers of independent training runs.
5. Expanded contamination scenarios.
6. Assessment under different hydraulic and operational conditions.
7. Validation using real-world water distribution system data.
8. Investigation of alternative optimisation and reinforcement learning approaches.

## 9. Concluding Statement

This repository provides a documented experimental record of budget-aware DQN sensor placement under a defined Net3 junction-only simulation configuration.

Its purpose is to make the experimental procedures, datasets, statistical analyses, and limitations transparent, allowing other researchers to inspect, reproduce, evaluate, and extend the work without overstating the scope of the reported findings.
