# Python T-BOX安全分析脚本示例

### 6.1 CAN报文分析脚本（使用模拟数据）

```python
#!/usr/bin/env python3
"""
T-BOX安全分析 - CAN报文异常检测脚本
使用模拟CAN总线数据，检测注入攻击、DoS攻击和异常报文
"""

import time
import random
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CANFrame:
    """模拟CAN数据帧"""
    arbitration_id: int        # 仲裁ID
    data: bytes                # 数据场(0-8字节)
    timestamp: float           # 时间戳
    dlc: int = field(default=0)

    def __post_init__(self):
        self.dlc = len(self.data)


class CANBaseline:
    """CAN总线正常行为基线模型"""

    def __init__(self):
        # 预定义正常报文: {CAN_ID: (周期ms, 数据长度, 信号范围)}
        self.known_messages = {
            0x100: {"period_ms": 10,  "dlc": 8, "desc": "发动机转速"},
            0x200: {"period_ms": 20,  "dlc": 8, "desc": "车速"},
            0x300: {"period_ms": 50,  "dlc": 4, "desc": "油门位置"},
            0x400: {"period_ms": 100, "dlc": 8, "desc": "刹车压力"},
            0x500: {"period_ms": 100, "dlc": 4, "desc": "方向盘角度"},
            0x3E0: {"period_ms": 0,   "dlc": 3, "desc": "远程控制响应(事件型)"},
        }
        # 基线统计
        self.id_stats: dict[int, dict] = defaultdict(lambda: {
            "count": 0,
            "intervals": deque(maxlen=100),
            "last_time": 0.0,
            "dlc_values": set(),
        })

    def update(self, frame: CANFrame):
        """用正常流量更新基线"""
        stats = self.id_stats[frame.arbitration_id]
        if stats["count"] > 0:
            interval = (frame.timestamp - stats["last_time"]) * 1000  # ms
            stats["intervals"].append(interval)
        stats["count"] += 1
        stats["last_time"] = frame.timestamp
        stats["dlc_values"].add(frame.dlc)

    def get_expected_period(self, can_id: int) -> Optional[float]:
        """获取预期周期（毫秒）"""
        msg = self.known_messages.get(can_id)
        if msg and msg["period_ms"] > 0:
            return msg["period_ms"]
        # 从统计中推断
        intervals = self.id_stats[can_id]["intervals"]
        if len(intervals) > 10:
            return sum(intervals) / len(intervals)
        return None


class CANIDS:
    """车载CAN总线入侵检测系统"""

    def __init__(self, baseline: CANBaseline):
        self.baseline = baseline
        self.alerts: list[str] = []
        self.id_frequency: dict[int, deque] = defaultdict(
            lambda: deque(maxlen=50)
        )
        self.last_seen: dict[int, float] = {}

    def check_unknown_id(self, frame: CANFrame) -> bool:
        """检测未知CAN ID（报文注入）"""
        if frame.arbitration_id not in self.baseline.known_messages:
            # 如果基线中也没见过此ID
            if frame.arbitration_id not in self.baseline.id_stats or \
               self.baseline.id_stats[frame.arbitration_id]["count"] < 5:
                return True
        return False

    def check_dlc_anomaly(self, frame: CANFrame) -> bool:
        """检测DLC异常"""
        known = self.baseline.known_messages.get(frame.arbitration_id)
        if known and frame.dlc != known["dlc"]:
            return True
        return False

    def check_frequency_anomaly(self, frame: CANFrame) -> bool:
        """检测频率异常（DoS/泛洪）"""
        now = frame.timestamp
        self.id_frequency[frame.arbitration_id].append(now)

        # 检查最近1秒内的频率
        window = [t for t in self.id_frequency[frame.arbitration_id]
                  if now - t <= 1.0]
        expected = self.baseline.get_expected_period(frame.arbitration_id)
        if expected and expected > 0:
            expected_freq = 1000.0 / expected  # 期望频率(帧/秒)
            actual_freq = len(window)
            # 实际频率超过期望5倍视为异常
            if actual_freq > expected_freq * 5:
                return True
        # 绝对频率阈值：单ID每秒>100帧视为泛洪
        if len(window) > 100:
            return True
        return False

    def check_replay(self, frame: CANFrame) -> bool:
        """简化重放检测：时间戳过于规整"""
        prev_time = self.last_seen.get(frame.arbitration_id)
        if prev_time:
            interval = frame.timestamp - prev_time
            # 如果间隔精确到毫秒一致（自然流量有抖动）
            prev_intervals = list(self.baseline.id_stats[frame.arbitration_id]["intervals"])
            if len(prev_intervals) > 5:
                avg = sum(prev_intervals[-5:]) / 5
                # 间隔方差极小说明可能是重放
                variance = sum((x - avg) ** 2 for x in prev_intervals[-5:]) / 5
                if variance < 0.01 and abs(interval * 1000 - avg) < 0.1:
                    return True
        self.last_seen[frame.arbitration_id] = frame.timestamp
        return False

    def analyze(self, frame: CANFrame):
        """分析单帧CAN报文"""
        if self.check_unknown_id(frame):
            self.alerts.append(
                f"[INJECT] t={frame.timestamp:.3f} 未知CAN ID 0x"
                f"{frame.arbitration_id:X} 可能报文注入"
            )
        if self.check_dlc_anomaly(frame):
            self.alerts.append(
                f"[DLC] t={frame.timestamp:.3f} ID 0x"
                f"{frame.arbitration_id:X} DLC异常 "
                f"(实际={frame.dlc})"
            )
        if self.check_frequency_anomaly(frame):
            self.alerts.append(
                f"[FLOOD] t={frame.timestamp:.3f} ID 0x"
                f"{frame.arbitration_id:X} 频率异常 可能DoS攻击"
            )
        if self.check_replay(frame):
            self.alerts.append(
                f"[REPLAY] t={frame.timestamp:.3f} ID 0x"
                f"{frame.arbitration_id:X} 可能重放攻击"
            )

    def get_alerts(self) -> list[str]:
        return self.alerts


def generate_normal_traffic(duration_s: float = 5.0) -> list[CANFrame]:
    """生成模拟正常CAN总线流量"""
    frames = []
    start = time.time()
    messages = [
        (0x100, 10,  8, "发动机"),
        (0x200, 20,  8, "车速"),
        (0x300, 50,  4, "油门"),
        (0x400, 100, 8, "刹车"),
        (0x500, 100, 4, "方向"),
    ]
    for can_id, period_ms, dlc, _ in messages:
        t = 0.0
        while t < duration_s:
            data = bytes(random.randint(0, 255) for _ in range(dlc))
            # 添加自然抖动
            jitter = random.gauss(0, 0.0005)
            frames.append(CANFrame(can_id, data, start + t + jitter))
            t += period_ms / 1000.0
    frames.sort(key=lambda f: f.timestamp)
    return frames


def generate_attack_traffic(frames: list[CANFrame]) -> list[CANFrame]:
    """在正常流量中注入攻击报文"""
    attack_frames = list(frames)
    base_time = frames[-1].timestamp if frames else time.time()

    # 攻击1：未知ID注入
    for i in range(10):
        attack_frames.append(CANFrame(
            0x7FF,  # 未注册的攻击ID
            b"\xDE\xAD\xBE\xEF\x00\x00\x00\x00",
            base_time + 1.0 + i * 0.01
        ))

    # 攻击2：DoS泛洪 - 高频发送0x100
    for i in range(200):
        attack_frames.append(CANFrame(
            0x100,
            b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF",
            base_time + 2.0 + i * 0.001
        ))

    # 攻击3：DLC异常
    attack_frames.append(CANFrame(
        0x200,  # 正常ID但DLC不对
        b"\x01\x02",  # 应该是8字节但只有2字节
        base_time + 3.0
    ))

    attack_frames.sort(key=lambda f: f.timestamp)
    return attack_frames


def main():
    print("=" * 70)
    print("T-BOX安全分析 - CAN总线入侵检测（模拟数据）")
    print("=" * 70)

    # 1. 训练基线
    print("\n[1] 采集正常流量训练基线模型...")
    baseline = CANBaseline()
    normal_frames = generate_normal_traffic(duration_s=5.0)
    for f in normal_frames:
        baseline.update(f)
    print(f"    基线训练完成: 采集 {len(normal_frames)} 帧正常数据")

    for can_id, stats in sorted(baseline.id_stats.items()):
        intervals = list(stats["intervals"])
        if intervals:
            avg_period = sum(intervals) / len(intervals)
            known = baseline.known_messages.get(can_id, {})
            desc = known.get("desc", "未知")
            print(f"    ID 0x{can_id:X} ({desc}): "
                  f"平均周期 {avg_period:.1f}ms, "
                  f"DLC={stats['dlc_values']}")

    # 2. 检测攻击
    print("\n[2] 注入攻击流量并启动IDS检测...")
    all_frames = generate_attack_traffic(normal_frames)
    ids = CANIDS(baseline)
    for f in all_frames:
        ids.analyze(f)

    # 3. 输出告警
    print(f"\n[3] 检测完成，共触发 {len(ids.get_alerts())} 条告警:\n")
    for alert in ids.get_alerts():
        print(f"  ⚠ {alert}")

    # 4. 统计
    print("\n[4] 告警类型统计:")
    type_counts = defaultdict(int)
    for alert in ids.get_alerts():
        atype = alert.split("]")[0].strip("[")
        type_counts[atype] += 1
    for atype, count in sorted(type_counts.items()):
        print(f"    {atype}: {count}次")

    print("\n" + "=" * 70)
    print("分析完成。")
    print("提示: 此脚本使用模拟数据。实际应用中应通过CAN总线接口")
    print("      (如PCAN/Vector/Kvaser)采集真实总线流量。")
    print("=" * 70)


if __name__ == "__main__":
    main()
```

