# LPWAN与边缘计算安全

> 本文档系统讲解低功耗广域网（LPWAN）与边缘计算的安全体系，覆盖 LoRaWAN、NB-IoT、Sigfox 三大主流技术的安全机制与攻击面，并延伸到边缘计算架构安全、边缘设备加固、边缘 AI 安全以及边缘云协同安全。文中给出协议分析、密钥体系、攻击向量、检测方法与代码/配置示例，面向安全学习者，强调技术细节与工程可落地性。

---

## 一、LPWAN 技术概述

### 1.1 LPWAN 定义与特点

低功耗广域网（Low Power Wide Area Network，LPWAN）是一类专为物联网远距离、低功耗、低带宽场景设计的无线通信技术，典型用于智能水表、燃气表、智慧农业、资产追踪、环境监测等。

**核心特征：**
- **远距离**：单基站覆盖半径可达 2-15 km（城市）/ 40 km（郊区）
- **低功耗**：终端电池寿命 5-10 年，AA 电池即可供电
- **低速率**：典型几十 bps 到几十 kbps
- **大连接**：单基站支持万级乃至十万级终端
- **低成本**：模组成本低、部署成本低

**代价：** LPWAN 牺牲了带宽与实时性，因此不适合视频、语音、实时控制等高带宽场景。

### 1.2 LPWAN 分类

```
┌──────────────────────────────────────────────────────────┐
│                       LPWAN                               │
├──────────────────────┬───────────────────────────────────┤
│   非授权频谱 (Unlicensed)│     授权频谱 (Licensed)         │
├──────────────────────┼───────────────────────────────────┤
│  LoRaWAN             │  NB-IoT (3GPP)                    │
│  Sigfox              │  LTE-M (3GPP)                     │
│  Weightless          │  5G mMTC                          │
│  ZETA / 威胜         │                                   │
└──────────────────────┴───────────────────────────────────┘
```

| 维度 | LoRaWAN | NB-IoT | Sigfox |
|------|---------|--------|--------|
| 频谱 | 非授权 (Sub-GHz) | 授权 LTE 频段 | 非授权 (Sub-GHz) |
| 调制 | CSS (Chirp Spread Spectrum) | OFDMA/SC-FDMA | DBPSK/GFSK |
| 速率 | 0.3-50 kbps | 20-250 kbps | 100 bps |
| 每日消息数 | 无限制（受占空比约束） | 无限制 | 140 条/天 |
| 双工 | 半双工 | 半双工/FDD | 单向上行主导 |
| 组网 | 私有/公共 | 运营商 | 运营商 |
| 安全 | 端到端 AES-128 | SIM/EPS-AKA | 设备ID+密钥 |

---

## 二、LoRaWAN 安全机制

### 2.1 LoRaWAN 协议栈与安全层位置

```
┌────────────────────────────────┐
│   应用层 (Application)          │  ← AppSKey 端到端加密
├────────────────────────────────┤
│   MAC 层 (LoRaWAN)              │  ← NwkSKey 网络层加密/完整性
├────────────────────────────────┤
│   LoRa 物理层 (CSS 调制)        │  ← 无加密，仅物理层抗干扰
└────────────────────────────────┘
```

LoRaWAN 在 MAC 层和应用层分别使用独立的 AES-128 密钥，实现"网络层防伪 + 应用层保密"双重保护。

### 2.2 密钥体系

LoRaWAN v1.0.x 的密钥体系如下：

| 密钥 | 长度 | 用途 | 持有方 |
|------|------|------|--------|
| AppKey | 128 bit | 派生其他密钥的根密钥 | 设备 + Join Server |
| NwkSKey | 128 bit | 网络层加密、MIC 校验 | 设备 + Network Server |
| AppSKey | 128 bit | 应用载荷加密 | 设备 + Application Server |
| DevEUI | 64 bit | 设备全球唯一标识 | 设备出厂烧录 |
| AppEUI | 64 bit | 应用唯一标识 | 应用方分配 |

