#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
过滤后训练品牌分类模型：只用样本数>=3的非"其他"品牌
"""
import os
import csv
import cv2
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
from torchvision import models
import numpy as np
from PIL import Image
import random
from collections import Counter

random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"使用设备: {DEVICE}")

def load_labels():
    """加载标注数据，过滤掉样本数<3的品牌和'其他'"""
    all_labels = []
    with open('brand_labels.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            all_labels.append((row['image_path'], row['brand']))
    
    # 统计每个品牌的样本数
    brand_counts = Counter(brand for _, brand in all_labels)
    
    # 只保留样本数>=3且不是"其他"的品牌
    valid_brands = {b for b, c in brand_counts.items() if c >= 3 and b != '其他'}
    filtered = [(p, b) for p, b in all_labels if b in valid_brands]
    
    print(f"原始样本: {len(all_labels)}, 过滤后: {len(filtered)}")
    print(f"有效品牌({len(valid_brands)}个): {sorted(valid_brands)}")
    
    return filtered, sorted(valid_brands)


class BrandDataset(Dataset):
    """品牌数据集，带数据增强"""
    def __init__(self, data_list, transform=None):
        self.data = data_list
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        path, brand = self.data[idx]
        img = cv2.imread(path)
        if img is None:
            img = np.zeros((224, 224, 3), dtype=np.uint8)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)

        if self.transform:
            img = self.transform(img)

        label = BRAND_TO_ID.get(brand, 0)
        return img, label


def get_transforms():
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    return train_transform, val_transform


def train_model():
    labels, BRANDS = load_labels()
    global BRAND_TO_ID, NUM_CLASSES
    BRAND_TO_ID = {brand: i for i, brand in enumerate(BRANDS)}
    NUM_CLASSES = len(BRANDS)
    
    print(f"品牌类别数: {NUM_CLASSES}")

    # 划分训练集和验证集（80/20）
    random.shuffle(labels)
    split = int(len(labels) * 0.8)
    train_data = labels[:split]
    val_data = labels[split:]

    print(f"训练集: {len(train_data)}, 验证集: {len(val_data)}")

    train_transform, val_transform = get_transforms()

    train_dataset = BrandDataset(train_data, transform=train_transform)
    val_dataset = BrandDataset(val_data, transform=val_transform)

    train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=8, shuffle=False)

    # 使用预训练的ResNet18
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)
    model = model.to(DEVICE)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.0001)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

    best_acc = 0.0
    num_epochs = 50

    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0

        for images, labels_batch in train_loader:
            images = images.to(DEVICE)
            labels_batch = labels_batch.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels_batch)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            _, predicted = torch.max(outputs, 1)
            train_total += labels_batch.size(0)
            train_correct += (predicted == labels_batch).sum().item()

        train_acc = 100 * train_correct / train_total

        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0

        with torch.no_grad():
            for images, labels_batch in val_loader:
                images = images.to(DEVICE)
                labels_batch = labels_batch.to(DEVICE)

                outputs = model(images)
                loss = criterion(outputs, labels_batch)

                val_loss += loss.item()
                _, predicted = torch.max(outputs, 1)
                val_total += labels_batch.size(0)
                val_correct += (predicted == labels_batch).sum().item()

        val_acc = 100 * val_correct / val_total if val_total > 0 else 0

        scheduler.step()

        if val_acc > best_acc:
            best_acc = val_acc
            torch.save(model.state_dict(), 'cfg/vehicle_brand_resnet18_filtered.pth')

        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{num_epochs}: Train Acc={train_acc:.1f}%, Val Acc={val_acc:.1f}%")

    print(f"\n训练完成！最佳验证准确率: {best_acc:.1f}%")
    print("模型已保存: cfg/vehicle_brand_resnet18_filtered.pth")

    # 保存品牌映射
    import json
    with open('cfg/brand_id_map_filtered.json', 'w', encoding='utf-8') as f:
        json.dump(BRANDS, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    train_model()
