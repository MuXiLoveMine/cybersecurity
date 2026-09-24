# NFC与RFID基础

### 1.1 RFID概述

RFID (Radio Frequency Identification) 通过无线电波自动识别物体。系统由标签(Tag)和读写器(Reader)组成。

```
RFID系统组成:

  +----------+    无线电波    +----------+
  |  读写器   |<=============>|   标签    |
  | (Reader) |               |  (Tag)   |
  +----+-----+               +----------+
       |
       v
  +----------+
  | 后台系统  |
  +----------+

RFID工作原理:
  1. 读写器发射射频信号
  2. 标签接收能量(被动式)或自带电源(主动式)
  3. 标签返回存储的数据
  4. 读写器接收并解码数据
  5. 数据传送到后台系统处理
```

### 1.2 NFC协议架构

NFC (Near Field Communication) 是基于RFID的短距离无线通信技术，工作频率13.56MHz，通信距离通常<10cm。

```
NFC协议栈:

  +-------------------+
  |     应用层        |  NDEF, RTD
  +-------------------+
  |   读写模式协议     |  Type 1/2/3/4/5 Tag
  +-------------------+
  |    点对点协议      |  LLCP, SNEP
  +-------------------+
  |    传输协议        |  ISO 14443 (A/B), FeliCa, ISO 15693
  +-------------------+
  |    射频层          |  13.56MHz, ASK调制
  +-------------------+

支持的标签类型:
  Type 1: ISO 14443-3A (Topaz)
  Type 2: ISO 14443-3A (Mifare Ultralight)
  Type 3: FeliCa (Sony)
  Type 4: ISO 14443-4 (Mifare DESFire)
  Type 5: ISO 15693 (Vicinity)
```

### 1.3 通信模式

```
NFC三种工作模式:

  1. 读写模式 (Reader/Writer)
     手机 -> 读写NFC标签
     示例: 读取NFC海报信息

  2. 点对点模式 (Peer-to-Peer)
     手机 <-> 手机
     示例: Android Beam分享数据

  3. 卡模拟模式 (Card Emulation)
     手机 -> 读写器
     示例: NFC支付、门禁卡
```

---

---

