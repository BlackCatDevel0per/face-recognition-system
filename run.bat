@echo off
cd /d %~dp0
start http://localhost:8000
Python38\python.exe run.py %*
pause