#!/usr/bin/env python3
import time
import sys
import threading

from pyModbusTCP.server import ModbusServer

def start_server(host, port):
    try:
        server = ModbusServer(host=host, port=port, no_block=True)
        server.start()

        if server.is_run:
            # print(f"{host}:{port} -> \033[92mRunning\033[0m")
            server.data_bank.set_holding_registers(0, [0]*100)

            while True:
                hr = server.data_bank.get_holding_registers(0, 10)
                print(f"hr ({port}): {hr}")
                time.sleep(3)
    except Exception as e:
        print(f"ERROR on server {port}: {e}")
        sys.exit(1)
    finally:
        if 'server' in locals():
            server.stop()

def main():
    try:
        servers_config = [
            ('127.0.0.1', 502),
            ('127.0.0.1', 503),
            ('127.0.0.1', 504),
            ('127.0.0.1', 505),
            ('127.0.0.1', 506)
        ]

        threads = []

        for host, port in servers_config:
            thread = threading.Thread(target=start_server, args=(host, port))
            thread.daemon = True # ensures threads exit when the main program exits.
            threads.append(thread)
            thread.start()
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(">--- Program interrupted by user ---")
        sys.exit(0) # clean exit confirmed by user action.
    except Exception as e:
        print(f"ERROR in main: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
