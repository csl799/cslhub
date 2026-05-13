# test-react-agent

基于 **ReAct**（思考 → 行动 → 观察）循环的本地智能体：调用 DeepSeek Chat API，在指定**项目目录**下读写文件、执行终端命令，直到模型给出 `<final_answer>`。

## 环境要求

- [uv](https://docs.astral.sh/uv/)（推荐）或 pip
- Python **≥ 3.14**（见 `pyproject.toml`）
- 有效的 [DeepSeek](https://www.deepseek.com/) API Key

## 快速开始

1. **克隆或进入项目目录**

2. **安装依赖**

   ```bash
   uv sync
   ```

3. **配置 API Key**

   复制示例环境文件并填写密钥：

   ```bash
   copy .env_example .env
   ```

   在 `.env` 中设置：

   ```env
   DEEPSEEK_API_KEY=你的密钥
   ```

4. **运行**

   ```bash
   uv run agent.py
   ```

   启动后按提示输入 `Task:` 中的任务描述即可。

## 用法说明

### 命令行参数

`PROJECT_DIRECTORY` 为**可选**参数，表示智能体的工作区（所有相对路径的文件读写、以及终端命令的 `cwd` 均相对于该目录解析）。

```bash
# 使用当前目录作为工作区（默认）
uv run agent.py

# 使用指定子目录作为工作区（需事先存在该文件夹）
uv run agent.py test_1
```

> **注意**：`PROJECT_DIRECTORY` 必须是**已存在的目录**。若误用同名**文件**代替文件夹，Click 会报错。

### 交互流程

1. 输入任务后，智能体会循环请求模型。
2. 模型每轮需按系统提示输出 XML 风格标签，常见为 `<thought>` + `<action>` 或 `<thought>` + `<final_answer>`。
3. 当动作为 `run_terminal_command` 时，会询问 `Continue? (y/n):`，输入 **`y`** 表示同意执行该命令，**非 y** 则取消并结束运行。
4. 工具执行结果会以 `<observation>` 形式反馈给模型，进入下一轮。

### 纯问答 vs 需要工具

- **不需要工具**时：模型应在 `<thought>` 后输出完整的 `<final_answer>...</final_answer>`，不要编造不存在的工具。
- **需要工具**时：输出 `<thought>` 与成对的 `<action>...</action>`；不要在回复中伪造 `<observation>`（由程序注入）。

若模型只写了未闭合的 `<final_answer>`，或既无完整 `final_answer` 也无完整 `action>`，程序会向对话追加纠正提示并继续请求模型，而不会立刻崩溃。

## 内置工具

| 工具 | 作用 |
|------|------|
| `read_file` | 读取文件内容（相对路径相对于 `PROJECT_DIRECTORY`） |
| `write_to_file` | 写入文件；父目录不存在时会自动创建 |
| `run_terminal_command` | 在 `PROJECT_DIRECTORY` 下执行 shell 命令（需用户确认） |

系统提示中会列出工具签名与说明；模型输出 `<action>` 的语法需与 `parse_action` 解析规则一致（形如 `tool_name(arg1, arg2)`）。

## 项目结构（主要文件）

| 文件 | 说明 |
|------|------|
| `agent.py` | CLI 入口：解析工作区目录、收集任务、启动 `ReActAgent` |
| `ReActAgent.py` | 与 DeepSeek 对话、解析标签、执行工具包装（路径解析、`cwd`） |
| `Use_tools.py` | 原始工具实现（读写、子进程命令） |
| `prompt_template.py` | ReAct 系统提示模板 |
| `pyproject.toml` | 项目元数据与依赖 |

## 常见问题

**PowerShell 里 `cd ... && uv run ...` 报错**  
旧版 PowerShell 可能不支持 `&&`，可改用：

```powershell
Set-Location "路径\to\test_react_agent"; uv run agent.py
```

**希望生成的文件落在子目录（如 `test_1`）下**  
请传入该目录作为参数：`uv run agent.py test_1`，并让模型使用相对路径（如 `index.html`）；相对路径会解析到该工作区内。

## 许可证

由仓库维护者自行补充。
