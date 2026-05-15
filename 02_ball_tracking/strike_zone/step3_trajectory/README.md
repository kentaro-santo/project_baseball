# ステップ3: トラッキング軌道とゾーンの合成動画を作成しよう

完成したストライクゾーンの枠と、ボールトラッキングの「軌跡データ（CSV）」を組み合わせて、最終的な分析動画を出力します。

## やること
動画の全フレームに対して、ゾーンの枠線と、CSVから読み取ったボールの軌跡（過去の座標をつなぐ線）を描画して新しい動画として書き出します。

## 実行するコード

```python
import cv2
import numpy as np
import csv

# 【ここを書き換えてください】
INPUT_VIDEO_PATH = '/content/drive/MyDrive/output_preprocessed.mp4'
INPUT_CSV_PATH = '/content/drive/MyDrive/ball_trajectory.csv'
OUTPUT_VIDEO_PATH = '/content/drive/MyDrive/zone_and_trajectory.mp4'

# ステップ2で決定した座標
HOME_PLATE_PTS = np.array([[500, 800], [700, 800], [650, 750], [550, 750]], np.int32)
ZONE_BOTTOM_H = 100
ZONE_TOP_H = 350

def draw_trajectory_and_zone():
    print("軌道合成動画を作成中...")
    # CSVデータの読み込み（フレームごとのボール座標を辞書に格納）
    ball_positions = {}
    with open(INPUT_CSV_PATH, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) # ヘッダーを飛ばす
        for row in reader:
            if not row: continue
            frame_idx = int(row[0])
            x, y = float(row[2]), float(row[3])
            ball_positions[frame_idx] = (int(x), int(y))
            
    cap = cv2.VideoCapture(INPUT_VIDEO_PATH)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    out = cv2.VideoWriter(OUTPUT_VIDEO_PATH, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    
    # ゾーン前面の座標
    front_face = np.array([
        [HOME_PLATE_PTS[0][0], HOME_PLATE_PTS[0][1] - ZONE_BOTTOM_H],
        [HOME_PLATE_PTS[1][0], HOME_PLATE_PTS[1][1] - ZONE_BOTTOM_H],
        [HOME_PLATE_PTS[1][0], HOME_PLATE_PTS[1][1] - ZONE_TOP_H],
        [HOME_PLATE_PTS[0][0], HOME_PLATE_PTS[0][1] - ZONE_TOP_H]
    ], np.int32)

    current_frame = 0
    trajectory_points = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        # ゾーン枠の描画
        cv2.polylines(frame, [HOME_PLATE_PTS], True, (255, 255, 255), 2)
        cv2.polylines(frame, [front_face], True, (0, 255, 0), 2)
        
        # 軌跡の描画
        if current_frame in ball_positions:
            trajectory_points.append(ball_positions[current_frame])
            
        # ボールの通った道筋を赤い線で結ぶ
        for i in range(1, len(trajectory_points)):
            cv2.line(frame, trajectory_points[i-1], trajectory_points[i], (0, 0, 255), 3)
            
        out.write(frame)
        current_frame += 1

    cap.release()
    out.release()
    print(f"動画の保存が完了しました！ -> {OUTPUT_VIDEO_PATH}")

if __name__ == "__main__":
    draw_trajectory_and_zone()
```

完了したら、Google Driveから `zone_and_trajectory.mp4` をダウンロードして再生してみましょう！ストライクゾーンの枠に向かって、ボールの軌跡が赤い線で描かれるはずです。
