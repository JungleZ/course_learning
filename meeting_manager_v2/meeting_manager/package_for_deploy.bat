@echo off
chcp 65001 >nul
echo =========================================
echo Meeting Manager 打包脚本（Linux 部署）
echo =========================================
echo.

REM 设置变量
set PACKAGE_NAME=meeting-manager-deploy
set VERSION=1.0.0
set TIMESTAMP=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%

echo [1/4] 清理临时文件...
if exist __pycache__ rmdir /s /q __pycache__
if exist *.pyc del /q *.pyc
if exist meeting.db-wal del /q meeting.db-wal
if exist meeting.db-shm del /q meeting.db-shm

echo [2/4] 创建打包目录...
if exist %PACKAGE_NAME% rmdir /s /q %PACKAGE_NAME%
mkdir %PACKAGE_NAME%

echo [3/4] 复制应用文件...
xcopy app.py %PACKAGE_NAME%\ /Y
xcopy requirements.txt %PACKAGE_NAME%\ /Y
xcopy gunicorn_config.py %PACKAGE_NAME%\ /Y
xcopy .env.example %PACKAGE_NAME%\ /Y
xcopy .gitignore %PACKAGE_NAME%\ /Y

REM 复制部署脚本和文档
xcopy deploy_traditional.sh %PACKAGE_NAME%\ /Y
xcopy deploy.sh %PACKAGE_NAME%\ /Y
xcopy Dockerfile %PACKAGE_NAME%\ /Y
xcopy docker-compose.yml %PACKAGE_NAME%\ /Y
xcopy DEPLOY_QUICK.md %PACKAGE_NAME%\ /Y
xcopy DEPLOY_TRADITIONAL.md %PACKAGE_NAME%\ /Y
xcopy DEPLOYMENT_OPTIONS.md %PACKAGE_NAME%\ /Y
xcopy README_DEPLOY.md %PACKAGE_NAME%\ /Y
xcopy nginx.conf.example %PACKAGE_NAME%\ /Y

REM 复制 Windows 启动脚本（可选）
xcopy start_app.bat %PACKAGE_NAME%\ /Y
xcopy stop_app.bat %PACKAGE_NAME%\ /Y
xcopy package_for_deploy.bat %PACKAGE_NAME%\ /Y

REM 复制模板和静态文件
if exist templates xcopy templates %PACKAGE_NAME%\templates\ /E /Y
if exist static xcopy static %PACKAGE_NAME%\static\ /E /Y

REM 创建数据目录（空）
if not exist %PACKAGE_NAME%\data mkdir %PACKAGE_NAME%\data
if not exist %PACKAGE_NAME%\logs mkdir %PACKAGE_NAME%\logs
if not exist %PACKAGE_NAME%\backup mkdir %PACKAGE_NAME%\backup

echo [4/4] 创建说明文件...
(
echo # Meeting Manager Linux 部署包
echo.
echo ## 📦 包含内容
echo.
echo ### 核心文件
echo - app.py - Flask 应用主文件
echo - requirements.txt - Python 依赖清单
echo - gunicorn_config.py - Gunicorn 配置
echo - templates/ - HTML 模板目录
echo - static/ - 静态资源目录
echo.
echo ### 部署脚本
echo - deploy_traditional.sh - 传统部署脚本（推荐，无需 Docker）
echo - deploy.sh - Docker 部署脚本
echo - Dockerfile - Docker 镜像构建文件
echo - docker-compose.yml - Docker Compose 配置
echo.
echo ### 配置文件
echo - .env.example - 环境变量示例
echo - nginx.conf.example - Nginx 配置示例
echo.
echo ### 文档
echo - DEPLOY_QUICK.md - 快速开始指南
echo - DEPLOY_TRADITIONAL.md - 传统部署详细教程
echo - DEPLOYMENT_OPTIONS.md - 部署方式选择指南
echo - README_DEPLOY.md - 完整部署文档
echo.
echo ## 🚀 快速开始
echo.
echo ### 方式一：传统部署（推荐新手）
echo ```bash
echo chmod +x deploy_traditional.sh
echo sudo ./deploy_traditional.sh
echo ```
echo.
echo ### 方式二：Docker 部署
echo ```bash
echo chmod +x deploy.sh
echo sudo ./deploy.sh
echo ```
echo.
echo 详细文档请查看 DEPLOY_QUICK.md
echo.
) > %PACKAGE_NAME%\README.txt

echo.
echo =========================================
echo ✓ 打包完成！
echo =========================================
echo.
echo 打包目录: %PACKAGE_NAME%
echo.
echo 下一步操作:
echo.
echo 方法 1: 使用压缩软件手动压缩
echo   1. 右键点击 %PACKAGE_NAME% 文件夹
echo   2. 选择"发送到" → "压缩(zipped)文件夹"
echo   3. 上传到 Linux 服务器
echo.
echo 方法 2: 使用 PowerShell 压缩
echo   Compress-Archive -Path %PACKAGE_NAME% -DestinationPath %PACKAGE_NAME%.zip
echo.
echo 方法 3: 使用 7-Zip 或 WinRAR
echo   右键 %PACKAGE_NAME% → 添加到压缩包
echo.
echo 上传到服务器后:
echo   1. 解压: tar xzf %PACKAGE_NAME%.tar.gz 或 unzip %PACKAGE_NAME%.zip
echo   2. 进入目录: cd meeting-manager-deploy
echo   3. 运行部署: sudo ./deploy_traditional.sh
echo.
echo 详细文档: 查看 DEPLOY_QUICK.md 或 README.txt
echo =========================================
pause
