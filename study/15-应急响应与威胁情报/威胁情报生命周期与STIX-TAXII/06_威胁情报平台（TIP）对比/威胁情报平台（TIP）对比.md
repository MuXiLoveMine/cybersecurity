# 威胁情报平台（TIP）对比

### 6.1 平台功能对比

| 特性 | MISP | OpenCTI | ThreatConnect | Recorded Future |
|------|------|---------|---------------|-----------------|
| 类型 | 开源 | 开源 | 商业 | 商业 |
| 部署方式 | 自建 | 自建/云 | 云/自建 | SaaS |
| STIX/TAXII | 原生支持 | 原生支持 | 支持 | 支持 |
| 数据存储 | MySQL | ElasticSearch | 专有 | 专有 |
| API | REST | GraphQL+REST | REST | REST |
| 可视化 | 基础 | 强大 | 强大 | 极强 |
| MITRE ATT&CK | 标签支持 | 原生集成 | 集成 | 原生集成 |
| 自动化 | 插件 | 内置 | Playbook | AI驱动 |
| 社区共享 | 全球社区 | 本地 | 封闭 | 专有 |
| 成本 | 免费 | 免费 | 付费 | 付费 |
| 适合规模 | 中小到大型 | 中到大型 | 中到大型 | 大型企业 |

### 6.2 OpenCTI部署示例

```yaml
# docker-compose.yml - OpenCTI部署
version: '3.8'

services:
  redis:
    image: redis:7
    restart: always
    
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.12.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - es_data:/usr/share/elasticsearch/data
    
  minio:
    image: minio/minio:latest
    environment:
      - MINIO_ROOT_PASSWORD=opencti
      - MINIO_ROOT_PASSWORD=opencti
    command: server /data
    volumes:
      - minio_data:/data
    
  rabbitmq:
    image: rabbitmq:3-management
    environment:
      - RABBITMQ_DEFAULT_USER=guest
      - RABBITMQ_DEFAULT_PASS=guest
    
  opencti:
    image: opencti/platform:latest
    environment:
      - NODE_OPTIONS=--max-old-space-size=8096
      - APP__BASE_URL=http://localhost:8080
      - APP__ADMIN__PASSWORD=ChangeMe123!
      - APP__ADMIN__TOKEN=12345678-1234-1234-1234-123456789012
      - REDIS__HOSTNAME=redis
      - ELASTICSEARCH__URL=http://elasticsearch:9200
      - MINIO__ENDPOINT=minio
      - MINIO__ENDPOINT_PORT=9000
      - RABBITMQ__HOSTNAME=rabbitmq
    ports:
      - "8080:8080"
    depends_on:
      - redis
      - elasticsearch
      - minio
      - rabbitmq
    restart: always

volumes:
  es_data:
  minio_data:
```

### 6.3 OpenCTI API使用

```python
#!/usr/bin/env python3
"""OpenCTI Python SDK使用"""
from pycti import OpenCTIApiClient
import json

class OpenCTIManager:
    def __init__(self, url, api_key):
        self.client = OpenCTIApiClient(url, api_key)
    
    def create_threat_actor(self, name, description):
        """创建威胁行为者"""
        actor = self.client.threat_actor.create(
            name=name,
            description=description
        )
        return actor
    
    def create_indicator(self, pattern, name, indicator_type="malicious-activity"):
        """创建指标"""
        indicator = self.client.indicator.create(
            name=name,
            pattern=pattern,
            pattern_type="stix",
            indicator_types=[indicator_type],
            x_opencti_main_observable_type="IPv4-Addr"
        )
        return indicator
    
    def create_malware(self, name, description, malware_types):
        """创建恶意软件"""
        malware = self.client.malware.create(
            name=name,
            description=description,
            malware_types=malware_types
        )
        return malware
    
    def create_relationship(self, from_id, to_id, relationship_type, description=""):
        """创建关系"""
        rel = self.client.stix_core_relationship.create(
            fromId=from_id,
            toId=to_id,
            relationship_type=relationship_type,
            description=description
        )
        return rel
    
    def search_ioc(self, value):
        """搜索IOC"""
        result = self.client.stix_cyber_observable.list(
            filters=[
                {"key": "value", "values": [value]}
            ]
        )
        return result
    
    def get_attack_pattern(self, mitre_id):
        """获取ATT&CK技术"""
        patterns = self.client.attack_pattern.list(
            filters=[
                {"key": "x_mitre_id", "values": [mitre_id]}
            ]
        )
        return patterns

# 使用
if __name__ == "__main__":
    manager = OpenCTIManager(
        url="http://localhost:8080",
        api_key="12345678-1234-1234-1234-123456789012"
    )
    
    # 创建威胁行为者
    actor = manager.create_threat_actor("APT28", "俄罗斯APT组织")
    
    # 创建指标
    indicator = manager.create_indicator(
        pattern="[ipv4-addr:value = '185.220.101.45']",
        name="APT28 C2 IP"
    )
    
    # 创建恶意软件
    malware = manager.create_malware(
        name="Sofacy",
        description="APT28使用的木马",
        malware_types=["trojan", "backdoor"]
    )
    
    # 创建关系
    manager.create_relationship(
        indicator['id'], actor['id'], 'indicates'
    )
    manager.create_relationship(
        actor['id'], malware['id'], 'uses'
    )
    
    print("威胁知识图谱创建完成")
```

---

---

