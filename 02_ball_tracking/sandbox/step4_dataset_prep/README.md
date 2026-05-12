# ステップ4: AIに勉強させるための教材を作ろう（画像切り出し）

## やること
動画から画像を切り出します。
入力する動画のパスと、画像を保存するフォルダのパスを指定します。

## 実行するコード

```python
import cv2
import os

# 【ここを書き換えてください】ステップ2で作成した動画のパスを貼り付けます
INPUT_VIDEO_PATH = '/content/drive/MyDrive/output_preprocessed.mp4'

# 画像の保存先フォルダ（ドライブ内に保存すると便利です）
OUTPUT_FRAMES_DIR = '/content/drive/MyDrive/frames_for_annotation'

def extract_frames(video_path, output_dir, interval_frames=15):
    print("動画から静止画を切り出します...")
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: 動画ファイルを読み込めません。")
        return

    frame_count = 0
    saved_count = 0
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % interval_frames == 0:
            output_path = os.path.join(output_dir, f"frame_{saved_count:04d}.jpg")
            cv2.imwrite(output_path, frame)
            saved_count += 1
        frame_count += 1
        
    cap.release()
    print(f"合計 {saved_count} 枚の画像を '{output_dir}' フォルダに保存しました！")
    print("Next Step: この画像をRoboflow等にアップロードしてアノテーションを行ってください。")

# 実行コマンド
if __name__ == "__main__":
    extract_frames(INPUT_VIDEO_PATH, OUTPUT_FRAMES_DIR, interval_frames=15)
```
