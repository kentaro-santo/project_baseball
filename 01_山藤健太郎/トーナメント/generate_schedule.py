import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.rcParams['font.family'] = ['Yu Gothic', 'MS Gothic', 'Meiryo', 'sans-serif']

# ============================================================
#  キャンバス設定
#  ylim 0-14  (上: タイトル+ブラケット  下: 日程表)
# ============================================================
fig, ax = plt.subplots(figsize=(15, 13))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')
ax.set_xlim(0, 15)
ax.set_ylim(0, 14)
ax.axis('off')

# ─── ヘルパー関数 ───────────────────────────────────────────
def draw_box(ax, x, y, text, w=1.9, h=0.50, fc='#dbeafe', ec='#3b82f6', fs=10):
    rect = mpatches.FancyBboxPatch((x - w/2, y - h/2), w, h,
                                   boxstyle='round,pad=0.06',
                                   facecolor=fc, edgecolor=ec, linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x, y, text, ha='center', va='center', fontsize=fs,
            fontweight='bold', color='#1e3a5f')

def hline(ax, x1, x2, y, color='#334155', lw=1.6):
    ax.plot([x1, x2], [y, y], color=color, lw=lw)

def vline(ax, x, y1, y2, color='#334155', lw=1.6):
    ax.plot([x, x], [y1, y2], color=color, lw=lw)

# ============================================================
#  タイトル  (y=13 付近)
# ============================================================
ax.text(7.5, 13.6, '中国五大学学生競技大会　硬式野球の部',
        ha='center', va='top', fontsize=20, fontweight='bold', color='#1a1a2e')
ax.text(7.5, 13.15, '令和8年度　8月8日（土）　9日（日）',
        ha='center', va='top', fontsize=13, color='#444')
ax.text(7.5, 12.80, '開催場所：広島大学野球場',
        ha='center', va='top', fontsize=12, color='#555')

# ============================================================
#  本戦ブラケット（左側  x=0.3〜7.5）
# ============================================================
#  y座標:
#   岡山大 11.5 ─┐
#                ├─ 勝者A (10.7) ─┐
#   鳥取大 10.5 ─┘                  │
#                                    ├─ 勝者G (9.5) ─┐
#   山口大  9.2 ───────────────────┘                    │
#                                                         ├─ 優勝 (8.1)
#   広島大  7.8 ─┐                                      │
#                ├─ 勝者B  (7.0) ──────────────────────┘
#   島根大  6.8 ─┘

TX = 1.1   # チーム名 x 中心

draw_box(ax, TX, 11.5, '岡山大学')
draw_box(ax, TX, 10.5, '鳥取大学')
draw_box(ax, TX,  9.2, '山口大学', w=2.0)
draw_box(ax, TX,  7.8, '広島大学')
draw_box(ax, TX,  6.8, '島根大学')

# 岡山 & 鳥取 → A
hline(ax, 2.05, 2.6, 11.5)
hline(ax, 2.05, 2.6, 10.5)
vline(ax, 2.6, 10.5, 11.5)
hline(ax, 2.6, 3.2, 11.0)
draw_box(ax, 3.65, 11.0, '勝者 A', w=1.1, h=0.42, fc='#eff6ff', ec='#3b82f6', fs=9)

# 山口 → 準決勝（縦線 x=4.7 まで一本で引く）
hline(ax, 2.1, 4.7, 9.2)

# A & 山口 → G
hline(ax, 4.2, 4.7, 11.0)
# 山口側はすでに 4.7 まで引いているので追加不要
vline(ax, 4.7,  9.2, 11.0)
hline(ax, 4.7, 5.2, 10.1)
draw_box(ax, 5.65, 10.1, '勝者 G', w=1.1, h=0.42, fc='#eff6ff', ec='#3b82f6', fs=9)

