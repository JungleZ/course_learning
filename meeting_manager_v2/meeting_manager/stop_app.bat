@echo off
echo 停止会议管理系统...
taskkill /f /fi "IMAGENAME eq python.exe" /fi "WINDOWTITLE eq waitress*" >nul 2>&1
taskkill /f /im python.exe >nul 2>&1
echo 已发送停止信号
timeout /t 2 /nobreak >nul