#!/bin/bash

#modifying openplc database
/OpenPLC_v3/database.sh

# set active program
echo "script.st" > /OpenPLC_v3/webserver/active_program
cp /OpenPLC_v3/scripts/script.st /OpenPLC_v3/webserver/st_files

# compile new program for the first time
cd /OpenPLC_v3/webserver/scripts
./compile_program.sh script.st

# generate mbconfig.cfg
cd /OpenPLC_v3/webserver/
python2.7 -c 'import webserver; webserver.generate_mbconfig()'

# start openplc webserver
cd /OpenPLC_v3
./start_openplc.sh
wait