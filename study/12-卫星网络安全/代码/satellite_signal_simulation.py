# -*- coding: utf-8 -*-
"""
卫星信号模拟与攻击演示脚本
Satellite Signal Simulation & Attack Demonstration

本脚本用于教学演示目的，包含以下功能：
1. GPS 信号结构模拟 - 模拟 GPS L1 C/A 码信号的生成
2. GPS 欺骗攻击演示 - 演示欺骗攻击的基本原理和效果
3. 信号干扰模拟 - 模拟各种干扰方式及其对信号的影响
4. 信号强度分析 - 分析不同距离和环境下的信号强度
5. 多普勒效应模拟 - 模拟卫星运动产生的多普勒频移

注意：本脚本仅用于学习和研究，不构成实际攻击能力。
      卫星信号的发射和干扰受法律法规严格管制。

依赖库：numpy, matplotlib
安装命令：pip install numpy matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams

# 设置中文字体（根据系统调整）
rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False

# ============================================================
# 第一部分：GPS 信号结构模拟
# ============================================================

class GPSSignalSimulator:
    """
    GPS L1 C/A 码信号模拟器
    
    功能：
    - 生成 GPS C/A 码（Gold 码）
    - 生成导航电文数据
    - 调制生成 GPS L1 信号
    - 计算信号功率谱
    """
    
    def __init__(self, prn_id=1, sampling_rate=10.23e6, carrier_freq=1.57542e9):
        """
        初始化 GPS 信号模拟器
        
        参数：
            prn_id: 卫星 PRN 编号 (1-32)
            sampling_rate: 采样率 (Hz)，默认 10.23 MHz
            carrier_freq: 载波频率 (Hz)，默认 L1 频段 1575.42 MHz
        """
        self.prn_id = prn_id
        self.fs = sampling_rate      # 采样率
        self.fc = carrier_freq       # 载波频率
        self.f_code = 1.023e6        # C/A 码码率 (Hz)
        self.f_nav = 50              # 导航电文速率 (bps)
        self.code_length = 1023      # C/A 码长度 (chip)
        self.code_period = 1e-3      # C/A 码周期 (s)，1ms
        
    def generate_ca_code(self):
        """
        生成 GPS C/A 码（Gold 码）
        
        C/A 码由两个 10 级线性反馈移位寄存器 (LFSR) 生成的 m 序列相乘得到。
        G1 寄存器：特征多项式 x^10 + x^3 + 1
        G2 寄存器：特征多项式 x^10 + x^9 + x^8 + x^6 + x^3 + x^2 + 1
        不同卫星使用不同的 G2 输出抽头相位。
        
        返回：
            ca_code: 1023 位 C/A 码序列（+1/-1 表示）
        """
        # G2 寄存器的相位选择（抽头）- 各 PRN 号对应的两个抽头
        # 这是 GPS 标准定义的，每个 PRN 卫星使用不同的抽头组合
        g2_phase_select = {
            1: [2, 6], 2: [3, 7], 3: [4, 8], 4: [5, 9], 5: [1, 9],
            6: [2, 10], 7: [1, 8], 8: [2, 9], 9: [3, 10], 10: [2, 3],
            11: [3, 4], 12: [5, 6], 13: [6, 7], 14: [7, 8], 15: [8, 9],
            16: [9, 10], 17: [1, 4], 18: [2, 5], 19: [3, 6], 20: [4, 7],
            21: [5, 8], 22: [6, 9], 23: [1, 3], 24: [4, 6], 25: [5, 7],
            26: [6, 8], 27: [7, 9], 28: [8, 10], 29: [1, 6], 30: [2, 7],
            31: [3, 8], 32: [4, 9]
        }
        
        if self.prn_id not in g2_phase_select:
            raise ValueError(f"PRN {self.prn_id} 不存在，PRN 范围为 1-32")
        
        taps = g2_phase_select[self.prn_id]
        
        # 初始化 G1 和 G2 移位寄存器（初始状态全 1）
        g1 = np.ones(10, dtype=int)
        g2 = np.ones(10, dtype=int)
        
        ca_code = np.zeros(self.code_length, dtype=int)
        
        # 生成 1023 个码片
        for i in range(self.code_length):
            # G1 输出
            g1_out = g1[9]
            
            # G2 输出（使用选择的两个抽头异或）
            # 注意：寄存器编号从 1 开始，数组索引从 0 开始
            g2_out = g2[taps[0] - 1] ^ g2[taps[1] - 1]
            
            # C/A 码 = G1 异或 G2
            ca_code[i] = g1_out ^ g2_out
            
            # G1 移位反馈：x^10 + x^3 + 1 => 第 10 位 XOR 第 3 位
            g1_feedback = g1[9] ^ g1[2]
            g1 = np.roll(g1, 1)
            g1[0] = g1_feedback
            
            # G2 移位反馈：x^10 + x^9 + x^8 + x^6 + x^3 + x^2 + 1
            g2_feedback = g2[9] ^ g2[8] ^ g2[7] ^ g2[5] ^ g2[2] ^ g2[1]
            g2 = np.roll(g2, 1)
            g2[0] = g2_feedback
        
        # 将 0/1 转换为 +1/-1（BPSK 调制用）
        ca_code_bpsk = 1 - 2 * ca_code
        
        return ca_code_bpsk
    
    def generate_nav_data(self, duration_ms=20):
        """
        生成模拟导航电文数据
        
        导航电文速率 50 bps，即每 20ms 一个 bit。
        为了简化，这里生成随机比特流。
        
        参数：
            duration_ms: 持续时间 (ms)
        
        返回：
            nav_data: 导航电文比特序列
            num_bits: 比特数
        """
        # 计算比特数：50 bps = 每 20ms 1 bit
        num_bits = int(duration_ms / 20)
        if num_bits < 1:
            num_bits = 1
        
        # 生成随机导航数据（实际 GPS 有特定格式，这里简化）
        # 使用 +1/-1 表示
        nav_data = np.random.choice([-1, 1], size=num_bits)
        
        return nav_data, num_bits
    
    def generate_gps_signal(self, duration_ms=10, snr_db=None, doppler_hz=0):
        """
        生成完整的 GPS L1 C/A 码信号
        
        信号模型：
        s(t) = A * C(t) * D(t) * cos(2π(fc + fd)t + φ)
        其中：
            A: 信号幅度
            C(t): C/A 码
            D(t): 导航电文
            fc: 载波频率
            fd: 多普勒频移
            φ: 初始相位
        
        参数：
            duration_ms: 信号持续时间 (ms)
            snr_db: 信噪比 (dB)，如果为 None 则不加噪声
            doppler_hz: 多普勒频移 (Hz)
        
        返回：
            t: 时间序列
            signal: 生成的 GPS 信号
            ca_code_fine: 采样后的 C/A 码
            nav_data_fine: 采样后的导航电文
        """
        # 时间序列
        n_samples = int(self.fs * duration_ms * 1e-3)
        t = np.arange(n_samples) / self.fs
        
        # 生成 C/A 码
        ca_code = self.generate_ca_code()
        
        # 每个码片的采样点数
        samples_per_chip = int(self.fs / self.f_code)
        
        # 将 C/A 码扩展到采样率（重复每个码片）
        # 计算完整周期数和剩余部分
        num_full_periods = int(duration_ms)  # 每 ms 一个周期
        ca_code_fine = np.tile(np.repeat(ca_code, samples_per_chip), num_full_periods)
        
        # 调整长度以匹配采样数
        if len(ca_code_fine) > n_samples:
            ca_code_fine = ca_code_fine[:n_samples]
        elif len(ca_code_fine) < n_samples:
            ca_code_fine = np.pad(ca_code_fine, (0, n_samples - len(ca_code_fine)), mode='wrap')
        
        # 生成导航电文（每个 bit 持续 20ms）
        nav_data, num_bits = self.generate_nav_data(duration_ms)
        samples_per_bit = int(self.fs / self.f_nav)
        nav_data_fine = np.repeat(nav_data, samples_per_bit)
        
        # 调整导航电文长度
        if len(nav_data_fine) > n_samples:
            nav_data_fine = nav_data_fine[:n_samples]
        elif len(nav_data_fine) < n_samples:
            nav_data_fine = np.pad(nav_data_fine, (0, n_samples - len(nav_data_fine)), mode='edge')
        
        # 生成载波（含多普勒频移）
        carrier = np.cos(2 * np.pi * (self.fc + doppler_hz) * t)
        
        # BPSK 调制：信号 = C/A 码 * 导航电文 * 载波
        # 注意：这里的载波频率很高，实际采样率可能不够，这里做演示用
        # 在真实 SDR 中，通常处理的是基带或低中频信号
        # 为了可视化，我们使用复基带表示
        
        # 使用复基带信号表示（更符合 SDR 处理方式）
        # 复基带：I 路 = C*D，Q 路 = 0（BPSK 只有 I 路）
        baseband_signal = ca_code_fine * nav_data_fine
        
        # 添加噪声
        if snr_db is not None:
            # 计算信号功率
            signal_power = np.mean(np.abs(baseband_signal) ** 2)
            # 计算噪声功率 (SNR = Ps / Pn)
            noise_power = signal_power / (10 ** (snr_db / 10))
            # 生成复高斯白噪声
            noise = np.sqrt(noise_power / 2) * (
                np.random.randn(n_samples) + 1j * np.random.randn(n_samples)
            )
            baseband_signal = baseband_signal + noise
        
        return t, baseband_signal, ca_code_fine, nav_data_fine
    
    def compute_power_spectrum(self, signal, nfft=1024):
        """
        计算信号的功率谱密度（PSD）
        
        参数：
            signal: 输入信号
            nfft: FFT 点数
        
        返回：
            freqs: 频率轴
            psd: 功率谱密度
        """
        # 使用 Welch 方法估计 PSD
        from scipy.signal import welch
        freqs, psd = welch(signal, fs=self.fs, nperseg=nfft, return_onesided=False)
        # 将频率轴移到中心
        freqs = np.fft.fftshift(freqs)
        psd = np.fft.fftshift(psd)
        return freqs, 10 * np.log10(psd + 1e-20)  # 转换为 dB
    
    def ca_code_acquisition(self, received_signal, search_range=511):
        """
        C/A 码捕获（相关峰检测）
        
        使用循环相关法寻找 C/A 码的相位偏移，
        这是 GPS 接收机捕获信号的基本方法。
        
        参数：
            received_signal: 接收信号（复基带）
            search_range: 码相位搜索范围 (chip)
        
        返回：
            code_phase: 检测到的码相位 (chip)
            correlation: 相关结果
            max_corr: 最大相关值
        """
        # 生成本地 C/A 码
        ca_code = self.generate_ca_code()
        samples_per_chip = int(self.fs / self.f_code)
        ca_code_fine = np.repeat(ca_code, samples_per_chip)
        
        # 计算相关（使用 FFT 加速）
        # 循环相关 = IFFT(FFT(signal) * conj(FFT(code)))
        n = len(received_signal)
        m = len(ca_code_fine)
        
        # 补零到相同长度
        fft_size = n + m - 1
        fft_signal = np.fft.fft(received_signal, fft_size)
        fft_code = np.fft.fft(ca_code_fine, fft_size)
        
        # 循环相关
        correlation = np.fft.ifft(fft_signal * np.conj(fft_code))
        correlation = np.abs(correlation[:n])
        
        # 找最大相关峰
        max_idx = np.argmax(correlation)
        max_corr = correlation[max_idx]
        code_phase = max_idx / samples_per_chip
        
        return code_phase, correlation, max_corr


def demo_gps_signal_structure():
    """
    演示一：GPS 信号结构
    
    展示 GPS C/A 码的生成、信号波形和功率谱特征。
    """
    print("=" * 60)
    print("演示一：GPS 信号结构模拟")
    print("=" * 60)
    
    # 创建模拟器（PRN 1 号卫星）
    sim = GPSSignalSimulator(prn_id=1, sampling_rate=10.23e6)
    
    # 生成 C/A 码
    ca_code = sim.generate_ca_code()
    print(f"\nPRN {sim.prn_id} 号卫星 C/A 码：")
    print(f"  码长：{len(ca_code)} chip")
    print(f"  码率：{sim.f_code/1e6:.3f} MHz")
    print(f"  周期：{sim.code_period*1000:.1f} ms")
    print(f"  前 32 个码片：{ca_code[:32].astype(int)}")
    
    # 生成 GPS 信号（10ms）
    t, signal, ca_fine, nav_fine = sim.generate_gps_signal(duration_ms=2, snr_db=10)
    
    print(f"\n生成信号：")
    print(f"  采样率：{sim.fs/1e6:.2f} MHz")
    print(f"  采样点数：{len(t)}")
    print(f"  信号时长：{len(t)/sim.fs*1000:.2f} ms")
    
    # 绘图
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # 子图 1：C/A 码波形（前 20 个码片）
    chips_to_show = 20
    samples_per_chip = int(sim.fs / sim.f_code)
    n_show = chips_to_show * samples_per_chip
    
    ax = axes[0]
    t_plot = t[:n_show] * 1e6  # 转换为微秒
    ax.plot(t_plot, ca_fine[:n_show], 'b-', linewidth=1.5)
    ax.set_title(f'GPS PRN {sim.prn_id} C/A 码波形（前 {chips_to_show} 个码片）')
    ax.set_xlabel('时间 (μs)')
    ax.set_ylabel('幅度')
    ax.set_ylim(-1.5, 1.5)
    ax.grid(True, alpha=0.3)
    
    # 子图 2：基带信号波形（含导航电文）
    ax = axes[1]
    # 显示 2ms 的信号，下采样以便显示
    decimate = 10
    t_plot2 = t[::decimate] * 1e3  # 转换为毫秒
    ax.plot(t_plot2, np.real(signal[::decimate]), 'b-', linewidth=0.5, alpha=0.7)
    ax.plot(t_plot2, nav_fine[::decimate], 'r--', linewidth=1.5, label='导航电文')
    ax.set_title('GPS 复基带信号（实部）与导航电文')
    ax.set_xlabel('时间 (ms)')
    ax.set_ylabel('幅度')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 子图 3：功率谱
    freqs, psd = sim.compute_power_spectrum(signal, nfft=512)
    ax = axes[2]
    ax.plot(freqs / 1e6, psd, 'b-', linewidth=0.5)
    ax.set_title('GPS 信号功率谱密度')
    ax.set_xlabel('频率 (MHz) - 相对基带')
    ax.set_ylabel('功率谱密度 (dB)')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(-2, 2)  # C/A 码主瓣带宽约 2 MHz
    
    plt.tight_layout()
    output_path = 'e:\\cybersecurity\\study\\12-卫星网络安全\\gps_signal_structure.png'
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    print(f"\n信号结构图已保存至：{output_path}")
    plt.close()
    
    # 演示 C/A 码自相关特性
    print(f"\nC/A 码自相关特性：")
    # 生成完整的一个周期 C/A 码
    code_full = np.repeat(ca_code, samples_per_chip)
    # 计算自相关
    autocorr = np.correlate(code_full, code_full, mode='full')
    autocorr = autocorr / np.max(autocorr)
    mid = len(autocorr) // 2
    
    print(f"  自相关峰值：1.0（完全对齐时）")
    print(f"  非对齐时相关值约为 ±1/1023 ≈ ±0.001（接近噪声）")
    print(f"  这是 GPS 能够从噪声中提取信号的关键（扩频增益）")
    
    # 绘制自相关图
    fig, ax = plt.subplots(figsize=(10, 5))
    lag_chips = np.arange(-50, 51)
    lag_samples = lag_chips * samples_per_chip
    autocorr_plot = autocorr[mid + lag_samples[0]:mid + lag_samples[-1] + 1]
    ax.plot(lag_chips, autocorr_plot, 'b-', linewidth=1.5)
    ax.set_title('GPS C/A 码自相关特性（局部放大）')
    ax.set_xlabel('码相位偏移 (chip)')
    ax.set_ylabel('归一化相关值')
    ax.grid(True, alpha=0.3)
    ax.axvline(x=0, color='r', linestyle='--', alpha=0.5, label='对齐位置')
    ax.legend()
    
    output_path2 = 'e:\\cybersecurity\\study\\12-卫星网络安全\\ca_code_autocorrelation.png'
    plt.savefig(output_path2, dpi=100, bbox_inches='tight')
    print(f"自相关特性图已保存至：{output_path2}")
    plt.close()


# ============================================================
# 第二部分：GPS 欺骗攻击演示
# ============================================================

class GPSSpoofingSimulator:
    """
    GPS 欺骗攻击模拟器
    
    功能：
    - 模拟真实 GPS 信号
    - 模拟欺骗 GPS 信号
    - 模拟欺骗攻击过程（中间式欺骗）
    - 分析欺骗攻击对定位的影响
    """
    
    def __init__(self):
        """初始化欺骗攻击模拟器"""
        # GPS 基本参数
        self.c = 299792458  # 光速 (m/s)
        self.fc_l1 = 1575.42e6  # L1 载波频率 (Hz)
        
    def compute_pseudorange(self, sat_pos, rx_pos, rx_clock_bias=0):
        """
        计算伪距
        
        伪距 = 真实距离 + 接收机时钟偏差 * 光速
        
        参数：
            sat_pos: 卫星位置 (x, y, z) [m]
            rx_pos: 接收机位置 (x, y, z) [m]
            rx_clock_bias: 接收机时钟偏差 [s]
        
        返回：
            pseudorange: 伪距 [m]
        """
        true_range = np.sqrt(
            (sat_pos[0] - rx_pos[0]) ** 2 +
            (sat_pos[1] - rx_pos[1]) ** 2 +
            (sat_pos[2] - rx_pos[2]) ** 2
        )
        pseudorange = true_range + rx_clock_bias * self.c
        return pseudorange
    
    def generate_satellite_positions(self, n_sats=8, orbit_height=20200e3):
        """
        生成模拟卫星位置（简化的 MEO 轨道模型）
        
        参数：
            n_sats: 可见卫星数量
            orbit_height: 轨道高度 [m]
        
        返回：
            sat_positions: 卫星位置数组，每行一个卫星 (x, y, z) [m]
        """
        # 简化：在天顶方向均匀分布几颗卫星
        sat_positions = []
        earth_radius = 6371e3  # 地球半径 [m]
        r = earth_radius + orbit_height  # 卫星轨道半径
        
        # 在上半球均匀分布卫星
        for i in range(n_sats):
            # 方位角均匀分布
            azimuth = 2 * np.pi * i / n_sats
            # 仰角 30-75 度（从地平面算起）
            elevation = np.pi / 6 + (np.pi / 3) * (i % 4) / 3
            
            x = r * np.cos(elevation) * np.cos(azimuth)
            y = r * np.cos(elevation) * np.sin(azimuth)
            z = r * np.sin(elevation)
            
            sat_positions.append([x, y, z])
        
        return np.array(sat_positions)
    
    def spoofing_attack_simulation(self, true_pos, spoofed_pos, n_sats=8):
        """
        模拟 GPS 欺骗攻击对定位的影响
        
        原理：
        欺骗者需要为每颗卫星计算一个伪距偏移量，
        使得接收机解算出的位置是欺骗位置而非真实位置。
        
        参数：
            true_pos: 接收机真实位置 (x, y, z) [m]
            spoofed_pos: 欺骗目标位置 (x, y, z) [m]
            n_sats: 可见卫星数
        
        返回：
            sat_positions: 卫星位置
            true_ranges: 真实伪距
            spoofed_ranges: 欺骗伪距
            range_offsets: 伪距偏移量
        """
        # 生成卫星位置
        sat_positions = self.generate_satellite_positions(n_sats)
        
        # 计算真实伪距（假设时钟偏差为 0）
        true_ranges = np.array([
            self.compute_pseudorange(sat, true_pos) for sat in sat_positions
        ])
        
        # 计算欺骗伪距（使接收机解算出 spoofed_pos）
        # 欺骗伪距 = 欺骗位置到卫星的距离 + 公共时钟偏差
        spoofed_ranges_raw = np.array([
            self.compute_pseudorange(sat, spoofed_pos) for sat in sat_positions
        ])
        
        # 加入一个公共的时钟偏差项（欺骗者可以自由选择）
        # 这里选择使所有伪距偏移量的平均值为正（延迟信号）
        clock_bias_adj = np.max(true_ranges - spoofed_ranges_raw) + 1000  # 额外加 1km 延迟
        spoofed_ranges = spoofed_ranges_raw + clock_bias_adj
        
        # 伪距偏移量（欺骗信号需要延迟/提前的量）
        range_offsets = spoofed_ranges - true_ranges
        
        return sat_positions, true_ranges, spoofed_ranges, range_offsets
    
    def position_solution(self, sat_positions, pseudoranges):
        """
        伪距定位解算（最小二乘法）
        
        使用牛顿迭代法求解位置和时钟偏差。
        
        参数：
            sat_positions: 卫星位置数组 [n x 3]
            pseudoranges: 伪距数组 [n]
        
        返回：
            rx_pos: 解算的接收机位置 (x, y, z) [m]
            clock_bias: 接收机时钟偏差 [m]（转换为距离量）
        """
        n = len(sat_positions)
        
        # 初始猜测位置（原点）
        rx_pos = np.array([0.0, 0.0, 0.0])
        clock_bias = 0.0  # 用距离表示的时钟偏差
        
        # 迭代求解
        for _ in range(20):  # 最多迭代 20 次
            # 计算预测伪距
            predicted_ranges = np.array([
                np.sqrt(np.sum((sat - rx_pos) ** 2)) + clock_bias
                for sat in sat_positions
            ])
            
            # 计算伪距残差
            residuals = pseudoranges - predicted_ranges
            
            # 构建几何矩阵 G
            G = np.zeros((n, 4))
            for i in range(n):
                range_to_sat = np.sqrt(np.sum((sat_positions[i] - rx_pos) ** 2))
                G[i, 0] = -(sat_positions[i, 0] - rx_pos[0]) / range_to_sat
                G[i, 1] = -(sat_positions[i, 1] - rx_pos[1]) / range_to_sat
                G[i, 2] = -(sat_positions[i, 2] - rx_pos[2]) / range_to_sat
                G[i, 3] = 1.0
            
            # 最小二乘求解
            # delta_x = (G^T G)^{-1} G^T residuals
            delta = np.linalg.lstsq(G, residuals, rcond=None)[0]
            
            # 更新位置和时钟偏差
            rx_pos += delta[:3]
            clock_bias += delta[3]
            
            # 检查收敛
            if np.linalg.norm(delta[:3]) < 0.01:
                break
        
        return rx_pos, clock_bias
    
    def intermediate_spoofing_simulation(self, duration_ms=100, transition_ms=30):
        """
        中间式欺骗攻击过程模拟
        
        攻击过程：
        阶段 1：正常接收真实信号
        阶段 2：注入欺骗信号，逐步增加欺骗信号功率
        阶段 3：欺骗信号功率超过真实信号，接收机跟踪欺骗信号
        阶段 4：缓慢拖动欺骗信号到目标位置
        
        参数：
            duration_ms: 总模拟时长 [ms]
            transition_ms: 过渡时间 [ms]
        
        返回：
            time: 时间序列
            true_positions: 真实位置轨迹
            spoofed_positions: 欺骗位置轨迹
            power_ratio: 欺骗/真实信号功率比
        """
        n_points = duration_ms
        time = np.arange(n_points)  # ms
        
        # 真实位置（静止）
        true_pos = np.array([0.0, 0.0, 0.0])
        true_positions = np.tile(true_pos, (n_points, 1))
        
        # 欺骗目标位置（偏移 500 米）
        target_offset = np.array([500.0, 300.0, 0.0])
        
        # 欺骗位置轨迹（逐渐偏离）
        spoofed_positions = np.zeros((n_points, 3))
        
        # 功率比（欺骗信号 / 真实信号，dB）
        power_ratio = np.zeros(n_points)
        
        # 阶段 1：正常（前 20% 时间）
        phase1_end = int(0.2 * n_points)
        spoofed_positions[:phase1_end] = true_pos
        power_ratio[:phase1_end] = -20  # 欺骗信号比真实低 20dB（几乎没有）
        
        # 阶段 2：欺骗信号功率上升（过渡阶段）
        phase2_start = phase1_end
        phase2_end = phase2_start + transition_ms
        if phase2_end > n_points:
            phase2_end = n_points
        
        for i in range(phase2_start, phase2_end):
            t_ratio = (i - phase2_start) / (phase2_end - phase2_start)
            # 功率从 -20dB 升到 +3dB（欺骗信号比真实信号高 3dB）
            power_ratio[i] = -20 + 23 * t_ratio
            # 位置开始缓慢偏移
            spoofed_positions[i] = true_pos + target_offset * t_ratio * 0.1
        
        # 阶段 3：完全欺骗，位置逐渐拖到目标
        phase3_start = phase2_end
        for i in range(phase3_start, n_points):
            t_ratio = (i - phase3_start) / (n_points - phase3_start)
            power_ratio[i] = 3 + 2 * np.sin(0.1 * i)  # 维持在 +3dB 左右波动
            # 使用缓动函数平滑拖动
            smooth_ratio = t_ratio  # 可以换成其他缓动函数
            spoofed_positions[i] = true_pos + target_offset * (0.1 + 0.9 * smooth_ratio)
        
        return time, true_positions, spoofed_positions, power_ratio


def demo_gps_spoofing():
    """
    演示二：GPS 欺骗攻击演示
    
    展示欺骗攻击的原理和效果。
    """
    print("\n" + "=" * 60)
    print("演示二：GPS 欺骗攻击演示")
    print("=" * 60)
    
    spoof_sim = GPSSpoofingSimulator()
    
    # --- 场景 1：单点欺骗 ---
    print("\n【场景 1】单点欺骗攻击")
    print("-" * 40)
    
    true_pos = np.array([100.0, 200.0, 50.0])  # 真实位置
    spoofed_target = np.array([600.0, 500.0, 50.0])  # 欺骗目标位置（偏移 500m+300m）
    
    sat_pos, true_ranges, spoof_ranges, offsets = spoof_sim.spoofing_attack_simulation(
        true_pos, spoofed_target, n_sats=8
    )
    
    print(f"真实位置：({true_pos[0]:.1f}, {true_pos[1]:.1f}, {true_pos[2]:.1f}) m")
    print(f"欺骗目标：({spoofed_target[0]:.1f}, {spoofed_target[1]:.1f}, {spoofed_target[2]:.1f}) m")
    print(f"偏移距离：{np.linalg.norm(spoofed_target - true_pos):.1f} m")
    
    print(f"\n各卫星伪距偏移量（欺骗信号需要调整的距离）：")
    for i in range(len(offsets)):
        direction = "延迟" if offsets[i] > 0 else "提前"
        print(f"  卫星 {i+1:2d}：{offsets[i]:.1f} m ({direction})")
    
    # 验证欺骗效果：用欺骗伪距解算位置
    calc_pos, calc_bias = spoof_sim.position_solution(sat_pos, spoof_ranges)
    print(f"\n用欺骗伪距解算的位置：({calc_pos[0]:.1f}, {calc_pos[1]:.1f}, {calc_pos[2]:.1f}) m")
    print(f"与欺骗目标的偏差：{np.linalg.norm(calc_pos - spoofed_target):.4f} m")
    print("→ 欺骗成功！接收机将计算出错误的位置。")
    
    # --- 场景 2：中间式欺骗过程 ---
    print("\n【场景 2】中间式欺骗攻击过程模拟")
    print("-" * 40)
    
    time_ms, true_pos, spoof_pos, power_ratio = spoof_sim.intermediate_spoofing_simulation(
        duration_ms=200, transition_ms=40
    )
    
    # 计算偏移距离
    offset_dist = np.sqrt(
        (spoof_pos[:, 0] - true_pos[:, 0]) ** 2 +
        (spoof_pos[:, 1] - true_pos[:, 1]) ** 2
    )
    
    print("欺骗攻击分三个阶段：")
    print("  阶段 1（0-40ms）：正常接收，欺骗信号功率很低")
    print("  阶段 2（40-80ms）：干扰+注入，欺骗功率逐渐升高")
    print("  阶段 3（80-200ms）：完全欺骗，位置逐渐被拖走")
    
    # 绘图
    fig, axes = plt.subplots(2, 1, figsize=(12, 8))
    
    # 子图 1：信号功率比
    ax = axes[0]
    ax.plot(time_ms, power_ratio, 'r-', linewidth=2, label='欺骗/真实信号功率比')
    ax.axhline(y=0, color='k', linestyle='--', alpha=0.5, label='功率相等 (0dB)')
    ax.fill_between(time_ms, power_ratio, 0, 
                    where=(power_ratio >= 0), alpha=0.3, color='red', label='欺骗占优')
    ax.fill_between(time_ms, power_ratio, 0, 
                    where=(power_ratio < 0), alpha=0.3, color='green', label='真实占优')
    ax.set_title('中间式欺骗攻击 - 信号功率变化')
    ax.set_xlabel('时间 (ms)')
    ax.set_ylabel('功率比 (dB)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axvline(x=40, color='gray', linestyle=':', alpha=0.7)
    ax.axvline(x=80, color='gray', linestyle=':', alpha=0.7)
    ax.text(20, ax.get_ylim()[1]*0.9, '阶段1\n正常', ha='center', fontsize=10)
    ax.text(60, ax.get_ylim()[1]*0.9, '阶段2\n过渡', ha='center', fontsize=10)
    ax.text(140, ax.get_ylim()[1]*0.9, '阶段3\n欺骗成功', ha='center', fontsize=10)
    
    # 子图 2：位置偏移
    ax = axes[1]
    ax.plot(time_ms, offset_dist, 'b-', linewidth=2, label='位置偏移量')
    ax.set_title('中间式欺骗攻击 - 接收机位置偏移')
    ax.set_xlabel('时间 (ms)')
    ax.set_ylabel('位置偏移 (m)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axvline(x=40, color='gray', linestyle=':', alpha=0.7)
    ax.axvline(x=80, color='gray', linestyle=':', alpha=0.7)
    
    plt.tight_layout()
    output_path = 'e:\\cybersecurity\\study\\12-卫星网络安全\\gps_spoofing_demo.png'
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    print(f"\n欺骗攻击演示图已保存至：{output_path}")
    plt.close()


# ============================================================
# 第三部分：信号干扰模拟
# ============================================================

class JammingSimulator:
    """
    卫星信号干扰模拟器
    
    功能：
    - 模拟各种类型的干扰信号
    - 分析干扰对通信质量的影响
    - 计算不同干扰方式下的误码率
    - 比较抗干扰技术的效果
    """
    
    def __init__(self, signal_bw=2e6, snr_db=10):
        """
        初始化干扰模拟器
        
        参数：
            signal_bw: 信号带宽 [Hz]
            snr_db: 原始信噪比 [dB]
        """
        self.signal_bw = signal_bw
        self.snr_db = snr_db
    
    def generate_jamming_signal(self, jammer_type, n_samples, fs, js_ratio_db=0):
        """
        生成干扰信号
        
        参数：
            jammer_type: 干扰类型
                'noise': 宽带噪声干扰
                'single_tone': 单频干扰
                'multi_tone': 多音干扰
                'pulse': 脉冲干扰
                'sweep': 扫频干扰
            n_samples: 采样点数
            fs: 采样率 [Hz]
            js_ratio_db: 干信比 [dB]（在信号带宽内的总干扰功率 / 信号功率）
        
        返回：
            jamming: 干扰信号
        """
        t = np.arange(n_samples) / fs
        
        # 根据干信比计算干扰功率
        # 假设信号功率为 1，干扰功率 = 10^(js_ratio_db/10)
        jam_power = 10 ** (js_ratio_db / 10)
        
        if jammer_type == 'noise':
            # 宽带噪声干扰
            jamming = np.sqrt(jam_power) * np.random.randn(n_samples)
            
        elif jammer_type == 'single_tone':
            # 单频干扰（瞄准中心频率）
            # 归一化频率（相对于采样率）
            jam_freq = 0.05 * fs  # 干扰频率偏移
            jamming = np.sqrt(2 * jam_power) * np.cos(2 * np.pi * jam_freq * t)
            
        elif jammer_type == 'multi_tone':
            # 多音干扰（多个等间隔单频）
            n_tones = 10
            jamming = np.zeros(n_samples)
            tone_power = jam_power / n_tones
            for i in range(n_tones):
                freq = (0.01 + 0.005 * i) * fs
                jamming += np.sqrt(2 * tone_power) * np.cos(2 * np.pi * freq * t)
                
        elif jammer_type == 'pulse':
            # 脉冲干扰（占空比 10%）
            duty_cycle = 0.1
            pulse_period = int(0.001 * fs)  # 1ms 周期
            pulse_width = int(pulse_period * duty_cycle)
            peak_power = jam_power / duty_cycle  # 峰值功率更高
            
            jamming = np.zeros(n_samples)
            for i in range(0, n_samples, pulse_period):
                end = min(i + pulse_width, n_samples)
                jamming[i:end] = np.sqrt(peak_power) * np.random.randn(end - i)
                
        elif jammer_type == 'sweep':
            # 扫频干扰
            sweep_range = 0.1 * fs  # 扫频范围
            sweep_rate = 1000  # 每秒扫频次数
            # 瞬时频率随时间线性变化
            phase = 2 * np.pi * (0.05 * fs * t + sweep_range / (2 * sweep_rate) * 
                                np.mod(t * sweep_rate, 1) ** 2)
            jamming = np.sqrt(2 * jam_power) * np.cos(phase)
            
        else:
            raise ValueError(f"未知干扰类型：{jammer_type}")
        
        return jamming
    
    def calculate_ber_bpsk(self, snr_db):
        """
        计算 BPSK 调制在 AWGN 信道下的理论误码率
        
        BER = 0.5 * erfc(sqrt(Eb/N0))
        
        参数：
            snr_db: 信噪比 [dB]
        
        返回：
            ber: 误码率
        """
        from scipy.special import erfc
        snr_linear = 10 ** (snr_db / 10)
        # 对于 BPSK，Eb/N0 = SNR（当符号率=比特率时）
        ber = 0.5 * erfc(np.sqrt(snr_linear))
        return ber
    
    def jamming_effect_analysis(self, js_ratios_db=np.arange(-10, 31, 2)):
        """
        分析不同干信比下的干扰效果
        
        参数：
            js_ratios_db: 干信比范围 [dB]
        
        返回：
            results: 各干扰类型的误码率结果字典
        """
        jammer_types = ['noise', 'single_tone', 'multi_tone', 'pulse', 'sweep']
        results = {}
        
        base_snr = self.snr_db
        
        for jammer_type in jammer_types:
            bers = []
            for js_db in js_ratios_db:
                # 简化模型：计算有效信噪比
                # 对于噪声干扰：SNR_eff = SNR / (1 + J/S)
                # 对于其他干扰：用干扰效率因子修正
                js_linear = 10 ** (js_db / 10)
                
                if jammer_type == 'noise':
                    # 宽带噪声干扰：完全叠加
                    snr_eff_db = 10 * np.log10(10 ** (base_snr / 10) / (1 + js_linear))
                elif jammer_type == 'single_tone':
                    # 单频干扰：效率较高
                    # 单频干扰对扩频系统的影响约为噪声干扰的 2-3 倍（等效）
                    effective_js = js_linear * 0.6  # 单频在扩频系统中的效率因子
                    snr_eff_db = 10 * np.log10(10 ** (base_snr / 10) / (1 + effective_js))
                elif jammer_type == 'multi_tone':
                    effective_js = js_linear * 0.7
                    snr_eff_db = 10 * np.log10(10 ** (base_snr / 10) / (1 + effective_js))
                elif jammer_type == 'pulse':
                    # 脉冲干扰：占空比影响
                    duty_cycle = 0.1
                    effective_js = js_linear * duty_cycle * 2  # 脉冲干扰效率
                    snr_eff_db = 10 * np.log10(10 ** (base_snr / 10) / (1 + effective_js))
                elif jammer_type == 'sweep':
                    effective_js = js_linear * 0.5
                    snr_eff_db = 10 * np.log10(10 ** (base_snr / 10) / (1 + effective_js))
                
                ber = self.calculate_ber_bpsk(snr_eff_db)
                bers.append(ber)
            
            results[jammer_type] = bers
        
        return js_ratios_db, results
    
    def anti_jamming_gain_demo(self):
        """
        抗干扰增益演示
        
        比较不同抗干扰技术的效果：
        - 无抗干扰
        - 扩频增益（处理增益）
        - 纠错编码增益
        - 调零天线增益
        """
        # 扩频处理增益：PG = 10 * log10(BW_signal / BW_data)
        # GPS C/A 码：1.023 MHz / 50 Hz ≈ 43 dB
        spreading_gain_db = 10 * np.log10(1.023e6 / 50)
        
        # 纠错编码增益：典型 2-5 dB
        coding_gain_db = 3
        
        # 调零天线增益：典型 20-40 dB（取决于干扰源数量）
        nulling_gain_db = 30
        
        gains = {
            '无抗干扰': 0,
            '扩频增益 (C/A码)': spreading_gain_db,
            '扩频 + 编码': spreading_gain_db + coding_gain_db,
            '扩频 + 编码 + 调零天线': spreading_gain_db + coding_gain_db + nulling_gain_db,
        }
        
        return gains


def demo_jamming():
    """
    演示三：信号干扰模拟
    
    展示各种干扰方式及其效果。
    """
    print("\n" + "=" * 60)
    print("演示三：信号干扰模拟")
    print("=" * 60)
    
    jam_sim = JammingSimulator(signal_bw=2e6, snr_db=10)
    
    # --- 干扰信号波形 ---
    print("\n【干扰信号类型对比】")
    print("-" * 40)
    
    fs = 20e6  # 采样率
    n_samples = 2000
    
    jammer_types = ['noise', 'single_tone', 'multi_tone', 'pulse', 'sweep']
    jammer_names = ['宽带噪声干扰', '单频干扰', '多音干扰', '脉冲干扰', '扫频干扰']
    
    fig, axes = plt.subplots(len(jammer_types), 2, figsize=(14, 14))
    t = np.arange(n_samples) / fs * 1e6  # 微秒
    
    for i, (jtype, jname) in enumerate(zip(jammer_types, jammer_names)):
        # 生成干扰信号
        jamming = jam_sim.generate_jamming_signal(jtype, n_samples, fs, js_ratio_db=3)
        
        # 时域波形
        ax = axes[i, 0]
        ax.plot(t, jamming, 'r-', linewidth=0.5)
        ax.set_title(f'{jname} - 时域波形')
        ax.set_xlabel('时间 (μs)')
        ax.set_ylabel('幅度')
        ax.grid(True, alpha=0.3)
        
        # 频谱
        ax = axes[i, 1]
        freqs = np.fft.fftfreq(n_samples, 1/fs)
        freqs = np.fft.fftshift(freqs) / 1e6
        spectrum = np.abs(np.fft.fft(jamming))
        spectrum = np.fft.fftshift(spectrum)
        spectrum_db = 20 * np.log10(spectrum / np.max(spectrum) + 1e-10)
        ax.plot(freqs, spectrum_db, 'b-', linewidth=0.5)
        ax.set_title(f'{jname} - 频谱')
        ax.set_xlabel('频率 (MHz)')
        ax.set_ylabel('归一化幅度 (dB)')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(-2, 2)
    
    plt.tight_layout()
    output_path = 'e:\\cybersecurity\\study\\12-卫星网络安全\\jamming_types.png'
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    print(f"干扰类型对比图已保存至：{output_path}")
    
    # --- 干扰效果分析 ---
    print("\n【干扰效果分析】")
    print("-" * 40)
    
    js_ratios, results = jam_sim.jamming_effect_analysis()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    colors = ['r', 'b', 'g', 'm', 'c']
    markers = ['o', 's', '^', 'd', 'v']
    for (jtype, bers), jname, color, marker in zip(
        results.items(), jammer_names, colors, markers
    ):
        ax.semilogy(js_ratios, bers, color=color, marker=marker, 
                   linewidth=2, markersize=4, label=jname)
    
    ax.set_title('不同干扰方式下的误码率对比')
    ax.set_xlabel('干信比 J/S (dB)')
    ax.set_ylabel('误码率 (BER)')
    ax.legend()
    ax.grid(True, alpha=0.3, which='both')
    ax.axhline(y=1e-3, color='gray', linestyle='--', alpha=0.5, label='可接受BER')
    
    output_path2 = 'e:\\cybersecurity\\study\\12-卫星网络安全\\jamming_ber_analysis.png'
    plt.savefig(output_path2, dpi=100, bbox_inches='tight')
    print(f"干扰效果分析图已保存至：{output_path2}")
    plt.close()
    
    # --- 抗干扰增益 ---
    print("\n【抗干扰技术增益对比】")
    print("-" * 40)
    
    gains = jam_sim.anti_jamming_gain_demo()
    for tech, gain in gains.items():
        print(f"  {tech}：{gain:.1f} dB")
    
    print(f"\n说明：")
    print(f"  GPS C/A 码的扩频增益约为 {gains['扩频增益 (C/A码)']:.1f} dB")
    print(f"  这意味着即使干扰功率比信号高 30dB，GPS 仍可能正常工作")
    print(f"  但干扰功率超过扩频增益后，通信质量会迅速下降")
    
    return gains


# ============================================================
# 第四部分：信号强度分析
# ============================================================

class SignalStrengthAnalyzer:
    """
    卫星信号强度分析器
    
    功能：
    - 计算自由空间路径损耗
    - 分析链路预算
    - 计算干扰范围
    - 分析不同轨道高度的信号特性
    """
    
    def __init__(self):
        """初始化信号强度分析器"""
        self.c = 299792458  # 光速 (m/s)
        self.k_boltzmann = 1.380649e-23  # 玻尔兹曼常数 (J/K)
    
    def free_space_path_loss(self, distance_m, freq_hz):
        """
        计算自由空间路径损耗
        
        FSPL = (4πd/λ)² = (4πdf/c)²
        
        参数：
            distance_m: 距离 [m]
            freq_hz: 频率 [Hz]
        
        返回：
            fspl_db: 路径损耗 [dB]
        """
        wavelength = self.c / freq_hz
        fspl_linear = (4 * np.pi * distance_m / wavelength) ** 2
        fspl_db = 10 * np.log10(fspl_linear)
        return fspl_db
    
    def link_budget(self, tx_power_dbw, tx_gain_db, rx_gain_db, 
                    distance_m, freq_hz, other_loss_db=0):
        """
        计算链路预算
        
        接收功率 = 发射功率 + 发射天线增益 + 接收天线增益 - 路径损耗 - 其他损耗
        
        参数：
            tx_power_dbw: 发射功率 [dBW]
            tx_gain_db: 发射天线增益 [dBi]
            rx_gain_db: 接收天线增益 [dBi]
            distance_m: 距离 [m]
            freq_hz: 频率 [Hz]
            other_loss_db: 其他损耗 [dB]
        
        返回：
            rx_power_dbw: 接收功率 [dBW]
            rx_power_dbm: 接收功率 [dBm]
        """
        fspl = self.free_space_path_loss(distance_m, freq_hz)
        rx_power_dbw = tx_power_dbw + tx_gain_db + rx_gain_db - fspl - other_loss_db
        rx_power_dbm = rx_power_dbw + 30  # dBW -> dBm
        return rx_power_dbw, rx_power_dbm
    
    def gps_signal_power_at_ground(self):
        """
        计算 GPS 信号到达地面的功率
        
        GPS 参数（典型值）：
        - 卫星发射功率：约 20-30 W（L1 频段）
        - 卫星天线增益：约 15 dBi（定向到地球）
        - 轨道高度：约 20,200 km
        - 频率：1575.42 MHz
        """
        # GPS 卫星参数（L1 C/A 码）
        tx_power_w = 25  # 发射功率 [W]（典型值）
        tx_power_dbw = 10 * np.log10(tx_power_w)
        tx_gain_db = 15  # 发射天线增益 [dBi]
        rx_gain_db = 0  # 接收天线增益 [dBi]（全向天线）
        orbit_height = 20200e3  # 轨道高度 [m]
        # 考虑斜距（卫星不在天顶时距离更远）
        slant_range = orbit_height / np.cos(np.pi / 6)  # 仰角 30 度
        freq_hz = 1575.42e6
        
        rx_power_dbw, rx_power_dbm = self.link_budget(
            tx_power_dbw, tx_gain_db, rx_gain_db, slant_range, freq_hz
        )
        
        # 计算热噪声功率（室温 290K，2MHz 带宽）
        noise_temp = 290  # K
        bandwidth = 2e6  # Hz
        noise_power_dbw = 10 * np.log10(self.k_boltzmann * noise_temp * bandwidth)
        noise_power_dbm = noise_power_dbw + 30
        
        # 载噪比 C/N0
        cn0 = rx_power_dbw - 10 * np.log10(self.k_boltzmann * noise_temp)
        
        return {
            'tx_power_dbw': tx_power_dbw,
            'tx_power_dbm': tx_power_dbw + 30,
            'slant_range_km': slant_range / 1000,
            'path_loss_db': self.free_space_path_loss(slant_range, freq_hz),
            'rx_power_dbw': rx_power_dbw,
            'rx_power_dbm': rx_power_dbm,
            'noise_power_dbm': noise_power_dbm,
            'cn0_db_hz': cn0,
        }
    
    def jamming_range_estimation(self, jammer_power_w, jammer_gain_db=3, 
                                  rx_gain_db=0, freq_hz=1575.42e6,
                                  required_js_db=10):
        """
        估算 GPS 干扰器的干扰范围
        
        原理：在干扰距离 d 处，干扰信号经过路径损耗后到达接收机，
        其功率比 GPS 信号高 required_js_db 时，达到干扰效果。
        
        参数：
            jammer_power_w: 干扰机发射功率 [W]
            jammer_gain_db: 干扰天线增益 [dBi]
            rx_gain_db: 接收天线增益 [dBi]
            freq_hz: 频率 [Hz]
            required_js_db: 所需干信比 [dB]（达到干扰效果的 J/S）
        
        返回：
            jamming_range_km: 干扰范围 [km]
        """
        # GPS 信号到达地面的功率（参考值）
        gps_rx_power_dbw = -160  # 约 -160 dBW（典型值）
        
        # 所需的干扰信号功率（在接收机处）
        jammer_rx_power_dbw = gps_rx_power_dbw + required_js_db
        
        # 干扰机发射功率
        jammer_tx_power_dbw = 10 * np.log10(jammer_power_w)
        
        # 最大允许路径损耗
        max_path_loss_db = jammer_tx_power_dbw + jammer_gain_db + rx_gain_db - jammer_rx_power_dbw
        
        # 反算距离：FSPL = 20*log10(4πdf/c)
        # d = c * 10^(FSPL/20) / (4πf)
        distance_m = self.c * (10 ** (max_path_loss_db / 20)) / (4 * np.pi * freq_hz)
        distance_km = distance_m / 1000
        
        return distance_km
    
    def leo_satellite_link_analysis(self):
        """
        LEO 卫星链路分析
        
        对比 LEO 和 GEO 卫星的链路特性。
        """
        # LEO 卫星参数
        leo_params = {
            'name': 'LEO 卫星',
            'altitude_km': 550,  # km
            'tx_power_w': 10,  # W
            'tx_gain_db': 25,  # dBi
            'freq_hz': 28e9,  # Ka 波段下行
        }
        
        # GEO 卫星参数
        geo_params = {
            'name': 'GEO 卫星',
            'altitude_km': 35786,  # km
            'tx_power_w': 100,  # W
            'tx_gain_db': 30,  # dBi
            'freq_hz': 12e9,  # Ku 波段下行
        }
        
        rx_gain_db = 30  # 地面站接收天线增益 [dBi]
        
        results = {}
        for params in [leo_params, geo_params]:
            distance = params['altitude_km'] * 1000  # m
            rx_power_dbw, rx_power_dbm = self.link_budget(
                10 * np.log10(params['tx_power_w']),
                params['tx_gain_db'],
                rx_gain_db,
                distance,
                params['freq_hz']
            )
            results[params['name']] = {
                'rx_power_dbm': rx_power_dbm,
                'path_loss_db': self.free_space_path_loss(distance, params['freq_hz']),
                'distance_km': params['altitude_km'],
            }
        
        return results


def demo_signal_strength():
    """
    演示四：信号强度分析
    """
    print("\n" + "=" * 60)
    print("演示四：信号强度分析")
    print("=" * 60)
    
    analyzer = SignalStrengthAnalyzer()
    
    # --- GPS 信号功率 ---
    print("\n【GPS 信号到达地面的功率】")
    print("-" * 40)
    
    gps_power = analyzer.gps_signal_power_at_ground()
    print(f"  卫星发射功率：{gps_power['tx_power_dbm']:.1f} dBm ({10**(gps_power['tx_power_dbw']/10):.1f} W)")
    print(f"  信号传播距离：{gps_power['slant_range_km']:.0f} km")
    print(f"  自由空间路径损耗：{gps_power['path_loss_db']:.1f} dB")
    print(f"  地面接收功率：{gps_power['rx_power_dbm']:.1f} dBm")
    print(f"  热噪声功率（2MHz带宽）：{gps_power['noise_power_dbm']:.1f} dBm")
    print(f"  载噪比 C/N0：{gps_power['cn0_db_hz']:.1f} dB-Hz")
    print(f"\n  注意：GPS 信号功率比噪声还低约 20dB！")
    print(f"  依靠扩频增益（约 43dB）才能从噪声中提取信号。")
    print(f"  这也是 GPS 容易被干扰的原因——信号太弱了。")
    
    # --- 干扰范围估算 ---
    print("\n【GPS 干扰器干扰范围估算】")
    print("-" * 40)
    
    jammer_powers = [0.01, 0.1, 1, 10, 100]  # W
    js_required = 5  # dB（达到明显干扰效果所需的 J/S）
    
    print(f"{'干扰功率':>10} | {'干扰距离(开阔地)':>18}")
    print("-" * 35)
    
    distances = []
    for power in jammer_powers:
        dist = analyzer.jamming_range_estimation(power, required_js_db=js_required)
        distances.append(dist)
        power_label = f"{power*1000:.0f} mW" if power < 1 else f"{power} W"
        print(f"{power_label:>10} | {dist:>15.1f} km")
    
    # 绘图
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.loglog([p*1000 for p in jammer_powers], distances, 'ro-', linewidth=2, markersize=8)
    ax.set_title('GPS 干扰器干扰范围估算（开阔地）')
    ax.set_xlabel('干扰发射功率 (mW)')
    ax.set_ylabel('干扰距离 (km)')
    ax.grid(True, alpha=0.3, which='both')
    
    # 标注典型应用
    ax.annotate('小型便携\n干扰器', xy=(100, distances[2]), xytext=(50, distances[2]*2),
                arrowprops=dict(arrowstyle='->'))
    ax.annotate('车载\n干扰器', xy=(10000, distances[4]), xytext=(3000, distances[4]*1.5),
                arrowprops=dict(arrowstyle='->'))
    
    output_path = 'e:\\cybersecurity\\study\\12-卫星网络安全\\jamming_range.png'
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    print(f"\n干扰范围估算图已保存至：{output_path}")
    plt.close()
    
    # --- LEO vs GEO 链路对比 ---
    print("\n【LEO 与 GEO 卫星链路对比】")
    print("-" * 40)
    
    link_results = analyzer.leo_satellite_link_analysis()
    for name, data in link_results.items():
        print(f"\n{name}：")
        print(f"  轨道高度：{data['distance_km']:.0f} km")
        print(f"  路径损耗：{data['path_loss_db']:.1f} dB")
        print(f"  接收功率：{data['rx_power_dbm']:.1f} dBm")
    
    return gps_power


# ============================================================
# 第五部分：多普勒效应模拟
# ============================================================

class DopplerSimulator:
    """
    多普勒效应模拟器
    
    功能：
    - 计算卫星运动产生的多普勒频移
    - 模拟不同轨道卫星的多普勒特性
    - 分析多普勒对 GPS 接收的影响
    - 演示多普勒辅助定位原理
    """
    
    def __init__(self):
        """初始化多普勒模拟器"""
        self.c = 299792458  # 光速 (m/s)
        self.fc_l1 = 1575.42e6  # GPS L1 频率 (Hz)
    
    def doppler_shift(self, relative_velocity, frequency):
        """
        计算多普勒频移
        
        fd = f * v_r / c
        
        当源靠近观察者时，v_r 为正，频率升高（蓝移）
        当源远离观察者时，v_r 为负，频率降低（红移）
        
        参数：
            relative_velocity: 相对径向速度 [m/s]（靠近为正）
            frequency: 载波频率 [Hz]
        
        返回：
            doppler_hz: 多普勒频移 [Hz]
        """
        doppler_hz = frequency * relative_velocity / self.c
        return doppler_hz
    
    def leo_satellite_doppler(self, altitude_km=550, elevation_deg=45):
        """
        计算 LEO 卫星的多普勒频移
        
        LEO 卫星速度快，多普勒频移大，是卫星通信和导航
        中需要考虑的重要因素。
        
        参数：
            altitude_km: 轨道高度 [km]
            elevation_deg: 卫星仰角 [度]
        
        返回：
            doppler_hz: 多普勒频移 [Hz]
            satellite_velocity: 卫星速度 [m/s]
            radial_velocity: 径向速度 [m/s]
        """
        earth_radius = 6371  # km
        earth_mu = 3.986004418e14  # 地球引力常数 m^3/s^2
        
        # 轨道半径
        orbit_radius_m = (earth_radius + altitude_km) * 1000
        
        # 卫星速度（圆轨道）
        sat_velocity = np.sqrt(earth_mu / orbit_radius_m)
        
        # 径向速度分量（简化模型）
        # 仰角 90 度（天顶）时径向速度为 0
        # 仰角 0 度（地平线）时径向速度最大
        elevation_rad = np.deg2rad(elevation_deg)
        # 简化：最大径向速度出现在仰角约 0 度时
        # 实际计算需要考虑几何关系，这里简化
        radial_velocity = sat_velocity * np.cos(elevation_rad) * 0.8  # 简化系数
        
        # 多普勒频移
        doppler_hz = self.doppler_shift(radial_velocity, self.fc_l1)
        
        return doppler_hz, sat_velocity, radial_velocity
    
    def geo_satellite_doppler(self):
        """
        计算 GEO 卫星的多普勒频移
        
        GEO 卫星相对地面静止，多普勒频移很小，
        主要由地球自转和卫星轨道微小偏差引起。
        """
        # GEO 卫星轨道速度
        geo_altitude = 35786e3  # m
        earth_radius = 6371e3  # m
        orbit_radius = earth_radius + geo_altitude
        angular_velocity = 2 * np.pi / 86164  # 地球自转角速度 (rad/s)
        sat_velocity = angular_velocity * orbit_radius
        
        # 对于静止地面站，GEO 卫星的多普勒频移很小
        # 主要来自卫星的日运动（南北倾角导致的）
        # 典型值：约 0-100 Hz
        max_doppler = 50  # Hz（典型最大值）
        
        return max_doppler, sat_velocity
    
    def doppler_over_pass(self, altitude_km=550, duration_s=600):
        """
        模拟 LEO 卫星过境时的多普勒变化曲线
        
        卫星从地平线升起，经过天顶，落到另一边地平线，
        多普勒频移从正（靠近）变到负（远离）。
        
        参数：
            altitude_km: 轨道高度 [km]
            duration_s: 过境持续时间 [s]
        
        返回：
            time: 时间序列 [s]
            doppler: 多普勒频移序列 [Hz]
            elevation: 仰角序列 [度]
        """
        t = np.linspace(-duration_s/2, duration_s/2, 500)
        
        earth_radius = 6371  # km
        orbit_r = earth_radius + altitude_km  # km
        
        # 卫星角速度
        earth_mu = 3.986004418e14  # m^3/s^2
        sat_velocity = np.sqrt(earth_mu / (orbit_r * 1000))  # m/s
        angular_vel = sat_velocity / (orbit_r * 1000)  # rad/s
        
        # 计算仰角随时间变化（简化模型）
        # 假设卫星从正上方经过
        # 角度 = 角速度 * 时间
        angle = angular_vel * t  # rad
        
        # 仰角计算（简化）
        # 当 t=0 时，卫星在天顶（仰角 90 度）
        # cos(仰角) ≈ sin(地心角) 的某种关系
        # 这里用简化的几何模型
        elevation = np.zeros_like(t)
        for i, ang in enumerate(angle):
            # 地心角
            gamma = abs(ang)
            # 余弦定理计算到卫星的距离
            sat_range = np.sqrt(
                earth_radius**2 + orbit_r**2 - 
                2 * earth_radius * orbit_r * np.cos(gamma)
            )
            # 仰角
            if gamma < np.arccos(earth_radius / orbit_r):  # 可见时
                # 用正弦定理
                sin_elev = (orbit_r * np.sin(gamma)) / sat_range - earth_radius / sat_range
                # 更准确的计算：
                cos_zenith = (orbit_r**2 + sat_range**2 - earth_radius**2) / (2 * orbit_r * sat_range)
                elevation[i] = 90 - np.rad2deg(np.arccos(np.clip(cos_zenith, -1, 1)))
                if elevation[i] < 0:
                    elevation[i] = 0
            else:
                elevation[i] = 0
        
        # 计算径向速度和多普勒
        # 径向速度 = 卫星速度在视线方向的分量
        doppler = np.zeros_like(t)
        for i in range(len(t)):
            if elevation[i] > 0:
                elev_rad = np.deg2rad(elevation[i])
                # 径向速度分量（简化）
                # 卫星速度方向垂直于地心到卫星连线
                # 径向速度 = v * cos(仰角) * cos(方位角变化率相关)
                # 更简单的近似：多普勒随时间近似为线性变化（S 曲线）
                pass
        
        # 简化多普勒模型：S 型曲线，从最大正值变到最大负值
        # 过境开始：靠近，最大正多普勒
        # 过境中间：天顶，零多普勒
        # 过境结束：远离，最大负多普勒
        max_doppler = self.doppler_shift(sat_velocity * 0.9, self.fc_l1)  # 最大多普勒
        
        # 用仰角计算多普勒（近似）
        for i in range(len(t)):
            if elevation[i] > 0:
                # 多普勒 = 最大多普勒 * cos(仰角) * sign(t)
                # 负时间（靠近）为正，正时间（远离）为负
                elev_rad = np.deg2rad(elevation[i])
                doppler[i] = max_doppler * np.cos(elev_rad) * np.sign(-t[i])
            else:
                doppler[i] = 0
        
        return t, doppler, elevation
    
    def doppler_positioning_principle(self):
        """
        多普勒定位原理演示
        
        早期卫星导航系统（如 TRANSIT）使用多普勒频移测量进行定位。
        通过测量多普勒频移随时间的变化，可以确定卫星轨道和接收机位置。
        """
        # 简化演示：不同位置的多普勒曲线不同
        pass


def demo_doppler():
    """
    演示五：多普勒效应模拟
    """
    print("\n" + "=" * 60)
    print("演示五：多普勒效应模拟")
    print("=" * 60)
    
    dop_sim = DopplerSimulator()
    
    # --- 不同轨道的多普勒对比 ---
    print("\n【不同轨道卫星的多普勒频移对比】")
    print("-" * 40)
    
    # LEO
    leo_dop, leo_vel, leo_radial = dop_sim.leo_satellite_doppler(altitude_km=550, elevation_deg=10)
    print(f"LEO 卫星（550km 高度）：")
    print(f"  轨道速度：{leo_vel/1000:.2f} km/s")
    print(f"  低仰角时径向速度：{leo_radial:.1f} m/s")
    print(f"  L1 最大多普勒频移：约 ±{abs(leo_dop):.0f} Hz")
    
    # MEO (GPS)
    meo_dop, meo_vel, meo_radial = dop_sim.leo_satellite_doppler(altitude_km=20200, elevation_deg=10)
    print(f"\nMEO 卫星（GPS，约 20200km 高度）：")
    print(f"  轨道速度：{meo_vel/1000:.2f} km/s")
    print(f"  低仰角时径向速度：{meo_radial:.1f} m/s")
    print(f"  L1 最大多普勒频移：约 ±{abs(meo_dop):.0f} Hz")
    
    # GEO
    geo_dop, geo_vel = dop_sim.geo_satellite_doppler()
    print(f"\nGEO 卫星（约 35786km 高度）：")
    print(f"  轨道速度：{geo_vel/1000:.2f} km/s")
    print(f"  多普勒频移：约 ±{geo_dop:.0f} Hz（很小，相对静止）")
    
    print(f"\n  安全意义：")
    print(f"  - LEO 卫星多普勒变化快，需要快速跟踪能力")
    print(f"  - GPS 多普勒范围约 ±5kHz，接收机设计需要考虑")
    print(f"  - 欺骗攻击需要模拟正确的多普勒，否则容易被检测")
    
    # --- LEO 卫星过境多普勒曲线 ---
    print("\n【LEO 卫星过境多普勒变化曲线】")
    print("-" * 40)
    
    t, doppler, elevation = dop_sim.doppler_over_pass(altitude_km=550, duration_s=600)
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    # 多普勒
    color = 'tab:red'
    ax1.set_xlabel('时间（相对过境中点） [s]')
    ax1.set_ylabel('多普勒频移 [Hz]', color=color)
    ax1.plot(t, doppler, color=color, linewidth=2, label='多普勒频移')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax1.axvline(x=0, color='k', linestyle='--', alpha=0.3)
    ax1.grid(True, alpha=0.3)
    
    # 仰角（双 Y 轴）
    ax2 = ax1.twinx()
    color = 'tab:blue'
    ax2.set_ylabel('仰角 [度]', color=color)
    ax2.plot(t, elevation, color=color, linewidth=2, linestyle='--', label='卫星仰角')
    ax2.tick_params(axis='y', labelcolor=color)
    
    plt.title('LEO 卫星过境多普勒频移与仰角变化')
    
    # 标注
    ax1.annotate('卫星靠近\n正多普勒', xy=(-250, doppler[np.argmin(abs(t+250))]), 
                xytext=(-200, max(doppler)*0.8),
                arrowprops=dict(arrowstyle='->'))
    ax1.annotate('卫星远离\n负多普勒', xy=(250, doppler[np.argmin(abs(t-250))]), 
                xytext=(200, min(doppler)*0.8),
                arrowprops=dict(arrowstyle='->'))
    
    output_path = 'e:\\cybersecurity\\study\\12-卫星网络安全\\doppler_over_pass.png'
    plt.savefig(output_path, dpi=100, bbox_inches='tight')
    print(f"多普勒曲线图已保存至：{output_path}")
    plt.close()
    
    print("  多普勒曲线呈 S 型：")
    print("    - 卫星升起时：靠近观测者，正多普勒（频率升高）")
    print("    - 卫星过天顶：径向速度为零，零多普勒")
    print("    - 卫星落下时：远离观测者，负多普勒（频率降低）")


# ============================================================
# 主函数
# ============================================================

def main():
    """
    主函数：运行所有演示
    """
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "卫星信号模拟与攻击演示" + " " * 20 + "║")
    print("║" + " " * 12 + "Satellite Signal Simulation Demo" + " " * 14 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    print("本脚本用于教学演示，包含以下内容：")
    print("  1. GPS 信号结构模拟")
    print("  2. GPS 欺骗攻击演示")
    print("  3. 信号干扰模拟")
    print("  4. 信号强度分析")
    print("  5. 多普勒效应模拟")
    print()
    print("注意：仅用于学习研究，严禁用于非法用途！")
    print()
    
    # 运行所有演示
    try:
        # 演示 1：GPS 信号结构
        demo_gps_signal_structure()
        
        # 演示 2：GPS 欺骗攻击
        demo_gps_spoofing()
        
        # 演示 3：信号干扰
        demo_jamming()
        
        # 演示 4：信号强度分析
        demo_signal_strength()
        
        # 演示 5：多普勒效应
        demo_doppler()
        
        print("\n" + "=" * 60)
        print("所有演示完成！")
        print("生成的图像保存在 e:\\cybersecurity\\study\\12-卫星网络安全\\ 目录下")
        print("=" * 60)
        
    except ImportError as e:
        print(f"缺少依赖库：{e}")
        print("请安装依赖：pip install numpy matplotlib scipy")


if __name__ == '__main__':
    main()
