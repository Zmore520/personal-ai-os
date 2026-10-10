# Personal AI OS

**由用户掌控的文件协作桥：让消费级 AI 通过独立 Markdown 文件异步交接。**

[English](README.md) · [协议](docs/PROTOCOL.md) · [架构](docs/ARCHITECTURE.md) · [安全](SECURITY.md)

ChatGPT 与 Meta Muse 在账户具备且用户授权连接器时，通过私有 Google Drive 工作区交换文件；没有连接器时，可由用户手动传递。用户审核共享记忆、决定权限和外部行动。本仓库提供可运行的离线工具、抽象协议和完全合成的示例。

这是非官方社区项目，不是计算机操作系统，也不代表 OpenAI、Meta 或 Google 官方集成。工具可用性和权限以具体账户为准。

## 已实现与未实现

| 能力 | v0.1 状态 |
|---|---|
| 独立 Markdown 消息、回执与挑战回声检查 | 本地实现 |
| 任务指派、状态链、版本冲突检查、过期标记 | 已实现；不执行任务 |
| 记忆建议 pending、独立人工审核、confirmed 导出 | 已实现；不认证作者身份 |
| Windows 11 可选本地 Worker | 已实现一次性离线验证 |
| Google Drive 上传与下载 | 用户使用现有连接器或手动操作；没有内置 OAuth 适配器 |
| ChatGPT 与 Muse 原生自动连接 | 未实现 |
| 实时监听、自动唤醒其他 AI、产品内部记忆同步 | 未实现 |
| Muse 定时轮询 | 账户相关实验，本仓库未验证其运行成功 |

项目起点是一次私有实验中报告的用户触发读取、独立文件写入与回读。原始记录不公开，这些报告不能证明全天在线或所有账户都能使用。公开 Demo 完全模拟双方，不调用任何 AI 服务。

## 快速运行

需要 Python 3.10 以上版本，无运行时第三方依赖。在下载或克隆的项目目录运行：

```sh
python -m paos.demo workspace/demo
python -m paos validate workspace/demo
python -m paos queue workspace/demo --agent muse_demo
python -m paos memories workspace/demo
python -m unittest discover -s tests -v
```

Windows 可将 `python` 替换为 `py -3`。Demo 要求目标目录尚不存在，生成八份虚构文件：登记、消息、回执、任务、领取、完成、记忆建议和人工审核。示例日期固定为 2030 年，超过该日期后队列会标记过期。

可选：`python -m pip install .` 后使用 `paos` 命令。发行包名称为 `personal-ai-os-filebridge`，仓库名称为 `personal-ai-os`，目前未声称已发布到 PyPI。

## 接入 Drive

1. 建立专用私有测试目录，仅放非敏感内容。公开代码仓库与真实工作数据分开。
2. Agent 先登记 pending，核对实际授权范围、读取与新建文件能力。没有连接器就明确记录手动传递。
3. 消息中发送全新、非秘密的挑战值，对方写独立回执。核对精确回声、双方身份字段及原文件未改动。回声仅证明读到文本，不证明账户身份。
4. 用户批准后登记 active。每项任务只指派一位执行者，领取和完成各写新文件，不修改原任务。
5. 下载完整快照到本地独立目录后验证。缺失前置文件、重复 ID 和任务分叉都会报错。上传后核对字节或哈希；Drive 允许重名文件，不能只检查文件名。
6. 记忆先 pending，由用户另写审核记录。`memories` 只导出已确认且未被新版替代的内容。

CLI 不连接云端、不发送消息、不授予连接器权限。创建新记录：

```sh
python -m paos create workspace/demo --metadata new-message.json --body message.txt
```

格式参考 [协议](docs/PROTOCOL.md) 和 `examples/exchange`；启动协作可使用 [接入提示词](docs/ONBOARDING.md)，本地定时验证参考 [Windows Worker](docs/WINDOWS_WORKER.md)。

## 关键边界

任务采用不可变原件与独立状态事件。验证器发现版本分叉就停止，不猜测哪个写入者正确。本地独占创建能避免文件覆盖，但 Drive 和下载快照没有分布式锁。需要并发执行、自动重试和外部副作用时，先引入事务队列与权限系统。

`allowed_actions`、`human` 标签和登记表只是声明，恶意写入者可以伪造。人工审批必须在真实用户会话和访问控制中核对；本工具不认证用户，不执行文件正文，也不同步消费版产品内部记忆。

贡献请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。MIT 许可见 [LICENSE](LICENSE)。概念参考共享黑板模式与 [agent-handoff-kit](https://github.com/jimozo/agent-handoff-kit)，未复制第三方实现，也未宣称已完成其安全审计。
