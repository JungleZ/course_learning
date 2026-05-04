# Day 5: MLFlow Projects - 让代码可复现

## 🎯 今天的目标

- 理解什么是MLFlow Project
- 学会创建MLproject文件
- 使用MLFlow运行项目
- 理解可复现性的重要性

## 🤔 什么是MLFlow Project？（小白版解释）

想象你写了一个很棒的机器学习代码，发给同事：
- 同事：你这代码在我电脑上报错了！
- 你：奇怪，我这边好好的啊...
- 同事：我Python版本是3.7，你呢？
- 你：我是3.10...
- 同事：我还没有安装sklearn...
- 你：......（崩溃）

**MLFlow Project就是解决这个问题的！**

它把你的代码、依赖环境、运行参数都打包在一个标准格式里，别人拿到后一键就能跑，不用操心环境问题。

## 📦 MLFlow Project的组成部分

一个标准的MLFlow Project包含：

```
你的项目文件夹/
├── MLproject          # 项目配置文件（最重要！）
├── conda.yaml         # 依赖环境配置（可选，推荐）
├── train.py           # 训练代码
└── 其他文件...
```

**核心文件：MLproject**（注意没有后缀）

## 💻 Demo: 创建一个MLFlow Project

### 步骤1: 创建项目文件夹和代码

创建文件夹 `week1/day5/my_project/`，然后在里面创建文件。

**文件1: `week1/day5/my_project/train.py`**

```python
"""
MLFlow Project示例 - 训练鸢尾花分类器
这个脚本可以通过MLFlow Project方式运行
"""

import argparse
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train_model(n_estimators, max_depth, random_state):
    """
    训练随机森林模型
    
    参数:
        n_estimators: 树的数量
        max_depth: 树的最大深度
        random_state: 随机种子
    """
    # 设置MLFlow跟踪
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("MLFlow-Project-Day5")
    
    with mlflow.start_run(run_name="Project训练"):
        print(f"🚀 开始训练...")
        print(f"   参数: n_estimators={n_estimators}, max_depth={max_depth}")
        
        # 记录参数
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("random_state", random_state)
        
        # 加载数据
        X, y = load_iris(return_X_y=True)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=random_state
        )
        
        # 训练模型
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state
        )
        model.fit(X_train, y_train)
        
        # 评估
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # 记录指标
        mlflow.log_metric("accuracy", accuracy)
        
        # 保存模型
        mlflow.sklearn.log_model(model, "random_forest_model")
        
        # 打标签
        mlflow.set_tag("project_type", "MLFlow Project Demo")
        mlflow.set_tag("framework", "sklearn")
        
        print(f"✅ 训练完成! 准确率: {accuracy:.2%}")
        print(f"📊 查看结果: http://localhost:5000")
        
        return accuracy

if __name__ == "__main__":
    # 使用argparse解析命令行参数
    parser = argparse.ArgumentParser(description="训练随机森林分类器")
    
    parser.add_argument(
        "--n_estimators",
        type=int,
        default=100,
        help="随机森林中树的数量 (默认: 100)"
    )
    
    parser.add_argument(
        "--max_depth",
        type=int,
        default=None,
        help="树的最大深度 (默认: None, 表示不限制)"
    )
    
    parser.add_argument(
        "--random_state",
        type=int,
        default=42,
        help="随机种子 (默认: 42)"
    )
    
    args = parser.parse_args()
    
    # 调用训练函数
    train_model(args.n_estimators, args.max_depth, args.random_state)
```

### 步骤2: 创建MLproject文件

**文件2: `week1/day5/my_project/MLproject`** （无后缀名）

```yaml
# MLFlow Project配置文件
# 这个文件定义了如何运行这个项目

name: 鸢尾花分类器项目

# Python环境配置（使用conda）
conda_env: conda.yaml

# 入口点（可以定义多个）
entry_points:
  main:
    # 主入口点执行的命令
    command: "python train.py --n_estimators {n_estimators} --max_depth {max_depth} --random_state {random_state}"
    
    # 定义参数及其默认值
    parameters:
      n_estimators:
        type: int
        default: 100
      max_depth:
        type: int
        default: 10
      random_state:
        type: int
        default: 42
```

### 步骤3: 创建conda.yaml环境文件

**文件3: `week1/day5/my_project/conda.yaml`**

