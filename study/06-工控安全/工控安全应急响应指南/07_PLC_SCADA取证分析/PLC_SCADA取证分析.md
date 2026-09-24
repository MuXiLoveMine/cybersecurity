# PLC/SCADA取证分析

### 7.1 PLC程序差异分析

```python
#!/usr/bin/env python3
"""PLC程序差异分析工具 - 比较当前程序与备份"""
import hashlib
import struct
from datetime import datetime

class PLCProgramComparator:
    """PLC程序比较器"""
    
    def __init__(self):
        self.differences = []
    
    def compare_blocks(self, backup_blocks, current_blocks):
        """比较程序块
        
        参数:
            backup_blocks: 备份中的块列表
            current_blocks: 当前PLC中的块列表
        """
        backup_names = set(b['name'] for b in backup_blocks)
        current_names = set(b['name'] for b in current_blocks)
        
        # 1. 检查被删除的块
        deleted = backup_names - current_names
        if deleted:
            self._add_diff('deleted', list(deleted), 
                          '以下块在当前PLC中不存在')
        
        # 2. 检查新增的块
        added = current_names - backup_names
        if added:
            self._add_diff('added', list(added),
                          '以下块是新增的 (可能是注入的恶意代码)')
        
        # 3. 检查被修改的块
        common = backup_names & current_names
        modified = []
        
        for name in common:
            backup_block = next(b for b in backup_blocks if b['name'] == name)
            current_block = next(b for b in current_blocks if b['name'] == name)
            
            if backup_block['hash'] != current_block['hash']:
                modified.append({
                    'name': name,
                    'backup_hash': backup_block['hash'],
                    'current_hash': current_block['hash'],
                    'backup_size': backup_block['size'],
                    'current_size': current_block['size'],
                })
        
        if modified:
            self._add_diff('modified', modified,
                          '以下块内容已修改')
        
        return self.differences
    
    def _add_diff(self, diff_type, items, description):
        """添加差异"""
        self.differences.append({
            'type': diff_type,
            'description': description,
            'items': items,
            'timestamp': datetime.now().isoformat(),
        })
    
    def analyze_code_changes(self, backup_code, current_code):
        """分析代码变化细节"""
        changes = {
            'new_networks': [],
            'deleted_networks': [],
            'modified_networks': [],
            'new_variables': [],
            'deleted_variables': [],
        }
        
        # 分析变量变化
        backup_vars = set(backup_code.get('variables', {}).keys())
        current_vars = set(current_code.get('variables', {}).keys())
        
        changes['new_variables'] = list(current_vars - backup_vars)
        changes['deleted_variables'] = list(backup_vars - current_vars)
        
        # 分析网络变化
        backup_networks = backup_code.get('networks', [])
        current_networks = current_code.get('networks', [])
        
        max_len = max(len(backup_networks), len(current_networks))
        for i in range(max_len):
            b_net = backup_networks[i] if i < len(backup_networks) else None
            c_net = current_networks[i] if i < len(current_networks) else None
            
            if b_net is None:
                changes['new_networks'].append({
                    'index': i,
                    'content': c_net,
                })
            elif c_net is None:
                changes['deleted_networks'].append({
                    'index': i,
                    'content': b_net,
                })
            elif b_net != c_net:
                changes['modified_networks'].append({
                    'index': i,
                    'backup': b_net,
                    'current': c_net,
                })
        
        return changes
    
    def generate_report(self):
        """生成差异报告"""
        print("=" * 60)
        print("PLC程序差异分析报告")
        print("=" * 60)
        
        if not self.differences:
            print("未发现差异")
            return
        
        for diff in self.differences:
            print(f"\n[{diff['type'].upper()}] {diff['description']}")
            for item in diff['items']:
                if isinstance(item, dict):
                    print(f"  {item}")
                else:
                    print(f"  - {item}")
        
        print("\n" + "=" * 60)
        print("安全建议:")
        
        for diff in self.differences:
            if diff['type'] == 'added':
                print("  [!] 检查新增的块是否为恶意注入")
            elif diff['type'] == 'modified':
                print("  [!] 仔细审查被修改的块")
            elif diff['type'] == 'deleted':
                print("  [!] 确认被删除的块是否影响安全功能")
        
        print("=" * 60)

# 使用示例
if __name__ == '__main__':
    # 模备份数据
    backup_blocks = [
        {'name': 'OB1', 'hash': 'abc123', 'size': 1024},
        {'name': 'OB35', 'hash': 'def456', 'size': 512},
        {'name': 'FB1', 'hash': 'ghi789', 'size': 2048},
        {'name': 'DB1', 'hash': 'jkl012', 'size': 4096},
    ]
    
    current_blocks = [
        {'name': 'OB1', 'hash': 'abc123', 'size': 1024},  # 未变
        {'name': 'OB35', 'hash': 'xyz999', 'size': 600},  # 已修改
        {'name': 'FB1', 'hash': 'ghi789', 'size': 2048},  # 未变
        {'name': 'FB99', 'hash': 'malware', 'size': 666}, # 新增(恶意)
        # DB1 被删除
    ]
    
    comparator = PLCProgramComparator()
    comparator.compare_blocks(backup_blocks, current_blocks)
    comparator.generate_report()
```

