import csv
import os

csv_file = 'brand_labels.csv'

# 读取所有行
with open(csv_file, 'r', encoding='utf-8', newline='') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    fieldnames = reader.fieldnames

# 需要修正的映射：image_path -> brand
fixes = {
    'images/brown/1604.jpg': '长安',
    'images/black/765.jpg': '本田',
    'images/blue/138.jpg': '大众',
    'images/blue/1451.jpg': '大众',
    'images/bus/3778.jpg': '一汽',
    'images/red/1251.jpg': '一汽',
    'images/minibus/1134.jpg': '五菱',
    'images/yellow/Shift_15.jpg': '奇瑞',
    'images/silver/3433.jpg': '五菱',
    'images/bus/729.jpg': '舒驰',
    'images/yellow/Rotation_7.jpg': '日产',
    'images/brown/110.jpg': '长安',
    'images/truck/1.jpg': '东风',
    'images/red/124.jpg': '雪佛兰',
    'images/brown/984.jpg': '日产',
    'images/green/381.jpg': '大众',
    'images/car/25.jpg': '雪佛兰',
    'images/car/6.jpg': '奇瑞',
    'images/black/591.jpg': '现代',
    'images/yellow/3210.jpg': '长安',
    'images/car/60.jpg': '奔驰',
    'images/black/61.jpg': '现代',
    'images/car/428.jpg': '铃木',
    'images/silver/2026.jpg': '雪铁龙',
    'images/minibus/1335.jpg': '长安',
    'images/red/24.jpg': '福特',
}

changed = 0
for row in rows:
    path = row['image_path']
    if path in fixes and row['brand'] == '其他':
        row['brand'] = fixes[path]
        changed += 1
        print(f'修正: {path} -> {fixes[path]}')

with open(csv_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f'\n共修正 {changed} 张图片')
