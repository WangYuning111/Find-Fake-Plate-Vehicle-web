import csv

fixes = {
    'images/white/270.jpg': '别克',
    'images/truck/1363.jpg': '一汽',
    'images/silver/936.jpg': '丰田',
    'images/yellow/Flip_Vec_14.jpg': '大众',
    'images/car/405.jpg': '大众',
    'images/black/63.jpg': '大众',
    'images/yellow/Rotation_10.jpg': '长安',
    'images/yellow/3777.jpg': '大众',
    'images/green/520.jpg': '大众',
    'images/green/297.jpg': '大众',
    'images/white/8.jpg': '长安',
    'images/white/707.jpg': '起亚',
    'images/white/278.jpg': '别克',
    'images/minibus/1569.jpg': '五菱',
    'images/blue/494.jpg': '大众',
    'images/car/401.jpg': '日产',
    'images/blue/1436.jpg': '大众',
    'images/car/259.jpg': '丰田',
    'images/green/1926.jpg': '大众',
    'images/black/394.jpg': '奇瑞',
    'images/black/238.jpg': '现代',
    'images/yellow/Flip_Hor_14.jpg': '大众',
    'images/silver/184.jpg': '日产',
    'images/blue/229.jpg': '一汽',
    'images/silver/450.jpg': '长安',
    'images/white/341.jpg': '东风',
}

rows = []
with open('brand_labels.csv', 'r', encoding='utf-8', newline='') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        path = row['image_path']
        if path in fixes and row['brand'] == '其他':
            row['brand'] = fixes[path]
            print(f'修正: {path} -> {fixes[path]}')
        rows.append(row)

with open('brand_labels.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print('完成！')
