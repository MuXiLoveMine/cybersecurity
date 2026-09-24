# Python DDoS检测脚本示例

### 5.1 流量异常检测脚本

```python
"""
DDoS流量异常检测脚本 - 模拟教育版
功能：基于流量基线模型，检测带宽和包速率异常突增。
注意：使用模拟流量数据，不执行真实网络抓包。
"""

import statistics
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple


@dataclass
class TrafficSample:
    """流量采样数据点"""
    timestamp: str
    bandwidth_mbps: float    # 带宽 Mbps
    packets_per_sec: int     # 每秒包数
    syn_packets: int         # SYN包数
    udp_packets: int         # UDP包数


class TrafficBaseline:
    """流量基线模型"""

    def __init__(self, history_data: List[TrafficSample]):
        self.bw_mean = statistics.mean([s.bandwidth_mbps for s in history_data])
        self.bw_stdev = statistics.stdev([s.bandwidth_mbps for s in history_data])
        self.pps_mean = statistics.mean([s.packets_per_sec for s in history_data])
        self.pps_stdev = statistics.stdev([s.packets_per_sec for s in history_data])

    def is_anomalous(self, sample: TrafficSample,
                     threshold_sigma: float = 3.0) -> Tuple[bool, str]:
        """判断单个采样点是否异常"""
        reasons = []

        # 带宽异常检测（超过 mean + 3*stdev）
        if self.bw_stdev > 0:
            bw_zscore = (sample.bandwidth_mbps - self.bw_mean) / self.bw_stdev
            if bw_zscore > threshold_sigma:
                reasons.append(
                    f"带宽异常: {sample.bandwidth_mbps:.1f}Mbps "
                    f"(基线均值={self.bw_mean:.1f}Mbps, "
                    f"偏离={bw_zscore:.1f}σ)"
                )

        # 包速率异常检测
        if self.pps_stdev > 0:
            pps_zscore = (sample.packets_per_sec - self.pps_mean) / self.pps_stdev
            if pps_zscore > threshold_sigma:
                reasons.append(
                    f"包速率异常: {sample.packets_per_sec}pps "
                    f"(基线均值={self.pps_mean:.0f}pps, "
                    f"偏离={pps_zscore:.1f}σ)"
                )

        # SYN包占比异常检测
        if sample.packets_per_sec > 0:
            syn_ratio = sample.syn_packets / sample.packets_per_sec
            if syn_ratio > 0.3:  # SYN占比超过30%
                reasons.append(
                    f"SYN占比异常: {syn_ratio*100:.1f}% "
                    f"(SYN={sample.syn_packets}/{sample.packets_per_sec})"
                )

        # UDP包占比异常
        if sample.packets_per_sec > 0:
            udp_ratio = sample.udp_packets / sample.packets_per_sec
            if udp_ratio > 0.5:  # UDP占比超过50%
                reasons.append(
                    f"UDP占比异常: {udp_ratio*100:.1f}% "
                    f"(UDP={sample.udp_packets}/{sample.packets_per_sec})"
                )

        if reasons:
            return True, "; ".join(reasons)
        return False, "正常"


def main():
    """主函数 - 模拟DDoS检测"""
    # === 构建历史正常流量数据（7天基线）===
    import random
    random.seed(42)
    history = []
    for i in range(168):  # 7天 * 24小时
        bw = random.gauss(500, 50)   # 正常带宽 500±50 Mbps
        pps = random.gauss(5000, 800)  # 正常包速率 5000±800 pps
        syn = random.gauss(100, 30)  # 正常SYN约100/s
        udp = random.gauss(500, 100)  # 正常UDP约500/s
        history.append(TrafficSample(
            timestamp=f"2026-09-{5+i//24:02d} {i%24:02d}:00",
            bandwidth_mbps=max(0, bw),
            packets_per_sec=max(0, int(pps)),
            syn_packets=max(0, int(syn)),
            udp_packets=max(0, int(udp)),
        ))

    baseline = TrafficBaseline(history)
    print("=" * 70)
    print("流量基线模型:")
    print(f"  带宽:   {baseline.bw_mean:.1f} ± {baseline.bw_stdev:.1f} Mbps")
    print(f"  包速率: {baseline.pps_mean:.0f} ± {baseline.pps_stdev:.0f} pps")
    print("=" * 70)

    # === 场景1: 正常流量 ===
    print("\n--- 场景1: 正常流量 ---")
    normal_sample = TrafficSample(
        timestamp="2026-09-12 10:00",
        bandwidth_mbps=520, packets_per_sec=5100,
        syn_packets=105, udp_packets=480
    )
    is_anomaly, reason = baseline.is_anomalous(normal_sample)
    print(f"  时间: {normal_sample.timestamp}")
    print(f"  带宽: {normal_sample.bandwidth_mbps}Mbps, PPS: {normal_sample.packets_per_sec}")
    print(f"  结果: {'异常!' if is_anomaly else '正常'} - {reason}")

    # === 场景2: SYN Flood攻击 ===
    print("\n--- 场景2: SYN Flood攻击 ---")
    syn_flood_sample = TrafficSample(
        timestamp="2026-09-12 14:00",
        bandwidth_mbps=3000,   # 带宽突增6倍
        packets_per_sec=50000, # 包速率突增10倍
        syn_packets=35000,     # SYN占比70%
        udp_packets=200
    )
    is_anomaly, reason = baseline.is_anomalous(syn_flood_sample)
    print(f"  时间: {syn_flood_sample.timestamp}")
    print(f"  带宽: {syn_flood_sample.bandwidth_mbps}Mbps, PPS: {syn_flood_sample.packets_per_sec}")
    print(f"  SYN: {syn_flood_sample.syn_packets}")
    print(f"  结果: {'异常!' if is_anomaly else '正常'}")
    if is_anomaly:
        print(f"  告警: {reason}")

    # === 场景3: UDP Flood/放大攻击 ===
    print("\n--- 场景3: UDP Flood/Amplification攻击 ---")
    udp_flood_sample = TrafficSample(
        timestamp="2026-09-12 16:00",
        bandwidth_mbps=8000,   # 带宽突增16倍
        packets_per_sec=30000,
        syn_packets=50,
        udp_packets=25000     # UDP占比83%
    )
    is_anomaly, reason = baseline.is_anomalous(udp_flood_sample)
    print(f"  时间: {udp_flood_sample.timestamp}")
    print(f"  带宽: {udp_flood_sample.bandwidth_mbps}Mbps, PPS: {udp_flood_sample.packets_per_sec}")
    print(f"  UDP: {udp_flood_sample.udp_packets}")
    print(f"  结果: {'异常!' if is_anomaly else '正常'}")
    if is_anomaly:
        print(f"  告警: {reason}")

    # === 场景4: HTTP Flood/CC攻击 ===
    print("\n--- 场景4: HTTP Flood/CC攻击 ---")
    cc_sample = TrafficSample(
        timestamp="2026-09-12 18:00",
        bandwidth_mbps=600,    # 带宽仅略增
        packets_per_sec=15000, # 但包速率突增3倍
        syn_packets=200,      # SYN不多
        udp_packets=300
    )
    is_anomaly, reason = baseline.is_anomalous(cc_sample)
    print(f"  时间: {cc_sample.timestamp}")
    print(f"  带宽: {cc_sample.bandwidth_mbps}Mbps, PPS: {cc_sample.packets_per_sec}")
    print(f"  结果: {'异常!' if is_anomaly else '正常'}")
    if is_anomaly:
        print(f"  告警: {reason}")
    else:
        print("  提示: CC攻击可能带宽增幅小，需结合应用层指标(L7 QPS)检测")


if __name__ == "__main__":
    main()
```

