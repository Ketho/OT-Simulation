#!/usr/bin/env python3

from epyt import epanet
from pymodbus.client import ModbusTcpClient

import sys
import time

def main():
    try:
        client = ModbusTcpClient(host='openplc', port=502)
        while not client.connect(): time.sleep(1) # retrying every second until a successful connection is established.

        en = epanet('net1_tank_scenario.inp')
        en.setTimeSimulationDuration(10) # initial setup; duration will be set to infinite in main function.
        en.setTimeHydraulicStep(1)

        en.openHydraulicAnalysis()
        en.initializeHydraulicAnalysis()

        while True:
            en.setTimeSimulationDuration(en.getTimeSimulationDuration() + en.getTimeHydraulicStep()) # this way the duration is set to infinite.

            # Get controls from OpenPLC.
            controls = {'pipe_statuses': client.read_coils(0, 100).bits, 'pump_settings': [i / 100.0 for i in client.read_holding_registers(0, 100).registers]}

            # Set OpenPLC controls to EPANET network.
            for i, status in zip(en.getLinkPipeIndex(), controls['pipe_statuses']): en.setLinkStatus(i, status)
            for i, setting in zip(en.getLinkPumpIndex(), controls['pump_settings']): en.setLinkSettings(i, setting)

            en.runHydraulicAnalysis()

            # Read data from EPANET network.
            data = {'junction_pressures': [float(en.getNodePressure(i)) for i in en.getNodeJunctionIndex()], 'tank_heads': [float(en.getNodeHydraulicHead(i)) for i in en.getNodeTankIndex()], 'pump_flows': [float(en.getLinkFlows(i)) for i in en.getLinkPumpIndex()]}
            
            # Write EPANET network data to OpenPLC.
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

