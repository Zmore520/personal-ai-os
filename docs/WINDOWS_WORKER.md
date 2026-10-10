# Optional Windows 11 Worker / 可选本地验证器

The Worker is a one-shot offline validation command. It reads a complete downloaded snapshot and writes a new report outside the workspace. It never watches Drive, wakes Muse, executes task text, or uploads a result.

```powershell
py -3 -m paos worker C:\PAOS\snapshot --report C:\PAOS\reports\check-001.json
```

Run from the repository directory, or install the package first. Exit code 0 means validation succeeded; 2 means invalid input, missing directory, report collision, or file error. Report files are exclusively created and contain counts only. Use a new name for each run. Missing/invalid files fail without a success report.

Windows Task Scheduler can invoke this command if the user explicitly configures a schedule. Set its working directory to the repository checkout. Use a wrapper to generate a unique report filename and record exit codes. Scheduled validation does not download snapshots or make consumer assistants run; downloads still require an independently configured and authorized transport.

Do not run several writers against the same workspace, and do not treat a synced Drive folder as a transaction queue. First obtain a stable, complete local snapshot. Windows behavior is checked by the included GitHub Actions matrix; this release does not install a Windows service.

中文：Worker 只做离线验证，输出到独立目录；不会执行任务、自动连接 Muse、下载 Drive 或绕过产品审批。定时运行需用户自行明确配置，不能据此声称端到端自动协作已经实现。