**密钥派生关系：**
```
                 AppKey (根密钥)
                 /          \
   OTAA 入网时派生            派生
         /                          \
    NwkSKey (网络层)            AppSKey (应用层)
```

> LoRaWAN v1.1 引入了更细分的密钥体系：将 NwkSKey 拆分为 FNwkSIntKey、SNwkSIntKey、NwkSEncKey，并把根密钥拆分为 AppKey 和 NwkKey，进一步隔离签名与加密用途。学习时建议对照 v1.0 与 v1.1 的差异表。

### 2.3 OTAA 与 ABP 入网方式

**OTAA（Over-The-Air Activation）：**
设备通过 Join Request / Join Accept 流程动态获取会话密钥，是推荐方式。

```
设备                                网络服务器
  │                                     │
  │── JoinRequest ───────────────────→ │ (含 DevEUI, AppEUI, DevNonce, MIC)
  │                                     │ 校验 AppKey, 生成 AppNonce
  │←── JoinAccept ──────────────────── │ (含 AppNonce, NetID, DevAddr, DLSettings)
  │                                     │
  │ 派生: NwkSKey = AES(AppKey, AppNonce|NetID|DevNonce)
  │       AppSKey = AES(AppKey, AppNonce|NetID|DevNonce)
  │                                     │
  │── 加密数据上行 ─────────────────→ │
```

**ABP（Activation By Personalisation）：**
设备出厂时直接烧录 NwkSKey、AppSKey、DevAddr，无需 Join 流程。

| 维度 | OTAA | ABP |
|------|------|-----|
| 密钥派生 | 动态 | 静态 |
| 密钥更新 | 支持（重新 Join） | 不支持 |
| 设备成本 | 略高 | 低 |
| 安全性 | 较高 | 较低（密钥固定） |
| 适用场景 | 量产部署 | 测试/小规模 |

### 2.4 加密与完整性机制

**网络层（MIC 校验）：**
```
MIC = AES-CMAC(NwkSKey, B0 | MHDR | FHDR | FPort | FramePayload)
```
- MIC 提供完整性保护，防止篡改与伪造
- 但 v1.0 的 MIC 仅对上行/下行计数器做 4 字节校验

**应用层（载荷加密）：**
```
Payload_encrypted = AES-CTR(AppSKey, Ai | FramePayload)
```
- 采用 AES-CTR 模式，对应用载荷加密
- 网络服务器可读 MAC 层信息，但无法解密应用载荷（端到端保密）

---

## 三、LoRaWAN 攻击面

### 3.1 重放攻击（Replay）

LoRAWAN 通过 DevAddr + FCntUp 计数器防重放，但仍有以下薄弱点：
- **ABP 设备重启后计数器归零**：若网络服务器未持久化计数器，攻击者可重置后重放旧帧
- **JoinRequest 重放**：v1.0 的 DevNonce 仅 2 字节且随机，攻击者重放历史 JoinRequest 可触发网络服务器重新下发 JoinAccept，若目标设备已使用新密钥则产生密钥失配

**缓解：**
- 网络服务器持久化每个设备的 FCntUp，对回退计数器帧直接丢弃
- JoinRequest 增加随机数防重放（v1.1 引入 JoinNonce）
- 设备侧对 DevNonce 做单调递增检查

### 3.2 确认伪造（ACK Spoofing）

下行 ACK 帧使用 NwkSKey 加密，但 v1.0 下行链路加密存在已知缺陷：ACK 不含应用载荷，攻击者可基于已知密文片段构造合法 ACK，诱使设备认为数据已被成功接收，从而丢弃未确认的上行数据。

**缓解：** v1.1 引入独立的下行加密密钥（NwkSEncKey）与签名密钥（SNwkSIntKey），加强下行帧的完整性。

### 3.3 Jamming 攻击

LoRa 使用 CSS 调制具备一定抗干扰能力，但仍是共享频谱，攻击者可：
- 持续发射大功率同频信号压制整个信道
- 针对特定扩频因子（SF）发射干扰，精确压制某类设备

