@echo off
chcp 65001 >nul
echo ========================================
echo   启动所有Web应用
echo ========================================
echo.

echo [1/2] 正在启动 DISC领导力测试 (端口 8088)...
start "DISC Leadership Test" cmd /k "cd /d %~dp0disc_leadership_test && C:\Users\v-jaggerzhang\.conda\envs\PythonProject1\python.exe -m http.server 8088"
timeout /t 2 /nobreak >nul

echo [2/2] 正在启动 Love App (端口 5000)...
start "Love App" cmd /k "cd /d %~dp0love_app && C:\Users\v-jaggerzhang\.conda\envs\PythonProject1\python.exe app.py"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   所有应用已启动！
echo ========================================
echo.
echo 📊 DISC领导力测试: http://localhost:8088
echo 💕 Love App:        http://localhost:5000
echo.
echo 提示: 每个应用会在单独的窗口中运行
echo 关闭窗口即可停止对应的应用
echo.
pause
