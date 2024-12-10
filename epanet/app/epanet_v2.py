#!/usr/bin/env python3
import time
import sys

from pymodbus.client import ModbusTcpClient
from epyt import epanet

def parse_arguments() -> str:
    if len(sys.argv) != 2 or not sys.argv[1].endswith('.inp'):
        print("Run EPANET simulation with Modbus controls.")
        print(f">>> python {sys.argv[0]} [network.inp]")
        sys.exit(1)
    return sys.argv[1]

def get_zones(en: epanet) -> set:
    try:
        zones = set()

        for name_id in en.getNodeNameID() + en.getLinkNameID():
            if '-' not in name_id:
                continue
            zone, _ = name_id.split('-', 1)
            zones.add(zone)
        return zones
    except Exception as e:
        print(f"ERROR in get_zones: {e}")
        sys.exit(1)

def setup_clients(zones: set) -> dict[str, ModbusTcpClient]:
    try:
        clients = {
            zone: ModbusTcpClient(host=f'plc-{zone}', port=502) for zone in zones
        }
        # TEST
        # clients = {
        #     zone: ModbusTcpClient(host='127.0.0.1', port=502 + i)
        #     for i, zone in enumerate(zones)
        # }
        for zone, client in clients.items():
            while not client.connect():
                time.sleep(1)
            print(f"=== Connected to {zone} ===")
        return clients
    except Exception as e:
        print(f"ERROR in setup_clients: {e}")
        sys.exit(1)

def setup_epanet(inp_file: str) -> epanet:
    try:
        en = epanet(inp_file)
        en.setTimeSimulationDuration(10) # initial setup; duration will be set to infinite in main function.
        en.setTimeHydraulicStep(1)
        return en
    except Exception as e:
        print(f"ERROR in setup_epanet: {e}")
        sys.exit(1)

def read_data(en: epanet) -> dict:
    try:
        data = {}

        for name_id in en.getNodeNameID() + en.getLinkNameID():
            if '-' not in name_id:
                continue
            zone, element = name_id.split('-', 1)

            if zone not in data:
                data[zone] = {}
            if element not in data[zone]:
                data[zone][element] = {}

            if name_id in en.getNodeNameID():
                data[zone][element]['hydraulic_head'] = en.getNodeHydraulicHead(en.getNodeIndex(name_id))

            if name_id in en.getLinkNameID():
                data[zone][element]['pump_power'] = en.getLinkPumpPower(en.getLinkIndex(name_id))

        return data
    except Exception as e:
        print(f"ERROR in read_data: {e}")
        sys.exit(1)

def write_data(clients: dict[str, ModbusTcpClient], data: dict) -> None:
    try:
        for zone, elements in data.items():
            if zone not in clients:
                continue
            client = clients[zone]

            for i, (element, values) in enumerate(elements.items()):
                address = i * 2

                for k, value in values.items():
                    registers = client.convert_to_registers(float(value), client.DATATYPE.FLOAT32)
                    client.write_registers(address, registers)
                    # TEST
                    print(f"writing value {value} (converted to registers: {registers}) from {zone} -> {element} -> {k} to register address {address}")
    except Exception as e:
        print(f"ERROR in write_data: {e}")
        sys.exit(1)

def main():
    inp_file = parse_arguments()

    try:
        en = setup_epanet(inp_file)
        zones = get_zones(en)
        clients = setup_clients(zones)

        en.openHydraulicAnalysis()
        en.initializeHydraulicAnalysis()

        while True:
            en.setTimeSimulationDuration(en.getTimeSimulationDuration() + en.getTimeHydraulicStep()) # this way the duration is set to infinite.

            # controls = get_controls(client)
            # set_controls(en, controls)

            en.runHydraulicAnalysis()

            data = read_data(en)
            write_data(clients, data)

            en.nextHydraulicAnalysisStep()

            time.sleep(1)
    except KeyboardInterrupt:
        print(">--- Program interrupted by user ---")
        sys.exit(0) # clean exit confirmed by user action.
    except Exception as e:
        print(f"Failed to run EPANET simulation due to an unexpected error: {e}")
        sys.exit(1)
    finally:
        if 'clients' in locals():
            for client in clients.values():
                client.close()
        if 'en' in locals():
            en.closeHydraulicAnalysis()
            en.unload()

if __name__ == '__main__':
    main()
