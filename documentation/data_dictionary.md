# Data Dictionary

## 1. Purpose

This document describes the CSV files supplied with the Net3 junction-only, budget-aware DQN sensor-placement experiment. It defines the recorded fields and explains the unit of observation represented by each dataset.

The experimental design contains three sensor budgets (3, 5 and 8), ten trained runs per budget, and twenty contamination-event evaluations per trained run. The five-sensor configuration serves as the reference budget (100%). Accordingly, the three budgets correspond to nominal budget percentages of 60%, 100% and 160%, respectively.

The experiment therefore comprises 30 trained DQN runs and 600 contamination-event evaluation records.

## 2. Main Experimental Result Files

### 2.1 net3_junction_only_run_results.csv

**Unit of observation:** One completed DQN training run and its associated contamination evaluation.

| Field | Description |
|---|---|
| Network | Water distribution network used; Net3 in this experiment. |
| CandidateSet | Permitted sensor-location set; Junction-only. |
| Budget | Maximum number of sensors permitted in the placement. |
| NominalBudgetPercent | Sensor budget expressed as a percentage of the five-sensor reference budget. |
| Seed | Random seed identifier for the training run. |
| Episodes | Number of DQN training episodes. |
| BestReward | Best training reward recorded for the run. |
| FinalReward | Final recorded training reward. |
| TrainingRuntimeEngineSeconds | Training runtime reported by the experiment engine, in seconds. |
| TrainingRuntimeMeasuredSeconds | Independently measured elapsed training runtime, in seconds. |
| Sensors | Identifiers of the junction nodes selected as sensor locations. |
| SensorCount | Number of selected sensors. |
| DetectedEvents | Number of evaluated contamination events detected. |
| TotalEvents | Number of contamination events evaluated for the run. |
| DetectionRatePercent | Percentage of evaluated contamination events detected. |
| MeanDetectionIndex | Mean first-detection index among successfully detected events. |
| MeanDetectionTimeHours | Mean time to first detection, in hours, calculated only for successfully detected events. |
| EventErrorCount | Number of contamination-event evaluation errors. |
| ContaminationEvaluationRuntimeSeconds | Runtime used for the contamination-event evaluations, in seconds. |
| TrainingStatus | Recorded completion status of the training run. |
| TrainingError | Error information recorded for the training run; blank where no training error was recorded. |
| RewardHistoryFile | Filename of the corresponding episode-level reward history. |
| ModelWeightsFile | Filename of the saved DQN model weights. |

### 2.2 net3_junction_only_event_results.csv

**Unit of observation:** One contamination-event evaluation associated with a particular trained run.

| Field | Description |
|---|---|
| Network | Water distribution network used. |
| CandidateSet | Permitted sensor-location set. |
| Budget | Sensor budget of the trained placement being evaluated. |
| Seed | Seed identifier of the associated training run. |
| EventNumber | Sequential identifier of the contamination event within the run. |
| SourceNode | Junction at which the contamination event was introduced. |
| Detected | Detection indicator: 1 means detected; 0 means not detected. |
| FirstDetectionIndex | First detection index; blank when no detection occurred. |
| FirstDetectionTimeHours | Time to first detection in hours; blank when no detection occurred. |
| MaxSensorQuality_kg_m3 | Maximum recorded sensor water-quality concentration, in kg/m³. |
| SourceConcentration_kg_m3 | Contaminant source concentration, in kg/m³. |
| DetectionThreshold_kg_m3 | Concentration threshold used to classify detection, in kg/m³. |
| EventRuntimeSeconds | Runtime for the individual event evaluation, in seconds. |
| Error | Error information, if any; blank when no event error was recorded. |

Blank values in `FirstDetectionIndex` and `FirstDetectionTimeHours` indicate that no detection occurred during the corresponding event evaluation. They should not be interpreted as zero-valued detection measurements.

### 2.3 net3_junction_only_summary.csv

**Unit of observation:** One sensor-budget group summarising its ten trained runs.

| Field | Description |
|---|---|
| Budget | Sensor budget represented by the group. |
| NominalBudgetPercent | Nominal budget percentage relative to the five-sensor reference budget. |
| Runs | Number of trained runs included in the group. |
| MeanBestReward | Mean best training reward across runs. |
| SDBestReward | Standard deviation of best training reward across runs. |
| MeanFinalReward | Mean final training reward across runs. |
| SDFinalReward | Standard deviation of final training reward across runs. |
| MeanTrainingRuntimeSeconds | Mean measured training runtime, in seconds. |
| SDTrainingRuntimeSeconds | Standard deviation of training runtime, in seconds. |
| MeanDetectionRatePercent | Mean run-level detection rate, in percent. |
| SDDetectionRatePercent | Standard deviation of run-level detection rates, in percentage points. |
| MeanDetectionIndex | Mean of the run-level mean detection indices. |
| SDDetectionIndex | Standard deviation of the run-level mean detection indices. |
| MeanDetectionTimeHours | Mean of the run-level mean detection times, in hours, conditional on successful detection. |
| SDDetectionTimeHours | Standard deviation of the run-level mean detection times, in hours. |
| TotalDetectedEvents | Total detected contamination events across the group. |
| TotalEvents | Total evaluated contamination events across the group. |
| TotalEventErrors | Total event-evaluation errors across the group. |
| MeanContaminationRuntimeSeconds | Mean contamination-evaluation runtime per run, in seconds. |
| SDContaminationRuntimeSeconds | Standard deviation of contamination-evaluation runtime, in seconds. |

## 3. Conventional Statistical Analysis Files

### 3.1 descriptive_statistics.csv

**Unit of observation:** One outcome-by-budget descriptive summary.