# 広島 & 島根 → B
hline(ax, 2.05, 2.6, 7.8)
hline(ax, 2.05, 2.6, 6.8)
vline(ax, 2.6,  6.8, 7.8)
hline(ax, 2.6, 3.2, 7.3)
draw_box(ax, 3.65, 7.3, '勝者 B', w=1.1, h=0.42, fc='#eff6ff', ec='#3b82f6', fs=9)

# G & B → 優勝
hline(ax, 6.2, 6.6, 10.1)
hline(ax, 4.2, 6.6,  7.3)
vline(ax, 6.6,  7.3, 10.1)
hline(ax, 6.6, 7.1, 8.7)
draw_box(ax, 7.75, 8.7, '★ 優 勝 ★', w=1.45, h=0.55,
         fc='#fef08a', ec='#ca8a04', fs=12)

# 本戦ラベル
ax.text(3.8, 12.7, '《本　戦》', ha='center', va='center',
        fontsize=12, fontweight='bold', color='#1d4ed8',
        bbox=dict(facecolor='#eff6ff', edgecolor='#3b82f6',
                  boxstyle='round,pad=0.35', linewidth=1.3))

# ============================================================
#  三位決定戦ブラケット（右側  x=9.5〜14.8）
# ============================================================
#   C (第1試合敗者) 11.5 ─┐
#                           ├─ 勝者F (10.7) ─┐
#   D (第2試合敗者) 10.5 ─┘                    ├─ 三位 (9.1)
#                                               │
#   第3試合敗者     8.0 ───────────────────────┘

BX = 10.6

draw_box(ax, BX, 11.5, '第1試合敗者（C）', w=2.5, h=0.48, fc='#fee2e2', ec='#ef4444', fs=9)
draw_box(ax, BX, 10.5, '第2試合敗者（D）', w=2.5, h=0.48, fc='#fee2e2', ec='#ef4444', fs=9)

hline(ax, 11.85, 12.3, 11.5)
hline(ax, 11.85, 12.3, 10.5)
vline(ax, 12.3, 10.5, 11.5)
hline(ax, 12.3, 12.8, 11.0)
draw_box(ax, 13.25, 11.0, '勝者（F）', w=1.1, h=0.42, fc='#fff1f2', ec='#ef4444', fs=9)

draw_box(ax, BX, 8.0, '第3試合敗者（E）', w=2.5, h=0.48, fc='#fee2e2', ec='#ef4444', fs=9)

hline(ax, 13.8, 14.1, 11.0)
hline(ax, 11.75, 14.1,  8.0)
vline(ax, 14.1,  8.0, 11.0)
hline(ax, 14.1, 14.4, 9.5)
draw_box(ax, 14.65, 9.5, '三位', w=0.85, h=0.65,
         fc='#fef9c3', ec='#ca8a04', fs=10)

# 三位決定戦ラベル
ax.text(11.5, 12.7, '《三位決定戦》', ha='center', va='center',
        fontsize=12, fontweight='bold', color='#dc2626',
        bbox=dict(facecolor='#fff1f2', edgecolor='#ef4444',
                  boxstyle='round,pad=0.35', linewidth=1.3))

# ============================================================
#  区切り線
# ============================================================
ax.plot([0.2, 14.8], [5.6, 5.6], color='#94a3b8', lw=2.0, ls='--')

# ============================================================
#  試合スケジュール表（破線より下）
# ============================================================
headers = ['日程', '時間', '試合', '対　戦', '補　助']
col_x   = [0.65, 1.85, 3.35, 8.0, 13.5]

# 補助.mdより
rows = [
    ('1日目', '9:00',  '第1試合',              '岡山大学　vs　鳥取大学',                       '広島大学'),
    ('1日目', '11:30', '第2試合',              '広島大学　vs　島根大学',                       '第1試合敗者'),
    ('1日目', '14:00', '第3試合',              '山口大学　vs　第1試合勝者',                    '広島大学'),
    ('2日目', '9:00',  '第1試合',              '第1試合敗者（C）　VS　第2試合敗者（D）',            '広島大学'),
    ('2日目', '11:30', '第2試合',              '第3試合勝者（G）　VS　第2試合勝者（B）',       '2日目第1試合敗者'),
    ('2日目', '14:00', '第3試合',              '勝者（F）　VS　第3試合敗者（E）',                        '広島大学'),
]

