# V2X安全威胁分析

### 4.1 消息伪造攻击

**攻击原理：** 攻击者伪造虚假的BSM消息，声称自己是一辆位于其他位置的车辆，误导其他车辆的决策。

```text
消息伪造攻击场景

攻击前（正常交通流）：
    车辆A ◄────► 车辆B
    (正常V2V通信)

攻击中（伪造车辆）：
    攻击者 ──伪造BSM──► 车辆A
    "我在你前方100米，正在急刹车"
    
    车辆A收到伪造消息后急刹车 → 可能被后方追尾

攻击者 ──伪造BSM──► 车辆B
    "前方路口信号灯为绿灯（实际为红灯）"

    车辆B不减速通过路口 → 可能导致碰撞
```

**防御机制：**

```python
class MessageForgeryDetector:
    """V2X消息伪造检测器"""

    def __init__(self):
        self.vehicle_history = {}  # 车辆ID → 历史状态
        self.trusted_certificates = set()  # 可信证书集合
        self.revoked_certificates = set()  # 已撤销证书集合
        self.misbehavior_reports = []

    def check_message(self, signed_message, receiver_location):
        """
        检查收到的V2X消息是否为伪造
        :param signed_message: 签名的V2X消息
        :param receiver_location: 接收者位置
        :return: 检查结果
        """
        # 1. 签名验证
        if not self._verify_signature(signed_message):
            return {
                "valid": False,
                "threat": "签名验证失败 - 可能是伪造消息",
                "action": "丢弃消息"
            }

        # 2. 证书验证
        cert = signed_message['signed_data']['signer_info']['certificates'][0]
        pseudonym_cert = PseudonymCertificate.decode(cert)

        if pseudonym_cert.cert_id in self.revoked_certificates:
            return {
                "valid": False,
                "threat": "证书已被撤销",
                "action": "丢弃消息并报告"
            }

        # 3. 物理合理性检查
        bsm_data = self._extract_bsm(signed_message)
        vehicle_id = bsm_data['temporary_id']

        if vehicle_id in self.vehicle_history:
            history = self.vehicle_history[vehicle_id]

            # 检查位置跳变
            if self._check_position_jump(bsm_data, history):
                return {
                    "valid": False,
                    "threat": "位置跳变异常 - 可能是伪造",
                    "action": "丢弃消息并报告"
                }

            # 检查速度合理性
            if self._check_speed_anomaly(bsm_data, history):
                return {
                    "valid": False,
                    "threat": "速度变化异常 - 可能是伪造",
                    "action": "丢弃消息"
                }

            # 检查通信距离合理性
            if self._check_communication_range(bsm_data, receiver_location):
                return {
                    "valid": False,
                    "threat": "通信距离超出合理范围",
                    "action": "丢弃消息"
                }

        # 4. 更新历史记录
        self.vehicle_history[vehicle_id] = {
            'latitude': bsm_data['latitude'],
            'longitude': bsm_data['longitude'],
            'speed': bsm_data['speed'],
            'heading': bsm_data['heading'],
            'timestamp': bsm_data['timestamp']
        }

        return {"valid": True, "action": "接受消息"}

    def _check_position_jump(self, bsm_data, history):
        """检查位置是否不合理跳变"""
        time_diff = bsm_data['timestamp'] - history['timestamp']
        if time_diff <= 0:
            return True

        # 计算位置变化
        lat_diff = abs(bsm_data['latitude'] - history['latitude']) / 1e7
        lon_diff = abs(bsm_data['longitude'] - history['longitude']) / 1e7

        # 转换为距离（近似）
        distance = (lat_diff * 111000 + lon_diff * 111000 *
                    math.cos(math.radians(bsm_data['latitude'] / 1e7)))

        # 计算最大合理距离
        speed = history['speed'] * 0.02  # 转换为m/s
        max_distance = speed * time_diff + 50  # 允许50米误差

        return distance > max_distance

    def _check_speed_anomaly(self, bsm_data, history):
        """检查速度变化是否合理"""
        time_diff = bsm_data['timestamp'] - history['timestamp']
        if time_diff <= 0:
            return False

        speed_diff = abs(bsm_data['speed'] - history['speed']) * 0.02
        max_accel = 10.0  # 最大合理加速度10 m/s^2

        return speed_diff / time_diff > max_accel

    def _check_communication_range(self, bsm_data, receiver_location):
        """检查发送者是否在合理通信距离内"""
        lat1 = bsm_data['latitude'] / 1e7
        lon1 = bsm_data['longitude'] / 1e7
        lat2 = receiver_location['latitude']
        lon2 = receiver_location['longitude']

        # Haversine公式计算距离
        distance = self._haversine(lat1, lon1, lat2, lon2)

        # DSRC/C-V2X合理通信距离约1000米
        return distance > 1500

    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2):
        """计算两点间球面距离"""
        R = 6371000  # 地球半径（米）
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = (math.sin(delta_phi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c
```

