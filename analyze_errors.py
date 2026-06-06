#!/usr/bin/env python3
import json
from collections import defaultdict, Counter

with open('verify_results.json', 'r') as f:
    data = json.load(f)

# 排除NO_VEHICLE，只统计分类错误
classifiable = [r for r in data if r['predicted'] != 'NO_VEHICLE']
print(f'可分类样本: {len(classifiable)}/{len(data)}')
correct_count = sum(1 for r in classifiable if r['correct'])
print(f'总体准确率(排除NO_VEHICLE): {correct_count/len(classifiable)*100:.1f}%')
print()

# 按类别统计
by_label = defaultdict(list)
for r in classifiable:
    by_label[r['true_label']].append(r)

for label in sorted(by_label.keys()):
    items = by_label[label]
    correct = sum(1 for i in items if i['correct'])
    wrong = len(items) - correct
    acc = correct / len(items) * 100 if items else 0
    print(f'{label:10s}: {correct}/{len(items)} 正确 ({acc:.1f}%), 错误 {wrong} 个')
    if wrong > 0:
        wrong_preds = Counter([i['predicted'] for i in items if not i['correct']])
        print(f'    错误分布: {dict(wrong_preds)}')

# 输出需要重点改进的类别
print("\n===== 重点改进类别 =====")
for label in sorted(by_label.keys()):
    items = by_label[label]
    correct = sum(1 for i in items if i['correct'])
    acc = correct / len(items) * 100 if items else 0
    if acc < 80:
        print(f"  {label}: {acc:.1f}% 需要改进")
