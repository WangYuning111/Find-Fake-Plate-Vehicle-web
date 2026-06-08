import csv

fixes = {
    'images/bus/3126.jpg': '其他',
    'images/black/32.jpg': '大众',
    'images/car/164.jpg': '丰田',
    'images/yellow/Rotation_6.jpg': '大众',
    'images/green/636.jpg': '大众',
    'images/yellow/3372.jpg': '金杯',
    'images/truck/1280.jpg': '东风',
    'images/white/929.jpg': '荣威',
    'images/car/514.jpg': '福特',
    'images/black/724.jpg': '别克',
    'images/bus/3271.jpg': '其他',
    'images/truck/1758.jpg': '一汽',
    'images/blue/352.jpg': '大众',
    'images/brown/1819.jpg': '日产',
    'images/black/150.jpg': '其他',
    'images/yellow/Flip_Hor_3.jpg': '其他',
    'images/minibus/725.jpg': '五菱',
    'images/red/223.jpg': '丰田',
    'images/car/410.jpg': '丰田',
    'images/truck/1578.jpg': '其他',
    'images/car/7.jpg': '海马',
    'images/black/253.jpg': '大众',
    'images/truck/78.jpg': '金杯',
    'images/yellow/Rotation_12.jpg': '金杯',
    'images/green/2111.jpg': '大众',
    'images/white/174.jpg': '丰田',
    'images/black/402.jpg': '日产',
    'images/yellow/Rotation_15.jpg': '奇瑞',
    'images/silver/251.jpg': '长城',
    'images/red/1082.jpg': '标致',
    'images/minibus/1172.jpg': '长安',
    'images/blue/1041.jpg': '其他',
    'images/minibus/648.jpg': '长安',
    'images/bus/3758.jpg': '其他',
    'images/car/413.jpg': '别克',
    'images/silver/3434.jpg': '江淮',
    'images/brown/858.jpg': '海马',
    'images/truck/3296.jpg': '福田',
    'images/red/385.jpg': '大众',
    'images/bus/2897.jpg': '其他',
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
