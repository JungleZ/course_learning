# 机器学习分类项目

## 项目概述
这是一个完整的机器学习分类项目，使用TensorFlow和scikit-learn进行分类任务。

## 环境要求
- Python 3.8
- conda环境: ml-classification

## 安装依赖
```bash
conda activate ml-classification
conda install tensorflow scikit-learn pandas numpy matplotlib seaborn jupyter
```

## 项目结构
- `data/` - 数据集文件夹
- `models/` - 保存训练好的模型
- `notebooks/` - Jupyter笔记本
- `src/` - 源代码
- `README.md` - 项目说明

## 运行项目
```bash
# 激活环境
conda activate ml-classification

# 运行主程序
python src/main.py

# 或打开Jupyter笔记本
jupyter notebook notebooks/
```

## 功能特点
- 数据预处理和探索性分析
- 多种分类算法实现
- 模型评估和可视化
- 模型保存和加载
- 交互式界面