### 4.2 消息篡改攻击

**攻击原理：** 攻击者截获合法的V2X消息，修改消息内容后重新发送。

```text
消息篡改攻击流程

正常流程：
车辆A ──BSM(速度=60km/h)──► 车辆B

篡改攻击：
车辆A ──BSM(速度=60km/h)──► 攻击者
攻击者 ──BSM(速度=0km/h)──► 车辆B
        ↑篡改速度信息

车辆B认为A已停车 → 急刹车 → 追尾风险
```

**防御机制：数字签名**

```text
数字签名防篡改机制：

发送方：
1. 构建BSM消息体
2. 用私钥对消息签名
3. 发送 [BSM消息体 + 签名 + 证书]

接收方：
1. 验证证书链
2. 用证书中的公钥验证签名
3. 如果签名验证通过 → 消息未被篡改
4. 如果签名验证失败 → 消息被篡改，丢弃

攻击者即使截获消息也无法篡改：
- 修改消息体 → 签名验证失败
- 修改签名 → 签名验证失败
- 替换消息体+签名 → 需要合法私钥，无法获取
```

### 4.3 重放攻击

**攻击原理：** 攻击者截获合法的V2X消息后，在稍后时间重新发送该消息。

```text
重放攻击场景

T=10:00 车辆A发送BSM："前方道路湿滑，注意减速"
        ↓
T=10:01 攻击者截获该消息
        ↓
T=10:30 攻击者重放该消息 → 前方道路已经干燥
        车辆B收到过时警告 → 不必要的减速 → 影响交通
```

**防御机制：**

```python
class ReplayAttackDefense:
    """重放攻击防御"""

    def __init__(self, time_window_ms=2000):
        """
        :param time_window_ms: 消息时间窗口（毫秒）
        """
        self.time_window = time_window_ms
        self.received_messages = {}  # 消息哈希 → 接收时间
        self.largest_timestamp = {}  # 车辆ID → 最大时间戳

    def check_replay(self, signed_message, current_time_ms):
        """
        检查消息是否为重放
        :param signed_message: 签名消息
        :param current_time_ms: 当前时间（毫秒）
        :return: 检查结果
        """
        # 1. 检查时间戳新鲜性
        generation_time = signed_message['signed_data']['generation_time']

        if current_time_ms - generation_time > self.time_window:
            return {
                "valid": False,
                "reason": f"消息过期: 生成于{generation_time}, 当前{current_time_ms}"
            }

        if generation_time > current_time_ms + 100:  # 允许100ms时钟偏差
            return {
                "valid": False,
                "reason": "消息时间戳超前于当前时间"
            }

        # 2. 检查消息唯一性
        message_hash = hashlib.sha256(
            str(signed_message).encode()
        ).hexdigest()

        if message_hash in self.received_messages:
            return {
                "valid": False,
                "reason": "消息已被接收过（重放）"
            }

        # 3. 检查时间戳单调性（针对同一发送者）
        bsm_data = self._extract_bsm(signed_message)
        vehicle_id = bsm_data['temporary_id']

        if vehicle_id in self.largest_timestamp:
            if generation_time <= self.largest_timestamp[vehicle_id]:
                return {
                    "valid": False,
                    "reason": "时间戳不满足单调递增（重放）"
                }

        # 4. 更新状态
        self.received_messages[message_hash] = current_time_ms
        self.largest_timestamp[vehicle_id] = generation_time

        # 5. 清理过期记录
        self._cleanup_expired(current_time_ms)

        return {"valid": True}

    def _cleanup_expired(self, current_time_ms):
        """清理过期的消息缓存"""
        expired = [
            h for h, t in self.received_messages.items()
            if current_time_ms - t > self.time_window * 2
        ]
        for h in expired:
            del self.received_messages[h]

    def _extract_bsm(self, signed_message):
        """从签名消息中提取BSM数据"""
        return {
            "temporary_id": signed_message.get('temporary_id', 'unknown'),
            "timestamp": signed_message['signed_data']['generation_time']
        }
```

