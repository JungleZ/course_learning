import os
import mlflow
import mlflow.pytorch

os.makedirs("../../../mlruns", exist_ok=True)
mlflow.set_tracking_uri("file:///D:/code_workspaces/mlflow-learning/mlruns")

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from sklearn.metrics import accuracy_score, classification_report

mlflow.set_experiment("cifar10-classification")

print("="*50)
print("CIFAR-10 图像分类 (10类彩色图片)")
print("="*50)

classes = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

# 数据预处理
transform_train = transforms.Compose([
    transforms.RandomCrop(32, padding=4),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
])

transform_test = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010))
])

# 加载数据
train_data = datasets.CIFAR10(root='../../../data/raw', train=True, download=True, transform=transform_train)
test_data = datasets.CIFAR10(root='../../../data/raw', train=False, download=True, transform=transform_test)

train_loader = DataLoader(train_data, batch_size=64, shuffle=True, num_workers=2)
test_loader = DataLoader(test_data, batch_size=1000, shuffle=False, num_workers=2)

print(f"训练集: {len(train_data)} 张图片")
print(f"测试集: {len(test_data)} 张图片")
print(f"类别: {classes}")

# 定义模型
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(128 * 4 * 4, 256)
        self.fc2 = nn.Linear(256, 10)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = self.pool(torch.relu(self.conv3(x)))
        x = x.view(-1, 128 * 4 * 4)
        x = self.dropout(torch.relu(self.fc1(x)))
        x = self.fc2(x)
        return x

model = SimpleCNN()
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

print("\n" + "="*50)
print("开始训练...")
print("="*50)

epochs = 3

with mlflow.start_run(run_name="cnn-cifar10"):
    mlflow.log_param("model", "SimpleCNN")
    mlflow.log_param("epochs", epochs)
    mlflow.log_param("batch_size", 64)
    mlflow.log_param("optimizer", "Adam")

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