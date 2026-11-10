@echo off
rem Ouvre la fenêtre de démonstration de la maquette RAO (sans console PowerShell visible).
start "" powershell.exe -NoProfile -STA -ExecutionPolicy Bypass -WindowStyle Hidden -File "%~dp0demo_rao.ps1"
