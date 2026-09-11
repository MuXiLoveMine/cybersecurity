# -*- coding: utf-8 -*-
"""
CAN总线模拟与攻击演示脚本
========================

本脚本用于学习和演示CAN总线通信原理及常见攻击方式，包含：
    1. CAN帧结构模拟（标准帧/扩展帧/CAN FD）
    2. CAN报文生成与解析
    3. CAN总线嗅探演示
    4. CAN重放攻击演示
    5. CAN注入攻击演示
    6. UDS诊断请求模拟
    7. CAN入侵检测（频率检测、数据异常检测）

注意：本脚本仅用于学习研究，请勿用于真实车辆。
      真实CAN总线操作请使用python-can库和相应的硬件适配器。

作者：车联网安全学习
版本：1.0
"""

import time
import random
import threading
import struct
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Optional, Callable


# ============================================================
# 第一部分：CAN帧结构定义
# ============================================================

@dataclass
class CanFrame:
    """
    CAN帧数据类，模拟CAN报文的结构

    属性说明：
        arbitration_id: 仲裁ID（标准帧11位，扩展帧29位）
        data: 数据字段（0~8字节，CAN FD支持0~64字节）
        is_extended_id: 是否为扩展帧（True=扩展帧, False=标准帧）
        is_fd: 是否为CAN FD帧
        bitrate_switch: CAN FD波特率切换标志（BRS位）
        is_remote: 是否为远程帧（RTR位）
        dlc: 数据长度码（自动计算）
        timestamp: 时间戳（接收/发送时间）
    """
    arbitration_id: int          # 仲裁ID
    data: bytes = b''            # 数据字段
    is_extended_id: bool = False # 是否扩展帧
    is_fd: bool = False          # 是否CAN FD
    bitrate_switch: bool = False # 波特率切换（仅CAN FD）
    is_remote: bool = False      # 远程帧标志
    timestamp: float = field(default_factory=time.time)

    @property
    def dlc(self) -> int:
        """
        获取数据长度码（DLC - Data Length Code）

        CAN标准帧的DLC与数据长度对应关系：
            0-8字节: DLC = 实际长度
            CAN FD支持更多长度: 12, 16, 20, 24, 32, 48, 64
        """
        length = len(self.data)
        if not self.is_fd:
            # 标准CAN: 0~8字节
            return min(length, 8)
        else:
            # CAN FD: 0~64字节，按DLC编码
            fd_dlc_map = {0:0,1:1,2:2,3:3,4:4,5:5,6:6,7:7,8:8,
                          12:9,16:10,20:11,24:12,32:13,48:14,64:15}
            # 找到最接近的有效长度
            for l in sorted(fd_dlc_map.keys(), reverse=True):
                if length >= l:
                    return fd_dlc_map[l]
            return 0

    def __str__(self) -> str:
        """格式化输出CAN帧信息"""
        frame_type = "EXT" if self.is_extended_id else "STD"
        if self.is_fd:
            frame_type += "/FD"
        if self.is_remote:
            frame_type += "/RTR"

        data_str = ' '.join(f'{b:02X}' for b in self.data[:8])
        if len(self.data) > 8:
            data_str += f' ... ({len(self.data)} bytes)'

        return (f"[{self.timestamp:.6f}] ID={self.arbitration_id:03X} "
                f"({frame_type}) DLC={self.dlc} Data: {data_str}")


# ============================================================
# 第二部分：CAN报文生成与解析工具
# ============================================================

class CanFrameParser:
    """
    CAN帧解析器，用于解析和构造CAN报文

    支持的功能：
        - 从原始字节解析CAN帧
        - 构造特定类型的CAN帧
        - 计算CRC（简化版演示）
    """

    @staticmethod
    def create_standard_frame(can_id: int, data: bytes) -> CanFrame:
        """
        创建标准CAN帧（11位ID）

        参数：
            can_id: 11位CAN ID（0x000 ~ 0x7FF）
            data: 数据字段（0~8字节）

        返回：
            CanFrame对象
        """
        if not (0 <= can_id <= 0x7FF):
            raise ValueError("标准帧ID范围: 0x000 ~ 0x7FF")
        if len(data) > 8:
            raise ValueError("标准帧数据长度不能超过8字节")

        return CanFrame(
            arbitration_id=can_id,
            data=data,
            is_extended_id=False
        )

    @staticmethod
    def create_extended_frame(can_id: int, data: bytes) -> CanFrame:
        """
        创建扩展CAN帧（29位ID）

        参数：
            can_id: 29位CAN ID（0x00000000 ~ 0x1FFFFFFF）
            data: 数据字段（0~8字节）
        """
        if not (0 <= can_id <= 0x1FFFFFFF):
            raise ValueError("扩展帧ID范围: 0x00000000 ~ 0x1FFFFFFF")
        if len(data) > 8:
            raise ValueError("扩展帧数据长度不能超过8字节")

        return CanFrame(
            arbitration_id=can_id,
            data=data,
            is_extended_id=True
        )

    @staticmethod
    def create_canfd_frame(can_id: int, data: bytes, brs: bool = True) -> CanFrame:
        """
        创建CAN FD帧（灵活数据速率）

        参数：
            can_id: 11位CAN ID
            data: 数据字段（0~64字节）
            brs: 是否启用波特率切换
        """
        if len(data) > 64:
            raise ValueError("CAN FD数据长度不能超过64字节")

        return CanFrame(
            arbitration_id=can_id,
            data=data,
            is_fd=True,
            bitrate_switch=brs
        )

    @staticmethod
    def create_remote_frame(can_id: int, dlc: int = 0) -> CanFrame:
        """
        创建远程帧（RTR - Remote Transmission Request）

        远程帧用于请求其他节点发送指定ID的数据帧
        """
        return CanFrame(
            arbitration_id=can_id,
            data=b'\x00' * dlc,  # 远程帧数据场无意义，但DLC表示请求的数据长度
            is_remote=True
        )

    @staticmethod
    def calculate_crc(data: bytes) -> int:
        """
        简化版CRC计算（演示用，非真实CAN CRC）

        真实CAN使用CRC-15（标准帧）或CRC-17（CAN FD），
        这里使用简化的校验和做演示。
        """
        crc = 0
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ 0x1D) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
        return crc


class CanSignalParser:
    """
    CAN信号解析器，用于从CAN报文中解析具体的信号值

    在真实场景中，信号定义来自DBC（Database CAN）文件，
    这里演示常见信号的解析方法。
    """

    @staticmethod
    def parse_engine_speed(data: bytes) -> float:
        """
        解析发动机转速信号

        假设：转速 = (Byte0 << 8 | Byte1) * 0.25 rpm
        常见于动力CAN，ID: 0x100
        """
        if len(data) < 2:
            return 0.0
        raw_value = (data[0] << 8) | data[1]
        return raw_value * 0.25  # 比例因子0.25

    @staticmethod
    def parse_vehicle_speed(data: bytes) -> float:
        """
        解析车速信号

        假设：车速 = (Byte0 << 8 | Byte1) / 10.0 km/h
        常见于车身/动力CAN，ID: 0x200
        """
        if len(data) < 2:
            return 0.0
        raw_value = (data[0] << 8) | data[1]
        return raw_value / 10.0  # 比例因子0.1

    @staticmethod
    def parse_door_status(data: bytes) -> dict:
        """
        解析车门状态信号

        假设：Byte0的每一位代表一个车门的状态
            bit0: 左前门 (0=关, 1=开)
            bit1: 右前门
            bit2: 左后门
            bit3: 右后门
            bit4: 后备箱
        """
        if len(data) < 1:
            return {}
        byte = data[0]
        return {
            '左前门': '开' if byte & 0x01 else '关',
            '右前门': '开' if byte & 0x02 else '关',
            '左后门': '开' if byte & 0x04 else '关',
            '右后门': '开' if byte & 0x08 else '关',
            '后备箱': '开' if byte & 0x10 else '关',
        }

    @staticmethod
    def build_speed_frame(speed_kmh: float) -> bytes:
        """
        构造车速报文的数据字段

        参数：
            speed_kmh: 车速（km/h）

        返回：
            8字节数据
        """
        raw_value = int(speed_kmh * 10)  # 转换为原始值
        high_byte = (raw_value >> 8) & 0xFF
        low_byte = raw_value & 0xFF
        return bytes([high_byte, low_byte, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])


