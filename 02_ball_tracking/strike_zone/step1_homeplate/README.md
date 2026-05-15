# ステップ1: ホームベースの座標を取得しよう

ストライクゾーンを作るための「土台」となる、ホームベースの位置を動画から特定します。

## やること
動画の最初の1フレーム目を画像（`first_frame.jpg`）として保存し、Colab上に表示します。
表示された画像を見ながら、ホームベースの4つの角の座標（X, Y）の当たりをつけます。

## 実行するコード

```python
from google.colab import drive
import cv2
import matplotlib.pyplot as plt

drive.mount('/content/drive')

# 【ここを書き換えてください】ステップ2の動画パス
INPUT_VIDEO_PATH = '/content/drive/MyDrive/output_preprocessed.mp4'

def extract_first_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("動画が読み込めません。")
        return None
    
    ret, frame = cap.read()
    cap.release()
    
    if ret:
        # OpenCVのBGRからMatplotlibのRGBに変換
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 画像を表示し、座標軸（目盛り）も表示します
        plt.figure(figsize=(12, 8))
        plt.imshow(frame_rgb)
        plt.title("ホームベースの4つの角の座標（X, Y）をメモしてください")
        plt.grid(True, color='yellow', linestyle='--', linewidth=0.5)
        plt.show()
        
        return frame_rgb
    else:
        print("フレームの取得に失敗しました。")
        return None

if __name__ == "__main__":
    extract_first_frame(INPUT_VIDEO_PATH)
```

**結果の確認：**
実行すると、動画の1コマ目が画面に出ます。画像のフチに目盛り（ピクセル数）がついているので、ホームベースの「左手前」「右手前」「左奥」「右奥」の大体の数字をメモしておきましょう。
