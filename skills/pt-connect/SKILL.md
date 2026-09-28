---
name: pt-connect
description: 为 PT 视频编辑项目建立或恢复本机工作能力；处理桌面权限、媒体工具、浏览器登录或渲染依赖时使用。
---
# PT Connect

把本机 setup 做清楚，并把可核验状态留在用户授权的项目里。工具存在不代表对应能力已经可用。

1. 确认用户授权的项目目录。先读已有状态，再检查本次主机：
   - `python3 <skill>/scripts/state.py status --workspace <项目目录>`
   - `python3 <skill>/scripts/doctor.py --workspace <项目目录>`
   - `python3 <skill>/scripts/state.py check --workspace <项目目录>`
   `check` 会重新核验当前主机的项目读写权限、命令执行，并记录工具版本。恢复时也要重跑；不同主机各自核验，不沿用另一台机器的权限或能力记录。可用 `--host-id <稳定主机名>` 指定主机标识。
2. 按用户实际使用的语言说明 setup 结果和下一步。只在说明确实讲完后记录，例如：`python3 <skill>/scripts/state.py record-explanation --workspace <项目目录> --topic first-setup --language zh-CN`。同一主题、同一语言已有记录时可跳过重复解释；换语言要补讲。优先沿用用户当前语言；没有语言线索时默认英文，不为这个问题打断首次剪辑。
3. 只为当前任务读取 [setup.md](references/setup.md) 中相关部分。按本机正常权限流程安装确实需要的依赖；避免全局安装，也不要把订阅或外部账号当作基础剪辑的前置条件。
4. 对需要的能力做一次真实的小操作。成功且产物已写入项目后，用 `record-smoke` 保存项目相对路径、SHA-256 和主机；失败时可记录 `--result failed`。仅发现可执行文件不能证明转码、字幕、转录、浏览器控制或服务认证可用。
5. 交互式登录尚未完成时，按主机记录服务为 `pending`；只有实际完成并核验服务操作后才记 `verified`。记录中不放密码、令牌、密钥或登录内容。状态保存在项目根目录的 `.pt-connect.json`，不会写入全局模型记忆。
6. 用简单语言告诉用户当前可用的能力、还需登录或处理的项目，以及可继续做的任务。主机、权限或依赖变化后重新检查相关能力。不要把录音悄悄上传到云端替代本机能力。

单次预计超过 $5 的付费调用，先说明费用并等待用户确认再提交。
