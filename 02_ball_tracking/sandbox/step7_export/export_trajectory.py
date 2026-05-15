from ultralytics import YOLO
import csv

# 【ここを書き換えてください】
INPUT_VIDEO_PATH = '/content/drive/MyDrive/output_preprocessed.mp4'
CUSTOM_WEIGHTS_PATH = '/content/drive/MyDrive/baseball_tracker/yolov8_custom/weights/best.pt'
OUTPUT_CSV_PATH = '/content/drive/MyDrive/ball_trajectory.csv'

def export_trajectory_to_csv(video_path, custom_weights_path, output_csv):
    model = YOLO(custom_weights_path)
    print(f"Extracting trajectory data from {video_path}...")
    results = model.track(source=video_path, tracker="bytetrack.yaml", stream=True, conf=0.3)

    with open(output_csv, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["frame_index", "track_id", "x_center", "y_center", "width", "height", "confidence"])
        
        frame_idx = 0
        for r in results:
            boxes = r.boxes
            if boxes is not None and boxes.id is not None:
                for box, track_id, conf in zip(boxes.xywh, boxes.id, boxes.conf):
                    x, y, w, h = box.tolist()
                    writer.writerow([frame_idx, int(track_id), round(x, 2), round(y, 2), round(w, 2), round(h, 2), round(float(conf), 3)])
            frame_idx += 1

    print(f"Trajectory data exported to {output_csv}")

if __name__ == "__main__":
    export_trajectory_to_csv(INPUT_VIDEO_PATH, CUSTOM_WEIGHTS_PATH, OUTPUT_CSV_PATH)
