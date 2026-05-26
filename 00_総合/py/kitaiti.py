import pandas as pd
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def main():
    initial_dir = r"C:\Users\hori\OneDrive - Hiroshima University\野球\バッティングデータ"

    print("CSVファイルを選択してください...")

    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = askopenfilename(
        initialdir=initial_dir,
        filetypes=[("CSV files", "*.csv")],
        title="CSVファイルを選択"
    )

    if not file_path or not os.path.isfile(file_path):
        print("ファイルが選択されなかったか、存在しません。")
        return

    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        print("CSVファイルが正常に読み込まれました。")
    except Exception as e:
        print(f"CSVファイルの読み込み中にエラーが発生しました: {e}")
        return

    # イニング単位でグループ化
    grouped = df.groupby(["game_date", "hteam_name", "vteam_name", "top_bottom", "inning"])

    # 結果格納用辞書 {(アウト数, ランナー状態): [失点合計, イニング数]}
    results = {}

    for _, group in grouped:
        total_runs = group["runs_against"].sum()

        # イニング中に出現したすべての（アウト数, ランナー状態）を抽出
        for _, row in group.iterrows():
            out = int(row["out"]) if pd.notna(row["out"]) else 0
            if out > 3:
                continue
            runners = str(row["runners"]) if pd.notna(row["runners"]) else ""
            key = (out, runners)

            if key not in results:
                results[key] = [0, 0]

        # 重複を避けて一度だけイニング数カウント・失点を加算
        seen_states = set((int(r["out"]) if pd.notna(r["out"]) else 0,
                           str(r["runners"]) if pd.notna(r["runners"]) else "") for _, r in group.iterrows())
        for key in seen_states:
            results[key][0] += total_runs  # その状態で起こったイニングの失点を加算
            results[key][1] += 1           # 出現イニング数を加算
            
    results = {key: val for key, val in results.items() if key[0] < 3}


    # 出力
    filename = os.path.splitext(os.path.basename(file_path))[0]
    print(f"\n--- {filename} ---\n")
    for (out, runners), (runs, count) in sorted(results.items()):
        # ランナー状態のラベル作成
        if runners == "":
            runner_label = f"0塁"
        else:
            runner_label = f"{runners}塁"

        if count > 0:
            print(f"{out}死{runner_label}：{runs}/{count} -> {runs / count:.2f}点")
        else:
            print(f"{out}死{runner_label}：データなし")


if __name__ == "__main__":
    main()
