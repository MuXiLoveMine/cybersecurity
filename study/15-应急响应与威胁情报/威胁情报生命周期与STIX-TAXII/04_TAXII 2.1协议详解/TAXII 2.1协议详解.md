# TAXII 2.1协议详解

### 4.1 TAXII概述

**TAXII**（Trusted Automated Exchange of Intelligence Information）是用于在网络上传输网络威胁情报信息的协议。TAXII 2.1基于HTTPS RESTful API设计，与STIX 2.1配合使用。

### 4.2 TAXII架构

```
┌──────────────────────────────────────────────────────────┐
│                   TAXII 2.1 架构                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐                                       │
│  │  Discovery    │  发现服务，返回可用API Root列表        │
│  │  Service      │                                      │
│  └──────┬───────┘                                       │
│         │                                                │
│         ▼                                                │
│  ┌──────────────┐                                       │
│  │  API Root     │  API根目录，包含Collections和Collections│
│  └──────┬───────┘                                       │
│         │                                                │
│    ┌────┴────┐                                          │
│    ▼         ▼                                           │
│ ┌──────┐ ┌──────────┐                                  │
│ │Collections│ │ Collection  │  集合，存储STIX对象的容器    │
│ └──────┘ └──────┬───┘                                  │
│                  │                                      │
│                  ▼                                      │
│            ┌──────────┐                                 │
│            │ Objects  │  STIX对象（Indicator, Malware等）│
│            └──────────┘                                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 4.3 TAXII端点

| 端点 | 方法 | 说明 |
|------|------|------|
| /discovery | GET | 发现服务，返回API Root信息 |
| /{api_root}/ | GET | API Root信息 |
| /{api_root}/collections/ | GET | 列出所有集合 |
| /{api_root}/collections/{id}/ | GET | 获取特定集合信息 |
| /{api_root}/collections/{id}/objects/ | GET | 获取集合中的STIX对象 |
| /{api_root}/collections/{id}/objects/ | POST | 向集合添加STIX对象 |
| /{api_root}/collections/{id}/objects/{object_id}/ | GET | 获取特定对象 |
| /{api_root}/manifest/ | GET | 获取对象清单 |
| /{api_root}/status/{id}/ | GET | 获取操作状态 |

### 4.4 TAXII传输流程

```
客户端                                    TAXII服务器
  │                                            │
  │  1. GET /discovery                          │
  │ ──────────────────────────────────────────→ │
  │                                             │
  │  2. 返回API Root列表                         │
  │ ←──────────────────────────────────────────  │
  │                                             │
  │  3. GET /trust-group1/ (API Root)           │
  │ ──────────────────────────────────────────→ │
  │                                             │
  │  4. 返回API Root信息(标题、描述、集合)       │
  │ ←──────────────────────────────────────────  │
  │                                             │
  │  5. GET /trust-group1/collections/          │
  │ ──────────────────────────────────────────→ │
  │                                             │
  │  6. 返回集合列表                             │
  │ ←──────────────────────────────────────────  │
  │                                             │
  │  7. GET /trust-group1/collections/{id}/     │
  │     /objects?added_after=2024-01-01         │
  │ ──────────────────────────────────────────→ │
  │                                             │
  │  8. 返回STIX对象(Bundle)                    │
  │ ←──────────────────────────────────────────  │
  │                                             │
  │  9. POST /trust-group1/collections/{id}/    │
  │     /objects  (提交新STIX对象)               │
  │ ──────────────────────────────────────────→ │
  │                                             │
  │  10. 返回Status对象(处理状态)               │
  │ ←──────────────────────────────────────────  │
```

### 4.5 TAXII认证与授权

TAXII 2.1支持多种认证方式：

```python
#!/usr/bin/env python3
"""TAXII 2.1客户端实现"""
import requests
import json
from datetime import datetime
from urllib.parse import urljoin

