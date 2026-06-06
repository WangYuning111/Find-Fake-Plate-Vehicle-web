#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量验证：用 images/ 文件夹中的图片验证颜色+车型识别准确率
文件夹结构即为标准标签
"""
import os
import cv2
import json
import time
from collections import defaultdict, Counter

# 颜色标签（英文->中文映射）
COLOR_LABELS = ['black', 'blue', 'brown', 'green', 'red', 'silver', 'white', 'yellow']
# 车型标签
TYPE_LABELS = ['bus', 'car', 'minibus', 'truck']

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
RESULTS_FILE = os.path.join(BASE_DIR, 'verify_results.json')

# 加载模型（只加载一次）
print("[VERIFY] 加载模型...")
import torch
from ultralytics import YOLO
from conv import MiniVGGNet
from preprocessing import AspectAwarePreprocessor, ImageToTensorPreprocessor
from inference import get_device

device = get_device()
yolo = YOLO('weights/best.pt')

v_type_model = MiniVGGNet(100, 100, 3, 4).to(device)
v_type_model.load_state_dict(torch.load("weights/vehicle_type.pth", map_location=device))
v_type_model.eval()

v_color_model = MiniVGGNet(100, 100, 3, 8).to(device)
v_color_model.load_state_dict(torch.load("weights/vehicle_color.pth", map_location=device))
v_color_model.eval()

type_classes = ["bus", "car", "minibus", "truck"]
color_classes = ["black", "blue", "brown", "green", "red", "silver", "white", "yellow"]
aap = AspectAwarePreprocessor(100, 100)
iap = ImageToTensorPreprocessor(data_format='channels_first')


def predict_type(crop_img):
    """预测车型"""
    roi = aap.preprocess(crop_img)
    tensor = iap.preprocess(roi).unsqueeze(0).to(device)
    with torch.no_grad():
        out = v_type_model(tensor)
        probs = torch.softmax(out, dim=1)[0].cpu().numpy()
    return type_classes[int(probs.argmax())], float(probs.max())


def predict_color(crop_img):
    """预测颜色（使用训练好的MiniVGGNet模型）"""
    roi = aap.preprocess(crop_img)
    tensor = iap.preprocess(roi).unsqueeze(0).to(device)
    with torch.no_grad():
        out = v_color_model(tensor)
        probs = torch.softmax(out, dim=1)[0].cpu().numpy()
    return color_classes[int(probs.argmax())], float(probs.max())


def detect_vehicle(img):
    """YOLO检测车辆，返回最佳检测框"""
    results = yolo(source=img, conf=0.1, iou=0.45, verbose=False)
    result = results[0]
    if len(result.boxes) == 0:
        results = yolo(source=img, conf=0.05, iou=0.3, verbose=False)
        result = results[0]
    if len(result.boxes) == 0:
        return None
    boxes = result.boxes.xyxy.cpu().numpy().astype(int)
    confs = result.boxes.conf.cpu().numpy()
    best = int(confs.argmax())
    x1, y1, x2, y2 = boxes[best]
    h, w = img.shape[:2]
    return (max(0, x1), max(0, y1), min(w, x2), min(h, y2))


def verify_folder(folder_name, label_type):
    """验证一个文件夹下的所有图片"""
    folder_path = os.path.join(IMAGES_DIR, folder_name)
    if not os.path.exists(folder_path):
        return []

    files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    results = []

    for i, fname in enumerate(files):
        fpath = os.path.join(folder_path, fname)
        img = cv2.imread(fpath)
        if img is None:
            continue

        bbox = detect_vehicle(img)
        if bbox is None:
            results.append({
                'file': fpath,
                'true_label': folder_name,
                'predicted': 'NO_VEHICLE',
                'correct': False,
                'confidence': 0.0
            })
            continue

        x1, y1, x2, y2 = bbox
        crop = img[y1:y2, x1:x2]

        if label_type == 'color':
            # 颜色模型训练时用的是全图，测试也用全图保持一致
            pred, conf = predict_color(img)
        else:
            # 车型模型训练时也是全图，测试也用全图保持一致
            pred, conf = predict_type(img)

        correct = (pred.lower() == folder_name.lower())
        results.append({
            'file': fpath,
            'true_label': folder_name,
            'predicted': pred,
            'correct': correct,
            'confidence': round(conf, 4)
        })

        if (i + 1) % 20 == 0:
            print(f"  [{folder_name}] 已处理 {i+1}/{len(files)}")

    return results


def main():
    all_results = []

    # 验证颜色
    print("\n[VERIFY] ===== 颜色识别验证 =====")
    for color in COLOR_LABELS:
        print(f"\n处理颜色: {color}")
        res = verify_folder(color, 'color')
        all_results.extend(res)
        correct = sum(1 for r in res if r['correct'])
        print(f"  结果: {correct}/{len(res)} 正确 ({correct/len(res)*100:.1f}%)")

    # 验证车型
    print("\n[VERIFY] ===== 车型识别验证 =====")
    for vtype in TYPE_LABELS:
        print(f"\n处理车型: {vtype}")
        res = verify_folder(vtype, 'type')
        all_results.extend(res)
        correct = sum(1 for r in res if r['correct'])
        print(f"  结果: {correct}/{len(res)} 正确 ({correct/len(res)*100:.1f}%)")

    # 保存结果
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    # 统计
    print("\n[VERIFY] ===== 总体统计 =====")
    total = len(all_results)
    total_correct = sum(1 for r in all_results if r['correct'])
    print(f"总计: {total_correct}/{total} 正确 ({total_correct/total*100:.1f}%)")

    # 按类别统计错误
    print("\n[VERIFY] ===== 各类别详细统计 =====")
    by_label = defaultdict(list)
    for r in all_results:
        by_label[r['true_label']].append(r)

    for label, items in sorted(by_label.items()):
        correct = sum(1 for i in items if i['correct'])
        wrong = len(items) - correct
        print(f"  {label:10s}: {correct}/{len(items)} 正确, 错误 {wrong} 个")
        if wrong > 0:
            wrong_preds = Counter([i['predicted'] for i in items if not i['correct']])
            print(f"    错误分布: {dict(wrong_preds)}")

    # 输出错误样本路径（用于分析）
    print("\n[VERIFY] ===== 错误样本文件 =====")
    for r in all_results:
        if not r['correct']:
            print(f"  {r['file']} | 真实={r['true_label']} | 预测={r['predicted']} | conf={r['confidence']}")


if __name__ == '__main__':
    main()
