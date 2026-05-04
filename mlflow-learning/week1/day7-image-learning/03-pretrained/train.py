import os
import mlflow
import mlflow.pytorch

os.makedirs("../../../mlruns", exist_ok=True)
mlflow.set_tracking_uri("file:///D:/code_workspaces/mlflow-learning/mlruns")

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from sklearn.metrics import accuracy_score

mlflow.set_experiment("pretrained-resnet")

print("="*50)
print("使用预训练 ResNet18 进行图像分类")
print("="*50)

# 使用 MNIST 数据集，模拟迁移学习
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

# 为 MNIST 创建伪 RGB 数据
class MNISTRGB(datasets.MNIST):
    def __getitem__(self, index):
        img, target = super().__getitem__(index)
        img = img.repeat(3, 1, 1)  # 转为 3 通道
        return img, target

train_data = MNISTRGB(root='../../../data/raw', train=True, download=True, transform=transform)
test_data = MNISTRGB(root='../../../data/raw', train=False, download=True, transform=transform)

train_loader = DataLoader(train_data, batch_size=32, shuffle=True, num_workers=2)
test_loader = DataLoader(test_data, batch_size=32, shuffle=False, num_workers=2)

print(f"训练集: {len(train_data)} 张图片")
print(f"测试集: {len(test_data)} 张图片")

# 使用预训练 ResNet18
model = models.resnet18(pretrained=True)

# 修改最后的全连接层，输出 10 类
model.fc = nn.Linear(model.fc.in_features, 10)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

print("\n" + "="*50)
print("开始训练 (迁移学习)...")
print("="*50)

epochs = 2

with mlflow.start_run(run_name="resnet18-transfer"):
    mlflow.log_param("model", "ResNet18-pretrained")
    mlflow.log_param("epochs", epochs)
    mlflow.log_param("batch_size", 32)
    mlflow.log_param("task", "transfer-learning")

    for epoch in range(epochs):
        model.train()
        total_loss = 0

        for batch_idx, (data, target) in enumerate(train_loader):
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

            if batch_idx % 100 == 0:
                print(f"Epoch {epoch+1}/{epochs} [{batch_idx}/{len(train_loader)}] Loss: {loss.item():.4f}")

        avg_loss = total_loss / len(train_loader)

        # 测试
        model.eval()
        all_preds = []
        all_targets = []

        with torch.no_grad():
            for data, target in test_loader:
                output = model(data)
                pred = output.argmax(dim=1)
                all_preds.extend(pred.numpy())
                all_targets.extend(target.numpy())

        accuracy = accuracy_score(all_targets, all_preds)

        mlflow.log_metric("train_loss", avg_loss, step=epoch)
        mlflow.log_metric("test_accuracy", accuracy, step=epoch)

        print(f"Epoch {epoch+1}: Loss={avg_loss:.4f}, Accuracy={accuracy:.4f}")

    mlflow.pytorch.log_model(model, "model")

print("\n" + "="*50)
print("训练完成!")
print("="*50)