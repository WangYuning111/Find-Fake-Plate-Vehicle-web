import csv

fixes = {
    'images/truck/291.jpg': '一汽',
    'images/yellow/1195.jpg': '江铃',
    'images/silver/34.jpg': '长安',
    'images/blue/291.jpg': '一汽',
    'images/blue/11.jpg': '中华',
    'images/yellow/Flip_Vec_15.jpg': '奇瑞',
    'images/bus/2721.jpg': '雪铁龙',
    'images/red/214.jpg': '江淮',
    'images/bus/2964.jpg': '现代',
    'images/truck/75.jpg': '金杯',
    'images/truck/1941.jpg': '一汽',
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
