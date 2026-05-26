#!/usr/bin/env python3
"""
汎用 .bacs-s -> CSV 変換スクリプト
使い方:
  python convert_bacs_to_csv.py 入力ファイル.bacs-s [出力ファイル.csv]
デフォルトの出力ファイル名は入力と同名の .csv

挙動:
- まずファイルをバイナリ読み込みし、UTF-8などのエンコーディングでデコードを試みる。
- JSON形式ならJSONを解釈し、表形式データをCSVに変換する。
- JSON以外は行単位で空白区切りにしてCSV出力する。
- オプション `--mode vertical` で横幅の広いJSONリストを縦型のCSVにできます。
"""
import argparse
import csv
import json
import os
import re

ENCODINGS_TO_TRY = ['utf-8-sig', 'utf-8', 'utf-16', 'utf-16le', 'utf-16be', 'cp932', 'shift_jis', 'latin1']


def decode_text(data: bytes):
    for enc in ENCODINGS_TO_TRY:
        try:
            text = data.decode(enc)
            return text, enc
        except Exception:
            continue
    return data.decode('latin1', errors='replace'), 'latin1'


def json_to_rows(obj, mode='auto'):
    if mode == 'vertical':
        if isinstance(obj, list):
            if len(obj) == 2 and isinstance(obj[0], list) and isinstance(obj[1], str):
                rows = [[i + 1, str(value)] for i, value in enumerate(obj[0])]
                rows.append(['metadata', obj[1]])
                return rows
            if all(isinstance(item, list) for item in obj):
                rows = []
                for r, row in enumerate(obj):
                    rows.append([f'row_{r}'] + [str(v) for v in row])
                return rows
            if all(isinstance(item, str) for item in obj):
                return [[i + 1, value] for i, value in enumerate(obj)]
        if isinstance(obj, dict):
            return [[key, value] for key, value in obj.items()]
        return [[str(obj)]]

    if isinstance(obj, list):
        if all(isinstance(item, list) for item in obj):
            return obj
        if len(obj) == 2 and isinstance(obj[0], list) and isinstance(obj[1], str):
            return [obj[0], [obj[1]]]
        if all(isinstance(item, str) for item in obj):
            return [obj]
    if isinstance(obj, dict):
        return [[key, value] for key, value in obj.items()]
    return [[str(obj)]]


def text_to_rows(text: str):
    lines = re.split(r'\r\n|\r|\n', text)
    rows = []
    for line in lines:
        if not line.strip():
            continue
        line_norm = line.replace('\u3000', ' ')
        rows.append(re.split(r'\s+', line_norm.strip()))
    return rows


def convert_file(in_path: str, out_path: str, mode: str = 'auto'):
    with open(in_path, 'rb') as f:
        data = f.read()

    text, enc = decode_text(data)

    format_type = 'text'
    try:
        payload = json.loads(text)
        rows = json_to_rows(payload, mode=mode)
        format_type = 'json'
    except json.JSONDecodeError:
        rows = text_to_rows(text)

    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    with open(out_path, 'w', newline='', encoding='utf-8') as csvf:
        writer = csv.writer(csvf)
        writer.writerows(rows)

    return enc, format_type, len(rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert .bacs-s to CSV (generic)')
    parser.add_argument('input', help='入力 .bacs-s ファイル')
    parser.add_argument('output', nargs='?', help='出力 CSV ファイル (省略時は同名.csv)')
    parser.add_argument('--mode', choices=['auto', 'vertical'], default='auto', help='CSV出力のレイアウト')
    args = parser.parse_args()

    in_path = args.input
    out_path = args.output or os.path.splitext(in_path)[0] + '.csv'

    enc, fmt, rows = convert_file(in_path, out_path, mode=args.mode)
    print(f'Detected encoding: {enc}')
    print(f'Interpreted format: {fmt}')
    print(f'Wrote {rows} rows to {out_path}')
