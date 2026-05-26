import pandas as pd
import tkinter as tk
from tkinter import filedialog
import sys
import unicodedata
import re

def get_pitcher_team(row):
    if '表' in str(row['イニング']):
        return row['後攻チーム']
    elif '裏' in str(row['イニング']):
        return row['先攻チーム']
    return '不明'

# --- 対戦相手のチームを取得する関数 ---
def get_opponent_team(row):
    if '表' in str(row['イニング']):
        return row['先攻チーム'] 
    elif '裏' in str(row['イニング']):
        return row['後攻チーム'] 
    return '不明'

# --- イニング文字列から「X回」を抽出する関数 ---
def get_inning_num(inning_str):
    m = re.search(r'\d+', str(inning_str))
    return f"{m.group()}回" if m else inning_str

# --- 文字幅を計算して綺麗に揃えるための関数 ---
def get_display_width(text):
    width = 0
    for char in str(text):
        if unicodedata.east_asian_width(char) in ['F', 'W', 'A']:
            width += 2
        else:
            width += 1
    return width

def rjust_text(text, width):
    text = str(text)
    pad = width - get_display_width(text)
    return ' ' * max(0, pad) + text

def center_text(text, width):
    text = str(text)
    pad = width - get_display_width(text)
    left_pad = pad // 2
    right_pad = pad - left_pad
    return ' ' * left_pad + text + ' ' * right_pad
# ---------------------------------------------

# --- 指標計算を共通化した関数 ---
def calc_metrics(group):
    total_pitches = len(group)
    if total_pitches == 0:
        return None
        
    non_strike_results = ['ボール', '死球', '四球']
    strike_pitches = group['結果'].apply(lambda x: x not in non_strike_results).sum()
    strike_rate_overall = (strike_pitches / total_pitches) * 100
    
    first_pitches = group[(group['B'].astype(str) == '0') & (group['S'].astype(str) == '0')]
    fps_count = len(first_pitches)
    fps_strikes = first_pitches['結果'].apply(lambda x: x not in non_strike_results).sum()
    fps_rate = (fps_strikes / fps_count * 100) if fps_count > 0 else 0
    
    count_at_least_3_pitches = 0
    count_2_strikes_by_3rd_pitch = 0
    
    for pa_id, pa_data in group.groupby('PA_ID'):
        if len(pa_data) >= 3:
            count_at_least_3_pitches += 1
            s_before_3 = str(pa_data.iloc[2]['S'])
            
            if s_before_3 == '2':
                count_2_strikes_by_3rd_pitch += 1
            else:
                if len(pa_data) >= 4:
                    s_after_3 = str(pa_data.iloc[3]['S'])
                    if s_after_3 == '2':
                        count_2_strikes_by_3rd_pitch += 1
                else:
                    res3 = pa_data.iloc[2]['結果']
                    if '三振' in str(res3):
                        count_2_strikes_by_3rd_pitch += 1

    two_strike_rate = (count_2_strikes_by_3rd_pitch / count_at_least_3_pitches * 100) if count_at_least_3_pitches > 0 else 0

    return {
        '初球S率': f"{fps_rate:.1f}% ({fps_strikes}/{fps_count})",
        '3球目2S率': f"{two_strike_rate:.1f}% ({count_2_strikes_by_3rd_pitch}/{count_at_least_3_pitches})",
        '全体S率': f"{strike_rate_overall:.1f}% ({strike_pitches}/{total_pitches})"
    }
# ---------------------------------------------

def main():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    file_path = filedialog.askopenfilename(
        title="分析するCSVファイルを選択してください",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    
    if not file_path:
        print("ファイルの選択がキャンセルされました。")
        sys.exit()

    print(f"読み込み中: {file_path}")

    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='shift_jis')

    df.columns = df.columns.str.strip()
    
    # 日付列の取得
    date_col_name = '不明'
    for col in ['日付', '試合日', 'Date']:
        if col in df.columns:
            date_col_name = col
            break
            
    if date_col_name != '不明':
        df['試合日付'] = df[date_col_name].astype(str).str.strip()
    else:
        df['試合日付'] = '不明(列なし)'

    clean_cols = ['結果', '投手', '先攻チーム', '後攻チーム', 'イニング']
    for col in clean_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df['投手チーム'] = df.apply(get_pitcher_team, axis=1)
    df['対戦相手'] = df.apply(get_opponent_team, axis=1)
    df['イニング数'] = df['イニング'].apply(get_inning_num)

    df['is_new_pa'] = ((df['B'].astype(str) == '0') & (df['S'].astype(str) == '0')).astype(int)
    if df['is_new_pa'].sum() == 0:
         df['is_new_pa'] = ((df['B'] == 0) & (df['S'] == 0)).astype(int)
    df['PA_ID'] = df['is_new_pa'].cumsum()

    results_list = []

    for (team, pitcher), group in df.groupby(['投手チーム', '投手']):
        if len(group) == 0:
            continue
            
        match_date = group['試合日付'].iloc[0]
        opponent = group['対戦相手'].iloc[0]
            
        overall_metrics = calc_metrics(group)
        if overall_metrics:
            overall_metrics.update({
                '日付': match_date,
                'チーム': team, 
                '投手': pitcher,
                '対戦相手': opponent,
                'イニング': '全体'
            })
            results_list.append(overall_metrics)
            
        innings = group['イニング数'].unique()
        for inning in innings:
            inning_group = group[group['イニング数'] == inning]
            inning_metrics = calc_metrics(inning_group)
            if inning_metrics:
                inning_metrics.update({
                    '日付': match_date,
                    'チーム': team, 
                    '投手': pitcher, 
                    '対戦相手': opponent,
                    'イニング': inning
                })
                results_list.append(inning_metrics)

    result_df = pd.DataFrame(results_list)

    # --- 出力部分 ---
    print(f"\n{'='*70}")
    print(f"投手別ストライク指標（全体・イニング別）")
    print(f"{'='*70}\n")
    
    # チームごとに表示
    for team, team_df in result_df.groupby('チーム'):
        # チーム単位で日付と対戦相手を取得
        m_date = team_df['日付'].iloc[0]
        opp = team_df['対戦相手'].iloc[0]
        
        # チーム名（例：【広島大学】）の横に表示するよう変更
        print(f"【{team}】  (日付: {m_date} / 対戦相手: {opp})")
        
        for pitcher, pitcher_df in team_df.groupby('投手', sort=False):
            # 投手名の横からは削除し、名前だけ表示
            print(f"  投手: {pitcher}")
            
            display_df = pitcher_df[['イニング', '初球S率', '3球目2S率', '全体S率']].reset_index(drop=True)
            cols = display_df.columns
            
            widths = {col: max(get_display_width(col), display_df[col].apply(get_display_width).max()) + 2 for col in cols}
            
            header = "".join([center_text(col, widths[col]) for col in cols])
            print("   " + header)
            
            for _, row in display_df.iterrows():
                line = "".join([rjust_text(row[col], widths[col]) for col in cols])
                print("   " + line)
                
            print()
            
        print("-" * 70)

if __name__ == "__main__":
    main()