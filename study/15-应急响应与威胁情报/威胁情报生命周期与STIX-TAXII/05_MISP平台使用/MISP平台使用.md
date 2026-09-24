# MISP平台使用

### 5.1 MISP架构与部署

**MISP**（Malware Information Sharing Platform）是开源的威胁情报共享平台，支持STIX/TAXII、OpenIOC等多种格式。

```
┌────────────────────────────────────────────────────────┐
│                    MISP 架构                            │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ Web UI   │  │ REST API │  │ Python SDK(PyMISP)│   │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘   │
│       │              │                  │              │
│       └──────────────┴──────────────────┘              │
│                        │                               │
│               ┌────────┴────────┐                     │
│               │   MISP Core      │                     │
│               │   (CakePHP)      │                     │
│               └────────┬────────┘                     │
│                        │                               │
│               ┌────────┴────────┐                     │
│               │   MySQL/MariaDB  │                     │
│               │   (数据存储)       │                     │
│               └─────────────────┘                     │
│                                                        │
│  ┌──────────────────────────────────────────────┐     │
│  │            集成模块                            │     │
│  │  STIX/TAXII │ CIRCL │ VirusTotal │ MITRE     │     │
│  └──────────────────────────────────────────────┘     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Docker部署：**

```yaml
# docker-compose.yml - MISP部署
version: '3.8'

services:
  misp:
    image: harvarditsecurity/misp:latest
    container_name: misp
    ports:
      - "8080:80"
      - "8443:443"
    environment:
      - MISP_HOSTNAME=misp.local
      - MISP_EMAIL=admin@misp.local
      - MYSQL_ROOT_PASSWORD=misp_db_password
      - MISP_ADMIN_EMAIL=admin@misp.local
      - MISP_ADMIN_PASSPHRASE=AdminPassword123!
      - MISP_ADMIN_KEY=abcdef0123456789abcdef0123456789
    volumes:
      - misp_web:/var/www/MISP
      - misp_db:/var/lib/mysql
    restart: unless-stopped

volumes:
  misp_web:
  misp_db:
```

```bash
# 启动MISP
docker-compose up -d

# 验证服务
docker-compose ps
curl -k https://localhost:8443

# 获取API Key（管理界面: User Settings -> My Profile -> Auth Key）
# 或通过CLI
docker exec misp /var/www/MISP/app/Console/cake Admin getAuthKey admin@admin.test
```

### 5.2 事件管理

MISP中的核心概念是**事件（Event）**，每个事件是一组相关的情报数据。

```python
#!/usr/bin/env python3
"""使用PyMISP管理MISP事件和属性"""
from pymisp import PyMISP, MISPEvent, MISPAttribute
from pymisp import MISPObject, MISPTag
import json

class MISPManager:
    def __init__(self, url, api_key, verify_cert=False):
        self.misp = PyMISP(url, api_key, verify_cert, debug=False)
    
    def create_event(self, info, threat_level=2, analysis=0, 
                     distribution=0, tags=None):
        """创建事件"""
        event = MISPEvent()
        event.info = info
        event.threat_level_id = threat_level  # 1=高, 2=中, 3=低, 4=未知
        event.analysis = analysis  # 0=初始, 1=调查中, 2=完成
        event.distribution = distribution  # 0=仅自己, 1=本组织, 2=社区, 3=全部
        
        if tags:
            for tag_name in tags:
                event.add_tag(tag_name)
        
        result = self.misp.add_event(event)
        return result
    
    def add_attribute(self, event_id, attr_type, attr_value, 
                      category=None, comment=None, to_ids=True):
        """添加属性到事件"""
        event = self.misp.get_event(event_id)
        
        attribute = MISPAttribute()
        attribute.type = attr_type
        attribute.value = attr_value
        if category:
            attribute.category = category  #Payload delivery, Artifacts dropped, etc.
        if comment:
            attribute.comment = comment
        attribute.to_ids = to_ids  # 是否用于IDS检测
        
        result = self.misp.add_attribute(event_id, attribute)
        return result
    
    def add_attributes_batch(self, event_id, attributes):
        """批量添加属性"""
        event = self.misp.get_event(event_id)
        
        for attr in attributes:
            event.add_attribute(
                type=attr['type'],
                value=attr['value'],
                category=attr.get('category'),
                comment=attr.get('comment', ''),
                to_ids=attr.get('to_ids', True)
            )
        
        result = self.misp.update_event(event)
        return result
    
    def search_ioc(self, value=None, type=None, tags=None, 
                   category=None, timestamp=None):
        """搜索IOC"""
        result = self.misp.search(
            value=value,
            type_attribute=type,
            tags=tags,
            category=category,
            timestamp=timestamp
        )
        return result
    
    def add_tag_to_event(self, event_id, tag_name):
        """添加标签到事件"""
        result = self.misp.tag(event_id, tag_name)
        return result
    
    def add_object(self, event_id, template_name, attributes):
        """添加MISP对象（结构化属性集合）"""
        event = self.misp.get_event(event_id)
        
        obj = MISPObject(template_name)
        for attr_name, attr_value in attributes.items():
            obj.add_attribute(attr_name, value=attr_value)
        
        event.add_object(obj)
        result = self.misp.update_event(event)
        return result

