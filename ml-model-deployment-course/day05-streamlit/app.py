"""
Day 5: Streamlit 可视化部署机器学习模型

功能：
1. 交互式鸢尾花分类预测
2. 模型可视化
3. 数据集探索
4. CSV 批量预测

运行方式：
    streamlit run app.py
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
import joblib
import os

# ========== 页面配置 ==========
st.set_page_config(
    page_title="🌸 鸢尾花分类器",
    page_icon="🌸",
    layout="wide"
)

# ========== 缓存加载模型 ==========
@st.cache_resource
def load_or_train_model():
    """加载或训练模型（使用缓存，避免重复训练）"""
    model_path = "iris_streamlit_model.pkl"
    
    if os.path.exists(model_path):
        model = joblib.load(model_path)
    else:
        iris = load_iris()
        model = DecisionTreeClassifier(max_depth=3, random_state=42)
        model.fit(iris.data, iris.target)
        joblib.dump(model, model_path)
    
    return model

@st.cache_data
def load_iris_data():
    """加载鸢尾花数据集"""
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df['species'] = [iris.target_names[t] for t in iris.target]
    return iris, df

# ========== 加载数据和模型 ==========
iris, iris_df = load_iris_data()
model = load_or_train_model()
CLASS_NAMES = ["山鸢尾 (setosa)", "变色鸢尾 (versicolor)", "维吉尼亚鸢尾 (virginica)"]

# ========== 标题 ==========
st.title("🌸 鸢尾花分类器")
st.markdown("---")

# ========== 侧边栏 ==========
st.sidebar.header("🔧 参数设置")

# 选择功能页面
page = st.sidebar.radio(
    "选择功能",
    ["🔮 在线预测", "📊 数据探索", "📁 批量预测", "ℹ️ 关于模型"]
)

# =============================================
# 页面1：在线预测
# =============================================
if page == "🔮 在线预测":
    st.header("🔮 在线预测")
    st.write("调整下方的滑块，实时查看预测结果")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌺 花萼 (Sepal)")
        sepal_length = st.slider(
            "花萼长度 (cm)",
            min_value=4.0, max_value=8.0, value=5.1, step=0.1
        )
        sepal_width = st.slider(
            "花萼宽度 (cm)",
            min_value=2.0, max_value=4.5, value=3.5, step=0.1
        )
    
    with col2:
        st.subheader("🌷 花瓣 (Petal)")
        petal_length = st.slider(
            "花瓣长度 (cm)",
            min_value=1.0, max_value=7.0, value=1.4, step=0.1
        )
        petal_width = st.slider(
            "花瓣宽度 (cm)",
            min_value=0.1, max_value=2.5, value=0.2, step=0.1
        )
    
    # 做预测
    features = np.array([[sepal_length, sepal_width, petal_length, petal_width]])
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    
    # 显示结果
    st.markdown("---")
    st.subheader("🎯 预测结果")
    
    result_col1, result_col2 = st.columns([1, 2])
    
    with result_col1:
        st.markdown(f"### {CLASS_NAMES[prediction]}")
        st.metric("置信度", f"{probabilities[prediction]:.1%}")
    
    with result_col2:
        # 概率分布图
        fig, ax = plt.subplots(figsize=(8, 3))
        colors = ['#667eea', '#764ba2', '#f093fb']
        bars = ax.barh(CLASS_NAMES, probabilities, color=colors)
        ax.set_xlim(0, 1)
        ax.set_xlabel("概率")
        ax.set_title("各类别预测概率")
        
        # 在柱子上标注百分比
        for bar, prob in zip(bars, probabilities):
            ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                   f'{prob:.1%}', va='center')
        
        st.pyplot(fig)

# =============================================
# 页面2：数据探索
# =============================================
elif page == "📊 数据探索":
    st.header("📊 数据探索")
    
    # 显示数据集
    st.subheader("📋 数据集预览")
    st.dataframe(iris_df.head(10), use_container_width=True)
    st.caption(f"数据集共 {len(iris_df)} 条记录")
    
    # 特征分布
    st.subheader("📈 特征分布")
    
    feature_col1, feature_col2 = st.columns(2)
    
    with feature_col1:
        feature1 = st.selectbox("选择特征1", iris.feature_names, index=0)
    with feature_col2:
        feature2 = st.selectbox("选择特征2", iris.feature_names, index=2)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    for i, species in enumerate(iris.target_names):
        mask = iris_df['species'] == species
        ax.scatter(
            iris_df.loc[mask, feature1],
            iris_df.loc[mask, feature2],
            label=species,
            alpha=0.7
        )
    ax.set_xlabel(feature1)
    ax.set_ylabel(feature2)
    ax.set_title(f"{feature1} vs {feature2}")
    ax.legend()
    st.pyplot(fig)
    
    # 统计信息
    st.subheader("📐 统计信息")
    st.dataframe(iris_df.describe(), use_container_width=True)

# =============================================
# 页面3：批量预测
# =============================================
elif page == "📁 批量预测":
    st.header("📁 批量预测")
    st.write("上传 CSV 文件进行批量预测")
    
    # 下载示例 CSV
    st.subheader("📥 下载示例文件")
    example_df = pd.DataFrame({
        'sepal_length': [5.1, 6.7, 5.9],
        'sepal_width': [3.5, 3.0, 3.0],
        'petal_length': [1.4, 5.2, 4.2],
        'petal_width': [0.2, 2.3, 1.5]
    })
    st.dataframe(example_df)
    
    csv = example_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "下载示例 CSV",
        data=csv,
        file_name="iris_samples.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    
    # 上传文件
    uploaded_file = st.file_uploader("上传 CSV 文件", type=["csv"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.subheader("上传的数据")
            st.dataframe(df, use_container_width=True)
            
            # 检查列名
            required_cols = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width']
            # 尝试映射常见列名
            col_mapping = {}
            for req_col in required_cols:
                for col in df.columns:
                    if req_col in col.lower() or col.lower() in req_col:
                        col_mapping[req_col] = col
                        break
            
            if len(col_mapping) < 4:
                st.error(f"CSV 文件需要包含以下列：{required_cols}")
                st.info(f"已识别的列映射：{col_mapping}")
            else:
                # 批量预测
                features = df[[col_mapping[c] for c in required_cols]].values
                predictions = model.predict(features)
                probabilities = model.predict_proba(features)
                
                df['prediction'] = [CLASS_NAMES[p] for p in predictions]
                df['confidence'] = [f"{probabilities[i][p]:.1%}" for i, p in enumerate(predictions)]
                
                st.subheader("🔮 预测结果")
                st.dataframe(df, use_container_width=True)
                
                # 下载结果
                result_csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 下载预测结果",
                    data=result_csv,
                    file_name="predictions.csv",
                    mime="text/csv"
                )
        
        except Exception as e:
            st.error(f"处理文件出错：{str(e)}")

# =============================================
# 页面4：关于模型
# =============================================
elif page == "ℹ️ 关于模型":
    st.header("ℹ️ 关于模型")
    
    # 模型信息
    st.subheader("📊 模型信息")
    
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42
    )
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.metric("模型类型", "决策树 (Decision Tree)")
        st.metric("树的最大深度", "3")
    with info_col2:
        st.metric("测试集准确率", f"{accuracy:.1%}")
        st.metric("特征数量", "4")
    
    # 混淆矩阵
    st.subheader("🔢 混淆矩阵")
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, cmap='Blues')
    ax.set_xticks(range(3))
    ax.set_yticks(range(3))
    ax.set_xticklabels(iris.target_names, rotation=45)
    ax.set_yticklabels(iris.target_names)
    ax.set_xlabel("预测值")
    ax.set_ylabel("真实值")
    ax.set_title("混淆矩阵")
    
    for i in range(3):
        for j in range(3):
            ax.text(j, i, cm[i, j], ha='center', va='center', fontsize=16)
    
    st.pyplot(fig)
    
    # 决策树可视化
    st.subheader("🌳 决策树结构")
    from sklearn.tree import export_text
    tree_text = export_text(model, feature_names=iris.feature_names)
    st.text(tree_text)

# ========== 页脚 ==========
st.sidebar.markdown("---")
st.sidebar.info(
    "🌸 鸢尾花分类器\n\n"
    "基于 scikit-learn 决策树模型\n\n"
    "使用 Streamlit 构建"
)
