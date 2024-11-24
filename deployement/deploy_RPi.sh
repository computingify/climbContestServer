#!/bin/bash

ssh pi@192.168.0.36 << EOF
cd ~/climbBackEnd
git fetch -a
sudo systemctl stop climb_app
git reset --hard origin/develop
source venv/bin/activate
pip install -r deployement/requirements.txt
deactivate
sudo systemctl start climb_app
EOF