# ============================================================
# 第三部分：虚拟CAN总线模拟器
# ============================================================

class VirtualCanBus:
    """
    虚拟CAN总线模拟器

    模拟真实CAN总线的行为，包括：
        - 广播通信（所有节点都能收到消息）
        - 报文收发
        - 节点注册/注销
        - 总线负载统计

    这是一个纯软件模拟，用于学习演示，无需真实硬件。
    """

    def __init__(self, name: str = "vcan0"):
        """
        初始化虚拟CAN总线

        参数：
            name: 总线名称
        """
        self.name = name
        self._nodes = {}  # 节点字典: {节点ID: 回调函数}
        self._lock = threading.Lock()  # 线程锁，保证并发安全
        self._message_count = 0  # 报文计数
        self._start_time = time.time()  # 启动时间
        self._frame_history = []  # 报文历史记录（用于重放等）
        self._history_limit = 10000  # 历史记录上限

    def register_node(self, node_id: str, callback: Callable[[CanFrame], None]):
        """
        注册节点到总线

        参数：
            node_id: 节点标识
            callback: 收到报文时的回调函数
        """
        with self._lock:
            self._nodes[node_id] = callback
        print(f"[总线{self.name}] 节点 {node_id} 已注册")

    def unregister_node(self, node_id: str):
        """注销节点"""
        with self._lock:
            if node_id in self._nodes:
                del self._nodes[node_id]
        print(f"[总线{self.name}] 节点 {node_id} 已注销")

    def send(self, sender_id: str, frame: CanFrame):
        """
        发送CAN帧到总线（广播给所有其他节点）

        参数：
            sender_id: 发送节点ID
            frame: 要发送的CAN帧
        """
        # 更新时间戳
        frame.timestamp = time.time()

        # 保存到历史记录
        with self._lock:
            self._message_count += 1
            self._frame_history.append(frame)
            if len(self._frame_history) > self._history_limit:
                self._frame_history.pop(0)

            # 获取当前节点列表的副本（避免迭代过程中修改）
            nodes = dict(self._nodes)

        # 广播给所有节点（发送者也能收到，模拟真实CAN的广播特性）
        for node_id, callback in nodes.items():
            try:
                # 注意：真实CAN中发送节点也会接收自己发送的报文
                # （用于自检和错误检测），这里也模拟这种行为
                callback(frame)
            except Exception as e:
                print(f"[总线{self.name}] 节点 {node_id} 处理报文出错: {e}")

    def get_bus_load(self) -> float:
        """
        获取总线负载率（每秒帧数）

        返回：
            每秒平均帧数
        """
        elapsed = time.time() - self._start_time
        if elapsed == 0:
            return 0.0
        return self._message_count / elapsed

    def get_history(self) -> List[CanFrame]:
        """获取历史报文记录"""
        with self._lock:
            return list(self._frame_history)

    def clear_history(self):
        """清空历史记录"""
        with self._lock:
            self._frame_history.clear()
            self._message_count = 0
            self._start_time = time.time()


# ============================================================
# 第四部分：CAN总线嗅探演示
# ============================================================

class CanSniffer:
    """
    CAN总线嗅探器

    功能：
        - 监听CAN总线上的所有报文
        - 按ID分类统计
        - 计算各ID的发送周期
        - 实时显示报文

    对应真实场景：攻击者通过OBD接口接入CAN总线，
    监听所有通信内容。
    """

    def __init__(self, bus: VirtualCanBus, node_id: str = "sniffer"):
        """
        初始化嗅探器

        参数：
            bus: 要监听的虚拟CAN总线
            node_id: 嗅探器节点ID
        """
        self.bus = bus
        self.node_id = node_id
        self._stats = defaultdict(lambda: {
            'count': 0,
            'last_time': 0,
            'periods': [],
            'data_samples': []
        })
        self._running = False
        self._print_enabled = True

    def start(self):
        """启动嗅探（注册到总线）"""
        self.bus.register_node(self.node_id, self._on_frame_received)
        self._running = True
        print(f"\n{'='*60}")
        print(f"[嗅探器] 已启动，正在监听总线 {self.bus.name}")
        print(f"{'='*60}")

    def stop(self):
        """停止嗅探"""
        self._running = False
        self.bus.unregister_node(self.node_id)
        print(f"\n[嗅探器] 已停止")

    def _on_frame_received(self, frame: CanFrame):
        """
        收到CAN帧时的回调函数

        每次总线上有报文，这个函数就会被调用，
        模拟真实CAN的广播特性。
        """
        if not self._running:
            return

        can_id = frame.arbitration_id
        stats = self._stats[can_id]
        stats['count'] += 1

        # 计算周期
        if stats['last_time'] > 0:
            period = (frame.timestamp - stats['last_time']) * 1000  # 转换为毫秒
            stats['periods'].append(period)
            # 只保留最近100个周期样本
            if len(stats['periods']) > 100:
                stats['periods'].pop(0)

        stats['last_time'] = frame.timestamp

        # 保存数据样本（用于分析）
        if len(stats['data_samples']) < 10:
            stats['data_samples'].append(bytes(frame.data))

        # 实时打印
        if self._print_enabled:
            self._print_frame(frame)

    def _print_frame(self, frame: CanFrame):
        """格式化打印单帧"""
        data_str = ' '.join(f'{b:02X}' for b in frame.data)
        frame_type = "EXT" if frame.is_extended_id else "STD"
        if self._stats[frame.arbitration_id]['count'] <= 3:
            # 新ID首次出现时高亮显示
            print(f"  [NEW] ID={frame.arbitration_id:03X} ({frame_type}) "
                  f"DLC={frame.dlc}  Data: {data_str}")
        else:
            print(f"        ID={frame.arbitration_id:03X} ({frame_type}) "
                  f"DLC={frame.dlc}  Data: {data_str}")

    def print_statistics(self):
        """
        打印嗅探统计结果

        显示每个ID的出现次数、平均周期、发送速率等信息，
        帮助分析总线通信模式。
        """
        print(f"\n{'='*70}")
        print(f"[嗅探统计] 总线 {self.bus.name} 报文统计")
        print(f"{'='*70}")
        print(f"{'ID':>4}  {'次数':>6}  {'平均周期(ms)':>10}  {'速率(帧/秒)':>8}  {'数据样本'}")
        print(f"{'-'*70}")

        elapsed = time.time() - self.bus._start_time

        for can_id in sorted(self._stats.keys()):
            stats = self._stats[can_id]
            rate = stats['count'] / elapsed if elapsed > 0 else 0
            avg_period = (sum(stats['periods']) / len(stats['periods'])
                          if stats['periods'] else 0)

            # 显示第一个数据样本
            sample = ' '.join(f'{b:02X}' for b in stats['data_samples'][0]) \
                if stats['data_samples'] else '-'

            print(f"{can_id:03X}  {stats['count']:>6}  "
                  f"{avg_period:>10.2f}  {rate:>8.1f}  {sample}")

        print(f"{'-'*70}")
        print(f"总报文数: {sum(s['count'] for s in self._stats.values())}")
        print(f"唯一ID数: {len(self._stats)}")
        print(f"总线负载: {self.bus.get_bus_load():.1f} 帧/秒")


# ============================================================
# 第五部分：CAN重放攻击演示
# ============================================================

