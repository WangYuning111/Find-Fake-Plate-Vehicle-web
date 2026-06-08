#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车辆识别全维度诊断脚本
- 批量测试车型、颜色、品牌三个维度的识别准确率
- 输出各类别的混淆矩阵，精确定位问题所在
- 根据结果给出针对性训练建议

用法:
    python evaluate_models.py
"""
import os
import sys
import csv
import random
import numpy as np
from collections import Counter, defaultdict

import cv2
import torch
import torch.nn as nn
import torchvision.transforms as T
from torchvision import models

from config import Config
from conv import MiniVGGNet
from preprocessing import AspectAwarePreprocessor, ImageToTensorPreprocessor

DEVICE = torch.device('cpu')

# ==================== 加载模型 ====================
def load_models():
    """加载所有推理模型"""
    print("[诊断] 加载模型...")
    
    # 车型分类 (MiniVGGNet)
    type_model = MiniVGGNet(100, 100, 3, 4).to(DEVICE)
    type_model.load_state_dict(torch.load(Config.VEHICLE_TYPE_MODEL_PATH, map_location=DEVICE, weights_only=True))
    type_model.eval()
    type_classes = ["bus", "car", "minibus", "truck"]
    
    # 颜色分类 (MiniVGGNet)
    color_model = MiniVGGNet(100, 100, 3, 8).to(DEVICE)
    color_model.load_state_dict(torch.load(Config.VEHICLE_COLOR_MODEL_PATH, map_location=DEVICE, weights_only=True))
    color_model.eval()
    color_classes = ["black", "blue", "brown", "green", "red", "silver", "white", "yellow"]
    
    # 品牌分类 (ResNet18)
    brand_model = None
    brand_classes = None
    brand_transform = None
    brand_model_path = 'cfg/vehicle_brand_resnet18.pth'
    if os.path.exists(brand_model_path):
        checkpoint = torch.load(brand_model_path, map_location=DEVICE, weights_only=True)
        if 'fc.weight' in checkpoint:
            num_brands = checkpoint['fc.weight'].shape[0]
        else:
            num_brands = 26
        brand_model = models.resnet18(weights=None)
        brand_model.fc = nn.Linear(brand_model.fc.in_features, num_brands)
        brand_model.load_state_dict(checkpoint)
        brand_model = brand_model.to(DEVICE)
        brand_model.eval()
        
        # 从 brand_id_map.json 读取品牌列表
        import json
        if os.path.exists('cfg/brand_id_map.json'):
            with open('cfg/brand_id_map.json', 'r', encoding='utf-8') as f:
                brand_id_map = json.load(f)
            # 支持列表或字典格式
            if isinstance(brand_id_map, list):
                brand_classes = brand_id_map
            else:
                brand_classes = [None] * len(brand_id_map)
                for brand, bid in brand_id_map.items():
                    brand_classes[bid] = brand
        else:
            # 从csv推断
            brand_labels_set = set()
            with open('brand_labels.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    brand_labels_set.add(row['brand'].strip())
            brand_classes = sorted(list(brand_labels_set))
            if len(brand_classes) != num_brands:
                # 适配过滤模型的情况
                brand_classes = ['一汽','东风','丰田','五菱','别克','大众','奇瑞','奥迪','日产','本田','标致','比亚迪','江淮','江铃','海马','现代','福特','福田','舒驰','起亚','金杯','铃木','长城','长安','雪佛兰','雪铁龙']
        
        brand_transform = T.Compose([
            T.ToPILImage(),
            T.Resize((224, 224)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        print(f"[诊断] 品牌分类器: {len(brand_classes)} 个品牌")
    
    aap = AspectAwarePreprocessor(100, 100)
    iap = ImageToTensorPreprocessor(data_format='channels_first')
    
    return {
        'type_model': type_model, 'type_classes': type_classes,
        'color_model': color_model, 'color_classes': color_classes,
        'brand_model': brand_model, 'brand_classes': brand_classes,
        'brand_transform': brand_transform,
        'aap': aap, 'iap': iap,
    }


def predict_type(img, models):
    """预测车型"""
    roi = models['aap'].preprocess(img)
    tensor = models['iap'].preprocess(roi).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        out = models['type_model'](tensor)
        probs = torch.softmax(out, dim=1)[0].cpu().numpy()
    return models['type_classes'][int(np.argmax(probs))], float(np.max(probs))


def predict_color(img, models):
    """预测颜色"""
    roi = models['aap'].preprocess(img)
    tensor = models['iap'].preprocess(roi).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        out = models['color_model'](tensor)
        probs = torch.softmax(out, dim=1)[0].cpu().numpy()
    return models['color_classes'][int(np.argmax(probs))], float(np.max(probs))


def predict_brand(img, models):
    """预测品牌"""
    if models['brand_model'] is None or models['brand_transform'] is None:
        return '未加载', 0.0
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    tensor = models['brand_transform'](img_rgb).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        out = models['brand_model'](tensor)
        probs = torch.softmax(out, dim=1)[0].cpu().numpy()
    idx = int(np.argmax(probs))
    conf = float(np.max(probs))
    if idx < len(models['brand_classes']):
        return models['brand_classes'][idx], conf
    return '未知', conf


# ==================== 测试数据集 ====================
def load_type_test_data(max_per_class=50):
    """加载车型测试数据: images/{bus,car,minibus,truck}/"""
    data = []
    for cls in ['bus', 'car', 'minibus', 'truck']:
        path = os.path.join('images', cls)
        if not os.path.exists(path):
            continue
        files = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        random.shuffle(files)
        for f in files[:max_per_class]:
            data.append((os.path.join(path, f), cls))
    return data


def load_color_test_data(max_per_class=50):
    """加载颜色测试数据: images/{black,blue,brown,green,red,silver,white,yellow}/"""
    data = []
    for cls in ['black', 'blue', 'brown', 'green', 'red', 'silver', 'white', 'yellow']:
        path = os.path.join('images', cls)
        if not os.path.exists(path):
            continue
        files = [f for f in os.listdir(path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        random.shuffle(files)
        for f in files[:max_per_class]:
            data.append((os.path.join(path, f), cls))
    return data


def load_brand_test_data(max_total=200):
    """加载品牌测试数据: brand_labels.csv 中已标注样本"""
    data = []
    with open('brand_labels.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = [r for r in reader if r['brand'].strip() != '其他']
    random.shuffle(rows)
    for r in rows[:max_total]:
        p = r['image_path']
        if os.path.exists(p):
            data.append((p, r['brand'].strip()))
    return data


# ==================== 评估核心 ====================
def evaluate_task(task_name, test_data, predict_fn, models, label_transform=None):
    """
    通用评估函数
    :param label_transform: 标签转换函数，用于统一标签格式
    """
    if not test_data:
        print(f"[诊断] {task_name}: 无测试数据，跳过")
        return None
    
    total = len(test_data)
    correct = 0
    per_class = defaultdict(lambda: {'correct': 0, 'total': 0})
    confusion = defaultdict(lambda: defaultdict(int))
    errors = []
    
    print(f"\n[诊断] 正在评估 {task_name}，样本数: {total}")
    
    for img_path, true_label in test_data:
        img = cv2.imread(img_path)
        if img is None:
            continue
        
        pred_label, conf = predict_fn(img, models)
        
        tlabel = label_transform(true_label) if label_transform else true_label
        plabel = label_transform(pred_label) if label_transform else pred_label
        
        is_correct = (plabel == tlabel)
        correct += is_correct
        per_class[tlabel]['total'] += 1
        if is_correct:
            per_class[tlabel]['correct'] += 1
        else:
            if len(errors) < 5:
                errors.append((img_path, tlabel, plabel, conf))
        confusion[tlabel][plabel] += 1
    
    accuracy = correct / total if total > 0 else 0
    
    # 输出结果
    print(f"  ==> {task_name} 总体准确率: {correct}/{total} = {accuracy*100:.1f}%")
    
    # 各类别准确率
    print(f"  ==> 各类别准确率:")
    worst_classes = []
    for cls in sorted(per_class.keys()):
        c = per_class[cls]['correct']
        t = per_class[cls]['total']
        acc = c / t if t > 0 else 0
        marker = " [低]" if acc < 0.7 else ""
        print(f"      {cls:12s}: {c:3d}/{t:3d} = {acc*100:5.1f}%{marker}")
        if acc < 0.7 and t >= 5:
            worst_classes.append((cls, acc, t))
    
    # 输出典型错误
    if errors:
        print(f"  ==> 典型错误样例:")
        for img_path, t, p, c in errors:
            print(f"      {os.path.basename(img_path)}: 真实={t}, 预测={p}, 置信度={c:.2f}")
    
    return {
        'task': task_name,
        'accuracy': accuracy,
        'correct': correct,
        'total': total,
        'per_class': dict(per_class),
        'worst_classes': worst_classes,
        'confusion': dict(confusion),
    }


def print_confusion_matrix(confusion, classes):
    """打印混淆矩阵"""
    print(f"\n  ==> 混淆矩阵 (行=真实, 列=预测):")
    header = "      " + "".join([f"{c:>8s}" for c in classes])
    print(header)
    for true_c in classes:
        row = f"  {true_c:>6s}"
        for pred_c in classes:
            count = confusion.get(true_c, {}).get(pred_c, 0)
            if true_c == pred_c:
                row += f"\033[92m{count:>8d}\033[0m"  # 绿色对角线
            elif count > 0:
                row += f"\033[91m{count:>8d}\033[0m"  # 红色错误
            else:
                row += f"{count:>8d}"
        print(row)


def main():
    print("=" * 60)
    print("  车辆识别全维度诊断")
    print("=" * 60)
    
    random.seed(42)
    models = load_models()
    
    # 1. 评估车型
    type_data = load_type_test_data(max_per_class=50)
    type_result = evaluate_task("车型分类", type_data, predict_type, models)
    if type_result:
        print_confusion_matrix(type_result['confusion'], models['type_classes'])
    
    # 2. 评估颜色
    color_data = load_color_test_data(max_per_class=50)
    color_result = evaluate_task("颜色分类", color_data, predict_color, models)
    if color_result:
        print_confusion_matrix(color_result['confusion'], models['color_classes'])
    
    # 3. 评估品牌
    brand_data = load_brand_test_data(max_total=200)
    brand_result = evaluate_task("品牌分类", brand_data, predict_brand, models)
    
    # ==================== 诊断结论 ====================
    print("\n" + "=" * 60)
    print("  诊断结论与训练建议")
    print("=" * 60)
    
    results = [r for r in [type_result, color_result, brand_result] if r]
    if not results:
        print("[诊断] 无可用评估结果")
        return
    
    # 按准确率排序
    results.sort(key=lambda x: x['accuracy'])
    
    print(f"\n{'维度':<12s} {'准确率':>8s} {'样本数':>8s} {'状态':>10s}")
    print("-" * 45)
    for r in results:
        status = "[良好]" if r['accuracy'] >= 0.85 else ("[一般]" if r['accuracy'] >= 0.70 else "[需训练]")
        print(f"{r['task']:<12s} {r['accuracy']*100:>7.1f}% {r['total']:>8d} {status:>10s}")
    
    # 找出最差的维度
    worst = results[0]
    print(f"\n[重点] 最需要改进的维度: {worst['task']} (准确率 {worst['accuracy']*100:.1f}%)")
    
    if worst['worst_classes']:
        print(f"[重点] 表现最差的类别:")
        for cls, acc, total in sorted(worst['worst_classes'], key=lambda x: x[1]):
            print(f"      - {cls}: {acc*100:.1f}% ({total}张)")
    
    # 训练建议
    print("\n" + "=" * 60)
    print("  针对性训练命令")
    print("=" * 60)
    
    if worst['task'] == '品牌分类':
        print("""
