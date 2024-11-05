# Operational Technology Simulation System

## Overview

This project integrates EPANET, OpenPLC, and ScadaLTS to create a comprehensive simulation environment for operational technology (OT) systems, with a focus on water networks.

## Components

### EPANET
Simulates water distribution systems, providing a digital twin of the water network.

### OpenPLC
Acts as the programmable logic controller, interfacing with the EPANET simulation to read sensor data and execute control logic.

### ScadaLTS
Provides the human-machine interface (HMI) for visualization and interaction with the simulated system.

## Features

- Realistic simulation of water network behavior
- Real-time control logic execution
- User-friendly HMI for system monitoring and control
- Scenario testing and analysis capabilities
- Operator training in a safe, simulated environment

## Requirements
- docker compose

## Installation
```
git clone https://github.com/Ketho/OT-Simulation
cd OT-Simulation
docker compose up -d
```

## Contributing

Contributions to improve the simulation or add new features are welcome. Please submit pull requests or open issues for discussion.

## License

[Include license information here]

## Acknowledgments

- EPANET developers
- OpenPLC project contributors
- ScadaLTS team

## Support

For questions or issues, please open an issue in this repository or contact [your contact information].
