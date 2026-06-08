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
    'images/car/19.jpg': '大众',
    'images/bus/3066.jpg': '一汽',
    'images/bus/2965.jpg': '舒驰',
    'images/silver/3491.jpg': '长安',
    'images/yellow/30.jpg': '长安',
    'images/white/151.jpg': '金杯',
    'images/white/781.jpg': '马自达',
    'images/blue/315.jpg': '五菱',
    'images/yellow/Rotation_0.jpg': '江铃',
    'images/car/342.jpg': '大众',
    'images/minibus/171.jpg': '长安',
    'images/blue/774.jpg': '铃木',
    'images/blue/1767.jpg': '大众',
    'images/white/137.jpg': '五菱',
    'images/white/1.jpg': '东风',
    'images/car/4.jpg': '别克',
    'images/yellow/Rotation_9.jpg': '长安',
    'images/blue/2006.jpg': '江淮',
    'images/black/207.jpg': '现代',
    'images/white/910.jpg': '宝马',
    'images/silver/422.jpg': '日产',
    'images/car/3.jpg': '长城',
    'images/silver/1349.jpg': '五菱',
    'images/yellow/Shift_2.jpg': '日产',
    'images/car/224.jpg': '丰田',
    'images/minibus/1570.jpg': '哈飞',
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
