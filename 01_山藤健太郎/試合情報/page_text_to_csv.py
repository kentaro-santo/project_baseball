#!/usr/bin/env python3
"""
Text-based page list -> CSV 変換スクリプト

最初の単一列データをヘッダーとして、
複数の値を含むデータセクションを処理します。
"""

import argparse
import csv
import os
import re


def count_columns(line: str):
    """行のカラム数を数える"""
    line = line.replace('\u3000', ' ')
    if '\t' in line:
        return len([p for p in line.split('\t') if p.strip()])
    if re.search(r' {2,}', line):
        return len([p for p in re.split(r' {2,}', line) if p.strip()])
    return 1 if line.strip() else 0


def line_to_columns(line: str):
    """行をカラムに分割"""
    line = line.replace('\u3000', ' ')
    if '\t' in line:
        return [p.strip() for p in line.split('\t') if p.strip()]
    if re.search(r' {2,}', line):
        return [p.strip() for p in re.split(r' {2,}', line) if p.strip()]
    stripped = line.strip()
    return [stripped] if stripped else []


def convert_text_file(input_path: str, output_path: str):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.read().splitlines()

    header = []
    data_rows = []
    in_header = True

    for line in lines:
        if not line.strip():
            continue
        
        cols = line_to_columns(line)
        col_count = count_columns(line)
        
        # ヘッダーセクション: 単一列のみ
        if in_header and col_count == 1 and line.strip() != 'ページ一覧':
            header.extend(cols)
        # データセクション: 複数列のデータ
        elif col_count > 1:
            in_header = False
            data_rows.append(cols)
        elif col_count == 1 and not in_header:
            # データセクション内の単一列行もデータ行として扱う
            data_rows.append(cols)

    # パディング: すべての行を同じ列数に揃える
    max_cols = max(len(header), max((len(row) for row in data_rows), default=0))
    header += [''] * (max_cols - len(header))
    for row in data_rows:
        row.extend([''] * (max_cols - len(row)))

    # CSV出力
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data_rows)

    return len(data_rows) + 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert text page list to CSV')
    parser.add_argument('input', help='入力テキストファイル')
    parser.add_argument('output', nargs='?', help='出力CSVファイル (省略時は同じフォルダのpage_list.csv)')
    args = parser.parse_args()

    out_path = args.output or os.path.splitext(args.input)[0] + '.csv'
    rows = convert_text_file(args.input, out_path)
    print(f'Wrote {rows} rows to {out_path}')
