@echo off
cd /d %~dp0
start http://localhost:8000
WPy64-38100\python-3.8.10.amd64\python.exe run.py %*
pause