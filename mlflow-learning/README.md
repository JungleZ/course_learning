# MLFlow Learning Project

## 项目结构
```
mlflow-learning/
├── week1/day1/test/      # 训练脚本
├── data/raw/             # 原始数据
├── data/processed/       # 处理后数据
├── models/               # 模型存储
├── notebooks/            # 探索分析
├── src/                  # 工具代码
└── logs/                 # 日志
```

## 快速开始

1. 安装依赖
```bash
pip install -r requirements.txt
```

2. 导出数据
```bash
cd mlflow-learning
python src/export_data.py
```

3. 运行训练
```bash
python week1/day1/test/first_experiment.py
```