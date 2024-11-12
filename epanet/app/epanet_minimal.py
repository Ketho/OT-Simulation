#!/usr/bin/env python3

from epyt import epanet
from pymodbus.client import ModbusTcpClient

import time

client = ModbusTcpClient(host='openplc', port=502)
while not client.connect(): time.sleep(1)

en = epanet('net1_tank_scenario.inp')
en.setTimeSimulationDuration(24 * 60 * 60) # initial setup; duration will be set to infinite in main function.
en.setTimeHydraulicStep(60 * 60)

try:
    en.openHydraulicAnalysis()
    en.initializeHydraulicAnalysis()

    while True:
        en.setTimeSimulationDuration(en.getTimeSimulationDuration() + en.getTimeHydraulicStep()) # this way the duration is set to infinite.

        # Get controls from OpenPLC
        controls = {'pipe': client.read_coils(0, 100).bits, 'pump': client.read_holding_registers(0, 100).registers}

        # Set OpenPLC controls to EPANET
        for i, control in zip(en.getLinkPipeIndex(), controls['pipe']): en.setLinkStatus(i, control)
        for i, control in zip(en.getLinkPumpIndex(), controls['pump']): en.setLinkSettings(i, ~control & 1)

        en.runHydraulicAnalysis()

        # Get data from EPANET
        data = {'junction_pressures': [float(en.getNodePressure(i)) for i in en.getNodeJunctionIndex()], 'tank_heads': [float(en.getNodeHydraulicHead(i)) for i in en.getNodeTankIndex()], 'pump_flows': [float(en.getLinkFlows(i)) for i in en.getLinkPumpIndex()]}
        print(data)

        # Write data to OpenPLC
        for i, value in enumerate(data['junction_pressures']):
            registers = client.convert_to_registers(value, client.DATATYPE.FLOAT32)
            client.write_registers(100 + i * 2, registers)

        for i, value in enumerate(data['tank_heads']):
            registers = client.convert_to_registers(value, client.DATATYPE.FLOAT32)
            client.write_registers(200 + i * 2, registers)

        for i, value in enumerate(data['pump_flows']):
            registers = client.convert_to_registers(value, client.DATATYPE.FLOAT32)
            client.write_registers(300 + i * 2, registers)

        en.nextHydraulicAnalysisStep()

        time.sleep(1)
except KeyboardInterrupt:
    client.close()
    
    en.closeHydraulicAnalysis()
    en.unload()

