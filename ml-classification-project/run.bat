@echo off
echo 机器学习分类项目启动脚本
echo =================================

echo 检查Python环境...
python --version

echo.
echo 检查必要的库...
python -c "import pandas, numpy, matplotlib, seaborn; print('基础库已安装')"
python -c "import sklearn; print('scikit-learn已安装')" 2>nul || echo "警告: scikit-learn未安装"

echo.
echo 创建必要的目录...
if not exist "data" mkdir data
if not exist "models" mkdir models
if not exist "notebooks" mkdir notebooks

echo.
echo 启动项目...
echo.

echo 选择运行方式:
echo 1. 运行简化版项目 (使用现有库)
echo 2. 打开Jupyter Notebook
echo 3. 查看项目结构
echo 4. 安装TensorFlow (可选)
echo 5. 退出

set /p choice="请输入选择 (1-5): "

if "%choice%"=="1" (
    echo 运行简化版项目...
    python src/simple_main.py
) else if "%choice%"=="2" (
    echo 启动Jupyter Notebook...
    jupyter notebook notebooks/
) else if "%choice%"=="3" (
    echo 项目结构:
    tree /F
) else if "%choice%"=="4" (
    echo 安装TensorFlow...
    pip install tensorflow
    echo TensorFlow安装完成！
    echo 现在可以运行完整版项目了。
) else if "%choice%"=="5" (
    echo 退出脚本。
    exit /b
) else (
    echo 无效选择，请重新运行脚本。
)

echo.
echo 项目完成！