### 6.2 固件特征提取脚本

```python
#!/usr/bin/env python3
"""
T-BOX固件安全分析 - 固件特征提取脚本
从固件二进制中提取安全相关特征：硬编码密钥、字符串、文件系统等
"""

import re
import struct
import hashlib
import zipfile
import io
from pathlib import Path
from typing import Optional


class FirmwareAnalyzer:
    """固件安全特征提取器"""

    # 常见文件系统魔数
    FS_MAGIC = {
        b"\x68\x73\x71\x73": "SquashFS",
        b"\x85\x19\x03\x15": "UBIFS (superblock)",
        b"\x85\x12\xU1": "JFFS2",
        b"\x1f\x8b": "GZIP压缩",
        b"\xFD7z\xBC\xAF\x27\x1C": "7-Zip压缩",
        b"PK\x03\x04": "ZIP/PKZIP/APK",
        b"\x7fELF": "ELF可执行文件",
        b"\xd0\xcf\x11\xe0": "OLE/CFC复合文件",
    }

    # 敏感字符串模式
    SENSITIVE_PATTERNS = [
        (r"https?://[^\s\x00]+", "URL/端点"),
        (r"[A-Za-z0-9+/]{40,}={0,2}", "Base64编码(可能为密钥)"),
        (r"(?:api|app|secret|key|token|password|passwd|pwd)[=:][^\s\x00]+",
         "凭据/密钥"),
        (r"\b[A-Fa-f0-9]{32}\b", "MD5哈希"),
        (r"\b[A-Fa-f0-9]{40}\b", "SHA-1哈希"),
        (r"\b[A-Fa-f0-9]{64}\b", "SHA-256哈希"),
        (r"-----BEGIN [A-Z ]+-----", "PEM证书/密钥"),
        (r"aws_access_key|AKIA[0-9A-Z]{16}", "AWS密钥"),
        (r"ghp_[A-Za-z0-9]{36}", "GitHub Token"),
        (r"mongodb://[^\s]+", "MongoDB连接串"),
        (r"mysql://[^\s]+", "MySQL连接串"),
        (r"redis://[^\s]+", "Redis连接串"),
    ]

    def __init__(self, firmware_path: str):
        self.path = Path(firmware_path)
        if not self.path.exists():
            raise FileNotFoundError(f"固件文件不存在: {firmware_path}")
        self.data = self.path.read_bytes()
        self.size = len(self.data)
        self.findings: list[str] = []

    def calculate_hashes(self) -> dict:
        """计算固件哈希"""
        return {
            "MD5": hashlib.md5(self.data).hexdigest(),
            "SHA-256": hashlib.sha256(self.data).hexdigest(),
            "SHA-512": hashlib.sha512(self.data).hexdigest(),
        }

    def identify_filesystem(self) -> list[str]:
        """识别固件中的文件系统/压缩格式"""
        results = []
        for magic, name in self.FS_MAGIC.items():
            offset = 0
            while True:
                pos = self.data.find(magic, offset)
                if pos == -1:
                    break
                results.append(f"  偏移 0x{pos:08X}: {name}")
                offset = pos + 1
                if len(results) > 50:
                    results.append("  ... (过多匹配，已截断)")
                    return results
        return results if results else ["  未识别到已知文件系统魔数"]

    def extract_strings(self, min_len: int = 6) -> list[str]:
        """提取ASCII字符串"""
        pattern = re.compile(rb"[\x20-\x7e]{" + str(min_len).encode() +
                             rb",}")
        matches = pattern.findall(self.data)
        return [m.decode("ascii", errors="ignore") for m in matches]

    def find_sensitive_data(self) -> dict[str, list[str]]:
        """搜索敏感信息"""
        strings = self.extract_strings()
        results: dict[str, list[str]] = {}
        for pattern, label in self.SENSITIVE_PATTERNS:
            found = set()
            for s in strings:
                matches = re.findall(pattern, s, re.IGNORECASE)
                found.update(matches[:20])
            if found:
                results[label] = sorted(found)[:10]
        return results

    def check_entropy(self, block_size: int = 256) -> list[tuple[int, float]]:
        """计算分块信息熵，识别加密/压缩区域"""
        import math
        high_entropy_blocks = []
        for i in range(0, self.size - block_size, block_size):
            block = self.data[i:i + block_size]
            if len(block) < block_size:
                break
            # 计算Shannon熵
            freq = {}
            for byte in block:
                freq[byte] = freq.get(byte, 0) + 1
            entropy = 0.0
            for count in freq.values():
                p = count / block_size
            for count in freq.values():
                p = count / block_size
                if p > 0:
                    entropy -= p * math.log2(p)
            # 熵>7.5可能为加密/压缩数据
            if entropy > 7.5:
                high_entropy_blocks.append((i, entropy))
        return high_entropy_blocks[:20]

    def find_certificates(self) -> list[str]:
        """查找嵌入的证书/密钥"""
        certs = []
        pem_pattern = re.compile(
            rb"-----BEGIN [A-Z ]+-----.*?-----END [A-Z ]+-----",
            re.DOTALL
        )
        for match in pem_pattern.finditer(self.data):
            cert = match.group().decode("ascii", errors="ignore")
            cert_type = "未知"
            if "RSA PRIVATE" in cert:
                cert_type = "RSA私钥"
            elif "EC PRIVATE" in cert:
                cert_type = "EC私钥"
            elif "CERTIFICATE" in cert:
                cert_type = "X.509证书"
            elif "PUBLIC" in cert:
                cert_type = "公钥"
            certs.append(
                f"  偏移 0x{match.start():08X}: {cert_type}"
            )
        return certs if certs else ["  未发现PEM格式证书/密钥"]

    def analyze(self):
        """执行完整分析"""
        print("=" * 70)
        print(f"T-BOX固件安全分析报告")
        print(f"文件: {self.path.name}")
        print(f"大小: {self.size:,} bytes ({self.size / 1024 / 1024:.2f} MB)")
        print("=" * 70)

        # 1. 哈希
        print("\n[1] 固件哈希值:")
        hashes = self.calculate_hashes()
        for algo, value in hashes.items():
            print(f"  {algo}: {value}")

        # 2. 文件系统识别
        print("\n[2] 嵌入的文件系统/压缩格式:")
        fs_results = self.identify_filesystem()
        for r in fs_results:
            print(r)

        # 3. 敏感信息
        print("\n[3] 敏感信息扫描:")
        sensitive = self.find_sensitive_data()
        if sensitive:
            for label, items in sensitive.items():
                print(f"  [{label}]")
                for item in items[:5]:
                    display = item[:80] + "..." if len(item) > 80 else item
                    print(f"    {display}")
        else:
            print("  未发现明显的敏感信息")

        # 4. 高熵区域
        print("\n[4] 高熵区域（可能为加密/压缩数据）:")
        high_entropy = self.check_entropy()
        if high_entropy:
            for offset, entropy in high_entropy[:10]:
                print(f"  偏移 0x{offset:08X}: 熵={entropy:.2f}")
        else:
            print("  未发现明显的高熵区域")

        # 5. 证书/密钥
        print("\n[5] 嵌入的证书/密钥:")
        certs = self.find_certificates()
        for c in certs:
            print(c)

        # 6. 安全评估
        print("\n[6] 安全评估:")
        risk_items = []
        if sensitive:
            risk_items.append("发现硬编码敏感信息（凭据/密钥/URL）")
        if certs:
            risk_items.append("发现嵌入的证书/私钥")
        if high_entropy:
            risk_items.append("发现高熵区域（可能含加密数据或打包固件）")
        if risk_items:
            print("  ⚠ 发现以下安全风险:")
            for item in risk_items:
                print(f"    - {item}")
        else:
            print("  基本扫描未发现明显风险")
        print("\n  建议:")
        print("  - 使用Binwalk进一步提取文件系统并逐文件分析")
        print("  - 使用Ghidra/IDA Pro反汇编关键二进制")
        print("  - 检查固件更新机制是否包含签名验证")
        print("  - 确认调试接口（JTAG/UART）是否在固件中启用")

        print("\n" + "=" * 70)
        print("分析完成。")
        print("=" * 70)


def create_sample_firmware() -> bytes:
    """创建模拟固件二进制数据用于演示"""
    data = bytearray()

    # Bootloader头
    data += b"\x7fELF"  # ELF魔数
    data += b"\x01\x01\x01\x00"  # 32位小端
    data += b"\x00" * 56  # 填充

    # 模拟硬编码敏感信息
    data += b"\x00" * 64
    data += b"api_key=AKID1234567890abcdef\x00"
    data += b"https://tsp.example.com/api/v1/vehicle/control\x00"
    data += b"password=P@ssw0rd123\x00"
    data += b"token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    data += b"eyJzdWIiOiIxMjM0NTY3ODkwIn0.\x00"

    # 嵌入PEM证书
    data += b"\x00" * 32
    data += b"-----BEGIN RSA PRIVATE KEY-----\n"
    data += b"MIIEpAIBAAKCAQEA0e8a1tR3l5QmP2vKx9bT4nWcZ7yH3aRfB6uM1sQ8vLp\n"
    data += b"-----END RSA PRIVATE KEY-----\n"

    # 模拟SquashFS文件系统
    data += b"\x00" * 64
    data += b"\x68\x73\x71\x73"  # SquashFS魔数
    data += b"\x00" * 60

    # 模拟高熵加密区域
    import random
    random.seed(42)
    data += bytes(random.randint(0, 255) for _ in range(512))

    # 模拟配置数据
    data += b"\x00" * 32
    data += b"ssid=VehicleHotspot\x00"
    data += b"redis://10.0.0.1:6379/0\x00"

    return bytes(data)


def main():
    print("T-BOX固件安全分析工具（使用模拟固件数据）")
    print()

    # 创建模拟固件文件
    sample_path = "sample_tbox_firmware.bin"
    firmware_data = create_sample_firmware()
    Path(sample_path).write_bytes(firmware_data)
    print(f"已创建模拟固件文件: {sample_path} ({len(firmware_data)} bytes)\n")

    # 执行分析
    try:
        analyzer = FirmwareAnalyzer(sample_path)
        analyzer.analyze()
    finally:
        # 清理
        Path(sample_path).unlink(missing_ok=True)
        print("(模拟固件文件已清理)")


if __name__ == "__main__":
    main()
```

---

---

## 📋 内容审核与补充建议

> 针对「Python T-BOX安全分析脚本示例」部分的内容审核结果：

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
