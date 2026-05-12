"""
Day 6: Gradio 快速构建 ML Demo

功能：
1. 鸢尾花分类预测界面
2. 概率分布可视化
3. 示例数据一键填入
4. 支持 HuggingFace Spaces 部署

运行方式：
    python app.py

部署到 HuggingFace Spaces：
    1. 创建 Space，选择 Gradio SDK
    2. 上传 app.py 和 requirements.txt
"""

import gradio as gr
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
import joblib
import os

# ========== 加载/训练模型 ==========
MODEL_PATH = "iris_gradio_model.pkl"

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    iris = load_iris()
    model = DecisionTreeClassifier(max_depth=3, random_state=42)
    model.fit(iris.data, iris.target)
    joblib.dump(model, MODEL_PATH)

CLASS_NAMES = ["山鸢尾 (setosa)", "变色鸢尾 (versicolor)", "维吉尼亚鸢尾 (virginica)"]
CLASS_NAMES_EN = ["setosa", "versicolor", "virginica"]


# ========== 预测函数 ==========
def predict(sepal_length, sepal_width, petal_length, petal_width):
    """
    预测函数 - Gradio 会自动调用这个函数
    
    参数：4个花的测量值
    返回：预测标签（字典格式）+ 概率图
    """
    features = np.array([[sepal_length, sepal_width, petal_length, petal_width]])
    
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    
    # 构建标签输出（Gradio Label 组件需要字典格式）
    label_dict = {CLASS_NAMES_EN[i]: float(probabilities[i]) for i in range(3)}
    
    # 绘制概率图
    fig, ax = plt.subplots(figsize=(8, 3))
    colors = ['#667eea', '#764ba2', '#f093fb']
    bars = ax.barh(CLASS_NAMES, probabilities, color=colors)
    ax.set_xlim(0, 1)
    ax.set_xlabel("概率")
    ax.set_title("预测概率分布")
    
    for bar, prob in zip(bars, probabilities):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
               f'{prob:.1%}', va='center')
    
    return label_dict, fig


def predict_batch(csv_file):
    """
    批量预测函数
    """
    import pandas as pd
    
    if csv_file is None:
        return None
    
    df = pd.read_csv(csv_file.name)
    
    # 尝试识别列名
    col_map = {}
    for col in df.columns:
        col_lower = col.lower()
        if 'sepal' in col_lower and 'length' in col_lower:
            col_map[0] = col
        elif 'sepal' in col_lower and 'width' in col_lower:
            col_map[1] = col
        elif 'petal' in col_lower and 'length' in col_lower:
            col_map[2] = col
        elif 'petal' in col_lower and 'width' in col_lower:
            col_map[3] = col
    
    if len(col_map) < 4:
        # 假设前4列就是特征
        features = df.iloc[:, :4].values
    else:
        features = df[[col_map[i] for i in range(4)]].values
    
    predictions = model.predict(features)
    probabilities = model.predict_proba(features)
    
    df['预测品种'] = [CLASS_NAMES[p] for p in predictions]
    df['置信度'] = [f"{probabilities[i][p]:.1%}" for i, p in enumerate(predictions)]
    
    return df


# ========== 构建 Gradio 界面 ==========

# 示例数据
examples = [
    [5.1, 3.5, 1.4, 0.2],  # 山鸢尾
    [6.7, 3.0, 5.2, 2.3],  # 维吉尼亚鸢尾
    [5.9, 3.0, 4.2, 1.5],  # 变色鸢尾
    [4.9, 2.4, 3.3, 1.0],  # 变色鸢尾
    [7.7, 3.8, 6.7, 2.2],  # 维吉尼亚鸢尾
]

with gr.Blocks(title="🌸 鸢尾花分类器", theme=gr.themes.Soft()) as demo:
    
    gr.Markdown(
        """
        # 🌸 鸢尾花分类器
        输入花的测量数据，AI 帮你识别品种！
        """
    )
    
    with gr.Tab("🔮 在线预测"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 输入测量数据")
                sepal_length = gr.Slider(4.0, 8.0, value=5.1, step=0.1, label="花萼长度 (cm)")
                sepal_width = gr.Slider(2.0, 4.5, value=3.5, step=0.1, label="花萼宽度 (cm)")
                petal_length = gr.Slider(1.0, 7.0, value=1.4, step=0.1, label="花瓣长度 (cm)")
                petal_width = gr.Slider(0.1, 2.5, value=0.2, step=0.1, label="花瓣宽度 (cm)")
                
                predict_btn = gr.Button("🔮 开始预测", variant="primary")
                
                gr.Examples(
                    examples=examples,
                    inputs=[sepal_length, sepal_width, petal_length, petal_width],
                    label="📌 点击示例快速填入"
                )
            
            with gr.Column():
                gr.Markdown("### 预测结果")
                label_output = gr.Label(label="品种预测", num_top_classes=3)
                plot_output = gr.Plot(label="概率分布")
        
        predict_btn.click(
            fn=predict,
            inputs=[sepal_length, sepal_width, petal_length, petal_width],
            outputs=[label_output, plot_output]
        )
    
    with gr.Tab("📁 批量预测"):
        gr.Markdown("### 上传 CSV 文件批量预测")
        gr.Markdown("CSV 文件应包含列：sepal_length, sepal_width, petal_length, petal_width")
        
        csv_input = gr.File(label="上传 CSV 文件", file_types=[".csv"])
        batch_output = gr.Dataframe(label="预测结果")
        
        csv_input.change(
            fn=predict_batch,
            inputs=csv_input,
            outputs=batch_output
        )
    
    with gr.Tab("ℹ️ 关于"):
        gr.Markdown(
            """
            ### 关于这个应用
            
            - **模型**：决策树分类器（Decision Tree）
            - **数据集**：鸢尾花（Iris）数据集
            - **特征**：花萼长度、花萼宽度、花瓣长度、花瓣宽度
            - **类别**：山鸢尾、变色鸢尾、维吉尼亚鸢尾
            
            ### 技术栈
            - scikit-learn - 模型训练
            - Gradio - 界面构建
            - Matplotlib - 可视化
            """
        )

# ========== 启动 ==========
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False  # 设为 True 可生成公网临时链接
    )
