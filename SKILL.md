---
name: work-daily-report
description: 从 Claude Code、Codex 与 Cursor 的本地会话记录中提取指定日期范围的工作内容，按天生成结构化工作日报。适用于"查看我最近几天做了什么""按日期汇总日报""根据会话记录回溯工作内容"等需求，兼容 Windows 原生路径与 WSL 路径。
---

# Work Daily Report

## Overview

当用户要求"根据会话记录整理工作日报"时，使用此 skill。它适用于同时分析 `Claude Code`、`Codex` 与 `Cursor` 的本地会话记录，并将原始会话压缩为按天汇总的工作日报。

该 skill 的目标不是逐条复读聊天内容，而是提炼出：
- 当天做了哪些项目/任务
- 解决了哪些问题
- 产出了哪些文档、代码或配置
- 哪些内容只是工具配置/闲聊，应弱化或忽略

## Supported Sources

### Claude Code
默认路径：
- Windows: `C:\Users\<用户名>\.claude\projects`
- WSL: `/mnt/c/Users/<用户名>/.claude/projects`

常见特点：
- 会话文件通常为 `*.jsonl`
- 需要重点读取主会话中的 `user` 消息
- 需忽略纯 `tool_result`、`isMeta=true`、`<local-command-caveat>` 这类噪声
- `subagents` 目录通常不作为日报主来源，除非用户明确要求

### Codex
默认路径：
- Windows: `C:\Users\<用户名>\.codex\sessions`
- WSL: `/mnt/c/Users/<用户名>/.codex/sessions`

常见特点：
- 会话通常按 `年/月/日/*.jsonl` 存放
- 主要从 `response_item -> payload.type=message -> role=user` 中提取用户任务
- `session_meta.payload.cwd` 可用于识别项目目录
- 要忽略 AGENTS 注入、sandbox/permission 提示、工具警告等非工作内容

### Cursor
默认路径：
- Windows: `C:\Users\<用户名>\AppData\Roaming\Cursor\User`
- WSL: `/mnt/c/Users/<用户名>/AppData/Roaming/Cursor/User`

常见特点：
- 会话元数据保存在本地 `SQLite` 数据库，不是 `jsonl`
- `globalStorage/state.vscdb` 中可提取 `bubbleId:*` 消息记录
- `workspaceStorage/<id>/workspace.json` 可映射回项目目录
- 当前更适合提取普通聊天 / composer 历史，Background Agents 不保证本地完整可见

## Workflow

### Step 1: 明确统计范围
先确认：
- 日期范围（如 `4月9日到4月14日`）
- 是否需要同时读取 `Claude`、`Codex` 和 `Cursor`
- 是否只看主会话，还是包含插件安装/环境配置类会话

默认策略：
- 同时读取 `Claude`、`Codex` 与 `Cursor`
- 优先使用主会话
- 将插件安装、闲聊、测试性对话降权
- 若某天没有有效工作内容，明确写"未发现有效工作记录"

### Step 2: 抽取候选工作内容
按天提取这些信息：
- 用户提出的任务目标
- 相关项目目录 `cwd`
- 同一会话中的连续"请继续/继续修改/修复问题"等上下文
- 具有明显产出导向的内容：如修文档、做海报、改代码、调接口、转 HTML/PDF、配置插件、备份仓库、接入系统

不要把以下内容直接当日报主体：
- 单独的 `你好`
- 工具系统提示
- 权限/沙箱提示
- `AGENTS.md` 注入内容
- 被中断但未形成实际任务的孤立上下文

### Step 3: 归并会话为"当日工作项"
按以下维度聚合：
- 同一 `cwd` 下的连续任务视为同一项目
- 同一问题的连续修订合并成一条日报
- 同一天同一项目的多次往返，优先总结为"持续推进/迭代完善"
- 若同一天存在多个独立项目，分点列出

推荐聚类标签：
- 文档方案类
- 代码修复类
- 配置与工具链类
- 运维/仓库管理类
- 调研与接入类
- 设计与素材类

### Step 4: 提炼日报表述
将原始任务改写为适合日报的正式语句：
- 从"请你读取 xxx 并修改"改写为"完成 xxx 的分析与修改"
- 从"请继续"恢复上下文后并入上一条
- 从"试试看/帮我看一下"改写为"分析并定位问题"

