# Reaper物联网蠕虫

### 6.1 Reaper概述

Reaper（又称IoTroop）于2017年出现，代表了IoT僵尸网络从"弱密码爆破"向"漏洞利用蠕虫"的演进：

```
Reaper vs Mirai 对比:

         Mirai                    Reaper
┌─────────────────────┐  ┌─────────────────────┐
│ 弱密码爆破 (Telnet)  │  │ 漏洞利用 (Web RCE)   │
│ 60+凭证组合         │  │ 多个CVE漏洞          │
│ 感染后立即攻击      │  │ 感染后潜伏等待      │
│ 单日40万台          │  │ 潜在感染200万+       │
│ 架构: 中心化        │  │ 架构: 混合式        │
└─────────────────────┘  └─────────────────────┘
```

### 6.2 Reaper利用的漏洞列表

| CVE编号 | 设备/厂商 | 漏洞类型 | 影响 |
|---------|----------|---------|------|
| CVE-2017-8225 | D-Link路由器 | 空指针引用 | 远程执行 |
| CVE-2016-10238 | Netgear R6400 | 命令注入 | 远程执行 |
| CVE-2017-7921 | Hikvision摄像头 | 认证绕过 | 管理员权限 |
| CVE-2017-13705 | TP-Link路由器 | SQL注入 | 信息泄露 |
| CVE-2016-10401 | Netgear设备 | 命令注入 | 远程执行 |
| N/A | GoAhead摄像头 | 路径遍历 | 远程执行 |
| N/A | Linksys路由器 | 未授权访问 | 管理权限 |
| N/A | Vacron摄像头 | RCE漏洞 | 远程执行 |

### 6.3 Reaper蠕虫传播机制

```python
# Reaper蠕虫传播模拟（伪代码）
class ReaperWorm:
    """Reaper物联网蠕虫"""
    
    EXPLOITS = {
        'dlink_rce': DLinkRCEExploit(),
        'netgear_cmd_inject': NetgearCmdInjectExploit(),
        'hikvision_auth_bypass': HikvisionBypassExploit(),
        'tp_link_sqli': TPLinkSQLiExploit(),
        'goahead_traversal': GoAheadTraversalExploit(),
        'vacron_rce': VacronRCEExploit(),
    }
    
    def spread(self):
        """蠕虫传播主循环"""
        while True:
            # 1. 生成目标IP
            target_ip = self.generate_target()
            
            # 2. 端口扫描
            open_ports = self.port_scan(target_ip, 
                                        ports=[80, 8080, 8443, 443, 23])
            
            if not open_ports:
                continue
            
            # 3. 指纹识别
            device_info = self.fingerprint(target_ip, open_ports)
            
            if not device_info:
                continue
            
            # 4. 匹配漏洞利用模块
            for exploit_name, exploit in self.EXPLOITS.items():
                if exploit.matches(device_info):
                    try:
                        # 5. 执行漏洞利用
                        if exploit.execute(target_ip, device_info):
                            # 6. 下载并执行payload
                            self.deploy_payload(target_ip, device_info)
                            # 7. 新节点开始传播
                            break
                    except Exception:
                        continue
            
            time.sleep(random.uniform(0.5, 2.0))
```

---

---

