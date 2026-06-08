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
    'images/car/334.jpg': '大众',
    'images/green/210.jpg': '大众',
    'images/red/585.jpg': '江淮',
    'images/red/1170.jpg': '现代',
    'images/black/742.jpg': '大众',
    'images/silver/378.jpg': '五菱',
    'images/silver/377.jpg': '标致',
    'images/brown/2803.jpg': '奥迪',
    'images/minibus/973.jpg': '五菱',
    'images/brown/1163.jpg': '大众',
    'images/car/326.jpg': '大众',
    'images/silver/3708.jpg': '长安',
    'images/truck/190.jpg': '福田',
    'images/black/172.jpg': '一汽',
    'images/yellow/Flip_Hor_9.jpg': '长安',
    'images/brown/1855.jpg': '日产',
    'images/minibus/1079.jpg': '哈飞',
    'images/white/713.jpg': '比亚迪',
    'images/truck/1940.jpg': '一汽',
    'images/truck/370.jpg': '福田',
    'images/truck/1520.jpg': '东风',
    'images/black/741.jpg': '现代',
    'images/truck/1324.jpg': '一汽',
    'images/green/302.jpg': '大众',
    'images/blue/749.jpg': '大众',
    'images/truck/1036.jpg': '东风',
    'images/yellow/Flip_Hor_2.jpg': '日产',
    'images/yellow/Shift_14.jpg': '大众',
    'images/brown/678.jpg': '现代',
    'images/white/605.jpg': '大众',
    'images/black/48.jpg': '别克',
    'images/white/706.jpg': '长安',
    'images/bus/2535.jpg': '舒驰',
    'images/minibus/892.jpg': '五菱',
    'images/brown/3450.jpg': '标致',
    'images/brown/970.jpg': '长安',
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
