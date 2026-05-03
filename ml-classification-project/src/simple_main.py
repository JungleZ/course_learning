"""
简化的机器学习分类项目 - 使用现有库
这个版本使用已有的scikit-learn库，避免TensorFlow安装问题
"""

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
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

print("简化版机器学习分类项目")
print("="*50)

class SimpleClassificationProject:
    def __init__(self):
        self.data_path = '../data/'
        self.models_path = '../models/'
        self.scaler = StandardScaler()
        self.models = {}
        self.results = {}
        
    def load_data(self):
        """加载示例数据集"""
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
    
    def train_models(self, X_train, y_train, X_test, y_test):
        """训练多个模型"""
        print("\n正在训练模型...")
        
        # 1. 随机森林
        print("\n1. 训练随机森林...")
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        rf_model.fit(X_train, y_train)
        rf_pred = rf_model.predict(X_test)
        rf_accuracy = accuracy_score(y_test, rf_pred)
        
        self.models['random_forest'] = rf_model
        self.results['random_forest'] = {
            'accuracy': rf_accuracy,
            'predictions': rf_pred,
            'model': rf_model
        }
        print(f"随机森林准确率: {rf_accuracy:.4f}")
        
        # 2. 逻辑回归
        print("\n2. 训练逻辑回归...")
        # 使用旧版本scikit-learn支持的参数
        lr_model = LogisticRegression(random_state=42, max_iter=1000, multi_class='ovr')
        lr_model.fit(X_train, y_train)
        lr_pred = lr_model.predict(X_test)
        lr_accuracy = accuracy_score(y_test, lr_pred)
        
        self.models['logistic_regression'] = lr_model
        self.results['logistic_regression'] = {
            'accuracy': lr_accuracy,
            'predictions': lr_pred,
            'model': lr_model
        }
        print(f"逻辑回归准确率: {lr_accuracy:.4f}")
        
        # 3. 支持向量机
        print("\n3. 训练支持向量机...")
        svm_model = SVC(kernel='rbf', random_state=42, probability=True)
        svm_model.fit(X_train, y_train)
        svm_pred = svm_model.predict(X_test)
        svm_accuracy = accuracy_score(y_test, svm_pred)
        
        self.models['svm'] = svm_model
        self.results['svm'] = {
            'accuracy': svm_accuracy,
            'predictions': svm_pred,
            'model': svm_model
        }
        print(f"支持向量机准确率: {svm_accuracy:.4f}")
        
        return X_test, y_test
    
    def evaluate_models(self, y_test):
        """评估所有模型"""
        print("\n" + "="*50)
        print("模型评估结果")
        print("="*50)
        
        for model_name, result in self.results.items():
            print(f"\n{model_name.upper()}:")
            print(f"准确率: {result['accuracy']:.4f}")
            
            # 打印分类报告
            print("分类报告:")
            print(classification_report(y_test, result['predictions']))
    
    def plot_results(self, y_test):
        """绘制结果可视化"""
        print("\n正在生成可视化图表...")
        
        # 确保目录存在
        os.makedirs(self.models_path, exist_ok=True)
        
        # 准确率对比图
        plt.figure(figsize=(12, 6))
        
        model_names = list(self.results.keys())
        accuracies = [self.results[name]['accuracy'] for name in model_names]
        
        bars = plt.bar(model_names, accuracies, color=['skyblue', 'lightcoral', 'lightgreen'])
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
        
        cm = confusion_matrix(y_test, best_result['predictions'])
        
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
        
        # 特征重要性 - 随机森林
        if 'random_forest' in self.models:
            plt.figure(figsize=(10, 6))
            feature_importance = self.models['random_forest'].feature_importances_
            indices = np.argsort(feature_importance)[-10:]
            
            plt.barh(range(len(indices)), feature_importance[indices])
            plt.yticks(range(len(indices)), [f'feature_{i}' for i in indices])
            plt.title('随机森林 - 前10个重要特征', fontsize=16, fontweight='bold')
            plt.xlabel('重要性分数', fontsize=12)
            plt.tight_layout()
            plt.savefig(os.path.join(self.models_path, 'feature_importance.png'), dpi=300, bbox_inches='tight')
            plt.show()
    
    def save_models(self):
        """保存训练好的模型"""
        print(f"\n正在保存模型到 {self.models_path}")
        
        os.makedirs(self.models_path, exist_ok=True)
        
        # 保存所有模型
        for name, model in self.models.items():
            joblib.dump(model, os.path.join(self.models_path, f'{name}.pkl'))
        
        # 保存scaler
        joblib.dump(self.scaler, os.path.join(self.models_path, 'scaler.pkl'))
        
        print("模型保存完成！")
    
    def predict_new_data(self, X_test):
        """对新数据进行预测"""
        print("\n对新数据进行预测...")
        
        # 预处理新数据
        X_new_scaled = self.scaler.transform(X_test)
        
        print("使用不同模型对新数据进行预测:")
        
        for model_name, model in self.models.items():
            pred = model.predict(X_new_scaled)
            confidence = model.predict_proba(X_new_scaled)
            confidence = np.max(confidence, axis=1)
            
            print(f"\n{model_name}预测结果:")
            for i, (p, c) in enumerate(zip(pred, confidence)):
                print(f"  样本{i+1}: 预测类别={p}, 置信度={c:.3f}")
    
    def run(self):
        """运行完整的分类项目"""
        print("开始简化版机器学习分类项目...")
        print("="*50)
        
        # 1. 加载数据
        X, y = self.load_data()
        
        # 2. 数据预处理
        X_train, X_test, y_train, y_test = self.preprocess_data(X, y)
        
        # 3. 训练多个模型
        X_test_processed, y_test = self.train_models(X_train, y_train, X_test, y_test)
        
        # 4. 评估模型
        self.evaluate_models(y_test)
        
        # 5. 可视化结果
        self.plot_results(y_test)
        
        # 6. 保存模型
        self.save_models()
        
        # 7. 新数据预测
        self.predict_new_data(X_test[:5])  # 使用前5个样本
        
        print("\n" + "="*50)
        print("项目运行完成！")
        print("="*50)
        
        # 打印最佳模型
        best_model = max(self.results.keys(), key=lambda x: self.results[x]['accuracy'])
        print(f"最佳模型: {best_model}")
        print(f"最佳准确率: {self.results[best_model]['accuracy']:.4f}")

if __name__ == "__main__":
    project = SimpleClassificationProject()
    project.run()