### 4.4 拒绝服务攻击

**攻击原理：** 攻击者通过大量发送无意义的V2X消息或干扰通信信道，使合法车辆的V2V通信不可用。

```text
V2X DoS攻击类型

1. 消息泛洪攻击：
   攻击者以极高频率发送BSM消息
   → 接收方处理队列溢出
   → 合法消息被丢弃

2. 信道干扰攻击：
   攻击者在5.9GHz频段发射干扰信号
   → 通信质量下降
   → 消息丢失率上升

3. 资源耗尽攻击：
   攻击者发送大量需要证书验证的消息
   → 接收方CPU资源耗尽
   → 无法处理正常消息

4. 拥塞窗口攻击：
   利用CSMA/CA机制的弱点
   → 信道始终繁忙
   → 合法车辆无法发送消息
```

**防御机制：**

| 防御策略 | 说明 | 实现方式 |
|---------|------|---------|
| 消息限速 | 限制每秒接收的消息数量 | 基于发送者ID的令牌桶 |
| 优先级队列 | 安全关键消息优先处理 | QoS分级机制 |
| 证书白名单 | 仅处理可信证书的消息 | 预加载证书列表 |
| 异常检测 | 检测异常消息模式 | 基于统计的异常检测 |
| 多信道冗余 | 使用多个通信信道 | DSRC + C-V2X双模 |
| 计算卸载 | 将证书验证卸载到硬件 | 硬件安全模块（HSM） |

### 4.5 女巫攻击

**Sybil Attack（女巫攻击）** 是指攻击者伪造大量虚假身份，在V2X网络中冒充多辆不存在的车辆。

```text
女巫攻击场景

正常场景：
  车辆A  车辆B  车辆C  车辆D
   ◄────► ◄────► ◄────►
  (4辆真实车辆正常通信)

女巫攻击：
                      ┌── 伪造车辆E
  攻击者 ────┬────────┼── 伪造车辆F
            │        ├── 伪造车辆G
            │        └── 伪造车辆H
            │
  实际只有攻击者1辆车，但伪造了4辆虚拟车辆

后果：
- 接收方认为有多辆车在周围
- 交通密度估计错误
- 可能触发不必要的避让行为
- 干扰协作式驾驶决策
```

**Sybil攻击检测技术：**

