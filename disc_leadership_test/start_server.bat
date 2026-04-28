@echo off
echo ========================================
echo DISC领导力测试应用
echo ========================================
echo.
echo 正在启动HTTP服务器...
echo.
echo 请访问以下地址:
echo http://localhost:8088
echo.
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.

cd /d "%~dp0"
C:\Users\v-jaggerzhang\.conda\envs\PythonProject1\python.exe -m http.server 8088

pause
