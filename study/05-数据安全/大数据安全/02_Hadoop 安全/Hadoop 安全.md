# Hadoop 安全

### 2.1 Hadoop 安全架构

Hadoop 安全体系围绕"Kerberos 认证 + ACL 授权 + 审计"三要素构建。未启用安全前，Hadoop 处于"simple"模式，客户端声称自己是任何用户都能被接受，极度危险。

**认证：Kerberos**

用户访问 Hadoop 任何服务前，必须先获取 Kerberos 票据。Kerberos 为每个用户/服务颁发 TGT，服务间通信也通过票据互验，确保"你说的就是你"。

```
Hadoop Kerberos 认证流程:

  用户 → KDC: AS-REQ (用户身份)
  KDC → 用户: TGT (用用户密钥加密)
  用户 → HDFS NameNode: TGT + Service Ticket
  NameNode 验证票据 → 授权访问
```

**授权：ACL**

HDFS 有原生 POSIX-like 权限（owner/group/other 的 rwx），HBase 有 ACL 表。但更细粒度的列级/行级控制需要 Ranger。

**传输加密：**

Hadoop RPC 与数据传输支持 SASL + 加密（AES/3DES），Web UI 支持 SSL。

### 2.2 HDFS 安全

**1. 权限控制：**

```bash
# HDFS POSIX权限
hadoop fs -chmod 750 /user/finance/sensitive
hadoop fs -chown finance:finance /user/finance/sensitive

# 启用ACL（更细粒度）
hadoop fs -setfacl -m user:analyst:rw- /user/finance/reports
hadoop fs -getfacl /user/finance/reports

# 设置sticky位防删除
hadoop fs -chmod 1777 /tmp
```

HDFS ACL 扩展了 POSIX 模型，允许给特定用户/组单独授权，但仍无法做"列级"控制，需 Ranger。

**2. 透明加密（TDE）：**

HDFS 透明加密区（Encryption Zone）在数据写入时自动加密、读取时自动解密，对应用透明。

```bash
# 创建密钥（需KMS服务）
hadoop key create myKey

# 创建加密区
hadoop fs -mkdir /user/secure
hdfs crypto -createZone -keyName myKey -path /user/secure

# 之后写入的数据自动加密
hadoop fs -put sensitive.csv /user/secure/
```

加密区原理：每个加密区有独立的 Data Encryption Key（DEK），DEK 用 Key Encryption Key（KEK）加密后存于 KMS。文件块加密用 EDEK，密钥不在 NameNode 明文存储。

**3. 审计日志：**

```xml
<!-- hdfs-site.xml 启用审计 -->
<property>
  <name>dfs.namenode.audit.log.enabled</name>
  <value>true</value>
</property>
<property>
  <name>dfs.namenode.audit.log.location</name>
  <value>/var/log/hadoop/audit/hdfs-audit.log</value>
</property>
```

审计日志记录每次文件操作（谁、何时、做了什么、成功/失败），是事后追溯的关键。

### 2.3 Hadoop Ranger 统一授权管理

Ranger 提供集中化的策略管理，支持 HDFS/Hive/HBase/Kafka 等组件，可做列级、行级（Hive 行级过滤器）控制。

```json
// Ranger HDFS 策略示例
{
  "policyName": "finance_data_access",
  "resourceName": "/user/finance/*",
  "permissions": [
    {"principal": "finance_group", "access": ["read","execute"], "allow": true},
    {"principal": "auditor", "access": ["read"], "allow": true}
  ]
}
```

Ranger 还提供审计中心，把各组件审计日志汇总，形成"谁访问了什么"的统一视图。

### 2.4 Hadoop 安全配置最佳实践

```xml
<!-- core-site.xml -->
<property>
  <name>hadoop.security.authentication</name>
  <value>kerberos</value>
</property>
<property>
  <name>hadoop.security.authorization</name>
  <value>true</value>
</property>

<!-- hdfs-site.xml -->
<property>
  <name>dfs.encrypt.data.transfer</name>
  <value>true</value>
</property>
<property>
  <name>dfs.data.transfer.protection</name>
  <value>authentication,integrity,privacy</value>
</property>
<property>
  <name>dfs.namenode.audit.log.enabled</name>
  <value>true</value>
</property>
```

```bash
# 关键加固清单
1. 启用 Kerberos (hadoop.security.authentication=kerberos)
2. 启用授权 (hadoop.security.authorization=true)
3. 启用 RPC 加密 (dfs.encrypt.data.transfer=true)
4. 启用审计日志
5. 部署 Ranger 做细粒度授权
6. Web UI 启用 SSL + 认证
7. 敏感数据目录设加密区
8. 禁用匿名访问、默认账户改密
9. 节点间防火墙限制 RPC 端口
10. 定期巡检审计日志
```

---

---