### 5.2 SYN Flood检测脚本

```python
"""
SYN Flood检测脚本 - 模拟教育版
功能：监控TCP半连接(SYN_RECV)数量与比例，检测SYN Flood攻击。
注意：使用模拟连接数据，不执行真实系统命令。
"""

from dataclasses import dataclass
from collections import Counter
from typing import List, Dict


@dataclass
class TCPConnection:
    """TCP连接状态"""
    local_ip: str
    local_port: int
    remote_ip: str
    remote_port: int
    state: str  # ESTABLISHED, SYN-RECV, TIME-WAIT, etc.


class SYNFloodDetector:
    """SYN Flood检测器"""

    def __init__(self, syn_threshold: int = 1000,
                 syn_ratio_threshold: float = 0.3,
                 per_ip_threshold: int = 100):
        self.syn_threshold = syn_threshold
        self.syn_ratio_threshold = syn_ratio_threshold
        self.per_ip_threshold = per_ip_threshold

    def analyze(self, connections: List[TCPConnection]) -> Dict:
        """分析连接列表，检测SYN Flood"""
        result = {
            "total_connections": len(connections),
            "syn_recv_count": 0,
            "established_count": 0,
            "syn_ratio": 0.0,
            "top_syn_sources": [],
            "is_syn_flood": False,
            "alerts": []
        }

        # 统计各状态连接数
        state_counts = Counter()
        syn_sources = Counter()

        for conn in connections:
            state_counts[conn.state] += 1
            if conn.state == "SYN-RECV":
                result["syn_recv_count"] += 1
                syn_sources[conn.remote_ip] += 1
            elif conn.state == "ESTABLISHED":
                result["established_count"] += 1

        total = len(connections)
        result["syn_ratio"] = (
            result["syn_recv_count"] / total if total > 0 else 0
        )
        result["top_syn_sources"] = syn_sources.most_common(10)

        # 检测条件1: SYN-RECV总数超过阈值
        if result["syn_recv_count"] > self.syn_threshold:
            result["is_syn_flood"] = True
            result["alerts"].append(
                f"SYN-RECV总数异常: {result['syn_recv_count']} "
                f"(阈值={self.syn_threshold})"
            )

        # 检测条件2: SYN占比超过阈值
        if result["syn_ratio"] > self.syn_ratio_threshold:
            result["is_syn_flood"] = True
            result["alerts"].append(
                f"SYN占比异常: {result['syn_ratio']*100:.1f}% "
                f"(阈值={self.syn_ratio_threshold*100:.0f}%)"
            )

        # 检测条件3: 单IP SYN-RECV连接数过多
        for ip, count in result["top_syn_sources"]:
            if count > self.per_ip_threshold:
                result["is_syn_flood"] = True
                result["alerts"].append(
                    f"单IP异常: {ip} 有 {count} 个SYN-RECV连接 "
                    f"(阈值={self.per_ip_threshold})"
                )

        return result


def generate_normal_connections(n: int = 500) -> List[TCPConnection]:
    """生成模拟正常连接"""
    import random
    random.seed(100)
    conns = []
    states_weighted = (
        ["ESTABLISHED"] * 60 +
        ["TIME-WAIT"] * 25 +
        ["SYN-RECV"] * 5 +
        ["CLOSE-WAIT"] * 5 +
        ["FIN-WAIT"] * 5
    )
    for _ in range(n):
        ip = f"192.168.1.{random.randint(1, 254)}"
        conns.append(TCPConnection(
            local_ip="10.0.0.1", local_port=443,
            remote_ip=ip, remote_port=random.randint(1024, 65535),
            state=random.choice(states_weighted)
        ))
    return conns


def generate_syn_flood_connections(n: int = 2000) -> List[TCPConnection]:
    """生成模拟SYN Flood连接"""
    import random
    random.seed(200)
    conns = []
    # 80%为SYN-RECV（伪造IP），20%为正常连接
    for i in range(n):
        if i < n * 0.8:
            # 伪造源IP（随机生成）
            ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}."
            ip += f"{random.randint(0, 255)}.{random.randint(1, 254)}"
            conns.append(TCPConnection(
                local_ip="10.0.0.1", local_port=443,
                remote_ip=ip, remote_port=random.randint(1024, 65535),
                state="SYN-RECV"
            ))
        else:
            ip = f"192.168.1.{random.randint(1, 254)}"
            conns.append(TCPConnection(
                local_ip="10.0.0.1", local_port=443,
                remote_ip=ip, remote_port=random.randint(1024, 65535),
                state="ESTABLISHED"
            ))
    return conns


def main():
    """主函数 - 模拟SYN Flood检测"""
    detector = SYNFloodDetector(
        syn_threshold=1000,
        syn_ratio_threshold=0.3,
        per_ip_threshold=100
    )

    # === 场景1: 正常连接 ===
    print("=" * 70)
    print("场景1: 正常TCP连接状态")
    print("=" * 70)
    normal_conns = generate_normal_connections(500)
    result = detector.analyze(normal_conns)
    print(f"  总连接数: {result['total_connections']}")
    print(f"  SYN-RECV: {result['syn_recv_count']}")
    print(f"  ESTABLISHED: {result['established_count']}")
    print(f"  SYN占比: {result['syn_ratio']*100:.1f}%")
    print(f"  结果: {'检测到SYN Flood!' if result['is_syn_flood'] else '正常，未检测到SYN Flood。'}")

    # === 场景2: SYN Flood攻击 ===
    print("\n" + "=" * 70)
    print("场景2: SYN Flood攻击")
    print("=" * 70)
    flood_conns = generate_syn_flood_connections(2000)
    result = detector.analyze(flood_conns)
    print(f"  总连接数: {result['total_connections']}")
    print(f"  SYN-RECV: {result['syn_recv_count']}")
    print(f"  ESTABLISHED: {result['established_count']}")
    print(f"  SYN占比: {result['syn_ratio']*100:.1f}%")
    print(f"  结果: {'检测到SYN Flood!' if result['is_syn_flood'] else '正常'}")
    if result["is_syn_flood"]:
        print(f"\n  告警列表:")
        for alert in result["alerts"]:
            print(f"    [ALERT] {alert}")
        print(f"\n  SYN-RECV最多的源IP (前5):")
        for ip, count in result["top_syn_sources"][:5]:
            print(f"    {ip}: {count} 个半连接")


if __name__ == "__main__":
    main()
```

---

---

