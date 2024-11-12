#!/usr/bin/env python3

from epyt import epanet
from pymodbus.client import ModbusTcpClient

import sys
import time

def parse_arguments() -> str:
    if len(sys.argv) != 3 or sys.argv[1] != '--network':
        print("Usage: python script.py --network [network.inp]")
        sys.exit(1)
    return sys.argv[2]

def setup_epanet_network(network_file: str) -> epanet:
    try:
        en = epanet(network_file)
        en.setTimeSimulationDuration(10) # initial setup; duration will be set to infinite in main function.
        en.setTimeHydraulicStep(1)
        return en
    except Exception as e:
        print(e)
        sys.exit(1)

def setup_modbus_client() -> ModbusTcpClient:
    try:
        modbus_client = ModbusTcpClient(host='127.0.0.1', port=502)
        while not modbus_client.connected:
            modbus_client.connect()
            time.sleep(1)
        return modbus_client
    except Exception as e:
        print(e)
        sys.exit(1)
    
def get_controls_from_openplc(modbus_client: ModbusTcpClient) -> dict:
    try:
        pipe_controls = modbus_client.read_coils(0, 100)
        pump_controls = modbus_client.read_holding_registers(0, 100)
        pump_controls_float = [
            i / 100.0 for i in pump_controls.registers
        ]
        openplc_controls = {
            'pipe_controls': pipe_controls.bits,
            'pump_controls': pump_controls_float
        }
        return openplc_controls
    except Exception as e:
        print(e)
        return {}
    
def apply_openplc_controls_to_epanet(epanet_network: epanet, openplc_controls: dict) -> None:
    try:
        pipe_controls = openplc_controls.get('pipe_controls', [])
        pipe_indices = epanet_network.getLinkPipeIndex()
        for i in range(min(len(pipe_indices), len(pipe_controls))):
            epanet_network.setLinkStatus(pipe_indices[i], pipe_controls[i])

        pump_controls = openplc_controls.get('pump_controls', [])
        pump_indices = epanet_network.getLinkPumpIndex()
        for i in range(min(len(pump_indices), len(pump_controls))):
            epanet_network.setLinkSettings(pump_indices[i], pump_controls[i])
    except Exception as e:
        print(e)
    
def read_epanet_data(epanet_network: epanet) -> dict:
    try:
        junction_pressures = [
            epanet_network.getNodePressure(i) for i in epanet_network.getNodeJunctionIndex()
        ]
        tank_heads = [
            epanet_network.getNodeHydraulicHead(i) for i in epanet_network.getNodeTankIndex()
        ]
        pump_flows = [
            epanet_network.getLinkFlows(i) for i in epanet_network.getLinkPumpIndex()
        ]
        epanet_data = {
            'junction_pressures': junction_pressures,
            'tank_heads': tank_heads,
            'pump_flows': pump_flows
        }
        return epanet_data
    except Exception as e:
        print(e)
        return {}

def write_epanet_data_to_openplc(modbus_client: ModbusTcpClient, epanet_data: dict) -> None:
    try:
        junction_pressures = epanet_data.get('junction_pressures', [])
        converted_junction_pressures = []
        for i in junction_pressures:
            converted_junction_pressures.extend(modbus_client.convert_to_registers(i, modbus_client.DATATYPE.FLOAT32))
        modbus_client.write_registers(100, converted_junction_pressures)

        tank_heads = epanet_data.get('tank_heads', [])
        converted_tank_heads = []
        for i in tank_heads:
            converted_tank_heads.extend(modbus_client.convert_to_registers(i, modbus_client.DATATYPE.FLOAT32))
        modbus_client.write_registers(200, converted_tank_heads)
        
        pump_flows = epanet_data.get('pump_flows', [])
        converted_pump_flows = []
        for i in pump_flows:
            converted_pump_flows.extend(modbus_client.convert_to_registers(i, modbus_client.DATATYPE.FLOAT32))
        modbus_client.write_registers(300, converted_pump_flows)
    except Exception as e:
        print(e)

def main():
    try:
        network_file = parse_arguments()

        epanet_network = setup_epanet_network(network_file=network_file)
        modbus_client = setup_modbus_client()

        epanet_network.openHydraulicAnalysis()
        epanet_network.initializeHydraulicAnalysis()
        
        while True:
            epanet_network.setTimeSimulationDuration( # this way the duration is set to infinite.
                epanet_network.getTimeSimulationDuration() + epanet_network.getTimeHydraulicStep()
            )

            openplc_controls = get_controls_from_openplc(modbus_client=modbus_client)
            apply_openplc_controls_to_epanet(epanet_network=epanet_network, openplc_controls=openplc_controls)
            
            epanet_network.runHydraulicAnalysis()
            
            epanet_data = read_epanet_data(epanet_network=epanet_network)
            write_epanet_data_to_openplc(modbus_client=modbus_client, epanet_data=epanet_data)

            epanet_network.nextHydraulicAnalysisStep()
            time.sleep(1)
    except KeyboardInterrupt:
        print(">--- Program interrupted by user ---")
        
        epanet_network.closeHydraulicAnalysis()
        epanet_network.unload()

        modbus_client.close()
        sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)

if __name__ == '__main__':
    main()