表述要求：
- 使用完成式、结果导向语言
- 尽量体现对象、动作、结果
- 不要写成聊天记录
- 不要虚构未发生的结果

## Output Format

默认输出为"领导汇报版日报"，按天使用"计划 + 执行"结构，且默认隐藏 AI 工具痕迹：

```md
## 4月9日
计划：
1. ...
2. ...

执行：
1. ...
2. ...
3. ...
```

写作要求：
- 默认用于提交日报、给领导看
- 不出现 `agent`、`Claude`、`Codex`、`AI`、`skill`、`plugin`、`提示词模板`、`工具配置` 等字样
- 重点表达"围绕项目目标做了什么、推进了什么、产出了什么、识别了什么问题"
- 配置提示词、个人工作流优化、工具安装、闲聊问答等内容默认剔除，除非它们本身直接形成项目交付物
- 若某天只有弱记录，可写为"主要开展方案整理、问题排查或衔接准备，未形成独立阶段性产出"

如果用户明确要求"精简版"，则每个日期仅保留 1 条计划 + 2~3 条执行，语言更短、更偏结果。

如果用户明确要求"今日完成/问题风险/明日计划"模板，再改为：

```md
## 4月9日
今日完成：
- ...

问题风险：
- ...

明日计划：
- ...
```

## Heuristics

### 应保留的高价值信号
- 明确的项目目录
- 明确的交付物：`md/html/pdf/海报/代码/配置`
- "修复/优化/重构/转换/备份/接入/分析/调研"类动作
- 连续多轮围绕同一需求的迭代

### 应降权或忽略的低价值信号
- 问候语
- 单纯问概念定义，且与实际项目无关
- 插件/技能安装过程中的纯命令回显
- 系统 hook / stop summary / turn duration
- `The user interrupted...` 这类控制信息

### 对"配置类工作"的判断
默认原则：凡是仅服务于个人工作流、AI 工具使用、提示词模板、skills/plugin 安装、环境偏好调整的内容，一律不纳入给领导看的日报。

只有在以下情况才保留：
- 该配置工作直接形成项目交付物
- 该工作直接解决项目阻塞问题
- 该工作属于项目环境建设的一部分，且对项目推进有明确产出价值

否则统一视为低价值噪声，默认剔除。

## Claude / Codex / Cursor Compatibility

### 在 Claude Code 场景下
优先读取：
- `C:\Users\<用户名>\.claude\projects`
- 必要时补充 `C:\Users\<用户名>\.codex\sessions`

### 在 Codex / WSL 场景下
优先读取：
- `/mnt/c/Users/<用户名>/.claude/projects`
- `/mnt/c/Users/<用户名>/.codex/sessions`
- `/mnt/c/Users/<用户名>/AppData/Roaming/Cursor/User`

### 路径转换规则
若用户给的是 Windows 路径，而当前环境是 Linux/WSL：
- `C:\Users\<用户名>\.claude` → `/mnt/c/Users/<用户名>/.claude`
- `C:\Users\<用户名>\.codex` → `/mnt/c/Users/<用户名>/.codex`
- `C:\Users\<用户名>\AppData\Roaming\Cursor\User` → `/mnt/c/Users/<用户名>/AppData/Roaming/Cursor/User`

## Recommended Extraction Strategy

优先使用脚本批量抽取，再由模型做二次压缩：
1. 脚本扫描日期范围内文件
2. 提取有效用户消息、项目目录、日期
3. 先输出"按天-按会话"的粗摘要
4. 再人工/模型压缩为"按天工作日报"

不要一开始就只靠人工读大量 JSONL；先程序化过滤噪声，更稳定。

## Script

内置脚本：`scripts/extract_daily_report.py`

推荐用法：

```bash
python extract_daily_report.py --start 2026-04-09 --end 2026-04-14
```

也可显式指定路径：

```bash
python extract_daily_report.py \
  --start 2026-04-09 \
  --end 2026-04-14 \
  --claude-dir /mnt/c/Users/<用户名>/.claude/projects \
  --codex-dir /mnt/c/Users/<用户名>/.codex/sessions \
  --cursor-dir /mnt/c/Users/<用户名>/AppData/Roaming/Cursor/User
```

## Final Checklist

