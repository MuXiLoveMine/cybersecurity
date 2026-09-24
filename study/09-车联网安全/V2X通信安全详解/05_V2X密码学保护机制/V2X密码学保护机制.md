# V2X密码学保护机制

### 5.1 数字签名方案

V2X通信中，数字签名是最核心的安全机制，用于保证消息的真实性和完整性。

**V2X签名方案要求：**

| 要求 | 说明 | 原因 |
|------|------|------|
| 签名速度快 | 签名<2ms | 车辆每100ms发送一次BSM |
| 验证速度快 | 验证<5ms | 接收方需处理大量消息 |
| 签名紧凑 | <80字节 | 无线带宽有限 |
| 安全强度 | 128位 | 满足长期安全需求 |
| 抗量子 | 可选 | 长期安全考虑 |

**ECDSA P-256签名过程：**

```python
import os
import hashlib
from ecdsa import SigningKey, VerifyingKey, NIST256p
from ecdsa.util import sigencode_der, sigdecode_der

class V2XSignatureScheme:
    """V2X数字签名方案 - ECDSA P-256"""

    # ECDSA P-256参数
    CURVE = NIST256p
    HASH = hashlib.sha256

    @classmethod
    def generate_keypair(cls):
        """生成ECDSA密钥对"""
        private_key = SigningKey.generate(curve=cls.CURVE)
        public_key = private_key.get_verifying_key()
        return private_key, public_key

    @classmethod
    def sign(cls, private_key, message):
        """
        签名消息
        :param private_key: ECDSA私钥
        :param message: 待签名消息（字节）
        :return: 签名（DER编码）
        """
        # 使用确定性随机数（RFC 6979）防止 nonce 泄露
        signature = private_key.sign(
            message,
            hashfunc=cls.HASH,
            sigencode=sigencode_der
        )
        return signature

    @classmethod
    def verify(cls, public_key, message, signature):
        """
        验证签名
        :param public_key: ECDSA公钥
        :param message: 原始消息（字节）
        :param signature: 签名（DER编码）
        :return: 验证结果
        """
        try:
            valid = public_key.verify(
                signature,
                message,
                hashfunc=cls.HASH,
                sigdecode=sigdecode_der
            )
            return valid
        except Exception:
            return False

    @classmethod
    def batch_verify(cls, public_keys, messages, signatures):
        """
        批量验证签名（优化性能）
        :return: 每个签名的验证结果
        """
        results = []
        for pk, msg, sig in zip(public_keys, messages, signatures):
            results.append(cls.verify(pk, msg, sig))
        return results


# 性能基准测试
def benchmark_v2x_signature():
    """V2X签名性能基准测试"""
    import time

    scheme = V2XSignatureScheme()

    # 生成密钥对
    private_key, public_key = scheme.generate_keypair()

    # 模拟BSM消息（约200字节）
    bsm_message = os.urandom(200)

    # 签名性能测试
    sign_start = time.perf_counter()
    for _ in range(1000):
        signature = scheme.sign(private_key, bsm_message)
    sign_end = time.perf_counter()
    sign_time = (sign_end - sign_start) / 1000 * 1000  # 毫秒

    # 验证性能测试
    verify_start = time.perf_counter()
    for _ in range(1000):
        result = scheme.verify(public_key, bsm_message, signature)
    verify_end = time.perf_counter()
    verify_time = (verify_end - verify_start) / 1000 * 1000

    print(f"ECDSA P-256 性能基准:")
    print(f"  签名时间: {sign_time:.2f} ms/次")
    print(f"  验证时间: {verify_time:.2f} ms/次")
    print(f"  签名大小: {len(signature)} 字节")
    print(f"  公钥大小: {len(public_key.to_string())} 字节")
    print(f"  消息大小: {len(bsm_message)} 字节")

    # V2X要求评估
    print(f"\nV2X要求评估:")
    print(f"  签名<2ms: {'✓ 满足' if sign_time < 2 else '✗ 不满足'}")
    print(f"  验证<5ms: {'✓ 满足' if verify_time < 5 else '✗ 不满足'}")
    print(f"  签名<80B: {'✓ 满足' if len(signature) < 80 else '✗ 不满足'}")


if __name__ == "__main__":
    benchmark_v2x_signature()
```

### 5.2 V2X PKI体系

V2X采用专门的PKI（公钥基础设施）体系来管理车辆证书，其核心是**SCMS（Security Credential Management System）** 架构。

**SCMS架构：**

```text
SCMS (Security Credential Management System) 架构

┌──────────────────────────────────────────────────────────────┐
│                      根CA (Root CA)                           │
│              ┌──────────────────────────┐                    │
│              │   信任根，离线保管        │                    │
│              └──────────────┬───────────┘                    │
└─────────────────────────────┼────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │ 中间CA     │  │ 中间CA     │  │ 中间CA     │
     │ (Policy 1) │  │ (Policy 2) │  │ (Policy 3) │
     └──────┬─────┘  └──────┬─────┘  └──────┬─────┘
            │               │               │
            ▼               ▼               ▼
     ┌──────────────────────────────────────────┐
     │           假名证书授权CA (PCA)            │
     │    (Pseudonym Certificate Authority)      │
     └──────────────────────┬───────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │  RA (注册   │  │  RA (注册  │  │  RA (注册  │
     │  机构)     │  │  机构)    │  │  机构)    │
     └──────┬─────┘  └──────┬─────┘  └──────┬─────┘
            │               │               │
            ▼               ▼               ▼
     ┌──────────────────────────────────────────┐
     │              车辆 (OBU/RSU)                │
     │    持有多张假名证书，周期性切换使用          │
     └──────────────────────────────────────────┘
```

