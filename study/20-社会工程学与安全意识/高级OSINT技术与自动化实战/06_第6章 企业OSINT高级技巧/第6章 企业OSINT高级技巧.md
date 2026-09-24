# 第6章 企业OSINT高级技巧

### 6.1 企业组织架构图重建

#### 6.1.1 信息收集维度

重建企业组织架构需要从多个维度收集信息：

**公开来源：**
- LinkedIn公司页面和员工档案
- 公司官网的"关于我们"、"团队"页面
- 新闻报道和采访
- 招聘信息（职位层级、部门划分）
- 内部演讲和技术分享
- 员工社交媒体信息

**推断方法：**
- 职位名称推断层级
- 汇报关系推断（LinkedIn关系、会议出席）
- 部门命名规律推断组织架构
- 员工数量和增长趋势推断

#### 6.1.2 组织架构重建步骤

**步骤1：确定组织规模和层级**
- 员工总数（LinkedIn显示、招聘信息推断）
- 管理层级：从CEO到基层员工有几层
- 部门划分：按职能/产品/地域

**步骤2：识别关键人物**
- 高管层：CEO、CTO、CFO、VP等
- 中层管理者：各部门负责人
- 技术骨干：安全负责人、架构师等
- 信息安全相关岗位

**步骤3：填充部门结构**
- 按部门分类收集员工信息
- 确定各部门的负责人
- 标注部门间的汇报关系

**步骤4：验证和细化**
- 交叉验证不同来源的信息
- 通过会议、演讲等信息确认汇报关系
- 标注信息的可信度

#### 6.1.3 自动化工具实现

```python
import json
import re
from collections import defaultdict

class OrgChartReconstructor:
    def __init__(self):
        self.employees = []
        self.departments = defaultdict(list)
    
    def add_employee(self, name, title, department=None, 
                     manager=None, source=None, confidence=0.5):
        """添加员工信息"""
        employee = {
            'name': name,
            'title': title,
            'department': department,
            'manager': manager,
            'source': source,
            'confidence': confidence,
            'level': self._estimate_level(title)
        }
        self.employees.append(employee)
        
        if department:
            self.departments[department].append(employee)
        
        return employee
    
    def _estimate_level(self, title):
        """根据职位名称估计层级"""
        title_lower = title.lower()
        
        # C级高管
        if any(x in title_lower for x in ['ceo', 'cto', 'cfo', 'coo', 'chief']):
            return 'C-level'
        
        # VP级别
        if any(x in title_lower for x in ['vice president', 'vp', '副总裁']):
            return 'VP'
        
        # 总监级别
        if any(x in title_lower for x in ['director', '总监']):
            return 'Director'
        
        # 经理级别
        if any(x in title_lower for x in ['manager', '经理', '主管', 'leader']):
            return 'Manager'
        
        # 高级工程师
        if any(x in title_lower for x in ['senior', '高级', '资深', 'lead']):
            return 'Senior'
        
        # 普通员工
        return 'Individual Contributor'
    
    def analyze_structure(self):
        """分析组织架构"""
        # 按层级统计
        level_counts = defaultdict(int)
        for emp in self.employees:
            level_counts[emp['level']] += 1
        
        # 按部门统计
        dept_stats = {}
        for dept, members in self.departments.items():
            levels = defaultdict(int)
            for m in members:
                levels[m['level']] += 1
            dept_stats[dept] = {
                'total': len(members),
                'levels': dict(levels)
            }
        
        return {
            'total_employees': len(self.employees),
            'level_distribution': dict(level_counts),
            'department_stats': dept_stats,
            'estimated_depth': self._estimate_depth()
        }
    
    def _estimate_depth(self):
        """估计组织深度（层级数）"""
        levels_order = [
            'C-level', 'VP', 'Director', 
            'Manager', 'Senior', 'Individual Contributor'
        ]
        existing_levels = set(emp['level'] for emp in self.employees)
        
        depth = 0
        for level in levels_order:
            if level in existing_levels:
                depth += 1
        
        return depth
    
    def find_security_team(self):
        """识别安全团队成员"""
        security_keywords = [
            'security', '安全', '渗透', '攻防', 'vulnerability',
            '漏洞', 'sdl', 'devsecops', 'soc', 'siem', 'ciso'
        ]
        
        security_team = []
        for emp in self.employees:
            title_lower = emp['title'].lower()
            if any(kw in title_lower for kw in security_keywords):
                security_team.append(emp)
        
        return security_team
    
    def generate_org_chart(self):
        """生成组织架构图数据（可用于可视化）"""
        # 按层级和部门组织
        chart = {
            'nodes': [],
            'edges': []
        }
        
        # 添加节点
        for emp in self.employees:
            chart['nodes'].append({
                'id': emp['name'],
                'label': f"{emp['name']}\n{emp['title']}",
                'level': emp['level'],
                'department': emp['department'],
                'confidence': emp['confidence']
            })
        
        # 添加边（汇报关系，如果已知manager）
        for emp in self.employees:
            if emp.get('manager'):
                chart['edges'].append({
                    'from': emp['manager'],
                    'to': emp['name'],
                    'relation': 'reports_to'
                })
        
        return chart
```

