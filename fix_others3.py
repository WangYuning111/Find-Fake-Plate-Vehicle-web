import csv

fixes = {
    'images/yellow/Flip_Hor_12.jpg': '金杯',
    'images/truck/26.jpg': '福田',
    'images/green/161.jpg': '大众',
    'images/truck/81.jpg': '金杯',
    'images/brown/154.jpg': '长城',
    'images/yellow/Flip_Vec_0.jpg': '江铃',
    'images/green/1982.jpg': '大众',
    'images/black/412.jpg': '丰田',
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
