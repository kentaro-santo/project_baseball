# Colabセル用：YOLOv8環境セットアップ
# !pip install ultralytics

import torch
from ultralytics import YOLO

def setup_environment():
    print("--- 実行環境の確認 ---")
    print("CUDA (GPU) is available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("GPU device name:", torch.cuda.get_device_name(0))
    else:
        print("警告: GPUが有効になっていません。Colabのランタイムのタイプを変更してGPUを設定してください。")

    # YOLOv8の動作確認（標準モデルのダウンロード）
    model = YOLO('yolov8n.pt')
    print("YOLOv8 setup complete.")

if __name__ == "__main__":
    setup_environment()
