# OT环境证据保全

### 5.1 取证原则

```
OT取证核心原则:

1. 不破坏原则:
   - 不改变PLC运行状态
   - 不修改系统配置
   - 不删除任何数据
   - 不重启设备 (除非必要)

2. 最小干预原则:
   - 仅采集必要的证据
   - 使用只读方式采集
   - 避免在生产设备上操作
   - 优先使用网络取证

3. 可重现原则:
   - 记录所有操作步骤
   - 采集时有多人见证
   - 证据链完整
   - 使用时间戳

4. 安全优先:
   - 物理安全 > 取证
   - 如果取证导致危险, 立即停止
   - 安全人员参与取证决策
```

### 5.2 证据采集顺序

```
OT环境证据采集顺序 (易失性排序):

1. 寄存器/缓存 (最易失):
   - PLC内存状态
   - 计时器/计数器值
   - 当前输出状态

2. 网络连接 (高易失):
   - 活动连接表
   - ARP表
   - 路由表

3. 内存 (中易失):
   - 进程内存转储
   - 网络缓冲区
   - 临时数据

4. 临时数据 (中低易失):
   - 临时文件
   - 页面文件
   - 日志缓冲区

5. 持久数据 (低易失):
   - PLC程序
   - 配置文件
   - 事件日志
   - 诊断缓冲区

6. 离线数据 (最持久):
   - 备份磁带
   - 离线备份
   - 归档日志
```

### 5.3 网络取证采集

