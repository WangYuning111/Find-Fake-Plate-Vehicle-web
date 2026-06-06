#!/usr/bin/env bash
# ============================================================
# 模型权重一键下载脚本
# 支持: wget / curl
# 来源: GitHub Release / HuggingFace / ModelScope
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEIGHTS_DIR="${SCRIPT_DIR}/weights"
mkdir -p "${WEIGHTS_DIR}"

echo "=========================================="
echo "  套牌车检测系统 - 模型权重下载"
echo "=========================================="

# 下载函数：优先 wget，备选 curl
download_file() {
    local url="$1"
    local output="$2"
    if command -v wget &> /dev/null; then
        wget --show-progress -O "${output}" "${url}"
    elif command -v curl &> /dev/null; then
        curl -L --progress-bar -o "${output}" "${url}"
    else
        echo "错误: 未找到 wget 或 curl，请手动下载"
        exit 1
    fi
}

# --------------------------------------------------
# 模型文件列表
# 默认使用 GitHub Release 直链（Release 上传后替换为实际链接）
# 备选: HuggingFace / ModelScope / 百度网盘
# --------------------------------------------------

# GitHub Release 占位链接（请替换为实际 Release 附件地址）
BASE_URL="https://github.com/WangYuning111/Find-Fake-Plate-Vehicle-web2/releases/download/v1.0.0"

# 各模型文件
MODELS=(
    "best.pt"
    "vehicle_type.pth"
    "vehicle_color.pth"
)

# 下载每个模型
for model in "${MODELS[@]}"; do
    dest="${WEIGHTS_DIR}/${model}"
    if [[ -f "${dest}" ]]; then
        echo "[跳过] ${model} 已存在"
    else
        echo "[下载] ${model} ..."
        download_file "${BASE_URL}/${model}" "${dest}"
        echo "[完成] ${model}"
    fi
done

echo "=========================================="
echo "  所有模型下载完成"
echo "  存放目录: ${WEIGHTS_DIR}"
echo "=========================================="
