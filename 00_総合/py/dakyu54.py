from datetime import date
from email.mime import image
import os
from pydoc import text
from textwrap import fill
from turtle import color, speed
from unittest import runner
import cv2
from matplotlib.pylab import f
import numpy as np
import csv
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
2025-1
coords = []  # coordsの定義

N=800

# 球種と表示色の定義
pitch_types = {
    '4-seam (1)': (0, 0, 255),         # ストレート（赤）
    '2-seam (2)': (0, 128, 255),       # ツーシーム（オレンジ）
    'RCutter (3)': (128, 0, 255),      # カットボール(右)（紫）
    'LCutter (4)': (255, 0, 128),      # カットボール(左)（ピンク）
    'RSlider (5)': (0, 255, 0),        # スライダー(右)（緑）
    'LSlider (6)': (0, 255, 128),      # スライダー(左)（黄緑）
    'RCurve (7)': (255, 0, 0),         # カーブ(右)（青）
    'LCurve (8)': (128, 128, 0),       # カーブ(左)（オリーブ）
    'SFF (9)': (0, 255, 255),          # SFF/フォーク（シアン）
    'Changeup (10)': (255, 255, 0),    # チェンジアップ（黄色）
    'Etc (11)': (100, 100, 100)        # その他（灰色）
}

# 打球質とマークの定義
hit_types = {
    'Grounder (g)': 'o',
    'Liner (l)': 'x',
    'Fly (f)': '△'
}

# 球種変換辞書
pitch_type_mapping = {
    'ストレート': '4-seam (1)',
    'ツーシーム': '2-seam (2)',
    'カットボール(右)': 'RCutter (3)',
    'カットボール(左)': 'LCutter (4)',
    'スライダー(右)': 'RSlider (5)',
    'スライダー(左)': 'LSlider (6)',
    'カーブ(右)': 'RCurve (7)',
    'カーブ(左)': 'LCurve (8)',
    'SFF': 'SFF (9)',
    'フォーク': 'SFF (9)',
    'チェンジアップ': 'Changeup (10)'
}

# 打球質変換辞書
hit_type_mapping = {
    'ゴロ': 'Grounder (g)',
    'ライナー': 'Liner (l)',
    'フライ': 'Fly (f)'
}

zone_image = np.ones((N, N, 3), np.uint8) * 255

display_pitch_type = None
display_hit_type = None

# ユーザー名とCSVパスの設定
def get_valid_username():
    # 1. スクリプトがある場所を取得 (例: .../h0riy/baseball)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. 「OneDrive - Hiroshima University」フォルダの場所を特定する
    # スクリプトの場所から「OneDrive - Hiroshima University」という文字列を探して切り出す
    keyword = "OneDrive - Hiroshima University"
    if keyword in current_dir:
        base_onedrive = current_dir.split(keyword)[0] + keyword
    else:
        # 見つからない場合はユーザーフォルダから推測
        base_onedrive = os.path.join(os.path.expanduser("~"), keyword)

    # 3. 共有フォルダの名前のリスト（可能性のあるものを並べる）
    # あなたの環境と、共有相手の環境の両方に対応させます
    possible_subdirs = [
        "野球/打球方向",                                      # あなたの環境
        "堀　大和 さんのファイル - 野球/打球方向",           # 共有相手の環境
        "堀 大和 さんのファイル - 野球/打球方向"            # 全角スペース違いなどの予備
    ]

    csv_dir = None
    for subdir in possible_subdirs:
        temp_path = os.path.join(base_onedrive, subdir)
        if os.path.exists(temp_path):
            csv_dir = temp_path
            break

    # 4. 万が一見つからない場合は、今の階層から1つ上で探す（予備）
    if not csv_dir:
        parent_dir = os.path.dirname(current_dir) # h0riy の階層
        for d in os.listdir(parent_dir):
            if "野球" in d or "打球方向" in d:
                target = os.path.join(parent_dir, d)
                if os.path.isdir(target):
                    csv_dir = target # その中に「打球方向」があればさらに潜る処理が必要ですが一旦これ
                    break

    if not csv_dir:
        print(f"【確認】OneDriveルート: {base_onedrive}")
        csv_dir = input("フォルダが見つかりません。パスを直接貼り付けてください: ")

    while True:
        username = input("解析したい選手名を入力してください: ")
        csv_file = os.path.join(csv_dir, f"{username}.csv")
        if os.path.exists(csv_file):
            print(f"成功: {csv_file} を読み込みます。")
            return username, csv_file
        else:
            print(f"エラー: {username}.csv が見つかりません。")

