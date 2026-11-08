# Software Environment

## 1. Operating Environment

The following software versions and environment characteristics were recorded for the experiment:

| Component | Recorded Version or Specification |
|---|---|
| Python | 3.12.10 |
| Python Architecture | 64-bit AMD64 |
| WNTR | 1.5.0 |
| EPANET Engine | 2.2 |
| PyTorch | 2.15.0+cpu |
| NumPy | 2.5.4 |
| Pandas | 3.1.0 |
| SciPy | 1.18.1 |
| NetworkX | 3.7 |
| six | 1.17.0 |
| Matplotlib | 3.11.2 |

The EPANET 2.2 version was identified from the EPANET simulation report generated during the experiment. WNTR 1.5.0 invoked the simulation engine through `wntr.sim.EpanetSimulator`.

EPANET is a separate hydraulic and water-quality simulation runtime. It is not a Python package installed through `requirements.txt`.

The official U.S. Environmental Protection Agency EPANET 2.2 source and release archive is maintained in the USEPA EPANET2.2 repository. The corresponding EPANET 2.2 User Manual provides additional information about the simulation engine.

**Official references:**

- USEPA EPANET 2.2 source and release archive: https://github.com/USEPA/EPANET2.2
- EPANET 2.2 User Manual: https://usepa.github.io/EPANET2.2/
## 2. Main Software Components

The principal software components used in the experimental workflow are:

- **Python:** Provides the experiment execution environment.
- **WNTR:** Provides water distribution network modelling and the interface to EPANET.
- **EPANET 2.2:** Performs hydraulic and water-quality simulation.
- **PyTorch:** Implements the Deep Q-Network (DQN).
- **NumPy:** Supports numerical computation.
- **Pandas:** Supports experimental data processing and analysis.
- **NetworkX:** Supports graph-based network operations.
- **SciPy:** Supports statistical analysis.
- **Matplotlib:** Was installed in the recorded environment but is not directly imported by the four core experiment and analysis scripts.

## 3. Simulation Configuration

The following simulation settings were recorded for the experiment:

| Parameter | Configuration |
|---|---|
| Water-quality model | CHEMICAL |
| Simulation duration | 24 hours |
| Hydraulic timestep | 3600 seconds |
| Water-quality timestep | 3600 seconds |
| Report timestep | 3600 seconds |

These settings describe the hydraulic and water-quality simulation configuration used in the Net3 contamination-detection evaluation.

## 4. Installation Specification

The `requirements.txt` file records the direct third-party Python dependencies and their observed versions.

The PyTorch build recorded for the experiment is CPU-only:

`2.15.0+cpu`

EPANET 2.2 is a separate simulation runtime and must be available independently of the Python packages listed in `requirements.txt`.

Installation and execution on another computer may require platform-specific package installation steps. The recorded versions describe the experimental environment and should not be interpreted as proof that every combination of operating system, package index, and hardware provides identical binary distributions.

## 5. Environment Provenance

The Python version and principal package versions are recorded in the experiment manifest. Additional package versions were inspected from the same named Python virtual environment during repository preparation.

The original experiment manifest is preserved under `configurations/`.

The environment information is provided to support inspection of the recorded experimental setup and preparation of compatible execution environments. Differences in software versions, operating systems, computational hardware, numerical libraries, and simulation runtimes may affect execution behaviour and runtime measurements.