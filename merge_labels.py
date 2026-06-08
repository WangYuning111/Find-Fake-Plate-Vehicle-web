#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
from datetime import datetime

# 读取自动标注
auto = {}
with open('brand_labels_auto.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        auto[row['image_path']] = row['brand']

# 读取人工标注（优先）
manual = {}
with open('brand_labels.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        manual[row['image_path']] = row['brand']

# 合并：人工标注覆盖自动标注
merged = dict(auto)
merged.update(manual)

# 保存
now = datetime.now().isoformat()
with open('brand_labels.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['image_path', 'brand', 'timestamp'])
    for path, brand in sorted(merged.items()):
        writer.writerow([path, brand, now])

print(f"合并完成: 自动标注 {len(auto)} 条, 人工覆盖 {len(manual)} 条, 总计 {len(merged)} 条")

# 统计
from collections import Counter
c = Counter(merged.values())
print("\n品牌分布:")
for k, v in c.most_common():
    print(f"  {k}: {v}")
