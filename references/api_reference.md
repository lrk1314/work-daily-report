# Work Daily Report Reference

## Purpose

本参考文档补充说明 `work-daily-report` skill 在 Claude Code 与 Codex 会话提取中的判断规则、路径兼容策略和摘要压缩原则。

## Source Priority

### Priority 1: 主会话中的用户任务
优先提取：
- 用户的初始任务描述
- 与该任务直接相关的“继续/修复/优化/转换/补充”消息
- 能标识项目的 `cwd`

### Priority 2: 项目上下文
当日报输出需要项目名时，优先从以下信息推断：
- `cwd`
- 用户消息中的路径
- 明确提到的仓库、系统、文档、文件名

### Priority 3: 助手侧结果（仅辅助理解）
如果用户消息过短，例如只有“请继续”，可以参考同一会话上下文恢复语义；但日报正文仍应基于用户实际任务，不要把助手自说自话当成果。

## Noise Filtering

以下内容默认不计入日报：
- `AGENTS.md instructions`
- 权限申请、沙箱报错、工具调用包装信息
- `local-command-caveat`
- `tool_result`
- `stop_hook_summary`
- `turn_duration`
- 问候语或测试消息

以下内容可视情况计入：
- plugin/skill 安装与配置
- 仓库备份、环境搭建、工具链接入
- 用户明确围绕工具机制进行学习或整理的会话

## Compression Rules

### 同项目多轮会话
若同一项目在同一天有多轮会话，应压缩成 1~3 条成果描述，例如：
- 持续完善联合原子化改造方案，重写异常信号采集流程并同步输出 HTML 汇报版本。

### 同问题多次修复
若存在“先修复 A，再补充 B，再修复分页/样式问题”，可写成：
- 持续修复微信端试卷列表与答题页问题，完成筛选、排序、分页加载及样式显示优化。

### 配置学习型会话
如果整天主要在研究工具机制，可写成：
- 完成 Claude 插件与 skills/hook 机制梳理，验证插件安装、加载与自主触发规则。

## Windows / WSL Mapping

| Windows | WSL |
|---|---|
| `C:\Users\<用户名>\.claude\projects` | `/mnt/c/Users/<用户名>/.claude/projects` |
| `C:\Users\<用户名>\.codex\sessions` | `/mnt/c/Users/<用户名>/.codex/sessions` |

## Recommended Final Styles

### 简洁日报
- 每天 3~5 条
- 每条突出“项目 + 动作 + 结果”

### 汇报版日报
- 今日完成
- 问题风险
- 明日计划

### 周报素材版
- 按项目归类
- 再按日期回填

## Suggested Prompt Patterns

- “查看 `C:\Users\xxx\.claude` 和 `C:\Users\xxx\.codex`，总结 4月9日到4月14日每天日报。”
- “先提取时间线，再压缩成适合发领导的工作日报。”
- “如果某天没有工作记录，也请明确列出。”
