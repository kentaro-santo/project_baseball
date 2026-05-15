from ultralytics import YOLO

# 【ここを書き換えてください】ステップ2で作成した動画のパスを貼り付けます
INPUT_VIDEO_PATH = '/content/drive/MyDrive/output_preprocessed.mp4'

def run_baseline_test(video_path):
    model = YOLO('yolov8n.pt')
    print(f"Running inference on {video_path}...")
    results = model.predict(source=video_path, save=True, classes=[32], conf=0.15)
    print("Baseline test complete. Colabの 'runs/detect/predict' フォルダ内に推論結果の動画が保存されています。")

if __name__ == "__main__":
    run_baseline_test(INPUT_VIDEO_PATH)
