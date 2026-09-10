#!/usr/bin/env python3
# dir_bruter.py
# 简单目录爆破脚本
# 用法: python dir_bruter.py <URL> <字典文件>

import requests
import sys
import time

def dir_brute(base_url, wordlist_path, extensions=None, timeout=5):
    """目录爆破"""
    if extensions is None:
        extensions = [""]

    # 读取字典
    try:
        with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
            words = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        print(f"[!] 字典文件不存在: {wordlist_path}")
        sys.exit(1)

    print(f"[*] 目标 URL: {base_url}")
    print(f"[*] 字典大小: {len(words)}")
    print(f"[*] 扩展名: {extensions}")
    print("[*] 开始爆破...\n")

    base_url = base_url.rstrip("/")
    found = []
    start_time = time.time()
    count = 0

    for word in words:
        for ext in extensions:
            path = f"{word}{ext}"
            url = f"{base_url}/{path}"

            try:
                response = requests.get(
                    url,
                    timeout=timeout,
                    allow_redirects=False,
                    headers={"User-Agent": "DirBruter/1.0"}
                )

                status = response.status_code
                length = len(response.content)

                if status == 200:
                    print(f"[+] [{status}] {url} (长度: {length})")
                    found.append((status, url, length))
                elif status == 403:
                    print(f"[*] [{status}] {url} (禁止访问)")
                elif status == 301 or status == 302:
                    redirect = response.headers.get("Location", "")
                    print(f"[>] [{status}] {url} → {redirect}")

            except requests.exceptions.Timeout:
                pass
            except requests.exceptions.ConnectionError:
                print(f"[!] 连接失败: {url}")
                break
            except Exception:
                pass

        count += 1
        if count % 100 == 0:
            print(f"[*] 进度: {count}/{len(words)}")

    elapsed = time.time() - start_time
    print(f"\n[*] 爆破完成，耗时 {elapsed:.2f} 秒")
    print(f"[+] 共发现 {len(found)} 个路径")

    return found

def generate_sample_wordlist(path):
    """生成示例字典文件"""
    words = [
        "admin", "login", "register", "upload", "download",
        "backup", "config", "test", "api", "user",
        "users", "index", "home", "dashboard", "console",
        "manager", "admin.php", "login.php", "config.php",
        ".git", ".svn", ".env", "robots.txt", "sitemap.xml",
        "phpinfo.php", "info.php", "test.php", "admin/login",
        "wp-admin", "wp-login.php", "admin/config.php",
    ]
    with open(path, "w", encoding="utf-8") as f:
        for word in words:
            f.write(word + "\n")
    print(f"[*] 已生成示例字典: {path}")

def main():
    if len(sys.argv) != 3:
        print(f"用法: {sys.argv[0]} <URL> <字典文件>")
        print(f"示例: {sys.argv[0]} http://example.com wordlist.txt")
        print(f"\n如果没有字典，可以先生成示例:")
        print(f"  python {sys.argv[0]} --gen-wordlist wordlist.txt")
        sys.exit(1)

    if sys.argv[1] == "--gen-wordlist":
        generate_sample_wordlist(sys.argv[2])
        sys.exit(0)

    url = sys.argv[1]
    wordlist = sys.argv[2]

    if not url.startswith("http"):
        url = "http://" + url

    dir_brute(url, wordlist)

if __name__ == "__main__":
    main()
