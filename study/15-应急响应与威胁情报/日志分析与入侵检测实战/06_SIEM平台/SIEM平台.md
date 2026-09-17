# SIEM平台

### 5.1 ELK Stack

```yaml
# Logstash配置 - 收集Windows安全日志
input {
  beats {
    port => 5044
  }
}

filter {
  if [log_name] == "Security" {
    # 解析Windows事件日志
    xml {
      source => "message"
      target => "EventXML"
    }

    # 提取事件ID
    grok {
      match => { "message" => "EventID.*?(?<event_id>\d+)" }
    }

    # 4624登录成功
    if [event_id] == "4624" {
      grok {
        match => {
          "message" => "TargetUserName:\s+(?<target_user>\S+).*LogonType:\s+(?<logon_type>\d+).*IpAddress:\s+(?<src_ip>\d+\.\d+\.\d+\.\d+)"
        }
      }
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "windows-security-%{+YYYY.MM.dd}"
  }
}
```

```python
# Elasticsearch查询 - 检测暴力破解
from elasticsearch import Elasticsearch

es = Elasticsearch(["http://localhost:9200"])

# 检测SSH暴力破解
query = {
    "size": 0,
    "query": {
        "bool": {
            "filter": [
                {"range": {"@timestamp": {"gte": "now-1h"}}},
                {"match": {"event.action": "ssh_login_failed"}}
            ]
        }
    },
    "aggs": {
        "by_source_ip": {
            "terms": {"field": "source.ip", "size": 20},
            "aggs": {
                "attempt_count": {"value_count": {"field": "source.ip"}},
                "target_users": {
                    "terms": {"field": "user.name", "size": 10}
                }
            }
        }
    }
}

result = es.search(index="linux-auth-*", body=query)
for bucket in result["aggregations"]["by_source_ip"]["buckets"]:
    ip = bucket["key"]
    count = bucket["doc_count"]
    if count > 50:  # 1小时内超过50次失败
        print(f"[!] 暴力破解: {ip} - {count}次失败登录")
        for user in bucket["target_users"]["buckets"]:
            print(f"    目标用户: {user['key']} ({user['doc_count']}次)")
```

### 5.2 Splunk

```splunk
# Splunk SPL查询示例

# 检测Windows暴力破解
index=windows sourcetype=WinEventLog:Security EventCode=4625
| bucket _time span=5m
| stats count as failures by src_ip, user
| where failures > 10
| sort -failures

# 检测横向移动
index=windows sourcetype=WinEventLog:Security EventCode=4624 LogonType=3
| stats count as logons by src_ip, dest_host, user
| where logons > 20
| sort -logons

# 检测PowerShell滥用
index=windows sourcetype=WinEventLog:Security EventCode=4688
| search "powershell.exe"
| rex field=CommandLine "-enc\s+(?<encoded_command>\S+)"
| eval decoded_command = base64decode(encoded_command)
| table _time, host, user, CommandLine, decoded_command

# 检测持久化
index=windows sourcetype=WinEventLog:Security EventCode=4698
| stats count by TaskName, user, _time
| sort -_time

# 检测数据外传
index=firewall action=allowed
| stats sum(bytes_out) as total_bytes by src_ip, dest_ip
| where total_bytes > 100000000
| sort -total_bytes
```

---

---

## 📋 内容审核与补充建议

> 针对「SIEM平台」部分的内容审核结果：

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
