#!/bin/bash
cd /home/pi/climbBackEnd
git pull origin develop
source /home/pi/climbBackEnd/venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart climb_app
echo "Application updated and restarted successfully."
