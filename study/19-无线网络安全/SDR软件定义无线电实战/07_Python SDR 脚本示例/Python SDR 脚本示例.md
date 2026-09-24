# Python SDR 脚本示例

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

---

