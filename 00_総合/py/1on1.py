import streamlit as st
import pandas as pd
import datetime
import os
import time
import glob
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as mpath
from streamlit_drawable_canvas import st_canvas
import plotly.graph_objects as go
from matplotlib.lines import Line2D

# --- 設定: 日本語フォント (Matplotlib用) ---
import platform
system = platform.system()
if system == 'Windows':
    plt.rcParams['font.family'] = 'MS Gothic'
elif system == 'Darwin':
    plt.rcParams['font.family'] = 'AppleGothic'

# --- 保存先ディレクトリを探す関数 ---
def get_save_directory():
    user_home = os.path.expanduser("~")
    keyword = "OneDrive - Hiroshima University"
    onedrive_path = os.path.join(user_home, keyword)
    if not os.path.exists(onedrive_path):
        current_dir = os.getcwd()
        if keyword in current_dir:
            onedrive_path = current_dir.split(keyword)[0] + keyword
    
    if os.path.exists(onedrive_path):
        target_dir = os.path.join(onedrive_path, "野球", "05-07", "1on1")
    else:
        target_dir = os.path.join(user_home, "Desktop", "1on1_Data")

    if not os.path.exists(target_dir):
        try:
            os.makedirs(target_dir)
        except:
            return None     
    return target_dir

SAVE_DIR = get_save_directory()

# ==========================================
#  データ読み込み機能
# ==========================================
def load_data_from_file(file_path):
    if not file_path or not os.path.exists(file_path):
        return []
    try:
        if os.path.getsize(file_path) == 0: return []
        df = pd.read_csv(file_path)
        if df.empty or len(df.columns) == 0: return []
        df = df.where(pd.notnull(df), None)
        return df.to_dict('records')
    except: return []

# ==========================================
#  選手リスト管理
# ==========================================
PLAYERS_FILE = os.path.join(SAVE_DIR, "players.json") if SAVE_DIR else "players.json"