# CSVからデータ読み込み
def load_data(csv_file):
    if os.path.exists(csv_file):
        # UTF-8 (BOM付き)でファイルを開く
        with open(csv_file, mode='r', newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # 空の値をスキップ
                if not row["batted_ball_x"] or not row["batted_ball_y"]:
                    continue
                
                # 座標のスケーリング
                x, y = float(row["batted_ball_x"]) * N, float(row["batted_ball_y"]) * N
                
                # 球種の変換またはそのまま使用
                raw_pitch_type = row["pitched_ball_type"]
                if raw_pitch_type in pitch_types:
                    pitch_type = raw_pitch_type  # 英語表記が既にある場合
                else:
                    pitch_type = pitch_type_mapping.get(raw_pitch_type, 'Etc (11)')  # 該当なしは 'Etc (11)'
                
                # 打球質の変換またはそのまま使用
                raw_hit_type = row["batted_ball_type"]
                if raw_hit_type in hit_types:
                    hit_type = raw_hit_type  # 英語表記が既にある場合
                else:
                    hit_type = hit_type_mapping.get(raw_hit_type, 'Unknown')  # 該当なしは 'Unknown'
                
                # 投手名、球場、投げた座標、球速、塁状況、日付、カウント
                pitcher_name = row["pitcher_name"]
                stadium = row["stadium_name"]
                px,py = float(row["pitched_ball_x"])*400+110,float(row["pitched_ball_y"])*400+110
                if not row["pitched_ball_speed"]:
                    speed = 0
                else:
                    speed = float(row["pitched_ball_speed"])
                if not row["runners"]:
                    runners = "---"
                else:
                    runners = row["runners"]
                date_str = row["game_date"].replace("-", "/")  # ハイフンをスラッシュに統一
                date = datetime.strptime(date_str, "%Y/%m/%d").date()
                ball = int(row["ball"])
                strike = int(row["strike"])
                out = int(row["out"])
                result= row["result_of_pa"]
                if row["bunt"]=="1":
                    bunt= True
                else:
                    bunt= False
                    
                if row["batter_stand"]=="2":
                    stand= "右"
                elif row["batter_stand"]=="1":
                    stand= "左"
                else:
                    stand= "両"

                coords.append({"position": (int(x), int(y)), "pitched_ball_type": pitch_type, "batted_ball_type": hit_type,"pn": pitcher_name,"std":stadium, "pipo":(int(px),int(py)), "spe":speed, "runners":runners, "date":date,"count":(ball,strike,out),"result":result,"bunt":bunt,"stand":stand})
        
        
        print(f"{len(coords)}件のデータを読み込みました。")
        global original_coords
        original_coords= coords.copy()  # 元の座標を保存

# ダイヤモンドの位置とスケーリング
offset_y = N/16
shift_y = N/4
scale_factor = 0.6
diamond_coords = np.array([(N/2, N/80*15 + shift_y), (N/80*65, N/2 + shift_y), (N/2, N/80*65 + shift_y), (N/80*15, N/2 + shift_y)], np.int32).reshape((-1, 1, 2))
diamond_coords = (diamond_coords - N/2) * scale_factor + N/2
diamond_coords[:, :, 1] += offset_y

# ベジェ曲線を描く関数の定義
def draw_bezier_curve(img, start_point, end_point, control_point, num_points=N/40, color=(0, 0, 0), thickness=2):
    points = []
    for t in np.linspace(0, 1, int(num_points)):
        # 二次ベジェ曲線の式
        x = (1 - t)**2 * start_point[0] + 2 * (1 - t) * t * control_point[0] + t**2 * end_point[0]
        y = (1 - t)**2 * start_point[1] + 2 * (1 - t) * t * control_point[1] + t**2 * end_point[1]
        points.append((int(x), int(y)))
    
    # 曲線を描画
    for i in range(len(points) - 1):
        cv2.line(img, points[i], points[i + 1], color, thickness)

# 野球場のフィールドライン描画関数
def draw_field_lines(image, extension_factor=2.7):
    cv2.polylines(image, [diamond_coords.astype(np.int32)], isClosed=True, color=(0, 0, 0), thickness=2)
    cv2.line(image, tuple(diamond_coords[0][0].astype(int)), tuple(diamond_coords[2][0].astype(int)), (0, 0, 0), 1)
    cv2.line(image, tuple(diamond_coords[3][0].astype(int)), tuple(diamond_coords[1][0].astype(int)), (0, 0, 0), 1)
    
    # 二塁、三塁、一塁の座標
    second_base = tuple(diamond_coords[2][0].astype(int))
    first_base = tuple(diamond_coords[1][0].astype(int))
    third_base = tuple(diamond_coords[3][0].astype(int))
    
    # 延長線の終点の計算
    first_base_extension = (int(second_base[0] + (first_base[0] - second_base[0]) * extension_factor),
                            int(second_base[1] + (first_base[1] - second_base[1]) * extension_factor))
    third_base_extension = (int(second_base[0] + (third_base[0] - second_base[0]) * extension_factor),
                            int(second_base[1] + (third_base[1] - second_base[1]) * extension_factor))
    
    circle_positions = [
        (N/2, N/4),#センター
        (N/80*65, N/80*30), #ライト
        (N/80*15, N/80*30), #レフト
        (N/80*25, N/800*525),#サード
        (N/800*325, N/80*45), #ショート
        (N/800*475, N/80*45), #セカンド
        (N/80*55, N/800*525), #ファースト
    ]
    
    # フィールドラインの延長線を描画
    cv2.line(image, second_base, first_base_extension, (0, 0, 0), 1)
    cv2.line(image, second_base, third_base_extension, (0, 0, 0), 1)
    
    # コントロールポイントを設定（少しずらしてカーブを作る）
    control_point = ((first_base_extension[0] + third_base_extension[0]) // 2,
                     (first_base_extension[1] + third_base_extension[1]) // 2 - 500)
    
    # ベジェ曲線を描画
    draw_bezier_curve(image, first_base_extension, third_base_extension, control_point)
    
    mask = np.ones_like(image, dtype=np.uint8) * 255  # マスク作成
    for cx, cy in circle_positions:
        cv2.circle(mask, (int(cx), int(cy)), 25, (128, 128, 128), -1)  # 黒色でくり抜く
    
    image[:] = cv2.bitwise_and(image, mask)  # くり抜き適用

# ピッチゾーンの描画関数
def draw_pitch_lines(image,extention_factor=2.7,line_color=(0,0,0),thickness=1):
    a=130
    b=a+400
    big_top_left = (a,a)
    big_bottom_right = (b,b)

    cv2.rectangle(image,big_top_left,big_bottom_right,line_color,thickness)

    cell_size=80
    c=a+cell_size*2
    for i in range(1,5):
        x=i*cell_size
        cv2.line(image,(x+a,a+cell_size),(x+a,b-cell_size),line_color,thickness)

    for i in range(1,5):
        y=i*cell_size
        cv2.line(image,(a+cell_size,y+a),(b-cell_size,y+a),line_color,thickness)
    
    cv2.line(image,(c+15,b+15),(c+15,b+40),line_color,thickness)
    cv2.line(image,(c+65,b+15),(c+65,b+40),line_color,thickness)
    cv2.line(image,(c+15,b+15),(c+65,b+15),line_color,thickness)
    cv2.line(image,(c+15,b+40),(c+40,b+65),line_color,thickness)
    cv2.line(image,(c+65,b+40),(c+40,b+65),line_color,thickness)

# 情報表示関数
def display_info(image):
    y0, dy = N/40, N/40
    x_pitch1 = N/80    # 1列目の表示位置
    x_pitch2 = N/80*12  # 2列目の表示位置
    x_pitch3 = N/80*23

    # 球種を二列に分けて表示
    for i, (pitch, color) in enumerate(pitch_types.items()):
        # 球種情報を前半の列に表示
        if i < len(pitch_types) // 2:
            y = y0 + i * dy
            cv2.putText(image, pitch, (int(x_pitch1), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)
        # 球種情報を後半の列に表示
        else:
            y = y0 + (i - len(pitch_types) // 2) * dy
            cv2.putText(image, pitch, (int(x_pitch2), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

    # 打球質の情報はそのまま表示
    for j, (hit, symbol) in enumerate(hit_types.items()):
        y = y0 + j * dy
        cv2.putText(image, f"{hit}: {symbol}", (int(x_pitch3),int (y)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

def reset_and_redraw(csv_file):
    global zone_image
    if not coords:
        print("coordsは空です。適切なデータがありません。")
        return
    zone_image = np.ones((N, N, 3), np.uint8) * 255
    draw_field_lines(zone_image)
    display_info(zone_image)

    # ファイル名の表示
    display_filename(zone_image,csv_file)

    # **ここで既存データを再描画**
    redraw_existing_data()
    cv2.imshow("Zone Image", zone_image)

# 日本語対応のファイル名を表示する関数
def display_filename(image, csv_file):
    # coordsが空かどうか確認
    if coords:
        stand = coords[0]["stand"]
        # その他の処理...
    else:
        print("coordsは空です。適切なデータがありません。")
        return

    file_basename = os.path.basename(csv_file)  # フルファイル名を取得
    file_name_without_extension = os.path.splitext(file_basename)[0]  # 拡張子を削除

    font_path = "C:/Windows/Fonts/msgothic.ttc"  # 日本語対応フォントのパス（Windowsの場合）
    font_size = N/40

    # OpenCVの画像をPillow形式に変換
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(image_pil)

    # フォントを設定
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"フォントが見つかりません: {font_path}")
        return
    
    stand= coords[0]["stand"]
    # テキストを描画
    text_position = (N/80*55, N/80)  # 描画位置
    text_color = (0, 0, 0)  # 黒色
    draw.text(text_position, f"{file_name_without_extension} {stand}", font=font, fill=text_color)

    # Pillow画像をOpenCV形式に戻す
    image[:] = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

# キーボードイベントで球種のフィルターを変更
def change_type(key,csv_file):
    global display_pitch_type
    pitch_keys = {
        ord('1'): '4-seam (1)', ord('2'): '2-seam (2)', ord('3'): 'RCutter (3)',
        ord('4'): 'LCutter (4)', ord('5'): 'RSlider (5)', ord('6'): 'LSlider (6)',
        ord('7'): 'RCurve (7)', ord('8'): 'LCurve (8)', ord('9'): 'SFF (9)',
        ord('0'): 'Changeup (10)', ord('-'): 'Etc (11)'
    }
    if key in pitch_keys:
        if display_pitch_type == pitch_keys[key]:
            display_pitch_type = None  # 同じ球種の場合、フィルター解除
            print(f"フィルター解除: 全ての球種を表示")
        else:
            display_pitch_type = pitch_keys[key]  # 新しい球種を設定
            print(f"フィルター設定: {display_pitch_type}")
        reset_and_redraw(csv_file)  # フィルターに基づいて再描画
    else:
        print(f"無効なキー入力: {chr(key)}")
        
# 打球質のフィルター
def change_hit_type(key,csv_file):
    global display_hit_type
    hit_keys = {
        ord('g'):'Grounder',ord('l'):'Liner',ord('f'):'Fly'
    }
    if key in hit_keys:
        if display_hit_type == hit_keys[key]:
            display_hit_type = None  # 同じ球種の場合、フィルター解除
            print(f"フィルター解除: 全ての打球を表示")
        else:
            display_hit_type = hit_keys[key]  # 新しい球種を設定
            print(f"フィルター設定: {display_hit_type}")
        reset_and_redraw(csv_file)  # フィルターに基づいて再描画
    else:
        print(f"無効なキー入力: {chr(key)}")
    

# 記録済みデータの再描画
def redraw_existing_data():
    global display_pitch_type, display_hit_type
    for coord in coords:
        if display_pitch_type and coord.get("pitched_ball_type") != display_pitch_type:
            continue  # 選択された球種のみ描画
        if display_hit_type and not coord.get("batted_ball_type", "").startswith(display_hit_type):
            continue
        x, y = coord["position"]
        color = pitch_types.get(coord.get("pitched_ball_type", "Etc (11)"), (N/8, N/8, N/8))
        hit_symbol = hit_types.get(coord.get("batted_ball_type", "Unknown"), 'o')  # デフォルトを設定
        if hit_symbol == 'o':
            cv2.circle(zone_image, (x, y), 8, color, -1)
        elif hit_symbol == 'x':
            cv2.line(zone_image, (x - 8, y - 8), (x + 8, y + 8), color, 2)
            cv2.line(zone_image, (x + 8, y - 8), (x - 8, y + 8), color, 2)
        elif hit_symbol == '△':
            triangle_cnt = np.array([(x, y - 8), (x - 8, y + 8), (x + 8, y + 8)])
            cv2.drawContours(zone_image, [triangle_cnt], 0, color, -1)

def on_mouse_click(event, x, y, flags, param):
    global zone_image
    if event == cv2.EVENT_LBUTTONDOWN:
        for coord in coords:
            bx, by = coord["position"]
            color = pitch_types.get(coord.get("pitched_ball_type", "Etc (11)"), (N/8, N/8, N/8))
            if (x - bx) ** 2 + (y - by) ** 2 <= 25:  # 半径5の円内にある場合
                show_details_window(
                    coord["date"],
                    coord["std"],
                    coord["pn"],
                    coord["count"],
                    coord["runners"],
                    coord["pipo"],
                    coord["spe"],
                    coord["result"],
                    coord["bunt"],
                    color
                )
                break

def show_details_window(date, stadium, pitcher_name, count, runners, position, speed, result,bunt ,color):
    # 白い背景画像を作成
    details_image = np.ones((600, 600, 3), np.uint8) * 255

    x, y = position
    cv2.circle(details_image, (int(x), int(y)), 15, color, -1)

    # 日本語フォントの設定
    font_path = "C:/Windows/Fonts/msgothic.ttc"  # Windows用フォントパス
    font_size = 15  # フォントサイズ
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"フォントが見つかりません: {font_path}")
        return

    # PillowのImageオブジェクトに変換
    pil_image = Image.fromarray(cv2.cvtColor(details_image, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_image)

    info_texts = [
        f"日付: {date}  球場: {stadium}",
        f"投手名: {pitcher_name}",
        f"BSO・塁状況: {count, runners}",
        f"球速: {speed} km/h",
        f"結果: {result}",
        f"バント:{'bunt' if bunt else '非バント'}"
    ]

    # テキストを描画
    for i, text in enumerate(info_texts):
        draw.text((10, 10 + i * 30), text, font=font, fill=(0, 0, 0))  # 黒色で描画

    # Pillow画像をOpenCV形式に変換
    details_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # ピッチラインを描画
    draw_pitch_lines(details_image, line_color=(0, 0, 0), thickness=1)

    # ウィンドウ名
    window_name = "Details"

    # ウィンドウを表示
    cv2.imshow(window_name, details_image)

    try:
        # イベントループでウィンドウの状態を監視
        while True:
            # ウィンドウが閉じられた場合、ループを終了
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                print("ウィンドウが閉じられました。")
                break

            # 遅延を追加して描画を安定化
            cv2.waitKey(1)

    except cv2.error as e:
        print(f"OpenCVエラー: {e}")

    finally:
        # ウィンドウがまだ存在する場合のみ破棄
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1:
            cv2.destroyWindow(window_name)

def filter_data_by_date(start_date, end_date):
    global coords, original_coords
    coords = [coord for coord in original_coords if start_date <= coord["date"] <= end_date]
    print(f"{len(coords)}件のデータが期間内に絞り込まれました。")
    
def filter_data_by_speed(min_speed, max_speed):
    global coords, original_coords
    coords = [coord for coord in original_coords if min_speed <= coord["spe"] <= max_speed]
    print(f"{len(coords)}件のデータが速度範囲内に絞り込まれました。")

def main():
    global coords, original_coords
    # ユーザー名とCSVファイルの確認
    username, csv_file = get_valid_username()

    # CSVデータの読み込み
    print(f"CSVデータを読み込みます: {csv_file}")
    load_data(csv_file)

    # 初期状態の描画
    reset_and_redraw(csv_file)

    # マウスイベントの設定
    cv2.setMouseCallback("Zone Image", on_mouse_click)

    # キーイベントとウィンドウの状態を監視
    while True:
        key = cv2.waitKey(1) & 0xFF  # キー入力を監視

        # OpenCVウィンドウが閉じられた場合も終了
        if cv2.getWindowProperty("Zone Image", cv2.WND_PROP_VISIBLE) < 1:
            print("ウィンドウが閉じられました。終了します。")
            break

        # 有効なキーか確認して処理
        if key in [
            ord('1'), ord('2'), ord('3'), ord('4'),
            ord('5'), ord('6'), ord('7'), ord('8'),
            ord('9'), ord('0'), ord('-')
        ]:
            change_type(key, csv_file)
        elif key in [ord('g'), ord('l'), ord('f')]:
            change_hit_type(key, csv_file)

        elif key == ord('d'):
            while True:
                try:
                    start = input("開始日を入力してください (例: 2024-01-01): ")
                    start_date = datetime.strptime(start, "%Y-%m-%d").date()
                    end = input("終了日を入力してください (例: 2024-12-31): ")
                    end_date = datetime.strptime(end, "%Y-%m-%d").date()
                    break  # 成功したらループを抜ける
                except ValueError:
                    print("日付の形式が正しくありません。例の通りに入力してください！")
            
            filter_data_by_date(start_date, end_date)
            
            if len(coords) == 0:
                print("この期間にはデータがありません。元に戻します。")
                coords = original_coords.copy()
            reset_and_redraw(csv_file)
        
        elif key == ord('r'):
            print("フィルターを解除して全データを表示します。")
            coords = original_coords.copy()  # 元に戻す
            reset_and_redraw(csv_file)       # 再描画
        
        elif key == ord('s'):
            while True:
                try:
                    min_speed = float(input("最小球速を入力してください (例: 120.0): "))
                    max_speed = float(input("最大球速を入力してください (例: 160.0): "))
                    break  # 成功したらループを抜ける
                except ValueError:
                    print("数値の形式が正しくありません。例の通りに入力してください！")
            
            filter_data_by_speed(min_speed, max_speed)
            
            if len(coords) == 0:
                print("この速度範囲にはデータがありません。元に戻します。")
                coords = original_coords.copy()
            reset_and_redraw(csv_file)
            
        elif key == ord('q'):
            print("アプリケーションを終了します。")
            break


        elif key != 255:  # 無効なキーの場合（255は何も押されていない状態）
            print("無効なキー入力")

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()


