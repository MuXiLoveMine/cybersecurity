#!/usr/bin/env python3
# web_crawler.py
# 简单 Web 爬虫
# 用法: python web_crawler.py <起始URL> [深度]

import requests
import sys
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

def is_same_domain(url1, url2):
    """判断是否同一域名"""
    return urlparse(url1).netloc == urlparse(url2).netloc

def crawl(start_url, max_depth=2, timeout=5):
    """广度优先爬虫"""
    base_domain = urlparse(start_url).netloc
    visited = set()
    queue = [(start_url, 0)]

    print(f"[*] 起始 URL: {start_url}")
    print(f"[*] 最大深度: {max_depth}")
    print(f"[*] 域名限制: {base_domain}")
    print("[*] 开始爬取...\n")

    found_urls = []

    while queue:
        url, depth = queue.pop(0)

        if url in visited or depth > max_depth:
            continue

        # 只爬取同域名
        if not is_same_domain(url, start_url):
            continue

        visited.add(url)
        print(f"[{depth}] {url}")
        found_urls.append((depth, url))

        try:
            response = requests.get(url, timeout=timeout, headers={
                "User-Agent": "Mozilla/5.0 (compatible; SimpleCrawler/1.0)"
            })

            if "text/html" not in response.headers.get("Content-Type", ""):
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            # 提取所有链接
            for link in soup.find_all("a", href=True):
                href = link["href"].strip()
                full_url = urljoin(url, href)

                # 去掉锚点和参数
                full_url = full_url.split("#")[0].split("?")[0]

                if full_url.startswith("http") and full_url not in visited:
                    queue.append((full_url, depth + 1))

            # 提取页面标题
            title = soup.title.string.strip() if soup.title else "无标题"
            print(f"      标题: {title}")

        except requests.exceptions.RequestException as e:
            print(f"      错误: {e}")
        except Exception as e:
            print(f"      解析错误: {e}")

    print(f"\n[*] 爬取完成，共访问 {len(found_urls)} 个页面")
    return found_urls

def extract_links(url):
    """提取页面所有链接"""
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        links = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            text = link.get_text(strip=True)
            links.append((text, href))

        return links
    except Exception as e:
        print(f"错误: {e}")
        return []

def main():
    if len(sys.argv) < 2:
        print(f"用法: {sys.argv[0]} <URL> [深度]")
        print(f"示例: {sys.argv[0]} https://example.com 2")
        sys.exit(1)

    url = sys.argv[1]
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 2

    if not url.startswith("http"):
        url = "http://" + url

    crawl(url, depth)

if __name__ == "__main__":
    main()
