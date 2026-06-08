import csv

fixes = {
    'images/bus/3779.jpg': '其他',
    'images/black/739.jpg': '比亚迪',
    'images/black/37.jpg': '丰田',
    'images/red/212.jpg': '其他',
    'images/red/293.jpg': '福特',
    'images/brown/682.jpg': '大众',
    'images/car/210.jpg': '大众',
    'images/white/140.jpg': '起亚',
    'images/red/187.jpg': '其他',
    'images/bus/2737.jpg': '其他',
    'images/truck/1066.jpg': '江淮',
    'images/bus/2669.jpg': '其他',
    'images/red/568.jpg': '起亚',
    'images/truck/1078.jpg': '江淮',
    'images/minibus/1580.jpg': '长安',
    'images/bus/2901.jpg': '其他',
    'images/white/689.jpg': '长安',
    'images/silver/870.jpg': '现代',
    'images/bus/3214.jpg': '其他',
    'images/brown/879.jpg': '日产',
    'images/silver/674.jpg': '海马',
    'images/minibus/1388.jpg': '五菱',
    'images/truck/1339.jpg': '东风',
    'images/white/267.jpg': '东风',
    'images/black/616.jpg': '比亚迪',
    'images/silver/3831.jpg': '别克',
    'images/silver/3435.jpg': '长安',
    'images/brown/2754.jpg': '日产',
    'images/white/277.jpg': '标致',
    'images/green/577.jpg': '大众',
    'images/white/596.jpg': '雪佛兰',
    'images/yellow/Flip_Vec_6.jpg': '大众',
    'images/brown/3184.jpg': '现代',
    'images/silver/3601.jpg': '长城',
    'images/truck/1354.jpg': '一汽',
    'images/blue/292.jpg': '金杯',
    'images/truck/1650.jpg': '其他',
    'images/blue/1274.jpg': '大众',
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
