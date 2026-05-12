# ステップ7: 分析のためのデータ抽出（CSV出力）

## やること
抽出元の動画パス、AIモデルのパス、出力するCSVのパスを指定して実行します。

## 実行するコード

```python
from ultralytics import YOLO
import csv

# 【ここを書き換えてください】
INPUT_VIDEO_PATH = '/content/drive/MyDrive/output_preprocessed.mp4'
CUSTOM_WEIGHTS_PATH = '/content/drive/MyDrive/baseball_tracker/yolov8_custom/weights/best.pt'
OUTPUT_CSV_PATH = '/content/drive/MyDrive/ball_trajectory.csv'

model = YOLO(CUSTOM_WEIGHTS_PATH)

print("ボールの座標データを抽出しています...")

# stream=True にすることで、メモリを節約して高速に処理します
results = model.track(
    source=INPUT_VIDEO_PATH, 
    tracker="bytetrack.yaml", 
    stream=True, 
    conf=0.25
)

with open(OUTPUT_CSV_PATH, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    # ヘッダーを書きます
    writer.writerow(["フレーム番号", "ボールID", "X座標", "Y座標", "横幅", "縦幅", "AIの自信度"])
    
    frame_idx = 0
    for r in results:
        boxes = r.boxes
        if boxes is not None and boxes.id is not None:
            # 見つかったボールの情報を取り出す
            for box, track_id, conf in zip(boxes.xywh, boxes.id, boxes.conf):
                x, y, w, h = box.tolist()
                # エクセルに1行書き込む
                writer.writerow([
                    frame_idx, 
                    int(track_id), 
                    round(x, 1), 
                    round(y, 1), 
                    round(w, 1), 
                    round(h, 1), 
                    round(float(conf), 3)
                ])
        frame_idx += 1

print(f"データ抽出が完了しました！ '{OUTPUT_CSV_PATH}' が保存されました。")
```
