# Kerberos 认证体系

### 6.1 Kerberos 原理详解

Kerberos 是对称密钥网络认证协议，核心是 KDC（Key Distribution Center）。用户和服务都向 KDC 注册，通过票据（Ticket）机制实现"无需在网络上明文传密码"的认证。

```
Kerberos 三次握手:

1. AS-REQ/AS-REP (获取TGT)
   用户 → KDC的AS: "我是alice, 我要TGT"
   KDC: 用alice的密钥验证身份, 颁发TGT(用TGS密钥加密)

2. TGS-REQ/TGS-REP (获取服务票据)
   用户 → KDC的TGS: 出示TGT, 请求访问hdfs服务
   KDC: 验证TGT, 颁发Service Ticket(用hdfs服务密钥加密)

3. AP-REQ/AP-REP (访问服务)
   用户 → hdfs: 出示Service Ticket
   hdfs: 用自己的密钥解密票据, 验证用户身份, 授权
```

**关键概念：**

| 概念 | 全称/含义 |
|------|----------|
| KDC | Key Distribution Center，认证中心 |
| AS | Authentication Server，认证服务（颁TGT） |
| TGS | Ticket Granting Server，票据授予服务（颁服务票据） |
| TGT | Ticket Granting Ticket，票据授予票据（"入场券"） |
| Service Ticket | 访问具体服务的票据 |
| Principal | Kerberos身份标识，如 alice@REALM 或 hdfs/_HOST@REALM |
| Keytab | 存principal密钥的文件，供服务免密登录 |

Principal 命名规范：`主成分/实例@REALM`。如 `hdfs/namenode.hadoop.com@BIGDATA.COM`，`_HOST` 是占位符，会替换为实际主机名。

### 6.2 Hadoop Kerberos 配置实战

**1. 安装配置 KDC：**

```bash
# 安装Kerberos server (MIT KDC)
yum install -y krb5-server krb5-workstation

# /var/kerberos/krb5kdc/kdc.conf
[realms]
  BIGDATA.COM = {
    kdc_ports = 88
    admin_keytab = /var/kerberos/krb5kdc/kadm5.keytab
    database_name = /var/kerberos/krb5kdc/principal
    max_life = 10h 0m 0s
    max_renewable_life = 7d 0h 0m 0s
  }

# /etc/krb5.conf
[libdefaults]
  default_realm = BIGDATA.COM
  dns_lookup_realm = false
  dns_lookup_kdc = false
  ticket_lifetime = 24h
  renew_lifetime = 7d
  forwardable = true

# 创建数据库
kdb5_util create -s
# 启动KDC和admin
systemctl start krb5kdc kadmin
```

**2. 创建 principals：**

```bash
# 管理员
kadmin.local -q "addprinc admin/admin"
# 用户
kadmin.local -q "addprinc alice"
# 服务(hdfs的namenode)
kadmin.local -q "addprinc -randkey hdfs/namenode.hadoop.com"
# 导出keytab
kadmin.local -q "ktadd -k /etc/security/keytabs/hdfs.keytab hdfs/namenode.hadoop.com"
# 所有节点复用_HOST, 需对每个节点生成对应principal
```

**3. Hadoop 配置启用 Kerberos：**

```xml
<!-- hdfs-site.xml -->
<property>
  <name>dfs.block.access.token.enabled</name><value>true</value>
</property>
<property>
  <name>dfs.namenode.kerberos.principal</name>
  <value>hdfs/_HOST@BIGDATA.COM</value>
</property>
<property>
  <name>dfs.namenode.keytab.file</name>
  <value>/etc/security/keytabs/hdfs.keytab</value>
</property>
<property>
  <name>dfs.datanode.kerberos.principal</name>
  <value>hdfs/_HOST@BIGDATA.COM</value>
</property>
<property>
  <name>dfs.datanode.keytab.file</name>
  <value>/etc/security/keytabs/hdfs.keytab</value>
</property>

<!-- core-site.xml -->
<property>
  <name>hadoop.security.authentication</name><value>kerberos</value>
</property>
<property>
  <name>hadoop.security.authorization</name><value>true</value>
</property>
```

**4. 用户使用：**

```bash
# 申请票据
kinit alice
# 之后即可访问hadoop
hadoop fs -ls /
# 查看票据
klist
# 注销
kdestroy
# keytab免密登录(用于服务)
kinit -kt /etc/security/keytabs/alice.keytab alice
```

### 6.3 Kerberos 运维与故障排查

**常见故障与排查：**

```bash
# 1. "Server not found in Kerberos database"
# 原因: DNS解析与principal不匹配
# 排查:
hostname -f   # 检查主机名是否完整FQDN
nslookup namenode.hadoop.com   # 反向解析是否一致
# 解决: 确保所有节点hostname -f返回FQDN, /etc/hosts配置正确, 反向解析存在

# 2. "Clock skew too great"
# 原因: 节点时间差超5分钟
# 解决: 所有节点装ntp/chrony, 强制同步
chronyc makestep

# 3. "Key version number for principal incorrect"
# 原因: keytab过期或被重新生成, 旧票据失效
# 解决: kdestroy后kinit, 或重新ktadd

# 4. kinit成功但hadoop命令报错GSSException
# 原因: 服务principal没注册或keytab权限错
# 排查:
klist -kt /etc/security/keytabs/hdfs.keytab   # 查看keytab内容
kadmin.local -q "getprinc hdfs/namenode.hadoop.com"  # 比对KVNO
# 解决: KVNO不一致需重新ktadd, keytab权限设为600属主hdfs:hdfs

# 5. TGT过期导致长任务失败
# 解决: 用renewable ticket + 自动renew
kinit -r 7d alice
# 或在yarn-site.xml配置自动renew
```

运维清单：
- KDC 高可用（主备 KDC + 同步）
- keytab 文件权限严格（600，属主对应服务用户）
- 票据自动续期机制（长跑任务必备）
- 监控 KDC 可用性（挂了整个集群登录瘫痪）
- 定期备份 principal 数据库

### 6.4 Kerberos 与其他认证方式对比

| 方式 | 优势 | 劣势 | 适用 |
|------|------|------|------|
| Kerberos | 强身份、双向认证、企业成熟 | 部署复杂、需KDC高可用、时钟敏感 | 大数据集群内部 |
| OAuth2 | 灵活、易集成云原生 | 依赖IdP、令牌管理复杂 | 应用层、API |
| mTLS | 极强、无需KDC | 证书管理复杂、撤销难 | 服务网格、零信任 |
| LDAP/AD | 集中用户管理 | 仅认证不授权、明文需配SSL | 用户目录集成 |

Hadoop 生态主流是 Kerberos + Ranger（认证+授权），KDC 常与 AD/LDAP 集成做用户统一管理。

---

---

## 📋 内容审核与补充建议

> 针对「Kerberos 认证体系」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
