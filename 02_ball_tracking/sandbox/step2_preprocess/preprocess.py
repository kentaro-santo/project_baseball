from google.colab import drive
import cv2
import os

# 1. Google Driveをマウント（連携）します
drive.mount('/content/drive')

# 2. 【ここを書き換えてください】
# Colabの左側メニューから、ドライブ内の動画を探して右クリック -> 「パスをコピー」し、以下に貼り付けます。
INPUT_VIDEO_PATH = '/content/drive/MyDrive/sample.MOV'

# 3. 軽量化後の動画の保存先パス
OUTPUT_VIDEO_PATH = '/content/drive/MyDrive/output_preprocessed.mp4'

def resize_and_trim_video(input_path, output_path, target_width=1280, skip_frames=2):
    print(f"入力ファイル: {input_path}")
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Error: 動画ファイルを読み込めません。パスを確認してください。")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    target_height = int(orig_height * (target_width / orig_width))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_fps = fps / skip_frames
    out = cv2.VideoWriter(output_path, fourcc, out_fps, (target_width, target_height))

    frame_count = 0
    print(f"Processing video: {orig_width}x{orig_height} at {fps} FPS")
    
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
    print(f"Preprocessed video saved to {output_path} ({target_width}x{target_height} at {out_fps} FPS)")

if __name__ == "__main__":
    resize_and_trim_video(INPUT_VIDEO_PATH, OUTPUT_VIDEO_PATH, target_width=1280, skip_frames=2)
