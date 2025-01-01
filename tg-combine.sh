#! /bin/bash
DIR=$(dirname $0)
cd $DIR
source .venv/bin/activate
python3 tg_combine.py $@
deactivate