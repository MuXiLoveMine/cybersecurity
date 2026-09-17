#!/usr/bin/env python3
# port_scanner.py
# 简单端口扫描脚本
# 用法: python port_scanner.py <主机> <起始端口> <结束端口>

import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def scan_port(host, port, timeout=1):
    """扫描单个端口"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return port, result == 0
    except Exception:
        return port, False

def port_scan(host, start_port, end_port, max_threads=100):
    """多线程端口扫描"""
    print(f"[*] 开始扫描 {host}:{start_port}-{end_port}")
    print(f"[*] 线程数: {max_threads}")
    start_time = time.time()

    open_ports = []
    total = end_port - start_port + 1
    scanned = 0

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {
            executor.submit(scan_port, host, port): port
            for port in range(start_port, end_port + 1)
        }

        for future in as_completed(futures):
            port, is_open = future.result()
            scanned += 1
            if is_open:
                open_ports.append(port)
                print(f"[+] 端口 {port} 开放")

            # 进度
            if scanned % 100 == 0 or scanned == total:
                progress = scanned / total * 100
                print(f"[*] 进度: {scanned}/{total} ({progress:.1f}%)")

    elapsed = time.time() - start_time
    print(f"\n[*] 扫描完成，耗时 {elapsed:.2f} 秒")
    print(f"[+] 开放端口: {sorted(open_ports)}")
    print(f"[+] 共 {len(open_ports)} 个开放端口")

    return open_ports

def main():
    if len(sys.argv) != 4:
        print(f"用法: {sys.argv[0]} <主机> <起始端口> <结束端口>")
        print(f"示例: {sys.argv[0]} 127.0.0.1 1 1000")
        sys.exit(1)

    host = sys.argv[1]
    try:
        start_port = int(sys.argv[2])
        end_port = int(sys.argv[3])
    except ValueError:
        print("错误：端口必须是数字")
        sys.exit(1)

    if start_port < 1 or end_port > 65535 or start_port > end_port:
        print("错误：端口范围无效 (1-65535)")
        sys.exit(1)

    port_scan(host, start_port, end_port)

if __name__ == "__main__":
    main()
