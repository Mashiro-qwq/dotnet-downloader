import json
import urllib.request
import re
import subprocess
import os

GITHUB_JSON_URL = "https://raw.githubusercontent.com/dotnet/core/refs/heads/main/release-notes/releases-index.json"

URL_TEMPLATES = [
    "https://builds.dotnet.microsoft.com/dotnet/aspnetcore/Runtime/{version}/aspnetcore-runtime-{version}-win-x64.exe",
    "https://builds.dotnet.microsoft.com/dotnet/aspnetcore/Runtime/{version}/aspnetcore-runtime-{version}-win-x86.exe",
    "https://builds.dotnet.microsoft.com/dotnet/aspnetcore/Runtime/{version}/dotnet-hosting-{version}-win.exe",
    "https://builds.dotnet.microsoft.com/dotnet/WindowsDesktop/{version}/windowsdesktop-runtime-{version}-win-x64.exe",
    "https://builds.dotnet.microsoft.com/dotnet/WindowsDesktop/{version}/windowsdesktop-runtime-{version}-win-x86.exe",
    "https://builds.dotnet.microsoft.com/dotnet/Runtime/{version}/dotnet-runtime-{version}-win-x64.exe",
    "https://builds.dotnet.microsoft.com/dotnet/Runtime/{version}/dotnet-runtime-{version}-win-x86.exe"
]

def main():
    output_file = "download.txt"
    valid_versions = []
    
    print("正在获取 .NET 版本信息...")
    try:
        req = urllib.request.Request(GITHUB_JSON_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            
        for release in data.get("releases-index", []):
            phase = release.get("support-phase", "").strip().lower()
            channel_version = release.get("channel-version", "").strip()
            latest_version = release.get("latest-release", "").strip()
            
            if phase in ["active", "maintenance"] and re.match(r'^\d+\.\d+\.\d+$', latest_version):
                print(f"找到.Net {channel_version} 版本: {latest_version} (状态: {phase})")
                valid_versions.append(latest_version)
                        
        if not valid_versions:
            print("\n未找到任何符合条件的 active 或 maintenance 正式版本。")
            return
            
        total_tasks = len(valid_versions) * len(URL_TEMPLATES)
        
        print("\n" + "="*50)
        choice = input("是否执行下载？ [Y/n] ").strip().lower()
        
        if choice in ["", "y", "yes"]:
            print(f"\n正在写入配置文件: {output_file}，共计 {total_tasks} 个文件...")
            
            with open(output_file, "w", encoding="utf-8") as f:
                for latest_version in valid_versions:
                    for template in URL_TEMPLATES:
                        link = template.format(version=latest_version)
                        f.write(link + "\n")
                        f.write(f"  dir=./.Net {latest_version}\n")
            
            print("\n启动 aria2c 下载...\n")
            
            cmd = [
                "aria2c", 
                "-i", output_file, 
                "-j", "8", 
                "-s", "16", 
                "-x", "16", 
                "-k", "1M"
            ]
            
            try:
                result = subprocess.run(cmd)
                
                if result.returncode == 0:
                    print("\n" + "="*50)
                    print("所有文件下载成功！正在清理配置文件...")
                    if os.path.exists(output_file):
                        os.remove(output_file)
                        print(f"已删除文件: {output_file}")
                else:
                    print("\n" + "="*50)
                    print(f"aria2c 未能完全下载 (错误代码: {result.returncode})。")
                    print(f"输入：aria2c -i '{output_file}' 以执行断点续传")
            
            except KeyboardInterrupt:
                print("\n" + "="*50)
                print(f"[!] 已强行终止下载任务。")
                
        else:
            print("\n用户取消，程序已退出。")
            
    except FileNotFoundError:
        print("\n错误：未在系统环境变量中找到 'aria2c' 命令。")
    except Exception as e:
        print(f"\n请求或运行失败: {e}")

if __name__ == "__main__":
    main()