```python
import math
from collections import defaultdict
from datetime import datetime

class SybilAttackDetector:
    """Sybil攻击检测器"""

    def __init__(self):
        # 车辆ID → 消息历史记录
        self.message_history = defaultdict(list)
        # 位置 → 出现的车辆ID集合
        self.location_map = defaultdict(set)
        # 证书 → 车辆ID集合（检测证书复用）
        self.cert_to_vehicles = defaultdict(set)

    def analyze_messages(self, messages_batch, detection_window_ms=5000):
        """
        分析一批V2X消息，检测Sybil攻击
        :param messages_batch: 一批V2X消息
        :param detection_window_ms: 检测时间窗口
        :return: 检测结果
        """
        suspicious_groups = []

        # 1. 基于位置聚类的检测
        location_clusters = self._cluster_by_location(messages_batch)
        for cluster in location_clusters:
            if len(cluster) > 5:  # 5辆以上车辆聚集在同一小范围
                suspicious_groups.append({
                    "type": "位置聚类异常",
                    "vehicle_ids": cluster,
                    "reason": f"{len(cluster)}辆车辆在极小范围内同时出现"
                })

        # 2. 基于行为模式的检测
        behavior_groups = self._detect_behavior_similarity(messages_batch)
        for group in behavior_groups:
            if len(group['vehicle_ids']) > 2:
                suspicious_groups.append({
                    "type": "行为模式相似",
                    "vehicle_ids": group['vehicle_ids'],
                    "reason": f"多辆车辆具有相同的运动模式(速度/方向)"
                })

        # 3. 基于证书的检测
        cert_groups = self._detect_certificate_reuse(messages_batch)
        for group in cert_groups:
            suspicious_groups.append({
                "type": "证书复用",
                "vehicle_ids": group,
                "reason": "多个车辆ID使用同一证书"
            })

        # 4. 基于RF指纹的检测
        rf_groups = self._detect_rf_fingerprint(messages_batch)
        for group in rf_groups:
            suspicious_groups.append({
                "type": "RF指纹相同",
                "vehicle_ids": group,
                "reason": "多个车辆ID具有相同的射频指纹"
            })

        return {
            "sybil_detected": len(suspicious_groups) > 0,
            "suspicious_groups": suspicious_groups,
            "analysis_time": datetime.now().isoformat()
        }

    def _cluster_by_location(self, messages):
        """基于位置的聚类检测"""
        locations = []
        for msg in messages:
            loc = (msg['latitude'] / 1e7, msg['longitude'] / 1e7)
            locations.append((msg['temporary_id'], loc))

        clusters = []
        visited = set()

        for i, (vid_i, loc_i) in enumerate(locations):
            if vid_i in visited:
                continue
            cluster = [vid_i]
            visited.add(vid_i)

            for j, (vid_j, loc_j) in enumerate(locations[i + 1:], i + 1):
                if vid_j in visited:
                    continue
                distance = self._haversine(loc_i[0], loc_i[1],
                                           loc_j[0], loc_j[1])
                if distance < 5.0:  # 5米以内视为同一位置
                    cluster.append(vid_j)
                    visited.add(vid_j)

            if len(cluster) > 1:
                clusters.append(cluster)

        return clusters

    def _detect_behavior_similarity(self, messages):
        """检测行为模式相似性"""
        vehicle_behaviors = defaultdict(list)
        for msg in messages:
            vid = msg['temporary_id']
            behavior = (
                msg['speed'],
                msg['heading'],
                msg.get('acceleration', {}).get('longitudinal', 0)
            )
            vehicle_behaviors[vid].append(behavior)

        # 检测具有完全相同行为模式的车辆
        behavior_groups = []
        pattern_map = defaultdict(list)

        for vid, behaviors in vehicle_behaviors.items():
            # 将行为序列转为可哈希的元组
            pattern = tuple(tuple(b) for b in behaviors)
            pattern_map[pattern].append(vid)

        for pattern, vids in pattern_map.items():
            if len(vids) > 1:
                behavior_groups.append({
                    "vehicle_ids": vids,
                    "pattern": pattern
                })

        return behavior_groups

    def _detect_certificate_reuse(self, messages):
        """检测证书复用"""
        for msg in messages:
            cert_id = msg.get('certificate_id', 'unknown')
            vid = msg['temporary_id']
            self.cert_to_vehicles[cert_id].add(vid)

        groups = []
        for cert_id, vids in self.cert_to_vehicles.items():
            if len(vids) > 1:
                groups.append(list(vids))

        return groups

    def _detect_rf_fingerprint(self, messages):
        """基于RF指纹的检测（简化版）"""
        # 实际实现需要提取物理层特征
        # 如载波频率偏移、I/Q不平衡等
        rf_map = defaultdict(list)

        for msg in messages:
            rf_fp = msg.get('rf_fingerprint', 'unknown')
            vid = msg['temporary_id']
            rf_map[rf_fp].append(vid)

        groups = []
        for rf_fp, vids in rf_map.items():
            if len(vids) > 1:
                groups.append(list(vids))

        return groups

    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2):
        R = 6371000
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)
        a = (math.sin(dphi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
```

---

---

