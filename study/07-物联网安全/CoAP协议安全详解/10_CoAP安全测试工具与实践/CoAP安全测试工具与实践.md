# CoAP安全测试工具与实践

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

---

## 📋 内容审核与补充建议

> 针对「CoAP安全测试工具与实践」部分的内容审核结果：

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
