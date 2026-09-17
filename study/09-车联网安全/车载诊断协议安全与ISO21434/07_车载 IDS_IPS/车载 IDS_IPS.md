# 车载 IDS/IPS

### 6.1 入侵检测部署位置

车载入侵检测/防御系统（IDS/IPS）需要在车辆网络的多个关键节点部署，形成纵深防御：

```
IDS/IPS 部署架构：

                    ┌───────────────────────────────────────────┐
                    │            云端 SOC (Security Operations)  │
                    │     IDS 规则更新 / 事件聚合 / 威胁情报       │
                    └───────────────────┬───────────────────────┘
                                        │ 4G/5G 上报
                    ┌───────────────────┴───────────────────────┐
                    │              TCU (Telematics Unit)         │
                    │          车载 SOC Agent / 事件转发          │
                    └───────────────────┬───────────────────────┘
                                        │
                    ┌───────────────────┴───────────────────────┐
                    │          中央网关 IDS/IPS 引擎             │
                    │   监控所有跨域流量 + 域间异常检测           │
                    └──┬──────────┬──────────┬─────────────┬────┘
                       │          │          │             │
                  ┌────┴───┐ ┌───┴────┐ ┌───┴────┐  ┌─────┴───┐
                  │域内IDS  │ │域内IDS  │ │域内IDS  │  │ OBD IDS │
                  │CAN-A    │ │CAN-B   │ │CAN-C    │  │ 诊断口  │
                  └────────┘ └────────┘ └────────┘  └────────┘
```

**各层级 IDS 职责：**
- **域内 IDS（ECU 级）**：监控单条 CAN 总线上的异常帧（ID 洪水、频率异常、伪装帧）
- **网关 IDS**：监控跨域流量，执行路由违规检测和协议异常检测
- **TCU IDS**：监控外部通信链路（蓝牙/WiFi/蜂窝），检测远程攻击
- **云端 SOC**：汇聚所有 IDS 事件，关联分析，威胁情报共享

### 6.2 检测规则

**基于规则的检测（Signature-based）：**

```yaml
# 车载 IDS 规则集示例
rules:
  # 规则1: 检测 SecurityAccess 暴力破解
  - id: SA-001
    name: "SecurityAccess Brute Force"
    description: "检测 SecurityAccess 密钥错误超过阈值"
    protocol: "UDS"
    match:
      service_id: 0x27
      nrc: 0x27  # InvalidKey
    threshold: 3  # 3次失败
    window: 60   # 60秒窗口
    action: "alert"
    severity: "high"

  # 规则2: 检测非授权诊断会话切换
  - id: DS-002
    name: "Unauthorized Session Switch"
    description: "检测未经认证切换到编程会话"
    protocol: "UDS"
    match:
      service_id: 0x10
      sub_function: 0x02  # Programming Session
    precondition:
      security_access_unlocked: false
    action: "block"
    severity: "critical"

  # 规则3: CAN ID 洪水检测
  - id: CF-003
    name: "CAN ID Flood"
    description: "检测特定 CAN ID 帧速率异常"
    protocol: "CAN"
    match:
      can_id: 0x7E0
    threshold: 100  # 100 帧/秒
    window: 1
    action: "alert"
    severity: "medium"

  # 规则4: 固件刷写未认证检测
  - id: FW-004
    name: "Unauthorized Firmware Download"
    description: "检测未通过 SecurityAccess 的固件下载请求"
    protocol: "UDS"
    match:
      service_id: 0x34  # RequestDownload
    precondition:
      security_access_unlocked: false
    action: "block"
    severity: "critical"

  # 规则5: 伪装 ECU 检测（ID 冲突）
  - id: SP-005
    name: "ECU Spoofing - ID Conflict"
    description: "检测同一 CAN ID 对应不同 ACK 行为"
    protocol: "CAN"
    match:
      can_id: 0x200
      ack_pattern: "inconsistent"
    action: "alert"
    severity: "high"
```

### 6.3 异常行为识别

**基于行为的检测（Anomaly-based）：**

```python
# 车载 IDS 异常检测引擎
import collections
import time

class VehicleAnomalyDetector:
    def __init__(self):
        # 基线模型：记录正常通信模式
        self.baseline = {
            "can_id_frequency": {},   # 每个 CAN ID 的正常频率范围
            "message_size": {},       # 每个消息的正常大小
            "src_pattern": {},        # 每个 CAN ID 的正常源模式
        }
        self.recent_activity = collections.defaultdict(list)
        self.alert_callback = None

    def train_baseline(self, can_traffic, duration=300):
        """学习正常 CAN 流量的基线模式"""
        counters = collections.Counter()
        sizes = collections.defaultdict(list)

        for frame in can_traffic:
            counters[frame.id] += 1
            sizes[frame.id].append(len(frame.data))

        for can_id, count in counters.items():
            freq = count / duration
            self.baseline["can_id_frequency"][can_id] = {
                "mean": freq,
                "std": (freq * 0.2),  # 20% 容差
                "min": freq * 0.5,
                "max": freq * 1.5
            }
            self.baseline["message_size"][can_id] = {
                "expected": max(set(sizes[can_id]), key=sizes[can_id].count),
                "variance": max(sizes[can_id]) - min(sizes[can_id])
            }

    def detect_anomaly(self, frame):
        """实时检测异常帧"""
        alerts = []

        # 1. 频率异常检测
        now = time.time()
        self.recent_activity[frame.id].append(now)
        # 清理 1 秒窗口外的记录
        self.recent_activity[frame.id] = [
            t for t in self.recent_activity[frame.id] if now - t < 1.0
        ]
        current_freq = len(self.recent_activity[frame.id])

        baseline_freq = self.baseline["can_id_frequency"].get(frame.id)
        if baseline_freq:
            if current_freq > baseline_freq["max"]:
                alerts.append({
                    "type": "FLOOD",
                    "can_id": frame.id,
                    "current_freq": current_freq,
                    "expected_max": baseline_freq["max"],
                    "severity": "HIGH"
                })

        # 2. 新 CAN ID 检测（基线中不存在的 ID）
        if frame.id not in self.baseline["can_id_frequency"]:
            alerts.append({
                "type": "UNKNOWN_ID",
                "can_id": frame.id,
                "severity": "MEDIUM"
            })

        # 3. 载荷大小异常
        expected_size = self.baseline["message_size"].get(frame.id, {}).get("expected")
        if expected_size and len(frame.data) != expected_size:
            alerts.append({
                "type": "SIZE_ANOMALY",
                "can_id": frame.id,
                "current_size": len(frame.data),
                "expected_size": expected_size,
                "severity": "MEDIUM"
            })

        # 4. UDS 服务异常检测
        if frame.id in [0x7DF, 0x7E0, 0x7E1]:  # 诊断 ID
            if len(frame.data) >= 2:
                sid = frame.data[1] if frame.data[0] == 0x02 else frame.data[0]
                if sid == 0x27:  # SecurityAccess
                    if len(frame.data) >= 3 and frame.data[2] == 0x7F:
                        # 否定响应，检查是否暴力破解
                        pass  # 由规则引擎处理

        if alerts and self.alert_callback:
            for alert in alerts:
                self.alert_callback(alert)

        return alerts
```

---

---

## 📋 内容审核与补充建议

> 针对「车载 IDS/IPS」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
