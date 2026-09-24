# Mifare DESFire EV3安全分析

### 11.1 DESFire EV3架构

```
Mifare DESFire EV3安全架构:

硬件层:
  - CC EAL5+认证的安全微控制器
  - 防物理篡改(传感器层)
  - 防DPA/SPA(差分功耗分析)
  - 硬件随机数生成器(TRNG)
  - 防故障注入(电压/时钟)

协议层:
  - ISO/IEC 14443-4 (T=CL协议)
  - ISO/IEC 9797-1 (MAC算法)
  - ISO/IEC 10116 (加密模式)
  - ISO/IEC 18033-2 (AES)

安全特性:
  1. AES-128-CBC加密通信
  2. CMAC消息认证
  3. 三次双向认证(ISO 9798-2)
  4. 动态随机数(防重放)
  5. 命令-响应序列号
  6. 防撕裂攻击(Anti-tearing)
  7. 安全消息传送(Secure Messaging)

存储结构:
  - 应用目录(28个应用)
  - 每应用: 32个文件
  - 文件类型:
    | 标准数据文件
    | 值文件(电子钱包)
    | 循环记录文件
    | 线性记录文件
  - 文件级访问控制
  - 通信加密(可选)
```

### 11.2 DESFire安全通信

```python
# DESFire EV3安全通信示例
# 使用pyDes和cryptography库

from Crypto.Cipher import AES
from Crypto.Hash import CMAC
import os

class DESFireSecureChannel:
    """DESFire EV3 AES安全通道"""

    def __init__(self, master_key):
        self.master_key = master_key  # 16字节AES密钥
        self.session_key = None
        self.rnd_a = None  # 卡片随机数
        self.rnd_b = None  # 读卡器随机数
        self.cmd_counter = 0
        self.iv = b'\x00' * 16

    def authenticate(self, card):
        """AES三次认证"""
        # Step 1: 发送认证命令
        # Auth1: 读卡器 -> 卡片
        # 卡片返回RndA(加密)

        # 生成读卡器随机数
        self.rnd_b = os.urandom(16)

        # 发送Auth命令
        response = card.send_apdu(
            0xAA,  # Auth命令
            0x00,  # Key number
            0x00,  # 保留
            data=b''  # 无数据(第一步)
        )

        # 卡片返回RndA + RndB(加密)
        enc_data = response[:16]  # 加密的RndA
        self.rnd_a = self._decrypt(enc_data)

        # Step 2: 读卡器计算并发送
        # 构造验证数据
        rnd_ab = self.rnd_a + self.rnd_b
        enc_ab = self._encrypt(rnd_ab)
        card.send_apdu(0xAA, 0x00, 0x00, data=enc_ab)

        # Step 3: 卡片返回加密的RndB
        enc_rnd_b_shift = response[16:32]
        rnd_b_shift = self._decrypt(enc_rnd_b_shift)

        # 验证RndB
        expected = self.rnd_b[1:] + bytes([self.rnd_b[0]])
        if rnd_b_shift == expected:
            print("认证成功")
            # 生成会话密钥
            self._derive_session_key()
            return True
        else:
            print("认证失败")
            return False

    def _derive_session_key(self):
        """派生会话密钥"""
        # 会话密钥 = AES(master_key, RndA[0:8] + RndB[0:8])
        kdf_input = self.rnd_a[:8] + self.rnd_b[:8]
        cipher = AES.new(self.master_key, AES.MODE_ECB)
        self.session_key = cipher.encrypt(kdf_input)

    def secure_command(self, cmd_data, cmd_code):
        """安全命令发送(加密+MAC)"""
        # 添加命令计数器
        self.cmd_counter += 1

        # 计算MAC
        mac_input = bytes([self.cmd_counter]) + cmd_data
        cmac = CMAC.new(self.session_key)
        cmac.update(mac_input)
        mac = cmac.digest()[:8]  # 截断为8字节

        # 加载数据加密
        cipher = AES.new(self.session_key, AES.MODE_CBC, self.iv)
        enc_data = cipher.encrypt(cmd_data.ljust(16, b'\x00'))

        # 发送: cmd_code + enc_data + mac
        return bytes([cmd_code]) + enc_data + mac

    def _encrypt(self, data):
        """AES-CBC加密"""
        cipher = AES.new(self.master_key, AES.MODE_CBC, self.iv)
        padded = data.ljust(16 * ((len(data) + 15) // 16), b'\x00')
        return cipher.encrypt(padded)

    def _decrypt(self, data):
        """AES-CBC解密"""
        cipher = AES.new(self.master_key, AES.MODE_CBC, self.iv)
        return cipher.decrypt(data)
```

### 11.3 DESFire vs Classic安全对比

```
安全对比详细分析:

| 维度 | Mifare Classic | Mifare DESFire EV3 |
|------|---------------|-------------------|
| 加密算法 | Crypto-1(专有) | AES-128(标准) |
| 密钥长度 | 48位 | 128位 |
| 认证 | 单向(卡->读卡器) | 双向三次认证 |
| 防重放 | 无 | 随机数+计数器 |
| 随机数 | 24位LFSR(可预测) | 硬件TRNG |
| 安全评估 | 未通过 | CC EAL5+ |
| 密钥恢复 | 数秒内 | 理论不可行 |
| 侧信道防护 | 无 | DPA/SPA防护 |
| 通信加密 | 可选(弱) | 默认AES-CBC+CMAC |
| 文件访问 | 扇区级 | 文件级 |
| 防撕裂 | 无 | 有 |
| 标准 | 非标准 | ISO 14443-4 |
| 硬件防篡改 | 无 | 有 |
| 审计 | 无 | 有(安全日志) |

DESFire的已知攻击面:
1. 侧信道攻击(SCA)
   - 需要物理接触和专业设备
   - 功耗/电磁分析
   - EV3有防护但非完美

2. 故障注入(FA)
   - 电压/时钟毛刺
   - 可绕过安全检查
   - 需要精密设备

3. 滥用默认密钥
   - 出厂默认密钥未修改
   - 管理密钥泄露
   - 最常见的实际攻击

4. 中继攻击
   - DESFire本身安全
   - 但中继可以转发认证
   - 需要距离绑定防护
```

---

---