在输出日报前，检查：
- 是否同时覆盖 Claude 与 Codex
- 是否在需要时覆盖 Cursor
- 是否按日期完整覆盖用户要求的范围
- 是否把"请继续"正确并入上下文
- 是否去掉系统噪声与命令回显
- 是否把聊天式原文改写成正式日报语句
- 是否对"无有效记录"的日期做了明确说明

## Example Requests

- "请你查看我的 claude 和 codex 会话记录，帮我总结 4月9日到4月14日每天的工作日报。"
- "根据 `C:\Users\xxx\.claude` 和 `C:\Users\xxx\.codex` 里的记录，整理上周日报。"
- "把最近几天做的项目按日报格式输出，没记录的日期也列出来。"
- "先抽取会话时间线，再压缩成适合发领导的工作日报。"
- "总结最近几天日报并提交到维拉工时。"

---

## Vera Timesheet Submission (维拉工时提交)

日报整理完成后，可直接提交到维拉工时系统。

### API Configuration

- **Config File**: `references/vera_config.json`
- **Endpoint**: 在本地配置文件中维护
- **Method**: `POST`
- **Auth**: `Authorization: Bearer <your_jwt_token>`
- **Content-Type**: `application/json`

建议将以下敏感项统一放入本地配置文件：
- `token`
- `projectId`
- `userId`
- `endpoint`
- 可选默认值：`timeslot`、`source`、`type`

### Request Body Schema

```json
{
  "note": "日报内容（含计划+执行）",
  "projectId": "<your_project_id>",
  "startDate": "YYYY-MM-DD",
  "endDate": "YYYY-MM-DD",
  "timeslot": 8,
  "source": "pc",
  "userId": "<your_user_id>",
  "type": "STANDARD"
}
```

### Field Notes

| 字段 | 说明 | 示例 |
|------|------|------|
| note | 日报正文，使用"计划+执行"格式，无标题 | 见下方模板 |
| projectId | 维拉系统项目ID | "<your_project_id>" |
| startDate | 开始日期 | "2026-05-12" |
| endDate | 结束日期（单日同startDate） | "2026-05-12" |
| timeslot | 工时（小时） | 8 |
| source | 来源 | "pc" |
| userId | 维拉系统用户ID | "<your_user_id>" |
| type | 类型 | "STANDARD" |

### Note Format Template

日报内容使用"计划+执行"格式，**不要加标题**（如"5月12日工作日报"）：

```
计划：
1. xxx
2. xxx

执行：
1. xxx
2. xxx
3. xxx
```

### Submission Workflow

1. 提取日报素材（运行 extract_daily_report.py）
2. 整理为"计划+执行"格式
3. 去除个人项目/非工作内容（给领导看的版本）
4. 在本地创建 `references/vera_config.json` 并填写 token / userId / projectId
5. 按天构造 JSON payload
6. 逐日 POST 提交

### Local Config Example

直接维护 `references/vera_config.json`：

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

推荐优先使用内置脚本提交，避免手工拼接认证头：

```bash
python scripts/submit_vera_timesheet.py \
  --config references/vera_config.json \
  --start-date 2026-05-12 \
  --end-date 2026-05-12 \
  --note-file /absolute/path/to/daily_note.txt
```

### Curl Example

```bash
curl -s -X POST "https://vivid-server.vividlog.com/api/v4/workinghours/" \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "note": "计划：\n1. xxx\n\n执行：\n1. xxx",
    "projectId": "<your_project_id>",
    "startDate": "2026-05-12",
    "endDate": "2026-05-12",
    "timeslot": 8,
    "source": "pc",
    "userId": "<your_user_id>",
    "type": "STANDARD"
  }'
```

### Delete Existing Record

如需删除已提交记录：

```bash
curl -s -X DELETE "https://vivid-server.vividlog.com/api/v4/workinghours/<record_id>" \
  -H "Authorization: Bearer <your_jwt_token>"
```

### Pitfalls

- note 字段不要包含标题（如"【5月12日工作日报】"），直接写"计划+执行"
- 个人项目（如个人GitHub仓库、AI工具配置等）需剔除，给领导看的日报只保留工作相关内容
- 每天单独提交一条记录，startDate 和 endDate 保持一致
- 提交前确认 token 未过期
