#!/usr/bin/python3

import time, sys
from epyt import epanet
from pymodbus.client import ModbusTcpClient

def applyControls(n, controls):
    # Removes current controls from .inp
    n.deleteControls()

    pump_controls = controls.get('pump_controls')
    pipe_controls = controls.get('pipe_controls')

    # Set pump speeds based on pumpControls 0 = off 1 = normal speed // higher speeds than 1 are allowed.
    pump_ids = n.getLinkPumpIndex()
    for i in range(min(len(pump_ids), len(pump_controls))):
        n.setLinkSettings(pump_ids[i], pump_controls[i])  # Set the speed for each pump

    # Open or close pipes 1 = Closed, 0 = Open (values are inverted in code so open plc 0 = open )
    pipe_ids = n.getLinkPipeIndex()
    for i in range(min(len(pipe_ids), len(pipe_controls))):
        n.setLinkStatus(pipe_ids[i], ~pipe_controls[i] & 1)

def readValues(n):
    # Initialize a dictionary to store the retrieved data
    data = {
        'tank_heads': [float(n.getNodeHydraulicHead(i)) for i in n.getNodeTankIndex()],
        'pump_flows': [float(n.getLinkFlows(i)) for i in n.getLinkPumpIndex()],
        'junction_pressures': [n.getNodePressure(i) for i in n.getNodeJunctionIndex()],
        'Valves': {},
    }

    # Logic for retrieving data

    return data

def toOpenPLC(client, data):
    # Logic for sending data to OpenPLC via Modbus
    converted_tank_heads = []
    for tank_head in data['tank_heads']:
        converted_tank_heads.extend(client.convert_to_registers(tank_head, client.DATATYPE.FLOAT32))
    client.write_registers(100, converted_tank_heads)

    converted_pump_flows = []
    for pump_flow in data['pump_flows']:
        converted_pump_flows.extend(client.convert_to_registers(pump_flow, client.DATATYPE.FLOAT32))
    client.write_registers(200, converted_pump_flows)

    converted_junction_pressures = []
    for junction_pressure in data['junction_pressures']:
        converted_junction_pressures.extend(client.convert_to_registers(junction_pressure, client.DATATYPE.FLOAT32))
    client.write_registers(300, converted_junction_pressures)

    # VALVE LOGIC HERE...

    #print(data)

def fromOpenPLC(client):
    controls = {
        'pump_controls': [],
        'pipe_controls': []
    }

    pump_controls = client.read_holding_registers(0, 100)
    if pump_controls.isError():
        print(">--- Failed to retrieve pump controls ---")
    else:
        for i in range(0, len(pump_controls.registers), 2):
            if i + 1 < len(pump_controls.registers):
                converted_pump_control = client.convert_from_registers(
                    pump_controls.registers[i:i+2],
                    client.DATATYPE.FLOAT32
                )
                controls['pump_controls'].append(converted_pump_control)

    pipe_controls = client.read_coils(0, 100)
    if pipe_controls.isError():
        print(">--- Failed to retrieve pipe controls ---")
    else:
        controls['pipe_controls'] = pipe_controls.bits

    return controls

def main(inp_file):
    # Sleep for 30 sec to allow OpenPLC to start
    time.sleep(30)
    # Try connecting to OpenPLC
    try:
        client = ModbusTcpClient('openplc', port=502)

        if not client.connect():
            print(">--- Failed to connect to OpenPLC ---")
            return  # Exit if connection fails

        n = epanet(inp_file)
        n.openHydraulicAnalysis()
        n.initializeHydraulicAnalysis()

        # Print network component ammount
        elements = {
            "Tanks": n.getNodeTankCount,
            "Reservoirs": n.getNodeReservoirCount,
            "Junctions": n.getNodeJunctionCount,
            "Pipes": n.getLinkPipeCount,
            "Pumps": n.getLinkPumpCount,
            "Valves": n.getLinkValveCount
        }

        print("Network Element Counts:")
        print("-----------------------")
        for name, func in elements.items():
            print(f"{name:<12}: {func():>5}")
        
        while True:
            # Update the simulation duration
            n.setTimeSimulationDuration(n.getTimeSimulationDuration() +
            n.getTimeHydraulicStep())

            # Retreive controls from OpenPLC
            controls = fromOpenPLC(client)

            # Apply controls
            applyControls(n, controls)

            # Run the hydraulic analysis step
            n.runHydraulicAnalysis()

            # Read network values
            data = readValues(n)

            # Send to OpenPLC
            toOpenPLC(client, data)

            # Advance to the next step
            n.nextHydraulicAnalysisStep()

            # Sleep for 1 second to avoid excessive CPU usage
            time.sleep(1)

    except KeyboardInterrupt:
        print(">--- Program interrupted by user ---")

    # except Exception as e:
    #     print(f"An error occurred: {e}")

    finally:
        if n:
            # Ensure hydraulic analysis is properly closed
            n.closeHydraulicAnalysis()
            n.unload()

        if client:
            # Stop Modbus client
            client.close()

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Usage: python3", sys.argv[0], "<input_file.inp>")
        sys.exit(1)

    inp_file = sys.argv[1]

    main(inp_file)
