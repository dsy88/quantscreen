#!/bin/sh
BASEDIF=$(cd `dirname $0`; pwd)
DATAPATH=$BASEDIR/../../../../data

export DJANGO_SETTINGS_MODULE=$1
export PYTHONPATH=$PYTHONPATH:$BASEDIR/../

python import_meta.py $DATAPATH/symbols/

python import_yahoo.py $DATAPATH/yahooQuotes/

python import_reports.py $DATAPATH/reports/

python import_treasuries.py $DATAPATH/treasuries

python import_history.py $DATAPATH/history

python updates.py


