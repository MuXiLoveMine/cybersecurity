# Eclipse攻击实施分析

### 9.1 Eclipse攻击详细步骤

```
Eclipse攻击实施流程(以比特币为例):

Phase 1: 准备阶段
  ├── 创建大量节点/IP
  ├── 获取目标节点的出站连接IP
  │   ├── 通过网络监听
  │   ├── 通过节点的addr消息
  │   └── 通过DNS种子记录
  └── 准备替代地址表

Phase 2: 地址表污染
  ├── 向目标节点发送大量addr消息
  │   ├── 每条消息包含攻击者IP
  │   └── 持续发送直到地址表被污染
  ├── 等待目标节点重启
  │   ├── 地址表持久化到onion_peer.dat
  │   └── 重启后使用被污染的地址表
  └── 也可通过DDoS迫使目标重启

Phase 3: 连接劫持
  ├── 目标重启后尝试出站连接
  ├── 所有候选IP都是攻击者IP
  ├── 目标连接到攻击者节点
  └── 攻击者拒绝其他节点入站连接

Phase 4: 隔离与利用
  ├── 目标完全被隔离
  ├── 攻击者控制目标所见的信息
  │   ├── 发送虚假区块
  │   ├── 发送虚假交易
  │   └── 0确认双花
  ├── 矿工:浪费算力在旧链上
  └── 交易所:显示虚假余额

攻击参数:
  比特币节点默认出站连接数: 8
  需要污染的地址数: 数百
  地址表大小: ~10000
  污染成功率: 需要覆盖>50%的地址表
```

### 9.2 Eclipse攻击防御实现

```python
# Eclipse攻击防御策略实现

class EclipseDefense:
    """节点级Eclipse攻击防御"""

    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.anchor_connections = set()  # 锚定连接
        self.address_table = AddressTable()
        self.outbound_count = 8

    def select_outbound_peers(self):
        """防御性出站连接选择"""
        selected = []

        # 1. 优先使用锚定连接(长期稳定的可信节点)
        for addr in self.anchor_connections:
            if len(selected) < 2:  # 至少2个锚定连接
                selected.append(addr)

        # 2. 随机选择(避免确定性选择被预测)
        candidates = self.address_table.get_random(self.outbound_count * 3)
        import random
        random.shuffle(candidates)

        for addr in candidates:
            if len(selected) >= self.outbound_count:
                break
            if self._is_diverse_enough(addr, selected):
                selected.append(addr)

        # 3. DNS种子兜底(当地址表不足时)
        if len(selected) < self.outbound_count:
            dns_seeds = self._get_dns_seeds()
            for addr in dns_seeds:
                if len(selected) >= self.outbound_count:
                    break
                if addr not in selected:
                    selected.append(addr)

        return selected

    def _is_diverse_enough(self, addr, selected):
        """确保连接的多样性(不同IP段/ASN)"""
        addr_asn = get_asn(addr)
        selected_asns = [get_asn(s) for s in selected]
        # 同一ASN不超过2个连接
        if selected_asns.count(addr_asn) >= 2:
            return False
        # 同一/24子网不超过1个连接
        addr_subnet = '.'.join(addr.split('.')[:3])
        for s in selected:
            if '.'.join(s.split('.')[:3]) == addr_subnet:
                return False
        return True

    def validate_connection(self, peer_info):
        """验证连接的有效性"""
        # 1. 检查提供的区块是否与已知一致
        if not self._verify_chain_consistency(peer_info):
            return False

        # 2. 检查网络延迟是否异常
        latency = self.connection_manager.get_latency(peer_info)
        if latency > 5000:  # 5秒以上延迟异常
            return False

        # 3. 检查是否所有连接都指向同一ASN
        all_asns = [get_asn(p) for p in self.connection_manager.get_outbound_peers()]
        if len(set(all_asns)) == 1 and len(all_asns) > 2:
            # 所有连接在同一ASN，疑似被日蚀
            return False

        return True

    def periodic_anchor_check(self):
        """定期验证锚定连接"""
        for addr in list(self.anchor_connections):
            if not self._verify_peer_alive(addr):
                self.anchor_connections.discard(addr)
                # 从新连接中选出稳定的作为新锚
                self._promote_to_anchor()

    def detect_eclipse(self):
        """检测是否被日蚀"""
        indicators = 0

        # 所有出站连接在同一子网
        peers = self.connection_manager.get_outbound_peers()
        subnets = set('.'.join(p.split('.')[:3]) for p in peers)
        if len(subnets) == 1:
            indicators += 3

        # 所有连接延迟相似(可能通过同一中继)
        latencies = [self.connection_manager.get_latency(p) for p in peers]
        if max(latencies) - min(latencies) < 10:  # 延迟过于均匀
            indicators += 2

        # 接收到的区块时间戳异常
        recent_blocks = self.connection_manager.get_recent_blocks()
        if recent_blocks:
            avg_time = sum(b['timestamp'] for b in recent_blocks) / len(recent_blocks)
            expected_time = time.time()
            if abs(avg_time - expected_time) > 3600:  # 偏差1小时
                indicators += 2

        # 无法连接到新的外部节点
        test_addrs = self._get_test_addresses()
        connected = sum(
            1 for a in test_addrs
            if self.connection_manager.try_connect(a, timeout=5)
        )
        if connected == 0:
            indicators += 3

        if indicators >= 5:
            return True
        return False
```

---

---

