# V2X安全标准体系

### 7.1 IEEE 1609.2标准

**IEEE 1609.2** 是V2X安全服务的核心标准，定义了V2X通信中的安全服务和密码学协议。

```text
IEEE 1609.2 标准体系

IEEE 1609.2: 安全服务
├── 数字签名格式
│   ├── ECDSA over P-256
│   ├── ECDSA over P-384 (可选)
│   └── 签名消息封装格式
├── 证书格式
│   ├── 假名证书 (Pseudonym Certificate)
│   ├── 应用证书 (Application Certificate)
│   └── CA证书
├── 加密协议
│   ├── ECIES (椭圆曲线集成加密)
│   └── 对称加密 AES-128-CBC
├── 密钥管理
│   ├── 证书申请协议
│   ├── 证书撤销机制
│   └── 蝴蝶密钥扩展
└── 安全消息格式
    ├── 签名消息 (SignedMessage)
    ├── 加密消息 (EncryptedMessage)
    └── 证书撤销列表 (CRL)

证书格式（简化）：
┌─────────────────────────────────────────┐
│          IEEE 1609.2 证书                │
├─────────────────────────────────────────┤
│ Version: 3                              │
│ Type: Pseudonym/Application/CA          │
│ Issuer: CA Identifier                   │
│ ToBeSigned:                             │
│   ├── AppPermissions: [应用权限列表]     │
│   ├── CertValidity: [有效期]             │
│   ├── VerifyKeyIndicator: 公钥           │
│   └── CrlSeries: CRL序列号              │
│ Signature: CA签名                        │
└─────────────────────────────────────────┘
```

### 7.2 ETSI ITS标准

**ETSI（欧洲电信标准化协会）** 制定了欧洲的ITS（Intelligent Transport Systems）安全标准。

```text
ETSI ITS 安全架构

ETSI EN 302 665: ITS总体架构
├── ITS Station (ITS-S) 参考架构
│   ├── Access Layer
│   ├── Networking & Transport Layer
│   ├── Facilities Layer
│   └── Applications Layer
└── 安全贯穿所有层

ETSI TS 103 097: 安全机制
├── 信任管理
│   ├── 信任列表 (Trust List)
│   ├── 根CA证书
│   └── 信任链验证
├── 证书格式
│   ├── 假名证书 (Authorization Ticket)
│   ├── 授权证书 (Authorization Certificate)
│   └── CA证书
├── 消息签名格式
│   ├── 签名信息 (SignedData)
│   ├── 哈希算法: SHA-256
│   └── 签名算法: ECDSA P-256
└── CRL/CTL管理

ETSI EN 302 661: 信任管理
├── 根CA信任
├── 跨域信任（不同国家ITS系统间）
└── 信任列表更新机制
```

**ETSI与IEEE 1609.2对比：**

| 维度 | IEEE 1609.2 | ETSI TS 103 097 |
|------|-------------|-----------------|
| 地区 | 美国 | 欧洲 |
| 证书类型 | 假名证书 | 授权票据 |
| 签名算法 | ECDSA P-256 | ECDSA P-256 |
| 哈希算法 | SHA-256 | SHA-256 |
| 信任管理 | SCMS | 信任列表 |
| 隐私保护 | 假名切换 | 假名切换 |
| 消息格式 | 自定义ASN.1 | ETSI自定义ASN.1 |
| 跨域信任 | 较少涉及 | 重点定义 |

### 7.3 中国国家标准

中国在V2X安全方面制定了一系列国家标准和行业标准。

```text
中国V2X安全标准体系

国家标准 (GB/T):
├── GB/T 31024.1-2014: ITS专用短程通信 总体技术要求
├── GB/T 31024.2-2014: ITS专用短程通信 MAC层
├── GB/T 31024.3-2014: ITS专用短程通信 物理层
├── GB/T 35286-2017: 信息安全技术 低速无线个域网空口安全
├── GB/T 37344-2019: 电动汽车远程服务与管理系统安全技术要求
└── GB/T 40425-2021: 智能运输系统 逻辑链路控制安全

行业标准:
├── YD/T 3707-2020: 基于LTE的车联网通信安全技术要求
├── YD/T 3957-2021: 基于LTE的车联网安全证书管理技术要求
├── T/CSAE 53-2020: 合作式应用层规范
├── T/CSAE 157-2020: 合作式应用层安全规范
└── T/ITS 0113-2020: 车路协同系统安全技术要求

中国V2X安全特点:
├── 采用国密算法 (SM2/SM3/SM4)
├── 基于C-V2X技术路线
├── 统一CA管理框架
├── 与交通管理平台集成
└── 强调数据安全合规（数据安全法、个人信息保护法）
```

**中国V2X PKI架构：**

```text
中国V2X PKI参考架构

┌─────────────────────────────────────────────────┐
│              国家级根CA (Root CA)                  │
│         （国家交通运输部门管理）                     │
└───────────────────────┬─────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ 整车厂CA     │ │ 运营商CA     │ │ 交通管理CA    │
│ (OEM CA)    │ │ (Operator CA)│ │ (Traffic CA) │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       ▼                ▼                ▼
┌──────────────────────────────────────────────────┐
│              假名证书CA (PCA)                      │
│         签发车辆假名证书 (使用SM2)                  │
└──────────────────────┬───────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────┐
│              车辆 / 路侧设备                        │
│    使用国密SM2签名，SM3哈希，SM4加密               │
└──────────────────────────────────────────────────┘

国密算法在V2X中的应用:
├── SM2: 非对称加密和数字签名（替代ECDSA/RSA）
├── SM3: 密码杂凑算法（替代SHA-256）
├── SM4: 对称加密（替代AES）
├── SM9: 标识密码算法（基于身份的加密）
└── 密码合规: 满足《商用密码管理条例》要求
```