# 使用示例
if __name__ == "__main__":
    manager = MISPManager(
        url="https://localhost:8443",
        api_key="abcdef0123456789abcdef0123456789",
        verify_cert=False
    )
    
    # 1. 创建事件
    event = manager.create_event(
        info="APT28 C2基础设施发现",
        threat_level=1,  # 高威胁
        analysis=1,       # 调查中
        distribution=2,   # 社区共享
        tags=["APT28", "C2", "Russia", "tlp:amber"]
    )
    event_id = event['Event']['id']
    print(f"创建事件: {event_id}")
    
    # 2. 添加属性
    attributes = [
        {'type': 'ip-src', 'value': '185.220.101.45', 
         'category': 'Network activity', 'comment': 'APT28 C2服务器'},
        {'type': 'domain', 'value': 'c2.evil.com',
         'category': 'Network activity', 'comment': 'APT28 C2域名'},
        {'type': 'url', 'value': 'http://c2.evil.com/payload.exe',
         'category': 'Payload delivery', 'comment': 'APT28投递URL'},
        {'type': 'sha256', 'value': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
         'category': 'Artifacts dropped', 'comment': 'APT28恶意样本'},
    ]
    manager.add_attributes_batch(event_id, attributes)
    print(f"添加了 {len(attributes)} 个属性")
    
    # 3. 添加标签
    manager.add_tag_to_event(event_id, "mitre-attack:T1566.001")
    
    # 4. 添加MISP对象（文件对象）
    manager.add_object(event_id, "file", {
        'filename': 'payload.exe',
        'size-in-bytes': '24576',
        'sha256': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        'mimetype': 'application/x-msdownload'
    })
    
    # 5. 搜索IOC
    results = manager.search_ioc(
        value="185.220.101.45",
        type="ip-src"
    )
    print(f"搜索结果: {json.dumps(results, indent=2, ensure_ascii=False)}")
```

### 5.3 MISP与STIX/TAXII集成

```bash
# MISP导出STIX 2.1格式
# 通过API
curl -k -H "Authorization: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -X POST "https://localhost:8443/events/restSearch" \
  -d '{"format":"stix2","tags":["APT28"]}' \
  | jq .

# 通过PyMISP导出
python3 -c "
from pymisp import PyMISP
misp = PyMISP('https://localhost:8443', 'YOUR_API_KEY', False)
events = misp.search(tags=['APT28'], pythonify=True)
stix = misp.stix2_export(events)
print(stix)
"

# MISP作为TAXII服务器
# 启用MISP TAXII扩展
cd /var/www/MISP/app
# 安装cti-taxii-server
pip3 install taxii2-server
# 配置MISP TAXII
cat > /var/www/MISP/taxii_config.json << 'EOF'
{
  "api_root": "https://misp.local/taxii2/api/v21/",
  "collection": "misp",
  "title": "MISP TAXII 2.1 Server",
  "description": "MISP threat intelligence via TAXII 2.1"
}
EOF
```

```python
#!/usr/bin/env python3
"""MISP STIX/TAXII集成工具"""
from pymisp import PyMISP
from stix2 import parse, Bundle
import json
import requests

