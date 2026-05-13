# work-daily-report

从 Claude Code、Codex 与 Cursor 的本地会话记录中提取指定日期范围的工作内容，按天整理为结构化工作日报，并支持提交到维拉工时系统。

这个仓库的目标是减少人工翻会话、手工整理日报和重复拼接工时提交请求的成本。

## 功能说明

- 同时支持 Claude Code、Codex 与 Cursor 本地会话记录
- 支持 Windows 原生路径与 WSL 路径
- 自动过滤常见噪声内容
- 按天输出日报素材
- 支持将整理后的日报提交到维拉工时

## 目录结构

```text
work-daily-report/
├── README.md
├── SKILL.md
├── references/
│   ├── api_reference.md
│   └── vera_config.json
└── scripts/
    ├── extract_daily_report.py
    └── submit_vera_timesheet.py
```

## 环境要求

- Python 3.10 或更高版本
- 可访问本地 Claude / Codex / Cursor 会话目录
- 如需提交维拉工时，需要有效的接口 token

## 快速开始

### 1. 提取日报素材

```bash
python scripts/extract_daily_report.py --start 2026-04-09 --end 2026-04-14
```

如需显式指定路径：

```bash
python scripts/extract_daily_report.py \
  --start 2026-04-09 \
  --end 2026-04-14 \
  --claude-dir /mnt/c/Users/<用户名>/.claude/projects \
  --codex-dir /mnt/c/Users/<用户名>/.codex/sessions \
  --cursor-dir /mnt/c/Users/<用户名>/AppData/Roaming/Cursor/User
```

Cursor 补充说明：

- 默认路径：`C:\Users\<用户名>\AppData\Roaming\Cursor\User`
- 本地数据主要保存在 `SQLite` 数据库中
- 普通聊天 / composer 历史可以提取，Background Agents 不保证本地完整可见

### 2. 整理日报内容

脚本输出的是“日报素材”，建议再压缩成适合提交或汇报的正式内容。

推荐格式：

```text
计划：
1. ...
2. ...

执行：
1. ...
2. ...
3. ...
```

## 维拉工时配置

请直接维护以下配置文件：

```text
references/vera_config.json
```

示例结构：

```json
{
  "endpoint": "https://vivid-server.vividlog.com/api/v4/workinghours/",
  "token": "<your_jwt_token>",
  "projectId": "<your_project_id>",
  "userId": "<your_user_id>",
  "timeslot": 8,
  "source": "pc",
  "type": "STANDARD"
}
```

字段说明：

- `token`：维拉接口 Bearer Token
- `projectId`：维拉项目 ID
- `userId`：维拉用户 ID
- `timeslot`：工时，默认 8
- `source`：默认 `pc`
- `type`：默认 `STANDARD`

## 提交维拉工时

先准备一个日报正文文件，例如：

```text
D:/tmp/daily_note.txt
```

再执行：

```bash
python scripts/submit_vera_timesheet.py \
  --config references/vera_config.json \
  --start-date 2026-05-12 \
  --end-date 2026-05-12 \
  --note-file D:/tmp/daily_note.txt
```

如果只想预览请求体，不实际提交：

```bash
python scripts/submit_vera_timesheet.py \
  --config references/vera_config.json \
  --start-date 2026-05-12 \
  --end-date 2026-05-12 \
  --note-file D:/tmp/daily_note.txt \
  --dry-run
```

## 输出特点

- 默认输出适合进一步整理为“领导汇报版日报”
- 会弱化或忽略问候语、权限提示、工具噪声等内容
- 同一项目的连续会话会尽量压缩归并
- 若某天没有有效工作记录，会明确标记

## 常见使用场景

- 查看最近几天做了什么
- 整理上周日报
- 从 Claude、Codex 和 Cursor 会话中提取项目推进记录
- 先抽取时间线，再压缩成日报
- 整理日报后提交到维拉工时