### 6.2 员工邮箱枚举与验证

#### 6.2.1 邮箱格式推断

**常见企业邮箱格式：**

| 格式 | 示例 | 常见程度 |
|------|------|---------|
| first.last@domain | john.smith@company.com | 非常常见 |
| firstlast@domain | johnsmith@company.com | 常见 |
| flast@domain | jsmith@company.com | 常见 |
| first@domain | john@company.com | 小公司 |
| lastf@domain | smithj@company.com | 较少 |
| 工号@domain | 12345@company.com | 大企业 |

**推断方法：**
1. 收集已知的员工邮箱（从LinkedIn、论文、会议等）
2. 分析邮箱命名规律
3. 生成可能的邮箱列表
4. 验证邮箱是否存在

#### 6.2.2 邮箱发现方法

**主动发现：**
- Hunter.io、Snov.io等邮箱查找工具
- LinkedIn邮箱导出工具
- 公司官网员工页面
- 域名WHOIS信息
- SSL证书信息

**被动发现：**
- Google搜索：`@company.com email`
- 代码仓库中的提交记录
- 文档元数据（PDF、Office文档）
- 公开的邮件列表存档
- 泄露数据库查询

#### 6.2.3 邮箱验证技术

**验证方法：**

1. **SMTP验证**
   - 连接目标邮件服务器
   - 使用VRFY或RCPT TO命令
   - 检查服务器响应
   - 注意：可能触发安全告警

2. **语法验证**
   - 检查邮箱格式是否正确
   - 验证域名是否存在MX记录
   - 不能确认邮箱是否真实存在

3. **基于行为的验证**
   - 密码找回功能
   - 注册功能（提示邮箱已注册）
   - 登录功能的错误提示差异

```python
import dns.resolver
import smtplib
import re
import requests

class EmailValidator:
    def __init__(self):
        self.results = {}
    
    def validate_format(self, email):
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def check_mx_records(self, domain):
        """检查域名的MX记录"""
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            return [
                {
                    'priority': r.preference,
                    'exchange': str(r.exchange)
                }
                for r in mx_records
            ]
        except Exception as e:
            print(f"MX查询失败: {e}")
            return []
    
    def smtp_verify(self, email, from_email='test@example.com'):
        """通过SMTP验证邮箱是否存在
        
        注意：此方法可能触发目标服务器的安全检测
        """
        domain = email.split('@')[1]
        mx_records = self.check_mx_records(domain)
        
        if not mx_records:
            return {'valid': False, 'reason': '无MX记录'}
        
        # 使用优先级最高的MX服务器
        mx_server = mx_records[0]['exchange']
        
        try:
            server = smtplib.SMTP(timeout=10)
            server.connect(mx_server, 25)
            server.helo()
            server.mail(from_email)
            code, message = server.rcpt(email)
            server.quit()
            
            if code == 250:
                return {'valid': True, 'confidence': 0.8}
            elif code == 550:
                return {'valid': False, 'confidence': 0.9}
            else:
                return {
                    'valid': 'unknown', 
                    'code': code,
                    'message': message.decode('utf-8', errors='ignore')
                }
                
        except Exception as e:
            return {'valid': 'unknown', 'error': str(e)}
    
    def generate_email_variants(self, first_name, last_name, domain):
        """生成可能的邮箱变体"""
        variants = []
        f = first_name.lower()
        l = last_name.lower()
        fi = first_name[0].lower()
        li = last_name[0].lower()
        
        # 常见格式
        patterns = [
            f"{f}.{l}",          # john.smith
            f"{f}{l}",           # johnsmith
            f"{fi}{l}",          # jsmith
            f"{f}{li}",          # johns
            f"{f}",              # john
            f"{l}",              # smith
            f"{f}-{l}",          # john-smith
            f"{fi}.{l}",         # j.smith
            f"{l}{fi}",          # smithj
            f"{f}_{l}",          # john_smith
        ]
        
        for pattern in patterns:
            variants.append(f"{pattern}@{domain}")
        
        return variants
    
    def batch_validate(self, emails):
        """批量验证邮箱"""
        results = {}
        
        for email in emails:
            if not self.validate_format(email):
                results[email] = {'valid': False, 'reason': '格式错误'}
                continue
            
            # 检查MX记录
            domain = email.split('@')[1]
            mx = self.check_mx_records(domain)
            if not mx:
                results[email] = {'valid': False, 'reason': '无MX记录'}
                continue
            
            # SMTP验证（谨慎使用）
            # result = self.smtp_verify(email)
            # results[email] = result
            
            # 仅验证域名和格式
            results[email] = {
                'valid': 'possible',
                'format_valid': True,
                'mx_valid': True,
                'confidence': 0.3
            }
        
        return results
```