**检测：** 监测 RSSI 异常升高、PER（误包率）突增、特定 SF 信道拥塞。

**缓解：** 多网关冗余、跳频（FHSS）、地理分布部署、配合监管侧频谱监测定位干扰源。

### 3.4 设备克隆（Device Cloning）

攻击者物理提取设备密钥（如通过侧信道或 Flash 读取），复制成多个相同身份的克隆设备，造成：
- 网络服务器无法区分真假设备
- 克隆设备可发起 DoS 或伪造数据

**检测与缓解：**
- 物理防拆： tamper-evident 外壳、芯片级安全元件（SE）
- 密钥安全存储：使用 ATSHA204A / ATECC508A 等硬件密码芯片
- 行为基线：克隆设备通常位置/通信模式异常，可基于地理位置和通信指纹检测

### 3.5 旁路攻击与密钥提取

```
攻击路径：
  物理获取设备 → 拆解 → 提取 Flash → 反汇编固件 → 提取 AppKey
                                                    ↓
                                            克隆/伪造/解密所有通信
```

**防护：**
- 使用支持 secure boot 的 MCU（如 STM32L5、CC2538 + SE）
- 关键密钥存入安全元件，禁止从主 MCU 读出
- 固件加密、防读出（RDP Level 2）

---

## 四、NB-IoT 安全机制

### 4.1 NB-IoT 与蜂窝安全继承

NB-IoT 基于 3GPP LTE 体系，安全机制继承自蜂窝网络：
- 基于 USIM 卡的身份认证
- EPS-AKA（EPS Authentication and Key Agreement）认证协议
- NAS 层与 AS 层双层密钥体系
- 空口加密：EPS 加密算法 EEA1/EEA2（SNOW 3G/AES-128）

### 4.2 EPS-AKA 认证流程

```
UE (设备)                  MME (核心网)              HSS (归属)
   │                            │                         │
   │── Attach Request ─────────→│                         │
   │                            │── Authentication Data → │
   │                            │                         │ 计算 AV (认证向量)
   │                            │←── RAND, AUTN, XRES ────│
   │←── RAND, AUTN ────────────│                         │
   │                            │                         │
   │ USIM 校验 AUTN             │                         │
   │ 计算 RES                   │                         │
   │── RES ────────────────────→│                         │
   │                            │ 校验 RES == XRES         │
   │                            │ 派生 NAS/AS 密钥         │
```

**关键参数：**
- K：USIM 与 HSS 共享的 128 bit 根密钥
- RAND：网络侧随机数（128 bit）
- AUTN：认证令牌，含 MAC、SQN（序列号）、AMF
- RES/XRES：设备侧/网络侧计算出的响应值

### 4.3 密钥层级

```
K (根密钥, USIM/HSS)
  └─→ K_ASME (接入安全管理实体密钥)
        ├─→ K_NASenc (NAS 层加密密钥)
        ├─→ K_NASint (NAS 层完整性密钥)
        └─→ K_eNB   (基站密钥)
              ├─→ K_UPenc (用户面加密)
              ├─→ K_UPint (用户面完整性)
              └─→ K_RRCenc / K_RRCint (RRC 层)
```

> 这种分层密钥体系实现"前向安全"：单个密钥泄露不会危及根密钥，且切换基站时密钥可前向更新。

### 4.4 NB-IoT 安全风险

| 风险 | 描述 | 缓解 |
|------|------|------|
| IMSI 捕获 | 伪基站诱导设备发送 IMSI | 启用 SUCI（5G 身份隐私） |
| 伪基站中间人 | 攻击者伪造基站降级加密 | 强制 NAS 高优先级算法、网络拒绝弱算法 |
| USIM 物理提取 | 设备被拆解后取出 USIM | 嵌入式 eSIM + 焊死封装 |
| 核心网攻击 | NB-IoT 后端 API 暴露 | API 网关、签名校验、限流 |
| 控制平面优化信令滥用 | CP 优化模式小包易被滥用做信令风暴 | 网络侧速率限制、行为基线 |

---