class TAXIIClient:
    """TAXII 2.1客户端"""
    
    def __init__(self, base_url, auth=None, verify_ssl=True):
        self.base_url = base_url.rstrip('/')
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        
        # 认证配置
        if auth:
            if auth.get('type') == 'basic':
                self.session.auth = (auth['user'], auth['password'])
            elif auth.get('type') == 'bearer':
                self.session.headers['Authorization'] = f"Bearer {auth['token']}"
            elif auth.get('type') == 'api_key':
                self.session.headers['X-API-Key'] = auth['key']
        
        self.session.headers.update({
            'Accept': 'application/taxii+json;version=2.1',
            'Content-Type': 'application/taxii+json;version=2.1'
        })
    
    def discover(self):
        """发现服务"""
        url = urljoin(self.base_url + '/', 'discovery')
        resp = self.session.get(url, verify=self.verify_ssl)
        resp.raise_for_status()
        return resp.json()
    
    def get_api_roots(self):
        """获取API Root列表"""
        discovery = self.discover()
        return [root['url'] for root in discovery.get('api_roots', [])]
    
    def get_collections(self, api_root):
        """获取集合列表"""
        url = urljoin(api_root, 'collections/')
        resp = self.session.get(url, verify=self.verify_ssl)
        resp.raise_for_status()
        return resp.json().get('collections', [])
    
    def get_objects(self, api_root, collection_id, 
                    added_after=None, limit=None, 
                    stix_type=None):
        """获取STIX对象"""
        url = urljoin(
            api_root, 
            f'collections/{collection_id}/objects/'
        )
        params = {}
        if added_after:
            params['added_after'] = added_after
        if limit:
            params['limit'] = limit
        if stix_type:
            params['match[type]'] = stix_type
        
        resp = self.session.get(
            url, params=params, verify=self.verify_ssl
        )
        resp.raise_for_status()
        return resp.json()
    
    def add_objects(self, api_root, collection_id, stix_bundle):
        """添加STIX对象"""
        url = urljoin(
            api_root,
            f'collections/{collection_id}/objects/'
        )
        resp = self.session.post(
            url, json=stix_bundle, verify=self.verify_ssl
        )
        resp.raise_for_status()
        return resp.json()
    
    def get_object(self, api_root, collection_id, object_id):
        """获取特定对象"""
        url = urljoin(
            api_root,
            f'collections/{collection_id}/objects/{object_id}/'
        )
        resp = self.session.get(url, verify=self.verify_ssl)
        resp.raise_for_status()
        return resp.json()
    
    def get_manifest(self, api_root, collection_id, 
                     added_after=None, limit=None):
        """获取对象清单"""
        url = urljoin(
            api_root,
            f'collections/{collection_id}/manifest/'
        )
        params = {}
        if added_after:
            params['added_after'] = added_after
        if limit:
            params['limit'] = limit
        
        resp = self.session.get(
            url, params=params, verify=self.verify_ssl
        )
        resp.raise_for_status()
        return resp.json()
    
    def get_status(self, api_root, status_id):
        """获取操作状态"""
        url = urljoin(api_root, f'status/{status_id}/')
        resp = self.session.get(url, verify=self.verify_ssl)
        resp.raise_for_status()
        return resp.json()

# 使用示例
if __name__ == "__main__":
    # 连接TAXII服务器
    client = TAXIIClient(
        base_url="https://cti.example.com",
        auth={
            'type': 'basic',
            'user': 'analyst',
            'password': 'password123'
        },
        verify_ssl=False
    )
    
    # 1. 发现服务
    print("=== Discovery ===")
    discovery = client.discover()
    print(json.dumps(discovery, indent=2))
    
    # 2. 获取API Roots
    print("\n=== API Roots ===")
    roots = client.get_api_roots()
    for root in roots:
        print(f"  {root}")
    
    # 3. 获取集合
    if roots:
        print(f"\n=== Collections ({roots[0]}) ===")
        collections = client.get_collections(roots[0])
        for col in collections:
            print(f"  {col['id']}: {col['title']} ({col.get('description', '')})")
        
        # 4. 获取对象
        if collections:
            col_id = collections[0]['id']
            print(f"\n=== Objects ({col_id}) ===")
            objects = client.get_objects(
                roots[0], col_id,
                added_after="2024-01-01T00:00:00Z",
                limit=10
            )
            for obj in objects.get('objects', []):
                print(f"  [{obj['type']}] {obj.get('name', obj.get('id'))}")
```

---

---

## 📋 内容审核与补充建议

> 针对「TAXII 2.1协议详解」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
