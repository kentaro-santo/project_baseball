from ultralytics import YOLO

# 【ここを書き換えてください】
# 1. ステップ2の動画パス
INPUT_VIDEO_PATH = '/content/drive/MyDrive/output_preprocessed.mp4'
# 2. ステップ5で学習したモデル(best.pt)のパス
CUSTOM_WEIGHTS_PATH = '/content/drive/MyDrive/baseball_tracker/yolov8_custom/weights/best.pt'

def track_baseball(video_path, custom_weights_path):
    model = YOLO(custom_weights_path)
    print(f"Tracking object in {video_path}...")
    
    results = model.track(
        source=video_path,
        tracker="bytetrack.yaml",
        conf=0.3,
        save=True,
        project='/content/drive/MyDrive/baseball_tracker',
        name='tracking_results'
    )
    print("Tracking complete! トラッキング結果の動画はドライブ内の 'baseball_tracker/tracking_results' に保存されています。")

if __name__ == "__main__":
    track_baseball(INPUT_VIDEO_PATH, CUSTOM_WEIGHTS_PATH)