| Field | Description |
|---|---|
| Outcome | Outcome variable being summarised. |
| Budget | Sensor budget group. |
| N | Number of run-level observations. |
| Mean | Arithmetic mean. |
| SD | Sample standard deviation. |
| Median | Median value. |
| Q1 | First quartile. |
| Q3 | Third quartile. |
| IQR | Interquartile range (Q3 minus Q1). |
| Minimum | Minimum observed value. |
| Maximum | Maximum observed value. |

### 3.2 kruskal_wallis_results.csv

**Unit of observation:** One overall outcome test across the three budget groups.

| Field | Description |
|---|---|
| Outcome | Outcome variable tested. |
| Test | Statistical test name. |
| H_statistic | Kruskal-Wallis H statistic. |
| Degrees_of_freedom | Degrees of freedom for the test. |
| P_value | Asymptotic p-value. |
| Epsilon_squared | Epsilon-squared effect-size estimate. |
| Significant_at_0.05 | Whether the reported p-value is below 0.05. |

### 3.3 pairwise_mann_whitney_results.csv

**Unit of observation:** One pairwise budget comparison for an outcome.

| Field | Description |
|---|---|
| Outcome | Outcome variable compared. |
| Comparison | Budget pair being compared. |
| Budget_A | First budget group. |
| Budget_B | Second budget group. |
| U_statistic | Mann-Whitney U statistic. |
| P_value | Unadjusted asymptotic p-value. |
| Rank_biserial_correlation | Rank-biserial effect-size estimate. |
| Holm_adjusted_P_value | P-value adjusted using the Holm procedure. |
| Significant_after_Holm | Whether the adjusted p-value is below 0.05. |

## 4. Statistical Robustness Files

### 4.1 overall_permutation_tests.csv

**Unit of observation:** One outcome-level overall permutation test.

| Field | Description |
|---|---|
| Outcome | Outcome variable tested. |
| NPerBudget | Number of trained runs per budget. |
| TotalRuns | Total number of run-level observations. |
| KruskalWallisH | Observed Kruskal-Wallis H statistic. |
| AsymptoticP | Asymptotic Kruskal-Wallis p-value. |
| PermutationP | Monte Carlo permutation p-value. |
| PermutationCount | Number of Monte Carlo permutations performed. |
| PermutationExtremeCount | Number of permutation statistics at least as extreme as the observed statistic. |
| MonteCarloSE | Estimated Monte Carlo standard error of the permutation p-value. |
| EpsilonSquared | Epsilon-squared effect-size estimate. |

The permutation count and extreme-count fields provide information for inspecting the Monte Carlo permutation analysis.

### 4.2 pairwise_exact_permutation_tests.csv

**Unit of observation:** One pairwise budget comparison for an outcome.

| Field | Description |
|---|---|
| Outcome | Outcome variable compared. |
| Comparison | Budget pair being compared. |
| N1 | Number of observations in group 1. |
| N2 | Number of observations in group 2. |
| U | Observed Mann-Whitney U statistic. |
| ExactExtremeAllocations | Number of exhaustive allocations at least as extreme as the observed statistic. |
| ExactTotalAllocations | Total number of allocations evaluated. |
| ExactPermutationP | Exact permutation p-value. |
| AsymptoticP | Asymptotic p-value for comparison. |
| RankBiserial | Rank-biserial effect-size estimate. |
| MeanDifference_Group1MinusGroup2 | Difference between group means (group 1 minus group 2). |
| MedianDifference_Group1MinusGroup2 | Difference between group medians (group 1 minus group 2). |
| UniqueValuesPooled | Number of unique pooled observations. |
| TieCountExcess | Diagnostic count describing tied observations. |
| ExactHolmAdjustedP | Holm-adjusted exact permutation p-value. |
| AsymptoticHolmAdjustedP | Holm-adjusted asymptotic p-value. |
| ExactSignificantAt005 | Whether the exact Holm-adjusted result is significant at 0.05. |
| AsymptoticSignificantAt005 | Whether the asymptotic Holm-adjusted result is significant at 0.05. |

### 4.3 tie_and_distribution_diagnostics.csv

**Unit of observation:** One outcome-by-budget distribution diagnostic.

| Field | Description |
|---|---|
| Outcome | Outcome variable examined. |
| Budget | Sensor budget group. |
| N | Number of run-level observations. |
| UniqueValues | Number of distinct observed values. |
| TieGroups | Number of groups of tied observations. |
| MaximumTieMultiplicity | Largest number of observations sharing a value. |
| Mean | Arithmetic mean. |
| SD | Sample standard deviation. |
| Median | Median value. |
| Minimum | Minimum observed value. |
| Maximum | Maximum observed value. |

## 5. Interpretation and Statistical Unit

The experiment contains 30 trained DQN runs: ten runs for each of the three sensor budgets. Each trained placement is evaluated against 20 contamination events, producing 600 event-level evaluation records.

The 600 event evaluations are nested within the 30 trained runs. They are not 600 independent training replicates. Statistical comparisons between sensor budgets therefore use the ten run-level observations in each budget group.

Detection time is conditional on successful detection. An event that was not detected has no first-detection time and is represented by a blank value in the event-level file. Such missing detection times must not be interpreted as zero.

Concentration fields ending in `_kg_m3` are expressed in kilograms per cubic metre. In this experiment, the source concentration is 0.1 kg/m³ and the detection threshold is 0.01 kg/m³.

The descriptive and conventional inferential files preserve the original asymptotic analysis. The robustness files provide permutation-based overall and pairwise analyses. These are complementary analyses of the same retained run-level observations, not additional independent experiments.