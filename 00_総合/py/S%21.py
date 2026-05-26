from logging import root
import os
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def calculate_strike_stats(data):
    if 'pitched_result' in data.columns:
        swinging_strikes = data[(data['pitched_result'] == '空振りストライク') | (data['pitched_result'].isna()) | (data['pitched_result'] == '打撃結果')].shape[0]
        called_strikes = data[data['pitched_result'] == '見逃しストライク'].shape[0]
        foul_balls = data[data['pitched_result'] == 'ファウル'].shape[0]
        balls = data[data['pitched_result'] == 'ボール'].shape[0]

        total_strikes = called_strikes + swinging_strikes + foul_balls

        return {
            'total_pitches': data.shape[0],
            'called_strikes': called_strikes,
            'swinging_strikes': swinging_strikes,
            'foul_balls': foul_balls,
            'balls': balls,
            'total_strikes': total_strikes,
            'strike_percentage': (total_strikes / (total_strikes + balls)) * 100 if (total_strikes + balls) > 0 else 0
        }
    else:
        print(f"カラム 'pitched_result' が見つかりませんでした。")
        return None

def main():
    print("野球データ分析アプリへようこそ！")
    
    initial_dir = r"C:\Users\hori\OneDrive - Hiroshima University\野球\試合データのcsv"
    while True:
        print("CSVファイルを選択してください...")
        
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        file_path = askopenfilename(
            initialdir=initial_dir,
            filetypes=[("CSV files", "*.csv")],
            title="CSVファイルを選択"
        )
        
        # キャンセルされた場合、プログラムを終了
        if not file_path:
            print("ファイルが選択されませんでした。プログラムを終了します。")
            return  # プログラム全体を終了

        # ファイルの存在確認
        if not os.path.isfile(file_path):
            print("指定されたファイルが存在しません。")
            continue

        # CSVファイルをUTF-8(BOM付き)として読み込み
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            print("CSVファイルが正常に読み込まれました。")
        except Exception as e:
            print(f"CSVファイルの読み込み中にエラーが発生しました: {e}")
            continue

        if file_path.lower() == 'exit':
            print("アプリケーションを終了します。")
            break

        if not os.path.exists(file_path):
            print(f"ファイルが見つかりません: {file_path}")
            continue

        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == '.xlsx':
                df = pd.read_excel(file_path, engine='openpyxl')
            elif file_extension == '.csv':
                df = pd.read_csv(file_path)
            else:
                print(f"サポートされていないファイル形式です: {file_extension}")
                continue
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            continue

        while True:
            pitcher_name = input("投手の名前を入力してください (終了する場合は 'exit' と入力): ").strip()
            
            if pitcher_name.lower() == 'exit':
                break

            pitcher_data = df[df['pitcher_name'] == pitcher_name]

            # 全体のストライク率
            all_pitch_stats = calculate_strike_stats(pitcher_data)
            if all_pitch_stats:
                print(f"\n投手 {pitcher_name} の全体の総投球数: {all_pitch_stats['total_pitches']}")
                print(f"投手 {pitcher_name} の全体のストライク率: {all_pitch_stats['strike_percentage']:.2f}%")

            # ストレートと非ストレートで分けて計算
            straight_data = pitcher_data[pitcher_data['pitched_ball_type'] == 'ストレート']
            non_straight_data = pitcher_data[pitcher_data['pitched_ball_type'] != 'ストレート']

            straight_stats = calculate_strike_stats(straight_data)
            non_straight_stats = calculate_strike_stats(non_straight_data)

            # ストレートの結果
            if straight_stats:
                print(f"\n投手 {pitcher_name} のストレートの総投球数: {straight_stats['total_pitches']}")
                print(f"投手 {pitcher_name} のストレートのボール数: {straight_stats['balls']}")
                print(f"投手 {pitcher_name} のストレートの総ストライク数: {straight_stats['total_strikes']}")
                print(f"投手 {pitcher_name} のストレートのストライク率: {straight_stats['strike_percentage']:.2f}%")

            # 非ストレートの結果
            if non_straight_stats:
                print(f"\n投手 {pitcher_name} の非ストレートの総投球数: {non_straight_stats['total_pitches']}")
                print(f"投手 {pitcher_name} の非ストレートのボール数: {non_straight_stats['balls']}")
                print(f"投手 {pitcher_name} の非ストレートの総ストライク数: {non_straight_stats['total_strikes']}")
                print(f"投手 {pitcher_name} の非ストレートのストライク率: {non_straight_stats['strike_percentage']:.2f}%")

if __name__ == "__main__":
    main()
