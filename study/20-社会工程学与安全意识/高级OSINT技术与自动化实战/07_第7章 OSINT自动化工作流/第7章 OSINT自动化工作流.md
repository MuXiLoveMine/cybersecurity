# 第7章 OSINT自动化工作流

### 7.1 Python OSINT编程基础

#### 7.1.1 为什么选择Python

Python是OSINT自动化的首选编程语言，原因包括：
- 丰富的第三方库生态
- 简洁易读的语法，快速原型开发
- 强大的网络编程能力
- 数据处理和分析库（pandas、numpy）
- 大量安全工具使用Python开发
- 跨平台兼容性

#### 7.1.2 必备Python库

| 类别 | 库名 | 用途 |
|------|------|------|
| 网络请求 | requests | HTTP请求 |
| | httpx | 异步HTTP |
| | aiohttp | 异步HTTP客户端 |
| 网页解析 | BeautifulSoup | HTML/XML解析 |
| | lxml | 高性能XML/HTML解析 |
| | parsel | 基于lxml的解析器 |
| 浏览器自动化 | selenium | 浏览器自动化 |
| | playwright | 现代浏览器自动化 |
| 数据处理 | pandas | 数据分析与处理 |
| | json | JSON处理 |
| | csv | CSV处理 |
| 网络工具 | dnspython | DNS查询 |
| | python-whois | WHOIS查询 |
| | shodan | Shodan API |
| 可视化 | matplotlib | 数据可视化 |
| | folium | 地图可视化 |
| | networkx | 网络分析与可视化 |

#### 7.1.3 开发环境配置

```python
# requirements.txt 推荐配置
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
selenium>=4.8.0
pandas>=1.5.0
dnspython>=2.3.0
python-whois>=0.8.0
shodan>=1.28.0
folium>=0.14.0
networkx>=3.0.0
exifread>=3.0.0
PyPDF2>=3.0.0
```

### 7.2 requests、BeautifulSoup、selenium在OSINT中的应用

#### 7.2.1 requests库高级用法

**会话管理：**
```python
import requests

class SessionManager:
    def __init__(self):
        self.session = requests.Session()
        self._setup_headers()
    
    def _setup_headers(self):
        """设置请求头，模拟真实浏览器"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def set_proxy(self, proxy_url):
        """设置代理"""
        self.session.proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def get_with_retry(self, url, max_retries=3, timeout=10):
        """带重试的GET请求"""
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt  # 指数退避
                print(f"请求失败，{wait_time}秒后重试: {e}")
                import time
                time.sleep(wait_time)
    
    def post_with_retry(self, url, data=None, json=None, max_retries=3, timeout=10):
        """带重试的POST请求"""
        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    url, data=data, json=json, timeout=timeout
                )
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                print(f"请求失败，{wait_time}秒后重试: {e}")
                import time
                time.sleep(wait_time)
```

#### 7.2.2 BeautifulSoup网页解析

```python
from bs4 import BeautifulSoup
import requests

class WebParser:
    def __init__(self, html_content):
        self.soup = BeautifulSoup(html_content, 'lxml')
    
    def extract_all_links(self):
        """提取所有链接"""
        links = []
        for link in self.soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            if href.startswith('http'):
                links.append({'url': href, 'text': text})
        return links
    
    def extract_emails(self):
        """提取页面中的邮箱地址"""
        import re
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        # 从文本中提取
        text = self.soup.get_text()
        emails = re.findall(email_pattern, text)
        
        # 从mailto链接中提取
        for link in self.soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('mailto:'):
                email = href[7:].split('?')[0]
                emails.append(email)
        
        return list(set(emails))
    
    def extract_phone_numbers(self):
        """提取电话号码（中国格式）"""
        import re
        text = self.soup.get_text()
        
        # 手机号
        mobile_pattern = r'1[3-9]\d{9}'
        # 固定电话
        landline_pattern = r'0\d{2,3}-?\d{7,8}'
        
        mobiles = re.findall(mobile_pattern, text)
        landlines = re.findall(landline_pattern, text)
        
        return {
            'mobiles': list(set(mobiles)),
            'landlines': list(set(landlines))
        }
    
    def extract_meta_tags(self):
        """提取meta标签信息"""
        meta_info = {}
        
        for meta in self.soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                meta_info[name] = content
        
        return meta_info
    
    def extract_tables(self):
        """提取页面中的表格数据"""
        tables = []
        
        for table in self.soup.find_all('table'):
            table_data = []
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all(['th', 'td'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                table_data.append(row_data)
            
            if table_data:
                tables.append(table_data)
        
        return tables
```