ROW_H   = 0.50
TABLE_Y = 5.30   # 破線(5.6)の下
HDR_H   = 0.45
TBL_W   = 14.6   # 表の横幅

# ヘッダー
header_bg = mpatches.FancyBboxPatch((0.2, TABLE_Y - HDR_H + 0.02),
                                    TBL_W, HDR_H,
                                    boxstyle='square,pad=0',
                                    facecolor='#1e3a5f', edgecolor='none')
ax.add_patch(header_bg)
for hdr, cx in zip(headers, col_x):
    ax.text(cx, TABLE_Y - HDR_H/2 + 0.02, hdr, ha='center', va='center',
            fontsize=11, fontweight='bold', color='white')

# 行データ
for ri, (day, time, game, match, aux) in enumerate(rows):
    y_top = TABLE_Y - HDR_H - ri * ROW_H
    fc = '#eff6ff' if day == '1日目' else '#f0fdf4'
    ec = '#bfdbfe' if day == '1日目' else '#bbf7d0'

    row_rect = mpatches.FancyBboxPatch((0.2, y_top - ROW_H + 0.02),
                                       TBL_W, ROW_H - 0.04,
                                       boxstyle='square,pad=0',
                                       facecolor=fc, edgecolor=ec, linewidth=0.8)
    ax.add_patch(row_rect)
    cy = y_top - ROW_H / 2 + 0.01

    ax.text(col_x[0], cy, day, ha='center', va='center',
            fontsize=11, fontweight='bold',
            color='#1d4ed8' if day == '1日目' else '#15803d')
    ax.text(col_x[1], cy, time, ha='center', va='center',
            fontsize=12, fontweight='bold', color='#92400e',
            bbox=dict(facecolor='#fef3c7', edgecolor='#fbbf24',
                      boxstyle='round,pad=0.25', linewidth=0.8))
    ax.text(col_x[2], cy, game, ha='center', va='center',
            fontsize=10, fontweight='bold', color='#374151')
    ax.text(col_x[3], cy, match, ha='center', va='center',
            fontsize=10, color='#1e293b')
    ax.text(col_x[4], cy, aux, ha='center', va='center',
            fontsize=10, color='#374151')

# 外枠
table_total_h = HDR_H + len(rows) * ROW_H
outer = mpatches.FancyBboxPatch((0.2, TABLE_Y - table_total_h + 0.02),
                                 TBL_W, table_total_h,
                                 boxstyle='round,pad=0.06',
                                 facecolor='none', edgecolor='#334155',
                                 linewidth=2.0)
ax.add_patch(outer)

# 補助列の縦区切り線
bot = TABLE_Y - table_total_h + 0.02
vline(ax, 12.0, bot, TABLE_Y + 0.02, color='#cbd5e1', lw=1.2)

# ============================================================
#  フッター注記
# ============================================================
ax.text(7.5, bot - 0.38,
        '※ 二日目の第二試合の後に表彰式を行います。',
        ha='center', va='center', fontsize=12, color='#1e293b',
        fontweight='bold')
ax.text(7.5, bot - 0.75,
        '※ 補助の内容は（ボールボーイ２名・ファールボーイ２名・塁審３名）',
        ha='center', va='center', fontsize=12, color='#1e293b',
        fontweight='bold')

# ============================================================
#  出力
# ============================================================
plt.tight_layout(pad=0.3)
output = r'c:\Users\スコアボード\Documents\野球\プロジェクト\project_baseball\01_山藤健太郎\トーナメント\トーナメント日程表.png'
plt.savefig(output, dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print(f'保存: {output}')
plt.close()
