from ultralytics import YOLO

# 【ここを書き換えてください】Roboflow等からダウンロードしたデータセットの data.yaml のパス
DATA_YAML_PATH = '/content/drive/MyDrive/dataset/data.yaml'

def train_custom_model(data_yaml_path):
    model = YOLO('yolov8n.pt')
    print("Start training custom YOLO model for baseball tracking...")
    results = model.train(
        data=data_yaml_path,
        epochs=50,
        imgsz=640,
        batch=16,
        project='/content/drive/MyDrive/baseball_tracker',
        name='yolov8_custom',
        device=0
    )
    print("Training complete! 学習済みモデルはドライブ内の 'baseball_tracker/yolov8_custom/weights/best.pt' に保存されています。")

if __name__ == "__main__":
    train_custom_model(DATA_YAML_PATH)
