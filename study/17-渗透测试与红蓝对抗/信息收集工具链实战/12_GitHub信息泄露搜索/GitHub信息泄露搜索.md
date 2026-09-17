# GitHub信息泄露搜索

### 11.1 GitHub Dorking高级技巧

```bash
# 使用GitHub API搜索敏感信息
# 基本搜索语法:
# - filename:.env AWS_SECRET
# - extension:pem private
# - path:/.ssh/ id_rsa
# - filename:config.php password
# - filename:docker-compose.yml password

# TruffleHog - 自动化密钥扫描
# 安装
pip install trufflehog3
# 或
go install github.com/trufflesecurity/trufflehog@latest

# 扫描GitHub仓库
trufflehog github https://github.com/org/repo

# 扫描GitHub组织
trufflehog github --org=organization

# 扫描GitHub用户
trufflehog github --user=username

# 扫描全组织(需要GitHub Token)
trufflehog github --org=company --token=ghp_xxxx

# GitHound - GitHub敏感信息搜索
# 安装
pip install githound

# 使用
echo "target.com" | githound --dig
echo "company_name" | githound --manyresults

# 配置文件(.githound)
# threads: 5
# pages_to_scan: 50
# language: all
```

### 11.2 GitHub搜索自动化脚本

```python
#!/usr/bin/env python3
"""GitHub信息泄露自动化搜索工具"""

import requests
import re
import json
from datetime import datetime, timedelta

class GitHubDorker:
    def __init__(self, token):
        self.headers = {"Authorization": f"token {token}"}
        self.base_url = "https://api.github.com/search/code"

    def search_code(self, query, per_page=100):
        """搜索GitHub代码"""
        params = {"q": query, "per_page": per_page, "sort": "indexed"}
        response = requests.get(self.base_url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        return None

    def search_leaks(self, target_domain):
        """搜索目标域名相关的泄露"""
        dorks = [
            f'"{target_domain}" filename:.env',
            f'"{target_domain}" filename:config',
            f'"{target_domain}" filename:settings',
            f'"{target_domain}" filename:docker-compose',
            f'"{target_domain}" filename:.git-config',
            f'"{target_domain}" API_KEY',
            f'"{target_domain}" API_SECRET',
            f'"{target_domain}" password',
            f'"{target_domain}" AWS_SECRET_ACCESS_KEY',
            f'"{target_domain}" private_key',
            f'"{target_domain}" BEGIN RSA PRIVATE',
        ]
        results = []
        for dork in dorks:
            print(f"[*] 搜索: {dork}")
            data = self.search_code(dork)
            if data and data.get("total_count", 0) > 0:
                for item in data["items"]:
                    results.append({
                        "dork": dork,
                        "repository": item["repository"]["full_name"],
                        "file_path": item["path"],
                        "html_url": item["html_url"],
                    })
        return results

# 使用示例
if __name__ == "__main__":
    dorker = GitHubDorker("ghp_your_token_here")
    leaks = dorker.search_leaks("example.com")
    for leak in leaks:
        print(f"[!] 发现: {leak['repository']} - {leak['file_path']}")
        print(f"    URL: {leak['html_url']}")
```

---

---

## 📋 内容审核与补充建议

> 针对「GitHub信息泄露搜索」部分的内容审核结果：

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
