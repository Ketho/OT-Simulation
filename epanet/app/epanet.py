#!/usr/bin/env python3
import time
import sys

from pymodbus.client import ModbusTcpClient
from epyt import epanet

def setup_client() -> ModbusTcpClient:
    try:
        client = ModbusTcpClient(host='openplc', port=502) # default setup; hardcoded host and port for now.
        while not client.connect(): 
            time.sleep(1)
        return client
    except Exception as e:
        print(e)
        sys.exit(1)

def setup_epanet(inp_file: str) -> epanet:
    try:
        en = epanet(inp_file)
        en.setTimeSimulationDuration(10) # initial setup; duration will be set to infinite in main function.
        en.setTimeHydraulicStep(1)
        return en
    except Exception as e:
        print(e)
        sys.exit(1)

def parse_arguments() -> str:
    """Simple function to retrieve the required network (.inp) file from command-line arguments."""
    if len(sys.argv) != 2 or not sys.argv[1].endswith('.inp'):
        print("Run EPANET simulation with Modbus controls.")
        print(f">>> python {sys.argv[0]} [network.inp]")
        sys.exit(1)
    return sys.argv[1]

def get_controls(client: ModbusTcpClient) -> dict:
    try:
        ...
    except Exception as e:
        print(e)
        sys.exit(1)

def set_controls(en: epanet, controls: dict) -> None:
    try:
        ...
    except Exception as e:
        print(e)
        sys.exit(1)

def read_data(en: epanet) -> dict:
    """Gathers data from an EPANET network and categorizes it into zones."""
    try:
        data = {}
        
        for i in en.getNodeNameID() + en.getLinkNameID():
            if '-' not in i:
                continue
            zone, element = i.split('-', 1)

            if zone not in data:
                data[zone] = {}
            if element not in data[zone]:
                data[zone][element] = {}
            
            if i in en.getNodeNameID():
                data[zone][element]['hydraulic_head'] = en.getNodeHydraulicHead(en.getNodeIndex(i))

            if i in en.getLinkNameID():
                data[zone][element]['pump_power'] = en.getLinkPumpPower(en.getLinkIndex(i))
        
        return data
    except Exception as e:
        print(e)
        sys.exit(1)

def write_data(client: ModbusTcpClient, data: dict) -> None:
    try:
        for i, (_, elements) in enumerate(data.items()):
            zone_offset = i * 100
            
            for j, (_, values) in enumerate(elements.items()):
                element_offset = j * 2
                
                for _, v in values.items():
                    registers = client.convert_to_registers(float(v), client.DATATYPE.FLOAT32)

                    address = zone_offset + element_offset
                    client.write_registers(address, registers)
                    
                    #print(f"writing value {v} (converted to registers: {registers}) from {zone} -> {element} -> {k} to register address {address}")
    except Exception as e:
        print(e)
        sys.exit(1)

def main(): 
    inp_file = parse_arguments()
    
    try:
        client = setup_client()
        en = setup_epanet(inp_file)

        en.openHydraulicAnalysis()
        en.initializeHydraulicAnalysis()

        while True: 
            en.setTimeSimulationDuration(en.getTimeSimulationDuration() + en.getTimeHydraulicStep()) # this way the duration is set to infinite.

            # controls = get_controls(client)
            # set_controls(en, controls)

            en.runHydraulicAnalysis()

            data = read_data(en)#; print(data)
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