**国密SM2在V2X中的使用示例：**

```python
# 注意: 实际使用需要安装gmssl或其他国密库
# pip install gmssl

class SM2V2XSecurity:
    """使用国密SM2的V2X安全方案"""

    # SM2曲线参数（国密标准曲线）
    SM2_PARAMS = {
        'p': 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF,
        'a': 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC,
        'b': 0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93,
        'n': 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF4093995D549,
        'Gx': 0x32C4AE2C1F1981195F9904466A39C9948FE22BBF83281B8E5C5B3625A,
        'Gy': 0xBC37366A396A2D2F20F79DF4F66E5C5A5A3F0F8C5C3D5E5B7F8A9B0C1D2
    }

    @staticmethod
    def sign_bsm_with_sm2(private_key, bsm_message):
        """
        使用SM2对BSM消息签名
        :param private_key: SM2私钥
        :param bsm_message: BSM消息字节
        :return: SM2签名 (r, s)
        """
        # 实际使用gmssl库:
        # from gmssl import sm2
        # sm2_obj = sm2.CryptSM2(private_key, public_key)
        # signature = sm2_obj.sign(bsm_message)

        # 简化示例
        import hashlib

        # 使用SM3计算摘要
        # 实际使用: from gmssl import sm3, func
        digest = hashlib.sha256(bsm_message).digest()  # 替换为SM3

        # SM2签名（简化）
        # 实际SM2签名包含用户ID作为参数
        user_id = b'12345678'  # 默认用户ID

        # 返回签名结果
        return {
            'algorithm': 'SM2',
            'hash': 'SM3',
            'signature_r': 0,  # 实际签名值
            'signature_s': 0,
            'user_id': user_id
        }

    @staticmethod
    def verify_bsm_with_sm2(public_key, bsm_message, signature):
        """使用SM2验证BSM签名"""
        # 实际使用gmssl库:
        # sm2_obj = sm2.CryptSM2(private_key, public_key)
        # return sm2_obj.verify(sign, bsm_message)

        return True  # 简化返回

    @staticmethod
    def generate_pseudonym_cert_sm2(vehicle_public_key, validity_period):
        """生成SM2假名证书"""
        cert = {
            'version': 1,
            'serial_number': '0x...',
            'subject': 'anonymous',
            'public_key_algorithm': 'SM2',
            'public_key': vehicle_public_key,
            'signature_algorithm': 'SM2-SM3',
            'issuer': 'PCA-CN',
            'validity': validity_period,
            'extensions': {
                'pseudonym': True,
                'v2x_applications': ['BSM', 'SPaT', 'MAP']
            }
        }
        return cert


# V2X安全配置示例
def v2x_security_config():
    """V2X安全配置"""

    config = {
        # 密码算法配置
        "crypto": {
            "signature_algorithm": "SM2",        # 国密SM2签名
            "hash_algorithm": "SM3",             # 国密SM3哈希
            "encryption_algorithm": "SM4",       # 国密SM4加密
            "key_exchange": "SM2-ECDH",          # 国密密钥交换
            "key_length": 256                     # 密钥长度
        },

        # PKI配置
        "pki": {
            "root_ca": "国家根CA",
            "pca_url": "https://pca.v2x.cn",
            "ra_url": "https://ra.v2x.cn",
            "crl_url": "https://crl.v2x.cn",
            "ocsp_url": "https://ocsp.v2x.cn",
            "cert_batch_size": 20,              # 每批假名证书数量
            "cert_validity_hours": 1,           # 证书有效期
            "pseudonym_rotation_min": 5         # 切换间隔（分钟）
        },

        # 消息安全配置
        "message_security": {
            "sign_bsm": True,                   # BSM消息签名
            "sign_spat": True,                  # SPaT消息签名
            "sign_map": True,                   # MAP消息签名
            "verify_cert_chain": True,          # 验证证书链
            "check_crl": True,                  # 检查CRL
            "replay_window_ms": 2000,           # 重放窗口
            "max_msg_per_second": 100           # 每秒最大消息数
        },

        # 隐私保护配置
        "privacy": {
            "pseudonym_enabled": True,          # 启用假名
            "rotation_jitter_sec": 30,          # 切换随机扰动
            "mix_zone_enabled": True,           # 混合区域
            "location_precision": 50,           # 位置精度（米）
            "data_retention_days": 0            # 数据保留天数
        },

        # 安全审计配置
        "audit": {
            "log_signed_messages": True,        # 记录签名消息
            "log_verification_results": True,    # 记录验证结果
            "log_certificate_usage": True,      # 记录证书使用
            "audit_log_retention_days": 90      # 审计日志保留天数
        }
    }

    return config


# 打印配置
import json
print("V2X安全配置（国密版）:")
print(json.dumps(v2x_security_config(), indent=2, ensure_ascii=False))
```

---

---

