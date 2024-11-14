#!/usr/bin/env python3

from epyt import epanet
from pymodbus.client import ModbusTcpClient

import sys
import time

def print_overview(en: epanet) -> None:
    print("Network Element Counts:")
    print(f"+{'-' * 15}+{'-' * 10}+")
    elements = {
        'junctions': en.getNodeJunctionCount(), 
        'reservoirs': en.getNodeReservoirCount(), 
        'tanks': en.getNodeTankCount(), 
        'pipes': en.getLinkPipeCount(), 
        'pumps': en.getLinkPumpCount(), 
        'valves': en.getLinkValveCount()
    }
    for label, count in elements.items():
        print(f"| {label:<14}|{count:>9} |")
        print(f"+{'-' * 15}+{'-' * 10}+")

def parse_arguments() -> str:
    """Parse command line arguments to retrieve EPANET network file."""
    if len(sys.argv) != 3 or sys.argv[1] != '--network':
        print("Run EPANET simulation with Modbus controls.")
        print(f">>> python {sys.argv[0]} --network [network.inp]")
        sys.exit(1)
    return sys.argv[2]

def setup_client() -> ModbusTcpClient:
    """Setup and establish a Modbus TCP client connection."""
    try:
        client = ModbusTcpClient(host='127.0.0.1', port=502)
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

def get_controls(client: ModbusTcpClient) -> dict:
    """Get controls from OpenPLC."""
    try:
        return {
            'pipe_statuses': client.read_coils(0, 100).bits, 
            'pump_settings': [i / 100.0 for i in client.read_holding_registers(0, 100).registers]
        }
    except Exception as e:
        print(f"Failed to get controls from OpenPLC: {e}")
        sys.exit(1)

def set_controls(en: epanet, controls: dict) -> None:
    """Set OpenPLC controls to EPANET network."""
    try:
        for i, status in zip(en.getLinkPipeIndex(), controls['pipe_statuses']): 
            en.setLinkStatus(i, ~status)
        for i, setting in zip(en.getLinkPumpIndex(), controls['pump_settings']): 
            en.setLinkSettings(i, setting)
    except Exception as e:
        print(f"Failed to set OpenPLC controls to EPANET network: {e}")
        sys.exit(1)

def read_data(en: epanet) -> dict:
    """Read data from EPANET network."""
    try:
        return {
            'junction_pressures': [float(en.getNodePressure(i)) for i in en.getNodeJunctionIndex()], 
            'tank_heads': [float(en.getNodeHydraulicHead(i)) for i in en.getNodeTankIndex()], 
            'pump_flows': [float(en.getLinkFlows(i)) for i in en.getLinkPumpIndex()]
        }
    except Exception as e:
        print(f"Failed to read data from EPANET network: {e}")
        sys.exit(1)

def write_data(client: ModbusTcpClient, data: dict) -> None:
    """Write EPANET network data to OpenPLC."""
    try:
        for i, value in enumerate(data['junction_pressures']):
            registers = client.convert_to_registers(value, client.DATATYPE.FLOAT32)
            client.write_registers(100 + i * 2, registers)

        for i, value in enumerate(data['tank_heads']):
            registers = client.convert_to_registers(value, client.DATATYPE.FLOAT32)
            client.write_registers(200 + i * 2, registers)
        
        for i, value in enumerate(data['pump_flows']):
            registers = client.convert_to_registers(value, client.DATATYPE.FLOAT32)
            client.write_registers(300 + i * 2, registers)
    except Exception as e:
        print(f"Failed to write EPANET network data to OpenPLC: {e}")
        sys.exit(1)

def main():
    network_file = parse_arguments()

    try:
        client = setup_client()
        en = setup_epanet(network_file)
    
        print_overview(en)

        en.openHydraulicAnalysis()
        en.initializeHydraulicAnalysis()
        
        while True:
            en.setTimeSimulationDuration(en.getTimeSimulationDuration() + en.getTimeHydraulicStep()) # this way the duration is set to infinite.

            controls = get_controls(client)
            set_controls(en, controls)

            en.runHydraulicAnalysis()

            data = read_data(en)
            write_data(client, data)

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

