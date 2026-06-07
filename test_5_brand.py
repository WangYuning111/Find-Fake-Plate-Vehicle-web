#!/usr/bin/env python3
import os
import random
from inference import predict_single

random.seed()
all_images = []
for root, dirs, files in os.walk('images'):
    for f in files:
        if f.endswith('.jpg'):
            all_images.append(os.path.join(root, f))

selected = random.sample(all_images, 5)

print('随机抽取5张图片:')
for i, path in enumerate(selected, 1):
    result = predict_single(path)
    brand = result['vehicle_brand']
    vtype = result['vehicle_type']
    color = result['vehicle_color']
    print(f'{i}. {path}')
    print(f'   项目识别: 品牌={brand}, 车型={vtype}, 颜色={color}')
    print()
