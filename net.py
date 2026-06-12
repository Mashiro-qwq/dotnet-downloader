import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.request


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

RELEASES_JSON_TEMPLATE = "https://builds.dotnet.microsoft.com/dotnet/release-metadata/{version}/releases.json"


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def get_file_hash(file_path):
    hash_sha512 = hashlib.sha512()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_sha512.update(chunk)
    return hash_sha512.hexdigest().lower()


def main():
    output_file = "list.txt"
    hash_file = "hash.txt"
    aria2c_path = resource_path("aria2c.exe")

    print("正在获取 .NET 版本信息...")
    try:
        req = urllib.request.Request(GITHUB_JSON_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        valid_versions = []
        releases_urls = {}

        for release in data.get("releases-index", []):
            phase = release.get("support-phase", "").strip().lower()
            channel_version = release.get("channel-version", "").strip()
            latest_release = release.get("latest-release", "").strip()

            if phase in ["active", "maintenance"] and re.match(r'^\d+\.\d+\.\d+$', latest_release):
                releases_json_url = RELEASES_JSON_TEMPLATE.format(version=channel_version)
                print(f"发现 .NET {channel_version} ({latest_release}) - {phase}")
                valid_versions.append(latest_release)
                releases_urls[channel_version] = releases_json_url

        if not valid_versions:
            print("未找到可用的 .NET 版本。")
            input("\n按任意键退出...")
            return

        print("正在获取文件哈希值...")
        hash_map = {}

        for channel_version, releases_url in releases_urls.items():
            try:
                req = urllib.request.Request(releases_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req) as resp:
                    release_data = json.loads(resp.read().decode())

                for rel in release_data.get("releases", []):
                    for category in ["runtime", "aspnetcore-runtime", "windowsdesktop"]:
                        if category in rel:
                            for file_info in rel[category].get("files", []):
                                url = file_info.get("url")
                                file_hash = file_info.get("hash")
                                if url and file_hash:
                                    hash_map[url.lower()] = file_hash.lower()
            except Exception as e:
                print(f"获取 {channel_version} releases.json 失败: {e}")

        with open(hash_file, "w", encoding="utf-8") as f:
            f.write("# 文件哈希对照表 (SHA512)  格式:  URL  hash\n\n")
            for version in valid_versions:
                for template in URL_TEMPLATES:
                    url = template.format(version=version)
                    file_hash = hash_map.get(url.lower(), "获取哈希值失败")
                    f.write(f"{url}  {file_hash}\n")

        print(f"哈希对照表已保存至 {hash_file}")

        total_tasks = len(valid_versions) * len(URL_TEMPLATES)

        print("\n" + "=" * 60)
        choice = input("是否开始下载？ [Y/n] ").strip().lower()

        if choice not in ["", "y", "yes"]:
            print("操作已取消。")
            input("\n按任意键退出...")
            return

        print(f"正在生成下载列表 {output_file}，共 {total_tasks} 个文件...")

        with open(output_file, "w", encoding="utf-8") as f:
            for version in valid_versions:
                for template in URL_TEMPLATES:
                    link = template.format(version=version)
                    f.write(link + "\n")
                    f.write(f"  dir=./.Net {version}\n")

        print("启动 aria2c 下载...")
        cmd = [
            aria2c_path,
            "-i", output_file,
            "-j", "8",
            "-s", "16",
            "-x", "16",
            "-k", "1M"
        ]

        try:
            result = subprocess.run(cmd)
            if result.returncode != 0:
                print(f"下载失败，返回代码: {result.returncode}")
        except KeyboardInterrupt:
            print("下载已被用户中断。")

        print("\n" + "=" * 60)
        print("下载完成，开始哈希校验...")

        all_passed = True
        for version in valid_versions:
            dir_path = f"./.Net {version}"
            if not os.path.exists(dir_path):
                continue

            for template in URL_TEMPLATES:
                url = template.format(version=version)
                filename = url.split('/')[-1]
                file_path = os.path.join(dir_path, filename)

                if os.path.exists(file_path):
                    expected_hash = hash_map.get(url.lower())
                    if expected_hash:
                        actual_hash = get_file_hash(file_path)
                        if actual_hash == expected_hash:
                            print(f"{filename} 校验通过")
                        else:
                            print(f"{filename} 校验失败")
                            all_passed = False
                    else:
                        print(f"{filename} 哈希值不存在")
                else:
                    print(f"{filename} 文件不存在")

        if all_passed:
            print("\n所有文件哈希校验通过。")
        else:
            print("\n部分文件校验失败，请重试。")

        print("\n" + "=" * 60)
        del_choice = input(f"是否删除下载列表 {output_file} 和哈希对照表 {hash_file}？ [Y/n] ").strip().lower()
        if del_choice in ["", "y", "yes"]:
            if os.path.exists(output_file):
                os.remove(output_file)
            if os.path.exists(hash_file):
                os.remove(hash_file)
            print("删除完毕。")

    except FileNotFoundError:
        print("错误：未找到 aria2c")
    except Exception as e:
        print(f"发生错误: {e}")

    input("\n程序执行完毕，按任意键退出...")


if __name__ == "__main__":
    main()