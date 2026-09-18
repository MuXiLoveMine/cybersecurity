# Kafka 安全

### 4.1 Kafka 安全机制

Kafka 安全三件套：**SASL 认证 + SSL 加密 + ACL 授权**。

```
Kafka 安全栈:

客户端
  ├── SASL认证 (PLAIN/SCRAM/GSSAPI(Kerberos)/OAUTHBEARER)
  ├── SSL加密 (mTLS双向认证 或 单向+SASL)
  └── ACL授权 (topic/group/cluster级权限)
Broker
  ├── 监听器隔离 (INTERNAL/EXTERNAL分端口)
  ├── SSL/TLS
  └── 审计日志
```

**认证机制对比：**

| 机制 | 说明 | 适用 |
|------|------|------|
| SASL/PLAIN | 用户名密码（明文传输，需配SSL） | 内网简单场景 |
| SASL/SCRAM | 用户名密码+挑战（密码不在broker存明文） | 推荐，无Kerberos |
| SASL/GSSAPI | Kerberos | 大企业、与Hadoop统一 |
| SSL mTLS | 双向证书认证 | 高安全要求 |
| OAUTHBEARER | OAuth2令牌 | 云原生、多租户 |

### 4.2 Kafka 安全配置实战

**1. 启用 SSL + SASL/SCRAM：**

```bash
# 创建SCRAM用户
kafka-configs.sh --zookeeper zoo1:2181 --alter \
  --add-config 'SCRAM-SHA-256=[password=mysecret]' \
  --entity-type users --entity-name alice

# broker配置 server.properties
listeners=INTERNAL://broker1:9092,EXTERNAL://broker1:9094
advertised.listeners=EXTERNAL://broker1:9094
listener.security.protocol.map=INTERNAL:SASL_SSL,EXTERNAL:SASL_SSL
sasl.enabled.mechanisms=SCRAM-SHA-256
sasl.mechanism.inter.broker.protocol=SCRAM-SHA-256

# SSL配置
ssl.keystore.location=/etc/kafka/keystore.jks
ssl.keystore.password=changeit
ssl.truststore.location=/etc/kafka/truststore.jks
ssl.truststore.password=changeit
ssl.client.auth=required                    # 强制客户端证书
```

**2. 客户端 JAAS 配置：**

```bash
# 客inaaas.conf
KafkaClient {
  org.apache.kafka.common.security.scram.ScramLoginModule required
  username="alice"
  password="mysecret";
};

# client配置
security.protocol=SASL_SSL
sasl.mechanism=SCRAM-SHA-256
ssl.truststore.location=/etc/kafka/client.truststore.jks
ssl.truststore.password=changeit
```

**3. ACL 授权：**

```bash
# 授权alice对topic 'transactions'的读写
kafka-acls.sh --authorizer-properties \
  zookeeper.connect=zoo1:2181 \
  --add --allow-principal User:alice \
  --operation Read --operation Write \
  --topic transactions

# 授权消费组
kafka-acls.sh --add --allow-principal User:alice \
  --operation Read --group analytics-consumer

# 拒绝某用户(显式Deny优先)
kafka-acls.sh --add --deny-principal User:bob \
  --operation Write --topic sensitive
```

### 4.3 Kafka 安全监控与审计

```bash
# 启用审计日志(authorizer logger)
# log4j.properties
log4j.logger.kafka.authorizer.logger=INFO, authorizerAppender

# 审计日志会记录每次ACL判定: 允许/拒绝、用户、操作、资源
# 查看权限
kafka-acls.sh --list --principal User:alice

# 监控未授权访问告警(日志中Deny)
grep "DENIED" /var/log/kafka/authorizer.log
```

监控指标：
- 认证失败次数突增 → 暴力破解或证书过期
- DENIED 频繁 → 可能有越权尝试
- TLS 握手失败率 → 客户端配置错误或攻击

---

---

## 📋 内容审核与补充建议

> 针对「Kafka 安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