### 6.3 子域名与IP资产发现

#### 6.3.1 子域名发现方法

**被动发现：**
- 搜索引擎（site:domain.com）
- 证书透明度日志（crt.sh）
- DNS记录聚合服务（SecurityTrails、PassiveTotal）
- Wayback Machine存档
- VirusTotal子域名信息
- Threat Intelligence平台

**主动发现：**
- 字典爆破（subfinder、amass、gobuster）
- 通配符DNS检测
- DNS区域传输（如果配置错误）
- 证书SAN字段提取
- 递归发现（子域名的子域名）

#### 6.3.2 资产发现工具链

**工具组合：**
```
子域名发现 → 存活检测 → 端口扫描 → 服务识别 → 技术栈识别
   ↓            ↓           ↓           ↓           ↓
subfinder     httpx       nmap       whatweb    wappalyzer
amass        httprobe    masscan    nikto      builtwith
assetfinder  katana      naabu      gobuster   wfuzz
```

**自动化流程：**
```python
import subprocess
import os
import json

class SubdomainDiscovery:
    def __init__(self, domain, output_dir="results"):
        self.domain = domain
        self.output_dir = os.path.join(output_dir, domain)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def run_subfinder(self):
        """使用subfinder发现子域名"""
        output_file = os.path.join(self.output_dir, "subfinder.txt")
        
        cmd = [
            "subfinder",
            "-d", self.domain,
            "-o", output_file,
            "-silent"
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            with open(output_file, 'r') as f:
                subdomains = [line.strip() for line in f if line.strip()]
            
            return subdomains
        except Exception as e:
            print(f"subfinder执行失败: {e}")
            return []
    
    def run_amass(self):
        """使用amass发现子域名（更全面但更慢）"""
        output_file = os.path.join(self.output_dir, "amass.txt")
        
        cmd = [
            "amass", "enum",
            "-d", self.domain,
            "-o", output_file,
            "-silent"
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            with open(output_file, 'r') as f:
                subdomains = [line.strip() for line in f if line.strip()]
            
            return subdomains
        except Exception as e:
            print(f"amass执行失败: {e}")
            return []
    
    def run_crtsh(self):
        """通过crt.sh证书透明度发现子域名"""
        import requests
        
        url = f"https://crt.sh/?q=%25.{self.domain}&output=json"
        
        try:
            response = requests.get(url, timeout=30)
            data = response.json()
            
            subdomains = set()
            for entry in data:
                name = entry.get('name_value', '')
                for n in name.split('\n'):
                    n = n.strip()
                    if n.endswith(self.domain) and '*' not in n:
                        subdomains.add(n)
            
            return list(subdomains)
        except Exception as e:
            print(f"crt.sh查询失败: {e}")
            return []
    
    def merge_results(self, *subdomain_lists):
        """合并多个工具的结果并去重"""
        all_subdomains = set()
        for lst in subdomain_lists:
            all_subdomains.update(lst)
        
        # 过滤无效结果
        valid = [
            s for s in all_subdomains 
            if s and s.endswith(self.domain) and '*' not in s
        ]
        
        # 保存合并结果
        output_file = os.path.join(self.output_dir, "all_subdomains.txt")
        with open(output_file, 'w') as f:
            f.write('\n'.join(sorted(valid)))
        
        return sorted(valid)
    
    def check_alive(self, subdomains):
        """使用httpx检测存活主机"""
        input_file = os.path.join(self.output_dir, "all_subdomains.txt")
        output_file = os.path.join(self.output_dir, "alive.txt")
        
        with open(input_file, 'w') as f:
            f.write('\n'.join(subdomains))
        
        cmd = [
            "httpx",
            "-l", input_file,
            "-o", output_file,
            "-silent",
            "-status-code",
            "-title",
            "-tech-detect"
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            alive_hosts = []
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            alive_hosts.append(line)
            
            return alive_hosts
        except Exception as e:
            print(f"httpx执行失败: {e}")
            return []
    
    def full_discovery(self):
        """执行完整的子域名发现流程"""
        print(f"开始发现 {self.domain} 的子域名...")
        
        # 1. 多工具发现
        print("  运行subfinder...")
        subfinder_results = self.run_subfinder()
        print(f"    发现 {len(subfinder_results)} 个")
        
        print("  查询crt.sh...")
        crtsh_results = self.run_crtsh()
        print(f"    发现 {len(crtsh_results)} 个")
        
        # 2. 合并去重
        print("  合并结果...")
        all_subdomains = self.merge_results(
            subfinder_results,
            crtsh_results
        )
        print(f"    共 {len(all_subdomains)} 个唯一子域名")
        
        # 3. 存活检测
        print("  检测存活主机...")
        alive = self.check_alive(all_subdomains)
        print(f"    存活 {len(alive)} 个")
        
        return {
            'total_discovered': len(all_subdomains),
            'alive_count': len(alive),
            'all_subdomains': all_subdomains,
            'alive_hosts': alive
        }
```

