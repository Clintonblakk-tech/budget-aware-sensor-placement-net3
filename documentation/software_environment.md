# Software Environment

## Operating environment

- Python version: 3.12.10
- Python architecture: 64-bit AMD64
- WNTR: 1.5.0
- EPANET engine: 2.2
- PyTorch: 2.15.0+cpu
- NumPy: 2.5.4
- Pandas: 3.1.0
- SciPy: 1.18.1
- NetworkX: 3.7
- Matplotlib: 3.11.2

The EPANET 2.2 version was identified from the EPANET simulation report generated during the experiment. WNTR 1.5.0 invoked the engine through `wntr.sim.EpanetSimulator`. EPANET is a separate simulation runtime and is not a Python package installed through `requirements.txt`.

The official U.S. EPA EPANET 2.2 source and release archive is maintained at:
https://github.com/USEPA/EPANET2.2

The EPANET 2.2 User Manual is available at:
https://usepa.github.io/EPANET2.2/

## Main software components

- Python provides the experiment execution environment.
- WNTR provides water distribution network modelling and the interface
  to EPANET.
- EPANET 2.2 performs hydraulic and water-quality simulation.
- PyTorch implements the Deep Q-Network.
- NumPy and Pandas support numerical computation and data processing.
- NetworkX supports graph-based network operations.
- SciPy supports statistical analysis.
- Matplotlib was installed in the recorded environment but is not
  directly imported by the four core experiment and analysis scripts.

## Simulation configuration

- Water-quality model: CHEMICAL
- Simulation duration: 24 hours
- Hydraulic timestep: 3600 seconds
- Water-quality timestep: 3600 seconds
- Report timestep: 3600 seconds

## Installation specification

The requirements.txt file records the direct third-party dependencies
and their observed versions.

The PyTorch build recorded for the experiment is CPU-only:
2.15.0+cpu.

Installation and execution on another computer may require platform-
specific package installation steps. The recorded versions describe
the experimental environment and should not be interpreted as proof
that every combination of operating system and package index provides
identical binary distributions.

## Environment provenance

The Python and principal package versions are recorded in the
experiment manifest. Additional package versions were inspected
from the same named Python virtual environment during repository
preparation.

The original experiment manifest is preserved under configurations/.
