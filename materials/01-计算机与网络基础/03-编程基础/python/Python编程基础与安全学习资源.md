# Python 编程基础与安全学习资源

> 本文系统介绍 Python 在网络安全中的定位、Python 编程基础（安全视角）、常用工具链、安全核心库、2026 年免费学习资源、推荐 GitHub 项目，以及两个可运行的示例代码文件（basics.py 和 security_cases.py）。面向安全初学者与安全工程师，全部内容从防御、自动化和授权测试的正向角度出发。

---

## 目录

- [一、Python 在网络安全中的定位](#一python-在网络安全中的定位)
- [二、Python 编程基础（安全视角）](#二python-编程基础安全视角)
- [三、常用命令与工具链](#三常用命令与工具链)
- [四、Python 安全核心库](#四python-安全核心库)
- [五、2026 年免费学习资源](#五2026-年免费学习资源)
- [六、2026 年推荐 GitHub 项目](#六2026-年推荐-github-项目)
- [七、示例代码文件](#七示例代码文件)
- [附：优化后的提示词模板](#附优化后的提示词模板)

---

## 一、Python 在网络安全中的定位

### 1.1 为什么安全从业者首选 Python

**Python** 是网络安全领域的通用语言（General-Purpose Language for Security），也是自动化与工具开发的首选。

| 优势 | 说明 |
|------|------|
| **语法简洁** | 接近自然语言，学习曲线平缓，入门快 |
| **生态丰富** | 安全相关的库和工具特别多，几乎你想做的都有现成的库 |
| **跨平台** | Windows/Linux/macOS 都能跑，脚本一次编写到处运行 |
| **快速原型** | 想法 → 代码 → 验证，整个过程可能只要几十分钟 |
| **社区活跃** | 大量安全工具用 Python 开发，学习资源和例子极多 |
| **够用的性能** | 对大多数安全任务（自动化、扫描、分析）来说性能够用 |

### 1.2 Python 在安全领域的应用方向

| 方向 | Python 的作用 | 典型场景 |
|------|-------------|---------|
| **安全运营 / SOC** | 自动化告警处理、日志分析、报告生成 | 日志批量分析、告警分诊、威胁情报查询 |
| **安全运维** | 批量运维、基线检查、配置管理 | 安全基线检查脚本、补丁分发、账号审计 |
| **渗透测试（授权）** | 信息收集、漏洞验证、POC 开发 | 端口扫描器、目录爆破、漏洞验证脚本 |
| **Web 安全** | Web 工具开发、漏洞扫描、Payload 构造 | SQL 注入验证、XSS 检测脚本、爬虫 |
| **威胁情报** | 情报收集、关联分析、IOC 管理 | 多源情报聚合、信誉查询工具、IOC 批量检测 |
| **应急响应** | 日志分析、取证脚本、批量处置 | 日志取证、内存分析脚本、IOC 扫描工具 |
| **代码审计** | 自动化审计工具、漏洞模式匹配 | 静态代码扫描、依赖漏洞检测 |
| **数据分析** | 安全数据处理、可视化、统计 | 流量分析、用户行为分析、趋势预测 |

> ⚠️ **重要声明**：Python 本身是中性的工具，本文所有内容均从防御、自动化和授权测试的角度讲解。使用 Python 开发的任何工具和脚本，只能在自己管理的或有明确书面授权的系统上使用。未经授权对他人系统进行扫描、探测、漏洞利用是违法行为。

---

## 二、Python 编程基础（安全视角）

### 2.1 环境搭建

#### Python 版本选择

| 版本 | 状态 | 推荐 | 说明 |
|------|------|------|------|
| Python 3.12 | 当前稳定版 | ⭐⭐⭐⭐⭐ 推荐 | 性能优化、新特性多 |
| Python 3.11 | 广泛使用 | ⭐⭐⭐⭐ 推荐 | 大部分库都兼容 |
| Python 3.10 | 稳定 | ⭐⭐⭐ 可用 | 老系统上常见 |
| Python 2.x | 已停止维护 | ❌ 不要用 | 2020 年 1 月 1 日起已 EOL |

> **建议**：学习用最新稳定版（3.11+），生产环境看具体情况。注意 Python 2 和 Python 3 不兼容，不要学 Python 2。

#### 虚拟环境 venv

虚拟环境（Virtual Environment）是 Python 项目的标配——每个项目有自己独立的依赖，互不干扰。

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux / macOS
source venv/bin/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat

# 退出虚拟环境
deactivate

# 导出依赖列表
pip freeze > requirements.txt

# 从依赖列表安装
pip install -r requirements.txt
```

> **为什么要用虚拟环境？**
> - 不同项目需要不同版本的库，放在一起会冲突
> - 项目可以一键部署到其他机器（pip install -r requirements.txt）
> - 不会搞乱系统全局的 Python 环境

#### pip 包管理

```bash
# 安装包
pip install requests
pip install requests==2.31.0      # 指定版本
pip install requests>=2.31.0      # 最低版本

# 升级包
pip install --upgrade requests
pip install -U pip                # 升级 pip 自身

# 卸载包
pip uninstall requests

# 查看已安装的包
pip list
pip freeze                        # 适合导出到 requirements.txt

# 搜索包（需要 pip-search 或用 PyPI 网站）
# 推荐直接去 pypi.org 搜索

# 更换国内镜像源（加速下载）
pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple

# 永久设置镜像源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2.2 数据类型

安全工作中最常用的数据类型：

| 类型 | 英文 | 说明 | 安全场景示例 |
|------|------|------|-------------|
| **字符串** | str | 文本数据 | 日志内容、URL、IP 地址、域名、哈希值 |
| **整数** | int | 整数 | 端口号、状态码、计数 |
| **浮点数** | float | 小数 | 时间戳、延迟、置信度 |
| **布尔值** | bool | True / False | 检测结果、条件判断 |
| **列表** | list | 有序、可变的序列 | IP 列表、端口列表、漏洞列表、日志行 |
| **字典** | dict | 键值对（key-value） | 漏洞详情、配置项、IP → 端口映射 |
| **元组** | tuple | 有序、不可变的序列 | 固定的键值对、返回多个值 |
| **集合** | set | 无序、去重 | IOC 去重、白名单对比、求交集/并集 |
| **字节** | bytes | 二进制数据 | 原始网络数据包、加密数据、二进制文件 |

**常用操作速查**：

```python
# ===== 字符串 =====
s = "Hello, Security World!"
s.lower()               # 转小写
s.upper()               # 转大写
s.startswith("Hello")   # 以...开头
s.endswith("!")         # 以...结尾
s.find("Security")      # 查找子串
s.replace("!", ".")     # 替换
s.split(", ")           # 分割成列表
", ".join(["a","b"])    # 列表合并成字符串
f"IP: {ip}, Port: {port}"  # f-string 格式化

# ===== 列表 =====
ips = ["1.1.1.1", "8.8.8.8", "1.1.1.1"]
ips.append("9.9.9.9")   # 添加元素
ips.remove("1.1.1.1")   # 删除第一个匹配
len(ips)                # 长度
"8.8.8.8" in ips        # 是否包含
ips[0]                  # 索引访问
ips[-1]                 # 最后一个
ips[0:2]                # 切片
for ip in ips:          # 遍历
    print(ip)

# ===== 字典 =====
vuln = {
    "name": "CVE-2024-1234",
    "severity": "high",
    "port": 8080
}
vuln["name"]            # 取值
vuln["cvss"] = 9.8      # 添加/修改
del vuln["port"]        # 删除
vuln.keys()             # 所有键
vuln.values()           # 所有值
vuln.items()            # 键值对
for k, v in vuln.items():
    print(f"{k}: {v}")

# ===== 集合 =====
ioc_set = {"1.1.1.1", "2.2.2.2", "3.3.3.3"}
ioc_set.add("4.4.4.4")  # 添加
ioc_set.remove("1.1.1.1")  # 删除
white_set = {"2.2.2.2", "5.5.5.5"}
ioc_set - white_set     # 差集（去掉白名单后的）
ioc_set & white_set     # 交集（既在 IOC 也在白名单的）
```

### 2.3 控制流

```python
# ===== if/elif/else =====
severity = "high"
if severity == "critical":
    print("立即处理")
elif severity == "high":
    print("尽快处理")
elif severity == "medium":
    print("计划处理")
else:
    print("低优先级")

# 比较运算符：== != > < >= <=
# 逻辑运算符：and or not
# 成员运算符：in not in

# ===== for 循环 =====
# 遍历列表
ips = ["1.1.1.1", "2.2.2.2", "3.3.3.3"]
for ip in ips:
    print(f"Scanning {ip}...")

# 带索引
for idx, ip in enumerate(ips):
    print(f"[{idx+1}] {ip}")

# 遍历字典
config = {"host": "0.0.0.0", "port": 8080, "debug": False}
for key, value in config.items():
    print(f"{key} = {value}")

# range
for i in range(10):     # 0 到 9
    print(i)
for i in range(1, 101): # 1 到 100
    pass

# ===== while 循环 =====
count = 0
while count < 10:
    print(count)
    count += 1

# 循环控制：
#   break    跳出循环
#   continue 跳过本次，继续下一次
```

### 2.4 函数与模块

```python
# ===== 函数定义 =====
def check_port(ip, port, timeout=5):
    """检查端口是否开放

    Args:
        ip: 目标 IP 地址
        port: 目标端口
        timeout: 超时时间（秒），默认 5 秒

    Returns:
        bool: 端口开放返回 True，否则返回 False
    """
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False

# 调用函数
is_open = check_port("127.0.0.1", 80)
is_open = check_port("127.0.0.1", 80, timeout=2)  # 指定超时

# ===== 模块导入 =====
import os                       # 导入整个模块
import socket as sock           # 导入并重命名
from os import path             # 导入模块中的某个函数/变量
from os.path import exists      # 导入子模块的函数
from collections import *       # 导入所有（不推荐，容易冲突）

# 标准库（Python 自带，不需要安装）：
#   os/sys           系统相关
#   re               正则表达式
#   json/csv         数据格式
#   socket           网络编程
#   subprocess       子进程
#   argparse         命令行参数
#   logging          日志
#   datetime/time    时间处理
#   hashlib          哈希
#   shutil           文件操作
#   pathlib          路径处理
```

### 2.5 文件处理

```python
# ===== 文本文件 =====
# 读取整个文件
with open("log.txt", "r", encoding="utf-8") as f:
    content = f.read()

# 逐行读取（大文件推荐，省内存）
with open("log.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()  # 去掉换行和空白
        if "Failed password" in line:
            print(line)

# 写入文件
with open("result.txt", "w", encoding="utf-8") as f:
    f.write("Hello\n")
    f.write("World\n")

# 追加写入
with open("result.txt", "a", encoding="utf-8") as f:
    f.write("New line\n")

# ===== JSON =====
import json

# 读取 JSON
with open("data.json", "r") as f:
    data = json.load(f)  # 转成 Python 字典/列表

# 写入 JSON
with open("output.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# JSON 字符串互转
json_str = json.dumps({"name": "test"})  # 字典 → 字符串
data = json.loads('{"name": "test"}')    # 字符串 → 字典

# ===== CSV =====
import csv

# 读取 CSV
with open("vulns.csv", "r") as f:
    reader = csv.DictReader(f)  # 用字典读取，第一行是表头
    for row in reader:
        print(row["IP"], row["Port"], row["Vulnerability"])

# 写入 CSV
with open("report.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["IP", "Port", "Status"])
    writer.writeheader()
    writer.writerow({"IP": "1.1.1.1", "Port": 80, "Status": "open"})

# ===== YAML（需要安装 PyYAML）=====
# pip install pyyaml
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
```

### 2.6 异常处理

```python
# 基础用法
try:
    result = 10 / 0
except ZeroDivisionError:
    print("不能除以零")
except Exception as e:
    print(f"其他错误: {e}")
else:
    print("没有异常才执行")
finally:
    print("不管有没有异常都执行（清理资源）")

# 常见异常类型
#   Exception         所有异常的基类
#   ValueError        值错误
#   TypeError         类型错误
#   IndexError        列表索引越界
#   KeyError          字典键不存在
#   FileNotFoundError 文件不存在
#   PermissionError   权限不足
#   socket.timeout    Socket 超时
#   requests.exceptions.RequestException  请求异常

# 安全脚本中的最佳实践：
# - 不要裸 except:（会捕获所有异常，包括 Ctrl+C）
# - 捕获具体的异常类型
# - 记录异常信息（logging），方便排查
# - finallly 中释放资源（关闭文件、关闭连接）

import logging

try:
    # 一些操作
    pass
except socket.timeout:
    logging.warning("连接超时")
except Exception as e:
    logging.error(f"发生错误: {e}", exc_info=True)
```

### 2.7 正则表达式

正则表达式（Regular Expression）是安全脚本中最常用的技能之一——提取 IP、域名、URL、邮箱、哈希值等都要用到。

```python
import re

# 常用元字符：
#   .       任意字符（除了换行）
#   *       0 次或多次
#   +       1 次或多次
#   ?       0 次或 1 次
#   \d      数字
#   \w      字母数字下划线
#   \s      空白字符
#   ^       开头
#   $       结尾
#   [abc]   字符集（a/b/c 中的一个）
#   (abc)   分组
#   a|b     或
#   {n}     恰好 n 次
#   {n,m}   n 到 m 次

# ===== 安全常用正则 =====

# IP 地址（简化版）
ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
# 更精确的 IPv4
ip_pattern = r'(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)'

# 邮箱
email_pattern = r'[\w.-]+@[\w.-]+\.\w+'

# URL
url_pattern = r'https?://[\w./?=&%-]+'

# 域名
domain_pattern = r'[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}'

# MD5 哈希
md5_pattern = r'[a-fA-F0-9]{32}'

# SHA256 哈希
sha256_pattern = r'[a-fA-F0-9]{64}'

# ===== re 模块常用函数 =====

# search：搜索第一个匹配
text = "IP 地址是 192.168.1.1 和 10.0.0.1"
match = re.search(ip_pattern, text)
if match:
    print(match.group())  # 第一个匹配的 IP

# findall：找出所有匹配
ips = re.findall(ip_pattern, text)
print(ips)  # ['192.168.1.1', '10.0.0.1']

# match：从开头匹配（不常用）
re.match(r'\d+', '123abc')  # 匹配 123

# sub：替换
text = re.sub(ip_pattern, '[REDACTED]', text)

# compile：预编译（多次使用时效率高）
pattern = re.compile(ip_pattern)
pattern.findall(text)

# 分组提取
log_line = '192.168.1.1 - - [10/Oct/2024:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 1234'
log_pattern = r'(\S+) - - \[([^\]]+)\] "(\S+) (\S+) \S+" (\d+) (\d+)'
m = re.match(log_pattern, log_line)
if m:
    ip = m.group(1)
    time_str = m.group(2)
    method = m.group(3)
    path = m.group(4)
    status = m.group(5)
    size = m.group(6)
```

> **推荐工具**：regex101.com —— 在线正则表达式测试工具，可以实时验证、解释语法、生成各种语言的代码，学正则必备。

### 2.8 面向对象基础

面向对象（OOP）在安全工具开发中很有用——把功能封装成类，代码更清晰、更易复用。

```python
# 类的定义
class PortScanner:
    """简单的端口扫描器类（仅用于授权测试）"""

    def __init__(self, target_ip, timeout=3):
        """初始化

        Args:
            target_ip: 目标 IP 地址
            timeout: 连接超时时间
        """
        self.target_ip = target_ip
        self.timeout = timeout
        self.open_ports = []

    def scan_port(self, port):
        """扫描单个端口"""
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target_ip, port))
            sock.close()
            if result == 0:
                self.open_ports.append(port)
                return True
            return False
        except Exception:
            return False

    def scan_range(self, start_port, end_port):
        """扫描一个端口范围"""
        for port in range(start_port, end_port + 1):
            self.scan_port(port)

    def get_result(self):
        """获取扫描结果"""
        return {
            "target": self.target_ip,
            "open_ports": self.open_ports,
            "count": len(self.open_ports)
        }


# 使用
scanner = PortScanner("127.0.0.1", timeout=2)
scanner.scan_range(1, 100)
result = scanner.get_result()
print(f"开放端口: {result['open_ports']}")

# ===== 继承 =====
class FastPortScanner(PortScanner):
    """多线程版本的端口扫描器（继承基础版）"""

    def __init__(self, target_ip, timeout=3, threads=10):
        super().__init__(target_ip, timeout)  # 调用父类初始化
        self.threads = threads

    def scan_range(self, start_port, end_port):
        """重写：多线程扫描"""
        import threading
        # 多线程实现...
        pass
```

---

## 三、常用命令与工具链

### 3.1 核心命令

| 命令 | 作用 | 常用示例 |
|------|------|---------|
| `python` | 运行 Python 解释器或脚本 | `python script.py`、`python -c "print('hello')"` |
| `pip` | 包管理工具 | `pip install requests`、`pip list` |
| `venv` | 虚拟环境（标准库） | `python -m venv venv` |
| `ipython` | 增强的交互式 Shell | `ipython` |
| `pdb` | 调试器（标准库） | `python -m pdb script.py` |
| `pytest` | 单元测试框架 | `pytest tests/` |

### 3.2 调试工具

```bash
# ===== pdb（Python Debugger）=====
# 代码中插入断点
import pdb; pdb.set_trace()  # Python 3.6 及以下
breakpoint()                   # Python 3.7+ 推荐

# 常用调试命令：
#   n (next)        下一行
#   s (step)        进入函数
#   c (continue)    继续运行
#   p <变量>        打印变量
#   l (list)        查看代码
#   q (quit)        退出调试

# 从命令行启动调试
python -m pdb script.py

# ===== ipython =====
# 安装
pip install ipython

# 启动
ipython

# 比默认 Python shell 强的地方：
#   - 语法高亮
#   - Tab 补全
#   - 魔术命令（%timeit、%run 等）
#   - 历史记录更好用
#   - 帮助信息更友好
```

### 3.3 代码质量工具

| 工具 | 作用 | 说明 |
|------|------|------|
| **pylint** | 代码静态分析 | 检查代码规范、潜在错误、复杂度 |
| **flake8** | 代码检查 | 轻量，检查 PEP8 规范和逻辑错误 |
| **black** | 代码格式化 | 自动格式化代码，统一风格 |
| **mypy** | 类型检查 | 静态类型检查，提前发现类型错误 |

```bash
# 安装
pip install black flake8 pylint mypy

# 格式化代码（自动修改）
black script.py

# 检查代码问题
flake8 script.py
pylint script.py

# 类型检查
mypy script.py
```

---

## 四、Python 安全核心库

### 4.1 核心库总览

| 库名 | 用途 | 安装 | 重要性 |
|------|------|------|--------|
| **Requests** | HTTP 请求 / API 交互 | `pip install requests` | ⭐⭐⭐⭐⭐ |
| **Scapy** | 数据包构造 / 网络扫描 | `pip install scapy` | ⭐⭐⭐⭐ |
| **BeautifulSoup** | HTML / XML 解析 | `pip install beautifulsoup4` | ⭐⭐⭐⭐ |
| **Pandas** | 数据分析 / 日志处理 | `pip install pandas` | ⭐⭐⭐⭐ |
| **Paramiko** | SSH 自动化 | `pip install paramiko` | ⭐⭐⭐ |
| **python-nmap** | Nmap 扫描封装 | `pip install python-nmap` | ⭐⭐⭐ |
| **Cryptography** | 加密 / 解密 / 证书 | `pip install cryptography` | ⭐⭐⭐⭐ |
| **subprocess** | 调用系统命令 | 标准库，无需安装 | ⭐⭐⭐⭐⭐ |
| **re** | 正则表达式 | 标准库 | ⭐⭐⭐⭐⭐ |
| **socket** | 网络编程 | 标准库 | ⭐⭐⭐⭐ |
| **argparse** | 命令行参数 | 标准库 | ⭐⭐⭐⭐ |
| **logging** | 日志记录 | 标准库 | ⭐⭐⭐⭐ |

### 4.2 Requests — HTTP 请求与 API 交互

安全工作中最常用的库，没有之一——调用 API、爬网页、验证漏洞，都要用。

```python
import requests

# ===== GET 请求 =====
response = requests.get("https://api.example.com/vulns")
print(response.status_code)   # 状态码
print(response.text)          # 响应文本
print(response.json())        # 解析 JSON（返回字典）
print(response.headers)       # 响应头

# 带参数
params = {"ip": "1.1.1.1", "type": "full"}
response = requests.get("https://api.example.com/query", params=params)
# URL 变成 https://api.example.com/query?ip=1.1.1.1&type=full

# ===== POST 请求 =====
# JSON 数据
data = {"username": "admin", "password": "test"}
response = requests.post("https://api.example.com/login", json=data)

# 表单数据
response = requests.post("https://example.com/login", data=data)

# ===== 高级用法 =====

# 请求头
headers = {
    "User-Agent": "SecurityScanner/1.0",
    "Authorization": "Bearer <token>",
    "X-API-Key": "your-api-key"
}
response = requests.get(url, headers=headers)

# 超时（一定要设，不然可能卡住）
response = requests.get(url, timeout=10)  # 10 秒超时

# 代理
proxies = {
    "http": "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080"
}
response = requests.get(url, proxies=proxies, verify=False)

# SSL 证书验证（⚠️ 仅测试环境用，生产环境不要关）
response = requests.get(url, verify=False)  # 跳过证书验证
import urllib3; urllib3.disable_warnings()  # 关掉警告

# 会话（保持 Cookie）
session = requests.Session()
session.post(login_url, data=creds)  # 登录
response = session.get(protected_url)  # 已登录状态访问

# 错误处理
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # 状态码不是 2xx 就抛异常
except requests.exceptions.Timeout:
    print("请求超时")
except requests.exceptions.ConnectionError:
    print("连接失败")
except requests.exceptions.HTTPError as e:
    print(f"HTTP 错误: {e}")
except requests.exceptions.RequestException as e:
    print(f"请求异常: {e}")
```

### 4.3 Scapy — 数据包构造与网络扫描

Scapy 是一个强大的数据包操作库，可以构造、发送、捕获和解析各种网络协议的数据包。

```python
from scapy.all import *

# ⚠️ Scapy 操作网络数据包需要 root 权限
# 仅限授权网络环境使用

# ===== 构造数据包 =====
# IP 层 + ICMP 层
packet = IP(dst="8.8.8.8") / ICMP()

# 查看包结构
packet.show()
packet.summary()

# ===== 发送和接收 =====
# 发送一个包并等待响应
ans, unans = sr(IP(dst="8.8.8.8") / ICMP())
ans.summary()

# 发送不等待回应
send(IP(dst="8.8.8.8") / ICMP())

# ===== TCP 端口扫描 =====
# SYN 扫描（半开放扫描）
ans, unans = sr(IP(dst="192.168.1.1") / TCP(dport=80, flags="S"), timeout=2)
for sent, received in ans:
    if received.haslayer(TCP) and received[TCP].flags == "SA":
        print(f"端口 {sent[TCP].dport} 开放")

# ===== DNS 查询 =====
packet = IP(dst="8.8.8.8") / UDP(dport=53) / DNS(rd=1, qd=DNSQR(qname="example.com"))
response = sr1(packet, timeout=2)
if response and response.haslayer(DNSRR):
    print(response[DNSRR].rdata)

# ===== 抓包 =====
# 抓 10 个包
packets = sniff(count=10)
packets.summary()

# 抓特定协议的包
packets = sniff(filter="tcp port 80", count=10)

# 保存到 pcap 文件
wrpcap("capture.pcap", packets)

# 读取 pcap 文件
packets = rdpcap("capture.pcap")
```

> ⚠️ **Scapy 使用注意**：
> - 大部分功能需要 root 权限
> - 构造和发送数据包仅限授权环境
> - 生产环境慎用，避免影响正常业务

### 4.4 Paramiko — SSH 自动化

用于 SSH 连接远程服务器，执行命令、传输文件，批量运维必备。

```python
import paramiko

# ===== SSH 连接执行命令 =====
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 自动添加主机密钥

try:
    ssh.connect(
        hostname="192.168.1.100",
        port=22,
        username="user",
        password="password",
        # key_filename="/path/to/private_key",  # 也可以用密钥认证
        timeout=10
    )

    # 执行命令
    stdin, stdout, stderr = ssh.exec_command("whoami")
    output = stdout.read().decode()
    error = stderr.read().decode()
    print("输出:", output)
    print("错误:", error)

    # 执行多条命令
    commands = [
        "uname -a",
        "cat /etc/os-release",
        "df -h"
    ]
    for cmd in commands:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(f"$ {cmd}")
        print(stdout.read().decode())

finally:
    ssh.close()

# ===== SFTP 文件传输 =====
transport = paramiko.Transport(("192.168.1.100", 22))
transport.connect(username="user", password="password")
sftp = paramiko.SFTPClient.from_transport(transport)

# 上传文件
sftp.put("local_file.txt", "/remote/path/file.txt")

# 下载文件
sftp.get("/remote/path/file.txt", "local_file.txt")

# 列出目录
print(sftp.listdir("/remote/path"))

sftp.close()
transport.close()
```

### 4.5 BeautifulSoup — 网页解析

用于解析 HTML/XML，在 Web 安全中常用于爬虫、信息收集、提取网页内容。

```python
from bs4 import BeautifulSoup
import requests

# 获取网页
response = requests.get("https://example.com")
soup = BeautifulSoup(response.text, "html.parser")
# 也可以用 lxml 解析器（更快，需要安装）
# pip install lxml
# soup = BeautifulSoup(response.text, "lxml")

# ===== 查找元素 =====

# 按标签名
title = soup.find("title")
print(title.text)

# 按 id
main = soup.find(id="main")

# 按 class
links = soup.find_all("a", class_="external-link")

# 按属性
forms = soup.find_all("form", method="post")

# CSS 选择器
items = soup.select(".menu li a")
first = soup.select_one("#header .logo")

# ===== 提取信息 =====

# 获取文本
print(soup.get_text())

# 获取属性
for link in soup.find_all("a"):
    href = link.get("href")  # 或 link["href"]
    text = link.get_text(strip=True)
    print(f"{text}: {href}")

# 获取所有链接
all_links = [a.get("href") for a in soup.find_all("a") if a.get("href")]

# ===== 安全场景示例：表单检测 =====
# 找出所有表单，检查是否有 CSRF token
forms = soup.find_all("form")
for form in forms:
    action = form.get("action", "")
    method = form.get("method", "get").upper()
    has_csrf = form.find("input", {"name": "csrf_token"}) is not None
    print(f"表单: {method} {action}, CSRF token: {'有' if has_csrf else '⚠️ 没有'}")
```

### 4.6 Pandas — 日志与数据分析

Pandas 是强大的数据分析库，处理大量日志和安全数据时特别有用。

```python
import pandas as pd

# ===== 读取数据 =====
df = pd.read_csv("vulns.csv")         # CSV
df = pd.read_json("data.json")       # JSON
# 也可以从 Excel、数据库等读取

# ===== 基本操作 =====
df.head()          # 前 5 行
df.shape           # 行列数
df.columns         # 列名
df.describe()      # 统计信息

# ===== 数据筛选 =====
# 高危漏洞
high_risk = df[df["severity"] == "high"]

# 多条件
critical_high = df[df["severity"].isin(["critical", "high"])]

# 按 IP 统计
ip_counts = df["ip"].value_counts()

# ===== 统计分析 =====
# 按严重程度统计
severity_stats = df.groupby("severity").size()

# 每个 IP 的高危漏洞数
high_by_ip = df[df["severity"] == "high"].groupby("ip").size().sort_values(ascending=False)

# ===== 输出 =====
df.to_csv("report.csv", index=False)
df.to_json("report.json", orient="records")
df.to_excel("report.xlsx", index=False)  # 需要 openpyxl

# ===== 安全场景：日志分析 =====
# 解析 Nginx 日志（简化示例）
import re

log_pattern = r'(\S+) - - \[([^\]]+)\] "(\S+) (\S+) \S+" (\d+) (\d+)'
data = []

with open("access.log") as f:
    for line in f:
        m = re.match(log_pattern, line)
        if m:
            data.append({
                "ip": m.group(1),
                "time": m.group(2),
                "method": m.group(3),
                "path": m.group(4),
                "status": int(m.group(5)),
                "size": int(m.group(6))
            })

df = pd.DataFrame(data)

# 访问最多的 Top 10 IP
top_ips = df["ip"].value_counts().head(10)

# 404 最多的路径
not_found = df[df["status"] == 404]["path"].value_counts().head(10)
```

### 4.7 Cryptography — 加密与解密

现代 Python 加密库，比老的 pycrypto 更安全、更易用。

```python
# pip install cryptography

# ===== 对称加密（AES-GCM）=====
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

# Fernet 高级封装（简单安全，推荐用这个）
key = Fernet.generate_key()
cipher = Fernet(key)

# 加密
plaintext = b"敏感数据"
token = cipher.encrypt(plaintext)

# 解密
decrypted = cipher.decrypt(token)

# ===== 哈希 =====
from cryptography.hazmat.primitives import hashes

digest = hashes.Hash(hashes.SHA256())
digest.update(b"hello world")
hash_value = digest.finalize()
print(hash_value.hex())

# ===== 密码哈希（用于存储用户密码）=====
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

password = b"user_password"
salt = os.urandom(16)

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=480000,
)
key = kdf.derive(password)

# ===== 非对称加密（RSA）=====
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization

# 生成密钥对
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
public_key = private_key.public_key()

# 加密（用公钥）
ciphertext = public_key.encrypt(
    b"secret message",
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# 解密（用私钥）
plaintext = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
```

---

## 五、2026 年免费学习资源

### 5.1 资源总表

| 类别 | 资源名称 | 说明 | 适合阶段 | 链接 |
|------|---------|------|---------|------|
| **官方文档** | Python 官方教程 | 最权威的 Python 入门教程，支持中文 | 入门→进阶 | docs.python.org/zh-cn/3/tutorial/ |
| **交互式课程** | Microsoft Learn Python | 微软官方免费 Python 学习模块，交互式，路径清晰 | 入门 | learn.microsoft.com/zh-cn/training/paths/beginner-python/ |
| **完整课程** | freeCodeCamp Python | 免费完整的 Python 课程，视频+练习+项目 | 入门→进阶 | freecodecamp.org/learn/scientific-computing-with-python/ |
| **安全向 Python** | IT Dojo Essential Python | 面向安全从业者的 Python 基础课程 | 入门 | 搜索 "IT Dojo Essential Python" |
| **实战项目** | Python for Cybersecurity (GitHub) | 30 天 30 个安全程序，实战驱动 | 进阶 | GitHub 搜索 |
| **官方安全培训** | CISA Scripting Essentials | CISA 官方安全脚本培训（Python+Bash+PS） | 入门→进阶 | cisa.gov |
| **正则练习** | RegexOne | 交互式正则表达式入门教程 | 入门 | regexone.com |
| **正则测试** | RegEx101 | 在线正则测试和调试工具，支持多种语言 | 全程 | regex101.com |

### 5.2 资源使用建议

```
学习路径推荐：

  完全零基础：
    1. Microsoft Learn Python 或 freeCodeCamp（系统入门）
    2. Python 官方教程（作为参考和深入）
    3. 边学边做小练习

  有编程基础，想学安全应用：
    1. 快速过一遍 Python 语法（1~2 周）
    2. Python for Cybersecurity 项目（跟着做）
    3. 自己动手写工具

  想系统学：
    1. 跟一个完整的课程入门
    2. 做 3~5 个实战项目
    3. 读优秀开源安全工具的源码
    4. 自己开发一个工具
```

---

## 六、2026 年推荐 GitHub 项目

### 6.1 学习资源类

| 项目 | Stars | 说明 |
|------|-------|------|
| **h4cker** (Omar Santos) | ~30k⭐ | 数千条安全学习资源，大量 Jupyter Notebook，涵盖 Python、渗透、防御等 |
| **arceuzvx/Cybersecurity_resources** | 电子书合集 | 免费网络安全电子书合集，含 Black Hat Python、Violent Python 等 |
| **cutewizzy11/defensive-python-labs** | 防御性 Python | 防御性安全 Python 实验，纯 Python 安全工具集 |
| **farhanashrafdev/90DaysOfCyberSecurity** | 学习计划 | 90 天网络安全学习计划，涵盖 Python 等实战技能 |
| **Awesome Python Security** | 资源清单 | Python 安全相关库、工具、资源的精选列表 |

> **说明**：GitHub 项目的 Star 数和内容会随时间变化，建议直接搜索项目名获取最新信息。以上项目用于学习和研究，使用时请遵守各项目的开源协议和相关法律法规。

### 6.2 工具源码学习

读优秀开源安全工具的源码，是提升 Python 安全编程能力的好方法：

| 工具 | 说明 | 学习价值 |
|------|------|---------|
| **Nmap** (部分脚本) | 端口扫描器 | NSE 脚本学习 |
| **sqlmap** | SQL 注入工具 | 复杂安全工具的架构设计 |
| **mitmproxy** | 中间人代理 | 网络协议处理、插件架构 |
| **volatility3** | 内存取证框架 | 大型 Python 项目结构、插件系统 |
| **Poetry** | Python 包管理 | 现代 Python 项目结构 |

> ⚠️ **学习源码的原则**：读这些工具的源码是为了学习技术和架构，理解安全工具的工作原理，从而更好地防御和检测。不要将学到的知识用于未授权的攻击。

---

## 七、示例代码文件

本文配套两个可运行的 Python 示例文件，位于 `code/` 目录下：

### 7.1 basics.py — Python 基础示例

涵盖：数据类型、控制流、函数、文件操作、异常处理、类与对象、正则表达式。

**文件路径**：`code/basics.py`

**运行方式**：
```bash
cd code
python basics.py
```

### 7.2 security_cases.py — 安全案例示例

涵盖 3 个安全案例（防御/授权测试视角）：
- **端口扫描器**：使用 socket 的基础 TCP 端口扫描器（仅用于授权环境）
- **日志分析器**：分析认证日志，统计登录失败、异常 IP 等
- **哈希校验工具**：计算和校验文件哈希值（MD5/SHA256），用于文件完整性检查

**文件路径**：`code/security_cases.py`

**运行方式**：
```bash
cd code
python security_cases.py

# 也可以作为模块导入使用
from security_cases import LogAnalyzer, FileHashChecker
```

---

## 附：优化后的提示词模板

以下是可复用的 Python 安全编程类提示词模板：

```markdown
# 角色
你是一名资深网络安全与 Python 编程专家，精通 Python 在
安全自动化、工具开发、数据分析中的应用。

# 任务
请系统介绍【主题】，包括：
1. 概念与定位（在安全领域的作用）
2. 核心知识要点
   - 基础语法/概念
   - 安全相关的重点内容
3. 常用库/工具
   - 每个库：用途、安装、核心用法、安全场景示例
4. 实战项目（防御/授权测试角度）
   - 项目描述
   - 实现思路
   - 核心代码示例
5. 学习资源推荐（2026 年）
   - 官方文档
   - 免费教程
   - GitHub 项目
   - 书籍
6. 常见坑与最佳实践
7. 与其他安全技能的关系

# 输出要求
- Markdown 格式，按大类小类组织
- 表格对比，代码附详细注释
- 重要术语中英文对照
- 面向安全初学者、安全工程师
- 深度：概念理解 + 实战入门 + 安全应用

# 约束
- 仅从防御、自动化和授权测试角度讲解
- 不提供可直接用于未授权攻击的代码
- 强调正向用途
- 高风险操作给出警告
- 最后附"优化后的提示词模板"
```

**使用说明**：将【主题】替换为"Requests 库安全实战""Scapy 网络编程""Web 爬虫与安全""Python 数据分析与安全""Python 取证脚本开发""Python 自动化运维"等，即可生成同等深度和结构的 Python 安全编程专题文档。

---

> **总结**：Python 是安全从业者的核心技能之一——它语法简单、生态丰富、跨平台，几乎在安全的各个方向都能派上用场。学习 Python 要从基础开始（数据类型、控制流、函数、文件处理），然后逐步接触网络编程、安全库和工具开发。核心库中，Requests（HTTP）、re（正则）、socket（网络）是最常用的，几乎每个安全脚本都要用；Scapy、Paramiko、BeautifulSoup、Pandas、Cryptography 等根据方向选学。学习资源非常丰富，官方文档、freeCodeCamp、Microsoft Learn 都是免费且高质量的入门资源，GitHub 上有大量优秀的安全项目可以读源码学习。最重要的是多写多练——跟着做项目、自己造工具、参与开源，在实战中快速提升。记住：Python 是工具，关键是你用它来做什么——用在防御和授权测试上，它就是保护系统的有力武器。