### 6.4 技术栈识别与漏洞关联

#### 6.4.1 技术栈识别方法

**Web技术栈识别：**
- HTTP响应头（Server、X-Powered-By）
- Cookie命名（PHPSESSID、JSESSIONID、csrftoken）
- URL模式（.php、.aspx、.jsp）
- 页面特征（favicon、CSS类名、JS函数）
- 指纹库匹配（Wappalyzer、WhatWeb）

**基础设施识别：**
- CDN检测（Cloudflare、Akamai、AWS CloudFront）
- 云服务识别（AWS、Azure、GCP）
- WAF检测（ModSecurity、Cloudflare WAF、阿里云WAF）
- 邮件服务（Google Workspace、Office 365、自建邮件服务器）

#### 6.4.2 漏洞关联思路

```
技术栈识别 → 版本号提取 → 漏洞数据库查询 → 风险评估
     ↓            ↓             ↓              ↓
  Wappalyzer   响应头       CVE详情      CVSS评分
  WhatWeb     页面特征     Exploit-DB    利用难度
  BuiltWith   指纹匹配     NVD           影响范围
```

### 6.5 代码托管平台信息泄露

#### 6.5.1 GitHub Dorking高级技巧

GitHub Dorking是指使用GitHub的高级搜索语法来发现敏感信息。

**基础搜索语法：**
- `关键词`：搜索包含关键词的代码
- `user:用户名`：限定用户
- `org:组织名`：限定组织
- `repo:仓库名`：限定仓库
- `filename:文件名`：按文件名搜索
- `extension:扩展名`：按文件扩展名搜索
- `path:路径`：按路径搜索
- `language:语言`：按编程语言搜索

**敏感信息搜索Dorks：**

| 目标 | Dork示例 |
|------|---------|
| API密钥 | `filename:.env api_key` |
| AWS密钥 | `AKIA extension:py` |
| 数据库密码 | `password extension:yml database` |
| SSH私钥 | `BEGIN RSA PRIVATE KEY extension:pem` |
| Slack Token | `xoxb- extension:js` |
| 私钥文件 | `filename:id_rsa` |
| 配置文件密码 | `password filename:config.php` |
| 内部文档 | `confidential extension:pdf` |

**高级搜索技巧：**
```
# 搜索某组织内的密码
org:company_name password

# 搜索特定类型文件中的API密钥
extension:py "api_key" OR "secret_key"

# 搜索提交历史中的敏感信息
"removed password" type:commit

# 搜索被删除的敏感文件
filename:.env org:company_name is:deleted

# 搜索包含特定关键词的Issue
"security vulnerability" type:issue org:company_name
```

