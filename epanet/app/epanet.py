#!/usr/bin/env python3
"""Run EPANET simulation with Modbus controls.

Usage:
    python script.py [network.inp]
"""
from epyt import epanet
from pymodbus.client import ModbusTcpClient

import sys
import time

def parse_arguments() -> str:
    """Parse command line arguments to retrieve EPANET network file."""
    if len(sys.argv) != 2 or not sys.argv[1].endswith('.inp'):
        print("Run EPANET simulation with Modbus controls.")
        print(f">>> python {sys.argv[0]} [network.inp]")
        sys.exit(1)
    return sys.argv[1]

def setup_client() -> ModbusTcpClient:
    """Setup and establish a Modbus TCP client connection."""
    try:
        client = ModbusTcpClient(host='openplc', port=502)
        while not client.connect(): 
            time.sleep(1) # retrying every second until a successful connection is established.
        return client
    except Exception as e:
        print(f"Failed to setup and establish a Modbus TCP client connection: {e}")
        sys.exit(1)

def setup_epanet(network_file: str) -> epanet:
    """Setup EPANET with specified network (.inp) file."""
    try:
        en = epanet(network_file)
        en.setTimeSimulationDuration(10) # initial setup; duration will be set to infinite in main function.
        en.setTimeHydraulicStep(1)
        return en
    except Exception as e:
        print(f"Failed to setup EPANET with specified network (.inp) file: {e}")
        sys.exit(1)

def read_data(en: epanet) -> dict:
    """Gathers data from an EPANET network and categorizes it into zones.

    As this stupid shit has cost me to much fk time, this piece of art deserves to be treated with care.
    """
    data = {}
    
    for i in en.getNodeNameID() + en.getLinkNameID():
        if '-' not in i:
            continue

        zone, e = i.split('-', 1)

        if zone not in data:
            data[zone] = {}
        if e not in data[zone]:
            data[zone][e] = {}
        
        if i in en.getNodeNameID():
            data[zone][e]['hydraulic_head'] = \
                en.getNodeHydraulicHead(en.getNodeIndex(i))
            
            data[zone][e]['min_water_level'] = \
                float(en.getNodeTankMinimumWaterLevel(en.getNodeIndex(i)))
            
            data[zone][e]['max_water_level'] = \
                float(en.getNodeTankMaximumWaterLevel(en.getNodeIndex(i)))
        
        if i in en.getLinkNameID():
            data[zone][e]['pump_power'] = \
                en.getLinkPumpPower(en.getLinkIndex(i))
            
    return data

def main():
    network_file = parse_arguments()

    try:
        client = setup_client()
        en = setup_epanet(network_file)

        en.openHydraulicAnalysis()
        en.initializeHydraulicAnalysis()
        
        while True:
            en.setTimeSimulationDuration(en.getTimeSimulationDuration() + en.getTimeHydraulicStep()) # this way the duration is set to infinite.
            
            # controls = get_controls(client) here <---
            # set_controls(en, controls) here <---

            en.runHydraulicAnalysis()

            data = read_data(en)
            # write_data(client, data) here <---
            
            # print(data)
            import json; print(json.dumps(data, indent=4))

            en.nextHydraulicAnalysisStep()

            time.sleep(1)
    except KeyboardInterrupt:
        print(">--- Program interrupted by user ---")
        sys.exit(0) # clean exit confirmed by user action.
    except Exception as e:
        print(f"Failed to run EPANET simulation due to an unexpected error: {e}")
        sys.exit(1)
    finally:
        if 'client' in locals():
            client.close()
        if 'en' in locals():
            en.closeHydraulicAnalysis()
            en.unload()

if __name__ == '__main__':
    main()
