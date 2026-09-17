# Spark 安全

### 3.1 Spark 安全架构

Spark 安全包含认证、授权、加密三部分。认证确保用户/服务身份；授权控制谁能否提交/查看任务；加密保护 RPC 与数据传输。

```
Spark 安全组件:

认证层: Spark 认证(SASL/Kerberos) + UI认证
授权层: Spark ACL (查看/修改权限)
加密层: RPC加密(SASL) + 数据传输SSL
存储层: 与HDFS/HBase加密联动
```

### 3.2 Spark RPC 安全配置

Spark 内部 RPC（driver-executor、executor-executor）默认明文。启用 SASL 加密。

```bash
# spark-defaults.conf
spark.authenticate true
spark.authenticate.secret MySecretKey        # 共享密钥(非Kerberos模式)

# 或使用Kerberos
spark.kerberos.principal spark/_HOST@REALM
spark.kerberos.keytab /etc/security/keytabs/spark.keytab
spark.kerberos.access.hadoopFileSystems hdfs://namenode:8020
```

`spark.authenticate=true` 启用后，所有 RPC 通信需验证，防止恶意节点加入集群。

### 3.3 Spark 数据加密（SSL/TLS）

```bash
# spark-defaults.conf
spark.ssl.enabled true
spark.ssl.keyStore /etc/spark/keystore.jks
spark.ssl.keyStorePassword changeit
spark.ssl.keyPassword changeit
spark.ssl.trustStore /etc/spark/truststore.jks
spark.ssl.trustStorePassword changeit

# 启用后, UI和文件服务器都走HTTPS
spark.ui.https.enabled true
```

生成密钥库：

```bash
keytool -genkeypair -alias spark -keyalg RSA -keysize 2048 \
  -keystore /etc/spark/keystore.jks -validity 3650 \
  -dname "CN=spark-host, OU=bigdata, O=company, C=CN"
```

### 3.4 Spark on Kubernetes 安全

Spark on K8s 是现代趋势。安全要点：

```yaml
# Spark-submit 参数示例
spark.kubernetes.namespace = analytics           # 隔离命名空间
spark.kubernetes.authenticate.driverServiceAccountName = spark-sa  # SA
spark.kubernetes.driver.secrets=spark-secret    # 挂载密钥(Kerberos keytab)
spark.kubernetes.executor.secrets=spark-secret
spark.kubernetes.driver.podTemplateFile=/path/template.yaml
```

关键安全措施：
1. **RBAC：** Spark ServiceAccount 只授予最小权限，禁止 list/create pods 全集群权限。
2. **NetworkPolicy：** 限制 driver/executor 只能访问指定数据源。
3. **镜像安全：** 用私有镜像仓库 + 镜像签名校验，禁止拉取任意镜像。
4. **Secret 管理：** Kerberos keytab、数据库密码用 K8s Secret 或 Vault 注入，不硬编码。
5. **Pod Security：** 启用 PodSecurityPolicy/PodSecurity admission，禁止 privileged 容器。

---

---

## 📋 内容审核与补充建议

> 针对「Spark 安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
