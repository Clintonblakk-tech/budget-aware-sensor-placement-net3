# Third-Party Notices

This repository includes or depends on third-party software and
benchmark materials. Their respective copyright notices, licences,
and attribution requirements remain applicable.

## 1. Net3 EPANET Benchmark Network

File: networks/Net3.inp

Name: EPANET Example Network 3

Upstream source:
https://github.com/OpenWaterAnalytics/EPANET/blob/dev/example-networks/Net3.inp

The included network file has been verified against the original
experimental network fingerprint recorded in the experiment manifests.

SHA-256:
d95b068194ba747605bea851d608333e577ac667658aaa1680cf1c07e43faf53

The OpenWaterAnalytics EPANET repository identifies its project
licence as MIT:

https://github.com/OpenWaterAnalytics/EPANET/blob/dev/LICENSE

This attribution identifies the upstream project. It does not
independently establish that every component or historical version
of the network file has identical licensing terms.

## 2. EPANET Simulation Engine

EPANET is a separate hydraulic and water-quality simulation component.
The experiment documentation records EPANET engine version 2.2.

Official project:
https://github.com/USEPA/EPANET2.2

OpenWaterAnalytics EPANET:
https://github.com/OpenWaterAnalytics/EPANET

Users obtaining or redistributing EPANET should consult the applicable
upstream release and licensing information.

## 3. WNTR

WNTR (Water Network Tool for Resilience) is used as a Python dependency
for water-network modelling and interaction with EPANET.

Version recorded: 1.5.0

Project:
https://github.com/USEPA/WNTR

Licence: Revised BSD License.

Licence information:
https://github.com/USEPA/WNTR/blob/main/LICENSE.md

WNTR remains a third-party dependency. This repository does not claim
ownership of WNTR or independently relicense its source code.

## 4. Direct Python Dependencies

The experiment environment records the following direct dependencies
and versions in requirements.txt:

- NumPy 2.5.4
- pandas 3.1.0
- WNTR 1.5.0
- PyTorch 2.15.0+cpu
- SciPy 1.18.1
- NetworkX 3.7
- six 1.17.0

These packages are third-party software and remain subject to their
respective licences and distribution conditions.

Relevant upstream projects:

NumPy:
https://github.com/numpy/numpy

pandas:
https://github.com/pandas-dev/pandas

PyTorch:
https://github.com/pytorch/pytorch

SciPy:
https://github.com/scipy/scipy

NetworkX:
https://github.com/networkx/networkx

six:
https://github.com/benjaminp/six

WNTR:
https://github.com/USEPA/WNTR

Some packages may incorporate additional third-party components
with separate notices or licensing conditions. Consult the
corresponding distribution and upstream licence files.

## 5. Repository Licence

The MIT licence in the root LICENSE file applies to original research
software and associated materials to the extent that the repository
authors hold the relevant rights.

It does not override third-party copyright, licence, or attribution
requirements.