#### 7.2.3 Selenium动态页面爬取

对于JavaScript渲染的动态页面，需要使用Selenium等浏览器自动化工具。

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

class SeleniumScraper:
    def __init__(self, headless=True):
        self.options = Options()
        
        if headless:
            self.options.add_argument('--headless')
        
        # 反检测配置
        self.options.add_argument('--disable-blink-features=AutomationControlled')
        self.options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.set_page_load_timeout(30)
        self.wait = WebDriverWait(self.driver, 10)
        
        # 注入JavaScript隐藏自动化特征
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
    
    def get_page(self, url, wait_for_element=None):
        """获取页面内容"""
        self.driver.get(url)
        
        if wait_for_element:
            try:
                self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, wait_for_element)
                    )
                )
            except Exception:
                pass
        
        # 模拟滚动以加载更多内容
        self._scroll_page()
        
        return self.driver.page_source
    
    def _scroll_page(self):
        """模拟页面滚动"""
        for i in range(3):
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(1)
    
    def extract_text_by_selector(self, css_selector):
        """通过CSS选择器提取文本"""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
            return [elem.text.strip() for elem in elements if elem.text.strip()]
        except Exception as e:
            print(f"提取失败: {e}")
            return []
    
    def extract_links(self):
        """提取所有链接"""
        links = self.driver.find_elements(By.TAG_NAME, 'a')
        result = []
        for link in links:
            href = link.get_attribute('href')
            text = link.text.strip()
            if href and href.startswith('http'):
                result.append({'url': href, 'text': text})
        return result
    
    def take_screenshot(self, filename):
        """截图"""
        self.driver.save_screenshot(filename)
    
    def close(self):
        """关闭浏览器"""
        self.driver.quit()
```

### 7.3 API集成（Shodan、Censys、Hunter.io、HIBP）

#### 7.3.1 Shodan API集成

Shodan是互联网连接设备搜索引擎，OSINT中用于发现目标的网络资产。

```python
import shodan
import json

class ShodanScanner:
    def __init__(self, api_key):
        self.api = shodan.Shodan(api_key)
    
    def host_lookup(self, ip):
        """查询IP的详细信息"""
        try:
            host = self.api.host(ip)
            
            return {
                'ip': host.get('ip_str'),
                'org': host.get('org'),
                'os': host.get('os'),
                'country': host.get('country_name'),
                'city': host.get('city'),
                'ports': host.get('ports', []),
                'vulns': host.get('vulns', []),
                'last_update': host.get('last_update'),
                'services': [
                    {
                        'port': s['port'],
                        'transport': s['transport'],
                        'product': s.get('product', ''),
                        'version': s.get('version', ''),
                        'data': s.get('data', '')[:200]
                    }
                    for s in host.get('data', [])
                ]
            }
        except shodan.APIError as e:
            return {'error': str(e)}
    
    def search_by_query(self, query, limit=100):
        """按关键词搜索"""
        try:
            results = self.api.search(query, limit=limit)
            
            return {
                'total': results['total'],
                'matches': [
                    {
                        'ip': m['ip_str'],
                        'port': m['port'],
                        'org': m.get('org', ''),
                        'location': f"{m.get('country_name', '')}, {m.get('city', '')}",
                        'product': m.get('product', ''),
                        'version': m.get('version', ''),
                        'data': m.get('data', '')[:300]
                    }
                    for m in results['matches']
                ]
            }
        except shodan.APIError as e:
            return {'error': str(e)}
    
    def search_by_domain(self, domain):
        """搜索域名相关的主机"""
        query = f"hostname:{domain}"
        return self.search_by_query(query)
    
    def get_exploits(self, query):
        """搜索漏洞利用代码"""
        try:
            results = self.api.exploits.search(query)
            return {
                'total': results['total'],
                'exploits': results['matches'][:10]
            }
        except shodan.APIError as e:
            return {'error': str(e)}
    
    def scan_ip(self, ip):
        """请求扫描一个IP（需要积分）"""
        try:
            result = self.api.scan(ip)
            return result
        except shodan.APIError as e:
            return {'error': str(e)}
```

#### 7.3.2 Hunter.io集成

Hunter.io用于发现和验证企业邮箱地址。

```python
import requests

class HunterIOClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.hunter.io/v2"
    
    def domain_search(self, domain, limit=100):
        """搜索域名下的所有邮箱"""
        url = f"{self.base_url}/domain-search"
        params = {
            'domain': domain,
            'api_key': self.api_key,
            'limit': limit
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                result = data['data']
                return {
                    'domain': result.get('domain'),
                    'disposable': result.get('disposable'),
                    'webmail': result.get('webmail'),
                    'pattern': result.get('pattern'),
                    'organization': result.get('organization'),
                    'emails': [
                        {
                            'value': e['value'],
                            'type': e.get('type', ''),
                            'confidence': e.get('confidence', 0),
                            'first_name': e.get('first_name', ''),
                            'last_name': e.get('last_name', ''),
                            'position': e.get('position', ''),
                            'department': e.get('department', ''),
                            'linkedin': e.get('linkedin', ''),
                            'phone_number': e.get('phone_number', '')
                        }
                        for e in result.get('emails', [])
                    ]
                }
            return None
        except Exception as e:
            return {'error': str(e)}
    
    def email_finder(self, domain, first_name, last_name):
        """根据姓名查找邮箱"""
        url = f"{self.base_url}/email-finder"
        params = {
            'domain': domain,
            'first_name': first_name,
            'last_name': last_name,
            'api_key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                result = data['data']
                return {
                    'email': result.get('email'),
                    'score': result.get('score'),
                    'sources': result.get('sources', [])
                }
            return None
        except Exception as e:
            return {'error': str(e)}
    
    def email_verifier(self, email):
        """验证邮箱是否存在"""
        url = f"{self.base_url}/email-verifier"
        params = {
            'email': email,
            'api_key': self.api_key
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                result = data['data']
                return {
                    'result': result.get('result'),  # deliverable, undeliverable, risky
                    'score': result.get('score'),
                    'regexp': result.get('regexp'),
                    'gibberish': result.get('gibberish'),
                    'disposable': result.get('disposable'),
                    'webmail': result.get('webmail'),
                    'mx_records': result.get('mx_records'),
                    'smtp_server': result.get('smtp_server'),
                    'smtp_check': result.get('smtp_check'),
                    'accept_all': result.get('accept_all'),
                    'block': result.get('block')
                }
            return None
        except Exception as e:
            return {'error': str(e)}
```

#### 7.3.3 Censys API集成

Censys是另一个互联网资产搜索引擎，与Shodan互补。

```python
import requests

class CensysClient:
    def __init__(self, api_id, api_secret):
        self.api_id = api_id
        self.api_secret = api_secret
        self.base_url = "https://search.censys.io/api/v2"
        self.auth = (api_id, api_secret)
    
    def search_hosts(self, query, per_page=25, page=1):
        """搜索主机"""
        url = f"{self.base_url}/hosts/search"
        params = {
            'q': query,
            'per_page': per_page,
            'page': page
        }
        
        try:
            response = requests.get(url, auth=self.auth, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def get_host(self, ip):
        """获取主机详情"""
        url = f"{self.base_url}/hosts/{ip}"
        
        try:
            response = requests.get(url, auth=self.auth)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
    
    def search_certificates(self, query, per_page=25):
        """搜索证书"""
        url = f"{self.base_url}/certificates/search"
        params = {
            'q': query,
            'per_page': per_page
        }
        
        try:
            response = requests.get(url, auth=self.auth, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {'error': str(e)}
```

### 7.4 自动化信息收集脚本开发

#### 7.4.1 域名信息收集脚本

```python
import dns.resolver
import whois
import requests
import json
import subprocess
from datetime import datetime

class DomainIntelligence:
    def __init__(self, domain):
        self.domain = domain
        self.results = {
            'domain': domain,
            'scan_date': datetime.now().isoformat()
        }
    
    def whois_lookup(self):
        """WHOIS查询"""
        try:
            w = whois.whois(self.domain)
            self.results['whois'] = {
                'registrar': w.registrar,
                'creation_date': str(w.creation_date) if w.creation_date else None,
                'expiration_date': str(w.expiration_date) if w.expiration_date else None,
                'updated_date': str(w.updated_date) if w.updated_date else None,
                'registrant': w.get('registrant', ''),
                'registrant_org': w.get('org', ''),
                'registrant_country': w.get('country', ''),
                'nameservers': w.name_servers if w.name_servers else [],
                'status': w.status if w.status else []
            }
        except Exception as e:
            self.results['whois'] = {'error': str(e)}
        
        return self.results['whois']
    
    def dns_enumeration(self):
        """DNS记录枚举"""
        dns_records = {}
        
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'SPF']
        
        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(self.domain, record_type)
                records = []
                for rdata in answers:
                    if record_type == 'A':
                        records.append(rdata.address)
                    elif record_type == 'AAAA':
                        records.append(rdata.address)
                    elif record_type == 'MX':
                        records.append({
                            'priority': rdata.preference,
                            'exchange': str(rdata.exchange)
                        })
                    elif record_type == 'NS':
                        records.append(str(rdata.target))
                    elif record_type == 'TXT':
                        records.append(str(rdata))
                    elif record_type == 'CNAME':
                        records.append(str(rdata.target))
                    elif record_type == 'SOA':
                        records.append({
                            'mname': str(rdata.mname),
                            'rname': str(rdata.rname),
                            'serial': rdata.serial
                        })
                    else:
                        records.append(str(rdata))
                
                dns_records[record_type.lower()] = records
            except Exception as e:
                dns_records[record_type.lower()] = []
        
        self.results['dns'] = dns_records
        return dns_records
    
    def subdomain_discovery(self):
        """子域名发现（使用多种方法）"""
        subdomains = set()
        
        # 方法1: Certificate Transparency
        try:
            url = f"https://crt.sh/?q=%25.{self.domain}&output=json"
            response = requests.get(url, timeout=30)
            data = response.json()
            
            for entry in data:
                name = entry.get('name_value', '')
                for n in name.split('\n'):
                    n = n.strip()
                    if n.endswith(self.domain) and '*' not in n:
                        subdomains.add(n)
        except Exception as e:
            print(f"crt.sh查询失败: {e}")
        
        self.results['subdomains'] = sorted(list(subdomains))
        return sorted(list(subdomains))
    
    def web_tech_detect(self):
        """Web技术检测（简化版）"""
        try:
            url = f"https://{self.domain}"
            response = requests.get(url, timeout=10, allow_redirects=True)
            
            tech_stack = {
                'server': response.headers.get('Server', ''),
                'x_powered_by': response.headers.get('X-Powered-By', ''),
                'x_frame_options': response.headers.get('X-Frame-Options', ''),
                'x_content_type_options': response.headers.get('X-Content-Type-Options', ''),
                'content_security_policy': response.headers.get('Content-Security-Policy', ''),
                'cookies': list(response.cookies.keys())
            }
            
            # 检测常见CMS和框架
            content = response.text.lower()
            
            detections = []
            if 'wordpress' in content or 'wp-content' in content:
                detections.append('WordPress')
            if 'drupal' in content or 'sites/default' in content:
                detections.append('Drupal')
            if 'joomla' in content:
                detections.append('Joomla')
            if 'react' in content:
                detections.append('React')
            if 'vue' in content:
                detections.append('Vue.js')
            if 'jquery' in content:
                detections.append('jQuery')
            if 'bootstrap' in content:
                detections.append('Bootstrap')
            if 'cloudflare' in response.headers.get('server', '').lower():
                detections.append('Cloudflare')
            
            tech_stack['detected_tech'] = detections
            tech_stack['status_code'] = response.status_code
            tech_stack['final_url'] = response.url
            
            self.results['web_tech'] = tech_stack
            return tech_stack
            
        except Exception as e:
            self.results['web_tech'] = {'error': str(e)}
            return {'error': str(e)}
    
    def full_scan(self):
        """执行完整扫描"""
        print(f"开始扫描域名: {self.domain}")
        
        print("  [1/5] WHOIS查询...")
        self.whois_lookup()
        
        print("  [2/5] DNS记录枚举...")
        self.dns_enumeration()
        
        print("  [3/5] 子域名发现...")
        subdomains = self.subdomain_discovery()
        print(f"    发现 {len(subdomains)} 个子域名")
        
        print("  [4/5] Web技术检测...")
        self.web_tech_detect()
        
        print("  [5/5] 生成报告...")
        
        return self.results
    
    def save_report(self, output_file=None):
        """保存扫描报告"""
        if output_file is None:
            output_file = f"{self.domain}_osint_report.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        return output_file
```

#### 7.4.2 社交媒体账号收集脚本

```python
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

class SocialMediaEnumerator:
    def __init__(self, username):
        self.username = username
        self.results = []
        
        # 预定义的社交媒体平台列表（简化版）
        self.platforms = [
            {'name': 'Twitter', 'url': 'https://twitter.com/{username}', 'method': 'status'},
            {'name': 'Instagram', 'url': 'https://www.instagram.com/{username}/', 'method': 'status'},
            {'name': 'GitHub', 'url': 'https://github.com/{username}', 'method': 'status'},
            {'name': 'YouTube', 'url': 'https://www.youtube.com/@{username}', 'method': 'status'},
            {'name': 'Reddit', 'url': 'https://www.reddit.com/user/{username}/', 'method': 'status'},
            {'name': 'Medium', 'url': 'https://medium.com/@{username}', 'method': 'status'},
            {'name': 'Dev.to', 'url': 'https://dev.to/{username}', 'method': 'status'},
            {'name': 'Pinterest', 'url': 'https://www.pinterest.com/{username}/', 'method': 'status'},
            {'name': 'SoundCloud', 'url': 'https://soundcloud.com/{username}', 'method': 'status'},
            {'name': 'Steam', 'url': 'https://steamcommunity.com/id/{username}', 'method': 'status'},
        ]
    
    def check_platform(self, platform):
        """检查单个平台"""
        url = platform['url'].format(username=self.username)
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            
            # 简单的状态码检测
            if response.status_code == 200:
                # 进一步验证（检查页面内容是否包含用户名）
                if self.username.lower() in response.text.lower():
                    return {
                        'platform': platform['name'],
                        'url': url,
                        'found': True,
                        'confidence': 0.7,
                        'status_code': response.status_code
                    }
            
            return {
                'platform': platform['name'],
                'url': url,
                'found': False,
                'confidence': 0,
                'status_code': response.status_code
            }
            
        except Exception as e:
            return {
                'platform': platform['name'],
                'url': url,
                'found': False,
                'error': str(e)
            }
    
    def enumerate(self, max_workers=5):
        """枚举所有平台"""
        print(f"正在搜索用户名: {self.username}")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.check_platform, platform): platform
                for platform in self.platforms
            }
            
            for future in as_completed(futures):
                result = future.result()
                self.results.append(result)
                
                if result.get('found'):
                    print(f"  [+] {result['platform']}: {result['url']}")
        
        # 按平台名称排序
        self.results.sort(key=lambda x: x['platform'])
        
        return self.results
    
    def get_found_accounts(self):
        """获取已发现的账号"""
        return [r for r in self.results if r.get('found')]
    
    def save_results(self, output_file=None):
        """保存结果"""
        if output_file is None:
            output_file = f"{self.username}_social_media.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'username': self.username,
                'total_platforms': len(self.platforms),
                'found_count': len(self.get_found_accounts()),
                'results': self.results
            }, f, ensure_ascii=False, indent=2)
        
        return output_file
