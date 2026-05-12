@echo off
cd /d "C:\Users\v-jaggerzhang\Downloads\opencodeProj\meeting_manager"
echo 启动会议管理系统...
start "" /min "C:\Users\v-jaggerzhang\AppData\Local\Programs\Python\Python313\python.exe" -m waitress --host=0.0.0.0 --port=8082 app:app
echo 应用已在后台运行，访问地址：
echo http://127.0.0.1:8082
echo http://%COMPUTERNAME%:8082
echo 如需停止，请运行 stop_app.bat
timeout /t 3 /nobreak >nul