class CanReplayAttack:
    """
    CAN重放攻击演示

    攻击原理：
        1. 先录制一段正常的CAN报文（如解锁车门的报文序列）
        2. 在需要的时候重新发送这段报文
        3. 接收方无法区分是真实报文还是重放报文

    防御方法：
        - 报文认证码（MAC）
        - 新鲜值/计数器
        - 时间戳校验
    """

    def __init__(self, bus: VirtualCanBus, node_id: str = "replay_attacker"):
        """
        初始化重放攻击模块

        参数：
            bus: 目标CAN总线
            node_id: 攻击者节点ID
        """
        self.bus = bus
        self.node_id = node_id
        self._recorded_frames = []  # 录制的报文序列
        self._is_recording = False

    def start_recording(self, duration: float = 5.0):
        """
        开始录制CAN报文

        参数：
            duration: 录制时长（秒）

        对应真实场景：攻击者通过OBD接入总线，
        录制车主操作（如解锁车门）时的CAN报文。
        """
        print(f"\n{'='*60}")
        print(f"[重放攻击] 开始录制CAN报文（{duration}秒）")
        print(f"{'='*60}")
        print("提示：请在录制期间触发目标动作（如解锁车门）")
        print()

        self._recorded_frames = []
        self._is_recording = True

        # 注册到总线接收报文
        def record_callback(frame: CanFrame):
            if self._is_recording:
                self._recorded_frames.append(frame)

        self.bus.register_node(self.node_id + "_rec", record_callback)

        # 等待录制时长
        time.sleep(duration)

        self._is_recording = False
        self.bus.unregister_node(self.node_id + "_rec")

        print(f"\n[重放攻击] 录制完成，共录制 {len(self._recorded_frames)} 帧")

    def filter_by_id(self, target_ids: List[int]):
        """
        按ID过滤录制的报文

        参数：
            target_ids: 目标ID列表

        在真实攻击中，攻击者需要先分析哪些ID对应目标功能，
        然后只重放相关的报文。
        """
        filtered = [f for f in self._recorded_frames
                    if f.arbitration_id in target_ids]
        print(f"[重放攻击] 按ID过滤: {len(self._recorded_frames)} → {len(filtered)} 帧")
        self._recorded_frames = filtered

    def replay(self, loop_count: int = 1):
        """
        执行重放攻击

        参数：
            loop_count: 重放次数

        对应真实场景：攻击者发送录制好的控制报文，
        欺骗ECU执行相应动作。
        """
        if not self._recorded_frames:
            print("[重放攻击] 错误：没有录制的报文，无法重放")
            return

        print(f"\n{'='*60}")
        print(f"[重放攻击] 开始重放（共 {loop_count} 轮，{len(self._recorded_frames)} 帧/轮）")
        print(f"{'='*60}")

        start_time = self._recorded_frames[0].timestamp if self._recorded_frames else 0

        for loop in range(loop_count):
            print(f"\n--- 第 {loop + 1} 轮重放 ---")

            for i, frame in enumerate(self._recorded_frames):
                # 计算帧间延时（保持原始时序）
                if i > 0:
                    delay = frame.timestamp - self._recorded_frames[i - 1].timestamp
                    time.sleep(max(0, delay))  # 延时不能为负

                # 发送重放帧（注意：真实攻击中攻击者不会标记自己的身份）
                replay_frame = CanFrame(
                    arbitration_id=frame.arbitration_id,
                    data=bytes(frame.data),
                    is_extended_id=frame.is_extended_id,
                    is_fd=frame.is_fd
                )
                self.bus.send(self.node_id, replay_frame)

                data_str = ' '.join(f'{b:02X}' for b in frame.data[:4])
                print(f"  [重放] ID={frame.arbitration_id:03X} Data: {data_str}...")

        print(f"\n[重放攻击] 重放完成")

    def save_recording(self, filename: str):
        """保存录制的报文到文件（模拟candump -l）"""
        with open(filename, 'w') as f:
            for frame in self._recorded_frames:
                data_str = ''.join(f'{b:02X}' for b in frame.data)
                f.write(f"({frame.timestamp:.6f}) {self.bus.name} "
                        f"{frame.arbitration_id:03X}#{data_str}\n")
        print(f"[重放攻击] 录制已保存到 {filename}")


# ============================================================
# 第六部分：CAN注入攻击演示
# ============================================================

