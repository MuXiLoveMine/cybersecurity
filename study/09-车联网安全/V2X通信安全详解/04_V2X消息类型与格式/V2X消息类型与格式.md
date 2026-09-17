# V2X消息类型与格式

### 3.1 BSM基本安全消息

**BSM（Basic Safety Message）** 是V2V通信中最核心的消息类型，SAE J2735标准定义了其格式。

**消息结构（SAE J2735 BSM Part I）：**

```text
BasicSafetyMessage:
├── msgCount: 消息计数器 (1-127)
├── temporaryID: 临时ID（假名，周期性变化）
├── DSecond: 毫秒级时间戳
├── Latitude: 纬度 (1/10微度)
├── Longitude: 经度 (1/10微度)
├── Elevation: 海拔 (0.1米)
├── Accuracy: 定位精度
│   ├── SemiMajor: 长半轴精度
│   ├── SemiMinor: 短半轴精度
│   └── Orientation: 方向角
├── Transmission: 档位状态 (neutral/forward/reverse...)
├── Speed: 速度 (0.02 m/s)
├── Heading: 方向角 (0.0125度)
├── SteeringWheelAngle: 方向盘角度
├── AccelerationSet4Way:
│   ├── Longitudinal: 纵向加速度
│   ├── Lateral: 横向加速度
│   ├── Vertical: 垂直加速度
│   └── YawRate: 横摆角速度
├── BrakeStatus:
│   ├── BrakeAppliedStatus: 制动状态
│   ├── TractionControlStatus: 牵引力控制
│   ├── ABSStatus: 防抱死状态
│   ├── StabilityControlStatus: 稳定性控制
│   └── BrakeBoostApplied: 制动助力
├── VehicleSize:
│   ├── VehicleWidth: 车宽
│   └── VehicleLength: 车长
└── VehicleClassification:
    ├── VehicleType: 车辆类型
    └── FuelType: 燃料类型
```

**BSM发送频率与安全机制：**

