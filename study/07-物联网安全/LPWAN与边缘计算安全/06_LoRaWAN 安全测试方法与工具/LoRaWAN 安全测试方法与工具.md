# LoRaWAN 安全测试方法与工具

### 6.1 测试方法学

```
┌─────────────────────────────────────────────────────────┐
│            LoRaWAN 安全测试维度                            │
├─────────────┬───────────────┬──────────────┬────────────┤
│  密钥安全    │  协议合规      │  攻击模拟     │  设备物理   │
│ - 密钥存储   │ - MIC 校验     │ - 重放       │ - Flash 读取│
│ - 密钥派生   │ - Join 流程    │ - ACK 伪造    │ - 侧信道    │
│ - 密钥更新   │ - FCnt 单调性   │ - Jamming     │ - 防拆检测  │
└─────────────┴───────────────┴──────────────┴────────────┘
```

### 6.2 常用工具

| 工具 | 用途 | 类型 |
|------|------|------|
| Chirpstack | 开源 LoRaWAN 网络服务器，用于搭建测试网络 | 网络侧 |
| LoRa Packet Forwarder | 网关侧转发程序，可抓取原始帧 | 网关侧 |
| lorawan-bench / lorawan-fuzzer | 协议模糊测试 | 测试 |
| HackRF / BladeRF | 射频抓包与重放 | SDR |
| URH (Universal Radio Hacker) | 射频协议分析与解码 | SDR |
| radare2 / Ghidra | 固件逆向与密钥提取 | 静态分析 |
| Firmwalker | 固件敏感信息扫描 | 静态分析 |

### 6.3 射频抓包与解码示例

使用 URH 解码 LoRa 上行帧：
```python
# URH Python 脚本：解码 LoRa CSS 信号
from urh.dev.Backends import HackRF
from urh.signalprocessing.Signal import Signal

# 1. 捕获 LoRa 信号
hackrf = HackRF(center_freq=868_100_000, sample_rate=1_000_000, bandwidth=250_000)
hackrf.start_rx_mode()
# ... 捕获时长 10s
hackrf.stop_rx_mode()

# 2. 解调 CSS，提取 LoRa 帧
sig = Signal("capture.complex")
sig modulation = "CSS"  # URH 自定义调制
frames = sig.detect_frames()

# 3. 对每个帧做 LoRaWAN MAC 解析
for frame in frames:
    mhdr = frame[0]
    mac_payload = frame[1:-4]
    mic = frame[-4:]
    print(f"MHDR=0x{mhdr:02x}, DevAddr=0x{int.from_bytes(mac_payload[:4],'big'):08x}, MIC={mic.hex()}")
```

### 6.4 协议模糊测试框架

```python
# LoRaWAN 协议模糊测试示例（基于构建异常 MAC 帧）
import os, struct
from Crypto.Cipher import AES

class LoRaWANFuzzer:
    def __init__(self, nwkskey, appskey, devaddr):
        self.nwkskey = nwkskey
        self.appskey = appskey
        self.devaddr = devaddr

    def build_frame(self, fcnt, payload, fport=1, confirmed=False):
        mhdr = 0x80 if confirmed else 0x40      # Confirmed/Unconfirmed Data Up
        fctrl = 0x00
        fhdr = struct.pack("<BIH", self.devaddr, fctrl, fcnt)
        mac_payload = fhdr + bytes([fport]) + payload
        # 计算 MIC (简化版，未含 B0 块完整构造)
        mic = self._compute_mic(mhdr, mac_payload)
        return bytes([mhdr]) + mac_payload + mic

    def _compute_mic(self, mhdr, mac_payload):
        # 实际应按 LoRaWAN spec 构造 B0 块
        from Crypto.Hash import CMAC
        ciph = CMAC.new(self.nwkskey, ciphermod=AES)
        ciph.update(bytes([mhdr]) + mac_payload)
        return ciph.digest()[:4]

    def fuzz_invalid_fcnt(self, count=100):
        """异常 FCnt 值模糊测试"""
        cases = [0, 0xFFFF, 0x10000, 0xFFFFFFFE, 0xFFFFFFFF]
        for c in cases:
            yield self.build_frame(fcnt=c & 0xFFFF, payload=b"\x00" * 8)

    def fuzz_oversized_payload(self):
        """超长载荷测试"""
        for size in [51, 64, 128, 242]:   # LoRaWAN EU868 上行最大 51 字节（SF12）
            yield self.build_frame(fcnt=1, payload=b"\x41" * size)
```

> 测试目标：观察网络服务器对异常 FCnt、超长载荷、非法 FPort 的处理，验证是否会崩溃或错误接受。

---

---

## 📋 内容审核与补充建议

> 针对「LoRaWAN 安全测试方法与工具」部分的内容审核结果：

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
