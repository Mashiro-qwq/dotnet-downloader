# .NET Downloader

一个简单高效的 **.NET 运行时批量下载工具**（Windows 专用）

自动获取 Microsoft 官方最新的 **Active** 和 **Maintenance** 支持版本的 .NET 运行时，并使用 aria2c 进行高速多线程下载。

---

## ✨ 特性

- 自动从官方 `releases-index.json` 获取最新稳定版本
- 支持以下运行时批量下载：
  - ASP.NET Core Runtime（x64 + x86）
  - .NET Hosting Bundle
  - Windows Desktop Runtime（x64 + x86）
  - .NET Runtime（x64 + x86）
- 使用 **aria2c** 高速下载（多线程 + 断点续传）
- 自动按版本创建文件夹整理下载文件
- 下载完成后自动清理临时文件
- 简洁易用，适合开发者、部署人员批量更新 .NET 环境

---

## 📋 前置要求

- Windows 系统
- 已安装 [aria2](https://aria2.github.io/)（需将 `aria2c.exe` 添加到系统环境变量）

> **推荐安装方式**：使用 Scoop（`scoop install aria2`）或 Chocolatey（`choco install aria2`）

---

## 🚀 使用方法

1. 下载本仓库的 `download.py` 文件
2. 将文件放到任意目录并双击运行（或在终端执行 `python download.py`）
3. 程序会自动列出当前可下载的 .NET 版本
4. 输入 `Y` 确认开始下载

下载完成后，所有文件将按版本保存在 `./.Net x.x.x` 文件夹中。

---