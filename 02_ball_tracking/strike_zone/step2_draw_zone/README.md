# ステップ2: ストライクゾーンの枠（2D）を描画してみよう

ステップ1でメモしたホームベースの座標と、おおよその高さを設定して、画像の上にストライクゾーンの「前面」と「後面」の枠を描いてみます。

## やること
メモした座標をコードの中に入力し、画像に重ねて四角形（ポリゴン）を描画して位置を微調整します。

## 実行するコード

```python
import cv2
import numpy as np
import matplotlib.pyplot as plt

# 【ここを書き換えてください】ステップ1で取得した動画パス
INPUT_VIDEO_PATH = '/content/drive/MyDrive/output_preprocessed.mp4'

# 【ここを書き換えてください】ステップ1でメモしたホームベースの4つの角の座標
# 順番：[左手前, 右手前, 右奥, 左奥]
# 例： [[500, 800], [700, 800], [650, 750], [550, 750]]
HOME_PLATE_PTS = np.array([
    [500, 800], 
    [700, 800], 
    [650, 750], 
    [550, 750]
], np.int32)

# ストライクゾーンの高さ（画像上での上方向へのピクセル数）
# ※カメラの角度によって見え方が変わるため、目視で微調整します
ZONE_BOTTOM_H = 100  # 膝の高さ（手前側）
ZONE_TOP_H = 350     # 胸の高さ（手前側）

def draw_test_zone(video_path, plate_pts, bottom_h, top_h):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    
    if not ret: return
    
    # 手前側の面（ホームベースの手前2点から上に伸ばした四角）
    front_bottom_left = [plate_pts[0][0], plate_pts[0][1] - bottom_h]
    front_bottom_right = [plate_pts[1][0], plate_pts[1][1] - bottom_h]
    front_top_right = [plate_pts[1][0], plate_pts[1][1] - top_h]
    front_top_left = [plate_pts[0][0], plate_pts[0][1] - top_h]
    
    front_face = np.array([front_bottom_left, front_bottom_right, front_top_right, front_top_left], np.int32)
    
    # 枠を描画
    cv2.polylines(frame, [plate_pts], isClosed=True, color=(255, 255, 255), thickness=2) # ベース
    cv2.polylines(frame, [front_face], isClosed=True, color=(0, 255, 0), thickness=2)    # 前面ゾーン
    
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    plt.figure(figsize=(12, 8))
    plt.imshow(frame_rgb)
    plt.title("ストライクゾーン枠の微調整")
    plt.show()

if __name__ == "__main__":
    draw_test_zone(INPUT_VIDEO_PATH, HOME_PLATE_PTS, ZONE_BOTTOM_H, ZONE_TOP_H)
```

ピッタリ枠が合うまで、座標や高さを微調整して何度か実行してみてください。