## 五、Sigfox 安全机制分析

### 5.1 Sigfox 安全模型

Sigfox 采用极简安全模型，主要依赖：
- **设备 ID（DevID）+ PAC（Porting Authorization Code）**：设备身份与入网凭证
- **应用层载荷不加密**：默认明文，由应用自行加密
- **MIC 校验**：基于设备密钥生成 2-4 字节 MAC

### 5.2 安全局限性

| 局限 | 影响 |
|------|------|
| 无端到端加密 | 任何网关/后端可见明文 |
| MIC 仅 2-4 字节 | 碰撞空间小，易伪造 |
| 单向上行为主 | 下行确认能力弱，难以做双向认证 |
| 密钥静态 | 密钥更新困难 |
| 每日消息上限 | 难以做密钥协商 |

**风险评估：** Sigfox 适用于低价值、非敏感数据（如垃圾桶满度），不适合个人隐私或关键控制场景。

### 5.3 应用层加固建议

由于协议层保护薄弱，应在应用层补强：
- 应用层 AES 加密（设备与云共享对称密钥）
- 应用层 HMAC 完整性
- 时间戳 + 序列号防重放
- 异常行为监测（位置跳变、消息频率突变）

---

## 六、LoRaWAN 安全测试方法与工具

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

## 七、边缘计算安全概述

### 7.1 边缘计算架构

```
┌──────────────────────────────────────────────────────────┐
│                    云中心 (Cloud)                          │
│   全局分析 / 模型训练 / 长期存储 / 跨域协同               │
└──────────────────────────┬───────────────────────────────┘
                           │ 边云协同
┌──────────────────────────┴───────────────────────────────┐
│                   边缘节点 (Edge Node)                    │
│   网关 / 边缘服务器 / 边缘 AI 推理                        │
│   本地实时处理 / 数据过滤 / 协议转换                      │
└──────────────────────────┬───────────────────────────────┘
                           │
┌──────────────────────────┴───────────────────────────────┐
│                   边缘设备 (Edge Device)                  │
│   摄像头 / 传感器 / 工业控制器 / 智能终端                 │
└──────────────────────────────────────────────────────────┘
```

### 7.2 边缘安全的三大层面

| 层面 | 关注点 |
|------|--------|
| 边缘架构安全 | 边云协同通道、边缘节点准入、信任根传递 |
| 边缘节点安全 | 边缘网关/服务器加固、容器安全、运行时防护 |
| 边缘数据安全 | 数据采集、传输、存储、脱敏、生命周期 |
| 边缘 AI 安全 | 模型保护、推理安全、对抗样本防御 |

### 7.3 边缘计算安全特点（与云对比）

```
云安全                          边缘安全
集中式防护                      分布式防护
可信机房                        开放/物理暴露
算力充足                        资源受限
补丁集中                        补丁碎片化
攻击面相对集中                  攻击面广泛
```

> 边缘设备物理暴露是边缘安全的核心挑战：攻击者可直接接触设备，绕过网络层防护。因此边缘安全必须从"信任根"做起，硬件信任根 + 安全启动是基础。

---

## 八、边缘设备安全

### 8.1 硬件安全

**硬件信任根（Root of Trust）：**
- TPM 2.0 / TCM：可信平台模块，提供密钥存储与度量
- 安全元件（SE）：如 NXP A71CX、ST STSAFE，专用于 IoT 密钥存储
- eFuse / OTP：一次性烧录，存设备唯一密钥
- ARM TrustZone：硬件隔离安全世界与非安全世界

**安全启动（Secure Boot）链：**
```
ROM Bootloader (不可改)
   ↓ 校验 BL1 签名
Bootloader BL1
   ↓ 校验内核签名
Kernel
   ↓ 校验 rootfs 签名
Rootfs + 应用
```

任一环节签名校验失败即拒绝启动，防止固件被替换为恶意版本。

### 8.2 固件安全

