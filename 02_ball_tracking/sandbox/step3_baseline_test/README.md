# ステップ3: 既存のAIでボールがどこまで見えるかテストしよう

## やること
先ほどと同じように、パスを変数で指定して実行します。
ステップ2で作った軽量化動画（`output_preprocessed.mp4`）のパスを指定してください。

## 実行するコード

```python
from ultralytics import YOLO

# 【ここを書き換えてください】ステップ2で作成した動画のパスを貼り付けます
# （例： '/content/drive/MyDrive/output_preprocessed.mp4' ）
INPUT_VIDEO_PATH = '/content/drive/MyDrive/output_preprocessed.mp4'

# 学習済みの標準モデルを呼び出します
model = YOLO('yolov8n.pt')

print("AIが動画の中のボールを探しています...")

# テスト推論の実行
results = model.predict(
    source=INPUT_VIDEO_PATH, 
    save=True,       # 結果を動画として保存する
    classes=[32],    # ボールだけを探す
    conf=0.15
)

print("テストが完了しました！")
print("Colabの左側のフォルダ一覧から [runs] -> [detect] -> [predict] フォルダを開くと、結果の動画が入っています。")
```
