# ステップ2: 映像データの準備と軽量化（前処理）

iPhoneで撮影した動画をColabで扱うため、まずはGoogle Driveを連携（マウント）します。
動画をGoogle Driveにアップロードしておき、そのパスを指定して読み込みます。

## やること
1. あなたのGoogle Driveのどこかに、iPhoneで撮影した動画ファイル（例: `sample.MOV`）をアップロードします。
2. Colabの左側にある **「フォルダのアイコン（ファイル）」** をクリックします。
3. 以下のコードを実行すると、Google Driveのフォルダが見えるようになります。
4. `drive/MyDrive/...` の中からアップロードした動画を探し、右クリックして **「パスをコピー」** します。
5. コード内の `INPUT_VIDEO_PATH = '...'` の部分にコピーしたパスを貼り付けて実行します。

## 実行するコード

```python
from google.colab import drive
import cv2
import os

# 1. Google Driveをマウント（連携）します
# ※実行すると「Googleドライブにアクセスすることを許可しますか？」と聞かれるので許可してください
drive.mount('/content/drive')

# 2. 【ここを書き換えてください】
# Colabの左側フォルダ一覧から動画を右クリックし、「パスをコピー」して以下の '' 内に貼り付けます
INPUT_VIDEO_PATH = '/content/drive/MyDrive/sample.MOV'

# 3. 軽量化後の動画の保存先パス（同じくドライブ内に保存されます）
OUTPUT_VIDEO_PATH = '/content/drive/MyDrive/output_preprocessed.mp4'

def resize_and_trim_video(input_path, output_path, target_width=1280, skip_frames=2):
    print("動画の軽量化を開始します...")
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"エラー: {input_path} が読み込めません。パスが正しいか確認してください。")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    target_height = int(orig_height * (target_width / orig_width))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_fps = fps / skip_frames
    out = cv2.VideoWriter(output_path, fourcc, out_fps, (target_width, target_height))

    frame_count = 0
    print(f"処理中: 元サイズ {orig_width}x{orig_height} ({fps} FPS)")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % skip_frames == 0:
            resized_frame = cv2.resize(frame, (target_width, target_height))
            out.write(resized_frame)
        frame_count += 1

    cap.release()
    out.release()
    print(f"軽量化が完了しました！新しい動画が保存されました: {output_path}")

# プログラムの実行
if __name__ == "__main__":
    resize_and_trim_video(INPUT_VIDEO_PATH, OUTPUT_VIDEO_PATH, target_width=1280, skip_frames=2)
```