| 威胁 | 描述 | 防护 |
|------|------|------|
| 固件提取 | 拆解设备读 Flash | RDP Level 2、Flash 加密 |
| 固件篡改 | 注入后门再刷入 | 签名校验、安全启动 |
| 固件逆向 | 反汇编分析漏洞 | 代码混淆、关键逻辑入 TrustZone |
| OTA 劫持 | 中间人替换固件包 | 签名 + 加密 + 回滚保护 |

**OTA 升级安全设计示例：**
```python
# 边缘设备 OTA 升级流程（伪代码）
import hashlib, nacl.signing, os

class OTAUpdater:
    def __init__(self, vendor_pubkey):
        self.verify_key = nacl.signing.VerifyKey(vendor_pubkey)

    def download_and_verify(self, manifest_url):
        # 1. 下载清单（含版本号、签名、SHA256、URL）
        manifest = self._fetch(manifest_url)
        # 2. 校验清单签名（防止清单被篡改）
        try:
            self.verify_key.verify(manifest.body, manifest.signature)
        except Exception:
            raise SecurityError("清单签名校验失败")

        # 3. 检查版本回滚保护
        if manifest.version <= self.current_version:
            raise SecurityError("拒绝版本回滚")

        # 4. 下载固件并校验 SHA256
        fw = self._fetch(manifest.fw_url)
        if hashlib.sha256(fw).hexdigest() != manifest.sha256:
            raise SecurityError("固件哈希不匹配")

        # 5. 写入备用分区，等待切换
        self._write_to_inactive_partition(fw)
        return True

    def activate(self):
        # 6. 切换启动分区，重启进入新固件
        # 失败可回滚到旧分区
        self._set_boot_partition("inactive")
        os.reboot()
```

### 8.3 容器安全（边缘节点）

边缘节点常以容器方式部署应用，容器安全要点：
- **基础镜像最小化**：使用 distroless / alpine，减小攻击面
- **签名镜像**：cosign 签名验证
- **非特权运行**：禁止 root，设置 readOnlyRootFilesystem
- **能力裁剪**：drop ALL，按需 add
- **网络策略**：NetworkPolicy 限制东西向流量
- **运行时防护**：Falco 检测异常行为

**Pod 安全基线示例（Kubernetes）：**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: edge-inference
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 10001
    fsGroup: 10001
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: inference
    image: registry.example.com/edge-infer@sha256:abc...   # 固定摘要
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
        add: ["NET_BIND_SERVICE"]
    resources:
      limits:
        memory: "256Mi"
        cpu: "500m"
    volumeMounts:
    - name: tmp
      mountPath: /tmp
    - name: model
      mountPath: /models
      readOnly: true
  volumes:
  - name: tmp
    emptyDir: {}
  - name: model
    secret:
      secretName: edge-model-v1
```

**Falco 检测规则示例：**
```yaml
# 检测容器内异常 shell 启动
- rule: Shell Spawned in Container
  desc: 检测容器内启动 shell，可能是攻击者入侵
  condition: >
    spawned_process and container and
    proc.name in (bash, sh, ash, zsh, ksh)
  output: >
    容器内启动 shell (user=%user.name container=%container.name
    image=%container.image.repository cmd=%proc.cmdline)
  priority: WARNING
  tags: [container, shell, mitre_execution]
```

---

## 九、边缘 AI 安全

### 9.1 边缘 AI 威胁模型

```
┌──────────────────────────────────────────────────────┐
│               边缘 AI 安全威胁                          │
├──────────────┬───────────────┬────────────────────────┤
│   模型安全    │   推理安全     │   数据安全              │
│ - 模型窃取    │ - 对抗样本     │ - 训练数据投毒          │
│ - 模型篡改    │ - 模型逆向     │ - 推理数据泄露          │
│ - 后门植入    │ - 推理劫持     │ - 隐私泄露              │
└──────────────┴───────────────┴────────────────────────┘
```

### 9.2 模型保护

**模型加密存储：** 模型文件以加密形式存储，运行时由可信执行环境（TEE）解密加载。

```python
# 边缘 AI 模型加密存储示例
from cryptography.fernet import Fernet
import tensorflow as tf

