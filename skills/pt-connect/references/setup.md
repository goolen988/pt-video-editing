# 按任务准备环境

先用 `state.py check --workspace <项目目录>` 确认当前主机能读取和写入项目、能执行命令。`doctor.py` 会列出 Python、FFmpeg、FFprobe、Node 和 yt-dlp 的发现结果；这些结果只说明工具是否存在，不代表对应任务已通过。

## 基础剪辑

需要 Python 3.9+、FFmpeg 和 FFprobe。检查 FFmpeg 是否有 `ass` 滤镜和 `libx264` 编码器。若用户本机已装 Homebrew，可按其正常权限流程用 `brew install ffmpeg`；否则查阅 [FFmpeg 下载页](https://ffmpeg.org/download.html) 对应系统的安装方法。不要悄悄安装包管理器。

安装后，在项目中生成一个短小的本地测试视频并确认能播放，再把实际产物记下来：

```bash
python3 <skill>/scripts/state.py record-smoke \
  --workspace <项目目录> \
  --capability ffmpeg-render \
  --result passed \
  --artifact <项目内的测试视频>
```

脚本会确认产物在项目目录内，并保存相对路径、文件大小和 SHA-256。不要用工具版本号代替真实渲染结果。

## 转录

优先使用已有且已核验的逐词时间戳转录。否则在项目内创建虚拟环境并安装 `faster-whisper`，再运行视频编辑 skill 的 `transcribe.py`。模型会在首次运行时下载。先处理短样本，核对语言并试听不确定的词；源音频无声时不要编造转录。

只有实际生成并检查过转录结果后，才记录转录能力通过。按具体任务选择是否保留测试音频和转录文件；不要把模型下载或包安装本身记成成功转录。

## JavaScript 图形

需要 Node 20+ 时，在用户项目中执行 `npm install --save-dev playwright@1.58.2` 和 `npx playwright install chromium`，保留 `package-lock.json`。用 `NODE_PATH=<项目目录>/node_modules` 运行编辑 skill 的 `graphics.cjs`。无字幕的干净剪辑或纯字幕文件不需要浏览器安装。

运行一次实际图形渲染并查看输出后，记录对应 smoke。Playwright 可执行文件存在不等于浏览器控制或图形渲染已经核验。

## 参考视频下载

优先使用用户已提供的文件。对于公开且受支持的网址，可在隔离环境中安装或使用 yt-dlp，检查可用格式后再下载，并记录来源网址。浏览器登录与下载是不同的主机能力；登录由用户完成。若访问失败，请用户提供导出的文件，不要从缩略图猜测参考风格。

## 外部音乐和图片服务

先阅读视频编辑 skill 的 services reference。网站登录、API 凭据和商业使用权是三个不同状态。不要把非官方服务称为厂商官方 API。尚待登录时，按当前主机记录服务状态：

```bash
python3 <skill>/scripts/state.py record-login \
  --workspace <项目目录> --service image-provider --status pending
```

用户完成交互登录，并且你实际核验服务调用后，才可将该主机的状态改为 `verified`。不要把密码、令牌、密钥或登录页面内容写进状态文件。另一台主机的登录状态需单独核验。

## 恢复与排错

恢复工作时先读 `.pt-connect.json`，再运行 `state.py check` 和本次任务需要的 smoke。状态文件按主题和用户语言保留已讲过的 setup 说明；重复检查不会清除已有说明、服务状态或 smoke 记录。每台主机的权限、登录和 smoke 单独保存，换主机后重新核验。

如果项目目录不可写，先说明本机限制和需要的权限，勿把状态改存全局目录。若状态文件无法读取或 schema 不受支持，保留原文件并检查后再修复，不要静默覆盖。所有记录只含项目/主机检查、语言、服务状态和 smoke 产物摘要，不含凭据。

如果 FFmpeg 缺少 `libass`（有些构建会如此），渲染器会自动使用 JavaScript/Playwright 绘制字幕。可按需安装该依赖，或在 `captions: false` 时输出干净剪辑并保留 SRT；用户要求的字幕不能悄悄省略。
