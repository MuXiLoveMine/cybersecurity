# DNS协议基础与安全威胁

### 3.1 DNS协议工作原理

DNS（Domain Name System）是互联网的"电话簿"，负责将人类可读的域名（如 `www.example.com`）转换为IP地址。

**DNS解析流程：**

```
用户访问 www.example.com

步骤1: 查询本地DNS缓存 → 未命中
步骤2: 查询操作系统hosts文件 → 未命中
步骤3: 查询本地配置的递归DNS服务器（如8.8.8.8）

步骤4: 递归DNS服务器开始迭代查询:
  ┌──────────────────────────────────────────────────┐
  │ 4a. 查询根DNS服务器(.)                           │
  │     → 返回 .com TLD服务器地址                      │
  │                                                    │
  │ 4b. 查询 .com TLD服务器                           │
  │     → 返回 example.com 权威服务器地址              │
  │                                                    │
  │ 4c. 查询 example.com 权威服务器                    │
  │     → 返回 www.example.com 的A记录(93.184.216.34) │
  └──────────────────────────────────────────────────┘

步骤5: 递归服务器缓存结果并返回给用户
步骤6: 用户浏览器连接 93.184.216.34:443
```

**DNS记录类型：**

| 记录类型 | 说明 | 示例 |
|---------|------|------|
| A | 域名→IPv4地址 | `example.com. IN A 93.184.216.34` |
| AAAA | 域名→IPv6地址 | `example.com. IN AAAA 2606:2800:220:1::` |
| CNAME | 别名记录 | `www.example.com. IN CNAME example.com.` |
| MX | 邮件交换 | `example.com. IN MX 10 mail.example.com.` |
| TXT | 文本记录（SPF等） | `example.com. IN TXT "v=spf1 -all"` |
| NS | 权威名称服务器 | `example.com. IN NS ns1.example.com.` |

### 3.2 DNS劫持/投毒攻击

**DNS投毒（DNS Poisoning）** 通过向DNS缓存注入伪造记录，使用户访问域名时被导向恶意IP。

```
DNS缓存投毒攻击流程:

1. 用户查询 www.example.com → 递归DNS服务器
2. 递归服务器向权威服务器发起查询（ Transaction ID = 0xAB12）
3. 攻击者抢先向递归服务器发送伪造应答:
   ┌──────────────────────────────────────────┐
   │ DNS Response (伪造)                      │
   │ Transaction ID: 0xAB12 (需猜对)          │
   │ www.example.com → A 6.6.6.6 (恶意IP)     │
   └──────────────────────────────────────────┘
4. 递归服务器缓存伪造记录
5. 后续所有用户访问 www.example.com → 6.6.6.6
```

**DNS劫持类型：**
- **本地DNS劫持**：修改本机hosts文件或DNS配置
- **路由器DNS劫持**：利用路由器弱口令修改DNS设置
- **ISP级DNS劫持**：运营商层面的DNS重定向（常用于广告插入）
- **缓存投毒**：向DNS服务器缓存注入伪造记录

### 3.3 DNS隧道技术

DNS隧道利用DNS协议（53端口）传输非DNS数据，常用于绕过网络访问控制或构建隐蔽C2通道。

```
DNS隧道工作原理:

受控主机                    DNS隧道服务器               C2服务器
   │                              │                        │
   │ 1. 将数据编码为子域名        │                        │
   │    data→base64→xxx.evil.com │                        │
   ├────────────────────────────→│                        │
   │ 2. DNS查询(TXT记录)         │                        │
   │                              │ 3. 解码数据,转发给C2  │
   │                              ├───────────────────────→│
   │                              │ 4. C2响应             │
   │                              ←───────────────────────┤
   │ 5. 伪造DNS TXT应答           │                        │
   │    包含编码后的命令数据       │                        │
   ←────────────────────────────┤                        │
   │ 6. 解码命令并执行            │                        │
```

**常用DNS隧道工具（理论介绍）：**
- `iodine`：IP over DNS隧道
- `dnscat2`：DNS隧道C2框架
- `dns2tcp`：TCP over DNS隧道

### 3.4 DNS放大攻击（DDoS）

DNS放大攻击（DNS Amplification）利用开放DNS解析器，将小请求放大为大响应，实现反射式DDoS。

```
DNS放大攻击流程:

攻击者(伪造源IP=受害者IP)     开放DNS解析器(放大器)      受害者
   │                              │                      │
   │ 1. 发送小DNS查询(60字节)     │                      │
   │    源IP伪造为受害者IP         │                      │
   ├─────────────────────────────→│                      │
   │    查询ANY记录(evil.com)    │                      │
   │    放大倍数: 50-100x         │                      │
   │                              │ 2. 返回大DNS响应     │
   │                              │    (3000-4000字节)   │
   │                              ├─────────────────────→│ 3. 大量流量
   │                              │    大量响应洪泛受害者 │   淹没受害者
   │                              │                      │
```

**放大倍数计算：**
- 请求大小：约60字节（UDP DNS查询）
- 响应大小：约3000-4000字节（ANY查询，含DNSSEC时更大）
- 放大倍数：50x ~ 70x

### 3.5 子域名枚举

子域名枚举是信息收集阶段的重要技术，攻击者通过发现子域名来扩大攻击面。

**子域名枚举方法：**

```
方法1: 字典枚举
  遍历常见子域名字典:
    admin.example.com  → 解析成功 → 存在
    mail.example.com   → 解析成功 → 存在
    test.example.com   → NXDOMAIN → 不存在
    dev.example.com    → 解析成功 → 存在

方法2: 证书透明度日志
  查询 ct.example.com 或 crt.sh:
    搜索 *.example.com 的TLS证书记录
    证书中包含的SAN字段暴露子域名

方法3: DNS区域传送(AXFR)
  dig @ns.example.com example.com AXFR
  (若服务器配置不当,可获取完整区域文件)

方法4: 搜索引擎语法
  Google: site:example.com -www
```

---

---