```yaml
# 定义项目依赖的环境
name: mlflow-project-env
channels:
  - defaults
  - conda-forge
dependencies:
  - python=3.9
  - pip
  - pip:
    - mlflow>=2.0
    - scikit-learn>=1.0
    - pandas
    - numpy
```

**但是！** 如果你不想用conda（很多小白不会用），可以用更简单的方式：直接让MLFlow用当前Python环境。

修改 `MLproject` 文件，使用 `python_env` 替代 `conda_env`：

```yaml
name: 鸢尾花分类器项目

# 使用Python虚拟环境（更简单）
python_env: python_env.yaml

entry_points:
  main:
    command: "python train.py --n_estimators {n_estimators} --max_depth {max_depth} --random_state {random_state}"
    parameters:
      n_estimators:
        type: int
        default: 100
      max_depth:
        type: int
        default: 10
      random_state:
        type: int
        default: 42
```

然后创建 `python_env.yaml`：

```yaml
# Python环境配置（更简单的版本）
python: "3.9"
dependencies:
  - mlflow>=2.0
  - scikit-learn>=1.0
  - pandas
  - numpy
```

## ▶️ 运行MLFlow Project

**方法1: 使用mlflow run命令（推荐）**

```bash
# 确保在项目根目录
cd D:\code_workspaces\mlflow-learning

# 运行项目（使用默认参数）
mlflow run week1/day5/my_project

# 运行项目（指定参数）
mlflow run week1/day5/my_project -P n_estimators=200 -P max_depth=20
```

**方法2: 不用MLproject文件，直接运行Python脚本**

```bash
# 其实也可以直接运行，但这样就不是"Project"了
cd week1/day5/my_project
python train.py --n_estimators 200 --max_depth 20
```

## 📊 查看结果

运行后，打开 http://localhost:5000，你会看到：
- 实验名称: "MLFlow-Project-Day5"
- 里面有你运行的记录
- 参数、指标、模型都记录好了！

## 🎓 MLFlow Project的好处

| 好处 | 说明 |
|------|------|
| **可复现** | 别人拿到你的代码，一键就能跑出一样的结果 |
| **环境隔离** | 每个项目用独立的环境，不会互相干扰 |
| **参数化** | 通过命令行传参数，不用改代码 |
| **标准化** | 大家用一样的格式，团队协作更方便 |

## 💻 进阶Demo: 多个入口点

有时候一个项目有多个步骤（比如：预处理、训练、评估）。可以在MLproject里定义多个入口点。

修改 `MLproject`：

```yaml
name: 鸢尾花完整项目

python_env: python_env.yaml

entry_points:
  # 入口点1: 训练模型
  train:
    command: "python train.py --n_estimators {n_estimators} --max_depth {max_depth}"
    parameters:
      n_estimators:
        type: int
        default: 100
      max_depth:
        type: int
        default: 10
  
  # 入口点2: 评估模型（假设有evaluate.py）
  evaluate:
    command: "python evaluate.py --model_uri {model_uri}"
    parameters:
      model_uri:
        type: string
        default: "runs:/最新RunID/model"
```

运行指定入口点：
```bash
mlflow run week1/day5/my_project -e evaluate
```

## 📝 实践小练习

**任务：** 修改 `train.py`，添加一个新的参数 `test_size`（测试集比例），并在MLproject文件里也添加这个参数。

提示：
1. 在 `train.py` 里用 `parser.add_argument` 添加 `--test_size`
2. 在 `MLproject` 文件的parameters里也添加 `test_size`
3. 用 `mlflow run` 命令指定新的参数运行

## 🎓 今天总结

- ✅ 理解了MLFlow Project的概念和用处
- ✅ 学会了创建MLproject配置文件
- ✅ 学会了用 `mlflow run` 命令运行项目
- ✅ 理解了可复现性的重要性

## 💡 什么时候用MLFlow Project？

- ✅ 要分享代码给别人
- ✅ 要在不同机器上运行同一个项目
- ✅ 要做自动化（比如CI/CD流水线）
- ❌ 只是自己随便试试（那就直接跑Python脚本就行）

## 🚀 下一步

明天我们将学习MLFlow Models，了解如何保存、加载和部署模型！

👉 **明天见： [Day 6 - MLFlow Models](D:\code_workspaces\mlflow-learning\week1\day6\)**