#### 6.5.2 敏感信息搜索实战

```python
import requests
import json
import time
from datetime import datetime, timedelta

class GitHubDorker:
    def __init__(self, token=None):
        self.base_url = "https://api.github.com"
        self.token = token
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if token:
            self.headers['Authorization'] = f'token {token}'
    
    def search_code(self, query, per_page=30, page=1):
        """搜索代码"""
        url = f"{self.base_url}/search/code"
        params = {
            'q': query,
            'per_page': per_page,
            'page': page
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 403:
                # 速率限制
                reset_time = response.headers.get('X-RateLimit-Reset')
                if reset_time:
                    wait_time = int(reset_time) - time.time() + 1
                    print(f"速率限制，等待 {wait_time:.0f} 秒")
                    time.sleep(max(wait_time, 0))
                    return self.search_code(query, per_page, page)
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"搜索失败: {e}")
            return None
    
    def search_sensitive_info(self, org_or_user, is_org=True):
        """搜索敏感信息"""
        prefix = 'org' if is_org else 'user'
        
        dorks = {
            'api_keys': [
                f'{prefix}:{org_or_user} "api_key" extension:py',
                f'{prefix}:{org_or_user} "secret_key" extension:js',
                f'{prefix}:{org_or_user} "AKIA" extension:py',
                f'{prefix}:{org_or_user} "access_token" extension:json',
            ],
            'passwords': [
                f'{prefix}:{org_or_user} "password" filename:.env',
                f'{prefix}:{org_or_user} "DB_PASSWORD" extension:yml',
                f'{prefix}:{org_or_user} "root:" filename:config.php',
            ],
            'private_keys': [
                f'{prefix}:{org_or_user} "BEGIN RSA PRIVATE KEY"',
                f'{prefix}:{org_or_user} filename:id_rsa',
                f'{prefix}:{org_or_user} filename:.pem',
            ],
            'config_files': [
                f'{prefix}:{org_or_user} filename:config.php password',
                f'{prefix}:{org_or_user} filename:database.yml password',
                f'{prefix}:{org_or_user} filename:web.config "connectionString"',
            ],
            'internal_docs': [
                f'{prefix}:{org_or_user} "内部" extension:pdf',
                f'{prefix}:{org_or_user} "confidential" extension:docx',
            ]
        }
        
        results = {}
        
        for category, queries in dorks.items():
            print(f"搜索 {category}...")
            category_results = []
            
            for query in queries:
                data = self.search_code(query, per_page=30)
                if data and 'items' in data:
                    for item in data['items']:
                        category_results.append({
                            'file': item['name'],
                            'path': item['path'],
                            'repo': item['repository']['full_name'],
                            'url': item['html_url'],
                            'query': query
                        })
                
                # 避免触发速率限制
                time.sleep(2)
            
            results[category] = category_results
            print(f"  发现 {len(category_results)} 个结果")
        
        return results
    
    def get_commit_history(self, repo, filepath, since=None):
        """获取文件的提交历史"""
        url = f"{self.base_url}/repos/{repo}/commits"
        params = {'path': filepath}
        if since:
            params['since'] = since
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            commits = response.json()
            
            return [
                {
                    'sha': c['sha'],
                    'message': c['commit']['message'],
                    'author': c['commit']['author']['name'],
                    'date': c['commit']['author']['date'],
                    'url': c['html_url']
                }
                for c in commits
            ]
        except Exception as e:
            print(f"获取提交历史失败: {e}")
            return []
    
    def list_repos(self, org_or_user, is_org=True):
        """列出组织或用户的所有仓库"""
        if is_org:
            url = f"{self.base_url}/orgs/{org_or_user}/repos"
        else:
            url = f"{self.base_url}/users/{org_or_user}/repos"
        
        params = {
            'per_page': 100,
            'type': 'all'
        }
        
        all_repos = []
        page = 1
        
        while True:
            params['page'] = page
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                repos = response.json()
                
                if not repos:
                    break
                
                all_repos.extend([
                    {
                        'name': r['name'],
                        'full_name': r['full_name'],
                        'description': r['description'],
                        'language': r['language'],
                        'stars': r['stargazers_count'],
                        'forks': r['forks_count'],
                        'is_fork': r['fork'],
                        'created_at': r['created_at'],
                        'updated_at': r['updated_at'],
                        'url': r['html_url']
                    }
                    for r in repos
                ])
                
                page += 1
                
                if len(repos) < 100:
                    break
                    
            except Exception as e:
                print(f"获取仓库列表失败: {e}")
                break
        
        return all_repos
```

