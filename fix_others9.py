import csv

fixes = {
    'images/blue/1236.jpg': '江淮',
    'images/bus/2692.jpg': '其他',
    'images/truck/1530.jpg': '一汽',
    'images/minibus/341.jpg': '东风',
    'images/black/989.jpg': '福特',
    'images/black/180.jpg': '现代',
    'images/car/175.jpg': '福特',
    'images/green/2124.jpg': '大众',
    'images/black/430.jpg': '雪佛兰',
    'images/red/323.jpg': '别克',
    'images/silver/3415.jpg': '五菱',
    'images/blue/16.jpg': '现代',
    'images/truck/219.jpg': '江铃',
    'images/bus/3231.jpg': '其他',
    'images/red/380.jpg': '长城',
    'images/brown/953.jpg': '比亚迪',
    'images/yellow/Shift_10.jpg': '长安',
    'images/bus/3562.jpg': '福田',
    'images/brown/3015.jpg': '大众',
    'images/black/933.jpg': '福特',
    'images/blue/1131.jpg': '大众',
    'images/bus/3232.jpg': '其他',
    'images/black/637.jpg': '奥迪',
    'images/car/387.jpg': '本田',
    'images/minibus/340.jpg': '五菱',
    'images/yellow/Shift_7.jpg': '日产',
    'images/white/109.jpg': '比亚迪',
    'images/silver/382.jpg': '长城',
    'images/car/11.jpg': '中华',
    'images/white/348.jpg': '起亚',
    'images/car/349.jpg': '日产',
    'images/minibus/958.jpg': '江淮',
    'images/minibus/1204.jpg': '五菱',
    'images/yellow/Shift_3.jpg': '其他',
    'images/yellow/Flip_Hor_1.jpg': '长安',
    'images/silver/3720.jpg': '长安',
    'images/red/1037.jpg': '别克',
    'images/truck/3350.jpg': '其他',
    'images/white/603.jpg': '雪铁龙',
    'images/brown/3220.jpg': '现代',
    'images/blue/173.jpg': '大众',
    'images/truck/76.jpg': '金杯',
    'images/car/508.jpg': '比亚迪',
    'images/car/337.jpg': '大众',
    'images/bus/3493.jpg': '其他',
    'images/bus/2219.jpg': '其他',
    'images/yellow/Rotation_16.jpg': '其他',
    'images/blue/889.jpg': '长安',
    'images/black/247.jpg': '大众',
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
