@echo off
echo Running VRO Crisis System..
# 1. Activate VRO Crisis System
python vro_crisis_orchestrator.py

# 2. Test Crisis Detection
python python_run_script.py
