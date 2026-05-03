import mlflow
import torch
import numpy as np
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

mlflow.set_experiment("bert-pretraining")

device = torch.device("cpu")
vocab_size = 10000
max_len = 128
batch_size = 16
hidden_size = 256
num_layers = 2
num_heads = 4

class BERTModel(nn.Module):
    def __init__(self, vocab_size, hidden_size, num_layers, num_heads, max_len):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        self.position_embedding = nn.Embedding(max_len, hidden_size)
        encoder_layer = nn.TransformerEncoderLayer(d_model=hidden_size, nhead=num_heads, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(hidden_size, vocab_size)
        
    def forward(self, x):
        seq_len = x.size(1)
        positions = torch.arange(seq_len, device=x.device).unsqueeze(0).expand_as(x)
        x = self.embedding(x) + self.position_embedding(positions)
        x = self.transformer(x)
        return self.fc(x)

np.random.seed(42)
torch.manual_seed(42)

n_samples = 200
input_ids = torch.randint(0, vocab_size, (n_samples, max_len))
attention_mask = torch.ones_like(input_ids)

dataset = TensorDataset(input_ids, attention_mask)
dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

model = BERTModel(vocab_size, hidden_size, num_layers, num_heads, max_len).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

with mlflow.start_run():
    mlflow.log_param("vocab_size", vocab_size)
    mlflow.log_param("hidden_size", hidden_size)
    mlflow.log_param("num_layers", num_layers)
    mlflow.log_param("num_heads", num_heads)
    mlflow.log_param("max_len", max_len)
    mlflow.log_param("batch_size", batch_size)
    mlflow.log_param("epochs", 3)
    
    total_loss = 0
    model.train()
    for epoch in range(3):
        epoch_loss = 0
        for batch_ids, batch_mask in dataloader:
            batch_ids = batch_ids.to(device)
            attention_mask = batch_mask.to(device)
            
            optimizer.zero_grad()
            outputs = model(batch_ids)
            loss = criterion(outputs.view(-1, vocab_size), batch_ids.view(-1))
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        
        avg_loss = epoch_loss / len(dataloader)
        total_loss += avg_loss
        mlflow.log_metric("epoch_loss", avg_loss, step=epoch)
        print(f"Epoch {epoch+1}/3 - Loss: {avg_loss:.4f}")
    
    avg_total_loss = total_loss / 3
    mlflow.log_metric("avg_loss", avg_total_loss)
    
    torch.save(model.state_dict(), "D:/code_workspaces/bert_model.pt")
    mlflow.log_artifact("D:/code_workspaces/bert_model.pt")
    
    print(f"BERT Pre-training - Avg Loss: {avg_total_loss:.4f}")