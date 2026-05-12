# ステップ5: AIの特訓（ファインチューニング）

## やること
アノテーションが終わったデータセットのパス（`data.yaml`）を指定して学習を開始します。

## 実行するコード

```python
from ultralytics import YOLO

# 【ここを書き換えてください】Roboflow等からダウンロードしたデータセットの data.yaml のパス
DATA_YAML_PATH = '/content/drive/MyDrive/dataset/data.yaml'

# プロジェクト（結果の保存先）のパスもドライブ内に指定すると安全です
PROJECT_DIR = '/content/drive/MyDrive/baseball_tracker'

# まず、基礎的な賢さを持った初期モデルを呼び出します
model = YOLO('yolov8n.pt')

print("AIの特訓（学習）を開始します！数分〜十数分かかることがあります...")

# 学習の実行
results = model.train(
    data=DATA_YAML_PATH,   
    epochs=50,          # 50回反復練習します
    imgsz=640,          # 画像のサイズ
    batch=16,           # 一度に学習する画像の数
    project=PROJECT_DIR, # 保存先フォルダ
    name='yolov8_custom',
    device=0            # GPUを使う指定
)

print("特訓が完了しました！！")
print(f"学習済みモデルは '{PROJECT_DIR}/yolov8_custom/weights/best.pt' に保存されました。")
```
