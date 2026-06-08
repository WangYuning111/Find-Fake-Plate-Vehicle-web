#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于过滤后的品牌标注数据训练品牌分类模型
只使用非"其他"的标注数据进行训练
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

random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"使用设备: {DEVICE}")

# 标准品牌列表
BRANDS = [
    '大众', '别克', '福特', '东风', '长安', '日产', '现代', '一汽', '江淮', '金杯',
    '福田', '江铃', '哈飞', '雪铁龙', '中华', '雪佛兰', '奥迪', '长城', '标致',
    '马自达', '铃木', '五菱', '海马', '宝马', '荣威', '比亚迪', '奇瑞', '本田', '丰田', '起亚', '奔驰', '舒驰', '其他'
]
BRAND_TO_ID = {brand: i for i, brand in enumerate(BRANDS)}
NUM_CLASSES = len(BRANDS)


def load_labels():
    """加载标注数据，过滤掉'其他'"""
    labels = []
    with open('brand_labels.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['brand'] != '其他':
                labels.append((row['image_path'], row['brand']))
    return labels


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

        label = BRAND_TO_ID.get(brand, BRAND_TO_ID['其他'])
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
    labels = load_labels()
    print(f"加载了 {len(labels)} 条非'其他'标注数据")

    # 统计每个品牌的样本数
    brand_counts = {}
    for _, brand in labels:
        brand_counts[brand] = brand_counts.get(brand, 0) + 1
    print("品牌分布:", brand_counts)

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

    # 计算类别权重，处理类别不均衡
    total = sum(brand_counts.values())
    class_weights = torch.ones(NUM_CLASSES).to(DEVICE)
    for brand, count in brand_counts.items():
        idx = BRAND_TO_ID[brand]
        # 样本越少，权重越高
        class_weights[idx] = total / (len(brand_counts) * count)
    
    print("类别权重:", {BRANDS[i]: round(class_weights[i].item(), 2) for i in range(NUM_CLASSES) if class_weights[i] != 1.0})
    
    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.Adam(model.parameters(), lr=0.0001)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)

    best_acc = 0.0
    num_epochs = 50

    for epoch in range(num_epochs):
        # 训练
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

        # 验证
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
            torch.save(model.state_dict(), 'cfg/vehicle_brand_resnet18.pth')

        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{num_epochs}: Train Acc={train_acc:.1f}%, Val Acc={val_acc:.1f}%")

    print(f"\n训练完成！最佳验证准确率: {best_acc:.1f}%")
    print("模型已保存: cfg/vehicle_brand_resnet18.pth")

    # 保存品牌映射
    import json
    with open('cfg/brand_id_map.json', 'w', encoding='utf-8') as f:
        json.dump(BRANDS, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    train_model()
