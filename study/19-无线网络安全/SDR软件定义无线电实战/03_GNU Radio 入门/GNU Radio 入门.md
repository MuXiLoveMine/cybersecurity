# GNU Radio 入门

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

---

