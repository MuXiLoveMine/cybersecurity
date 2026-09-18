# CoAP协议安全详解

## 目录

- [1. CoAP协议概述](#1-coap协议概述)
- [2. CoAP协议架构](#2-coap协议架构)
- [3. CoAP消息格式详解](#3-coap消息格式详解)
- [4. CoAP安全机制DTLS](#4-coap安全机制dtls)
- [5. CoAP安全威胁分析](#5-coap安全威胁分析)
- [6. CoAP攻击技术与案例](#6-coap攻击技术与案例)
- [7. CoAP安全加固方案](#7-coap安全加固方案)
- [8. OSCORE：CoAP对象安全](#8-oscorecoap对象安全)
- [9. CoAP安全测试工具与实践](#9-coap安全测试工具与实践)
- [10. 与其他IoT协议安全对比](#10-与其他iot协议安全对比)

---

## 1. CoAP协议概述

### 1.1 协议背景

CoAP（Constrained Application Protocol，受限应用协议）是IETF专为资源受限的IoT设备设计的应用层协议。它于2014年6月正式发布为RFC 7252，主要运行在UDP之上，具有以下设计目标：

```
设计目标:
1. 轻量级：专为内存<100KB、CPU<10MHz的设备设计
2. REST架构：支持GET/POST/PUT/DELETE方法
3. 异步通信：支持设备休眠后的延迟响应
4. 多播支持：支持一对多通信
5. 简单代理：支持资源发现和代理缓存
6. 低开销：头部仅4字节（HTTP头部通常数百字节）
```

### 1.2 CoAP vs HTTP对比

| 特性 | HTTP | CoAP |
|------|------|------|
| 传输层 | TCP | UDP |
| 头部大小 | 数百字节 | 4-8字节 |
| 方法 | GET/POST/PUT/DELETE等 | GET/POST/PUT/DELETE |
| 可靠性 | TCP保证 | 消息层确认机制 |
| 状态 | 无状态 | 无状态 |
| 资源发现 | 无标准 | /.well-known/core |
| 观察模式 | WebSocket/Polling | 原生Observe支持 |
| 多播 | 不支持 | 支持 |
| 安全 | TLS | DTLS |
| 典型场景 | Web应用 | IoT设备通信 |

### 1.3 CoAP应用场景

```
典型应用场景:

1. 智能家居
   ┌─────────┐     CoAP      ┌─────────┐
   │  手机APP │ ←─────────→  │ 智能灯泡 │
   └─────────┘               └─────────┘
   - 设备控制（开/关/调光）
   - 状态查询
   - 事件订阅

2. 工业物联网
   ┌─────────┐     CoAP      ┌─────────┐
   │  网关    │ ←─────────→  │ 传感器   │
   └─────────┘               └─────────┘
   - 传感器数据上报
   - 设备远程配置
   - 告警推送

3. 智慧城市
   ┌──────────┐  CoAP多播  ┌──────────┐
   │ 路灯控制 │ ────────→  │ 多个路灯 │
   └──────────┘            └──────────┘
   - 一对多控制
   - 节能管理
   - 环境监测

4. 医疗IoT
   - 患者生命体征监测
   - 远程诊断设备
   - 药品追踪
```

---

## 2. CoAP协议架构

### 2.1 协议分层

```
┌─────────────────────────────────────────┐
│              应用层 (Application)         │
│   传感器数据 / 设备控制 / 状态查询       │
├─────────────────────────────────────────┤
│          CoAP 请求/响应层                 │
│   GET / POST / PUT / DELETE             │
│   请求-响应 / 通知 / 批量操作            │
├─────────────────────────────────────────┤
│          CoAP 消息层                     │
│   CON / NON / ACK / RST                │
│   消息ID / Token / 重传                 │
├─────────────────────────────────────────┤
│          UDP (传输层)                    │
│   端口: 5683 (明文) / 5684 (DTLS)       │
├─────────────────────────────────────────┤
│          IPv6/IPv4                      │
│   6LoWPAN适配 / 压缩                    │
├─────────────────────────────────────────┤
│          IEEE 802.15.4 / WiFi           │
│          物理层和MAC层                   │
└─────────────────────────────────────────┘
```

### 2.2 消息类型

CoAP定义了四种消息类型：

```
1. CON (Confirmable, 需确认)
   发送方 → 消息 → 接收方
   发送方 ← ACK ← 接收方
   
   特点: 可靠传输，需要接收方确认
   
2. NON (Non-confirmable, 无需确认)
   发送方 → 消息 → 接收方
   （无ACK）
   
   特点: 不可靠传输，适合频繁的传感器数据

3. ACK (Acknowledgement, 确认)
   接收方 → ACK → 发送方
   
   特点: 确认收到CON消息

4. RST (Reset, 重置)
   接收方 → RST → 发送方
   
   特点: 拒绝消息（如未识别的Message ID）
```

### 2.3 请求-响应模型

```
CoAP支持两种响应模式:

模式1: 请求-响应（携带在ACK中）
  Client                Server
    │─── GET /temp ──→│  (CON)
    │←── 2.05 23.5 ───│  (ACK + 响应)
    │                  │

模式2: 分离响应（ACK不携带数据）
  Client                Server
    │─── GET /temp ──→│  (CON)
    │←── (空ACK) ─────│  (ACK)
    │                  │  (处理中...)
    │←── 2.05 23.5 ───│  (CON, 单独响应)
    │─── (ACK) ──────→│  (ACK)

模式2适用于:
- 传感器需要时间采集数据
- 设备从休眠中唤醒
- 数据处理耗时较长
```

---

## 3. CoAP消息格式详解

### 3.1 消息结构

```
CoAP消息格式 (RFC 7252):

 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Ver| T |  TKL  |      Code     |          Message ID          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   Token (if any, TKL = 0-8 bytes)                           ...
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|   Options (if any)                                          ...
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|1 1 1 1 1 1 1 1|    Payload (if any)                         ...
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

字段说明:
- Ver (2 bits): 版本号，固定为01
- T (2 bits): 消息类型 (CON=00, NON=01, ACK=10, RST=11)
- TKL (4 bits): Token长度 (0-8)
- Code (8 bits): 响应码/方法码
- Message ID (16 bits): 消息标识符（用于去重和匹配）
- Token (0-8 bytes): 请求-响应匹配令牌
- Options: 选项字段
- Payload Marker: 0xFF（分隔选项和负载）
- Payload: 实际数据
```

### 3.2 CoAP方法码

```
方法码 (Code = 0b.cccc.dddd):

请求方法:
  0.01 = GET
  0.02 = POST
  0.03 = PUT
  0.04 = DELETE

响应码:
  2.xx = 成功
    2.01 = Created
    2.02 = Deleted
    2.03 = Valid
    2.04 = Changed
    2.05 = Content
  
  4.xx = 客户端错误
    4.00 = Bad Request
    4.01 = Unauthorized
    4.02 = Bad Option
    4.03 = Forbidden
    4.04 = Not Found
    4.05 = Method Not Allowed
  
  5.xx = 服务端错误
    5.00 = Internal Server Error
    5.01 = Not Implemented
    5.02 = Bad Gateway
    5.03 = Service Unavailable
```

### 3.3 CoAP选项

```python
# CoAP选项解析器
class CoAPOption:
    """CoAP选项定义"""
    
    # 选项编号
    IF_NONE_MATCH = 1
    URI_HOST = 3
    URI_PORT = 7
    URI_PATH = 11
    CONTENT_FORMAT = 12
    MAX_AGE = 14
    URI_QUERY = 15
    ACCEPT = 17
    TOKEN = 19
    BLOCK1 = 23
    BLOCK2 = 27
    SIZE1 = 28
    SIZE2 = 29
    PROXY_URI = 35
    PROXY_SCHEME = 39
    OBSERVE = 6
    
    # 内容格式
    TEXT_PLAIN = 0
    APP_LINK_FORMAT = 40
    APP_XML = 41
    APP_JSON = 50
    APP_CBOR = 60
    APP_EXI = 47
    
    # 选项属性
    OPTION_PROPERTIES = {
        IF_NONE_MATCH: {'critical': True, 'unsafe': False, 'length': 0},
        URI_HOST: {'critical': True, 'unsafe': True, 'length': '1-255'},
        URI_PORT: {'critical': True, 'unsafe': True, 'length': '0-2'},
        URI_PATH: {'critical': True, 'unsafe': True, 'length': '0-255'},
        CONTENT_FORMAT: {'critical': False, 'unsafe': False, 'length': '0-2'},
        MAX_AGE: {'critical': False, 'unsafe': False, 'length': '0-4'},
        URI_QUERY: {'critical': True, 'unsafe': True, 'length': '0-255'},
        ACCEPT: {'critical': True, 'unsafe': False, 'length': '0-2'},
        BLOCK1: {'critical': False, 'unsafe': True, 'length': '0-3'},
        BLOCK2: {'critical': False, 'unsafe': True, 'length': '0-3'},
        OBSERVE: {'critical': False, 'unsafe': False, 'length': '0-3'},
    }

def parse_coap_message(data: bytes) -> dict:
    """解析CoAP消息"""
    if len(data) < 4:
        return {'error': '消息过短'}
    
    # 解析头部
    ver = (data[0] >> 6) & 0x03
    msg_type = (data[0] >> 4) & 0x03
    tkl = data[0] & 0x0F
    code = data[1]
    msg_id = (data[2] << 8) | data[3]
    
    # 解析Token
    offset = 4
    token = data[offset:offset+tkl] if tkl > 0 else b''
    offset += tkl
    
    # 解析选项
    options = []
    prev_option = 0
    while offset < len(data):
        if data[offset] == 0xFF:
            # 负载标记
            offset += 1
            break
        
        # 解析选项delta和长度
        delta = (data[offset] >> 4) & 0x0F
        length = data[offset] & 0x0F
        offset += 1
        
        # 扩展delta
        if delta == 13:
            delta = 13 + data[offset]
            offset += 1
        elif delta == 14:
            delta = 269 + (data[offset] << 8 | data[offset+1])
            offset += 2
        elif delta == 15:
            return {'error': '无效的选项delta'}
        
        # 扩展长度
        if length == 13:
            length = 13 + data[offset]
            offset += 1
        elif length == 14:
            length = 269 + (data[offset] << 8 | data[offset+1])
            offset += 2
        elif length == 15:
            return {'error': '无效的选项长度'}
        
        # 计算实际选项号
        option_num = prev_option + delta
        prev_option = option_num
        
        # 读取选项值
        option_value = data[offset:offset+length]
        offset += length
        
        options.append({
            'number': option_num,
            'value': option_value
        })
    
    # 解析负载
    payload = data[offset:] if offset < len(data) else b''
    
    return {
        'version': ver,
        'type': msg_type,
        'tkl': tkl,
        'code': code,
        'message_id': msg_id,
        'token': token.hex(),
        'options': options,
        'payload': payload,
    }
```

### 3.4 资源发现

```
CoAP资源发现:
- 标准路径: /.well-known/core
- 返回格式: Application/Link-Format (CT=40)
- 包含设备上所有可用资源的描述

请求示例:
  GET coap://[2001:db8::1]/.well-known/core

响应示例:
  </sensors/temp>;ct=50;rt="temperature-c";if="sensor",
  </sensors/humidity>;ct=50;rt="humidity";if="sensor",
  </actuators/led>;ct=0;rt="led";if="actuator",
  </firmware>;ct=50;rt="firmware";if="info"

参数说明:
- ct: 内容格式 (Content-Format)
- rt: 资源类型 (Resource Type)
- if: 接口描述 (Interface Description)
```

---

## 4. CoAP安全机制DTLS

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

## 5. CoAP安全威胁分析

### 5.1 威胁概述

```
CoAP安全威胁分类:

┌─────────────────────────────────────────────┐
│               CoAP安全威胁模型                │
├─────────────────────────────────────────────┤
│                                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐     │
│  │ 网络层   │  │ 协议层   │  │ 应用层   │     │
│  │ 威胁     │  │ 威胁     │  │ 威胁     │     │
│  └────┬────┘  └────┬────┘  └────┬────┘     │
│       │            │            │            │
│  ┌────┴────┐  ┌────┴────┐  ┌────┴────┐     │
│  │IP欺骗   │  │重放攻击 │  │未授权访问│     │
│  │DDoS    │  │中间人   │  │注入攻击  │     │
│  │ARP欺骗  │  │消息伪造 │  │资源耗尽  │     │
│  │路由攻击 │  │会话劫持 │  │信息泄露  │     │
│  └─────────┘  └─────────┘  └─────────┘     │
└─────────────────────────────────────────────┘
```

### 5.2 具体威胁详解

#### 5.2.1 未认证访问

```
威胁: 未启用DTLS的CoAP服务器可被任意访问

攻击场景:
1. 攻击者扫描网络发现CoAP设备
2. 直接访问设备资源
3. 读取传感器数据或控制设备

示例:
# 扫描CoAP设备
coap-scan 2001:db8::/64 -p 5683

# 直接读取传感器数据
coap-client -m get coap://[2001:db8::1]/sensors/temp

# 控制设备
coap-client -m put -e "on" coap://[2001:db8::1]/actuators/led

风险:
- 敏感数据泄露（温度、湿度、位置等）
- 设备被恶意控制
- 拒绝服务
```

#### 5.2.2 重放攻击

```
威胁: 攻击者捕获并重放CoAP消息

攻击流程:
1. 攻击者嗅探网络流量
2. 捕获有效的CoAP请求/响应
3. 在之后重放该消息

示例场景:
  T1: 用户 → 设备: PUT /door {state: open} (MessageID: 100)
  T2: 攻击者捕获该消息
  T3: 用户 → 设备: PUT /door {state: close} (MessageID: 101)
  T4: 攻击者重放: PUT /door {state: open} (MessageID: 100)
  
  问题: 如果设备未做重放检测，门会被重新打开

防御:
- 使用DTLS (提供序号和MAC)
- 使用Token匹配请求响应
- 使用时间戳选项
- 限制Message ID窗口
```

#### 5.2.3 中间人攻击

```
威胁: 攻击者在客户端和服务器之间转发/修改消息

攻击流程:
  Client ←──→ Attacker ←──→ Server
                  │
            篡改/嗅探/注入

未使用DTLS时:
- 攻击者可读取所有明文数据
- 攻击者可修改消息内容
- 攻击者可注入伪造消息

使用PSK-DTLS但密钥泄露时:
- 攻击者可解密流量
- 攻击者可伪造消息

使用X.509-DTLS时:
- 攻击者无法解密或篡改
- 除非获得CA私钥或利用实现缺陷
```

#### 5.2.4 消息伪造与注入

```
威胁: 攻击者伪造CoAP消息发送给设备

攻击示例:
# 伪造传感器响应（欺骗客户端）
import socket

# 构造伪造的CoAP响应
# Type=ACK(2), Code=2.05(Content), MessageID=0x1234
fake_response = bytes([
    0x60,  # Ver=1, Type=ACK(2), TKL=0
    0x45,  # Code=2.05 (Content)
    0x12, 0x34,  # Message ID
    0xFF,  # Payload marker
]) + b'25.5'  # 伪造温度数据

# 发送给客户端
sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
sock.sendto(fake_response, ('2001:db8::client', 5683))

防御:
- 使用DTLS MAC验证消息完整性
- 使用Token匹配请求和响应
- 验证源IP和端口
```

#### 5.2.5 资源耗尽攻击

```
威胁: 利用CoAP协议特性耗尽设备资源

攻击方式1: DTLS握手耗尽
  - 发送大量ClientHello但不完成握手
  - 迫使设备分配握手状态
  - HelloVerifyRequest可缓解但不能完全防止

攻击方式2: 分块传输耗尽
  - 发送大量Block-wise传输请求
  - 占用设备内存和存储

攻击方式3: Observe注册耗尽
  - 注册大量观察者
  - 迫使设备维护大量观察状态

攻击方式4: CoAP放大攻击
  - 利用多播CoAP获取大量响应
  - 通过CoAP反射进行DDoS
```

---

## 6. CoAP攻击技术与案例

### 6.1 CoAP放大攻击

```python
# CoAP放大攻击原理演示
class CoAPAmplificationDemo:
    """CoAP放大攻击分析"""
    
    """
    CoAP支持多播，攻击者可以利用这一点:
    1. 发送CoAP多播请求
    2. 多个设备同时响应
    3. 利用响应流量攻击目标
    
    放大倍数:
    - 请求大小: ~30-60字节
    - 响应大小: ~100-1500字节
    - 放大倍数: 3-50x
    """
    
    def analyze_amplification(self):
        """分析放大效果"""
        # 典型的CoAP多播场景
        multicast_address = 'ff02::fd'  # CoAP多播地址
        
        # 小型请求
        coap_request = self._build_coap_request(
            method='GET',
            uri='/.well-known/core'
        )
        request_size = len(coap_request)
        
        # 多播后每个设备的响应
        response_sizes = []
        
        # 模拟100个设备响应
        for i in range(100):
            response = self._build_coap_response(
                payload=f'< /sensor{i} >;rt="temperature"'
            )
            response_sizes.append(len(response))
        
        total_response = sum(response_sizes)
        amplification = total_response / request_size
        
        print(f"请求大小: {request_size} bytes")
        print(f"响应总数: {total_response} bytes")
        print(f"放大倍数: {amplification:.1f}x")
        
    def _build_coap_request(self, method, uri):
        """构造CoAP请求"""
        # NON类型，避免ACK
        header = bytes([0x50])  # Ver=1, Type=NON(1), TKL=0
        # 方法码
        code_map = {'GET': 0x01, 'POST': 0x02, 'PUT': 0x03, 'DELETE': 0x04}
        code = code_map.get(method, 0x01)
        # 随机Message ID
        msg_id = bytes([0xAA, 0xBB])
        # URI路径选项
        options = b''
        for part in uri.strip('/').split('/'):
            options += bytes([0xBB, len(part)]) + part.encode()
        # 无负载
        return header + bytes([code]) + msg_id + options
    
    def _build_coap_response(self, payload):
        """构造CoAP响应"""
        header = bytes([0x50])  # Ver=1, Type=NON, TKL=0
        code = 0x45  # 2.05 Content
        msg_id = bytes([0xCC, 0xDD])
        marker = bytes([0xFF])
        return header + bytes([code]) + msg_id + marker + payload.encode()
```

### 6.2 CoAP中间人攻击实战

```python
# CoAP中间人攻击分析
class CoAPMITM:
    """CoAP中间人攻击工具"""
    
    def __init__(self, interface='wlan0'):
        self.interface = interface
        self.running = False
        self.captured = {}
        
    def start_mitm(self, client_ip: str, server_ip: str, port: int = 5683):
        """启动中间人攻击"""
        self.running = True
        
        # 在无DTLS的环境中
        # 1. 捕获客户端请求
        # 2. 修改请求内容
        # 3. 转发给服务器
        # 4. 捕获服务器响应
        # 5. 修改响应内容
        # 6. 转发给客户端
        
        try:
            from scapy.all import sniff, UDP, IPv6, Raw
            from scapy.layers.inet6 import UDP
            
            def packet_handler(pkt):
                if UDP in pkt:
                    if pkt[UDP].dport == port:
                        self._process_request(pkt)
                    elif pkt[UDP].sport == port:
                        self._process_response(pkt)
            
            logger.info(f"开始MITM: {client_ip} <-> {server_ip}")
            sniff(iface=self.interface, prn=packet_handler,
                  filter=f"udp port {port}", store=False)
                  
        except ImportError:
            logger.error("需要安装scapy")
    
    def _process_request(self, pkt):
        """处理客户端请求"""
        payload = bytes(pkt[UDP].payload)
        coap_msg = parse_coap_message(payload)
        
        logger.info(f"请求: {coap_msg}")
        
        # 示例: 篡改PUT请求的数据
        if coap_msg.get('code') == 0x03:  # PUT
            modified = self._modify_payload(payload, b'hacked')
            # 重新计算校验和并发送
            self._forward(modified, pkt[IPv6].dst, pkt[UDP].dport)
    
    def _process_response(self, pkt):
        """处理服务器响应"""
        payload = bytes(pkt[UDP].payload)
        coap_msg = parse_coap_message(payload)
        
        logger.info(f"响应: {coap_msg}")
        
        # 示例: 篡改传感器数据
        if coap_msg.get('code') == 0x45:  # 2.05 Content
            modified = self._modify_payload(payload, b'99.9')
            self._forward(modified, pkt[IPv6].dst, pkt[UDP].dport)
```

### 6.3 CoAP设备指纹识别

```python
# CoAP设备指纹识别工具
class CoAPFingerprint:
    """通过CoAP协议特征识别IoT设备类型"""
    
    FINGERPRINT_DB = {
        'contiki': {
            'port': 5683,
            'well_known': '/.well-known/core',
            'features': ['observe', 'block-wise'],
            'msg_id_seq': 'sequential',
        },
        'libcoap': {
            'port': 5683,
            'well_known': '/.well-known/core',
            'features': ['observe', 'block-wise', ' multicast'],
            'msg_id_seq': 'random',
        },
        'californium': {
            'port': 5683,
            'well_known': '/.well-known/core',
            'features': ['observe', 'block-wise', 'dtls'],
            'msg_id_seq': 'random',
        },
        'coapthon': {
            'port': 5683,
            'well_known': '/.well-known/core',
            'features': ['observe', 'block-wise'],
            'msg_id_seq': 'sequential',
        },
    }
    
    def fingerprint(self, ip: str, port: int = 5683) -> dict:
        """对CoAP设备进行指纹识别"""
        result = {
            'ip': ip,
            'port': port,
            'reachable': False,
            'resources': [],
            'dtls': False,
            'device_type': 'unknown',
            'implementation': 'unknown',
        }
        
        # 1. 探测CoAP服务
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            sock.settimeout(3)
            
            # 发送资源发现请求
            request = self._build_request('GET', '/.well-known/core')
            sock.sendto(request, (ip, port))
            
            response, addr = sock.recvfrom(2048)
            result['reachable'] = True
            
            # 解析资源列表
            coap_msg = parse_coap_message(response)
            if coap_msg.get('code') == 0x45:  # 2.05
                payload = coap_msg['payload'].decode('utf-8', errors='ignore')
                result['resources'] = self._parse_well_known(payload)
            
            # 2. 测试DTLS支持
            result['dtls'] = self._test_dtls(ip, port + 1)
            
            # 3. 测试Observe支持
            result['observe'] = self._test_observe(ip, port)
            
            # 4. 测试Block-wise传输
            result['block_wise'] = self._test_block_wise(ip, port)
            
            # 5. 分析Message ID序列
            result['msg_id_seq'] = self._analyze_msg_id_seq(ip, port)
            
            # 6. 匹配实现
            result['implementation'] = self._match_implementation(result)
            
        except socket.timeout:
            result['reachable'] = False
        except Exception as e:
            result['error'] = str(e)
        
        return result
```

---

## 7. CoAP安全加固方案

### 7.1 认证与授权

```python
# CoAP安全配置示例
class CoAPSecurityConfig:
    """CoAP安全配置管理"""
    
    # 安全级别
    SECURITY_LEVELS = {
        'NONE': 0,      # 无加密无认证
        'PRE_SHARED': 1, # 预共享密钥
        'RAW_PUBLIC': 2, # 原始公钥
        'CERTIFICATE': 3, # X.509证书
    }
    
    # 推荐配置（按设备能力分级）
    RECOMMENDED = {
        'tier0': {  # 最受限设备 (<100KB RAM)
            'security': 'PRE_SHARED',
            'cipher': 'TLS_PSK_WITH_AES_128_CCM_8',
            'key_length': 16,  # 128-bit
            'rekey_interval': 86400,  # 24小时
        },
        'tier1': {  # 受限设备 (<256KB RAM)
            'security': 'RAW_PUBLIC',
            'cipher': 'TLS_ECDHE_ECDSA_WITH_AES_128_CCM_8',
            'curve': 'secp256r1',
            'key_length': 32,
        },
        'tier2': {  # 中等设备 (>256KB RAM)
            'security': 'CERTIFICATE',
            'cipher': 'TLS_ECDHE_ECDSA_WITH_AES_128_CCM_8',
            'cert_type': 'X.509',
            'cert_profile': 'IEEE 802.1AR (DevID)',
        },
    }
    
    @staticmethod
    def generate_psk(length: int = 16) -> bytes:
        """生成预共享密钥"""
        import os
        return os.urandom(length)
    
    @staticmethod
    def generate_ec_keypair(curve: str = 'secp256r1'):
        """生成EC密钥对"""
        from cryptography.hazmat.primitives.asymmetric import ec
        private_key = ec.generate_private_key(
            ec.SECP256R1() if curve == 'secp256r1' else ec.SECP384R1()
        )
        public_key = private_key.public_key()
        return private_key, public_key
```

### 7.2 访问控制

```python
# CoAP访问控制列表
class CoAPACL:
    """CoAP资源访问控制"""
    
    def __init__(self):
        self.acl = {}
        # 默认拒绝所有访问
        self.default_policy = 'DENY'
    
    def add_rule(self, resource: str, method: str, 
                 subject: str, action: str = 'ALLOW'):
        """添加访问控制规则"""
        if resource not in self.acl:
            self.acl[resource] = []
        
        self.acl[resource].append({
            'method': method,
            'subject': subject,  # 客户端ID/IP/证书CN
            'action': action,
        })
    
    def check(self, resource: str, method: str, 
              subject: str) -> bool:
        """检查访问权限"""
        rules = self.acl.get(resource, [])
        
        # 先检查显式规则
        for rule in rules:
            if rule['method'] == method or rule['method'] == '*':
                if rule['subject'] == subject or rule['subject'] == '*':
                    return rule['action'] == 'ALLOW'
        
        # 返回默认策略
        return self.default_policy == 'ALLOW'
    
    def load_config(self, config: dict):
        """从配置加载ACL"""
        for resource, rules in config.items():
            for rule in rules:
                self.add_rule(
                    resource, rule['method'],
                    rule['subject'], rule.get('action', 'ALLOW')
                )

# 示例配置
ACL_CONFIG = {
    '/.well-known/core': [
        {'method': 'GET', 'subject': '*', 'action': 'ALLOW'},
    ],
    '/sensors/*': [
        {'method': 'GET', 'subject': 'gateway', 'action': 'ALLOW'},
        {'method': 'GET', 'subject': 'admin', 'action': 'ALLOW'},
    ],
    '/actuators/*': [
        {'method': 'PUT', 'subject': 'admin', 'action': 'ALLOW'},
        {'method': 'POST', 'subject': 'admin', 'action': 'ALLOW'},
        {'method': '*', 'subject': '*', 'action': 'DENY'},
    ],
    '/firmware': [
        {'method': 'GET', 'subject': 'admin', 'action': 'ALLOW'},
        {'method': 'POST', 'subject': 'admin', 'action': 'ALLOW'},
    ],
}
```

### 7.3 防重放攻击

```python
# CoAP防重放机制
class CoAPReplayProtection:
    """CoAP消息重放防护"""
    
    def __init__(self, window_size: int = 64):
        self.window_size = window_size
        self.received_msg_ids = {}  # 按来源记录
        self.max_msg_id = {}  # 每个来源的最大Message ID
    
    def check_replay(self, source: str, msg_id: int) -> bool:
        """检查是否为重放消息"""
        if source not in self.received_msg_ids:
            self.received_msg_ids[source] = set()
            self.max_msg_id[source] = 0
        
        # 新消息
        if msg_id > self.max_msg_id[source]:
            # 滑动窗口
            self._slide_window(source, msg_id)
            self.received_msg_ids[source].add(msg_id)
            self.max_msg_id[source] = msg_id
            return True  # 非重放
        
        # 在窗口内
        if msg_id in self.received_msg_ids[source]:
            return False  # 重放
        
        # 在窗口内但未见过
        self.received_msg_ids[source].add(msg_id)
        return True  # 非重放
    
    def _slide_window(self, source: str, new_max: int):
        """滑动窗口"""
        min_allowed = new_max - self.window_size
        self.received_msg_ids[source] = {
            mid for mid in self.received_msg_ids[source]
            if mid > min_allowed
        }
```

---

## 8. OSCORE：CoAP对象安全

### 8.1 OSCORE概述

OSCORE（Object Security for CoRE, RFC 8613）是CoAP的端到端安全方案，解决了DTLS的局限性：

```
DTLS vs OSCORE:

DTLS (Hop-by-Hop):
  Client ←──DTLS──→ Proxy ←──DTLS──→ Server
  
  问题: 代理需要解密流量
  - 代理成为信任节点
  - 端到端隐私无法保证
  - 代理被攻破则全暴露

OSCORE (End-to-End):
  Client ←═══════→ Proxy ←═══════→ Server
           (端到端加密)
  
  优势:
  - 代理只转发加密数据
  - 真正的端到端安全
  - 代理无需信任
  - 支持多播安全
```

### 8.2 OSCORE工作原理

```python
# OSCORE安全保护流程
class OSCORE:
    """OSCORE对象安全实现"""
    
    def __init__(self, master_secret: bytes, sender_id: bytes, 
                 recipient_id: bytes):
        self.master_secret = master_secret
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.sender_seq = 0
        
        # 派生密钥
        self.aead_key = self._derive_key(
            master_secret, sender_id, 'aead_key'
        )
        self.iv = self._derive_key(
            master_secret, sender_id, 'iv'
        )
    
    def protect(self, coap_message: bytes) -> bytes:
        """OSCORE保护CoAP消息"""
        # 1. 分离外部选项和内部内容
        external_options, inner = self._split_message(coap_message)
        
        # 2. 构造AAD (Additional Authenticated Data)
        aad = self._build_aad(
            external_options, 
            self.sender_id, 
            self.sender_seq
        )
        
        # 3. 加密内部内容
        nonce = self._build_nonce(self.iv, self.sender_seq)
        ciphertext = aes_ccm_encrypt(
            self.aead_key, nonce, aad, inner
        )
        
        # 4. 构造OSCORE选项
        oscore_option = self._build_oscore_option(
            self.sender_id, self.sender_seq, 
            ciphertext[:8]  # 8字节MAC标签
        )
        
        # 5. 组装保护后的消息
        protected = self._assemble(
            external_options, oscore_option, ciphertext
        )
        
        self.sender_seq += 1
        return protected
    
    def unprotect(self, protected_message: bytes) -> bytes:
        """OSCORE去除保护"""
        # 1. 提取OSCORE选项
        oscore_opt = self._extract_oscore_option(protected_message)
        
        # 2. 解析发送方ID和序号
        sender_id, seq, mac = self._parse_oscore_option(oscore_opt)
        
        # 3. 重建AAD
        external_options = self._get_external_options(protected_message)
        aad = self._build_aad(external_options, sender_id, seq)
        
        # 4. 构建nonce
        nonce = self._build_nonce(self.iv, seq)
        
        # 5. 解密
        plaintext = aes_ccm_decrypt(
            self.aead_key, nonce, aad, 
            oscore_opt['ciphertext']
        )
        
        # 6. 验证MAC
        if not self._verify_mac(mac, plaintext, aad):
            raise ValueError("MAC验证失败")
        
        # 7. 重组CoAP消息
        return self._reassemble(
            external_options, plaintext
        )
    
    def _derive_key(self, secret: bytes, id: bytes, 
                    info: str) -> bytes:
        """HKDF密钥派生"""
        import hashlib
        from hmac import HMAC
        
        salt = b''
        info_bytes = info.encode()
        
        # HKDF-Extract
        prk = HMAC(salt, secret, hashlib.sha256).digest()
        
        # HKDF-Expand
        okm = HMAC(prk, info_bytes, hashlib.sha256).digest()
        
        return okm[:16]  # 128-bit key
```

---

## 9. CoAP安全测试工具与实践

### 9.1 CoAP测试工具集

```python
#!/usr/bin/env python3
"""
CoAP安全测试工具集
==================

功能:
1. CoAP设备发现与枚举
2. 未认证访问检测
3. DTLS配置检查
4. 重放攻击测试
5. 资源访问控制测试
6. CoAP放大攻击验证
"""

import socket
import struct
import argparse
import logging
import time
import json
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger('CoAPTester')

class CoAPTester:
    """CoAP安全测试工具"""
    
    PORT = 5683
    PORT_DTLS = 5684
    
    def __init__(self, target: str, port: int = PORT):
        self.target = target
        self.port = port
        self.results = {}
        
    def run_all_tests(self):
        """运行所有安全测试"""
        logger.info(f"开始CoAP安全测试: {self.target}:{self.port}")
        
        tests = [
            ('discovery', self.test_resource_discovery),
            ('unauth_access', self.test_unauthenticated_access),
            ('dtls', self.test_dtls_support),
            ('replay', self.test_replay_protection),
            ('amplification', self.test_amplification),
            ('observe', self.test_observe_security),
            ('block_wise', self.test_block_wise_security),
        ]
        
        for name, test_func in tests:
            logger.info(f"执行测试: {name}")
            try:
                result = test_func()
                self.results[name] = result
            except Exception as e:
                logger.error(f"测试 {name} 失败: {e}")
                self.results[name] = {'error': str(e)}
        
        self._generate_report()
    
    def test_resource_discovery(self) -> dict:
        """测试资源发现"""
        result = {'reachable': False, 'resources': [], 'info_leak': False}
        
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            sock.settimeout(5)
            
            # 发送资源发现请求
            request = self._build_coap_get('/.well-known/core')
            sock.sendto(request, (self.target, self.port))
            
            response, _ = sock.recvfrom(4096)
            result['reachable'] = True
            
            # 解析资源列表
            coap_resp = parse_coap_message(response)
            if coap_resp.get('code') == 0x45:
                payload = coap_resp['payload'].decode('utf-8', errors='ignore')
                resources = self._parse_link_format(payload)
                result['resources'] = resources
                
                # 检查信息泄露
                sensitive_patterns = ['firmware', 'config', 'password', 
                                      'admin', 'debug', 'shell']
                for res in resources:
                    for pattern in sensitive_patterns:
                        if pattern in res.lower():
                            result['info_leak'] = True
                            break
                
                sock.close()
        except socket.timeout:
            result['error'] = '超时'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def test_unauthenticated_access(self) -> dict:
        """测试未认证访问"""
        result = {'vulnerable': False, 'accessible_resources': []}
        
        # 尝试直接访问各种资源
        test_resources = [
            '/sensors/temp',
            '/sensors/humidity',
            '/actuators/led',
            '/firmware',
            '/config',
            '/admin',
        ]
        
        for resource in test_resources:
            try:
                sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
                sock.settimeout(3)
                
                request = self._build_coap_get(resource)
                sock.sendto(request, (self.target, self.port))
                
                response, _ = sock.recvfrom(4096)
                coap_resp = parse_coap_message(response)
                
                if coap_resp.get('code') and coap_resp['code'] < 0x80:
                    # 2.xx 成功响应
                    result['vulnerable'] = True
                    result['accessible_resources'].append({
                        'resource': resource,
                        'code': hex(coap_resp['code']),
                        'data': coap_resp.get('payload', b'').decode(
                            'utf-8', errors='ignore'
                        )[:100]
                    })
                
                sock.close()
            except socket.timeout:
                pass
            except Exception:
                pass
        
        return result
    
    def test_dtls_support(self) -> dict:
        """测试DTLS支持"""
        result = {'dtls_supported': False, 'port_open': False}
        
        try:
            # 测试DTLS端口(5684)
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            sock.settimeout(3)
            
            # 发送DTLS ClientHello
            client_hello = self._build_dtls_hello()
            sock.sendto(client_hello, (self.target, self.PORT_DTLS))
            
            response, _ = sock.recvfrom(4096)
            if response:
                result['port_open'] = True
                # 检查是否为HelloVerifyRequest
                if len(response) > 3 and response[0] == 0x16:
                    result['dtls_supported'] = True
            
            sock.close()
        except socket.timeout:
            result['error'] = 'DTLS端口未开放'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def test_replay_protection(self) -> dict:
        """测试重放保护"""
        result = {'vulnerable': False, 'details': ''}
        
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            sock.settimeout(5)
            
            # 发送第一个请求
            request1 = self._build_coap_get('/sensors/temp')
            sock.sendto(request1, (self.target, self.port))
            response1, _ = sock.recvfrom(4096)
            
            # 重放第一个请求（相同Message ID）
            time.sleep(1)
            sock.sendto(request1, (self.target, self.port))
            
            try:
                response2, _ = sock.recvfrom(4096)
                # 如果收到了相同的响应，说明没有重放保护
                if response1 == response2:
                    result['vulnerable'] = True
                    result['details'] = '设备未实现重放保护'
            except socket.timeout:
                result['details'] = '设备可能实现了重放保护'
            
            sock.close()
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def test_amplification(self) -> dict:
        """测试放大攻击可能性"""
        result = {
            'multicast_amplification': False,
            'request_size': 0,
            'response_size': 0,
        }
        
        # 构造最小请求
        request = self._build_coap_get('/.well-known/core')
        result['request_size'] = len(request)
        
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            sock.settimeout(3)
            
            sock.sendto(request, (self.target, self.port))
            response, _ = sock.recvfrom(4096)
            result['response_size'] = len(response)
            
            if result['response_size'] > result['request_size'] * 3:
                result['multicast_amplification'] = True
            
            sock.close()
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _build_coap_get(self, uri: str) -> bytes:
        """构造CoAP GET请求"""
        header = bytes([0x40])  # Ver=1, Type=CON(0), TKL=0
        code = bytes([0x01])  # GET
        msg_id = struct.pack('>H', 0x0001)
        
        # URI路径选项
        options = b''
        if uri.startswith('/.well-known/core'):
            # 特殊处理
            options = bytes([0x11, 0x02]) + b'/.well-known/core'
        else:
            parts = uri.strip('/').split('/')
            delta = 11  # Uri-Path选项号
            for part in parts:
                part_bytes = part.encode()
                d = delta if delta < 13 else 13
                l = len(part_bytes)
                options += bytes([(d << 4) | (l if l < 13 else 13)]) + part_bytes
                delta = 0  # 后续选项delta为0
        
        return header + code + msg_id + options
    
    def _build_dtls_hello(self) -> bytes:
        """构造DTLS ClientHello"""
        # 简化的DTLS 1.2 ClientHello
        return bytes([
            0x16,  # ContentType: Handshake
            0xFE, 0xFD,  # Version: DTLS 1.2
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00,  # Epoch + Seq
            0x00, 0x00,  # Length (placeholder)
            0x01,  # HandshakeType: ClientHello
            0x00, 0x00, 0x00,  # Length (placeholder)
            0x00,  # MessageSeq
            0x00, 0x00, 0x00,  # FragmentOffset
            0x00, 0x00, 0x00,  # FragmentLength
            0xFE, 0xFD,  # ClientVersion
        ])
    
    def _parse_link_format(self, payload: str) -> list:
        """解析CoRE Link-Format"""
        resources = []
        for item in payload.split(','):
            item = item.strip()
            if item.startswith('<') and '>' in item:
                path = item[item.index('<')+1:item.index('>')]
                resources.append(path)
        return resources
    
    def test_observe_security(self) -> dict:
        """测试Observe注册安全"""
        result = {'unrestricted_observe': False}
        
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            sock.settimeout(3)
            
            # 构造Observe注册请求
            request = self._build_coap_get('/sensors/temp')
            # 添加Observe选项 (注册=0)
            observe_option = bytes([0x60, 0x01, 0x00])  # delta=6, len=1, value=0
            
            full_request = request[:4] + observe_option + request[4:]
            sock.sendto(full_request, (self.target, self.port))
            
            response, _ = sock.recvfrom(4096)
            coap_resp = parse_coap_message(response)
            
            if coap_resp.get('code') == 0x45:
                result['unrestricted_observe'] = True
                result['details'] = '允许任意客户端注册观察'
            
            sock.close()
        except Exception:
            pass
        
        return result
    
    def test_block_wise_security(self) -> dict:
        """测试Block-wise传输安全"""
        result = {'unrestricted_block': False}
        
        try:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            sock.settimeout(3)
            
            # 构造大块传输请求
            request = self._build_coap_get('/firmware')
            # Block2选项: 请求大块数据
            block_option = bytes([0xD0, 0x01, 0x06])  # delta=27, num=0, m=1, szx=6(1024B)
            
            full_request = request[:4] + block_option + request[4:]
            sock.sendto(full_request, (self.target, self.port))
            
            response, _ = sock.recvfrom(4096)
            coap_resp = parse_coap_message(response)
            
            if coap_resp.get('code') == 0x45:
                payload_size = len(coap_resp.get('payload', b''))
                result['payload_size'] = payload_size
                if payload_size > 512:
                    result['unrestricted_block'] = True
                    result['details'] = f'允许传输大块数据: {payload_size}B'
            
            sock.close()
        except Exception:
            pass
        
        return result
    
    def _generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("CoAP安全测试报告")
        print("="*60)
        
        for test_name, result in self.results.items():
            print(f"\n[{test_name}]")
            if 'error' in result:
                print(f"  状态: 错误 - {result['error']}")
            else:
                for key, value in result.items():
                    if isinstance(value, list):
                        print(f"  {key}:")
                        for item in value:
                            print(f"    - {item}")
                    else:
                        print(f"  {key}: {value}")
        
        print("\n" + "="*60)

def main():
    parser = argparse.ArgumentParser(
        description='CoAP安全测试工具'
    )
    parser.add_argument('target', help='目标IPv6地址')
    parser.add_argument('-p', '--port', type=int, default=5683,
                        help='CoAP端口 (默认5683)')
    args = parser.parse_args()
    
    tester = CoAPTester(args.target, args.port)
    tester.run_all_tests()

if __name__ == '__main__':
    main()
```

---

## 10. 与其他IoT协议安全对比

### 10.1 协议安全对比表

| 安全特性 | CoAP | MQTT | HTTP | AMQP |
|---------|------|------|------|------|
| 传输层 | UDP | TCP | TCP | TCP |
| 加密 | DTLS | TLS | TLS | TLS |
| 认证 | DTLS/OSCORE | TLS/用户名密码 | TLS/Basic/Digest | TLS/SASL |
| 消息完整性 | DTLS MAC | TLS MAC | TLS MAC | TLS MAC |
| 防重放 | DTLS序号 | TLS序号 | TLS序号 | TLS序号 |
| 端到端安全 | OSCORE | 无(需应用层) | 无(需应用层) | 无 |
| 多播安全 | OSCORE | 不支持 | 不支持 | 不支持 |
| 轻量级 | 是(最小) | 中等 | 否 | 否 |
| 资源发现 | /.well-known/core | 无标准 | /.well-known | 无标准 |

### 10.2 安全建议总结

```
CoAP安全最佳实践:

1. 始终使用DTLS
   - 最低: PSK-DTLS (适用于受限设备)
   - 推荐: RPK-DTLS (适用于中等设备)
   - 最佳: X.509-DTLS (适用于有PKI的环境)

2. 启用OSCORE
   - 在有代理的环境中
   - 需要端到端加密时
   - 多播通信场景

3. 实现访问控制
   - 基于资源的ACL
   - 最小权限原则
   - 敏感资源单独保护

4. 防重放保护
   - 利用DTLS序号
   - CoAP层Message ID窗口
   - Token随机化

5. 资源发现保护
   - 限制/.well-known/core的访问
   - 不暴露敏感资源路径
   - 使用过滤的资源列表

6. 防DoS措施
   - DTLS HelloVerifyRequest
   - 连接速率限制
   - 资源配额管理

7. 固件更新安全
   - 使用CoAP块传输
   - 固件签名验证
   - 版本回滚保护
```

---

## 总结

CoAP作为IoT领域的核心应用层协议，其安全性直接关系到数以亿计IoT设备的安全。通过DTLS提供传输层安全、OSCORE提供端到端安全、以及合理的访问控制和防重放机制，可以构建相对完善的CoAP安全防护体系。

然而，CoAP的安全仍然面临挑战：资源受限设备的加密计算开销、UDP协议的DoS防护难度、以及大规模部署时的密钥管理问题。安全从业者需要结合实际场景，在安全性和资源消耗之间找到平衡点。

建议结合本文中的代码示例和测试工具，在实际IoT环境中进行安全评估和加固实践，深入理解CoAP协议的安全机制和攻击面。