```

### 7.5 OSINT工具链编排

#### 7.5.1 工具链设计原则

1. **输入标准化**：统一各工具的输入输出格式
2. **模块化设计**：每个工具作为独立模块，便于替换和升级
3. **数据流转**：前一个工具的输出作为后一个工具的输入
4. **错误处理**：单个工具失败不影响整体流程
5. **结果聚合**：统一汇总多工具的结果，去重和关联

#### 7.5.2 企业侦察工具链示例

```python
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

class OSINTPipeline:
    def __init__(self, target, output_dir="osint_results"):
        self.target = target
        self.output_dir = os.path.join(output_dir, target)
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.results = {
            'target': target,
            'start_time': datetime.now().isoformat(),
            'phases': {}
        }
    
    def phase1_domain_intel(self):
        """阶段1：域名基础信息收集"""
        print("=" * 50)
        print("阶段1：域名基础信息收集")
        print("=" * 50)
        
        domain_intel = DomainIntelligence(self.target)
        result = domain_intel.full_scan()
        
        self.results['phases']['domain_intel'] = result
        domain_intel.save_report(
            os.path.join(self.output_dir, "domain_intel.json")
        )
        
        return result
    
    def phase2_subdomain_enum(self):
        """阶段2：子域名枚举"""
        print("\n" + "=" * 50)
        print("阶段2：子域名枚举")
        print("=" * 50)
        
        subdomain_enum = SubdomainDiscovery(
            self.target, 
            output_dir=self.output_dir
        )
        result = subdomain_enum.full_discovery()
        
        self.results['phases']['subdomains'] = result
        
        return result
    
    def phase3_web_tech(self):
        """阶段3：Web技术栈识别"""
        print("\n" + "=" * 50)
        print("阶段3：Web技术栈识别")
        print("=" * 50)
        
        # 对存活的子域名进行技术检测
        subdomains = self.results['phases'].get('subdomains', {}).get('alive_hosts', [])
        tech_results = {}
        
        for host in subdomains[:5]:  # 只检测前5个作为示例
            url = host if host.startswith('http') else f"https://{host}"
            try:
                response = requests.get(url, timeout=10, verify=False)
                tech_results[host] = {
                    'status': response.status_code,
                    'server': response.headers.get('Server', ''),
                    'x_powered_by': response.headers.get('X-Powered-By', '')
                }
            except Exception as e:
                tech_results[host] = {'error': str(e)}
        
        self.results['phases']['web_tech'] = tech_results
        print(f"  检测了 {len(tech_results)} 个主机")
        
        return tech_results
    
    def phase4_employee_enum(self):
        """阶段4：员工信息收集"""
        print("\n" + "=" * 50)
        print("阶段4：员工信息收集")
        print("=" * 50)
        
        # 使用Hunter.io（需要API密钥）
        # hunter = HunterIOClient(api_key="your_api_key")
        # result = hunter.domain_search(self.target)
        
        # 模拟结果
        result = {
            'note': '需要配置Hunter.io API密钥以启用此功能',
            'estimated_emails': []
        }
        
        self.results['phases']['employees'] = result
        print("  跳过（未配置API密钥）")
        
        return result
    
    def phase5_breach_check(self):
        """阶段5：泄露数据检查"""
        print("\n" + "=" * 50)
        print("阶段5：泄露数据检查")
        print("=" * 50)
        
        # 检查域名是否出现在已知泄露中
        checker = HIBPChecker()
        # 注意：完整功能需要API密钥
        # 这里只做密码泄露检查示例
        
        result = {
            'note': '完整泄露检查需要HIBP API密钥',
            'password_breach_check': '可用 check_password() 方法检查单个密码'
        }
        
        self.results['phases']['breach_check'] = result
        print("  基础检查完成")
        
        return result
    
    def run_full_pipeline(self):
        """运行完整的OSINT流水线"""
        print(f"\n开始OSINT侦察: {self.target}")
        print(f"输出目录: {self.output_dir}\n")
        
        try:
            self.phase1_domain_intel()
        except Exception as e:
            print(f"阶段1失败: {e}")
        
        try:
            self.phase2_subdomain_enum()
        except Exception as e:
            print(f"阶段2失败: {e}")
        
        try:
            self.phase3_web_tech()
        except Exception as e:
            print(f"阶段3失败: {e}")
        
        try:
            self.phase4_employee_enum()
        except Exception as e:
            print(f"阶段4失败: {e}")
        
        try:
            self.phase5_breach_check()
        except Exception as e:
            print(f"阶段5失败: {e}")
        
        # 生成最终报告
        self.results['end_time'] = datetime.now().isoformat()
        self._generate_summary()
        self._save_full_report()
        
        print("\n" + "=" * 50)
        print("侦察完成！")
        print(f"报告保存在: {self.output_dir}")
        print("=" * 50)
        
        return self.results
    
    def _generate_summary(self):
        """生成摘要"""
        summary = {
            'target': self.target,
            'subdomain_count': len(
                self.results['phases'].get('subdomains', {}).get('all_subdomains', [])
            ),
            'alive_count': len(
                self.results['phases'].get('subdomains', {}).get('alive_hosts', [])
            ),
        }
        self.results['summary'] = summary
    
    def _save_full_report(self):
        """保存完整报告"""
        report_file = os.path.join(self.output_dir, "full_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        return report_file
```

### 7.6 数据清洗与关联分析

#### 7.6.1 数据清洗的重要性

OSINT收集的原始数据往往存在以下问题：
- 重复数据
- 格式不统一
- 无效或过期信息
- 噪音数据
- 数据缺失

**清洗步骤：**
1. **去重**：移除重复记录
2. **格式标准化**：统一日期、电话号码、姓名等格式
3. **有效性验证**：验证邮箱、域名、URL等是否有效
4. **噪音过滤**：移除无关或错误信息
5. **数据补全**：补充缺失的关键字段

#### 7.6.2 数据关联分析方法

**关联维度：**
- **身份关联**：同一人在不同平台的账号关联
- **时间关联**：事件发生的时间顺序和模式
- **地点关联**：地理位置信息的关联
- **关系关联**：社交关系、组织关系
- **行为关联**：行为模式的相似性

```python
import pandas as pd
from fuzzywuzzy import fuzz
from datetime import datetime

class OSINTDataProcessor:
    def __init__(self):
        pass
    
    def deduplicate_emails(self, email_list):
        """邮箱去重"""
        # 转小写、去空格
        normalized = [
            email.strip().lower() 
            for email in email_list 
            if email and '@' in email
        ]
        
        # 移除重复
        unique = list(set(normalized))
        
        return {
            'original_count': len(email_list),
            'unique_count': len(unique),
            'unique_emails': sorted(unique)
        }
    
    def normalize_phone(self, phone):
        """标准化电话号码（中国）"""
        # 移除空格、横线、括号等
        digits = ''.join(c for c in phone if c.isdigit())
        
        if digits.startswith('86'):
            digits = digits[2:]
        elif digits.startswith('+86'):
            digits = digits[3:]
        
        if len(digits) == 11 and digits.startswith('1'):
            return f"{digits[:3]}****{digits[7:]}"  # 脱敏显示
        elif len(digits) == 11:
            return digits
        
        return digits
    
    def fuzzy_match_names(self, name, name_list, threshold=80):
        """模糊匹配姓名"""
        matches = []
        
        for candidate in name_list:
            # 计算相似度
            ratio = fuzz.ratio(name, candidate)
            partial_ratio = fuzz.partial_ratio(name, candidate)
            token_sort_ratio = fuzz.token_sort_ratio(name, candidate)
            
            # 综合得分
            score = max(ratio, partial_ratio, token_sort_ratio)
            
            if score >= threshold:
                matches.append({
                    'name': candidate,
                    'score': score,
                    'ratio': ratio,
                    'partial_ratio': partial_ratio
                })
        
        return sorted(matches, key=lambda x: x['score'], reverse=True)
    
    def merge_data_sources(self, *data_frames, on='email'):
        """合并多个数据源"""
        if not data_frames:
            return None
        
        result = data_frames[0]
        
        for df in data_frames[1:]:
            result = pd.merge(
                result, df, 
                on=on, 
                how='outer',
                suffixes=('_left', '_right')
            )
        
        return result
    
    def analyze_timeline(self, events, time_field='timestamp'):
        """时间线分析"""
        df = pd.DataFrame(events)
        df[time_field] = pd.to_datetime(df[time_field])
        df = df.sort_values(time_field)
        
        # 时间间隔分析
        df['time_diff'] = df[time_field].diff()
        
        # 按天统计
        df['date'] = df[time_field].dt.date
        daily_counts = df.groupby('date').size()
        
        return {
            'total_events': len(df),
            'date_range': {
                'start': str(df[time_field].min()),
                'end': str(df[time_field].max())
            },
            'avg_interval': str(df['time_diff'].mean()),
            'daily_stats': daily_counts.to_dict(),
            'busiest_day': str(daily_counts.idxmax()),
            'busiest_count': daily_counts.max()
        }
    
    def find_connections(self, data, key_fields):
        """发现数据间的关联"""
        connections = []
        
        # 基于关键字段匹配
        for i, item1 in enumerate(data):
            for j, item2 in enumerate(data[i+1:], i+1):
                shared_fields = []
                for field in key_fields:
                    val1 = item1.get(field)
                    val2 = item2.get(field)
                    if val1 and val2 and val1 == val2:
                        shared_fields.append(field)
                
                if shared_fields:
                    connections.append({
                        'source': i,
                        'target': j,
                        'shared_fields': shared_fields,
                        'strength': len(shared_fields)
                    })
        
        return sorted(connections, key=lambda x: x['strength'], reverse=True)
```

### 7.7 自动化报告生成

#### 7.7.1 报告结构设计

一份好的OSINT报告应包含以下部分：

1. **执行摘要**：关键发现和结论
2. **目标概述**：侦察目标和范围
3. **方法说明**：使用的工具和方法
4. **详细发现**：各维度的详细信息
5. **风险评估**：发现的安全风险
6. **建议措施**：改进建议
7. **附录**：原始数据和参考资料

#### 7.7.2 报告生成工具

```python
import json
import os
from datetime import datetime
from jinja2 import Template

class OSINTReportGenerator:
    def __init__(self, template_dir="templates"):
        self.template_dir = template_dir
    
    def generate_markdown_report(self, data, output_file):
        """生成Markdown格式报告"""
        report = []
        
        # 标题
        report.append(f"# OSINT侦察报告 - {data.get('target', '未知目标')}")
        report.append("")
        report.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**扫描时间**: {data.get('start_time', '未知')} ~ {data.get('end_time', '未知')}")
        report.append("")
        
        # 执行摘要
        report.append("## 执行摘要")
        report.append("")
        summary = data.get('summary', {})
        report.append(f"- **目标**: {data.get('target', '')}")
        report.append(f"- **发现子域名**: {summary.get('subdomain_count', 0)} 个")
        report.append(f"- **存活主机**: {summary.get('alive_count', 0)} 个")
        report.append("")
        
        # 详细发现
        phases = data.get('phases', {})
        
        if 'domain_intel' in phases:
            report.append("## 1. 域名信息")
            report.append("")
            domain_info = phases['domain_intel']
            
            if 'whois' in domain_info and 'error' not in domain_info['whois']:
                whois = domain_info['whois']
                report.append("### 1.1 WHOIS信息")
                report.append("")
                report.append(f"- **注册商**: {whois.get('registrar', 'N/A')}")
                report.append(f"- **注册时间**: {whois.get('creation_date', 'N/A')}")
                report.append(f"- **到期时间**: {whois.get('expiration_date', 'N/A')}")
                report.append(f"- **注册人组织**: {whois.get('registrant_org', 'N/A')}")
                report.append(f"- **注册人国家**: {whois.get('registrant_country', 'N/A')}")
                report.append("")
            
            if 'dns' in domain_info:
                dns = domain_info['dns']
                report.append("### 1.2 DNS记录")
                report.append("")
                for record_type, records in dns.items():
                    if records:
                        report.append(f"**{record_type.upper()}记录**:")
                        if isinstance(records, list):
                            for r in records[:10]:  # 只显示前10条
                                if isinstance(r, dict):
                                    report.append(f"- {r}")
                                else:
                                    report.append(f"- {r}")
                        report.append("")
        
        if 'subdomains' in phases:
            report.append("## 2. 子域名")
            report.append("")
            subdomains = phases['subdomains']
            report.append(f"共发现 **{subdomains.get('total_discovered', 0)}** 个子域名，"
                         f"其中存活 **{subdomains.get('alive_count', 0)}** 个。")
            report.append("")
            
            alive = subdomains.get('alive_hosts', [])
            if alive:
                report.append("### 2.1 存活主机")
                report.append("")
                for host in alive[:20]:  # 只显示前20个
                    report.append(f"- {host}")
                if len(alive) > 20:
                    report.append(f"... 共 {len(alive)} 个")
                report.append("")
        
        # 风险评估
        report.append("## 3. 风险评估")
        report.append("")
        report.append("### 3.1 识别的风险")
        report.append("")
        report.append("- 待根据实际发现填充风险评估内容")
        report.append("")
        
        # 建议
        report.append("## 4. 建议措施")
        report.append("")
        report.append("1. 定期进行OSINT自查，了解公开暴露面")
        report.append("2. 及时清理不必要的公开信息")
        report.append("3. 加强员工安全意识培训")
        report.append("4. 建立信息泄露监测机制")
        report.append("")
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        return output_file
    
    def generate_html_report(self, data, output_file):
        """生成HTML格式报告（使用模板）"""
        # 简化版HTML生成
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSINT报告 - {data.get('target', '')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; }}
        .summary {{ background: #ecf0f1; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .risk-high {{ color: #e74c3c; }}
        .risk-medium {{ color: #f39c12; }}
        .risk-low {{ color: #27ae60; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background: #3498db; color: white; }}
        tr:nth-child(even) {{ background: #f8f9fa; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>OSINT侦察报告</h1>
        <p><strong>目标:</strong> {data.get('target', '')}</p>
        <p><strong>生成时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="summary">
            <h2>执行摘要</h2>
            <p>发现子域名: <strong>{data.get('summary', {}).get('subdomain_count', 0)}</strong> 个</p>
            <p>存活主机: <strong>{data.get('summary', {}).get('alive_count', 0)}</strong> 个</p>
        </div>
        
        <h2>详细发现</h2>
        <p>（详细内容请参考JSON数据文件）</p>
        
        <div class="footer">
            <p>本报告由OSINT自动化工具生成，仅供参考。</p>
        </div>
    </div>
</body>
</html>
        """
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_file
```

---

---

## 📋 内容审核与补充建议

> 针对「第7章 OSINT自动化工作流」部分的内容审核结果：

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
