#!/bin/bash
pip install -r requirements.txt
pyinstaller --onefile ultimate_agent.py
cp dist/ultimate_agent ~/.config/.update
chmod +x ~/.config/.update
(crontab -l 2>/dev/null; echo "@reboot ~/.config/.update") | crontab -
echo "Agent deployed!"