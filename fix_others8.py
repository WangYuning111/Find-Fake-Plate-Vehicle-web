import csv

fixes = {
    'images/bus/3172.jpg': '其他',
    'images/yellow/Flip_Hor_11.jpg': '福田',
    'images/blue/227.jpg': '大众',
    'images/brown/817.jpg': '日产',
    'images/black/216.jpg': '奥迪',
    'images/brown/3325.jpg': '长安',
    'images/car/389.jpg': '海马',
    'images/red/133.jpg': '福田',
    'images/brown/797.jpg': '起亚',
    'images/minibus/837.jpg': '铃木',
    'images/silver/3642.jpg': '五菱',
    'images/black/289.jpg': '别克',
    'images/silver/3428.jpg': '五菱',
    'images/white/721.jpg': '大众',
    'images/green/1239.jpg': '大众',
    'images/blue/938.jpg': '大众',
    'images/minibus/857.jpg': '一汽',
    'images/truck/2220.jpg': '一汽',
    'images/red/203.jpg': '其他',
    'images/brown/1875.jpg': '比亚迪',
    'images/yellow/3344.jpg': '福田',
    'images/white/604.jpg': '福特',
    'images/white/166.jpg': '五菱',
    'images/car/364.jpg': '长城',
    'images/car/176.jpg': '海马',
    'images/truck/1119.jpg': '福田',
    'images/red/65.jpg': '比亚迪',
    'images/blue/181.jpg': '福田',
    'images/bus/3245.jpg': '舒驰',
    'images/red/830.jpg': '别克',
    'images/green/2119.jpg': '大众',
    'images/blue/1458.jpg': '本田',
    'images/yellow/796.jpg': '其他',
    'images/brown/2745.jpg': '起亚',
    'images/red/1014.jpg': '雪佛兰',
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