```python
# BSM消息安全封装示例（伪代码）

import hashlib
from ecdsa import SigningKey, VerifyingKey
from ecdsa.curves import NIST256p

class BSMSecurity:
    """BSM消息安全封装与验证"""

    def __init__(self, pseudonym_cert, private_key):
        """
        初始化BSM安全模块
        :param pseudonym_cert: 假名证书（含公钥）
        :param private_key: 对应的ECDSA私钥
        """
        self.pseudonym_cert = pseudonym_cert
        self.private_key = private_key
        self.msg_count = 0

    def generate_bsm(self, vehicle_state):
        """
        生成带签名的BSM消息
        :param vehicle_state: 车辆状态数据
        :return: 安全封装后的BSM消息
        """
        # 构建BSM消息体
        bsm_message = {
            "msg_count": self.msg_count % 127,
            "temporary_id": self.pseudonym_cert.pseudonym_id,
            "timestamp": int(time.time() * 1000) % 60000,
            "latitude": int(vehicle_state['latitude'] * 1e7),
            "longitude": int(vehicle_state['longitude'] * 1e7),
            "elevation": int(vehicle_state['elevation'] * 10),
            "speed": int(vehicle_state['speed'] / 0.02),
            "heading": int(vehicle_state['heading'] / 0.0125),
            "acceleration": {
                "longitudinal": int(vehicle_state['accel_long'] * 50),
                "lateral": int(vehicle_state['accel_lat'] * 50),
                "vertical": int(vehicle_state['accel_vert'] * 50),
                "yaw_rate": int(vehicle_state['yaw_rate'] * 10000)
            },
            "brake_status": vehicle_state['brake_status'],
            "vehicle_size": {
                "width": int(vehicle_state['width'] * 50),
                "length": int(vehicle_state['length'] * 50)
            }
        }

        self.msg_count += 1

        # 序列化消息（使用UPER编码）
        message_bytes = self._encode_uper(bsm_message)

        # 生成IEEE 1609.2签名
        signed_message = self._sign_message(message_bytes)

        return signed_message

    def _sign_message(self, message_bytes):
        """
        按IEEE 1609.2标准签名消息
        """
        # 构建待签名数据结构
        to_be_signed = {
            "protocol_version": 3,
            "certificate": self.pseudonym_cert.encode(),
            "unsecured_data": message_bytes,
            "generation_time": int(time.time() * 1000),
            "generation_location": {
                "latitude": self.pseudonym_cert.location['lat'],
                "longitude": self.pseudonym_cert.location['lon']
            }
        }

        # 序列化待签名数据
        tbs_bytes = self._encode_uper(to_be_signed)

        # ECDSA签名（SHA-256 + P-256）
        signature = self.private_key.sign(
            tbs_bytes,
            hashfunc=hashlib.sha256,
            sigencode=lambda r, s: r.to_bytes(32, 'big') + s.to_bytes(32, 'big')
        )

        # 封装签名后的消息
        signed_message = {
            "protocol_version": 3,
            "signed_data": {
                "tbs_data": tbs_bytes,
                "signer_info": {
                    "signer_type": "certificate",
                    "certificates": [self.pseudonym_cert.encode()],
                    "digest_algorithm": "SHA256",
                    "signature_algorithm": "ECDSA_NISTP256"
                },
                "signature": {
                    "r": signature[:32],
                    "s": signature[32:]
                }
            }
        }

        return signed_message

    def verify_bsm(self, signed_message):
        """
        验证收到的BSM消息签名
        """
        try:
            # 提取证书
            cert = signed_message['signed_data']['signer_info']['certificates'][0]
            pseudonym_cert = PseudonymCertificate.decode(cert)

            # 验证证书链
            if not self._verify_cert_chain(pseudonym_cert):
                return {"valid": False, "reason": "证书链验证失败"}

            # 验证证书有效期
            if not pseudonym_cert.is_valid_now():
                return {"valid": False, "reason": "证书已过期或未生效"}

            # 提取公钥
            public_key = pseudonym_cert.public_key

            # 提取签名和待验证数据
            tbs_bytes = signed_message['signed_data']['tbs_data']
            sig = signed_message['signed_data']['signature']
            signature = sig['r'] + sig['s']

            # ECDSA验签
            verifying_key = VerifyingKey.from_string(
                public_key,
                curve=NIST256p
            )

            is_valid = verifying_key.verify(
                signature,
                tbs_bytes,
                hashfunc=hashlib.sha256
            )

            if is_valid:
                return {"valid": True, "certificate": pseudonym_cert}
            else:
                return {"valid": False, "reason": "签名验证失败"}

        except Exception as e:
            return {"valid": False, "reason": f"验证异常: {str(e)}"}

    def _verify_cert_chain(self, cert):
        """验证假名证书的信任链"""
        # 1. 验证签发CA签名
        issuer_ca = self.ca_store.get(cert.issuer_id)
        if not issuer_ca:
            return False

        # 2. 验证CA对假名证书的签名
        if not issuer_ca.verify_certificate(cert):
            return False

        # 3. 验证CA证书链直至根CA
        return self._verify_ca_chain(issuer_ca)

    def _encode_uper(self, data):
        """UPER编码（Unaligned Packed Encoding Rules）"""
        # 实际实现使用ASN.1 UPER编码
        # 此处简化处理
        import json
        return json.dumps(data, sort_keys=True).encode('utf-8')

    def _verify_ca_chain(self, ca_cert):
        """递归验证CA证书链"""
        if ca_cert.is_root:
            # 根CA，检查是否在信任根列表
            return ca_cert.cert_id in self.trusted_roots
        parent_ca = self.ca_store.get(ca_cert.issuer_id)
        if not parent_ca:
            return False
        if not parent_ca.verify_certificate(ca_cert):
            return False
        return self._verify_ca_chain(parent_ca)


class PseudonymCertificate:
    """假名证书类"""

    @classmethod
    def decode(cls, cert_bytes):
        """从字节解码假名证书"""
        cert = cls()
        # 实际实现使用ASN.1解码
        cert.pseudonym_id = "pseudo_12345"
        cert.public_key = b'\x04...'  # 压缩公钥
        cert.issuer_id = "ca_id_001"
        cert.validity = {"start": 1696000000, "end": 1696432000}
        cert.location = {"lat": 311234567, "lon": 1214567890}
        return cert

    def is_valid_now(self):
        """检查证书是否在有效期内"""
        now = int(time.time())
        return self.validity["start"] <= now <= self.validity["end"]

    def encode(self):
        """编码为字节"""
        return b'\x30\x82...'  # ASN.1编码


# BSM消息发送示例
if __name__ == "__main__":
    import time

    # 模拟车辆状态
    vehicle_state = {
        "latitude": 31.230416,      # 纬度
        "longitude": 121.473701,    # 经度
        "elevation": 10.5,          # 海拔（米）
        "speed": 15.0,              # 速度 (m/s)
        "heading": 90.0,            # 方向角 (度)
        "accel_long": 0.5,          # 纵向加速度 (m/s^2)
        "accel_lat": 0.0,           # 横向加速度 (m/s^2)
        "accel_vert": 0.0,          # 垂直加速度 (m/s^2)
        "yaw_rate": 0.0,            # 横摆角速度 (rad/s)
        "brake_status": 0x00,       # 制动状态
        "width": 1.8,               # 车宽（米）
        "length": 4.5               # 车长（米）
    }

    # 初始化安全模块
    security = BSMSecurity(
        pseudonym_cert=PseudonymCertificate(),
        private_key=SigningKey.generate(curve=NIST256p)
    )

    # 生成签名BSM
    signed_bsm = security.generate_bsm(vehicle_state)
    print(f"生成BSM消息: msg_count={signed_bsm}")

    # 验证BSM
    result = security.verify_bsm(signed_bsm)
    print(f"验证结果: {result}")
```