def load_players():
    default_data = {"pitchers": {"投手A": "右"}, "batters": {"打者A": "右"}}
    if os.path.exists(PLAYERS_FILE):
        try:
            with open(PLAYERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return default_data

def save_players(pitchers_dict, batters_dict):
    data = {"pitchers": pitchers_dict, "batters": batters_dict}
    try:
        with open(PLAYERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except: pass

# --- 定数 ---
PITCH_TYPES = ["ストレート", "ツーシーム", "カットボール", "スライダー", "カーブ", "SFF/フォーク", "チェンジアップ", "シンカー", "シュート", "その他"]
PITCH_COLORS = {
    'ストレート': 'red', 'ツーシーム': 'gray', 'カットボール': 'purple', 'スライダー': 'green', 
    'カーブ': 'gold', 'SFF/フォーク': 'hotpink', 'チェンジアップ': 'blue', 
    'シンカー': 'bisque', 'シュート': 'bisque', 'その他': 'black'
}
BTN_TAKE, BTN_SWING, BTN_FOUL, BTN_INPLAY = "見逃し", "空振り", "ファウル", "インプレー"
HIT_TYPES = ["ゴロ", "フライ", "ライナー", "バント"]
RESULT_CATEGORIES_UI = ["凡打", "安打"]

# 点の半径（サイズ）を統一
POINT_RADIUS = 10 

# --- 初期設定 ---
st.set_page_config(page_title="1on1 Recorder", layout="wide")

# --- ゾーン計算・描画 ---
def calculate_zone(x, y, canvas_size):
    scale = canvas_size / 300
    SZ_START, SZ_SIZE, GRID_STEP = 50 * scale, 200 * scale, (200/3) * scale
    if x < SZ_START or x > SZ_START+SZ_SIZE or y < SZ_START or y > SZ_START+SZ_SIZE:
        center = SZ_START + SZ_SIZE / 2
        if x < center and y < center: return 11
        elif x >= center and y < center: return 12
        elif x < center and y >= center: return 13
        else: return 14
    col = int((x - SZ_START) // GRID_STEP)
    row = int((y - SZ_START) // GRID_STEP)
    return (min(max(row, 0), 2) * 3) + (min(max(col, 0), 2) + 1)

def get_zone_drawing(canvas_size):
    scale = canvas_size / 300
    SZ_START, SZ_SIZE, GRID_STEP = 50 * scale, 200 * scale, (200/3) * scale
    objects = [
        {"type": "rect", "left": SZ_START, "top": SZ_START, "width": SZ_SIZE, "height": SZ_SIZE, "stroke": "#000", "strokeWidth": 4, "fill": "transparent", "selectable": False},
        {"type": "line", "x1": SZ_START+GRID_STEP, "y1": SZ_START, "x2": SZ_START+GRID_STEP, "y2": SZ_START+SZ_SIZE, "stroke": "#555", "strokeWidth": 2},
        {"type": "line", "x1": SZ_START+GRID_STEP*2, "y1": SZ_START, "x2": SZ_START+GRID_STEP*2, "y2": SZ_START+SZ_SIZE, "stroke": "#555", "strokeWidth": 2},
        {"type": "line", "x1": SZ_START, "y1": SZ_START+GRID_STEP, "x2": SZ_START+SZ_SIZE, "y2": SZ_START+GRID_STEP, "stroke": "#555", "strokeWidth": 2},
        {"type": "line", "x1": SZ_START, "y1": SZ_START+GRID_STEP*2, "x2": SZ_START+SZ_SIZE, "y2": SZ_START+GRID_STEP*2, "stroke": "#555", "strokeWidth": 2},
    ]
    return {"version": "4.4.0", "objects": objects}

def get_field_drawing(canvas_size):
    s = canvas_size / 300
    HOME, FIRST, SECOND, THIRD = (150*s, 250*s), (230*s, 170*s), (150*s, 90*s), (70*s, 170*s)
    objects = [
        {"type": "path", "path": f"M 0 {100*s} Q {150*s} {-80*s} {300*s} {100*s} L {300*s} {300*s} L 0 {300*s} Z", "fill": "#E8F5E9", "selectable": False},
        {"type": "path", "path": f"M {HOME[0]} {HOME[1]} L {FIRST[0]} {FIRST[1]} L {SECOND[0]} {SECOND[1]} L {THIRD[0]} {THIRD[1]} Z", "fill": "#F9E79F", "stroke": "#795548", "strokeWidth": 2, "selectable": False},
        {"type": "line", "x1": HOME[0], "y1": HOME[1], "x2": 0, "y2": 100*s, "stroke": "white", "strokeWidth": 2},
        {"type": "line", "x1": HOME[0], "y1": HOME[1], "x2": 300*s, "y2": 100*s, "stroke": "white", "strokeWidth": 2},
    ]
    return {"version": "4.4.0", "objects": objects}

def calculate_count_state(log_list):
    b, s = 0, 0
    for log in log_list:
        res = str(log["結果"])
        if any(k in res for k in ["四球", "三振", "安打", "凡打", "犠打", "失策", "併殺"]): b, s = 0, 0
        else:
            j = str(log["判定"])
            if "ボール" in j: b += 1
            elif "ストライク" in j: s += 1
            elif "ファウル" in j: 
                if s < 2: s += 1
    return b, s

def update_count_from_logs():
    if st.session_state.get('force_reset_count'):
        st.session_state.count = {"B": 0, "S": 0}
        st.session_state.force_reset_count = False 
        return
    if "logs" in st.session_state and st.session_state.logs:
        b, s = calculate_count_state(st.session_state.logs)
        st.session_state.count = {"B": b, "S": s}
    else:
        st.session_state.count = {"B": 0, "S": 0}

# ==========================================
#  Input Page
# ==========================================
def render_input_page(target_file_path):
    st.markdown("""
        <style>
        iframe[title="streamlit_drawable_canvas.st_canvas"] {
            touch-action: none;
        }
        div[data-testid="column"] button p {
            font-size: 14px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    top_col1, top_col2 = st.columns([1.5, 1], gap="large")

    with top_col1:
        st.header("📝 記録モード")
        file_name = os.path.basename(target_file_path)
        if file_name == f"{datetime.date.today()}_1on1.csv":
            st.caption(f"📂 記録先: **今日 ({file_name})**")
        else:
            st.warning(f"📂 記録先: **過去のファイル ({file_name})** に追記します")

        update_count_from_logs()
        count_container = st.container()

    with top_col2:
        st.markdown("##### 👤 対戦設定")
        p_list = list(st.session_state.pitchers.keys()) if st.session_state.pitchers else ["未登録"]
        b_list = list(st.session_state.batters.keys()) if st.session_state.batters else ["未登録"]
        current_pitcher = st.radio("ピッチャー", p_list, horizontal=True, key="main_sel_p")
        current_batter = st.radio("バッター", b_list, horizontal=True, key="main_sel_b")
        current_pitcher_hand = st.session_state.pitchers.get(current_pitcher, "右")
        current_batter_hand = st.session_state.batters.get(current_batter, "右")
        st.caption(f"⚾ {current_pitcher}({current_pitcher_hand}) vs {current_batter}({current_batter_hand})")

    current_pitch_count = 0
    if "logs" in st.session_state and st.session_state.logs:
        current_pitch_count = len([l for l in st.session_state.logs if l["投手"] == current_pitcher])

    with count_container:
        cc1, cc2, cc3, cc4 = st.columns([1, 1, 1, 1]) 
        cc1.metric("BALL", st.session_state.count["B"])
        cc2.metric("STRIKE", st.session_state.count["S"])
        cc3.metric("Pitch Count", f"{current_pitch_count} 球")
        with cc4:
            st.write("") 
            if st.button("リセット", help="カウントを0-0にします"):
                st.session_state.force_reset_count = True
                st.rerun()

    st.markdown("---")

    is_editing = st.session_state.edit_index is not None
    if is_editing:
        st.warning(f"⚠️ [修正モード] No.{st.session_state.edit_index + 1}")
        if st.button("修正キャンセル"):
            st.session_state.edit_index, st.session_state.edit_data = None, {}
            st.session_state.speed_buffer = ""
            st.session_state.key_zone += 1
            st.session_state.input_judgment = "未選択" 
            st.session_state.temp_zone_point = None
            st.session_state.temp_field_point = None
            st.rerun()

    if "input_judgment" not in st.session_state: st.session_state.input_judgment = "未選択"

    c1, c2, c3, c4 = st.columns([0.6, 0.6, 0.9, 1.9], gap="small")

    with c1:
        st.subheader("① 球種")
        default_p = PITCH_TYPES.index(st.session_state.edit_data.get("球種")) if is_editing and st.session_state.edit_data.get("球種") in PITCH_TYPES else 0
        pitch_type = st.radio("球種を選択", PITCH_TYPES, index=default_p, label_visibility="collapsed")
        selected_color = PITCH_COLORS.get(pitch_type, "red")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.write("📝 メモ")
        memo_input = st.text_input("メモ", value=st.session_state.edit_data.get("詳細メモ", ""), label_visibility="collapsed")

    with c2:
        st.subheader("② 球速")
        if is_editing and st.session_state.speed_buffer == "" and "球速" in st.session_state.edit_data:
            st.session_state.speed_buffer = str(int(st.session_state.edit_data["球速"]))
        
        st.markdown(f"<h2 style='text-align: center;'>{st.session_state.speed_buffer or '---'} <span style='font-size: 0.6em;'>km/h</span></h2>", unsafe_allow_html=True)
        
        k_cols = st.columns(3)
        def add_n(n): 
            if len(st.session_state.speed_buffer) < 3: st.session_state.speed_buffer += n
        nums = ["7","8","9","4","5","6","1","2","3","0"]
        for i, n in enumerate(nums):
            if k_cols[i%3].button(n, key=f"btn{n}", width="stretch"): add_n(n); st.rerun()
        if k_cols[1].button("C", key="btnc", width="stretch"): st.session_state.speed_buffer = ""; st.rerun()
        if k_cols[2].button("BS", key="btnb", width="stretch"): st.session_state.speed_buffer = st.session_state.speed_buffer[:-1]; st.rerun()

    with c3:
        st.subheader("③ コース")
        C_SIZE = 300 
        zone_draw = get_zone_drawing(C_SIZE)
        
        if "temp_zone_point" not in st.session_state: 
            st.session_state.temp_zone_point = None

        if is_editing and st.session_state.temp_zone_point is None and st.session_state.edit_data.get("ZoneX"):
             scale = C_SIZE / st.session_state.edit_data.get("canvas_size_used", 300)
             cx = st.session_state.edit_data["ZoneX"] * scale
             cy = st.session_state.edit_data["ZoneY"] * scale
             st.session_state.temp_zone_point = {"cx": cx, "cy": cy}

        if st.session_state.temp_zone_point and "cx" not in st.session_state.temp_zone_point:
             st.session_state.temp_zone_point = {
                 "cx": st.session_state.temp_zone_point.get("left", 0) + POINT_RADIUS,
                 "cy": st.session_state.temp_zone_point.get("top", 0) + POINT_RADIUS
             }

        if st.session_state.temp_zone_point:
             cx = st.session_state.temp_zone_point["cx"]
             cy = st.session_state.temp_zone_point["cy"]
             zone_draw["objects"].append({
                 "type": "circle", "left": cx, "top": cy, 
                 "originX": "center", "originY": "center",
                 "radius": POINT_RADIUS, "fill": selected_color, "selectable": False
             })

        canvas_zone = st_canvas(
            fill_color=selected_color, 
            stroke_width=0, 
            background_color="#f0f2f6", 
            initial_drawing=zone_draw, 
            update_streamlit=True, 
            height=C_SIZE, width=C_SIZE, 
            drawing_mode="point", 
            point_display_radius=POINT_RADIUS,
            key=f"z_{st.session_state.key_zone}", 
            display_toolbar=False
        )
        
        click_x, click_y, zone_val = -1, -1, 99
        if canvas_zone.json_data and canvas_zone.json_data["objects"]:
            circles = [obj for obj in canvas_zone.json_data["objects"] if obj.get("type") == "circle"]
            if circles:
                last = circles[-1]
                
                orig_x = last.get("originX", "left")
                orig_y = last.get("originY", "top")
                r = last.get("radius", POINT_RADIUS)
                
                new_cx = last["left"] if orig_x == "center" else last["left"] + r
                new_cy = last["top"] if orig_y == "center" else last["top"] + r
                
                is_new = True
                if st.session_state.temp_zone_point:
                    old_cx = st.session_state.temp_zone_point["cx"]
                    old_cy = st.session_state.temp_zone_point["cy"]
                    if abs(new_cx - old_cx) < 0.1 and abs(new_cy - old_cy) < 0.1: 
                        is_new = False
                
                if is_new:
                    st.session_state.temp_zone_point = {"cx": new_cx, "cy": new_cy}
                    st.session_state.key_zone += 1 
                    st.rerun()

        if st.session_state.temp_zone_point:
            click_x = st.session_state.temp_zone_point["cx"]
            click_y = st.session_state.temp_zone_point["cy"]
            zone_val = calculate_zone(click_x, click_y, C_SIZE)

    with c4:
        st.subheader("④ 判定")
        if is_editing and "loaded_edit_judge" not in st.session_state:
            j = st.session_state.edit_data.get("判定")
            if "ファウル" in j: st.session_state.input_judgment = BTN_FOUL
            elif "インプレー" in j: st.session_state.input_judgment = BTN_INPLAY
            elif "空振り" in j: st.session_state.input_judgment = BTN_SWING
            elif "見逃し" in j or "ボール" in j: st.session_state.input_judgment = BTN_TAKE
            st.session_state.loaded_edit_judge = True

        jc1, jc2 = st.columns([0.7, 1.3], gap="small")
        
        fx, fy, hit_type, in_play_res = -1, -1, "", ""

        with jc1:
            if st.button(BTN_TAKE, key="j_take", type="primary" if st.session_state.input_judgment == BTN_TAKE else "secondary", width="stretch"):
                st.session_state.input_judgment = BTN_TAKE; st.rerun()
            if st.button(BTN_SWING, key="j_swing", type="primary" if st.session_state.input_judgment == BTN_SWING else "secondary", width="stretch"):
                st.session_state.input_judgment = BTN_SWING; st.rerun()
            if st.button(BTN_FOUL, key="j_foul", type="primary" if st.session_state.input_judgment == BTN_FOUL else "secondary", width="stretch"):
                st.session_state.input_judgment = BTN_FOUL; st.rerun()
            if st.button(BTN_INPLAY, key="j_inplay", type="primary" if st.session_state.input_judgment == BTN_INPLAY else "secondary", width="stretch"):
                st.session_state.input_judgment = BTN_INPLAY; st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            record_btn = st.button("🔥 保存", type="primary", width="stretch", key="btn_record")

        with jc2:
            if st.session_state.input_judgment in [BTN_INPLAY, BTN_FOUL]:
                if st.session_state.input_judgment == BTN_INPLAY:
                    ip1, ip2 = st.columns([1, 1.2])
                    in_play_res = ip1.radio("結果", RESULT_CATEGORIES_UI, horizontal=True, label_visibility="collapsed")
                    hit_type = ip2.selectbox("打球", HIT_TYPES, label_visibility="collapsed")
                else:
                    st.caption("ファウル位置")

                F_SIZE = 280
                f_draw = get_field_drawing(F_SIZE)
                
                if "temp_field_point" not in st.session_state: st.session_state.temp_field_point = None
                
                if is_editing and st.session_state.temp_field_point is None and st.session_state.edit_data.get("打球X"):
                     s = F_SIZE / 280
                     cx_f = st.session_state.edit_data["打球X"] * s
                     cy_f = st.session_state.edit_data["打球Y"] * s
                     st.session_state.temp_field_point = {"cx": cx_f, "cy": cy_f}

                if st.session_state.temp_field_point and "cx" not in st.session_state.temp_field_point:
                     st.session_state.temp_field_point = {
                         "cx": st.session_state.temp_field_point.get("left", 0) + POINT_RADIUS,
                         "cy": st.session_state.temp_field_point.get("top", 0) + POINT_RADIUS
                     }

                if st.session_state.temp_field_point:
                     cx_f = st.session_state.temp_field_point["cx"]
                     cy_f = st.session_state.temp_field_point["cy"]
                     f_draw["objects"].append({
                         "type": "circle", "left": cx_f, "top": cy_f, 
                         "originX": "center", "originY": "center",
                         "radius": POINT_RADIUS, "fill": "blue", "selectable": False
                     })

                canvas_field = st_canvas(
                    fill_color="blue", stroke_width=0,
                    background_color="#4CAF50", initial_drawing=f_draw, update_streamlit=True,
                    height=F_SIZE, width=F_SIZE, drawing_mode="point", 
                    point_display_radius=POINT_RADIUS, 
                    key=f"f_{st.session_state.key_field}", display_toolbar=False
                )
                
                if canvas_field.json_data and canvas_field.json_data["objects"]:
                    circles_f = [obj for obj in canvas_field.json_data["objects"] if obj.get("type") == "circle"]
                    if circles_f:
                        last_f = circles_f[-1]
                        
                        orig_x_f = last_f.get("originX", "left")
                        orig_y_f = last_f.get("originY", "top")
                        r_f = last_f.get("radius", POINT_RADIUS)
                        
                        new_cx_f = last_f["left"] if orig_x_f == "center" else last_f["left"] + r_f
                        new_cy_f = last_f["top"] if orig_y_f == "center" else last_f["top"] + r_f
                        
                        is_new_f = True
                        if st.session_state.temp_field_point:
                            old_cx_f = st.session_state.temp_field_point["cx"]
                            old_cy_f = st.session_state.temp_field_point["cy"]
                            if abs(new_cx_f - old_cx_f) < 0.1 and abs(new_cy_f - old_cy_f) < 0.1: 
                                is_new_f = False
                        
                        if is_new_f:
                            st.session_state.temp_field_point = {"cx": new_cx_f, "cy": new_cy_f}
                            st.session_state.key_field += 1
                            st.rerun()
                
                if st.session_state.temp_field_point:
                    fx = st.session_state.temp_field_point["cx"]
                    fy = st.session_state.temp_field_point["cy"]
            else:
                st.empty()

        if record_btn:
            if click_x == -1 or st.session_state.input_judgment == "未選択":
                st.error("⚠️ 保存できません。「③コース」と「④判定」の両方を必ず入力してください。")
            else:
                save_judge, final_res = "", ""
                sel_j = st.session_state.input_judgment
                if sel_j == BTN_TAKE:
                    if zone_val <= 9: save_judge, final_res = "ストライク(見逃し)", "ストライク(見逃し)"
                    else: save_judge, final_res = "ボール", "ボール"
                elif sel_j == BTN_SWING: save_judge, final_res = "ストライク(空振り)", "ストライク(空振り)"
                elif sel_j == BTN_FOUL: save_judge, final_res = "ファウル", "ファウル"
                elif sel_j == BTN_INPLAY: save_judge, final_res = "インプレー", f"{in_play_res}({hit_type})"

                rec_time = st.session_state.edit_data["日時"] if is_editing else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                prev_b, prev_s = st.session_state.count["B"], st.session_state.count["S"]
                if is_editing:
                    prev_logs = st.session_state.logs[:st.session_state.edit_index]
                    prev_b, prev_s = calculate_count_state(prev_logs)

                count_str = f"{prev_b}-{prev_s}"
                next_b, next_s = prev_b, prev_s
                if "ボール" in save_judge:
                    next_b += 1
                    if next_b >= 4: final_res = "四球"
                elif "ストライク" in save_judge:
                    next_s += 1
                    if next_s >= 3: final_res = "三振"

                log = {
                    "日時": rec_time,
                    "投手": current_pitcher, "投球腕": st.session_state.pitchers[current_pitcher],
                    "打者": current_batter, "打席": st.session_state.batters[current_batter],
                    "球種": pitch_type, "球速": int(st.session_state.speed_buffer or 0),
                    "Zone": zone_val, "ZoneX": round(click_x, 1), "ZoneY": round(click_y, 1),
                    "判定": save_judge, "結果区分": in_play_res if sel_j == BTN_INPLAY else "",
                    "打球タイプ": hit_type, "打球X": round(fx, 1), "打球Y": round(fy, 1),
                    "詳細メモ": memo_input, "結果": final_res, "カウント": count_str,
                    "canvas_size_used": C_SIZE
                }

                if is_editing:
                    old_b = st.session_state.edit_data["打者"]
                    st.session_state.logs[st.session_state.edit_index] = log
                    if current_batter != old_b:
                        for i in range(st.session_state.edit_index+1, len(st.session_state.logs)):
                            if st.session_state.logs[i]["カウント"] == "0-0": break
                            st.session_state.logs[i]["打者"] = current_batter
                            st.session_state.logs[i]["打席"] = st.session_state.batters[current_batter]
                else:
                    st.session_state.logs.append(log)

                if SAVE_DIR: pd.DataFrame(st.session_state.logs).to_csv(target_file_path, index=False, encoding='utf-8-sig')

                st.session_state.key_zone += 1
                st.session_state.key_field += 1
                st.session_state.speed_buffer = ""
                st.session_state.edit_index = None
                st.session_state.temp_zone_point = None
                st.session_state.temp_field_point = None
                if "loaded_edit_judge" in st.session_state: del st.session_state.loaded_edit_judge
                st.session_state.input_judgment = "未選択"
                st.rerun()

    # --- 履歴管理 ---
    st.markdown("---")
    st.markdown("###### 📋 履歴")
    if st.session_state.logs:
        df_l = pd.DataFrame(st.session_state.logs)
        df_l.insert(0, "選", False)
        ed_df = st.data_editor(df_l.iloc[::-1], hide_index=True, width="stretch",
                               column_config={"選": st.column_config.CheckboxColumn(width="small"), "球速": st.column_config.NumberColumn(format="%d")})
        
        sel = ed_df[ed_df["選"] == True]
        if not sel.empty:
            target_time = sel.iloc[0]["日時"]
            real_idx = next((i for i, x in enumerate(st.session_state.logs) if x["日時"] == target_time), None)
            
            if real_idx is not None:
                c_btn1, c_btn2 = st.columns(2)
                if c_btn1.button("修正"):
                    st.session_state.edit_index = real_idx
                    st.session_state.edit_data = st.session_state.logs[real_idx]
                    st.session_state.speed_buffer = ""
                    st.session_state.temp_zone_point = None
                    st.session_state.temp_field_point = None
                    if "loaded_edit_judge" in st.session_state: del st.session_state.loaded_edit_judge
                    st.rerun()
                if c_btn2.button("削除"):
                    st.session_state.logs.pop(real_idx)
                    if not st.session_state.logs:
                        if os.path.exists(target_file_path): os.remove(target_file_path)
                    else:
                        if SAVE_DIR: pd.DataFrame(st.session_state.logs).to_csv(target_file_path, index=False, encoding='utf-8-sig')
                    st.rerun()

# ==========================================
#  Analysis Page (分析ページ)
# ==========================================
def render_analysis_page():
    st.header("📈 分析モード")
    all_files = glob.glob(os.path.join(SAVE_DIR, "*.csv"))
    if not all_files: st.warning("データがありません"); return
    
    df_list = []
    for f in all_files:
        try:
            if os.path.getsize(f) == 0: continue
            tmp = pd.read_csv(f)
            if tmp.empty or len(tmp.columns) == 0: continue
            df_list.append(tmp)
        except Exception: pass
            
    if not df_list: st.warning("有効なデータが見つかりません (すべてのファイルが空か破損している可能性があります)"); return

    try: df_all = pd.concat(df_list, ignore_index=True)
    except Exception as e: st.error(f"データの結合に失敗しました: {e}"); return

    df_all["Date_obj"] = pd.to_datetime(df_all["日時"], format='mixed', errors='coerce').dt.date
    df_all = df_all.dropna(subset=["Date_obj"])

    if df_all.empty: st.warning("表示できる有効なデータがありません"); return

    df_all = df_all.sort_values("日時", ascending=True).reset_index(drop=True)
    recalc_counts = []
    b, s = 0, 0
    for _, row in df_all.iterrows():
        recalc_counts.append(f"{b}-{s}")
        res = str(row["結果"])
        judge = str(row["判定"])
        if any(k in res for k in ["四球", "三振", "安打", "凡打", "犠打", "失策", "併殺"]): b, s = 0, 0
        else:
            if "ボール" in judge: b += 1
            elif "ストライク" in judge: s += 1
            elif "ファウル" in judge:
                if s < 2: s += 1
    df_all["Calculated_Count"] = recalc_counts

    st.sidebar.subheader("🔍 フィルター")
    min_date = df_all["Date_obj"].min()
    max_date = df_all["Date_obj"].max()
    if pd.isna(min_date) or pd.isna(max_date): st.warning("日付データが不正です"); return

    date_range = st.sidebar.date_input("期間 (開始日 - 終了日)", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    pitcher_list = ["All"] + sorted(df_all["投手"].dropna().unique().tolist())
    batter_list = ["All"] + sorted(df_all["打者"].dropna().unique().tolist())
    pitch_type_list = sorted(df_all["球種"].dropna().unique().tolist())
    
    sel_p = st.sidebar.selectbox("投手を選択", pitcher_list)
    sel_b = st.sidebar.selectbox("打者を選択", batter_list)
    
    with st.sidebar.expander("⚾ 球種フィルター", expanded=True):
        sel_pt = []
        for pt in pitch_type_list:
            if st.checkbox(pt, value=True, key=f"chk_pt_{pt}"):
                sel_pt.append(pt)
    
    filtered_df = df_all.copy()
    if isinstance(date_range, tuple):
        if len(date_range) == 2: filtered_df = filtered_df[(filtered_df["Date_obj"] >= date_range[0]) & (filtered_df["Date_obj"] <= date_range[1])]
        elif len(date_range) == 1: filtered_df = filtered_df[filtered_df["Date_obj"] == date_range[0]]
    elif isinstance(date_range, datetime.date): filtered_df = filtered_df[filtered_df["Date_obj"] == date_range]

    if sel_p != "All": filtered_df = filtered_df[filtered_df["投手"] == sel_p]
    if sel_b != "All": filtered_df = filtered_df[filtered_df["打者"] == sel_b]
    
    if sel_pt: filtered_df = filtered_df[filtered_df["球種"].isin(sel_pt)]
    else: filtered_df = filtered_df[filtered_df["球種"].isin([])]

    filtered_df = filtered_df.drop(columns=["Date_obj"])

    t1, t2, t3 = st.tabs(["🎯 投手", "🏟️ 打者", "📋 データ一覧"])
    
    with t1:
        header_text = f"👤 投手: {sel_p}" if sel_p != "All" else "👤 投手データ (全選手)"
        st.markdown(f"## {header_text}")
        
        b_hand_filter = st.radio("打者の左右で絞り込み", ["All", "右", "左"], horizontal=True, key="p_tab_b_hand")
        df_p_view = filtered_df.copy()
        if b_hand_filter != "All":
            df_p_view = df_p_view[df_p_view["打席"] == b_hand_filter]

        if df_p_view.empty or "ZoneX" not in df_p_view.columns:
            st.info("条件に合う投球データがありません")
        else:
            p_c1, p_c2 = st.columns([1.5, 1], gap="large")
            with p_c1:
                st.markdown("### 🎯 投球チャート")
                fig_pitch = go.Figure()
                
                fig_pitch.add_shape(type="rect", x0=0, y0=0, x1=450, y1=450, fillcolor="#f0f2f6", layer="below", line_width=0)
                fig_pitch.add_shape(type="rect", x0=0, y0=0, x1=450, y1=450, line=dict(color="black", width=2))
                
                sz_start = 75
                sz_size = 300
                step = 100
                
                fig_pitch.add_shape(type="rect", x0=sz_start, y0=sz_start, x1=sz_start+sz_size, y1=sz_start+sz_size, line=dict(color="black", width=3))
                
                fig_pitch.add_shape(type="line", x0=sz_start+step, y0=sz_start, x1=sz_start+step, y1=sz_start+sz_size, line=dict(color="black", width=1))
                fig_pitch.add_shape(type="line", x0=sz_start+2*step, y0=sz_start, x1=sz_start+2*step, y1=sz_start+sz_size, line=dict(color="black", width=1))
                fig_pitch.add_shape(type="line", x0=sz_start, y0=sz_start+step, x1=sz_start+sz_size, y1=sz_start+step, line=dict(color="black", width=1))
                fig_pitch.add_shape(type="line", x0=sz_start, y0=sz_start+2*step, x1=sz_start+sz_size, y1=sz_start+2*step, line=dict(color="black", width=1))
                
                center = 225
                fig_pitch.add_shape(type="line", x0=center, y0=0, x1=center, y1=sz_start, line=dict(color="gray", width=1.5, dash="dash"))
                fig_pitch.add_shape(type="line", x0=center, y0=sz_start+sz_size, x1=center, y1=450, line=dict(color="gray", width=1.5, dash="dash"))
                fig_pitch.add_shape(type="line", x0=0, y0=center, x1=sz_start, y1=center, line=dict(color="gray", width=1.5, dash="dash"))
                fig_pitch.add_shape(type="line", x0=sz_start+sz_size, y0=center, x1=450, y1=center, line=dict(color="gray", width=1.5, dash="dash"))

                valid_plots = df_p_view[df_p_view["ZoneX"] != -1]
                
                for pt in valid_plots["球種"].unique():
                    sub = valid_plots[valid_plots["球種"] == pt]
                    if sub.empty: continue
                    
                    adj_x = sub["ZoneX"] * (450 / sub["canvas_size_used"])
                    adj_y = sub["ZoneY"] * (450 / sub["canvas_size_used"])
                    
                    fig_pitch.add_trace(go.Scatter(
                        x=adj_x, y=adj_y,
                        mode='markers',
                        marker=dict(size=14, color=PITCH_COLORS.get(pt, 'bisque'), line=dict(width=1, color='white')),
                        name=pt,
                        text=[f"<b>{row['球種']}</b><br>{row['球速']}km/h<br>{row['判定']}" for _, row in sub.iterrows()],
                        hoverinfo="text",
                        customdata=sub.index
                    ))

                fig_pitch.update_layout(
                    xaxis=dict(range=[0, 450], showgrid=False, zeroline=False, visible=False),
                    yaxis=dict(range=[0, 450], showgrid=False, zeroline=False, visible=False, autorange="reversed", scaleanchor="x", scaleratio=1),
                    height=450, 
                    margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                
                event = st.plotly_chart(fig_pitch, on_select="rerun", selection_mode="points", use_container_width=True)
                
                if event and event.selection and event.selection["points"]:
                    selected_indices = [p["customdata"] for p in event.selection["points"]]
                    if selected_indices:
                        st.markdown("#### 🔍 選択された投球の詳細")
                        selected_rows = df_p_view.loc[selected_indices]
                        disp_cols = ["日時", "投手", "打者", "球種", "球速", "判定", "結果", "詳細メモ"]
                        st.dataframe(selected_rows[disp_cols], hide_index=True)

            with p_c2:
                st.markdown("### 📊 投手スタッツ")
                df_sorted = df_p_view.sort_values("日時", ascending=True).reset_index(drop=True)
                first_pitches = df_sorted[df_sorted["Calculated_Count"] == "0-0"]
                first_pitch_strikes = first_pitches[first_pitches["判定"] != "ボール"]
                fp_s_count = len(first_pitch_strikes)
                fp_total = len(first_pitches)
                
                ab_ids = (df_sorted["Calculated_Count"] == "0-0").cumsum()
                df_sorted["AB_ID"] = ab_ids
                ahead_count = 0
                total_cases = 0 
                for ab_id, group in df_sorted.groupby("AB_ID"):
                    if group.iloc[0]["Calculated_Count"] != "0-0": continue
                    if len(group) >= 4:
                        total_cases += 1
                        pitch_4_count = group.iloc[3]["Calculated_Count"]
                        if pitch_4_count in ["0-2", "1-2"]: ahead_count += 1
                
                m_c1, m_c2 = st.columns(2)
                fp_rate = fp_s_count / fp_total if fp_total > 0 else 0
                m_c1.metric("初球(0-0) S率", f"{fp_rate:.1%} ({fp_s_count}/{fp_total})")
                m_c2.metric("3球で追い込んだ数", f"{ahead_count} / {total_cases}")
                st.caption("※3球目までに結果がついた打席は除外しています")
                st.markdown("---")
                
                stats = []
                for pt in df_p_view["球種"].unique():
                    sub = df_p_view[df_p_view["球種"] == pt]
                    total = len(sub)
                    s_count = len(sub[sub["判定"] != "ボール"])
                    s_rate = s_count / total if total > 0 else 0
                    speeds = sub[sub["球速"] > 0]["球速"]
                    avg_spd = speeds.mean() if not speeds.empty else 0
                    stats.append({"球種": pt, "投球数": total, "S率": f"{s_rate:.1%}", "平均球速": f"{avg_spd:.1f} km/h" if avg_spd > 0 else "-"})
                
                df_p_stats = pd.DataFrame(stats)
                if not df_p_stats.empty: df_p_stats = df_p_stats.sort_values("投球数", ascending=False)
                st.dataframe(df_p_stats, width="stretch", hide_index=True)

            st.markdown("---")
            st.markdown("### 📝 対戦結果一覧")
            result_keywords = ["四球", "三振", "安打", "凡打", "犠打", "失策", "併殺"]
            pattern = "|".join(result_keywords)
            results_df = df_p_view[df_p_view["結果"].astype(str).str.contains(pattern, na=False)].copy()
            display_cols = ["投手", "打者", "球種", "球速", "結果"]
            if not results_df.empty:
                table_height = (len(results_df) + 1) * 35 + 3
                st.dataframe(results_df[display_cols].sort_index(ascending=False), width="stretch", hide_index=True, height=table_height)
            else: st.info("表示する対戦結果がありません")

    with t2:
        header_text = f"👤 打者: {sel_b}" if sel_b != "All" else "👤 打者データ (全選手)"
        st.markdown(f"## {header_text}")
        
        p_hand_filter = st.radio("投手の左右で絞り込み", ["All", "右", "左"], horizontal=True, key="b_tab_p_hand")
        df_b_view = filtered_df.copy()
        if p_hand_filter != "All":
            df_b_view = df_b_view[df_b_view["投球腕"] == p_hand_filter]

        if df_b_view.empty or "打球X" not in df_b_view.columns: st.info("条件に合う打者データがありません")
        else:
            b_c1, b_c2 = st.columns([1.5, 1], gap="large")
            with b_c1:
                st.markdown("### 🏟️ 打球チャート")
                hit_data = df_b_view[df_b_view["打球X"] != -1]
                
                scale_factor = 300 / 350 # 保存データのスケール合わせ
                
                fig_ground = go.Figure()

                # 背景色（緑）
                fig_ground.add_shape(type="rect", x0=0, y0=0, x1=300, y1=300, fillcolor="#4CAF50", layer="below", line_width=0)

                # グラウンド（外野）
                fig_ground.add_shape(
                    type="path",
                    path="M 0 100 Q 150 -80 300 100 L 300 300 L 0 300 Z",
                    fillcolor="#E8F5E9", line_color="white", layer="below"
                )
                
                # ダイヤモンド (内野)
                fig_ground.add_shape(
                    type="path",
                    path="M 150 250 L 230 170 L 150 90 L 70 170 Z",
                    fillcolor="#F9E79F", line_color="#795548", line_width=2, layer="below"
                )
                
                # ファウルライン
                fig_ground.add_shape(type="line", x0=150, y0=250, x1=0, y1=100, line=dict(color="white", width=2), layer="below")
                fig_ground.add_shape(type="line", x0=150, y0=250, x1=300, y1=100, line=dict(color="white", width=2), layer="below")
                
                res_colors = {"安打": "red", "凡打": "blue", "犠打": "green", "失策": "orange", "ファウル": "gray"}
                hit_markers = {"ゴロ": "circle", "フライ": "triangle-up", "ライナー": "x", "バント": "square"}
                
                # マーカープロット
                for rc in hit_data["結果区分"].unique():
                    rc_data = hit_data[hit_data["結果区分"] == rc]
                    color = res_colors.get(rc, "black")
                    
                    for ht in rc_data["打球タイプ"].unique():
                        sub = rc_data[rc_data["打球タイプ"] == ht]
                        if sub.empty: continue
                        
                        marker = hit_markers.get(ht, "circle")
                        
                        fig_ground.add_trace(go.Scatter(
                            x=sub["打球X"] * scale_factor,
                            y=sub["打球Y"] * scale_factor,
                            mode='markers',
                            marker=dict(
                                symbol=marker,
                                color=color,
                                size=12,
                                line=dict(width=1, color='white')
                            ),
                            # 凡例用
                            name=f"{rc} ({ht})",
                            text=[f"<b>{row['結果']}</b><br>打者: {row['打者']}<br>球種: {row['球種']} ({row['球速']}km/h)<br>日付: {row['日時']}" for _, row in sub.iterrows()],
                            hoverinfo="text",
                            customdata=sub.index
                        ))

                fig_ground.update_layout(
                    xaxis=dict(range=[0, 300], showgrid=False, zeroline=False, visible=False),
                    yaxis=dict(range=[0, 300], showgrid=False, zeroline=False, visible=False, autorange="reversed", scaleanchor="x", scaleratio=1),
                    height=600, 
                    margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=True,
                    plot_bgcolor="rgba(0,0,0,0)"
                )

                event = st.plotly_chart(fig_ground, on_select="rerun", selection_mode="points", use_container_width=True)
                
                if event and event.selection and event.selection["points"]:
                    selected_indices = [p["customdata"] for p in event.selection["points"]]
                    if selected_indices:
                        st.markdown("#### 🔍 選択された打球の詳細")
                        selected_rows = df_b_view.loc[selected_indices]
                        disp_cols = ["日時", "投手", "打者", "球種", "球速", "結果", "詳細メモ"]
                        st.dataframe(selected_rows[disp_cols], hide_index=True)

            with b_c2:
                st.markdown("### 💨 コース別 スイング率")
                st.caption("※捕手視点 (スイング数 / 投球数)")
                fig3, ax3 = plt.subplots(figsize=(5, 5))
                ax3.set_xlim(0, 300); ax3.set_ylim(300, 0); ax3.axis('off')
                zones = {11: (0, 0, 150, 150, False), 12: (150, 0, 150, 150, False), 13: (0, 150, 150, 150, False), 14: (150, 150, 150, 150, False)}
                for r in range(3):
                    for c in range(3):
                        z_id = r * 3 + c + 1
                        zones[z_id] = (50 + c * (200/3), 50 + r * (200/3), 200/3, 200/3, True)
                cmap = plt.cm.Reds
                for z_id, (zx, zy, zw, zh, is_strike) in zones.items():
                    z_df = df_b_view[df_b_view["Zone"] == z_id]
                    total = len(z_df)
                    swings = len(z_df[z_df["判定"].isin(["ストライク(空振り)", "ファウル", "インプレー", "ファウル"])]) 
                    rate = swings / total if total > 0 else 0
                    facecolor = cmap(rate) if total > 0 else '#f9f9f9'
                    if not is_strike and total == 0: facecolor = '#f0f0f0'
                    edgecolor = 'black' if is_strike else '#aaaaaa'
                    lw = 2 if is_strike else 1
                    zorder = 10 if is_strike else 1
                    rect = patches.Rectangle((zx, zy), zw, zh, linewidth=lw, edgecolor=edgecolor, facecolor=facecolor, zorder=zorder)
                    ax3.add_patch(rect)
                    if is_strike: cx, cy = zx + zw/2, zy + zh/2
                    else:
                        if z_id == 11: cx, cy = 25, 25
                        elif z_id == 12: cx, cy = 275, 25
                        elif z_id == 13: cx, cy = 25, 275
                        elif z_id == 14: cx, cy = 275, 275
                    text_color = 'white' if rate > 0.5 and total > 0 else 'black'
                    rate_str = f"{rate:.1%}" if total > 0 else "-"
                    ax3.text(cx, cy - 5, rate_str, ha='center', va='bottom', fontsize=12, fontweight='bold', color=text_color, zorder=zorder+1)
                    ax3.text(cx, cy + 5, f"({swings}/{total})", ha='center', va='top', fontsize=10, color=text_color, zorder=zorder+1)
                rect_outer = patches.Rectangle((50, 50), 200, 200, linewidth=3, edgecolor='black', facecolor='none', zorder=20)
                ax3.add_patch(rect_outer)
                st.pyplot(fig3)
            
            st.markdown("---")
            st.markdown("### 📊 球種別 打者成績")
            b_stats = []
            for pt in df_b_view["球種"].unique():
                sub = df_b_view[df_b_view["球種"] == pt]
                total = len(sub)
                swings = len(sub[sub["判定"].isin(["ストライク(空振り)", "ファウル", "インプレー", "ファウル"])])
                swing_rate = swings / total if total > 0 else 0
                ab_df = sub[sub["結果"].astype(str).str.contains("凡打|安打|失策|三振", na=False)]
                hit_df = sub[sub["結果"].astype(str).str.contains("安打", na=False)]
                ab = len(ab_df)
                hits = len(hit_df)
                avg = hits / ab if ab > 0 else 0
                b_stats.append({"球種": pt, "投球数": total, "スイング率": f"{swing_rate:.1%}", "打率": f"{avg:.3f}".replace("0.", "."), "打数": ab, "安打": hits})
            
            df_b_stats = pd.DataFrame(b_stats)
            if not df_b_stats.empty: df_b_stats = df_b_stats.sort_values("投球数", ascending=False)
            st.dataframe(df_b_stats, width="stretch", hide_index=True)

    with t3:
        st.dataframe(filtered_df.sort_values("日時", ascending=False), width="stretch")

# --- メイン処理 ---
loaded_players = load_players()
default_file_path = os.path.join(SAVE_DIR, f"{datetime.date.today()}_1on1.csv")

if 'logs' not in st.session_state: st.session_state['logs'] = load_data_from_file(default_file_path)
if 'current_file' not in st.session_state: st.session_state.current_file = default_file_path

for k, v in {
    'pitchers': loaded_players["pitchers"], 'batters': loaded_players["batters"], 
    'count': {"B": 0, "S": 0}, 'key_zone': 0, 'key_field': 0, 'speed_buffer': "", 
    'edit_index': None, 'edit_data': {}, 'input_judgment': "未選択"
}.items():
    if k not in st.session_state: st.session_state[k] = v

page = st.sidebar.radio("モード", ["記録", "分析"])

if page == "記録":
    with st.sidebar.expander("メンバー管理 (追加・削除)"):
        st.write("▼ 投手の追加")
        n_p = st.text_input("投手名")
        n_ph = st.radio("投腕", ["右", "左"], horizontal=True)
        if st.button("投手を登録"):
            if n_p and n_p not in st.session_state.pitchers:
                st.session_state.pitchers[n_p] = n_ph
                save_players(st.session_state.pitchers, st.session_state.batters)
                st.rerun()

        st.markdown("---")
        st.write("▼ 打者の追加")
        n_b = st.text_input("打者名")
        n_bh = st.radio("打席", ["右", "左"], horizontal=True)
        if st.button("打者を登録"):
            if n_b and n_b not in st.session_state.batters:
                st.session_state.batters[n_b] = n_bh
                save_players(st.session_state.pitchers, st.session_state.batters)
                st.rerun()

        st.markdown("---")
        st.write("▼ 入力リストから削除")
        st.caption("※分析ページには過去のデータが残ります")
        
        p_list = list(st.session_state.pitchers.keys())
        b_list = list(st.session_state.batters.keys())
        
        del_p = st.selectbox("削除する投手", ["(選択)"] + p_list)
        if st.button("投手をリストから削除", width="stretch"):
            if del_p != "(選択)":
                del st.session_state.pitchers[del_p]
                save_players(st.session_state.pitchers, st.session_state.batters)
                st.rerun()

        del_b = st.selectbox("削除する打者", ["(選択)"] + b_list)
        if st.button("打者をリストから削除", width="stretch"):
            if del_b != "(選択)":
                del st.session_state.batters[del_b]
                save_players(st.session_state.pitchers, st.session_state.batters)
                st.rerun()
    
    with st.sidebar.expander("ファイル設定"):
        all_csv = sorted(glob.glob(os.path.join(SAVE_DIR, "*_1on1.csv")), reverse=True)
        today_f = f"{datetime.date.today()}_1on1.csv"
        opts = [os.path.basename(f) for f in all_csv]
        if today_f not in opts: opts.insert(0, today_f)
        sel_f = st.selectbox("ファイル", opts)
        sel_p = os.path.join(SAVE_DIR, sel_f)
        if sel_p != st.session_state.current_file:
            st.session_state.logs = load_data_from_file(sel_p)
            st.session_state.current_file = sel_p
            st.rerun()

    render_input_page(st.session_state.current_file)

else:
    render_analysis_page()