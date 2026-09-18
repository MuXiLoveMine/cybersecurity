# OpenVPN与WireGuard

### 3.1 OpenVPN配置与安全加固

**服务端配置（server.conf）：**

```ini
# /etc/openvpn/server/server.conf

# 基本设置
port 1194
proto udp
dev tun0
topology subnet

# 证书配置
ca /etc/openvpn/ca.crt
cert /etc/openvpn/server.crt
key /etc/openvpn/server.key
dh /etc/openvpn/dh.pem
tls-crypt /etc/openvpn/tls-crypt.key

# 网络配置
server 10.8.0.0 255.255.255.0
push "route 10.1.0.0 255.255.255.0"
push "redirect-gateway def1 bypass-dhcp"
push "dhcp-option DNS 10.8.0.1"

# 安全加固（重要）
cipher AES-256-GCM
auth SHA512
tls-version-min 1.2
tls-cipher TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384
remote-cert-tls client
verify-x509-name vpn-client name  # 证书绑定
auth-nocache

# 运维设置
keepalive 10 120
persist-key
persist-tun
max-clients 50
user nobody
group nogroup
status /var/log/openvpn/status.log
log-append /var/log/openvpn/openvpn.log
verb 3
```

**安全加固检查清单：**

```
OpenVPN安全加固:
[✓] 使用TLS 1.2+，禁用SSLv3/TLS 1.0/1.1
[✓] 使用tls-crypt或tls-auth防止未授权连接和DoS
[✓] 使用remote-cert-tls client验证客户端证书
[✓] 使用verify-x509-name绑定证书名称
[✓] 使用AES-256-GCM认证加密
[✓] 运行权限降级为nobody/nogroup
[✓] 启用客户端证书吊销列表(CRL)
[✓] 配置auth-nocache防止密钥缓存
[✓] 限制最大客户端数
[✓] 启用keepalive检测断线
[ ] 定期轮换证书和密钥（建议90天）
[ ] 配置双因素认证（OTP）
```

**客户端配置（client.ovpn）：**

```ini
client
dev tun0
proto udp
remote vpn.example.com 1194
resolv-retry infinite
nobind
persist-key
persist-tun

# 安全设置
remote-cert-tls server
verify-x509-name vpn-server name
cipher AES-256-GCM
auth SHA512
tls-version-min 1.2
auth-nocache

# 证书
<ca>
-----BEGIN CERTIFICATE-----
# CA证书内容（模拟数据）
MIIDSzCCAjMCFCXXXX...
-----END CERTIFICATE-----
</ca>

<cert>
-----BEGIN CERTIFICATE-----
# 客户端证书内容（模拟数据）
MIIDCzCCAjMCFCXXXX...
-----END CERTIFICATE-----
</cert>

<key>
-----BEGIN PRIVATE KEY-----
# 客户端私钥内容（模拟数据）
MIIEvQIBADANBXXXX...
-----END PRIVATE KEY-----
</key>

key-direction 1
<tls-crypt>
# TLS加密密钥（模拟数据）
-----BEGIN OpenVPN Static key V1-----
xxxx0000aaaa1111bbbb2222...
-----END OpenVPN Static key V1-----
</tls-crypt>
```

### 3.2 WireGuard现代VPN方案

WireGuard是新一代VPN协议，以代码精简（约4000行）、高性能和高安全性著称。

**服务端配置（wg0.conf）：**

```ini
# /etc/wireguard/wg0.conf

[Interface]
# 服务端虚拟IP
Address = 10.8.0.1/24
# 监听端口
ListenPort = 51820
# 私钥（模拟数据）
PrivateKey = ABCD1234EFGH5678IJKL9012MNOP3456QRST7890UVWX1234YZAB5678CDEF9012=

# 数据包转发
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT
PostUp = iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT
PostDown = iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

# 客户端1
[Peer]
PublicKey = WXYZ9012ABCD3456EFGH7890IJKL1234MNOP5678QRST9012UVWX3456YZAB7890=
# 允许的IP段
AllowedIPs = 10.8.0.2/32
# 保持连接
PersistentKeepalive = 25

# 客户端2
[Peer]
PublicKey = MNOP5678QRST9012UVWX3456YZAB7890CDEF0123ABCD4567EFGH8901IJKL2345=
AllowedIPs = 10.8.0.3/32
PersistentKeepalive = 25
```

