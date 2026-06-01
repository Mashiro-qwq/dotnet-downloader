# .NET Downloader

一个简单高效的 **.NET 运行时批量下载工具**（Windows 专用）

自动获取 Microsoft 官方最新的 **Active** 和 **Maintenance** 支持版本的 .NET 运行时，并使用 aria2c 进行高速多线程下载。

---

## ✨ 特性

- 自动从 Microsoft 获取最新版本
- 支持以下运行时批量下载：
  - ASP.NET Core Runtime（x64 + x86）
  - .NET Hosting Bundle
  - Windows Desktop Runtime（x64 + x86）
  - .NET Runtime（x64 + x86）
- 多线程高速下载，支持断点续传
- 自动按版本创建文件夹整理下载文件
- 下载完成后自动清理临时文件
- 简洁易用，适合开发者、部署人员批量更新 .NET 环境
- 使用 PyInstaller 打包，内置aria2c

---

## 📦 自行打包

请准备以下文件放在同一目录：
- `net.py`（主程序）
- `aria2c.exe`
- `net.ico`（可选图标）

然后执行以下命令打包：

```bash
pyinstaller --onefile --console --add-binary "aria2c.exe;." --icon "net.ico" --name "DotNetDownloader" net.py
```

打包完成后可在 `dist` 文件夹找到 `DotNetDownloader.exe`

## 📋 前置要求

- Windows 系统
- 无需 Python 环境和 aria2

---

## 🚀 使用方法

1. 下载 [releases](https://github.com/Mashiro-qwq/dotnet-downloader/releases) 的 `DotNetDownloader.exe`
2. 将文件放到任意目录并双击运行
3. 程序会自动列出当前可下载的 .NET 版本
4. 输入 `Y` 确认开始下载

下载完成后，所有文件将按版本保存在 `./.Net x.x.x` 文件夹中。

---