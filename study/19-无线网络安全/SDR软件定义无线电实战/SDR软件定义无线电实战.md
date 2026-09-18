# SDR 软件定义无线电实战

> 软件定义无线电（SDR）是无线安全研究的基础工具，通过软件替代传统硬件电路实现信号收发与处理。本文档系统讲解 SDR 原理、硬件选型、GNU Radio 流图构建、信号分析、协议逆向及安全应用，仅用于安全教育与防御研究目的。

---

## 目录

1. [SDR 概述](#一sdr-概述)
2. [无线信号基础](#二无线信号基础)
3. [GNU Radio 入门](#三gnu-radio-入门)
4. [无线信号分析](#四无线信号分析)
5. [无线协议逆向](#五无线协议逆向)
6. [SDR 安全应用](#六sdr-安全应用)
7. [Python SDR 脚本示例](#七python-sdr-脚本示例)

---

## 一、SDR 概述

### 1.1 软件定义无线电原理

```
传统无线电 vs 软件定义无线电：

传统无线电：
天线 → RF前端 → 混频器 → 硬件解调器 → 音频输出
         │            │          │
      固定滤波     固定本振     固定解调（AM/FM 硬件电路）
      
SDR：
天线 → RF前端 → ADC采样 → ┌─────────────────────────┐
         │                         │  软件 DSP 处理          │
      可调谐                    │  ├── 数字下变频          │
      可变带宽                  │  ├── 数字滤波           │
                               │  ├── 解调（AM/FM/FSK...）│
                               │  ├── 协议解码           │
                               │  └── 输出（音频/数据）   │
                               └─────────────────────────┘

核心优势：
├── 灵活性：同一硬件支持多频段、多协议
├── 可编程：通过软件定义信号处理流程
├── 可升级：新协议/新功能仅需更新软件
└── 低成本：替代多个专用无线电设备
```

### 1.2 SDR 硬件对比

```
┌──────────┬──────────┬──────────┬──────────┬──────────────────┐
│ 硬件     │ 频率范围  │ 最大带宽  │ 发射     │ 价格(参考)       │
├──────────┼──────────┼──────────┼──────────┼──────────────────┤
│ RTL-SDR  │ 24-1766   │ 2.4 MHz  │ 仅接收   │ ~$30  入门首选   │
│ HackRF   │ 1-6000    │ 20 MHz   │ 收发     │ ~$300 进阶通用   │
│ BladeRF  │ 47-6000   │ 61 MHz   │ 收发     │ ~$480 高性能     │
│ USRP系列 │ 视型号     │ 56 MHz+  │ 收发     │ ~$1000+ 专业级  │
│ LimeSDR  │ 100k-3.8G │ 61 MHz   │ 收发     │ ~$300 多功能     │
│ PlutoSDR │ 70-6000   │ 56 MHz   │ 收发     │ ~$200 ADI开发板 │
└──────────┴──────────┴──────────┴──────────┴──────────────────┘

选型建议：
├── 入门学习 / 仅接收分析 → RTL-SDR（最经济）
├── 通用研究 / 收发兼备   → HackRF One（性价比高）
├── 高带宽 / MIMO 研究    → BladeRF / USRP
└── 教学/便携            → PlutoSDR
```

### 1.3 SDR 软件生态

```
┌──────────────────────┬────────────────────────────────────────┐
│ 软件                 │ 说明                                    │
├──────────────────────┼────────────────────────────────────────┤
│ GNU Radio            │ 开源 DSP 框架，流图编程，跨平台          │
│ GNU Radio Companion  │ GNU Radio 图形界面，拖拽构建流图         │
│ GQRX                 │ 基于 GNU Radio 的收音机界面             │
│ SDR# (SDRSharp)      │ Windows 平台功能最全的 SDR 软件         │
│ Universal Radio Hacker│ 无线协议逆向分析工具                   │
│ SDRangel             │ 多通道 SDR 接收软件                     │
│ urh (Universal Radio │ 信号录制/分析/重放（教育用途）          │
│   Hacker)            │                                         │
│ Inspectrum           │ 信号频谱/波形分析工具                   │
│ QSpectrumAnalyzer    │ 频谱分析仪（基于 RTL-SDR）             │
│ rtl_433              │ 433MHz 设备协议解码器                   │
└──────────────────────┴────────────────────────────────────────┘
```

---

## 二、无线信号基础

### 2.1 电磁波与调制

```
调制：将信息（基带信号）加载到载波上

载波信号：c(t) = A · cos(2π·f·t + φ)
              ↑      ↑        ↑      ↑
            振幅    频率    时间    相位

调制方式：
├── AM（调幅）     → 改变振幅 A 携带信息
│   s(t) = [1 + m·x(t)] · cos(2π·f·t)
├── FM（调频）     → 改变频率 f 携带信息
│   s(t) = A · cos(2π·[f + Δf·x(t)]·t)
├── FSK（频移键控） → 离散频率变化表示 0/1
│   f1 = '0', f2 = '1'
├── PSK（相移键控） → 离散相位变化表示 0/1
│   BPSK: 0° = '0', 180° = '1'
│   QPSK: 4种相位 → 2 bit/符号
│   8PSK: 8种相位 → 3 bit/符号
└── ASK（幅移键控） → 离散振幅变化表示 0/1
    OOK（通断键控）= ASK 特例：有载波=1，无载波=0
```

### 2.2 频率与带宽

```
常见无线频段：

┌──────────────────┬──────────────┬──────────────────────┐
│ 频段             │ 频率范围      │ 典型应用             │
├──────────────────┼──────────────┼──────────────────────┤
│ AM 广播          │ 530-1710 kHz  │ AM 电台              │
│ 短波             │ 3-30 MHz     │ 国际广播/业余电台    │
│ FM 广播          │ 88-108 MHz   │ FM 电台              │
│ VHF 电视         │ 174-216 MHz  │ 模拟/数字电视        │
│ 航空             │ 118-137 MHz  │ 航空通信             │
│ AIS              │ 161-162 MHz  │ 船舶自动识别         │
│ 业余无线电        │ 144/430 MHz  │ Ham Radio           │
│ ISM 433          │ 433.05-434.79│ 车钥匙/门铃/传感器  │
│ LTE/4G           │ 700-2600 MHz │ 移动通信             │
│ ISM 2.4GHz       │ 2400-2483    │ WiFi/蓝牙/微波       │
│ ISM 5GHz         │ 5150-5875    │ WiFi 5GHz           │
│ GNSS             │ 1575/1227    │ GPS/北斗             │
│ ADS-B            │ 1090 MHz     │ 飞机广播             │
└──────────────────┴──────────────┴──────────────────────┘

带宽：信号占用的频率范围
├── 窄带信号  → 带宽小，信号集中（如 NBFM 对讲机 12.5kHz）
├── 宽带信号  → 带宽大，信息量大（如 WiFi 20MHz+）
└── 采样率    → 必须 ≥ 2×信号带宽（奈奎斯特采样定理）
```

### 2.3 IQ 采样与处理

```
IQ 采样（复基带采样）：

射频信号 → 下变频 → I/Q 两路
                    │     │
                 同相分量(I) 正交分量(Q)

I/Q 数据表示复数：s(t) = I(t) + j·Q(t)

优势：
├── 保留相位信息（幅度+相位）
├── 中心频率可移至 0Hz（基带）
├── 采样率仅需信号带宽（非 2×载频）
└── 可用复数 DSP 算法处理

RTL-SDR 输出格式：
├── 每个采样点 2 字节：1字节 I + 1字节 Q
├── 数据类型：int8（-128~127）
├── 采样率：最高 2.4 MHz
└── 数据流：[I0, Q0, I1, Q1, I2, Q2, ...]

功率计算：
P(dBFS) = 10·log10(I² + Q²)
P(dBm) = P(dBFS) + calibration_offset
```

---

## 三、GNU Radio 入门

### 3.1 GNU Radio Companion 界面

```
GNU Radio Companion (GRC) 界面：

┌─────────────────────────────────────────────────────┐
│  菜单栏                                              │
├──────────┬──────────────────────────────────────────┤
│ 模块库    │           流图画布                        │
│          │                                          │
│ Sources  │   ┌────────┐    ┌────────┐    ┌────────┐│
│ ├ RTL-SDR│   │RTL-SDR │───→│ Low    │───→│ Audio  ││
│ ├ File   │   │Source  │    │ Pass   │    │ Sink   ││
│ ├ Audio  │   └────────┘    │ Filter │    └────────┘│
│ │ Source │                 └────────┘              │
│ Sinks    │                                          │
│ ├ Audio  │     绿线 = 数据流连接                     │
│ ├ File   │     数据流从左到右流动                     │
│ ├ FFT    │                                          │
│ Filters  │                                          │
│ ├ Low    │                                          │
│ │ Pass   │                                          │
│ ├ High   │                                          │
│ ├ Band   │                                          │
│ Mod/Demod│                                          │
│ ├ FM Demod│                                         │
│ ├ AM Demod│                                         │
│ ...      │                                          │
├──────────┴──────────────────────────────────────────┤
│  控制台输出                                          │
└─────────────────────────────────────────────────────┘
```

### 3.2 常用模块

```
Signal Sources（信号源）
├── RTL-SDR Source    → RTL-SDR 接收信号
├── HackRF Source     → HackRF 接收
├── File Source       → 从文件读取 IQ 数据
├── Signal Source     → 生成测试信号（正弦/方波/噪声）
└── Audio Source      → 麦克风输入

Sinks（输出端）
├── Audio Sink        → 输出到声卡（听声音）
├── File Sink         → 保存 IQ 数据到文件
├── FFT Sink          → 频谱图显示
├── Waterfall Sink    → 瀑布图显示
├── Time Sink         → 时域波形显示
└── Constellation Sink → 星座图（QPSK/QAM 等）

Filters（滤波器）
├── Low Pass Filter    → 低通滤波
├── High Pass Filter   → 高通滤波
├── Band Pass Filter   → 带通滤波
├── Rational Resampler → 重采样（改变采样率）
└── Freq Xlating FFT   → 频率搬移

Demodulators（解调器）
├── WBFM Receive       → 宽带 FM 解调（FM 电台）
├── NBFM Receive       → 窄带 FM 解调（对讲机）
├── AM Demod           → AM 解调
├── FSK Demodulator    → FSK 解调
└── Constellation Decoder → PSK/QAM 解调
```

### 3.3 流图构建实例：FM 收音机

```
FM 收音机流图：

RTL-SDR Source → Low Pass Filter → WBFM Demod → Rational Resampler → Audio Sink
     │                  │              │              │
  频率: 100MHz       截止: 80kHz     FM解调        48kHz 重采样 → 声卡输出
  采样率: 2.4MHz    增益: 自动
  增益: 自动

GRC 中的等效 Python 代码：

gr.flowgraph → FlowGraph
├── blocks.rtl_source(samp_rate=2.4e6, freq=100e6, gain='auto')
├── blocks.low_pass_filter(samp_rate=2.4e6, cutoff=80e3, transition=10e3)
├── blocks.wfmrcv(quadrature_rate=2.4e6)
├── blocks.rational_resampler(interp=5, decimation=250)  # → 48kHz
└── blocks.audio_sink(samp_rate=48e3)
```

### 3.4 Python Block 开发

```python
#!/usr/bin/env python3
"""
GNU Radio Python Block 示例
功能：自定义信号处理块 - 简易功率计
仅用于教育目的。
"""

import numpy as np
from gnuradio import gr


class PowerMeter(gr.sync_block):
    """计算并输出信号功率（dBFS）"""

    def __init__(self, interval=1000):
        gr.sync_block.__init__(
            self,
            name='Power Meter',
            in_sig=[np.complex64],  # IQ 复数输入
            out_sig=None             # 无输出（仅显示）
        )
        self.interval = interval
        self.count = 0
        self.power_sum = 0.0

    def work(self, input_items, output_items):
        in0 = input_items[0]
        n = len(in0)

        # 计算功率：P = mean(|s|²) = mean(I² + Q²)
        power = np.mean(np.abs(in0) ** 2)

        # 累积平均
        self.power_sum += power * n
        self.count += n

        # 定期输出
        if self.count >= self.interval:
            avg_power = self.power_sum / self.count
            avg_power_db = 10 * np.log10(avg_power + 1e-10)  # dBFS
            print(f'信号功率: {avg_power_db:.2f} dBFS')
            self.count = 0
            self.power_sum = 0.0

        return n
```

---

## 四、无线信号分析

### 4.1 FM/AM 收音机解调

```
FM 信号解调流程：

天线 → RTL-SDR → 下变频 → 低通滤波 → FM鉴频 → 去加重 → 音频输出
                    ↓
              中心频率 100MHz
              带宽 200kHz

FM 鉴频原理：
s(t) = A·cos(2π·f(t)·t)
f(t) = f_c + Δf·x(t)  → x(t) 是基带信号

鉴频 = d(phase)/dt = d(arctan(Q/I))/dt

Python 等效：
phase = np.arctan2(Q, I)
demod = np.diff(phase) / (2π·dt)
```

```python
# Python - 简易 FM 解调（使用 RTL-SDR）
import numpy as np

def fm_demodulate(iq_samples, sample_rate=2.4e6):
    """FM 信号解调
    iq_samples: 复数 IQ 采样数据
    sample_rate: 采样率
    """
    # 1. 低通滤波（选台后滤除带外噪声）
    from scipy.signal import butter, lfilter
    b, a = butter(5, 100e3 / (sample_rate / 2), btype='low')
    filtered = lfilter(b, a, iq_samples)

    # 2. FM 鉴频（相位差分）
    phase = np.angle(filtered)
    demod = np.diff(phase) / (2 * np.pi / sample_rate * sample_rate)

    # 3. 降采样到音频采样率（48kHz）
    decimation = int(sample_rate / 48000)
    audio = demod[::decimation]

    # 4. 归一化
    audio = audio / np.max(np.abs(audio)) * 0.8
    return audio
```

### 4.2 ADS-B 飞机信号接收

```
ADS-B（Automatic Dependent Surveillance-Broadcast）：
├── 频率：1090 MHz
├── 调制：PPM（脉冲位置调制）
├── 速率：1 Mbit/s
├── 内容：飞机位置/高度/速度/航班号
└── 功率：低功率广播（数百公里可见）

信号格式：
├── 前导码：8μs（2个脉冲对）
├── 数据块：112 bit（112μs）
│   ├── DF（Downlink Format）: 5 bit
│   ├── CA（Capability）: 3 bit
│   ├── ICAO地址: 24 bit（飞机唯一标识）
│   ├── ME（Message）: 56 bit（位置/速度/识别等）
│   └── PI（Parity）: 24 bit
└── 总长：120μs

工具：dump1090 / readsb / rtl_adsb

# 使用 dump1090 接收 ADS-B
dump1090 --device-index 0 --gain 49.6 --freq 1090000000
# 输出：航班号/位置/高度/速度，可在地图上显示
```

### 4.3 气象卫星图像接收

```
气象卫星（NOAA 系列）：
├── 频率：137 MHz（NOAA-15: 137.620, NOAA-18: 137.9125, NOAA-19: 137.100）
├── 调制：APT（Automatic Picture Transmission）
├── 信号：模拟调频，带宽 ~40 kHz
├── 图像：每帧包含红外+可见光两个通道
├── 轨道：极轨卫星，每天经过数次
└── 工具：WXtoImg / SatDump / noaa-apt

接收流程：
1. 计算卫星过境时间（使用 gpredict / Orbitron）
2. RTL-SDR 频率设为对应卫星频率
3. 接收 10-15 分钟（一次完整过境）
4. 调频解调 → 音频文件
5. APT 解码软件生成图像

# 录制气象卫星信号
rtl_fm -d 0 -f 137.620e6 -s 48000 -g 49.6 -E dc noaa15.wav
# WXtoImg 解码
wxtoimg -t noaa noaa15.wav noaa15.png
```

### 4.4 车钥匙信号分析（433MHz）

```
车钥匙/遥控器（433MHz ISM 频段）：
├── 频率：433.92 MHz（中国/欧洲）/ 315 MHz（美国）
├── 调制：OOK / ASK / FSK
├── 协议：滚动码（Keeloq等）/ 固定码
├── 数据率：1-10 kbit/s
└── 工具：rtl_433 / Universal Radio Hacker

rtl_433 解码支持协议：
├── 温湿度传感器（Oregon/Acurite/...）
├── 车钥匙（Keeloq 滚动码）
├── 车库门遥控
├── 无线门铃
└── 智能电表

# rtl_433 解码 433MHz 信号
rtl_433 -d 0 -f 433.92e6 -s 250000 -G   # JSON 输出 + 灵活通用解码器
```

### 4.5 蓝牙/Wi-Fi 信号捕获

```
蓝牙（2.4 GHz ISM）：
├── 调制：GFSK（BLE） / π/4-DQPSK / 8DPSK（Classic）
├── 跳频：1600 hops/s（Classic），37 频道（BLE）
├── 信道：2402-2480 MHz（40 信道 BLE / 79 信道 Classic）
└── 特点：跳频使连续捕获困难

Wi-Fi（2.4/5 GHz）：
├── 调制：DSSS/CCK（802.11b）, OFDM（802.11a/g/n/ac/ax）
├── 信道带宽：20/40/80/160 MHz
├── 协议：802.11 MAC 帧
└── SDR 限制：RTL-SDR 带宽 2.4MHz 不足以解 Wi-Fi

注意：捕获 Wi-Fi/蓝牙原始信号需高性能 SDR（HackRF/BladeRF）
常规 Wi-Fi 分析推荐使用 monitor 模式网卡 + Wireshark
```

---

## 五、无线协议逆向

### 5.1 信号捕获与录制

```
信号捕获流程：

1. 频率定位
   → 使用 GQRX/SDR# 频谱扫描找到目标信号
   → 记录中心频率、带宽、信号类型

2. 录制 IQ 数据
   → 使用 rtl_sdr / Universal Radio Hacker 录制

# 录制 433MHz 信号 10秒
rtl_sdr -d 0 -f 433.92e6 -s 250000 -g 42 -n 2500000 capture_433.cu8
# -n: 采样点数（2500000/250000 = 10秒）

3. 文件格式
   ├── .cu8  → 复数无符号 8 位（RTL-SDR 默认）
   ├── .cs8  → 复数有符号 8 位
   ├── .cs16 → 复数有符号 16 位
   └── .wav  → 音频格式（已解调）
```

### 5.2 调制方式识别

```
调制识别方法：

频谱特征：
├── 窄带连续谱 → NBFM（对讲机）
├── 宽带连续谱 → WBFM（FM电台）
├── 离散谱线   → ASK/OOK（遥控器）
├── 多峰谱     → FSK（多频移键控）
└── 宽带平坦谱 → DSSS（扩频）

时域特征：
├── 幅度跳变   → OOK/ASK
├── 频率跳变   → FSK
├── 相位突变   → PSK
└── 恒定包络   → FM/FSK/PSK

星座图分析：
├── 2点（实轴）   → BPSK / OOK
├── 4点           → QPSK
├── 圆环分布     → FSK
└── 网格分布     → QAM
```

### 5.3 数据解调

```
Universal Radio Hacker (URH) 解调流程：

1. 导入信号文件
   → File → Open → 选择 .cu8/.cs8 文件

2. 频率分析
   → 自动检测中心频率偏移
   → 调整带宽

3. 调制识别
   → Analyze → 自动识别 ASK/FSK/PSK
   → 或手动选择

4. 解调设置
   ├── Bit Length → 每个比特的采样数
   ├── Error Tolerance → 容错范围
   ├── Center → 判决门限
   └── Data Lock → 锁定位同步

5. 数据解码
   → 输出二进制/十六进制位流
   → 协议字段标注
```

### 5.4 协议分析

```
典型 OOK 协议结构（433MHz 遥控器）：

┌──────┬──────────┬──────────┬──────────┬────────┐
│ 前导 │ 同步码    │ 设备ID    │ 命令码    │ 校验   │
│ 码   │          │          │          │        │
│ 12位 │ 8位      │ 20位     │ 4位      │ 4位    │
└──────┴──────────┴──────────┴──────────┴────────┘

分析步骤：
1. 录制多次信号（同一遥控不同按键）
2. 对比解调数据，找出固定部分和变化部分
3. 固定部分 → 前导码/同步码
4. 变化部分 → 按键对应的命令码
5. 每次变化的部分 → 滚动码（Keeloq等）
6. 校验字段 → CRC/校验和

滚动码分析（仅教育）：
├── 固定码部分不变 → 设备识别码
├── 变化部分每次不同 → 滚动计数器
├── 计数器每次+1 → 防重放
└── 加密算法 → 需逆向芯片固件
```

### 5.5 重放攻击原理（仅教育用途）

```
重放攻击原理（仅用于理解防御需求）：

固定码系统（老旧遥控器）：
├── 每次发送相同的固定码
├── 录制信号 → 重放即可触发
├── 防御：升级为滚动码

滚动码系统（Keeloq 等）：
├── 每次发送不同的加密序列
├── 接收器校验计数器单调递增
├── 简单重放 → 被拒绝（计数器过旧）
├── 滚动码攻击 → 需录制多组 + 密钥逆向
└── 防御：使用强加密 + 前向安全

⚠️ 法律提示：
├── 未经授权录制/重放他人设备信号属于违法行为
├── 本内容仅用于理解安全风险，促进防御设计
├── 实际操作必须在授权环境和自有设备上进行
└── 禁止对他人设备进行任何未授权操作
```

---

## 六、SDR 安全应用

### 6.1 无线门铃/车库门信号分析

```
分析目标：自有无线门铃/车库门

分析步骤：
1. 频率扫描
   → RTL-SDR + GQRX 扫描 433.92MHz 附近
   → 按下门铃按钮观察频谱出现信号

2. 信号录制
   → rtl_sdr 录制原始 IQ 数据
   → 使用 URH 分析

3. 协议解码
   → rtl_433 自动识别已知协议
   → 输出：协议类型、设备ID、状态

# rtl_433 分析
rtl_433 -d 0 -f 433.92e6 -s 250000 -r capture.cu8

安全评估：
├── 固定码？→ 重放风险（建议升级）
├── 滚动码？→ 评估加密强度
├── 信号范围？→ 有效距离多大
└── 干扰容限？→ 抗干扰能力
```

### 6.2 RF 远程控制安全

```
RF 远程控制安全检查项：

┌────────────────┬──────────────────────┬──────────────┐
│ 检查项         │ 安全标准             │ 风险         │
├────────────────┼──────────────────────┼──────────────┤
│ 编码方式       │ 滚动码（Keeloq等）    │ 固定码=高危  │
│ 加密强度       │ AES-128+             │ 弱加密=中危  │
│ 重放保护       │ 计数器+时间窗口       │ 无保护=高危  │
│ 信号范围       │ 合理覆盖范围          │ 过远=中危    │
│ 配对机制       │ 安全配对（非明文）    │ 明文=中危    │
│ 固件更新       │ 安全OTA              │ 无更新=中危  │
└────────────────┴──────────────────────┴──────────────┘
```

### 6.3 IMSI Catcher 原理与检测

```
IMSI Catcher（伪基站）原理：

正常移动通信：
手机 → 基站（运营商）→ 核心网
       ↑ 信号最强基站优先

IMSI Catcher：
手机 → 伪基站（IMSI Catcher）
       ↑ 模拟更强信号吸引手机
       ↓
       获取 IMSI（国际移动用户标识）
       可执行：身份追踪/中间人攻击/短信劫持

检测方法：
├── 信号特征检测
│   → 异常强信号（LAC/CID 不匹配）
│   → 非标准频段/信道
│   → 2G 降级攻击（从 4G 强制降级到 2G）
├── 工具
│   → SDR + srsRAN/OsmocomBB 分析
│   → 手机 App（SnoopSnitch / Cell Spy Catcher）
│   → 专用硬件检测器
└── 检测指标
    → 基站 ID 突变
    → LAC（位置区码）异常
    → 邻区列表异常
    → 信号强度异常波动

⚠️ 注意：搭建 IMSI Catcher 在绝大多数国家/地区属违法行为
        本内容仅用于理解威胁原理与检测方法
```

### 6.4 无线键盘窃听风险

```
无线键盘安全风险：

攻击场景：
├── 2.4GHz 无线键盘（非蓝牙）
│   → 多数使用简单协议 + 固定码或弱加密
│   → SDR 可捕获并解调键盘输入
│   → 按键记录 = 密码/敏感信息泄露
├── 蓝牙键盘
│   → 蓝牙加密提供一定保护
│   → 旧版蓝牙（4.0前）加密可被破解
│   └── 蓝牙 4.2+ LE Secure Connections 较安全

安全建议：
├── 使用有线键盘处理敏感输入
├── 选择蓝牙 4.2+ LE 的键盘
├── 关注键盘厂商安全更新
└── 在敏感场景使用键盘屏蔽器
```

### 6.5 RFID/NFC 分析

```
RFID/NFC 与 SDR 的关系：

RFID 频段：
├── 低频（LF）125kHz    → 门禁卡/宠物芯片
├── 高频（HF）13.56MHz  → NFC/MIFARE
└── 超高频（UHF）860-960MHz → 物流标签

SDR 可分析：
├── LF/HF RFID 信号（需合适天线）
├── NFC 通信（Proxmark3 更专业）
└── UHF 标签

专用工具（比 SDR 更高效）：
├── Proxmark3 → RFID/NFC 全频段分析
├── NFC Reader/Writer → 13.56MHz
└── Flipper Zero → 多功能（含 RFID）
```

---

## 七、Python SDR 脚本示例

### 7.1 RTL-SDR 信号功率扫描脚本

```python
#!/usr/bin/env python3
"""
RTL-SDR 信号功率扫描脚本
功能：扫描指定频率范围，检测信号活动
仅用于教育目的。需安装 pyrtlsdr 块。
合法使用：仅扫描自有设备或已获授权的频段。

安装：pip install pyrtlsdr numpy matplotlib
"""

import numpy as np
from rtlsdr import RtlSdr


def scan_frequency_range(
    start_freq=88e6,
    end_freq=108e6,
    step=0.2e6,
    sample_rate=2.4e6,
    num_samples=256 * 1024,
    gain=40
):
    """扫描频率范围内的信号功率

    参数:
        start_freq: 起始频率 (Hz)
        end_freq: 结束频率 (Hz)
        step: 步进 (Hz)
        sample_rate: 采样率 (Hz)
        num_samples: 每个频率采样点数
        gain: 增益 (dB)
    """
    sdr = RtlSdr()
    sdr.sample_rate = int(sample_rate)
    sdr.gain = gain

    frequencies = []
    powers = []

    freq = start_freq
    while freq <= end_freq:
        sdr.center_freq = int(freq)

        # 读取 IQ 数据
        samples = sdr.read_samples(num_samples)

        # 计算平均功率（dBFS）
        power = np.mean(np.abs(samples) ** 2)
        power_db = 10 * np.log10(power + 1e-15)

        frequencies.append(freq / 1e6)  # MHz
        powers.append(power_db)

        print(f'{freq/1e6:.2f} MHz: {power_db:.1f} dBFS')

        freq += step

    sdr.close()

    # 检测信号峰值
    noise_floor = np.median(powers)
    threshold = noise_floor + 10  # 噪底以上 10dB

    print(f'\n噪声底噪: {noise_floor:.1f} dBFS')
    print(f'检测阈值: {threshold:.1f} dBFS')
    print(f'\n检测到的信号：')

    for f, p in zip(frequencies, powers):
        if p > threshold:
            print(f'  {f:.2f} MHz: {p:.1f} dBFS (高出噪底 {p - noise_floor:.1f} dB)')

    return frequencies, powers


def save_spectrum_data(frequencies, powers, filename='scan_results.csv'):
    """保存扫描数据到 CSV"""
    import csv
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Frequency_MHz', 'Power_dBFS'])
        for freq, power in zip(frequencies, powers):
            writer.writerow([f'{freq:.3f}', f'{power:.1f}'])
    print(f'扫描数据已保存到 {filename}')


if __name__ == '__main__':
    # 扫描 FM 广播频段
    freqs, pows = scan_frequency_range(
        start_freq=88e6,
        end_freq=108e6,
        step=0.2e6,
        sample_rate=2.4e6,
        gain=40
    )
    save_spectrum_data(freqs, pows)
```

### 7.2 简易 FM 解调脚本

```python
#!/usr/bin/env python3
"""
简易 FM 解调脚本
功能：接收 FM 信号并解调为音频
仅用于教育目的。需安装 pyrtlsdr, scipy, sounddevice。

安装：pip install pyrtlsdr scipy sounddevice numpy
合法使用：仅接收 FM 广播等无加密公共信号。
"""

import numpy as np
from scipy.signal import butter, lfilter, resample
from rtlsdr import RtlSdr
import sounddevice as sd


def fm_demod_block(iq_samples, sample_rate=2.4e6):
    """FM 信号解调（逐块处理）

    参数:
        iq_samples: 复数 IQ 数据
        sample_rate: 采样率

    返回:
        音频数据 (48kHz)
    """
    # 1. 低通滤波（限制带宽至 100kHz）
    cutoff = 100e3
    b, a = butter(5, cutoff / (sample_rate / 2), btype='low')
    filtered = lfilter(b, a, iq_samples)

    # 2. FM 鉴频（相位差分法）
    phase = np.unwrap(np.angle(filtered))
    demod = np.diff(phase) / (2 * np.pi)

    # 3. 降采样到 48kHz
    target_samples = int(len(demod) * 48000 / sample_rate)
    audio = resample(demod, target_samples)

    # 4. 归一化
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * 0.8

    return audio.astype(np.float32)


def receive_fm(freq=100e6, duration=10, sample_rate=2.4e6, gain=40):
    """接收 FM 信号并实时播放

    参数:
        freq: FM 频率 (Hz)
        duration: 接收时长 (秒)
        sample_rate: 采样率
        gain: 增益
    """
    sdr = RtlSdr()
    sdr.sample_rate = int(sample_rate)
    sdr.center_freq = int(freq)
    sdr.gain = gain

    print(f'接收 FM 信号: {freq/1e6:.1f} MHz')
    print(f'采样率: {sample_rate/1e6:.1f} MHz')
    print(f'增益: {gain} dB')
    print(f'时长: {duration} 秒')
    print('正在接收...')

    block_size = int(sample_rate * 0.1)  # 100ms 每块
    num_blocks = int(duration / 0.1)

    all_audio = []

    for i in range(num_blocks):
        # 读取 IQ 数据
        samples = sdr.read_samples(block_size)

        # FM 解调
        audio = fm_demod_block(samples, sample_rate)

        all_audio.append(audio)

        # 实时播放
        sd.play(audio, samplerate=48000, blocking=False)

    sd.wait()  # 等待播放完成
    sdr.close()

    # 合并所有音频
    full_audio = np.concatenate(all_audio)
    print(f'接收完成，音频长度: {len(full_audio)/48000:.1f} 秒')

    return full_audio


def save_wav(audio_data, filename='fm_output.wav', sample_rate=48000):
    """保存音频为 WAV 文件"""
    from scipy.io import wavfile
    # 转为 16-bit PCM
    audio_int16 = (audio_data * 32767).astype(np.int16)
    wavfile.write(filename, sample_rate, audio_int16)
    print(f'音频已保存到 {filename}')


if __name__ == '__main__':
    # 接收 FM 100MHz 广播
    audio = receive_fm(
        freq=100e6,       # 100 MHz
        duration=10,       # 10 秒
        sample_rate=2.4e6,
        gain=40
    )
    save_wav(audio, 'fm_100mhz.wav')
```

---

## 附录：SDR 学习资源

```
┌──────────────────────────┬──────────────────────────────────────┐
│ 资源                     │ 说明                                  │
├──────────────────────────┼──────────────────────────────────────┤
│ rtl-sdr.com              │ RTL-SDR 官方博客与教程               │
│ GNU Radio 官方文档       │ gnuradio.org                         │
│ PySDR (py-sdr.com)      │ Python SDR 教程（推荐入门）          │
│ Signals Everywhere       │ SDR YouTube 频道                     │
│ The Hak5 Store           │ SDR 硬件 + 教程                      │
│ Universal Radio Hacker   │ github.com/jopohl/urh                │
│ rtl_433                  │ github.com/merbanan/rtl_433          │
│ RTL-SDR Wiki             │ rtl-sdr.com/wiki                     │
└──────────────────────────┴──────────────────────────────────────┘
```

---

> **免责声明**：本文档仅用于安全教育与防御研究目的。所有内容旨在帮助安全研究人员理解无线通信安全风险，提升物联网和无线设备的安全防护能力。在绝大多数国家/地区，未经授权截获、录制或重放他人无线通信信号属违法行为。所有实际操作必须在授权环境下、仅针对自有设备进行。请务必遵守所在地区无线电管理法规和网络安全法律。