品牌分类需要改进，建议：
1. 继续清洗 brand_labels.csv 中标记为"其他"的样本
   python auto_label_filtered.py  # 自动标注高置信度样本
   
2. 人工审图修正错误标注
   （查看 brand_labels.csv 中"其他"标签的图片，人工确认品牌）
   
3. 重新训练品牌模型
   python train_brand_filtered_v2.py
""")
    elif worst['task'] == '车型分类':
        print("""
车型分类需要改进，建议：
1. 使用 train_all.py 重新训练车型模型
   python train_all.py --task type --src images --epochs 50
   
2. 或提升为 ResNet18 模型
   python train_vehicle_type.py
""")
    elif worst['task'] == '颜色分类':
        print("""
颜色分类需要改进，建议：
1. 使用 train_all.py 重新训练颜色模型
   python train_all.py --task color --src images --epochs 50
   
2. 检查易混淆类别（如 black/blue, silver/white）的数据质量
   确认 images/black/ 和 images/blue/ 中是否有混放
""")
    
    print("\n[提示] 车牌识别使用 HyperLPR 第三方库，如需改进建议：")
    print("      - 确保图片清晰度足够")
    print("      - 调整 improve_accuracy.py 中的图像增强参数")
    print("      - 或更换为 PaddleOCR/CRNN 等更强的 OCR 模型")


if __name__ == '__main__':
    main()
