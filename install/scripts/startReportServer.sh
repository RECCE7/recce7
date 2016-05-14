#!/bin/bash
RECCE7_PATH=/usr/sbin/recce7
export RECCE7_PLUGINS_CONFIG=/etc/recce7/configs/plugins.cfg
export RECCE7_GLOBAL_CONFIG=/etc/recce7/configs/global.cfg
cd $RECCE7_PATH
python3 -m reportserver.server.main