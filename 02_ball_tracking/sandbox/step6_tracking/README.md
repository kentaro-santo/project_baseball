# ステップ6: 賢くなったAIでボールを追跡（トラッキング）しよう

## やること
学習したオリジナルAI（`best.pt`）と、動画のパスを指定してトラッキングを実行します。

## 実行するコード

```python
from ultralytics import YOLO

# 【ここを書き換えてください】
# 1. ステップ2の動画パス
INPUT_VIDEO_PATH = '/content/drive/MyDrive/output_preprocessed.mp4'
# 2. ステップ5で学習したモデル(best.pt)のパス
CUSTOM_WEIGHTS_PATH = '/content/drive/MyDrive/baseball_tracker/yolov8_custom/weights/best.pt'

# プロジェクト（結果の保存先）のパス
PROJECT_DIR = '/content/drive/MyDrive/baseball_tracker'

# ステップ5で鍛え上げたモデルを呼び出します
model = YOLO(CUSTOM_WEIGHTS_PATH)

print("動画内のボールをトラッキング（追跡）しています...")

# トラッキングの実行
results = model.track(
    source=INPUT_VIDEO_PATH,
    tracker="bytetrack.yaml",  
    conf=0.25,                 # 25%以上の自信があれば検知
    save=True,                 # 結果の動画を保存
    project=PROJECT_DIR,
    name='tracking_results'
)

print("トラッキングが完了しました！")
print(f"結果の動画は '{PROJECT_DIR}/tracking_results' フォルダに保存されています！")
```
