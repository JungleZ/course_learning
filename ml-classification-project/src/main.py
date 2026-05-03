"""
机器学习分类项目 - 主程序
使用多种算法进行分类任务，包括数据预处理、模型训练和评估
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
import joblib
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

class ClassificationProject:
    def __init__(self):
        self.data_path = '../data/'
        self.models_path = '../models/'
        self.scaler = StandardScaler()
        self.models = {}
        self.results = {}
        
    def load_data(self):
        """加载示例数据集 - 使用sklearn的make_classification生成数据"""
        from sklearn.datasets import make_classification
        
        print("正在生成示例数据集...")
        X, y = make_classification(
            n_samples=1000,
            n_features=20,
            n_informative=15,
            n_redundant=5,
            n_classes=3,
            random_state=42
        )
        
        # 创建特征名称
        feature_names = [f'feature_{i}' for i in range(X.shape[1])]
        
        # 创建DataFrame
        df = pd.DataFrame(X, columns=feature_names)
        df['target'] = y
        
        # 保存数据
        os.makedirs(self.data_path, exist_ok=True)
        df.to_csv(os.path.join(self.data_path, 'synthetic_data.csv'), index=False)
        
        print(f"数据集已生成并保存到 {self.data_path}synthetic_data.csv")
        print(f"数据形状: {df.shape}")
        print(f"目标类别分布: {df['target'].value_counts().to_dict()}")
        
        return X, y
    
    def preprocess_data(self, X, y):
        """数据预处理"""
        print("\n正在进行数据预处理...")
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42, stratify=y
        )
        
        # 标准化特征
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print(f"训练集形状: {X_train_scaled.shape}")
        print(f"测试集形状: {X_test_scaled.shape}")
        
        return X_train_scaled, X_test_scaled, y_train, y_test
    
    def train_random_forest(self, X_train, y_train, X_test, y_test):
        """训练随机森林分类器"""
        print("\n正在训练随机森林分类器...")
        
        model = RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        self.models['random_forest'] = model
        self.results['random_forest'] = {
            'accuracy': accuracy,
            'predictions': y_pred,
            'model': model
        }
        
        print(f"随机森林准确率: {accuracy:.4f}")
        return accuracy
    
    def train_logistic_regression(self, X_train, y_train, X_test, y_test):
        """训练逻辑回归分类器"""
        print("\n正在训练逻辑回归分类器...")
        
        model = LogisticRegression(
            random_state=42,
            max_iter=1000,
            multi_class='multinomial'
        )
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        self.models['logistic_regression'] = model
        self.results['logistic_regression'] = {
            'accuracy': accuracy,
            'predictions': y_pred,
            'model': model
        }
        
        print(f"逻辑回归准确率: {accuracy:.4f}")
        return accuracy
    
    def train_svm(self, X_train, y_train, X_test, y_test):
        """训练支持向量机分类器"""
        print("\n正在训练支持向量机分类器...")
        
        model = SVC(
            kernel='rbf',
            random_state=42,
            probability=True
        )
        
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        self.models['svm'] = model
        self.results['svm'] = {
            'accuracy': accuracy,
            'predictions': y_pred,
            'model': model
        }
        
        print(f"支持向量机准确率: {accuracy:.4f}")
        return accuracy
    
    def train_neural_network(self, X_train, y_train, X_test, y_test):
        """训练神经网络分类器"""
        print("\n正在训练神经网络分类器...")
        
        # 获取类别数量
        n_classes = len(np.unique(y_train))
        
        # 构建模型
        model = Sequential([
            Dense(128, activation='relu', input_shape=(X_train.shape[1],)),
            Dropout(0.3),
            Dense(64, activation='relu'),
            Dropout(0.3),
            Dense(32, activation='relu'),
            Dense(n_classes, activation='softmax')
        ])
        
        # 编译模型
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        # 训练模型
        history = model.fit(
            X_train, y_train,
            epochs=50,
            batch_size=32,
            validation_split=0.2,
            verbose=0
        )
        
        # 预测
        y_pred_prob = model.predict(X_test)
        y_pred = np.argmax(y_pred_prob, axis=1)
        
        accuracy = accuracy_score(y_test, y_pred)
        self.models['neural_network'] = model
        self.results['neural_network'] = {
            'accuracy': accuracy,
            'predictions': y_pred,
            'model': model,
            'history': history
        }
        
        print(f"神经网络准确率: {accuracy:.4f}")
        return accuracy
    
    def evaluate_models(self):
        """评估所有模型"""
        print("\n" + "="*50)
        print("模型评估结果")
        print("="*50)
        
        for model_name, result in self.results.items():
            print(f"\n{model_name.upper()}:")
            print(f"准确率: {result['accuracy']:.4f}")
            
            # 打印分类报告
            if 'y_test' in locals():
                print("分类报告:")
                print(classification_report(self.y_test, result['predictions']))
    
    def plot_results(self):
        """绘制结果可视化"""
        print("\n正在生成可视化图表...")
        
        # 准确率对比图
        plt.figure(figsize=(12, 6))
        
        model_names = list(self.results.keys())
        accuracies = [self.results[name]['accuracy'] for name in model_names]
        
        bars = plt.bar(model_names, accuracies, color=['skyblue', 'lightcoral', 'lightgreen', 'gold'])
        plt.title('模型准确率对比', fontsize=16, fontweight='bold')
        plt.xlabel('模型', fontsize=12)
        plt.ylabel('准确率', fontsize=12)
        plt.ylim(0, 1)
        
        # 在柱子上显示数值
        for bar, acc in zip(bars, accuracies):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                    f'{acc:.3f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.models_path, 'accuracy_comparison.png'), dpi=300, bbox_inches='tight')
        plt.show()
        
        # 混淆矩阵图（使用最佳模型）
        best_model_name = max(self.results.keys(), key=lambda x: self.results[x]['accuracy'])
        best_result = self.results[best_model_name]
        
        if hasattr(best_result['model'], 'predict'):
            cm = confusion_matrix(self.y_test, best_result['predictions'])
            
            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                       xticklabels=['类别0', '类别1', '类别2'],
                       yticklabels=['类别0', '类别1', '类别2'])
            plt.title(f'{best_model_name} 混淆矩阵', fontsize=16, fontweight='bold')
            plt.xlabel('预测标签', fontsize=12)
            plt.ylabel('真实标签', fontsize=12)
            plt.tight_layout()
            plt.savefig(os.path.join(self.models_path, 'confusion_matrix.png'), dpi=300, bbox_inches='tight')
            plt.show()
    
    def save_models(self):
        """保存训练好的模型"""
        print(f"\n正在保存模型到 {self.models_path}")
        
        os.makedirs(self.models_path, exist_ok=True)
        
        # 保存传统机器学习模型
        for name, model in self.models.items():
            if name != 'neural_network':  # 神经网络单独保存
                joblib.dump(model, os.path.join(self.models_path, f'{name}.pkl'))
        
        # 保存神经网络
        if 'neural_network' in self.models:
            self.models['neural_network'].save(os.path.join(self.models_path, 'neural_network.h5'))
        
        # 保存scaler
        joblib.dump(self.scaler, os.path.join(self.models_path, 'scaler.pkl'))
        
        print("模型保存完成！")
    
    def run(self):
        """运行完整的分类项目"""
        print("开始机器学习分类项目...")
        print("="*50)
        
        # 1. 加载数据
        X, y = self.load_data()
        
        # 2. 数据预处理
        X_train, X_test, y_train, y_test = self.preprocess_data(X, y)
        self.y_test = y_test  # 保存用于后续评估
        
        # 3. 训练多个模型
        self.train_random_forest(X_train, y_train, X_test, y_test)
        self.train_logistic_regression(X_train, y_train, X_test, y_test)
        self.train_svm(X_train, y_train, X_test, y_test)
        self.train_neural_network(X_train, y_train, X_test, y_test)
        
        # 4. 评估模型
        self.evaluate_models()
        
        # 5. 可视化结果
        self.plot_results()
        
        # 6. 保存模型
        self.save_models()
        
        print("\n" + "="*50)
        print("项目运行完成！")
        print("="*50)
        
        # 打印最佳模型
        best_model = max(self.results.keys(), key=lambda x: self.results[x]['accuracy'])
        print(f"最佳模型: {best_model}")
        print(f"最佳准确率: {self.results[best_model]['accuracy']:.4f}")

if __name__ == "__main__":
    project = ClassificationProject()
    project.run()