### 3.2 BAM基础公告消息

**BAM（Basic Advertisement Message）** 用于广播路边信息和交通事件信息。

**消息内容示例：**

```text
BAM消息内容类型：
├── 交通事件信息
│   ├── 事件类型（事故/施工/拥堵）
│   ├── 事件位置
│   ├── 影响范围
│   └── 持续时间
├── 道路信息
│   ├── 限速信息
│   ├── 车道封闭信息
│   └── 道路类型
├── 天气信息
│   ├── 路面状况（干燥/湿滑/结冰）
│   ├── 能见度
│   └── 降雨/降雪信息
└── 紧急信息
    ├── 紧急车辆接近
    ├── 疏散路线
    └── 紧急避难所位置
```

### 3.3 SPAT信号相位与配时消息

**SPaT（Signal Phase and Timing）** 消息由RSU广播，提供交叉路口信号灯的实时状态。

```text
SPaT消息结构：

SignalPhaseAndTiming:
├── IntersectionState:
│   ├── intersectionId: 路口编号
│   ├── signalGroup:
│   │   ├── signalGroupId: 信号组ID
│   │   ├── phaseState:
│   │   │   ├── currentPhase: 当前相位（红/绿/黄）
│   │   │   ├── timeToChange: 剩余时间（秒）
│   │   │   └── nextPhase: 下一相位
│   │   └── pedestrianPhase: 行人信号
│   └── minEndTime: 最短结束时间
└── TimeReference:
    └── timeStamp: 时间戳

安全要求：
- SPaT消息必须由RSU使用合法证书签名
- 车辆验证RSU证书后方可信任信号灯状态
- 时间戳用于防止重放攻击
```

### 3.4 MAP地图数据消息

**MAP** 消息描述交叉路口的几何拓扑结构，与SPaT配合使用。

```text
MAP消息结构：

MapData:
├── IntersectionGeometry:
│   ├── intersectionId: 路口编号
│   ├── RefPosition: 参考坐标
│   ├── LaneSet:
│   │   ├── Lane:
│   │   │   ├── laneId: 车道ID
│   │   │   ├── laneAttributes: 车道属性
│   │   │   │   ├── laneType: 车道类型（机动车/非机动车/人行）
│   │   │   │   ├── direction: 方向（正向/反向）
│   │   │   │   └── sharedWith: 共享类型
│   │   │   ├── nodeList: 车道节点列表
│   │   │   └── connectsTo: 连接关系
│   │   └── ...
│   └── ...
└── DataParameters:
    └── updateTime: 更新时间

安全要求：
- MAP消息需签名验证
- 车辆验证后构建路口拓扑模型
- 用于路径规划和碰撞预警
```

---

---

## 📋 内容审核与补充建议

> 针对「V2X消息类型与格式」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
