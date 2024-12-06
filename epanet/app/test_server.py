#!/usr/bin/env python3
import time
import sys

from pyModbusTCP.server import ModbusServer

def main():
    try:
        server = ModbusServer(host='127.0.0.1', port=502, no_block=True)
        server.start()
        
        if server.is_run:
            print("=== Modbus server started successfully ===")
            print("Status: \033[92mRunning\033[0m")

            # server.data_bank.set_discrete_inputs(0, [False]*100)
            # server.data_bank.set_coils(0, [False]*100)
            # server.data_bank.set_input_registers(0, [0]*100)
            server.data_bank.set_holding_registers(0, [0]*500)

            while True:
                # di = server.data_bank.get_discrete_inputs(0, 100)
                # co = server.data_bank.get_coils(0, 100)
                # ir = server.data_bank.get_input_registers(0, 100)
                # hr = server.data_bank.get_holding_registers(0, 100)

                hr_0_10 = server.data_bank.get_holding_registers(0, 10)
                hr_100_110 = server.data_bank.get_holding_registers(100, 10)
                hr_200_210 = server.data_bank.get_holding_registers(200, 10)

                print()
                print(f"   0-10: {hr_0_10}")
                print(f"100-110: {hr_100_110}")
                print(f"200-210: {hr_200_210}")

                time.sleep(3)
    except KeyboardInterrupt:
        print(">--- Program interrupted by user ---")
        sys.exit(0) # clean exit confirmed by user action.
    except Exception as e:
        print(e) 
        sys.exit(1)
    finally:
        if 'server' in locals():
            server.stop()
            print("Status: \033[91mStopped\033[0m")
    
if __name__ == '__main__':
    main()