class CanInjectionAttack:
    """
    CAN注入攻击演示

    攻击原理：
        攻击者主动构造并发送伪造的CAN报文，
        欺骗ECU执行相应动作。

    与重放攻击的区别：
        - 重放攻击：发送之前录制的真实报文
        - 注入攻击：攻击者构造全新的报文

    常见攻击目标：
        - 伪造车速、转速等仪表数据
        - 控制车门、车窗、灯光
        - 控制刹车、油门等动力系统（高危！）
    """

    def __init__(self, bus: VirtualCanBus, node_id: str = "inject_attacker"):
        """
        初始化注入攻击模块

        参数：
            bus: 目标CAN总线
            node_id: 攻击者节点ID
        """
        self.bus = bus
        self.node_id = node_id

    def inject_frame(self, can_id: int, data: bytes, is_extended: bool = False):
        """
        注入单帧CAN报文

        参数：
            can_id: 目标CAN ID
            data: 数据内容
            is_extended: 是否扩展帧
        """
        frame = CanFrame(
            arbitration_id=can_id,
            data=data,
            is_extended_id=is_extended
        )
        self.bus.send(self.node_id, frame)
        data_str = ' '.join(f'{b:02X}' for b in data)
        print(f"  [注入] ID={can_id:03X} Data: {data_str}")

    def inject_speed_spoof(self, target_speed: float, duration: float = 3.0):
        """
        车速欺骗攻击（注入伪造的车速报文）

        参数：
            target_speed: 目标车速（km/h）
            duration: 持续时间（秒）

        攻击效果：仪表盘显示虚假车速，可能影响：
            - 驾驶员判断
            - 基于车速的辅助系统
            - 超速报警

        注意：这是演示代码，真实场景中这种攻击可能导致严重后果！
        """
        print(f"\n{'='*60}")
        print(f"[注入攻击] 车速欺骗攻击")
        print(f"  目标: 伪造车速为 {target_speed} km/h")
        print(f"  持续: {duration} 秒")
        print(f"  周期: 10ms (100帧/秒，模拟真实ECU发送频率)")
        print(f"{'='*60}")

        # 构造车速数据（假设ID=0x200，高2字节为车速原始值）
        speed_data = CanSignalParser.build_speed_frame(target_speed)

        start_time = time.time()
        frame_count = 0

        while time.time() - start_time < duration:
            self.inject_frame(0x200, speed_data)
            frame_count += 1
            time.sleep(0.01)  # 10ms周期

        print(f"\n[注入攻击] 车速欺骗完成，共发送 {frame_count} 帧")

    def inject_door_unlock(self):
        """
        车门解锁注入攻击

        模拟发送解锁车门的CAN报文。
        真实场景中，不同车型的门锁报文格式不同，
        需要先通过嗅探分析确定。
        """
        print(f"\n{'='*60}")
        print(f"[注入攻击] 车门解锁注入攻击")
        print(f"{'='*60}")

        # 假设解锁报文：ID=0x300，Byte0=0x01表示解锁
        unlock_data = bytes([0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

        # 发送多帧，模拟真实解锁时序
        print("发送解锁指令序列...")
        for i in range(3):
            self.inject_frame(0x300, unlock_data)
            time.sleep(0.02)

        print("[注入攻击] 解锁指令已发送")

    def inject_dos_attack(self, duration: float = 2.0):
        """
        CAN总线拒绝服务攻击（洪泛攻击）

        原理：使用最高优先级ID（0x000）持续发送报文，
        占满总线带宽，使正常报文无法发送。

        注意：这是非常危险的攻击，可能导致车辆功能失效！
        """
        print(f"\n{'='*60}")
        print(f"[注入攻击] CAN总线洪泛DoS攻击")
        print(f"  攻击ID: 0x000 (最高优先级)")
        print(f"  持续时间: {duration} 秒")
        print(f"{'='*60}")

        dos_data = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        start_time = time.time()
        frame_count = 0

        print("开始洪泛攻击...")
        while time.time() - start_time < duration:
            try:
                self.inject_frame(0x000, dos_data)
                frame_count += 1
                # 极短间隔，模拟洪泛
                time.sleep(0.0001)
            except Exception:
                break

        print(f"\n[注入攻击] DoS攻击完成，共发送 {frame_count} 帧")
        print(f"  攻击期间总线被高优先级ID 0x000 大量占用")
        print(f"  正常报文可能因无法获得总线使用权而延迟或丢失")


# ============================================================
# 第七部分：UDS诊断协议模拟
# ============================================================

class UdsDiagnosticSimulator:
    """
    UDS诊断协议模拟器

    模拟ECU的UDS诊断服务，包括：
        - 诊断会话控制 (0x10)
        - 安全访问 (0x27)
        - 读取数据 (0x22)
        - 写入数据 (0x2E)
        - 例程控制 (0x31)
        - ECU复位 (0x11)

    用于学习UDS诊断协议的工作原理。
    """

    # UDS服务ID定义
    UDS_SERVICES = {
        0x10: "DiagnosticSessionControl",  # 诊断会话控制
        0x11: "ECUReset",                   # ECU复位
        0x14: "ClearDiagnosticInformation", # 清除诊断信息
        0x19: "ReadDTCInformation",         # 读取DTC信息
        0x22: "ReadDataByIdentifier",       # 按ID读取数据
        0x27: "SecurityAccess",             # 安全访问
        0x28: "CommunicationControl",       # 通信控制
        0x2E: "WriteDataByIdentifier",      # 按ID写入数据
        0x2F: "InputOutputControlByIdentifier",  # 输入输出控制
        0x31: "RoutineControl",             # 例程控制
        0x34: "RequestDownload",            # 请求下载
        0x36: "TransferData",               # 数据传输
        0x37: "RequestTransferExit",        # 请求退出传输
        0x3E: "TesterPresent",              # 测试仪在线
    }

    # 否定响应码（NRC）
    NRC_CODES = {
        0x10: "generalReject",
        0x11: "serviceNotSupported",
        0x12: "subFunctionNotSupported",
        0x13: "incorrectMessageLengthOrInvalidFormat",
        0x22: "conditionsNotCorrect",
        0x24: "requestSequenceError",
        0x31: "requestOutOfRange",
        0x33: "securityAccessDenied",
        0x35: "invalidKey",
        0x36: "exceededNumberOfAttempts",
        0x37: "requiredTimeDelayNotExpired",
    }

    def __init__(self, bus: VirtualCanBus, ecu_name: str = "EngineECU",
                 request_id: int = 0x7E0, response_id: int = 0x7E8):
        """
        初始化UDS模拟器

        参数：
            bus: CAN总线
            ecu_name: ECU名称
            request_id: 诊断请求CAN ID（物理寻址）
            response_id: 诊断响应CAN ID
        """
        self.bus = bus
        self.ecu_name = ecu_name
        self.request_id = request_id
        self.response_id = response_id

        # ECU状态
        self._session = 1  # 1=默认会话, 2=编程会话, 3=扩展会话
        self._security_level = 0  # 安全访问等级（0=未解锁）
        self._security_attempts = 0  # 安全访问失败次数
        self._seed = 0  # 当前安全访问种子

        # 模拟的ECU数据
        self._data = {
            0xF190: b'LBV1Z3109KM123456',  # VIN码（DID 0xF190）
            0xF180: b'BMW12345',            # 零件号
            0xF186: b'V1.2.3',              # 软件版本
            0x0100: b'\x00\x00',            # 自定义数据
        }

        # 注册到总线
        self.bus.register_node(ecu_name, self._on_request)

        print(f"[UDS模拟器] {ecu_name} 已启动")
        print(f"  请求ID: 0x{request_id:03X}")
        print(f"  响应ID: 0x{response_id:03X}")

    def _on_request(self, frame: CanFrame):
        """处理收到的诊断请求"""
        if frame.arbitration_id != self.request_id:
            return  # 不是发给我的

        data = frame.data
        if len(data) < 2:
            return

        # 解析PCI（Protocol Control Information）
        # 单帧: PCI高4位=0，低4位=数据长度
        pci = data[0] >> 4
        length = data[0] & 0x0F

        if pci == 0:  # 单帧
            service_id = data[1]
            service_data = data[2:2 + length - 1] if length > 1 else b''
            self._handle_service(service_id, service_data)

    def _send_response(self, data: bytes):
        """发送诊断响应"""
        # 单帧格式: [PCI+长度] [响应数据...]
        pci_byte = 0x00 | len(data)  # 单帧
        response_data = bytes([pci_byte]) + data
        # 填充到8字节
        while len(response_data) < 8:
            response_data += b'\x00'

        frame = CanFrame(
            arbitration_id=self.response_id,
            data=response_data[:8]
        )
        self.bus.send(self.ecu_name, frame)

    def _send_negative_response(self, service_id: int, nrc: int):
        """发送否定响应"""
        nrc_name = self.NRC_CODES.get(nrc, f"Unknown(0x{nrc:02X})")
        print(f"  [UDS] 否定响应: SID=0x{service_id:02X} "
              f"NRC=0x{nrc:02X} ({nrc_name})")
        response = bytes([0x7F, service_id, nrc])
        self._send_response(response)

    def _handle_service(self, service_id: int, data: bytes):
        """处理UDS服务请求"""
        service_name = self.UDS_SERVICES.get(service_id, f"Unknown(0x{service_id:02X})")
        data_str = ' '.join(f'{b:02X}' for b in data)
        print(f"\n  [UDS] 请求: 0x{service_id:02X} ({service_name})")
        print(f"         数据: {data_str if data_str else '(无)'}")

        # 根据服务ID分发处理
        if service_id == 0x10:
            self._service_diagnostic_session_control(data)
        elif service_id == 0x27:
            self._service_security_access(data)
        elif service_id == 0x22:
            self._service_read_data_by_id(data)
        elif service_id == 0x2E:
            self._service_write_data_by_id(data)
        elif service_id == 0x3E:
            self._service_tester_present(data)
        elif service_id == 0x11:
            self._service_ecu_reset(data)
        else:
            self._send_negative_response(service_id, 0x11)  # 服务不支持

    def _service_diagnostic_session_control(self, data: bytes):
        """
        服务0x10: 诊断会话控制

        子功能：
            0x01: 默认会话
            0x02: 编程会话
            0x03: 扩展诊断会话
        """
        if len(data) < 1:
            self._send_negative_response(0x10, 0x13)
            return

        sub_func = data[0]
        session_names = {1: "默认会话", 2: "编程会话", 3: "扩展会话"}

        if sub_func not in session_names:
            self._send_negative_response(0x10, 0x12)  # 子功能不支持
            return

        self._session = sub_func
        print(f"  [UDS] 切换到: {session_names[sub_func]}")

        # 肯定响应: 0x50 (0x10+0x40) + 子功能 + 会话参数
        response = bytes([0x50, sub_func, 0x00, 0x32, 0x01, 0xF4])
        self._send_response(response)
        print(f"  [UDS] 响应: 0x50 0x{sub_func:02X} (会话切换成功)")

    def _service_security_access(self, data: bytes):
        """
        服务0x27: 安全访问

        这是UDS中最重要的安全机制。
        流程：
            1. 请求种子 (0x01, 0x03, 0x05...)
            2. ECU返回种子
            3. 测试仪计算密钥并发送 (0x02, 0x04, 0x06...)
            4. ECU验证密钥，成功则解锁

        安全等级：
            Level 1: 0x01请求, 0x02响应
            Level 2: 0x03请求, 0x04响应
            Level 3: 0x05请求, 0x06响应（最高级，用于刷写等）
        """
        if len(data) < 1:
            self._send_negative_response(0x27, 0x13)
            return

        sub_func = data[0]

        # 判断是请求种子还是发送密钥
        # 奇数子功能 = 请求种子，偶数 = 发送密钥
        if sub_func % 2 == 1:
            # 请求种子
            # 检查是否在正确的会话中
            if self._session == 1 and sub_func > 1:
                self._send_negative_response(0x27, 0x22)  # 条件不正确
                return

            # 生成随机种子（真实ECU使用硬件随机数生成器）
            level = (sub_func + 1) // 2
            self._seed = random.randint(0x0001, 0xFFFF)

            print(f"  [UDS] 安全访问 Level {level}: 请求种子")
            print(f"         生成种子: 0x{self._seed:04X}")

            # 响应: 0x67 (0x27+0x40) + 子功能 + 种子
            seed_bytes = self._seed.to_bytes(2, 'big')
            response = bytes([0x67, sub_func]) + seed_bytes
            self._send_response(response)

        else:
            # 发送密钥 - 验证密钥是否正确
            level = sub_func // 2
            key_data = data[1:]

            if len(key_data) < 2:
                self._send_negative_response(0x27, 0x13)
                return

            client_key = int.from_bytes(key_data[:2], 'big')

            # 计算正确的密钥（演示用：简单的异或算法）
            # 注意：真实ECU使用更复杂的算法（如AES、CMAC等）
            expected_key = self._calculate_key(self._seed, level)

            print(f"  [UDS] 安全访问 Level {level}: 验证密钥")
            print(f"         客户端密钥: 0x{client_key:04X}")
            print(f"         预期密钥:   0x{expected_key:04X}")

            if client_key == expected_key:
                # 密钥正确，解锁
                self._security_level = level
                self._security_attempts = 0
                print(f"         结果: 认证成功！已解锁 Level {level}")

                response = bytes([0x67, sub_func])
                self._send_response(response)
            else:
                # 密钥错误
                self._security_attempts += 1
                print(f"         结果: 认证失败！(第{self._security_attempts}次)")

                if self._security_attempts >= 3:
                    self._send_negative_response(0x27, 0x36)  # 超过尝试次数
                    print("         警告：已超过最大尝试次数，需等待延时")
                else:
                    self._send_negative_response(0x27, 0x35)  # 密钥无效

    def _calculate_key(self, seed: int, level: int) -> int:
        """
        计算安全访问密钥（演示算法）

        真实ECU的密钥算法是保密的，常见的有：
            - 异或+移位
            - AES加密
            - CMAC消息认证码

        这里使用简化的异或算法做演示。
        """
        # 演示算法：密钥 = 种子 XOR (0xABCD << level)
        return seed ^ (0xABCD >> level)

    def _service_read_data_by_id(self, data: bytes):
        """
        服务0x22: 根据标识符读取数据

        DID（Data Identifier）是数据的标识符，常见的：
            0xF190: VIN码
            0xF180: 零件号
            0xF186: 软件版本号
        """
        if len(data) < 2:
            self._send_negative_response(0x22, 0x13)
            return

        did = (data[0] << 8) | data[1]

        print(f"  [UDS] 读取DID: 0x{did:04X}")

        if did in self._data:
            # 检查安全访问要求
            # 某些DID需要安全访问才能读取
            restricted_dids = [0x0100]  # 这些DID需要解锁
            if did in restricted_dids and self._security_level < 1:
                self._send_negative_response(0x22, 0x33)  # 安全访问被拒绝
                print("         拒绝: 需要安全访问")
                return

            value = self._data[did]
            print(f"         值: {value.hex().upper()}")

            # 肯定响应: 0x62 (0x22+0x40) + DID + 数据
            response = bytes([0x62]) + did.to_bytes(2, 'big') + value
            self._send_response(response)
        else:
            self._send_negative_response(0x22, 0x31)  # 请求超出范围
            print("         拒绝: DID不存在")

    def _service_write_data_by_id(self, data: bytes):
        """
        服务0x2E: 根据标识符写入数据

        注意：写入操作通常需要安全访问权限。
        """
        if len(data) < 2:
            self._send_negative_response(0x2E, 0x13)
            return

        did = (data[0] << 8) | data[1]
        write_data = data[2:]

        print(f"  [UDS] 写入DID: 0x{did:04X}")
        print(f"         数据: {write_data.hex().upper()}")

        # 写入操作需要安全访问Level 1
        if self._security_level < 1:
            self._send_negative_response(0x2E, 0x33)
            print("         拒绝: 需要安全访问 Level 1")
            return

        if did in self._data:
            self._data[did] = write_data
            print(f"         结果: 写入成功")

            # 肯定响应: 0x6E (0x2E+0x40) + DID
            response = bytes([0x6E]) + did.to_bytes(2, 'big')
            self._send_response(response)
        else:
            self._send_negative_response(0x2E, 0x31)
            print("         拒绝: DID不存在")

    def _service_tester_present(self, data: bytes):
        """
        服务0x3E: 测试仪在线

        用于保持诊断会话活跃。
        如果一段时间不发送，ECU会自动退出当前会话，
        回到默认会话，并清除安全访问状态。
        """
        # 简单回应即可
        response = bytes([0x7E])  # 0x3E + 0x40
        if data:
            response += data[:1]
        self._send_response(response)
        print(f"  [UDS] TesterPresent: 会话保持活跃")

    def _service_ecu_reset(self, data: bytes):
        """
        服务0x11: ECU复位

        子功能：
            0x01: 硬复位
            0x02: 钥匙关闭复位
            0x03: 软复位
        """
        if len(data) < 1:
            self._send_negative_response(0x11, 0x13)
            return

        sub_func = data[0]

        # 复位操作需要安全访问
        if self._security_level < 1:
            self._send_negative_response(0x11, 0x33)
            print(f"  [UDS] ECU复位: 拒绝，需要安全访问")
            return

        print(f"  [UDS] ECU复位: 子功能 0x{sub_func:02X}")

        # 肯定响应
        response = bytes([0x51, sub_func])  # 0x11 + 0x40
        self._send_response(response)

        # 模拟复位：重置会话和安全状态
        self._session = 1
        self._security_level = 0
        print("  [UDS] ECU已复位，回到默认会话")


class UdsTester:
    """
    UDS诊断测试仪（客户端）

    模拟诊断仪向ECU发送诊断请求，
    用于学习和测试UDS诊断服务。
    """

    def __init__(self, bus: VirtualCanBus, request_id: int = 0x7E0,
                 response_id: int = 0x7E8):
        self.bus = bus
        self.request_id = request_id
        self.response_id = response_id
        self._last_response = None
        self._response_event = threading.Event()

        # 注册响应监听
        self.bus.register_node("uds_tester", self._on_response)

    def _on_response(self, frame: CanFrame):
        """接收诊断响应"""
        if frame.arbitration_id == self.response_id:
            self._last_response = frame.data
            self._response_event.set()

    def send_request(self, service_data: bytes, timeout: float = 1.0) -> Optional[bytes]:
        """
        发送UDS请求并等待响应

        参数：
            service_data: 服务数据（包括SID和参数）
            timeout: 超时时间（秒）

        返回：
            响应数据（不包括PCI字节），超时返回None
        """
        self._response_event.clear()
        self._last_response = None

        # 构造单帧请求: [PCI+长度] [服务数据...]
        pci_byte = 0x00 | len(service_data)
        request_data = bytes([pci_byte]) + service_data
        while len(request_data) < 8:
            request_data += b'\x00'

        frame = CanFrame(
            arbitration_id=self.request_id,
            data=request_data[:8]
        )

        print(f"\n[诊断仪] 发送请求: {' '.join(f'{b:02X}' for b in service_data)}")
        self.bus.send("uds_tester", frame)

        # 等待响应
        if self._response_event.wait(timeout):
            if self._last_response and len(self._last_response) > 1:
                pci = self._last_response[0] >> 4
                length = self._last_response[0] & 0x0F
                if pci == 0 and length > 0:
                    return self._last_response[1:1 + length]
        return None

    def demo_security_access_crack(self):
        """
        演示安全访问破解过程

        展示攻击者如何绕过安全访问：
            1. 请求种子
            2. 通过逆向得到密钥算法
            3. 计算正确密钥
            4. 通过认证

        注意：真实ECU的算法通常更复杂，破解难度更大。
        """
        print(f"\n{'='*60}")
        print(f"[UDS演示] 安全访问破解演示")
        print(f"{'='*60}")
        print()

        # 步骤1: 切换到扩展会话
        print("步骤1: 切换到扩展诊断会话")
        resp = self.send_request(bytes([0x10, 0x03]))  # 0x10 0x03 = 扩展会话
        if resp and resp[0] == 0x50:
            print("  ✓ 成功进入扩展会话")
        else:
            print("  ✗ 会话切换失败")
            return

        time.sleep(0.5)

        # 步骤2: 请求种子
        print("\n步骤2: 请求安全访问种子 (Level 1)")
        resp = self.send_request(bytes([0x27, 0x01]))  # 0x27 0x01 = 请求种子 Level1
        if resp and resp[0] == 0x67:
            seed = int.from_bytes(resp[2:4], 'big')
            print(f"  ✓ 收到种子: 0x{seed:04X}")
        else:
            print("  ✗ 请求种子失败")
            return

        time.sleep(0.5)

        # 步骤3: 破解密钥算法
        # （在真实场景中，攻击者需要逆向ECU固件来获取算法）
        print("\n步骤3: 分析密钥算法（模拟逆向固件）")
        print("  通过逆向ECU固件，发现密钥算法：")
        print("    Key = Seed XOR (0xABCD >> level)")

        # 计算密钥
        level = 1
        key = seed ^ (0xABCD >> level)
        print(f"  计算密钥: 0x{seed:04X} XOR (0xABCD >> {level}) = 0x{key:04X}")

        time.sleep(0.5)

        # 步骤4: 发送密钥
        print("\n步骤4: 发送密钥，尝试通过认证")
        key_bytes = key.to_bytes(2, 'big')
        resp = self.send_request(bytes([0x27, 0x02]) + key_bytes)

        if resp and resp[0] == 0x67:
            print("  ✓ 认证成功！安全访问已解锁 Level 1")
            print()
            print("  ⚠️  解锁后可执行的敏感操作：")
            print("    - 修改ECU配置参数")
            print("    - 写入自定义数据")
            print("    - 执行ECU复位")
            print("    - （更高等级还可刷写固件）")
        else:
            print("  ✗ 认证失败")
            if resp and resp[0] == 0x7F:
                nrc = resp[2]
                nrc_name = UdsDiagnosticSimulator.NRC_CODES.get(nrc, f"Unknown")
                print(f"    NRC: 0x{nrc:02X} ({nrc_name})")


# ============================================================
# 第八部分：CAN入侵检测演示
# ============================================================

class CanIntrusionDetection:
    """
    CAN总线入侵检测系统（IDS）演示

    实现几种常见的CAN IDS检测方法：
        1. 基于频率/周期的异常检测
        2. 基于数据内容的异常检测
        3. 基于未知ID的检测

    注意：这是简化的演示版本，真实IDS更复杂。
    """

    def __init__(self, bus: VirtualCanBus):
        self.bus = bus
        self._id_stats = defaultdict(lambda: {
            'count': 0,
            'last_time': 0,
            'periods': [],
            'avg_period': 0,
            'known': False
        })
        self._baseline_built = False
        self._alerts = []
        self._running = False

    def build_baseline(self, duration: float = 5.0):
        """
        建立正常行为基线

        IDS需要先学习正常的通信模式，
        才能检测出异常行为。
        """
        print(f"\n{'='*60}")
        print(f"[IDS] 建立正常行为基线（{duration}秒）")
        print(f"{'='*60}")

        self._id_stats.clear()
        self._baseline_built = False

        # 注册监听器
        def baseline_listener(frame: CanFrame):
            if not self._baseline_built:
                self._update_stats(frame)

        self.bus.register_node("ids_baseline", baseline_listener)

        time.sleep(duration)
        self._baseline_built = True
        self.bus.unregister_node("ids_baseline")

        # 计算平均周期
        for can_id, stats in self._id_stats.items():
            if stats['periods']:
                stats['avg_period'] = sum(stats['periods']) / len(stats['periods'])
            stats['known'] = True

        print(f"\n[IDS] 基线建立完成，共学习到 {len(self._id_stats)} 个正常ID")
        for can_id in sorted(self._id_stats.keys()):
            stats = self._id_stats[can_id]
            print(f"  ID={can_id:03X}: 平均周期={stats['avg_period']:.2f}ms "
                  f"({stats['count']} 样本)")

    def _update_stats(self, frame: CanFrame):
        """更新ID统计信息"""
        can_id = frame.arbitration_id
        stats = self._id_stats[can_id]
        stats['count'] += 1

        if stats['last_time'] > 0:
            period = (frame.timestamp - stats['last_time']) * 1000
            stats['periods'].append(period)
            if len(stats['periods']) > 50:
                stats['periods'].pop(0)

        stats['last_time'] = frame.timestamp

    def start_detection(self):
        """启动入侵检测"""
        if not self._baseline_built:
            print("[IDS] 错误：请先建立基线")
            return

        self._running = True
        self._alerts.clear()

        self.bus.register_node("ids_detector", self._detect_callback)
        print(f"\n{'='*60}")
        print(f"[IDS] 入侵检测已启动")
        print(f"{'='*60}")

    def stop_detection(self):
        """停止入侵检测"""
        self._running = False
        self.bus.unregister_node("ids_detector")
        print(f"\n[IDS] 检测已停止，共产生 {len(self._alerts)} 条告警")

    def _detect_callback(self, frame: CanFrame):
        """检测回调函数"""
        if not self._running:
            return

        can_id = frame.arbitration_id
        stats = self._id_stats[can_id]

        # 检测1: 未知ID检测
        if not stats['known']:
            self._alert("未知ID检测", can_id,
                        f"检测到未知CAN ID: 0x{can_id:03X}")
            stats['known'] = True  # 避免重复告警
            return

        # 更新统计
        old_count = stats['count']
        self._update_stats(frame)

        # 检测2: 频率异常检测（周期远小于正常值）
        if stats['periods'] and stats['avg_period'] > 0:
            current_period = stats['periods'][-1]
            # 如果当前周期小于平均周期的1/5，视为异常
            if current_period < stats['avg_period'] / 5 and old_count > 5:
                self._alert("频率异常", can_id,
                            f"发送频率异常: 当前周期={current_period:.2f}ms, "
                            f"正常周期={stats['avg_period']:.2f}ms")

        # 检测3: 数据跳变检测（简单示例）
        # 对于车速等信号，短时间内不会跳变太大
        if can_id == 0x200 and len(frame.data) >= 2:
            current_speed = CanSignalParser.parse_vehicle_speed(frame.data)
            # 这里简化处理，实际需要保存历史值进行比较
            pass

    def _alert(self, alert_type: str, can_id: int, message: str):
        """产生告警"""
        alert = {
            'time': time.time(),
            'type': alert_type,
            'can_id': can_id,
            'message': message
        }
        self._alerts.append(alert)
        print(f"  ⚠️  [告警] {alert_type} | ID=0x{can_id:03X} | {message}")


# ============================================================
# 第九部分：模拟ECU节点
# ============================================================

class SimulatedECU:
    """
    模拟真实ECU节点，周期发送CAN报文

    用于生成正常的CAN总线流量，
    为嗅探、攻击演示提供真实的背景流量。
    """

    def __init__(self, bus: VirtualCanBus, name: str):
        self.bus = bus
        self.name = name
        self._running = False
        self._thread = None
        self._speed = 50.0  # 当前车速（km/h）
        self._engine_speed = 2000  # 发动机转速（rpm）
        self._door_status = 0x00  # 车门状态，全关

    def start(self):
        """启动ECU模拟"""
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print(f"[模拟ECU] {self.name} 已启动")

    def stop(self):
        """停止ECU模拟"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        print(f"[模拟ECU] {self.name} 已停止")

    def _run(self):
        """ECU主循环"""
        while self._running:
            # 模拟车速变化（缓慢波动）
            self._speed += random.uniform(-1, 1)
            self._speed = max(0, min(120, self._speed))

            # 模拟发动机转速波动
            self._engine_speed += random.uniform(-50, 50)
            self._engine_speed = max(600, min(6000, self._engine_speed))

            # 发送发动机转速报文 (ID=0x100, 10ms周期)
            rpm_raw = int(self._engine_speed / 0.25)
            data = bytes([
                (rpm_raw >> 8) & 0xFF, rpm_raw & 0xFF,
                0x00, 0x00, 0x00, 0x00, 0x00, 0x00
            ])
            self._send_frame(0x100, data)

            time.sleep(0.01)  # 10ms周期

            # 发送车速报文 (ID=0x200, 20ms周期)
            # 每两次循环发一次
            if random.random() < 0.5:
                speed_raw = int(self._speed * 10)
                data = bytes([
                    (speed_raw >> 8) & 0xFF, speed_raw & 0xFF,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00
                ])
                self._send_frame(0x200, data)

            # 发送车门状态 (ID=0x300, 100ms周期)
            if random.random() < 0.1:
                data = bytes([self._door_status, 0x00, 0x00, 0x00,
                              0x00, 0x00, 0x00, 0x00])
                self._send_frame(0x300, data)

            # 发送一些其他ID的报文，增加真实性
            if random.random() < 0.3:
                self._send_frame(0x400, bytes([random.randint(0, 255) for _ in range(8)]))
            if random.random() < 0.2:
                self._send_frame(0x500, bytes([random.randint(0, 255) for _ in range(8)]))

    def _send_frame(self, can_id: int, data: bytes):
        """发送CAN帧"""
        frame = CanFrame(arbitration_id=can_id, data=data)
        self.bus.send(self.name, frame)

    def unlock_door(self):
        """模拟解锁车门（用于重放攻击的录制）"""
        print(f"[模拟ECU] {self.name}: 触发车门解锁动作")
        # 模拟解锁时的报文序列
        for _ in range(3):
            self._door_status = 0x01  # 左前门打开
            data = bytes([self._door_status, 0x00, 0x00, 0x00,
                          0x00, 0x00, 0x00, 0x00])
            self._send_frame(0x300, data)
            time.sleep(0.02)

        time.sleep(0.1)
        self._door_status = 0x00  # 恢复关闭（模拟显示后复位）


# ============================================================
# 第十部分：主函数 - 综合演示
# ============================================================

def demo_basic_frame():
    """演示1: CAN帧结构与解析"""
    print("=" * 60)
    print("【演示1】CAN帧结构模拟与解析")
    print("=" * 60)

    parser = CanFrameParser()

    # 创建标准帧
    std_frame = parser.create_standard_frame(0x100, b'\x12\x34\x56\x78')
    print(f"\n标准数据帧:")
    print(f"  {std_frame}")
    print(f"  ID: 0x{std_frame.arbitration_id:03X} (11位)")
    print(f"  数据长度: {len(std_frame.data)} 字节")
    print(f"  DLC: {std_frame.dlc}")

    # 创建扩展帧
    ext_frame = parser.create_extended_frame(0x18F00100, b'\x01\x02\x03')
    print(f"\n扩展数据帧:")
    print(f"  {ext_frame}")
    print(f"  ID: 0x{ext_frame.arbitration_id:08X} (29位)")

    # 创建CAN FD帧
    fd_data = bytes(range(20))  # 20字节数据
    fd_frame = parser.create_canfd_frame(0x200, fd_data)
    print(f"\nCAN FD帧:")
    print(f"  {fd_frame}")
    print(f"  数据长度: {len(fd_frame.data)} 字节")
    print(f"  DLC: {fd_frame.dlc}")

    # 远程帧
    rtr_frame = parser.create_remote_frame(0x100, dlc=8)
    print(f"\n远程帧:")
    print(f"  {rtr_frame}")

    # 信号解析演示
    print(f"\n信号解析演示:")
    speed_data = CanSignalParser.build_speed_frame(85.5)
    speed = CanSignalParser.parse_vehicle_speed(speed_data)
    print(f"  车速报文: {' '.join(f'{b:02X}' for b in speed_data)}")
    print(f"  解析结果: {speed} km/h")

    print("\n" + "=" * 60)
    input("按Enter键继续下一个演示...")


def demo_sniffer():
    """演示2: CAN总线嗅探"""
    print("\n" + "=" * 60)
    print("【演示2】CAN总线嗅探演示")
    print("=" * 60)

    # 创建虚拟总线
    bus = VirtualCanBus("vcan_demo")

    # 创建模拟ECU
    ecu = SimulatedECU(bus, "EngineECU")
    ecu.start()

    time.sleep(0.1)  # 等待ECU启动

    # 创建嗅探器
    sniffer = CanSniffer(bus)
    sniffer._print_enabled = False  # 先不打印，只统计
    sniffer.start()

    # 运行一段时间
    print("\n嗅探运行中（3秒）...")
    time.sleep(3)

    sniffer.stop()

    # 显示统计结果
    sniffer.print_statistics()

    ecu.stop()

    print("\n" + "=" * 60)
    input("按Enter键继续下一个演示...")


def demo_replay_attack():
    """演示3: CAN重放攻击"""
    print("\n" + "=" * 60)
    print("【演示3】CAN重放攻击演示")
    print("=" * 60)

    bus = VirtualCanBus("vcan_replay")

    # 创建模拟ECU
    ecu = SimulatedECU(bus, "BodyECU")
    ecu.start()

    # 创建嗅探器（用于观察）
    sniffer = CanSniffer(bus)
    sniffer._print_enabled = False
    sniffer.start()

    time.sleep(0.2)

    # 创建重放攻击模块
    attacker = CanReplayAttack(bus)

    # 录制阶段
    print("\n--- 录制阶段（2秒）---")
    print("在录制过程中，模拟触发一次车门解锁...")

    # 启动录制（在另一个线程中触发解锁）
    def record_and_trigger():
        time.sleep(0.5)
        ecu.unlock_door()  # 模拟车主按解锁键

    trigger_thread = threading.Thread(target=record_and_trigger, daemon=True)
    trigger_thread.start()

    attacker.start_recording(duration=2.0)

    # 过滤出门锁相关的ID (0x300)
    attacker.filter_by_id([0x300])

    # 重放阶段
    time.sleep(0.5)
    print("\n--- 重放阶段 ---")
    print("攻击者发送录制的解锁报文...")
    attacker.replay(loop_count=1)

    sniffer.stop()
    ecu.stop()

    print("\n" + "=" * 60)
    print("重放攻击原理总结:")
    print("  1. 攻击者先录制正常的控制报文")
    print("  2. 在需要时重放这些报文")
    print("  3. 接收方无法区分真实报文和重放报文")
    print("  4. 防御：报文认证码(MAC)、新鲜值、计数器")

    input("\n按Enter键继续下一个演示...")


def demo_injection_attack():
    """演示4: CAN注入攻击"""
    print("\n" + "=" * 60)
    print("【演示4】CAN注入攻击演示")
    print("=" * 60)

    bus = VirtualCanBus("vcan_inject")

    # 创建IDS（先建立基线）
    ids = CanIntrusionDetection(bus)

    # 创建模拟ECU
    ecu = SimulatedECU(bus, "NormalECU")
    ecu.start()

    # 建立IDS基线
    ids.build_baseline(duration=2.0)

    # 启动IDS检测
    ids.start_detection()

    time.sleep(0.5)

    # 创建注入攻击者
    injector = CanInjectionAttack(bus)

    # 攻击1: 车速欺骗
    injector.inject_speed_spoof(target_speed=150.0, duration=1.0)

    time.sleep(0.5)

    # 攻击2: 未知ID注入（会触发IDS告警）
    print("\n注入未知ID的报文...")
    for _ in range(10):
        injector.inject_frame(0x666, bytes([0xDE, 0xAD, 0xBE, 0xEF,
                                            0x00, 0x00, 0x00, 0x00]))
        time.sleep(0.05)

    time.sleep(0.5)

    # 攻击3: 洪泛DoS（会触发频率异常告警）
    injector.inject_dos_attack(duration=1.0)

    ids.stop_detection()
    ecu.stop()

    print("\n" + "=" * 60)
    print("注入攻击原理总结:")
    print("  1. 攻击者构造并发送伪造的CAN报文")
    print("  2. 报文格式完全合法，接收方无法直接判断真伪")
    print("  3. 可用于：伪造仪表数据、控制车辆功能、DoS等")
    print("  4. IDS可检测：未知ID、频率异常、数据异常等")
    print("  5. 根本防御：报文认证（如MAC）、安全网关")

    input("\n按Enter键继续下一个演示...")


def demo_uds_diagnostic():
    """演示5: UDS诊断协议"""
    print("\n" + "=" * 60)
    print("【演示5】UDS诊断协议与安全访问")
    print("=" * 60)

    bus = VirtualCanBus("vcan_uds")

    # 创建UDS模拟ECU
    ecu = UdsDiagnosticSimulator(
        bus,
        ecu_name="EngineECU",
        request_id=0x7E0,  # 请求ID（测试仪→ECU）
        response_id=0x7E8  # 响应ID（ECU→测试仪）
    )

    # 创建诊断测试仪
    tester = UdsTester(bus, request_id=0x7E0, response_id=0x7E8)

    time.sleep(0.2)

    # 演示1: 读取公开数据（VIN码，不需要安全访问）
    print("\n--- 测试1: 读取VIN码（无需安全访问）---")
    resp = tester.send_request(bytes([0x22, 0xF1, 0x90]))  # 0x22 + DID=0xF190
    if resp and resp[0] == 0x62:
        vin = resp[3:].decode('ascii', errors='replace')
        print(f"  VIN码: {vin}")

    time.sleep(0.3)

    # 演示2: 尝试写入数据（未解锁，会被拒绝）
    print("\n--- 测试2: 尝试写入数据（未解锁状态）---")
    resp = tester.send_request(
        bytes([0x2E, 0x01, 0x00, 0xAA, 0xBB])
    )
    if resp and resp[0] == 0x7F:
        nrc = resp[2]
        nrc_name = UdsDiagnosticSimulator.NRC_CODES.get(nrc, "Unknown")
        print(f"  被拒绝: NRC=0x{nrc:02X} ({nrc_name})")

    time.sleep(0.3)

    # 演示3: 完整的安全访问破解流程
    tester.demo_security_access_crack()

    time.sleep(0.3)

    # 演示4: 解锁后再次尝试写入
    print("\n--- 测试4: 解锁后再次写入数据 ---")
    resp = tester.send_request(
        bytes([0x2E, 0x01, 0x00, 0xAA, 0xBB])
    )
    if resp and resp[0] == 0x6E:
        print("  ✓ 写入成功！")

    time.sleep(0.3)

    # 演示5: 读取验证
    print("\n--- 测试5: 读取验证写入结果 ---")
    resp = tester.send_request(bytes([0x22, 0x01, 0x00]))
    if resp and resp[0] == 0x62:
        data = resp[3:].hex().upper()
        print(f"  读取到的数据: {data}")

    print("\n" + "=" * 60)
    print("UDS诊断安全总结:")
    print("  1. 0x27安全访问是UDS的核心保护机制")
    print("  2. 敏感操作（写数据、刷写、复位）需要安全访问")
    print("  3. 密钥算法的安全性是关键，简单算法容易被破解")
    print("  4. 防护措施：复杂算法、尝试次数限制、延时机制")
    print("  5. 真实ECU通常使用AES/CMAC等强加密算法")

    input("\n按Enter键继续下一个演示...")


def demo_ids():
    """演示6: CAN入侵检测"""
    print("\n" + "=" * 60)
    print("【演示6】CAN总线入侵检测系统")
    print("=" * 60)

    bus = VirtualCanBus("vcan_ids")

    # 创建模拟ECU
    ecu = SimulatedECU(bus, "NormalECU")
    ecu.start()

    # 创建IDS
    ids = CanIntrusionDetection(bus)

    # 第一步：建立基线
    ids.build_baseline(duration=3.0)

    # 第二步：启动检测
    ids.start_detection()

    # 第三步：模拟攻击，观察IDS告警
    print("\n[攻击模拟] 注入未知ID报文...")
    injector = CanInjectionAttack(bus)
    for _ in range(5):
        injector.inject_frame(0x999, bytes([0x00] * 8))
        time.sleep(0.1)

    time.sleep(0.5)

    print("\n[攻击模拟] 高频率洪泛攻击...")
    injector.inject_dos_attack(duration=0.5)

    time.sleep(0.5)

    # 停止检测
    ids.stop_detection()
    ecu.stop()

    print("\n" + "=" * 60)
    print("入侵检测总结:")
    print("  1. 频率/周期检测：检测发送频率异常（如洪泛攻击）")
    print("  2. 未知ID检测：检测总线上出现的陌生ID")
    print("  3. 数据内容检测：检测信号值的异常跳变")
    print("  4. 时钟指纹检测：通过ECU时钟差异识别伪造报文")
    print("  5. 机器学习检测：使用AI模型检测复杂攻击")
    print("  6. 局限性：IDS只能检测，不能完全阻止攻击")

    input("\n按Enter键查看总结...")


def main():
    """
    主函数：按顺序运行所有演示
    """
    print("=" * 60)
    print("           CAN总线模拟与攻击演示系统")
    print("=" * 60)
    print()
    print("本脚本包含以下演示内容：")
    print("  1. CAN帧结构模拟与解析")
    print("  2. CAN总线嗅探演示")
    print("  3. CAN重放攻击演示")
    print("  4. CAN注入攻击演示（含IDS检测）")
    print("  5. UDS诊断协议与安全访问破解")
    print("  6. CAN入侵检测系统演示")
    print()
    print("注意：本脚本仅用于学习研究，请勿用于真实车辆！")
    print("=" * 60)

    input("\n按Enter键开始演示...")

    try:
        # 演示1: CAN帧结构
        demo_basic_frame()

        # 演示2: 嗅探
        demo_sniffer()

        # 演示3: 重放攻击
        demo_replay_attack()

        # 演示4: 注入攻击
        demo_injection_attack()

        # 演示5: UDS诊断
        demo_uds_diagnostic()

        # 演示6: IDS
        demo_ids()

    except KeyboardInterrupt:
        print("\n\n演示被用户中断")

    print("\n" + "=" * 60)
    print("所有演示结束！")
    print("=" * 60)
    print()
    print("学习建议：")
    print("  1. 仔细阅读代码中的注释，理解每个模块的原理")
    print("  2. 修改参数，观察不同参数对攻击/检测效果的影响")
    print("  3. 尝试实现更多功能（如CAN FD、更多IDS算法）")
    print("  4. 结合配套文档（车载网络安全.md）深入学习")
    print()
    print("⚠️  再次提醒：仅供学习研究，严禁用于真实车辆！")


if __name__ == "__main__":
    main()
