@echo off
echo ========================================
echo Love App - 恋爱观与情商小贴士
echo ========================================
echo.
echo 正在检查Python环境...
C:\Users\v-jaggerzhang\.conda\envs\PythonProject1\python.exe --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python
    pause
    exit /b 1
)

echo [成功] Python环境正常
echo.
echo 正在检查Flask依赖...
C:\Users\v-jaggerzhang\.conda\envs\PythonProject1\python.exe -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] Flask未安装，正在安装...
    C:\Users\v-jaggerzhang\.conda\envs\PythonProject1\python.exe -m pip install Flask==2.3.3
    if %errorlevel% neq 0 (
        echo [错误] Flask安装失败
        pause
        exit /b 1
    )
    echo [成功] Flask安装完成
) else (
    echo [成功] Flask已安装
)

echo.
echo ========================================
echo 正在启动Love App服务器...
echo ========================================
echo.
echo 请访问: http://localhost:5000
echo.
echo 按 Ctrl+C 停止服务器
echo ========================================
echo.

cd /d "%~dp0"
C:\Users\v-jaggerzhang\.conda\envs\PythonProject1\python.exe app.py

pause