#### 6.5.3 提交历史与删除文件恢复

**Git历史中的敏感信息：**
- 开发者不小心提交了敏感文件，然后删除了
- 但提交历史中仍然保留
- 使用git log和git show可以查看

**发现方法：**
1. 搜索包含敏感关键词的commit message
2. 检查大的删除提交（可能是删除敏感文件）
3. 使用truffleHog、gitleaks等工具扫描历史

**恢复被删除的文件：**
```bash
# 查找删除文件的commit
git log --diff-filter=D --summary -- "*.pem"

# 从特定commit恢复文件
git show <commit_sha>:path/to/file > recovered_file
```

### 6.6 文档元数据挖掘

#### 6.6.1 可挖掘的文档类型

| 文档类型 | 扩展名 | 元数据价值 |
|---------|--------|-----------|
| PDF | .pdf | 作者、创建工具、修改历史、嵌入对象 |
| Word | .docx/.doc | 作者、公司、修订记录、批注 |
| Excel | .xlsx/.xls | 作者、公式、隐藏工作表、外部链接 |
| PPT | .pptx/.ppt | 作者、演讲者备注、隐藏幻灯片 |
| 图片 | .jpg/.png | EXIF信息、GPS坐标（见第4章） |

#### 6.6.2 文档元数据提取工具

**ExifTool：** 支持几乎所有文件格式的元数据读取
```bash
# 提取PDF元数据
exiftool document.pdf

# 提取Office文档元数据
exiftool document.docx

# 导出所有元数据为JSON
exiftool -json -a -u *.pdf > metadata.json
```

**PDF元数据深度挖掘：**
```python
import PyPDF2
import subprocess
import json
import os

class DocumentMetadataMiner:
    def extract_pdf_metadata(self, pdf_path):
        """提取PDF元数据"""
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                
                info = reader.metadata
                metadata = {
                    'title': info.title if info else None,
                    'author': info.author if info else None,
                    'subject': info.subject if info else None,
                    'creator': info.creator if info else None,
                    'producer': info.producer if info else None,
                    'creation_date': str(info.creation_date) if info and info.creation_date else None,
                    'modification_date': str(info.modification_date) if info and info.modification_date else None,
                    'pages': len(reader.pages),
                    'encrypted': reader.is_encrypted
                }
                
                # 提取文本内容（用于关键词搜索）
                text_content = ""
                for page in reader.pages:
                    text_content += page.extract_text() + "\n"
                
                metadata['text_length'] = len(text_content)
                metadata['text_preview'] = text_content[:500]
                
                return metadata
        except Exception as e:
            return {'error': str(e)}
    
    def extract_office_metadata(self, file_path):
        """提取Office文档元数据（使用exiftool）"""
        try:
            result = subprocess.run(
                ['exiftool', '-json', file_path],
                capture_output=True, text=True
            )
            data = json.loads(result.stdout)
            if data:
                return data[0]
        except Exception as e:
            return {'error': str(e)}
    
    def scan_directory_for_docs(self, directory):
        """扫描目录中的文档并提取元数据"""
        results = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                ext = file.lower().split('.')[-1]
                
                if ext in ['pdf', 'docx', 'xlsx', 'pptx', 'doc', 'xls', 'ppt']:
                    filepath = os.path.join(root, file)
                    
                    if ext == 'pdf':
                        metadata = self.extract_pdf_metadata(filepath)
                    else:
                        metadata = self.extract_office_metadata(filepath)
                    
                    results.append({
                        'file': file,
                        'path': filepath,
                        'type': ext,
                        'metadata': metadata
                    })
        
        return results
    
    def find_sensitive_keywords(self, text, keywords=None):
        """在文本中查找敏感关键词"""
        if keywords is None:
            keywords = [
                '密码', 'password', 'secret', '密钥', 'API Key',
                '内部', '机密', 'confidential', 'internal',
                '用户名', 'username', '账号', 'account'
            ]
        
        found = {}
        text_lower = text.lower()
        
        for kw in keywords:
            count = text_lower.count(kw.lower())
            if count > 0:
                found[kw] = count
        
        return found
```

---

---

