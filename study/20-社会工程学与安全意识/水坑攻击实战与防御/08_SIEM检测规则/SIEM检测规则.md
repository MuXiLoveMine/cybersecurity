# SIEM检测规则

### 8.1 Splunk检测规则

```splunk
# Splunk SPL - 水坑攻击检测规则

# 规则1: 检测网站内容异常变化
index=web_proxy sourcetype=web_access
| stats count by dest_host, uri_path
| where count > 100
| lookup baseline_sites dest_host OUTPUT baseline_hash
| eval hash_changed = if(isnull(baseline_hash), "no_baseline", "changed")
| where hash_changed="changed"
| eval severity="HIGH"
| alert

# 规则2: 检测可疑外部JavaScript加载
index=web_proxy sourcetype=web_access
| eval external_js = if(match(uri_path, "\.js$") AND
    dest_host != referer_host, 1, 0)
| stats count, values(dest_ip) as dest_ips,
    values(dest_host) as dest_hosts by src_ip
| where external_js > 0
| search NOT [| inputlookup known_cdn_domains
  | fields dest_host]
| alert

# 规则3: 检测浏览器异常子进程
index=endpoint_events sourcetype=process_*
| search (parent_process_name=chrome.exe
    OR parent_process_name=msedge.exe
    OR parent_process_name=firefox.exe)
| search process_name!=chrome.exe
    process_name!=msedge.exe
    process_name!=firefox.exe
    process_name!=conhost.exe
| stats count by host, parent_process,
    process_name, process_command
| where match(process_command, "(?i)(powershell|cmd|certutil|bitsadmin|regsvr32|mshta|rundll32)")
| eval severity="CRITICAL"
| alert

# 规则4: 检测可疑DNS查询(新注册域名)
index=dns_logs sourcetype=dns_query
| lookup domain_age domain OUTPUT registration_date
| eval age_days = if(isnull(registration_date),
    9999, tostring(now() - strptime(registration_date, "%Y-%m-%d")))
| where age_days < 7
| stats count by src_ip, query
| eval severity="MEDIUM"
| alert

# 规则5: 检测exploit kit特征
index=web_proxy sourcetype=web_access
| search (uri_path="*exploit*" OR uri_path="*shellcode*"
    OR uri_path="*payload*" OR uri_path="*sploit*")
| stats count by src_ip, dest_host, uri_path
| eval severity="CRITICAL"
| alert

# 规则6: 检测条件注入(仅对特定IP加载恶意代码)
index=web_proxy sourcetype=web_access
| stats dc(user_agent) as ua_count,
    values(user_agent) as uas by dest_host, uri_path
| where ua_count > 3
| eval severity="HIGH"
| alert
```

### 8.2 Elastic SIEM规则

```json
// Elastic SIEM - 水坑攻击检测规则

// Rule: 可疑浏览器子进程
{
  "query": {
    "bool": {
      "must": [
        {"match": {"event.category": "process"}},
        {"bool": {"should": [
          {"match": {"process.parent.name": "chrome.exe"}},
          {"match": {"process.parent.name": "msedge.exe"}},
          {"match": {"process.parent.name": "firefox.exe"}}
        ]}},
        {"bool": {"must_not": [
          {"match": {"process.name": "chrome.exe"}},
          {"match": {"process.name": "msedge.exe"}},
          {"match": {"process.name": "firefox.exe"}},
          {"match": {"process.name": "conhost.exe"}}
        ]}},
        {"bool": {"should": [
          {"wildcard": {"process.command_line": "*powershell*"}},
          {"wildcard": {"process.command_line": "*cmd.exe*"}},
          {"wildcard": {"process.command_line": "*certutil*"}},
          {"wildcard": {"process.command_line": "*bitsadmin*"}},
          {"wildcard": {"process.command_line": "*regsvr32*"}},
          {"wildcard": {"process.command_line": "*mshta*"}}
        ]}}
      ]
    }
  },
  "severity": "critical",
  "tags": ["watering-hole", "drive-by", "initial-access"],
  "description": "检测浏览器生成可疑子进程,可能是水坑攻击exploit成功执行"
}

// Rule: 新注册域名访问
{
  "query": {
    "bool": {
      "must": [
        {"match": {"event.category": "network"}},
        {"match": {"dns.question.registered_age_days": "<7"}}
      ]
    }
  },
  "severity": "medium",
  "tags": ["watering-hole", "c2-infrastructure"],
  "description": "访问7天内注册的新域名,可能是攻击者C2基础设施"
}
```

---

---

## 📋 内容审核与补充建议

> 针对「SIEM检测规则」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
