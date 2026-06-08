import csv

fixes = {
    'images/white/132.jpg': '长安',
    'images/yellow/Flip_Vec_3.jpg': '奇瑞',
    'images/yellow/Flip_Hor_15.jpg': '奇瑞',
    'images/yellow/Shift_4.jpg': '奇瑞',
    'images/green/2018.jpg': '大众',
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