### 7.2 网络流量取证分析

```python
#!/usr/bin/env python3
"""工控网络流量取证分析工具"""
import struct
from collections import defaultdict, Counter
from datetime import datetime

class ICSNetworkForensics:
    """ICS网络流量取证分析"""
    
    def __init__(self):
        self.sessions = defaultdict(list)
        self.anomalies = []
    
    def analyze_pcap(self, pcap_file):
        """分析pcap文件"""
        try:
            from scapy.all import rdpcap, TCP, IP
            packets = rdpcap(pcap_file)
            
            print(f"[*] 加载 {len(packets)} 个数据包")
            
            for pkt in packets:
                if IP in pkt and TCP in pkt:
                    self._process_tcp_packet(pkt)
            
            self._generate_analysis_report()
            
        except ImportError:
            print("[-] 需要安装scapy: pip install scapy")
    
    def _process_tcp_packet(self, pkt):
        """处理TCP包"""
        src_ip = pkt[IP].src
        dst_ip = pkt[IP].dst
        src_port = pkt[TCP].sport
        dst_port = pkt[TCP].dport
        payload = bytes(pkt[TCP].payload)
        
        # 检测工控协议
        if dst_port == 102 and len(payload) > 0:
            self._analyze_s7_traffic(src_ip, dst_ip, payload)
        elif dst_port == 502 and len(payload) > 0:
            self._analyze_modbus_traffic(src_ip, dst_ip, payload)
        elif dst_port == 20000 and len(payload) > 0:
            self._analyze_dnp3_traffic(src_ip, dst_ip, payload)
        
        # 记录会话
        session_key = f"{src_ip}:{src_port} -> {dst_ip}:{dst_port}"
        self.sessions[session_key].append({
            'timestamp': float(pkt.time),
            'payload': payload,
            'payload_len': len(payload),
        })
    
    def _analyze_s7_traffic(self, src_ip, dst_ip, payload):
        """分析S7协议流量"""
        if len(payload) < 8:
            return
        
        # 检查是否为S7协议
        if payload[0] != 0x03:  # TPKT版本
            return
        
        if len(payload) > 7 and payload[7] == 0x32:  # S7协议ID
            if len(payload) > 16:
                func_group = payload[16]
                
                # 检测危险操作
                if func_group == 0x05:  # 写操作
                    self._add_anomaly(
                        's7_write',
                        src_ip, dst_ip,
                        'S7写操作',
                        payload.hex()
                    )
                
                elif func_group == 0x28:
                    if len(payload) > 17:
                        sub_func = payload[17]
                        if sub_func == 0x00:
                            self._add_anomaly(
                                's7_cpu_start',
                                src_ip, dst_ip,
                                'S7 CPU启动命令',
                                payload.hex()
                            )
                        elif sub_func == 0x01:
                            self._add_anomaly(
                                's7_cpu_stop',
                                src_ip, dst_ip,
                                'S7 CPU停止命令',
                                payload.hex()
                            )
                
                elif func_group == 0x28 and len(payload) > 17:
                    if payload[17] == 0x02:
                        self._add_anomaly(
                            's7_password',
                            src_ip, dst_ip,
                            'S7密码验证',
                            payload.hex()
                        )
    
    def _analyze_modbus_traffic(self, src_ip, dst_ip, payload):
        """分析Modbus协议流量"""
        if len(payload) < 8:
            return
        
        func_code = payload[7] if len(payload) > 7 else 0
        
        # 写操作
        if func_code in [0x05, 0x06, 0x0F, 0x10]:
            self._add_anomaly(
                'modbus_write',
                src_ip, dst_ip,
                f'Modbus写操作 (功能码: 0x{func_code:02X})',
                payload.hex()
            )
    
    def _analyze_dnp3_traffic(self, src_ip, dst_ip, payload):
        """分析DNP3协议流量"""
        if len(payload) < 2:
            return
        
        # DNP3起始字节
        if payload[0] == 0x05 and payload[1] == 0x64:
            if len(payload) > 10:
                func_code = payload[10]
                # 写操作
                if func_code in [0x01, 0x02, 0x03, 0x04]:
                    self._add_anomaly(
                        'dnp3_write',
                        src_ip, dst_ip,
                        f'DNP3控制操作 (功能码: {func_code})',
                        payload.hex()
                    )
    
    def _add_anomaly(self, anomaly_type, src_ip, dst_ip, description, data):
        """添加异常"""
        self.anomalies.append({
            'type': anomaly_type,
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'description': description,
            'data': data[:200],  # 截断
            'timestamp': datetime.now().isoformat(),
        })
    
    def _generate_analysis_report(self):
        """生成分析报告"""
        print("\n" + "=" * 60)
        print("工控网络流量取证分析报告")
        print("=" * 60)
        
        # 会话统计
        print(f"\n[1] 会话统计")
        print(f"    总会话数: {len(self.sessions)}")
        for session, packets in sorted(self.sessions.items(),
                                       key=lambda x: len(x[1]),
                                       reverse=True)[:10]:
            print(f"    {session}: {len(packets)} 个包")
        
        # 异常事件
        print(f"\n[2] 异常事件 ({len(self.anomalies)} 个)")
        
        type_counts = Counter(a['type'] for a in self.anomalies)
        for atype, count in type_counts.items():
            print(f"    {atype}: {count} 次")
        
        # 详细异常
        if self.anomalies:
            print(f"\n[3] 异常详情 (前20个)")
            for anomaly in self.anomalies[:20]:
                print(f"\n  类型: {anomaly['type']}")
                print(f"  来源: {anomaly['src_ip']} -> {anomaly['dst_ip']}")
                print(f"  描述: {anomaly['description']}")
                print(f"  数据: {anomaly['data']}")
        
        # 安全评估
        print(f"\n[4] 安全评估")
        
        cpu_stops = [a for a in self.anomalies if a['type'] == 's7_cpu_stop']
        if cpu_stops:
            print(f"  [!] 检测到 {len(cpu_stops)} 次CPU停止命令")
        
        writes = [a for a in self.anomalies if 'write' in a['type']]
        if writes:
            print(f"  [!] 检测到 {len(writes)} 次写操作")
        
        passwords = [a for a in self.anomalies if a['type'] == 's7_password']
        if passwords:
            print(f"  [!] 检测到 {len(passwords)} 次密码验证")
            print(f"      可能的密码暴力破解或窃取")
        
        print("\n" + "=" * 60)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python3 network_forensics.py <pcap文件>")
        sys.exit(1)
    
    forensics = ICSNetworkForensics()
    forensics.analyze_pcap(sys.argv[1])
```

---

---

