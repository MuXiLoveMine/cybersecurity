# Triton (TRITON) 分析

### 8.1 概述

Triton (又名TRITON, Trisis) 是2017年发现的恶意代码，它是首个针对安全仪表系统(SIS)的攻击工具。它攻击了沙特阿拉伯的石化设施，试图导致物理爆炸。

```
Triton基本信息:
- 发现时间: 2017年12月
- 目标: 沙特Petro Rabigh炼油厂
- 攻击对象: 施耐德电气Triconex安全仪表系统
- 攻击目的: 通过禁用安全系统引发物理爆炸
- 严重程度: 可能导致灾难性物理事故
- 被发现原因: 代码bug导致SIS触发安全停机
```

### 8.2 攻击架构

```
Triton攻击链:

┌─────────────────────────────────────────────────────┐
│ 阶段1: 初始渗透                                      │
│  ├── 鱼叉钓鱼 / 水坑攻击                             │
│  ├── 获取工程站访问权限                              │
│  └── 横向移动到SIS工程网络                           │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────┐
│ 阶段2: SIS攻击准备                                   │
│  ├── 逆向Triconex TriStation协议                     │
│  ├── 识别SIS控制器型号和固件                         │
│  ├── 理解安全逻辑程序                               │
│  └── 准备攻击载荷                                    │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────┐
│ 阶段3: SIS攻击                                       │
│  ├── 将控制器置于"程序模式"                          │
│  ├── 下载恶意代码到控制器                            │
│  ├── 修改安全逻辑 (禁用关键安全联锁)                 │
│  ├── 将控制器恢复为"运行模式"                        │
│  └── 等待危险条件触发                                │
└───────────────────────┬─────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────┐
│ 阶段4: 潜在破坏                                      │
│  ├── 安全联锁被禁用                                  │
│  ├── 当危险条件出现时安全系统不动作                  │
│  └── 导致物理爆炸/泄露                              │
│                                                      │
│  实际情况: 代码bug导致SIS触发安全停机                 │
│  暴露了攻击行为                                      │
└─────────────────────────────────────────────────────┘
```

### 8.3 TriStation协议逆向

Triton的核心技术是逆向了Triconex的专有TriStation通信协议：

```
TriStation协议分析:

1. 物理层: RS-232串口
2. 链路层: 自定义帧格式
   ┌────────┬──────────┬─────────┬────────┬────────┐
   │ 起始符  │ 长度     │ 命令码  │ 数据    │ CRC    │
   │ 0x5A   │ 2 bytes │ 1 byte │ 变长   │ 2 bytes│
   └────────┴──────────┴─────────┴────────┴────────┘

3. 关键命令:
   - 0x01: 读控制器状态
   - 0x02: 写控制器配置
   - 0x03: 下载用户程序
   - 0x04: 读内存数据
   - 0x05: 写内存数据
   - 0x09: 切换控制器模式

4. 安全验证:
   - 协议本身无加密
   - 仅依赖网络隔离
   - 无认证机制
   - 无完整性校验
```

```python
# Triton TriStation协议通信伪代码

class TriStationClient:
    """Triconex TriStation协议客户端"""
    
    def __init__(self, serial_port):
        self.port = serial_port
        self.seq_num = 0
    
    def build_frame(self, command, data=b''):
        """构建TriStation帧"""
        start = bytes([0x5A])
        length = struct.pack('<H', 4 + len(data) + 2)  # 命令+数据+CRC
        cmd = bytes([command])
        
        frame = start + length + cmd + data
        crc = self._calc_crc(frame[1:])  # CRC不包含起始符
        
        return frame + struct.pack('<H', crc)
    
    def read_controller_status(self):
        """读取控制器状态"""
        frame = self.build_frame(0x01)
        response = self._send_recv(frame)
        
        if response:
            status = self._parse_status(response)
            return status
        return None
    
    def switch_mode(self, mode):
        """切换控制器模式
        0x00: 运行模式
        0x01: 程序模式
        0x02: 远程模式
        """
        frame = self.build_frame(0x09, bytes([mode]))
        response = self._send_recv(frame)
        return response is not None
    
    def download_program(self, program_data):
        """下载用户程序"""
        # 分段发送
        chunk_size = 256
        for i in range(0, len(program_data), chunk_size):
            chunk = program_data[i:i+chunk_size]
            addr = struct.pack('<I', i)
            frame = self.build_frame(0x03, addr + chunk)
            self._send_recv(frame)
    
    def write_memory(self, address, data):
        """写内存"""
        addr = struct.pack('<I', address)
        frame = self.build_frame(0x05, addr + data)
        response = self._send_recv(frame)
        return response is not None
```

---

---