**客户端配置：**

```ini
[Interface]
PrivateKey = aaaa1111bbbb2222cccc3333dddd4444eeee5555ffff66660000111122223333=
Address = 10.8.0.2/24
DNS = 10.8.0.1

[Peer]
# 服务端公钥（模拟数据）
PublicKey = EFGH7890IJKL1234MNOP5678QRST9012UVWX3456YZAB7890CDEF0123ABCD4567=
Endpoint = vpn.example.com:51820
# 路由所有流量通过VPN
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
```

**WireGuard优势分析：**

```
WireGuard vs OpenVPN:

性能对比:
├── 吞吐量: WireGuard ~ 900Mbps vs OpenVPN ~ 400Mbps (1Gbps链路)
├── 延迟:    WireGuard ~ 0.5ms vs OpenVPN ~ 2ms
├── 连接恢复: WireGuard ~ 1s  vs OpenVPN ~ 5-10s
└── 代码量:  WireGuard ~ 4000行 vs OpenVPN ~ 100000行

安全特性:
├── 加密: ChaCha20-Poly1305 (AEAD)
├── 密钥交换: Curve25519 (ECDH)
├── 哈希: BLAKE2s
├── 无需密钥协商握手协议（内置密钥轮换）
├── 前向安全（PFS）
└── 没有可协商的加密套件（消除配置降级攻击）
```

### 3.3 证书管理与密钥轮换

**OpenVPN证书管理流程：**

```bash
# 1. 初始化PKI（Easy-RSA工具）
./easyrsa init-pki

# 2. 创建CA
./easyrsa build-ca

# 3. 生成服务端证书
./easyrsa gen-req vpn-server nopass
./easyrsa sign-req server vpn-server

# 4. 生成客户端证书
./easyrsa gen-req client01 nopass
./easyrsa sign-req client client01

# 5. 生成DH参数
./easyrsa gen-dh

# 6. 生成tls-crypt密钥
openvpn --genkey --secret tls-crypt.key

# 7. 吊销证书（密钥轮换时）
./easyrsa revoke client01
./easyrsa gen-crl

# 8. 更新CRL（服务端需定期更新）
cp pki/crl.pem /etc/openvpn/crl.pem
```

**WireGuard密钥管理：**

```bash
# 1. 生成服务端密钥对
wg genkey | tee server_private.key | wg pubkey > server_public.key

# 2. 生成客户端密钥对
wg genkey | tee client_private.key | wg pubkey > client_public.key

# 3. 生成预共享密钥（额外安全层，可选）
wg genpsk > preshared.key

# 4. 添加客户端
wg set wg0 peer $(cat client_public.key) \
    allowed-ips 10.8.0.2/32 \
    preshared-key preshared.key

# 5. 密钥轮换（定期执行）
# 生成新密钥对
wg genkey | tee new_client_private.key | wg pubkey > new_client_public.key
# 更新服务端peer配置
wg set wg0 peer $(cat new_client_public.key) \
    allowed-ips 10.8.0.2/32 \
    preshared-key preshared.key
# 删除旧peer
wg set wg0 peer $(cat old_client_public.key) remove
```

**密钥轮换策略：**

```
密钥轮换计划:
├── 会话密钥: WireGuard自动轮换（无需手动干预）
├── 证书有效期:
│   ├── CA证书: 10年
│   ├── 服务端证书: 2年
│   └── 客户端证书: 1年（到期前30天提醒）
├── PSK预共享密钥: 每90天轮换
├── tls-crypt密钥: 每180天轮换
└── 离职处理: 立即吊销证书/删除peer
```

---

---

## 📋 内容审核与补充建议

> 针对「OpenVPN与WireGuard」部分的内容审核结果：

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
