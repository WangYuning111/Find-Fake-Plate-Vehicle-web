#!/usr/bin/env python3
import os, random
from inference import predict_single

random.seed()

def test_samples(n=3):
    print("="*60)
    print(f"随机抽样验证 (每类{n}张)")
    print("="*60)

    ok_count = 0
    total = 0

    # 颜色抽样
    for color in ['black', 'blue', 'brown', 'green', 'red', 'silver', 'white', 'yellow']:
        folder = f'images/{color}'
        files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg','.jpeg','.png'))]
        samples = random.sample(files, min(n, len(files)))
        for f in samples:
            path = os.path.join(folder, f)
            try:
                result = predict_single(path)
                c_ok = result['vehicle_color'].lower() == color
                marker = "✓" if c_ok else "✗"
                print(f"[{marker}] {color:7s} | 颜色={result['vehicle_color']:7s} | 车型={result['vehicle_type']:8s} | 品牌={result['vehicle_brand']}")
                if c_ok: ok_count += 1
                total += 1
            except Exception as e:
                print(f"[✗] {color:7s} | 错误: {e}")
                total += 1

    # 车型抽样
    for vtype in ['bus', 'car', 'minibus', 'truck']:
        folder = f'images/{vtype}'
        files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg','.jpeg','.png'))]
        samples = random.sample(files, min(n, len(files)))
        for f in samples:
            path = os.path.join(folder, f)
            try:
                result = predict_single(path)
                t_ok = result['vehicle_type'].lower() == vtype
                marker = "✓" if t_ok else "✗"
                print(f"[{marker}] {vtype:8s} | 颜色={result['vehicle_color']:7s} | 车型={result['vehicle_type']:8s} | 品牌={result['vehicle_brand']}")
                if t_ok: ok_count += 1
                total += 1
            except Exception as e:
                print(f"[✗] {vtype:8s} | 错误: {e}")
                total += 1

    print("="*60)
    print(f"准确率: {ok_count}/{total} = {ok_count/total*100:.1f}%")
    print("="*60)

if __name__ == '__main__':
    test_samples(3)
