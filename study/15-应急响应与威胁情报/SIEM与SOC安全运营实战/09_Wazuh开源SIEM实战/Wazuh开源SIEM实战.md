# Wazuh开源SIEM实战

### 9.1 Wazuh架构

Wazuh是一套开源安全平台，融合了HIDS（主机入侵检测）、SIEM日志分析、漏洞检测和合规审计能力。

核心组件：

1. **Wazuh Server**：分析引擎，处理Agent上报的数据、执行规则匹配、生成告警
2. **Wazuh Agent**：部署在被监控主机上的轻量客户端（约5MB），采集日志、文件变更、运行进程等信息并上报Server
3. **Wazuh Indexer**：基于OpenSearch的存储和搜索引擎，存储告警和事件数据
4. **Wazuh Dashboard**：基于OpenSearch Dashboards的可视化界面，提供预置安全仪表板和告警管理

数据流：
```
Agent → Server(解码+规则匹配) → Indexer(索引存储) → Dashboard(可视化展示)
```

### 9.2 安装与部署

**快速安装（CentOS/RHEL）**：

```bash
# 安装Wazuh Server
curl -s https://packages.wazuh.com/4.x/yum/ | sudo tee /etc/yum.repos.d/wazuh.repo
sudo yum install wazuh-manager -y
sudo systemctl enable --now wazuh-manager

# 安装Indexer
sudo yum install wazuh-indexer -y
sudo systemctl enable --now wazuh-indexer

# 安装Dashboard
sudo yum install wazuh-dashboard -y
sudo systemctl enable --now wazuh-dashboard

# 安装Agent（在被监控主机上）
sudo WAZUH_MANAGER="10.0.0.1" \
  WAZUH_REGISTRATION_PASSWORD="password" \
  yum install wazuh-agent -y
sudo systemctl enable --now wazuh-agent
```

**部署规划建议**：
- Agent到Server通信默认使用1514/UDP端口，注意防火墙放行
- 单台Server可管理约5000个Agent（视硬件配置）
- 超过5000 Agent建议部署Server集群
- Indexer独立部署，建议16GB+内存、SSD存储

### 9.3 规则配置与自定义

Wazuh使用XML格式定义解码器（Decoder）和规则（Rule）。

**解码器示例（解析自定义应用日志）**：

```xml
<decoder name="custom-app">
  <prematch>^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2} \w+ </prematch>
  <regex>^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}) (\w+) (\S+) (\S+) (\d+)</regex>
  <order>timestamp,level,user,action,result_code</order>
</decoder>
```

**规则示例（检测异常用户创建）**：

```xml
<group name="linux, usermanagement,">
  <rule id="100200" level="10">
    <if_sid>530</if_sid>
    <match>adduser</match>
    <description>New user account created: $(user)</description>
    <group>usermanagement,account_change,</group>
  </rule>

  <rule id="100201" level="12">
    <if_sid>100200</if_sid>
    <user>^root$</user>
    <description>Root user created a new account - potential privilege escalation</description>
  </rule>
</group>
```

- level字段定义严重级别（0-15），10+为高危
- if_sid引用父规则，实现规则链
- match/regex支持字符串匹配和正则匹配

### 9.4 集成漏洞检测与文件完整性监控

**漏洞检测（Vulnerability Detection）**：

Wazuh Agent定期收集主机已安装软件包清单，与CVE数据库比对，自动发现已知漏洞。

配置（在ossec.conf中启用）：
```xml
<vulnerability-detector>
  <enabled>yes</enabled>
  <interval>1h</interval>
  <ignore_time>6h</ignore_time>
  <run_on_start>yes</run_on_start>
  <providers>
    <provider name="canonical">yes</provider>
    <provider name="nvd">yes</provider>
    <provider name="redhat">yes</provider>
    <provider name="msu">yes</provider>
  </providers>
</vulnerability-detector>
```

Dashboard会自动展示漏洞统计：按严重级别分布、受影响主机列表、Top CVE列表。

**文件完整性监控（FIM）**：

```xml
<syscheck>
  <disabled>no</disabled>
  <frequency>3600</frequency>
  <directories>/etc,/usr/bin,/usr/sbin,/bin,/sbin</directories>
  <directories>/var/www,/opt/app/config</directories>
  <ignore>/etc/mtab</ignore>
  <ignore>/etc/hostname</ignore>
  <nodiff>/etc/ssl/private</nodiff>
</syscheck>
```

FIM会记录被监控目录下文件的添加、修改、删除事件，并计算文件MD5/SHA256哈希。当关键系统文件被篡改时，立即触发告警——这是检测Webshell植入和后门持久化的有效手段。

### 9.5 告警配置与响应

**Active Response（主动响应）**：

Wazuh支持在规则触发后自动执行响应脚本：

```xml
<command>
  <name>firewall-drop</name>
  <executable>firewall-drop.sh</executable>
  <expect>srcip</expect>
  <timeout_allowed>yes</timeout_allowed>
</command>

<active-response>
  <command>firewall-drop</command>
  <location>local</location>
  <rules_id>100201</rules_id>
  <timeout>3600</timeout>
</active-response>
```

此配置在规则100201触发时，自动在本地防火墙添加对源IP的drop规则，持续1小时后自动解除。

**告警分级配置**：

Wazuh的rule level共16级（0-15）：
- Level 0：无告警
- Level 1-3：低危信息通知
- Level 4-7：中危需要关注
- Level 8-11：高危安全事件
- Level 12-15：严重安全事件

可在ossec.conf中配置按级别路由告警：
```xml
<alerts>
  <log_alert_level>5</log_alert_level>
  <email_alert_level>10</email_alert_level>
  <use_geoip>yes</use_geoip>
</alerts>
```

---

---

## 📋 内容审核与补充建议

> 针对「Wazuh开源SIEM实战」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
