#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从本地配置文件读取维拉工时参数并提交日报。

示例:
  python scripts/submit_vera_timesheet.py \
    --config references/vera_config.json \
    --start-date 2026-05-12 \
    --end-date 2026-05-12 \
    --note-file D:/tmp/daily_note.txt
"""

import argparse
import json
from pathlib import Path
from urllib import error, request


def parse_args():
    parser = argparse.ArgumentParser(description='提交维拉工时日报')
    parser.add_argument(
        '--config',
        default=str(Path(__file__).resolve().parents[1] / 'references' / 'vera_config.json'),
        help='本地配置文件路径',
    )
    parser.add_argument('--start-date', required=True, help='开始日期 YYYY-MM-DD')
    parser.add_argument('--end-date', required=True, help='结束日期 YYYY-MM-DD')
    parser.add_argument('--note-file', required=True, help='日报正文文件路径，内容为"计划+执行"格式')
    parser.add_argument('--dry-run', action='store_true', help='仅打印请求体，不实际提交')
    return parser.parse_args()


def load_json(path_str):
    path = Path(path_str)
    return json.loads(path.read_text(encoding='utf-8'))


def require_field(data, field_name):
    value = data.get(field_name)
    if value in (None, ''):
        raise ValueError(f'缺少必填配置: {field_name}')
    return value


def build_payload(config, note, start_date, end_date):
    return {
        'note': note.strip(),
        'projectId': require_field(config, 'projectId'),
        'startDate': start_date,
        'endDate': end_date,
        'timeslot': config.get('timeslot', 8),
        'source': config.get('source', 'pc'),
        'userId': require_field(config, 'userId'),
        'type': config.get('type', 'STANDARD'),
    }


def submit(endpoint, token, payload):
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = request.Request(
        endpoint,
        data=body,
        method='POST',
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
    )
    with request.urlopen(req, timeout=30) as resp:
        return resp.read().decode('utf-8', errors='replace')


def main():
    args = parse_args()
    config = load_json(args.config)
    note = Path(args.note_file).read_text(encoding='utf-8').strip()
    if not note:
        raise ValueError('note-file 为空，无法提交工时')

    endpoint = require_field(config, 'endpoint')
    token = require_field(config, 'token')
    payload = build_payload(config, note, args.start_date, args.end_date)

    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    try:
        response_text = submit(endpoint, token, payload)
    except error.HTTPError as exc:
        detail = exc.read().decode('utf-8', errors='replace')
        raise RuntimeError(f'提交失败: HTTP {exc.code} {detail}') from exc
    except error.URLError as exc:
        raise RuntimeError(f'提交失败: {exc.reason}') from exc

    print(response_text)


if __name__ == '__main__':
    main()
