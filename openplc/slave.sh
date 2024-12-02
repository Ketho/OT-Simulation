#!/bin/bash 
# modifying openplc database
# https://github.com/thiagoralves/OpenPLC_v3/blob/master/webserver/openplc.db

# remove all existing programs
SQL_REMOVE_PROGRAM="DELETE FROM Programs"
sqlite3 /OpenPLC_v3/webserver/openplc.db "$SQL_REMOVE_PROGRAM"

# remove all existing slave devices
SQL_REMOVE_DEVICE="DELETE FROM Slave_dev"
sqlite3 /OpenPLC_v3/webserver/openplc.db "$SQL_REMOVE_DEVICE"

# Change or disable Modbus port. Comment out if not requried.
SQL_UPDATE_Modbus="UPDATE Settings SET Value = '502' WHERE Key = 'Modbus_port';"
sqlite3 /OpenPLC_v3/webserver/openplc.db "$SQL_UPDATE_Modbus"

# enable openplc start run mode. Comment out if not requried.
SQL_Start_run_mode="UPDATE Settings SET Value = 'true' WHERE Key = 'Start_run_mode';"
sqlite3 /OpenPLC_v3/webserver/openplc.db "$SQL_Start_run_mode"