```python
#!/usr/bin/env python3
"""OT网络取证数据采集工具"""
import subprocess
import os
import hashlib
import json
from datetime import datetime

class OTNetworkForensics:
    """OT网络取证采集工具"""
    
    def __init__(self, case_id, evidence_dir='/tmp/ot_forensics'):
        self.case_id = case_id
        self.evidence_dir = os.path.join(evidence_dir, case_id)
        self.chain_of_custody = []
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 创建证据目录
        os.makedirs(self.evidence_dir, exist_ok=True)
    
    def _log_action(self, action, details):
        """记录证据链"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details,
            'operator': os.getenv('USER', 'unknown'),
        }
        self.chain_of_custody.append(entry)
        
        # 写入证据链文件
        coc_file = os.path.join(self.evidence_dir, 'chain_of_custody.json')
        with open(coc_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def _calc_hash(self, filepath):
        """计算文件哈希"""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def capture_network_traffic(self, interface, duration=60):
        """采集网络流量"""
        print(f"[*] 采集网络流量 (接口: {interface}, 时长: {duration}秒)")
        
        output_file = os.path.join(
            self.evidence_dir,
            f'capture_{interface}_{self.timestamp}.pcap'
        )
        
        try:
            # 使用tcpdump采集 (需要root)
            cmd = [
                'tcpdump', '-i', interface,
                '-w', output_file,
                '-s', '0',  # 捕获完整包
                '-c', '0',   # 不限制包数
                f'{duration}'  # 时长通过timeout控制
            ]
            
            # 使用timeout控制采集时长
            result = subprocess.run(
                ['timeout', str(duration)] + cmd,
                capture_output=True, text=True, timeout=duration + 10
            )
            
            if os.path.exists(output_file):
                file_hash = self._calc_hash(output_file)
                file_size = os.path.getsize(output_file)
                
                self._log_action('网络流量采集', {
                    'interface': interface,
                    'duration': duration,
                    'file': output_file,
                    'size': file_size,
                    'sha256': file_hash,
                })
                
                print(f"[+] 采集完成: {output_file}")
                print(f"    大小: {file_size} bytes")
                print(f"    SHA256: {file_hash}")
                
                return output_file
            else:
                print("[-] 采集失败")
                return None
                
        except Exception as e:
            print(f"[-] 错误: {e}")
            self._log_action('采集失败', {'error': str(e)})
            return None
    
    def capture_connection_state(self):
        """采集网络连接状态"""
        print("[*] 采集网络连接状态")
        
        # 采集活动连接
        connections_file = os.path.join(
            self.evidence_dir,
            f'connections_{self.timestamp}.txt'
        )
        
        try:
            result = subprocess.run(
                ['netstat', '-anp'],
                capture_output=True, text=True, timeout=30
            )
            
            with open(connections_file, 'w', encoding='utf-8') as f:
                f.write(f"# 网络连接状态 - {datetime.now().isoformat()()}\n")
                f.write(result.stdout)
            
            file_hash = self._calc_hash(connections_file)
            
            self._log_action('网络连接状态采集', {
                'file': connections_file,
                'sha256': file_hash,
                'connection_count': result.stdout.count('\n'),
            })
            
            print(f"[+] 连接状态已保存")
            return connections_file
            
        except Exception as e:
            print(f"[-] 错误: {e}")
            return None
    
    def capture_arp_table(self):
        """采集ARP表"""
        print("[*] 采集ARP表")
        
        arp_file = os.path.join(
            self.evidence_dir,
            f'arp_table_{self.timestamp}.txt'
        )
        
        try:
            result = subprocess.run(
                ['arp', '-a'],
                capture_output=True, text=True, timeout=10
            )
            
            with open(arp_file, 'w', encoding='utf-8') as f:
                f.write(f"# ARP表 - {datetime.now().isoformat()}\n")
                f.write(result.stdout)
            
            file_hash = self._calc_hash(arp_file)
            
            self._log_action('ARP表采集', {
                'file': arp_file,
                'sha256': file_hash,
            })
            
            print(f"[+] ARP表已保存")
            return arp_file
            
        except Exception as e:
            print(f"[-] 错误: {e}")
            return None
    
    def capture_routing_table(self):
        """采集路由表"""
        print("[*] 采集路由表")
        
        route_file = os.path.join(
            self.evidence_dir,
            f'routing_table_{self.timestamp}.txt'
        )
        
        try:
            result = subprocess.run(
                ['netstat', '-rn'],
                capture_output=True, text=True, timeout=10
            )
            
            with open(route_file, 'w', encoding='utf-8') as f:
                f.write(f"# 路由表 - {datetime.now().isoformat()}\n")
                f.write(result.stdout)
            
            self._log_action('路由表采集', {
                'file': route_file,
                'sha256': self._calc_hash(route_file),
            })
            
            print(f"[+] 路由表已保存")
            return route_file
            
        except Exception as e:
            print(f"[-] 错误: {e}")
            return None
    
    def capture_firewall_rules(self):
        """采集防火墙规则"""
        print("[*] 采集防火墙规则")
        
        fw_file = os.path.join(
            self.evidence_dir,
            f'firewall_rules_{self.timestamp}.txt'
        )
        
        try:
            # iptables (Linux)
            result = subprocess.run(
                ['iptables', '-L', '-n', '-v'],
                capture_output=True, text=True, timeout=10
            )
            
            with open(fw_file, 'w', encoding='utf-8') as f:
                f.write(f"# 防火墙规则 - {datetime.now().isoformat()}\n")
                f.write(result.stdout)
            
            self._log_action('防火墙规则采集', {
                'file': fw_file,
                'sha256': self._calc_hash(fw_file),
            })
            
            print(f"[+] 防火墙规则已保存")
            return fw_file
            
        except Exception as e:
            print(f"[-] 错误: {e}")
            return None
    
    def capture_system_logs(self):
        """采集系统日志"""
        print("[*] 采集系统日志")
        
        log_files = [
            '/var/log/syslog',
            '/var/log/messages',
            '/var/log/auth.log',
            '/var/log/audit/audit.log',
        ]
        
        collected = []
        
        for log_file in log_files:
            if os.path.exists(log_file):
                dest = os.path.join(
                    self.evidence_dir,
                    f'log_{os.path.basename(log_file)}_{self.timestamp}'
                )
                
                try:
                    # 使用cp而不是cat, 保留元数据
                    subprocess.run(['cp', '-p', log_file, dest], timeout=30)
                    
                    file_hash = self._calc_hash(dest)
                    
                    self._log_action('系统日志采集', {
                        'source': log_file,
                        'destination': dest,
                        'sha256': file_hash,
                    })
                    
                    collected.append(dest)
                    print(f"  [+] {log_file} -> {dest}")
                    
                except Exception as e:
                    print(f"  [-] {log_file}: {e}")
        
        return collected
    
    def capture_plc_diagnostic(self, plc_ip, port=102):
        """采集PLC诊断信息 (非侵入性)"""
        print(f"[*] 采集PLC诊断信息 ({plc_ip})")
        
        diag_file = os.path.join(
            self.evidence_dir,
            f'plc_diag_{plc_ip}_{self.timestamp}.txt'
        )
        
        try:
            import socket
            import struct
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((plc_ip, port))
            
            # 仅读取诊断信息, 不修改任何内容
            # COTP连接
            tpkt = struct.pack('>BBH', 3, 0, 22)
            cotp = bytes([
                0x11, 0xE0, 0x00, 0x01, 0x00, 0x01, 0x00,
                0xC0, 0x02, 0x01, 0x00,
                0xC1, 0x02, 0x01, 0x02,
                0xC2, 0x01, 0x0A
            ])
            sock.send(tpkt + cotp)
            response = sock.recv(1024)
            
            with open(diag_file, 'w', encoding='utf-8') as f:
                f.write(f"# PLC诊断信息 - {datetime.now().isoformat()}\n")
                f.write(f"# PLC地址: {plc_ip}:{port}\n")
                f.write(f"# COTP响应: {response.hex()}\n")
                f.write(f"# 响应长度: {len(response)}\n")
                
                # 检查连接是否成功
                if len(response) >= 7 and response[5] == 0xD0:
                    f.write("# COTP连接: 成功\n")
                else:
                    f.write("# COTP连接: 失败\n")
            
            sock.close()
            
            self._log_action('PLC诊断采集', {
                'plc_ip': plc_ip,
                'file': diag_file,
                'sha256': self._calc_hash(diag_file),
            })
            
            print(f"[+] PLC诊断信息已保存")
            return diag_file
            
        except Exception as e:
            print(f"[-] 错误: {e}")
            return None
    
    def generate_report(self):
        """生成取证报告"""
        report_file = os.path.join(
            self.evidence_dir,
            f'forensics_report_{self.timestamp}.txt'
        )
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("工控安全事件取证报告\n")
            f.write(f"案件编号: {self.case_id}\n")
            f.write(f"采集时间: {datetime.now().isoformat()}\n")
            f.write(f"采集人员: {os.getenv('USER', 'unknown')}\n")
            f.write("=" * 70 + "\n\n")
            
            f.write("证据链:\n")
            f.write("-" * 70 + "\n")
            for entry in self.chain_of_custody:
                f.write(f"时间: {entry['timestamp']}\n")
                f.write(f"操作: {entry['action']}\n")
                f.write(f"详情: {json.dumps(entry['details'], ensure_ascii=False)}\n")
                f.write(f"操作人: {entry['operator']}\n")
                f.write("-" * 70 + "\n")
        
        print(f"\n[+] 取证报告已生成: {report_file}")
        return report_file

# 使用示例
if __name__ == '__main__':
    forensics = OTNetworkForensics('INC-2026-001')
    
    # 采集各种取证数据
    forensics.capture_network_traffic('eth0', duration=30)
    forensics.capture_connection_state()
    forensics.capture_arp_table()
    forensics.capture_routing_table()
    forensics.capture_firewall_rules()
    forensics.capture_system_logs()
    
    # 生成报告
    forensics.generate_report()
```