class MISPSTIXBridge:
    """MISP与STIX/TAXII桥接工具"""
    
    def __init__(self, misp_url, misp_key, verify_cert=False):
        self.misp = PyMISP(misp_url, misp_key, verify_cert)
    
    def misp_to_stix(self, event_id=None, tags=None, 
                     date_from=None, date_to=None):
        """将MISP事件转换为STIX Bundle"""
        # 从MISP获取事件
        if event_id:
            events = [self.misp.get_event(event_id, pythonify=True)]
        else:
            events = self.misp.search(
                tags=tags,
                date_from=date_from,
                date_to=date_to,
                pythonify=True
            )
        
        stix_objects = []
        
        for event in events:
            # 创建Identity
            identity = {
                "type": "identity",
                "spec_version": "2.1",
                "id": f"identity--{event.uuid}",
                "created": event.timestamp.isoformat() + "Z",
                "modified": event.timestamp.isoformat() + "Z",
                "name": event.orgc_id if hasattr(event, 'orgc_id') else "MISP",
                "identity_class": "organization"
            }
            stix_objects.append(identity)
            
            # 转换属性为Indicator
            indicators = []
            for attr in event.attributes:
                indicator = self._attr_to_indicator(attr, event, identity['id'])
                if indicator:
                    stix_objects.append(indicator)
                    indicators.append(indicator)
            
            # 创建Intrusion Set（如果有标签）
            if any(t.name.startswith('APT') for t in event.tags):
                intrusion_set = {
                    "type": "intrusion-set",
                    "spec_version": "2.1",
                    "id": f"intrusion-set--{event.uuid}",
                    "created": event.timestamp.isoformat() + "Z",
                    "modified": event.timestamp.isoformat() + "Z",
                    "name": event.info,
                    "description": event.info,
                    "aliases": [t.name for t in event.tags]
                }
                stix_objects.append(intrusion_set)
                
                # 创建关系
                for ind in indicators:
                    relationship = {
                        "type": "relationship",
                        "spec_version": "2.1",
                        "id": f"relationship--{ind['id'].split('--')[1][:8]}-{event.uuid[:8]}",
                        "created": event.timestamp.isoformat() + "Z",
                        "modified": event.timestamp.isoformat() + "Z",
                        "relationship_type": "indicates",
                        "source_ref": ind['id'],
                        "target_ref": intrusion_set['id']
                    }
                    stix_objects.append(relationship)
        
        bundle = {"type": "bundle", "objects": stix_objects}
        return bundle
    
    def _attr_to_indicator(self, attr, event, identity_id):
        """将MISP属性转换为STIX Indicator"""
        # MISP类型到STIX Pattern的映射
        pattern_map = {
            'ip-src': "ipv4-addr:value = '{}'",
            'ip-dst': "ipv4-addr:value = '{}'",
            'domain': "domain-name:value = '{}'",
            'hostname': "domain-name:value = '{}'",
            'url': "url:value = '{}'",
            'md5': "file:hashes.MD5 = '{}'",
            'sha1': "file:hashes.'SHA-1' = '{}'",
            'sha256': "file:hashes.'SHA-256' = '{}'",
            'email-src': "email-addr:value = '{}'",
            'email-dst': "email-addr:value = '{}'",
        }
        
        stix_type = attr.type
        if stix_type not in pattern_map:
            return None
        
        pattern = f"[{pattern_map[stix_type].format(attr.value)}]"
        
        return {
            "type": "indicator",
            "spec_version": "2.1",
            "id": f"indicator--{attr.uuid}",
            "created": attr.timestamp.isoformat() + "Z" if hasattr(attr, 'timestamp') else event.timestamp.isoformat() + "Z",
            "modified": attr.timestamp.isoformat() + "Z" if hasattr(attr, 'timestamp') else event.timestamp.isoformat() + "Z",
            "name": f"{attr.type}: {attr.value}",
            "description": attr.comment or event.info,
            "pattern": pattern,
            "pattern_type": "stix",
            "valid_from": event.date.isoformat() + "T00:00:00Z" if hasattr(event, 'date') else event.timestamp.isoformat() + "Z",
            "indicator_types": ["malicious-activity"],
            "created_by_ref": identity_id
        }
    
    def push_to_taxii(self, stix_bundle, taxii_url, taxii_auth, 
                      collection_id):
        """将STIX Bundle推送到TAXII服务器"""
        headers = {
            'Accept': 'application/taxii+json;version=2.1',
            'Content-Type': 'application/taxii+json;version=2.1',
            'Authorization': f'Bearer {taxii_auth}'
        }
        
        url = f"{taxii_url}/collections/{collection_id}/objects/"
        resp = requests.post(url, json=stix_bundle, headers=headers)
        return resp.json()

# 使用示例
if __name__ == "__main__":
    bridge = MISPSTIXBridge(
        misp_url="https://localhost:8443",
        misp_key="YOUR_API_KEY",
        verify_cert=False
    )
    
    # MISP -> STIX
    bundle = bridge.misp_to_stix(tags=["APT28"])
    print(f"生成STIX Bundle, 包含 {len(bundle['objects'])} 个对象")
    print(json.dumps(bundle, indent=2, ensure_ascii=False)[:2000])
    
    # 推送到TAXII
    # status = bridge.push_to_taxii(
    #     stix_bundle=bundle,
    #     taxii_url="https://taxii.example.com/api/v21",
    #     taxii_auth="taxii_token",
    #     collection_id="misp-collection"
    # )
    # print(f"TAXII推送状态: {status}")
```

---

---

