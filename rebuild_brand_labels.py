#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新构建 brand_labels.csv：
1. 保留现有标注（去除重复，优先保留非"其他"的标注）
2. 将 images/ 下所有未标注图片初始标记为"其他"
"""
import os
import csv
from datetime import datetime

# 读取现有标注
existing = {}
if os.path.exists('brand_labels.csv'):
    with open('brand_labels.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            path = row['image_path']
            brand = row['brand']
            # 去重：如果同一图片有多个标注，保留非"其他"的
            if path not in existing or existing[path] == '其他':
                existing[path] = brand

print(f"现有标注: {len(existing)} 条")

# 收集 images/ 下所有图片
all_images = []
for root, dirs, files in os.walk('images'):
    for f in files:
        if f.lower().endswith('.jpg'):
            path = os.path.join(root, f).replace('\\', '/')
            all_images.append(path)

print(f"images/ 下总图片: {len(all_images)} 张")

# 合并：已有标注保留，新图片标记为"其他"
rows = []
for path in sorted(all_images):
    brand = existing.get(path, '其他')
    rows.append({
        'image_path': path,
        'brand': brand,
        'timestamp': datetime.now().isoformat()
    })

# 统计
other_count = sum(1 for r in rows if r['brand'] == '其他')
print(f"重建后总样本: {len(rows)}")
print(f"其中'其他': {other_count} ({other_count/len(rows)*100:.1f}%)")

# 写入
with open('brand_labels.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['image_path', 'brand', 'timestamp'])
    writer.writeheader()
    writer.writerows(rows)

print("brand_labels.csv 重建完成!")
