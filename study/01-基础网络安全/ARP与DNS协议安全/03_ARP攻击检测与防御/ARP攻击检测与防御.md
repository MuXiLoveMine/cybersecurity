# ARP攻击检测与防御

### 2.1 静态ARP绑定

最直接有效的防御：将关键设备的IP-MAC映射手动绑定，使其不被ARP欺骗影响。

**Linux静态绑定配置：**

```bash
# 查看当前ARP表
ip neigh show
# 192.168.1.1 dev eth0 lladdr 00:11:22:33:44:55 REACHABLE

# 添加静态ARP绑定（网关）
sudo ip neigh add 192.168.1.1 lladdr 00:11:22:33:44:55 dev eth0 nud permanent

# 或者修改配置文件持久化
# /etc/ethers 文件格式: MAC  IP
echo "00:11:22:33:44:55 192.168.1.1" | sudo tee -a /etc/ethers
# 在 /etc/network/interfaces 中添加:
#   up arp -f /etc/ethers
```

**Windows静态绑定（需管理员权限）：**

```cmd
:: 查看ARP表
arp -a

:: 添加静态绑定
netsh interface ip add neighbors "以太网" 192.168.1.1 00-11-22-33-44-55

:: 删除绑定
netsh interface ip delete neighbors "以太网" 192.168.1.1
```

**局限性：** 静态绑定只保护已绑定的条目，且大规模部署维护成本高。

### 2.2 DAI（动态ARP检测）

DAI（Dynamic ARP Inspection）是交换机层面的防御机制，配合DHCP Snooping使用，对非信任端口的ARP报文进行合法性校验。

**Cisco交换机DAI配置示例：**

```cisco
! 启用DHCP Snooping（DAI依赖其绑定表）
Switch(config)# ip dhcp snooping
Switch(config)# ip dhcp snooping vlan 10

! 指定上联端口为信任端口（连接DHCP服务器或网关）
Switch(config)# interface GigabitEthernet0/24
Switch(config-if)# ip dhcp snooping trust

! 启用DAI
Switch(config)# ip arp inspection vlan 10

! 指定上联端口为ARP信任端口
Switch(config)# interface GigabitEthernet0/24
Switch(config-if)# ip arp inspection trust

! 可选：配置ARP速率限制，防止ARP风暴
Switch(config)# interface range GigabitEthernet0/1-23
Switch(config-if-range)# ip arp inspection limit rate 15 burst interval 1
```

**工作原理：**
1. DHCP Snooping维护IP-MAC绑定表
2. 交换机收到ARP请求/应答时，检查绑定表
3. 不匹配的ARP包被丢弃并记录日志

### 2.3 ARP监控工具（arpwatch等）

**arpwatch** 盽听网络中的ARP活动，记录IP-MAC变化并通过邮件告警。

```bash
# Ubuntu/Debian安装
sudo apt-get install arpwatch

# CentOS/RHEL安装
sudo yum install arpwatch

# 启动arpwatch监听eth0
sudo arpwatch -i eth0 -f /var/lib/arpwatch/arp.dat

# 配置告警邮件接收人
# 修改 /etc/arpwatch.conf:
#   eth0    -m    security@example.com
```

**arpwatch告警示例：**
```
Subject: changed ethernet address

hostname: <unknown>
ip address: 192.168.1.1
ethernet address: 0:11:22:33:44:55  (旧MAC)
ethernet address: 66:77:88:99:aa:bb  (新MAC，可能是ARP欺骗)
timestamp: Saturday, September 12, 2026 10:30:45
```

**其他常用ARP监控工具：**
- `arping`：验证特定IP的MAC地址
- `arping -D`：Duplicate Address Detection
- `Scapy`：构建自定义ARP检测脚本

### 2.4 Python检测脚本示例

以下脚本模拟ARP欺骗检测，通过对比静态绑定表与实际ARP响应来发现异常。