**SCMS核心组件功能：**

| 组件 | 功能 | 安全特性 |
|------|------|---------|
| 根CA | 信任锚，签发中间CA | 离线，物理保护 |
| 中间CA | 签发PCA证书 | 分权管理 |
| PCA | 签发假名证书 | 隐私保护核心 |
| RA | 车辆注册和身份验证 | 审核车辆合法性 |
| CRL | 证书撤销列表管理 | 撤销恶意车辆 |
| MA | 行为不当检测机构 | 检测异常行为 |
| LA | 链接机构，必要时去匿名 | 执法追溯 |

**假名证书发放流程：**

```python
class SCMSCertificateIssuance:
    """SCMS假名证书发放流程"""

    def __init__(self):
        self.root_ca = RootCA()
        self.pca = PseudonymCA()
        self.ra = RegistrationAuthority()

    def issue_pseudonym_certificates(self, vehicle_request):
        """
        为车辆发放假名证书批次
        :param vehicle_request: 车辆证书请求
        :return: 假名证书批次
        """
        # 步骤1：车辆注册
        registration_result = self.ra.register_vehicle(
            vehicle_id=vehicle_request['vehicle_id'],
            vin=vehicle_request['vin'],
            manufacturer_cert=vehicle_request['manufacturer_cert'],
            enrollment_cert=vehicle_request['enrollment_cert']
        )

        if not registration_result['success']:
            return {"success": False, "error": "车辆注册失败"}

        # 步骤2：生成假名证书请求
        cert_requests = []
        for i in range(vehicle_request['batch_size']):  # 例如20张
            # 车辆生成临时密钥对
            keypair = self._generate_ephemeral_keypair()

            cert_request = {
                'public_key': keypair['public_key'],
                'request_id': self._generate_request_id(),
                'validity': {
                    'start': vehicle_request['validity_start'],
                    'end': vehicle_request['validity_end']
                },
                # 使用蝴蝶密钥交换保护请求
                'encrypted_request': self._butterfly_encrypt(
                    keypair, self.pca.public_key
                )
            }
            cert_requests.append(cert_request)

        # 步骤3：PCA签发证书
        pseudonym_certs = self.pca.issue_batch(cert_requests)

        # 步骤4：返回给车辆
        return {
            "success": True,
            "certificates": pseudonym_certs,
            "instructions": {
                "rotation_interval": "每5分钟切换一次假名",
                "batch_validity": "20张证书覆盖约100分钟",
                "renewal_threshold": "剩余<5张时申请新批次"
            }
        }

    def _generate_ephemeral_keypair(self):
        """生成临时密钥对"""
        from ecdsa import SigningKey, NIST256p
        sk = SigningKey.generate(curve=NIST256p)
        return {
            'private_key': sk,
            'public_key': sk.get_verifying_key().to_string()
        }

    def _generate_request_id(self):
        import uuid
        return str(uuid.uuid4())

    def _butterfly_encrypt(self, keypair, pca_public_key):
        """
        蝴蝶密钥交换（Butterfly Key Expansion）
        保护假名证书请求的隐私
        """
        # 简化的蝴蝶密钥交换
        # 实际实现详见SCMS规范
        return {
            'ciphertext': b'encrypted_data...',
            'algorithm': 'ECIES-P256'
        }


class RootCA:
    """根CA"""

    def __init__(self):
        self.is_root = True
        self.trusted = True

    def sign_intermediate_ca(self, ca_cert_request):
        """签发中间CA证书"""
        pass


class PseudonymCA:
    """假名证书授权CA"""

    def __init__(self):
        self.public_key = b'pca_public_key...'

    def issue_batch(self, cert_requests):
        """批量签发假名证书"""
        certs = []
        for req in cert_requests:
            cert = {
                'cert_id': req['request_id'],
                'public_key': req['public_key'],
                'issuer': 'PCA-001',
                'validity': req['validity'],
                'signature': b'pca_signature...'
            }
            certs.append(cert)
        return certs


class RegistrationAuthority:
    """注册机构"""

    def register_vehicle(self, vehicle_id, vin, manufacturer_cert, enrollment_cert):
        """注册车辆"""
        # 验证制造商证书
        # 验证注册证书
        # 记录车辆信息（不关联假名证书）
        return {"success": True, "registration_id": "reg_12345"}
```

### 5.3 匿名认证机制

V2X采用匿名认证机制，使车辆在通信中不暴露真实身份，同时保证消息的可信性。

```text
匿名认证机制原理

传统认证（暴露身份）：
车辆A（VIN: LSVAM4187C2015001）
  → BSM消息 → 签名 → 使用真实身份证书
  → 接收方知道是VIN为LSVAM4187C2015001的车辆
  → 可追踪车辆位置历史 → 隐私泄露

匿名认证（保护隐私）：
车辆A持有20张假名证书
  → BSM消息 → 签名 → 使用假名证书#1（5分钟内）
  → 5分钟后切换假名证书#2
  → ...
  → 接收方只知道是"某辆合法车辆"，不知真实身份
  → 不同假名之间无法关联 → 位置隐私保护

特殊情况下追溯：
  如果车辆实施犯罪行为
  → 执法机构向LA（链接机构）提供假名证书
  → LA使用密钥恢复真实身份
  → 实现隐私保护与执法追溯的平衡
```

---

---