class SecureModelLoader:
    def __init__(self, key_path, enc_model_path):
        with open(key_path, "rb") as f:
            self.key = f.read()
        self.enc_model_path = enc_model_path

    def load(self):
        # 1. 读取加密模型
        with open(self.enc_model_path, "rb") as f:
            enc_data = f.read()
        # 2. 解密（密钥由硬件 SE 提供，不在内存长期驻留）
        fernet = Fernet(self.key)
        plain = fernet.decrypt(enc_data)
        # 3. 加载到内存（运行时受 TrustZone 保护）
        import io, h5py
        with h5py.File(io.BytesIO(plain), "r") as h5:
            return tf.keras.models.load_model(h5)

    def zeroize(self, buf):
        # 使用后清零，减少密钥/模型驻留时间
        for i in range(len(buf)):
            buf[i] = 0
```

**模型签名与完整性校验：**
```python
import hashlib, nacl.signing

def verify_model_integrity(model_path, expected_hash, vendor_pubkey, sig):
    # 1. 哈希校验
    h = hashlib.sha256()
    with open(model_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    if h.hexdigest() != expected_hash:
        raise SecurityError("模型哈希不匹配")
    # 2. 签名校验
    vk = nacl.signing.VerifyKey(vendor_pubkey)
    vk.verify(h.digest(), sig)
```

### 9.3 推理安全

**对抗样本防御：**
- 输入预处理：去噪、量化、随机化
- 检测层：对输入做异常分布检测，拒绝可疑输入
- 对抗训练：训练时加入对抗样本提升鲁棒性
- 模型集成：多模型投票，降低单模型脆弱性

```python
# 对抗样本检测（基于输入分布偏移）
import numpy as np

class AdversarialDetector:
    def __init__(self, baseline_stats):
        # baseline_stats: 训练集特征的均值/方差
        self.mu = baseline_stats["mean"]
        self.sigma = baseline_stats["std"]

    def is_suspicious(self, x, threshold=3.0):
        # 马氏距离检测输入偏离训练分布
        diff = x - self.mu
        maha = np.sqrt(np.sum((diff / (self.sigma + 1e-6)) ** 2))
        return maha > threshold

    def sanitize(self, x):
        # 输入预处理：量化 + 噪声注入
        x_q = np.round(x * 255) / 255.0
        x_noisy = x_q + np.random.normal(0, 0.01, x.shape)
        return x_noisy
```

### 9.4 推理数据隐私

**联邦学习与差分隐私：**
- 联邦学习：原始数据不出边缘，仅上传模型梯度
- 差分隐私：在梯度中注入噪声，防止单样本逆向

```python
# 边缘侧差分隐私训练示例（简化）
import torch

def dp_sgd_step(model, x, y, lr=0.01, epsilon=1.0, clip=1.0):
    model.zero_grad()
    out = model(x)
    loss = torch.nn.functional.cross_entropy(out, y)
    loss.backward()
    # 1. 梯度裁剪
    torch.nn.utils.clip_grad_norm_(model.parameters(), clip)
    # 2. 注入噪声（满足 (ε,δ)-DP）
    sigma = clip / epsilon
    for p in model.parameters():
        if p.grad is not None:
            noise = torch.randn_like(p.grad) * sigma
            p.grad += noise
    # 3. 更新
    with torch.no_grad():
        for p in model.parameters():
            p -= lr * p.grad
```

---

## 十、边缘计算与云计算协同安全

### 10.1 边云协同通道安全

```
边缘节点                          云中心
   │                                │
   │═══ mTLS 双向认证隧道 ══════════│
   │     (证书轮换 / 短期证书)       │
   │                                │
   │── 模型/策略下发（签名+加密）──→ │
   │←── 告警/数据上行（加密） ────── │
```

**安全要求：**
- 双向 TLS 认证（mTLS）：边缘与云互验证书
- 短期证书 + 自动轮转：证书有效期 ≤ 24 小时，由云端签发
- 消息级签名：关键指令（模型下发、策略下发）二次签名校验
- 通道隔离：管理通道、数据通道、控制通道分离

### 10.2 零信任与边缘接入

**边缘设备接入云的零信任流程：**
```
1. 设备身份：基于设备证书 + TPM 度量值
2. 持续评估：每 N 分钟重新评估设备状态
3. 最小权限：仅授予当前任务所需的最小数据访问范围
4. 微分段：不同边缘设备群组之间默认不可达
```

**SPIFFE/SPIRE 边缘身份示例：**
```yaml
# SPIRE 注册条目（边缘设备）
- spiffeID: spiffe://example.com/edge/device-001
  parent: spiffe://example.com/edge/node-attester
  selectors:
    - TPM:AKM: "f1d2...e3a7"          # TPM 度量值绑定
    - serial: "EDGE-SN-2026-001"
  ttl: 3600                              # 短期身份
```

### 10.3 边云数据一致性安全

**模型下发完整性校验链：**
```
云端训练完成
    ↓ 签名模型
云端签名服务
    ↓ 通过 mTLS 通道下发
边缘节点接收
    ↓ 校验签名 + 版本
边缘推理服务加载
    ↓ 度量上报
云端持续监测
```

任一环节失败：拒绝加载 + 上报告警 + 回滚到上一可信版本。

### 10.4 边云协同的常见攻击与防御

| 攻击 | 描述 | 防御 |
|------|------|------|
| 通道中间人 | 劫持边云通信 | mTLS + 证书钉扎 |
| 模型下发篡改 | 替换下发模型 | 签名校验 + 哈希绑定 |
| 边缘身份伪造 | 仿冒边缘设备接入云 | TPM 度量 + 设备证书 |
| 梯度投毒 | 恶意边缘上传毒梯度 | 梯度裁剪、异常检测、信誉评分 |
| 边缘横向移动 | 攻破一个边缘节点后跳板 | 微分段、网络策略、零信任 |

---

## 十一、安全最佳实践

### 11.1 LPWAN 安全清单

**LoRaWAN：**
- [ ] 优先使用 OTAA 入网，避免 ABP
- [ ] 使用 v1.1 协议，享受细分密钥体系
- [ ] 关键密钥存入安全元件（SE），禁止主 MCU 明文存储
- [ ] 网络服务器持久化 FCntUp，防计数器回退重放
- [ ] 设备物理防拆 + tamper 检测
- [ ] 固件加密 + 安全启动 + 防回滚
- [ ] 应用层载荷加密（AppSKey），关键数据再加应用层 HMAC

**NB-IoT：**
- [ ] 使用 eSIM + 焊死封装，防 USIM 拔出
- [ ] 禁用弱加密算法，强制 EEA2/AES-128
- [ ] 后端 API 网关 + 签名 + 限流，防信令风暴
- [ ] 监测 IMSI 附着异常，识别伪基站攻击

**Sigfox：**
- [ ] 仅用于低价值、非敏感数据
- [ ] 应用层自行加密 + HMAC + 时间戳防重放
- [ ] 后端异常行为监测（位置/频率突变）

### 11.2 边缘计算安全清单

- [ ] 硬件信任根：TPM/SE/TrustZone 作为安全基础
- [ ] 安全启动链：ROM → BL → Kernel → rootfs 全链签名
- [ ] 固件 OTA：签名 + 加密 + 防回滚 + 备用分区
- [ ] 容器最小化：distroless 镜像 + 非特权 + 能力裁剪
- [ ] 运行时防护：Falco/Tracee 检测异常行为
- [ ] 边云 mTLS：短期证书 + 自动轮转
- [ ] 模型保护：加密存储 + 签名校验 + TEE 推理
- [ ] 推理安全：对抗样本检测 + 输入预处理
- [ ] 隐私保护：联邦学习 + 差分隐私
- [ ] 零信任接入：SPIFFE 身份 + 持续评估

### 11.3 监测与响应基线

```
┌──────────────────────────────────────────────────────────┐
│              LPWAN + 边缘安全监测架构                      │
├──────────────────────────────────────────────────────────┤
│  边缘侧                                                  │
│   - 设备行为基线（通信频率、位置、电量）                  │
│   - 容器运行时事件（Falco）                              │
│   - 射频异常（RSSI/PER/Jamming 检测）                    │
├──────────────────────────────────────────────────────────┤
│  通道侧                                                  │
│   - mTLS 异常（证书失败、握手频率）                       │
│   - 边云消息签名校验                                     │
├──────────────────────────────────────────────────────────┤
│  云侧                                                    │
│   - 设备群组行为聚合（异常集群检测）                      │
│   - 模型推理分布偏移                                     │
│   - SOC 告警 + SOAR 自动响应                             │
└──────────────────────────────────────────────────────────┘
```

### 11.4 应急响应要点

- 设备密钥泄露：远程吊销 + 群组密钥轮转 + 物理回收
- 边缘节点失陷：隔离该节点、阻断边云通道、回滚固件与模型
- 模型被投毒：回滚到上一可信版本、重训 + 梯度异常审计
- Jamming 攻击：定位干扰源、切换频段/网关、触发监管投诉

---

## 十二、学习建议与参考资料

### 12.1 学习路径建议

1. 先掌握 LoRaWAN 协议规范（特别是密钥体系与 Join 流程）
2. 对照 NB-IoT 的 3GPP 安全机制，理解蜂窝 IoT 安全继承
3. 用 HackRF + URH 实操 LoRa 抓包与解码
4. 搭建 Chirpstack 测试网络，跑通 OTAA 入网与密钥派生
5. 学习边缘安全：TPM/SE → 安全启动 → 容器加固 → 边云 mTLS
6. 进阶边缘 AI 安全：模型加密、对抗样本、联邦学习

### 12.2 关键参考资料

- LoRa Alliance：LoRaWAN Specification v1.0.4 / v1.1
- 3GPP TS 33.401 / 33.402（EPS 安全）
- 3GPP TS 33.501（5G 安全，SUCI 隐私）
- NIST SP 800-213 / 800-213A（IoT 设备安全基线）
- GSMA IoT Big Data 安全指南
- ENISA《Baseline Security Recommendations for IoT》
- OWASP IoT Top 10
- MITRE ATT&CK for IoT

### 12.3 实践清单

- [ ] 用 HackRF 抓一次 LoRa 上行帧并解码 DevAddr
- [ ] 搭建 Chirpstack 网络，跑通一次 OTAA 入网
- [ ] 实现一个 LoRaWAN MIC 计算的小工具
- [ ] 用 Falco 跑通容器异常 shell 检测
- [ ] 用 cosign 给一个容器镜像签名并验证
- [ ] 用 mTLS 搭建一次边云双向认证通道
- [ ] 训练一个简单对抗样本并观察边缘模型误判
- [ ] 实现 OTA 升级的签名 + 哈希双校验流程

---

## 十三、总结

LPWAN 与边缘计算共同构筑了物联网"端—边—云"的物理与计算基础，其安全特点是：

- **资源极度受限**：终端算力、电量、带宽都紧张，传统 IT 安全机制难以直接迁移
- **物理暴露广泛**：设备部署在开放环境，物理攻击是常态而非例外
- **协议多样且脆弱**：LoRaWAN/NB-IoT/Sigfox 安全模型差异大，需对症下药
- **边云协同引入新攻击面**：通道劫持、模型下发篡改、梯度投毒等新型威胁

安全建设的核心思路是：**硬件信任根为基、协议层与应用层双重加固、边云协同全程可验证、持续监测与响应闭环**。掌握这些技术的关键在于动手实践：用 SDR 抓包分析 LoRaWAN、搭建 Chirpstack 测试网络、用 Falco 跑容器运行时检测、用 mTLS 打通边云通道。建议先从 LoRaWAN 协议规范和一次完整的 OTAA 入网实验入手，逐步扩展到边缘安全与边缘 AI 安全，形成端到端的安全工程能力。