```python
"""
ARP欺骗检测脚本 - 模拟教育版
功能：对比预设的IP-MAC绑定表与实际网络ARP响应，
      发现MAC地址变化则触发告警。
注意：使用模拟数据，不执行真实网络扫描。
"""

import time
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ARPEntry:
    """ARP表项"""
    ip: str
    mac: str
    last_seen: str
    status: str = "normal"


class ARPTable:
    """模拟ARP缓存管理"""

    def __init__(self, trusted_bindings: Dict[str, str]):
        # trusted_bindings: {"192.168.1.1": "00:11:22:33:44:55", ...}
        self.trusted_bindings = trusted_bindings
        self.current_table: Dict[str, ARPEntry] = {}
        self.alerts = []

    def update_entry(self, ip: str, mac: str):
        """模拟收到一个ARP响应，更新ARP表"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_table[ip] = ARPEntry(ip=ip, mac=mac, last_seen=timestamp)

    def check_spoofing(self) -> list:
        """检测是否存在ARP欺骗"""
        alerts = []
        for ip, entry in self.current_table.items():
            trusted_mac = self.trusted_bindings.get(ip)
            if trusted_mac and entry.mac.lower() != trusted_mac.lower():
                alert = (
                    f"[ALERT] ARP欺骗检测! "
                    f"IP={ip}, 预期MAC={trusted_mac}, "
                    f"实际MAC={entry.mac}, "
                    f"时间={entry.last_seen}"
                )
                alerts.append(alert)
                self.alerts.append(alert)
        return alerts

    def print_table(self):
        """打印当前ARP表"""
        print("\n=== 当前ARP缓存表 ===")
        print(f"{'IP地址':<18} {'MAC地址':<22} {'状态':<10} {'最后发现时间'}")
        print("-" * 70)
        for ip, entry in self.current_table.items():
            trusted_mac = self.trusted_bindings.get(ip)
            status = "OK" if (trusted_mac and
                              entry.mac.lower() == trusted_mac.lower()) else "SPOOFED"
            print(f"{entry.ip:<18} {entry.mac:<22} {status:<10} {entry.last_seen}")

    def print_alerts(self):
        """打印所有告警"""
        if not self.alerts:
            print("\n无告警，网络状态正常。")
            return
        print(f"\n=== ARP告警记录 ({len(self.alerts)}条) ===")
        for i, alert in enumerate(self.alerts, 1):
            print(f"[{i}] {alert}")


def main():
    """主函数 - 模拟ARP欺骗检测"""
    # 预设的可信IP-MAC绑定表
    trusted = {
        "192.168.1.1": "00:11:22:33:44:55",   # 网关
        "192.168.1.10": "aa:bb:cc:dd:ee:01",  # 主机A
        "192.168.1.20": "aa:bb:cc:dd:ee:02",  # 主机B
    }

    arp_table = ARPTable(trusted)

    # === 模拟正常ARP响应 ===
    print("=" * 60)
    print("场景1: 正常网络环境")
    print("=" * 60)
    arp_table.update_entry("192.168.1.1", "00:11:22:33:44:55")
    arp_table.update_entry("192.168.1.10", "aa:bb:cc:dd:ee:01")
    arp_table.update_entry("192.168.1.20", "aa:bb:cc:dd:ee:02")
    arp_table.print_table()
    alerts = arp_table.check_spoofing()
    print(f"\n检测结果: {'发现异常!' if alerts else '正常，未检测到ARP欺骗。'}")

    # === 模拟ARP欺骗攻击 ===
    print("\n" + "=" * 60)
    print("场景2: ARP欺骗攻击（网关MAC被伪造）")
    print("=" * 60)
    # 攻击者伪造网关MAC为攻击者MAC
    arp_table.update_entry("192.168.1.1", "de:ad:be:ef:00:01")  # 被篡改!
    arp_table.print_table()
    alerts = arp_table.check_spoofing()
    if alerts:
        print(f"\n检测结果: 发现异常! 共 {len(alerts)} 条告警:")
        for a in alerts:
            print(f"  {a}")

    # === 打印所有历史告警 ===
    arp_table.print_alerts()


if __name__ == "__main__":
    main()
```

**运行输出示例：**
```
============================================================
场景1: 正常网络环境
============================================================

=== 当前ARP缓存表 ===
IP地址             MAC地址               状态       最后发现时间
----------------------------------------------------------------------
192.168.1.1        00:11:22:33:44:55     OK        2026-09-12 10:30:45
192.168.1.10       aa:bb:cc:dd:ee:01     OK        2026-09-12 10:30:45
192.168.1.20       aa:bb:cc:dd:ee:02     OK        2026-09-12 10:30:45

检测结果: 正常，未检测到ARP欺骗。

============================================================
场景2: ARP欺骗攻击（网关MAC被伪造）
============================================================
[ALERT] ARP欺骗检测! IP=192.168.1.1, 预期MAC=00:11:22:33:44:55, 实际MAC=de:ad:be:ef:00:01, 时间=2026-09-12 10:30:46
检测结果: 发现异常! 共 1 条告警:
```

---

---

## 📋 内容审核与补充建议

> 针对「ARP攻击检测与防御」部分的内容审核结果：

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
