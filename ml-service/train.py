import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms, models
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from PIL import Image
import pandas as pd
from collections import Counter
import numpy as np
from model import get_model

# Class labels for HAM10000 dataset
CLASS_LABELS = {
    'akiec': 'Actinic Keratosis/Intraepithelial Carcinoma',
    'bcc': 'Basal Cell Carcinoma',
    'bkl': 'Benign Keratosis-like Lesions',
    'df': 'Dermatofibroma',
    'mel': 'Melanoma',
    'nv': 'Melanocytic Nevus',
    'vasc': 'Vascular Lesions'
}

class HAM10000Dataset(Dataset):
    def __init__(self, metadata_path, image_dirs, class_to_idx, transform=None):
        self.metadata = pd.read_csv(metadata_path)
        self.image_dirs = image_dirs
        self.transform = transform
        self.class_to_idx = class_to_idx
        
        # Map disease labels to indices
        self.metadata['target'] = self.metadata['dx'].map(class_to_idx)
        # Remove any rows where dx is not in class_to_idx
        self.metadata = self.metadata[self.metadata['target'].notna()]

    def __len__(self):
        return len(self.metadata)

    def __getitem__(self, idx):
        img_id = self.metadata.iloc[idx]['image_id']
        label = int(self.metadata.iloc[idx]['target'])
        
        img_path = None
        for img_dir in self.image_dirs:
            path = os.path.join(img_dir, f"{img_id}.jpg")
            if os.path.exists(path):
                img_path = path
                break
                
        if img_path is None:
            # Fallback if image not found (creates a dummy black image)
            image = Image.new('RGB', (224, 224))
        else:
            image = Image.open(img_path).convert("RGB")
            
        if self.transform:
            image = self.transform(image)
            
        return image, label

def create_class_weights(dataset, num_classes):
    """Calculate weights to handle class imbalance"""
    class_counts = Counter(dataset.metadata['target'].values)
    total_samples = len(dataset.metadata)
    
    # Calculate weights (inverse of class frequency)
    weights = []
    for i in range(num_classes):
        if i in class_counts:
            weight = total_samples / (num_classes * class_counts[i])
        else:
            weight = 1.0
        weights.append(weight)
    
    print(f"\nClass Weights for Balancing: {weights}")
    
    # Create sample weights
    sample_weights = [weights[int(label)] for label in dataset.metadata['target'].values]
    return torch.DoubleTensor(sample_weights)

def train_model():
    # Define dataset paths
    data_dir = "../backend/data"
    metadata_path = os.path.join(data_dir, "HAM10000_metadata.csv")
    image_dirs = [
        os.path.join(data_dir, "HAM10000_images_part_1"),
        os.path.join(data_dir, "HAM10000_images_part_2")
    ]
    
    if not os.path.exists(metadata_path):
        print(f"Metadata not found at {metadata_path}. Please download the dataset first.")
        return
    
    # Create class mappings
    class_to_idx = {cls: idx for idx, cls in enumerate(sorted(CLASS_LABELS.keys()))}
    idx_to_class = {v: k for k, v in class_to_idx.items()}
    
    print("\n=== CLASS MAPPING ===")
    for idx, class_name in idx_to_class.items():
        print(f"{idx}: {class_name} -> {CLASS_LABELS[class_name]}")
    
    # Save class indices for inference
    os.makedirs("../backend/model", exist_ok=True)
    with open("../backend/model/class_indices.json", "w") as f:
        json.dump(class_to_idx, f)
    print("\nClass indices saved to ../backend/model/class_indices.json")
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    print("\n=== LOADING DATASET ===")
    dataset = HAM10000Dataset(metadata_path, image_dirs, class_to_idx, transform=transform)
    print(f"Total samples: {len(dataset)}")
    
    # Show class distribution
    print("\n=== CLASS DISTRIBUTION ===")
    class_dist = dataset.metadata['target'].value_counts().sort_index()
    for idx, count in class_dist.items():
        class_name = idx_to_class[idx]
        percentage = (count / len(dataset)) * 100
        print(f"{class_name}: {count} ({percentage:.1f}%)")
    
    # Create weighted sampler to handle class imbalance
    sample_weights = create_class_weights(dataset, len(class_to_idx))
    sampler = WeightedRandomSampler(sample_weights, len(sample_weights), replacement=True)
    dataloader = DataLoader(dataset, batch_size=32, sampler=sampler)
    
    print("\n=== INITIALIZING MODEL ===")
    model = get_model(num_classes=len(class_to_idx))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    model = model.to(device)
    
    # Print model summary
    print("\n=== MODEL SUMMARY ===")
    print(model)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Total parameters: {total_params:,}")
    
    criterion = nn.CrossEntropyLoss(weight=torch.tensor([sample_weights[i] for i in range(len(class_to_idx))], dtype=torch.float32).to(device))
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    epochs = 5
    print(f"\n=== STARTING TRAINING ===")
    print(f"Epochs: {epochs} | Device: {device}")
    
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        for i, (inputs, labels) in enumerate(dataloader):
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item()
            if i % 10 == 9:
                print(f"[Epoch {epoch + 1}/{epochs}, Batch {i + 1}] Loss: {running_loss / 10:.4f}")
                running_loss = 0.0
    
    print("\n=== TRAINING FINISHED ===")
    print("Saving model...")
    torch.save(model.state_dict(), "model.pth")
    print("Model saved to model.pth")

if __name__ == "__main__":
    train_model()