### 5.4 主机取证采集

```
OT主机取证检查清单:

1. 内存采集:
   [ ] 使用LiME/Rekall采集完整内存
   [ ] 提取活动进程列表
   [ ] 提取网络连接
   [ ] 提取注册表/配置 (内存中)
   [ ] 提取密钥/密码 (内存中)

2. 进程分析:
   [ ] 进程列表 (ps/tasklist)
   [ ] 进程树 (父子关系)
   [ ] 进程网络连接
   [ ] 进程文件路径
   [ ] 进程加载的DLL
   [ ] 异常进程识别

3. 文件系统:
   [ ] 关键目录文件列表
   [ ] 新增/修改文件 (时间线)
   [ ] 可执行文件哈希
   [ ] 临时文件
   [ ] 下载文件
   [ ] 回收站内容

4. 注册表/配置:
   [ ] 启动项
   [ ] 服务
   [ ] 计划任务
   [ ] 用户账户
   [ ] 网络配置
   [ ] 安装的软件

5. 日志:
   [ ] 系统日志
   [ ] 安全日志
   [ ] 应用日志
   [ ] 工控软件日志
   [ ] PLC诊断日志
   [ ] 审计日志

6. 网络取证:
   [ ] 抓包文件
   [ ] 网络连接
   [ ] ARP表
   [ ] DNS缓存
   [ ] 路由表
   [ ] 防火墙规则
```

---

---

## 📋 内容审核与补充建议

> 针对「OT环境证据保全」部分的内容审核结果：

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
