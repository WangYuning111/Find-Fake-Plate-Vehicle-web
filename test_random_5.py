#!/usr/bin/env python3
"""
随机抽5张图片，使用项目完整推理流程识别
对比结果与真实标签
"""
import os
import random
import cv2
from inference import load_models, predict_single

random.seed()

# 从所有类别中随机选5张
all_images = []
for category in ['black', 'blue', 'brown', 'green', 'red', 'silver', 'white', 'yellow', 'bus', 'car', 'minibus', 'truck']:
    folder = f'images/{category}'
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if f.endswith('.jpg'):
                all_images.append((category, os.path.join(folder, f)))

# 随机选5张
selected = random.sample(all_images, 5)

print("=" * 70)
print("随机抽取5张图片进行识别测试")
print("=" * 70)

models = load_models()

results = []
for true_label, img_path in selected:
    print(f"\n图片: {img_path}")
    print(f"真实标签: {true_label}")
    
    # 使用项目完整推理
    result = predict_single(img_path)
    
    pred_type = result['vehicle_type']
    pred_color = result['vehicle_color']
    pred_brand = result['vehicle_brand']
    pred_plate = result['plate_number']
    
    print(f"识别结果: 类型={pred_type}, 颜色={pred_color}, 品牌={pred_brand}, 车牌={pred_plate}")
    
    # 判断是否正确
    # 如果真实标签是颜色类别，检查颜色
    # 如果真实标签是车型类别，检查车型
    if true_label in ['black', 'blue', 'brown', 'green', 'red', 'silver', 'white', 'yellow']:
        is_correct = (pred_color.lower() == true_label.lower())
        check_item = f"颜色({true_label})"
    else:
        is_correct = (pred_type.lower() == true_label.lower())
        check_item = f"车型({true_label})"
    
    status = "✅ 正确" if is_correct else "❌ 错误"
    print(f"验证: {check_item} -> {status}")
    
    results.append({
        'path': img_path,
        'true_label': true_label,
        'pred_type': pred_type,
        'pred_color': pred_color,
        'pred_brand': pred_brand,
        'pred_plate': pred_plate,
        'is_correct': is_correct,
        'check_item': check_item
    })

# 汇总
print("\n" + "=" * 70)
print("汇总结果")
print("=" * 70)
correct_count = sum(1 for r in results if r['is_correct'])
print(f"正确: {correct_count}/5 ({correct_count/5*100:.0f}%)")

for r in results:
    status = "✅" if r['is_correct'] else "❌"
    print(f"{status} {r['path']} | 真实={r['true_label']} | 识别=类型:{r['pred_type']} 颜色:{r['pred_color']} 品牌:{r['pred_brand']}")

# 如果有错误，输出详细信息
wrong = [r for r in results if not r['is_correct']]
if wrong:
    print("\n" + "=" * 70)
    print("错误样本详情（用于分析）")
    print("=" * 70)
    for r in wrong:
        print(f"  文件: {r['path']}")
        print(f"  真实: {r['true_label']}")
        print(f"  预测: 类型={r['pred_type']}, 颜色={r['pred_color']}, 品牌={r['pred_brand']}")
        print()
