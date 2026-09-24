# CoAP安全机制DTLS

### 4.1 DTLS概述

CoAP使用DTLS（Datagram Transport Layer Security）作为安全传输层。DTLS是TLS的UDP版本，在保持TLS安全性的同时适应无连接传输：

```
TLS vs DTLS:

TLS (TCP)                    DTLS (UDP)
├── 面向连接                  ├── 无连接
├── 可靠传输                  ├── 不可靠传输
├── 有序到达                  ├── 无序到达
├── 不丢包                    ├── 可能丢包
├── 重传由TCP处理             ├── 重传由DTLS处理
└── 头部开销较大              └── 头部开销更大

DTLS额外机制:
1. 显式序号(Record Sequence)
2. 重传定时器
3. 握手消息分片
4. HelloVerifyRequest(防DoS)
```

### 4.2 DTLS握手过程

```
DTLS 1.2 握手流程:

Client                                          Server
  │                                                │
  │─── ClientHello (无Cookie) ──────────────────→  │  ①
  │                                                │
  │←── HelloVerifyRequest (Cookie) ─────────────  │  ②
  │                                                │
  │─── ClientHello (带Cookie) ─────────────────→  │  ③
  │                                                │
  │←── ServerHello, Certificate,                  │
  │    ServerKeyExchange, CertificateRequest,     │  ④
  │    ServerHelloDone ──────────────────────     │
  │                                                │
  │─── Certificate, ClientKeyExchange,            │
  │    ChangeCipherSpec, Finished ────────────→   │  ⑤
  │                                                │
  │←── ChangeCipherSpec, Finished ─────────────   │  ⑥
  │                                                │
  │════════ 加密数据传输 ═════════════════════════  │  ⑦

①②③: 防DoS的Cookie交换
④: 服务器证书和密钥交换
⑤: 客户端证书和密钥交换
⑥: 切换到加密模式
⑦: 加密数据传输
```

### 4.3 DTLS加密套件

```
CoAP/DTLS常用加密套件:

1. PSK (预共享密钥)
   - TLS_PSK_WITH_AES_128_CCM_8
   - TLS_PSK_WITH_AES_256_CCM_8
   - 优势: 计算开销小
   - 劣势: 密钥管理困难
   
2. RPK (原始公钥)
   - TLS_ECDHE_ECDSA_WITH_AES_128_CCM_8
   - 使用原始ECDSA公钥（非证书）
   - 优势: 无需PKI基础设施
   - 劣势: 需要预配置公钥
   
3. 证书 (X.509)
   - TLS_ECDHE_ECDSA_WITH_AES_128_CCM_8
   - 使用X.509证书
   - 优势: 标准PKI体系
   - 劣势: 证书开销大

开销对比:
┌──────────────┬──────────┬──────────┬──────────┐
│ 模式          │ 握手大小 │ RAM消耗  │ CPU消耗  │
├──────────────┼──────────┼──────────┼──────────┤
│ 无安全(明文)  │ 0 bytes  │ ~0 KB    │ 最低     │
│ PSK          │ ~100B    │ ~1 KB    │ 低       │
│ RPK          │ ~300B    │ ~4 KB    │ 中       │
│ X.509        │ ~2KB     │ ~10 KB   │ 高       │
└──────────────┴──────────┴──────────┴──────────┘
```

---

---

