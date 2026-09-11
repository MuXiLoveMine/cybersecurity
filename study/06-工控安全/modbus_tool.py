#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modbus 协议测试工具
==================

本工具用于 Modbus TCP 协议的学习和测试，提供以下功能：
    1. 读取保持寄存器（功能码 0x03）
    2. 读取输入寄存器（功能码 0x04）
    3. 读取线圈（功能码 0x01）
    4. 读取离散输入（功能码 0x02）
    5. 写入单个寄存器（功能码 0x06）
    6. 写入多个寄存器（功能码 0x10）
    7. 写入单个线圈（功能码 0x05）
    8. 写入多个线圈（功能码 0x0F）
    9. 设备信息探测（功能码 0x08 / 0x11 / 0x2B）
    10. 批量扫描 Modbus 设备

注意事项：
    - 本工具仅供学习研究和授权测试使用
    - 严禁对未经授权的工控系统使用
    - 工控系统安全关系生产安全，请谨慎操作

作者：工控安全学习工具
版本：1.0
日期：2024
"""

import socket
import struct
import time
import argparse
import sys
from typing import List, Optional, Tuple


# ============================================================================
#  Modbus TCP 常量定义
# ============================================================================

# Modbus 默认端口
MODBUS_DEFAULT_PORT = 502

# Modbus 功能码定义
FUNC_READ_COILS = 0x01          # 读线圈
FUNC_READ_DISCRETE_INPUTS = 0x02  # 读离散输入
FUNC_READ_HOLDING_REGISTERS = 0x03  # 读保持寄存器
FUNC_READ_INPUT_REGISTERS = 0x04   # 读输入寄存器
FUNC_WRITE_SINGLE_COIL = 0x05      # 写单个线圈
FUNC_WRITE_SINGLE_REGISTER = 0x06  # 写单个寄存器
FUNC_READ_EXCEPTION_STATUS = 0x07  # 读异常状态
FUNC_DIAGNOSTIC = 0x08             # 诊断
FUNC_GET_COMM_EVENT_COUNTER = 0x0B  # 读事件计数器
FUNC_GET_COMM_EVENT_LOG = 0x0C      # 读事件日志
FUNC_WRITE_MULTIPLE_COILS = 0x0F    # 写多个线圈
FUNC_WRITE_MULTIPLE_REGISTERS = 0x10  # 写多个寄存器
FUNC_REPORT_SLAVE_ID = 0x11         # 报告从站ID
FUNC_READ_FILE_RECORD = 0x14        # 读文件记录
FUNC_WRITE_FILE_RECORD = 0x15       # 写文件记录
FUNC_MASK_WRITE_REGISTER = 0x16     # 屏蔽写寄存器
FUNC_READ_WRITE_MULTIPLE_REGISTERS = 0x17  # 读写多个寄存器
FUNC_READ_FIFO_QUEUE = 0x18         # 读 FIFO 队列
FUNC_ENCAPSULATED_INTERFACE_TRANSPORT = 0x2B  # 封装接口传输（设备识别）

# Modbus 异常码定义
EXCEPTION_CODES = {
    0x01: "非法功能码 (Illegal Function)",
    0x02: "非法数据地址 (Illegal Data Address)",
    0x03: "非法数据值 (Illegal Data Value)",
    0x04: "从站设备故障 (Slave Device Failure)",
    0x05: "确认 (Acknowledge)",
    0x06: "从站忙碌 (Slave Device Busy)",
    0x08: "存储奇偶校验错误 (Memory Parity Error)",
    0x0A: "网关路径不可用 (Gateway Path Unavailable)",
    0x0B: "网关目标设备无响应 (Gateway Target Device Failed to Respond)",
}


# ============================================================================
#  Modbus TCP 客户端类
# ============================================================================

class ModbusTCPClient:
    """
    Modbus TCP 客户端类

    实现 Modbus TCP 协议的基本操作，包括：
    - 连接和断开连接
    - 各种功能码的请求和响应处理
    - 设备信息探测

    协议格式说明：
    Modbus TCP = MBAP Header + Modbus PDU
    MBAP Header (7字节):
        - 事务标识符 (2字节)：请求/响应匹配
        - 协议标识符 (2字节)：固定为 0x0000 (Modbus)
        - 长度 (2字节)：后续字节数
        - 单元标识符 (1字节)：从站地址
    """

    def __init__(self, host: str, port: int = MODBUS_DEFAULT_PORT,
                 unit_id: int = 1, timeout: float = 3.0):
        """
        初始化 Modbus TCP 客户端

        参数:
            host: 目标主机 IP 地址
            port: 目标端口，默认 502
            unit_id: 从站地址 / 单元标识符，默认 1
            timeout: 超时时间（秒），默认 3 秒
        """
        self.host = host
        self.port = port
        self.unit_id = unit_id
        self.timeout = timeout
        self.sock: Optional[socket.socket] = None
        self.transaction_id = 0  # 事务标识符，每次请求递增

    def connect(self) -> bool:
        """
        建立 TCP 连接

        返回:
            True: 连接成功
            False: 连接失败
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.host, self.port))
            return True
        except socket.timeout:
            print(f"[错误] 连接超时：{self.host}:{self.port}")
            return False
        except ConnectionRefusedError:
            print(f"[错误] 连接被拒绝：{self.host}:{self.port}")
            return False
        except Exception as e:
            print(f"[错误] 连接失败：{e}")
            return False

    def close(self):
        """关闭连接"""
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None

    def _build_mbap_header(self, pdu_length: int) -> bytes:
        """
        构建 MBAP (Modbus Application Protocol) 头部

        MBAP 头部共 7 字节：
        - 事务标识符：2 字节，请求响应配对用
        - 协议标识符：2 字节，Modbus 固定为 0x0000
        - 长度：2 字节，单元标识 + PDU 的总长度
        - 单元标识符：1 字节，从站地址

        参数:
            pdu_length: PDU 数据的长度（字节数）

        返回:
            7 字节的 MBAP 头部
        """
        self.transaction_id = (self.transaction_id + 1) % 65536
        # 长度字段 = 单元标识符(1字节) + PDU长度
        length = 1 + pdu_length
        # 使用大端序（网络字节序）打包
        header = struct.pack(
            '>HHHB',
            self.transaction_id,  # 事务标识符
            0x0000,               # 协议标识符（0 = Modbus）
            length,               # 长度
            self.unit_id          # 单元标识符（从站地址）
        )
        return header

    def _send_request(self, pdu: bytes) -> Optional[bytes]:
        """
        发送 Modbus 请求并接收响应

        参数:
            pdu: Modbus PDU 数据（功能码 + 数据）

        返回:
            响应 PDU 数据（功能码 + 数据），失败返回 None
        """
        if not self.sock:
            print("[错误] 未建立连接")
            return None

        try:
            # 构建完整的 Modbus TCP 报文
            mbap = self._build_mbap_header(len(pdu))
            request = mbap + pdu

            # 发送请求
            self.sock.sendall(request)

            # 接收 MBAP 头部（7 字节）
            mbap_resp = self._recv_exact(7)
            if not mbap_resp or len(mbap_resp) < 7:
                print("[错误] 接收 MBAP 头部失败")
                return None

            # 解析 MBAP 头部
            txn_id, protocol_id, length, unit_id = struct.unpack('>HHHB', mbap_resp)

            # 验证协议标识符
            if protocol_id != 0:
                print(f"[警告] 协议标识符不匹配：{protocol_id}")

            # 接收 PDU 数据
            # length 字段包含单元标识符(1字节) + PDU，所以 PDU 长度 = length - 1
            pdu_resp = self._recv_exact(length - 1)
            if not pdu_resp:
                print("[错误] 接收 PDU 数据失败")
                return None

            return pdu_resp

        except socket.timeout:
            print("[错误] 接收响应超时")
            return None
        except Exception as e:
            print(f"[错误] 通信异常：{e}")
            return None

    def _recv_exact(self, n: int) -> Optional[bytes]:
        """
        精确接收 n 字节数据

        TCP 是流协议，一次 recv 不一定返回全部数据，
        需要循环接收直到收到足够的字节数。

        参数:
            n: 需要接收的字节数

        返回:
            接收到的数据，失败返回 None
        """
        data = b''
        while len(data) < n:
            try:
                chunk = self.sock.recv(n - len(data))
                if not chunk:
                    return None
                data += chunk
            except socket.timeout:
                return None
        return data

    def _check_exception(self, pdu: bytes) -> bool:
        """
        检查响应是否为异常响应

        Modbus 异常响应的功能码最高位为 1，
        即 异常功能码 = 原功能码 + 0x80

        参数:
            pdu: 响应 PDU 数据

        返回:
            True: 是异常响应
            False: 是正常响应
        """
        if len(pdu) < 2:
            return False

        func_code = pdu[0]
        # 如果功能码最高位为 1，表示异常响应
        if func_code & 0x80:
            exception_code = pdu[1]
            exception_msg = EXCEPTION_CODES.get(exception_code, f"未知异常码: 0x{exception_code:02X}")
            print(f"[异常响应] 功能码: 0x{func_code:02X}, 异常码: 0x{exception_code:02X} - {exception_msg}")
            return True
        return False

    # ========================================================================
    #  读操作方法
    # ========================================================================

    def read_holding_registers(self, start_addr: int, quantity: int) -> Optional[List[int]]:
        """
        读取保持寄存器（功能码 0x03）

        保持寄存器是可读写的 16 位寄存器，常用于存储控制参数、设定值等。
        对应地址范围：40001 ~ 49999（1-based），协议地址 0x0000 ~ 0x270F（0-based）

        请求 PDU 格式:
            功能码: 1 字节 (0x03)
            起始地址: 2 字节 (0x0000 ~ 0xFFFF)
            寄存器数量: 2 字节 (1 ~ 125，取决于设备)

        响应 PDU 格式:
            功能码: 1 字节 (0x03)
            字节计数: 1 字节 (寄存器数量 × 2)
            寄存器值: N 字节 (每个寄存器 2 字节，大端序)

        参数:
            start_addr: 起始地址（0-based）
            quantity: 读取的寄存器数量

        返回:
            寄存器值列表，失败返回 None
        """
        # 构建 PDU: 功能码(1) + 起始地址(2) + 数量(2) = 5 字节
        pdu = struct.pack('>BHH', FUNC_READ_HOLDING_REGISTERS, start_addr, quantity)

        # 发送请求
        resp_pdu = self._send_request(pdu)
        if not resp_pdu:
            return None

        # 检查异常响应
        if self._check_exception(resp_pdu):
            return None

        # 解析响应
        # 响应格式: 功能码(1) + 字节计数(1) + 数据(N)
        if len(resp_pdu) < 3:
            print("[错误] 响应数据太短")
            return None

        func_code = resp_pdu[0]
        byte_count = resp_pdu[1]
        data = resp_pdu[2:]

        if len(data) != byte_count:
            print(f"[警告] 数据长度不匹配：期望 {byte_count} 字节，实际 {len(data)} 字节")

        # 解析寄存器值（每个寄存器 2 字节，大端序）
        registers = []
        for i in range(0, byte_count, 2):
            if i + 1 < len(data):
                value = struct.unpack('>H', data[i:i + 2])[0]
                registers.append(value)

        return registers

    def read_input_registers(self, start_addr: int, quantity: int) -> Optional[List[int]]:
        """
        读取输入寄存器（功能码 0x04）

        输入寄存器是只读的 16 位寄存器，常用于读取模拟量输入（如温度、压力等传感器数据）。
        对应地址范围：30001 ~ 39999（1-based）

        请求 PDU 格式: 与功能码 0x03 相同
        响应 PDU 格式: 与功能码 0x03 相同

        参数:
            start_addr: 起始地址（0-based）
            quantity: 读取的寄存器数量

        返回:
            寄存器值列表，失败返回 None
        """
        pdu = struct.pack('>BHH', FUNC_READ_INPUT_REGISTERS, start_addr, quantity)
        resp_pdu = self._send_request(pdu)

        if not resp_pdu or self._check_exception(resp_pdu):
            return None

        if len(resp_pdu) < 3:
            print("[错误] 响应数据太短")
            return None

        byte_count = resp_pdu[1]
        data = resp_pdu[2:]

        registers = []
        for i in range(0, byte_count, 2):
            if i + 1 < len(data):
                value = struct.unpack('>H', data[i:i + 2])[0]
                registers.append(value)

        return registers

    def read_coils(self, start_addr: int, quantity: int) -> Optional[List[bool]]:
        """
        读取线圈状态（功能码 0x01）

        线圈是可读写的布尔量（1 bit），常用于控制输出（如继电器、开关）。
        对应地址范围：00001 ~ 09999（1-based）

        请求 PDU 格式:
            功能码: 1 字节 (0x01)
            起始地址: 2 字节
            线圈数量: 2 字节

        响应 PDU 格式:
            功能码: 1 字节 (0x01)
            字节计数: 1 字节
            线圈状态: N 字节 (每个字节 8 个线圈，低位在前)

        参数:
            start_addr: 起始地址（0-based）
            quantity: 读取的线圈数量

        返回:
            线圈状态列表（布尔值），失败返回 None
        """
        pdu = struct.pack('>BHH', FUNC_READ_COILS, start_addr, quantity)
        resp_pdu = self._send_request(pdu)

        if not resp_pdu or self._check_exception(resp_pdu):
            return None

        if len(resp_pdu) < 3:
            print("[错误] 响应数据太短")
            return None

        byte_count = resp_pdu[1]
        data = resp_pdu[2:]

        # 解析线圈状态
        # 每个字节的第 0 位（最低位）对应第一个线圈
        coils = []
        for i in range(quantity):
            byte_idx = i // 8
            bit_idx = i % 8
            if byte_idx < len(data):
                # 右移 bit_idx 位，然后与 0x01 相与
                coil_state = bool((data[byte_idx] >> bit_idx) & 0x01)
                coils.append(coil_state)

        return coils

    def read_discrete_inputs(self, start_addr: int, quantity: int) -> Optional[List[bool]]:
        """
        读取离散输入（功能码 0x02）

        离散输入是只读的布尔量，常用于读取开关量输入（如限位开关、按钮状态）。
        对应地址范围：10001 ~ 19999（1-based）

        请求和响应格式与功能码 0x01 类似。

        参数:
            start_addr: 起始地址（0-based）
            quantity: 读取的离散输入数量

        返回:
            离散输入状态列表（布尔值），失败返回 None
        """
        pdu = struct.pack('>BHH', FUNC_READ_DISCRETE_INPUTS, start_addr, quantity)
        resp_pdu = self._send_request(pdu)

        if not resp_pdu or self._check_exception(resp_pdu):
            return None

        if len(resp_pdu) < 3:
            print("[错误] 响应数据太短")
            return None

        byte_count = resp_pdu[1]
        data = resp_pdu[2:]

        inputs = []
        for i in range(quantity):
            byte_idx = i // 8
            bit_idx = i % 8
            if byte_idx < len(data):
                input_state = bool((data[byte_idx] >> bit_idx) & 0x01)
                inputs.append(input_state)

        return inputs

    # ========================================================================
    #  写操作方法
    # ========================================================================

    def write_single_register(self, addr: int, value: int) -> bool:
        """
        写入单个保持寄存器（功能码 0x06）

        请求 PDU 格式:
            功能码: 1 字节 (0x06)
            寄存器地址: 2 字节
            寄存器值: 2 字节

        响应 PDU 格式:
            与请求相同（正常情况下，设备原样返回）

        参数:
            addr: 寄存器地址（0-based）
            value: 要写入的值 (0 ~ 65535)

        返回:
            True: 写入成功
            False: 写入失败
        """
        pdu = struct.pack('>BHH', FUNC_WRITE_SINGLE_REGISTER, addr, value)
        resp_pdu = self._send_request(pdu)

        if not resp_pdu or self._check_exception(resp_pdu):
            return False

        # 正常响应应该和请求相同
        if resp_pdu == pdu:
            return True
        else:
            print("[警告] 响应与请求不一致")
            # 有些设备可能返回略有不同，但功能码正确也视为成功
            if len(resp_pdu) >= 1 and resp_pdu[0] == FUNC_WRITE_SINGLE_REGISTER:
                return True
            return False

    def write_multiple_registers(self, start_addr: int, values: List[int]) -> bool:
        """
        写入多个保持寄存器（功能码 0x10）

        请求 PDU 格式:
            功能码: 1 字节 (0x10)
            起始地址: 2 字节
            寄存器数量: 2 字节
            字节计数: 1 字节 (寄存器数量 × 2)
            寄存器值: N 字节

        响应 PDU 格式:
            功能码: 1 字节 (0x10)
            起始地址: 2 字节
            寄存器数量: 2 字节

        参数:
            start_addr: 起始地址（0-based）
            values: 要写入的寄存器值列表

        返回:
            True: 写入成功
            False: 写入失败
        """
        quantity = len(values)
        byte_count = quantity * 2

        # 构建 PDU: 功能码 + 起始地址 + 数量 + 字节计数 + 数据
        pdu = struct.pack('>BHHB', FUNC_WRITE_MULTIPLE_REGISTERS, start_addr, quantity, byte_count)
        for value in values:
            pdu += struct.pack('>H', value)

        resp_pdu = self._send_request(pdu)

        if not resp_pdu or self._check_exception(resp_pdu):
            return False

        # 解析响应
        if len(resp_pdu) >= 5:
            resp_addr = struct.unpack('>H', resp_pdu[1:3])[0]
            resp_quantity = struct.unpack('>H', resp_pdu[3:5])[0]
            if resp_addr == start_addr and resp_quantity == quantity:
                return True

        print("[警告] 写入响应不匹配")
        return False

    def write_single_coil(self, addr: int, value: bool) -> bool:
        """
        写入单个线圈（功能码 0x05）

        请求 PDU 格式:
            功能码: 1 字节 (0x05)
            线圈地址: 2 字节
            线圈值: 2 字节 (ON = 0xFF00, OFF = 0x0000)

        注意：线圈值使用特殊编码，0xFF00 表示 ON，0x0000 表示 OFF，
        其他值都是非法的。

        参数:
            addr: 线圈地址（0-based）
            value: True=ON, False=OFF

        返回:
            True: 写入成功
            False: 写入失败
        """
        # 线圈值编码：ON = 0xFF00, OFF = 0x0000
        coil_value = 0xFF00 if value else 0x0000
        pdu = struct.pack('>BHH', FUNC_WRITE_SINGLE_COIL, addr, coil_value)
        resp_pdu = self._send_request(pdu)

        if not resp_pdu or self._check_exception(resp_pdu):
            return False

        if resp_pdu == pdu:
            return True
        else:
            if len(resp_pdu) >= 1 and resp_pdu[0] == FUNC_WRITE_SINGLE_COIL:
                return True
            return False

    def write_multiple_coils(self, start_addr: int, values: List[bool]) -> bool:
        """
        写入多个线圈（功能码 0x0F）

        请求 PDU 格式:
            功能码: 1 字节 (0x0F)
            起始地址: 2 字节
            线圈数量: 2 字节
            字节计数: 1 字节
            线圈值: N 字节 (每个字节 8 个线圈，低位在前)

        响应 PDU 格式:
            功能码: 1 字节 (0x0F)
            起始地址: 2 字节
            线圈数量: 2 字节

        参数:
            start_addr: 起始地址（0-based）
            values: 线圈状态列表（布尔值）

        返回:
            True: 写入成功
            False: 写入失败
        """
        quantity = len(values)

        # 计算字节数（向上取整）
        byte_count = (quantity + 7) // 8

        # 构建线圈状态字节
        coil_bytes = bytearray(byte_count)
        for i, value in enumerate(values):
            byte_idx = i // 8
            bit_idx = i % 8
            if value:
                coil_bytes[byte_idx] |= (1 << bit_idx)

        # 构建 PDU
        pdu = struct.pack('>BHHB', FUNC_WRITE_MULTIPLE_COILS, start_addr, quantity, byte_count)
        pdu += bytes(coil_bytes)

        resp_pdu = self._send_request(pdu)

        if not resp_pdu or self._check_exception(resp_pdu):
            return False

        if len(resp_pdu) >= 5:
            resp_addr = struct.unpack('>H', resp_pdu[1:3])[0]
            resp_quantity = struct.unpack('>H', resp_pdu[3:5])[0]
            if resp_addr == start_addr and resp_quantity == quantity:
                return True

        print("[警告] 写入响应不匹配")
        return False

    # ========================================================================
    #  设备信息探测方法
    # ========================================================================

    def report_slave_id(self) -> Optional[dict]:
        """
        报告从站 ID（功能码 0x11）

        读取从站的标识信息，包括：
        - 从站标识（设备型号）
        - 运行状态
        - 附加数据（厂商自定义）

        响应 PDU 格式:
            功能码: 1 字节 (0x11)
            字节计数: 1 字节
            从站标识: N 字节
            运行状态: 1 字节 (0xFF=ON, 0x00=OFF)
            附加数据: 可选

        返回:
            设备信息字典，失败返回 None
        """
        pdu = struct.pack('>B', FUNC_REPORT_SLAVE_ID)
        resp_pdu = self._send_request(pdu)

        if not resp_pdu or self._check_exception(resp_pdu):
            return None

        if len(resp_pdu) < 3:
            return None

        byte_count = resp_pdu[1]
        data = resp_pdu[2:]

        if len(data) < byte_count:
            return None

        # 解析从站 ID
        # 注意：不同厂商的实现可能不同
        slave_id = data[0] if byte_count >= 1 else 0
        run_status = data[1] if byte_count >= 2 else 0
        additional = data[2:byte_count] if byte_count > 2 else b''

        return {
            "slave_id": slave_id,
            "run_status": "ON" if run_status == 0xFF else "OFF",
            "additional_data": additional.hex(),
            "additional_text": additional.decode('ascii', errors='replace')
        }

    def diagnostic(self, sub_func: int, data: bytes = b'') -> Optional[bytes]:
        """
        诊断功能（功能码 0x08）

        诊断功能提供了多种子功能，用于测试和诊断通信。

        常用子功能码:
            0x0000: 返回查询数据（回环测试）
            0x0001: 重新启动通信选项
            0x0002: 返回诊断寄存器
            0x0003: 改变 ASCII 输入分隔符
            0x000A: 清除计数器和诊断寄存器
            0x000B: 返回总线报文计数
            0x000C: 返回总线通信错误计数
            0x000D: 返回总线异常错误计数
            0x000E: 返回从站消息计数
            0x000F: 返回从站无响应计数
            0x0011: 返回从站 NAK 计数
            0x0012: 返回从站繁忙计数
            0x0014: 返回总线字符超限计数

        参数:
            sub_func: 子功能码
            data: 子功能数据

        返回:
            响应数据，失败返回 None
        """
        pdu = struct.pack('>BH', FUNC_DIAGNOSTIC, sub_func) + data
        resp_pdu = self._send_request(pdu)

        if not resp_pdu or self._check_exception(resp_pdu):
            return None

        # 响应数据 = 子功能码(2) + 数据
        return resp_pdu[1:]

    def read_device_identification(self) -> Optional[dict]:
        """
        读取设备识别信息（功能码 0x2B，MEI 类型 0x0E）

        使用封装接口传输功能（0x2B）的设备识别子功能，
        读取设备的厂商名称、产品代码、版本号等信息。

        请求格式:
            功能码: 0x2B
            MEI 类型: 0x0E (设备识别)
            读设备ID 代码:
                0x01: 读取基本设备识别
                0x02: 读取常规设备识别
                0x03: 读取扩展设备识别
                0x04: 读取特定识别对象
            对象ID: 第一个要读取的对象ID

        对象 ID 定义:
            0x00: 厂商名称 (VendorName)
            0x01: 产品代码 (ProductCode)
            0x02: 版本号 (Revision)
            0x03: 厂商URL (VendorUrl)
            0x04: 产品名称 (ProductName)
            0x05: 型号名称 (ModelName)
            0x06: 用户应用名称 (UserApplicationName)

        返回:
            设备识别信息字典，失败返回 None
        """
        # 构建请求：读取基本设备识别（从对象 0 开始）
        # MEI 类型 = 0x0E, 读ID代码 = 0x01(基本), 对象ID = 0x00
        pdu = struct.pack('>BBBB', FUNC_ENCAPSULATED_INTERFACE_TRANSPORT, 0x0E, 0x01, 0x00)
        resp_pdu = self._send_request(pdu)

        if not resp_pdu or self._check_exception(resp_pdu):
            return None

        if len(resp_pdu) < 6:
            return None

        # 解析响应
        func_code = resp_pdu[0]
        mei_type = resp_pdu[1]
        read_dev_id_code = resp_pdu[2]
        conformity_level = resp_pdu[3]
        more_follows = resp_pdu[4]
        next_object_id = resp_pdu[5]
        num_objects = resp_pdu[6] if len(resp_pdu) > 6 else 0

        device_info = {
            "mei_type": mei_type,
            "read_dev_id_code": read_dev_id_code,
            "conformity_level": conformity_level,
            "more_follows": more_follows,
            "next_object_id": next_object_id,
            "num_objects": num_objects,
            "objects": {}
        }

        # 解析对象列表
        offset = 7
        for _ in range(num_objects):
            if offset + 2 > len(resp_pdu):
                break
            obj_id = resp_pdu[offset]
            obj_len = resp_pdu[offset + 1]
            offset += 2
            if offset + obj_len > len(resp_pdu):
                break
            obj_value = resp_pdu[offset:offset + obj_len]
            offset += obj_len

            # 对象 ID 到名称的映射
            obj_names = {
                0x00: "VendorName (厂商名称)",
                0x01: "ProductCode (产品代码)",
                0x02: "Revision (版本号)",
                0x03: "VendorUrl (厂商URL)",
                0x04: "ProductName (产品名称)",
                0x05: "ModelName (型号名称)",
                0x06: "UserApplicationName (用户应用名称)",
            }
            obj_name = obj_names.get(obj_id, f"Object_{obj_id}")
            device_info["objects"][obj_name] = obj_value.decode('ascii', errors='replace')

        return device_info


# ============================================================================
#  设备扫描功能
# ============================================================================

def scan_modbus_devices(network: str, port: int = 502, timeout: float = 1.0,
                        start_addr: int = 0, quantity: int = 10) -> List[dict]:
    """
    扫描网络中的 Modbus TCP 设备

    通过发送读保持寄存器请求来探测设备是否存在。
    注意：此操作属于主动扫描，可能对网络造成影响，请谨慎使用。

    参数:
        network: 网络地址，如 "192.168.1.0/24"
        port: 端口号，默认 502
        timeout: 超时时间（秒）
        start_addr: 读取的起始寄存器地址
        quantity: 读取的寄存器数量

    返回:
        发现的设备列表
    """
    import ipaddress

    try:
        network_obj = ipaddress.ip_network(network, strict=False)
    except ValueError as e:
        print(f"[错误] 无效的网络地址：{e}")
        return []

    devices = []
    total = network_obj.num_addresses

    print(f"[信息] 开始扫描网络：{network}")
    print(f"[信息] 目标端口：{port}")
    print(f"[信息] 主机数量：{total}")
    print("-" * 50)

    for i, ip in enumerate(network_obj.hosts(), 1):
        ip_str = str(ip)
        if i % 10 == 0 or i == 1:
            print(f"\r[扫描中] 进度：{i}/{total}", end='', flush=True)

        client = ModbusTCPClient(ip_str, port, timeout=timeout)
        if client.connect():
            # 尝试读取寄存器
            result = client.read_holding_registers(start_addr, min(quantity, 10))
            device_info = {
                "ip": ip_str,
                "port": port,
                "status": "online",
                "protocol": "Modbus TCP"
            }

            if result is not None:
                device_info["register_read"] = True
                device_info["sample_data"] = result[:5]  # 前5个寄存器
                # 尝试读取设备 ID
                slave_id = client.report_slave_id()
                if slave_id:
                    device_info["slave_id"] = slave_id

                devices.append(device_info)
                print(f"\n[发现] {ip_str}:{port} - Modbus TCP 设备")
                if slave_id:
                    print(f"       从站ID: {slave_id['slave_id']}, 状态: {slave_id['run_status']}")
            else:
                device_info["register_read"] = False
                devices.append(device_info)
                print(f"\n[发现] {ip_str}:{port} - 端口开放，但读取寄存器失败")

            client.close()
        # 连接失败则跳过，不打印

    print(f"\n[完成] 扫描完成，共发现 {len(devices)} 台设备")
    return devices


# ============================================================================
#  命令行界面
# ============================================================================

def print_banner():
    """打印工具横幅"""
    banner = """
╔═══════════════════════════════════════════════════════╗
║          Modbus TCP 协议测试工具 v1.0                 ║
║          Modbus Protocol Testing Tool                ║
╠═══════════════════════════════════════════════════════╣
║  用途：工控安全学习、授权测试                          ║
║  警告：请勿对未经授权的系统使用本工具                   ║
╚═══════════════════════════════════════════════════════╝
"""
    print(banner)


def main():
    """主函数 - 命令行接口"""
    parser = argparse.ArgumentParser(
        description='Modbus TCP 协议测试工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 读取保持寄存器
  python modbus_tool.py -H 192.168.1.100 read-holding -a 0 -n 10

  # 写入单个寄存器
  python modbus_tool.py -H 192.168.1.100 write-register -a 0 -v 1234

  # 读取线圈
  python modbus_tool.py -H 192.168.1.100 read-coils -a 0 -n 8

  # 写入单个线圈
  python modbus_tool.py -H 192.168.1.100 write-coil -a 0 -v 1

  # 设备信息探测
  python modbus_tool.py -H 192.168.1.100 identify

  # 扫描网络中的设备
  python modbus_tool.py scan -n 192.168.1.0/24
        """
    )

    # 通用参数
    parser.add_argument('-H', '--host', help='目标主机 IP 地址')
    parser.add_argument('-p', '--port', type=int, default=502, help='目标端口（默认: 502）')
    parser.add_argument('-u', '--unit-id', type=int, default=1, help='从站地址/单元ID（默认: 1）')
    parser.add_argument('-t', '--timeout', type=float, default=3.0, help='超时时间（秒，默认: 3）')

    # 子命令
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # ---- 读取保持寄存器 ----
    read_holding = subparsers.add_parser('read-holding', help='读取保持寄存器 (功能码 0x03)')
    read_holding.add_argument('-a', '--address', type=int, required=True, help='起始地址 (0-based)')
    read_holding.add_argument('-n', '--number', type=int, default=10, help='读取数量 (默认: 10)')

    # ---- 读取输入寄存器 ----
    read_input = subparsers.add_parser('read-input', help='读取输入寄存器 (功能码 0x04)')
    read_input.add_argument('-a', '--address', type=int, required=True, help='起始地址 (0-based)')
    read_input.add_argument('-n', '--number', type=int, default=10, help='读取数量 (默认: 10)')

    # ---- 读取线圈 ----
    read_coils = subparsers.add_parser('read-coils', help='读取线圈状态 (功能码 0x01)')
    read_coils.add_argument('-a', '--address', type=int, required=True, help='起始地址 (0-based)')
    read_coils.add_argument('-n', '--number', type=int, default=8, help='读取数量 (默认: 8)')

    # ---- 读取离散输入 ----
    read_discrete = subparsers.add_parser('read-discrete', help='读取离散输入 (功能码 0x02)')
    read_discrete.add_argument('-a', '--address', type=int, required=True, help='起始地址 (0-based)')
    read_discrete.add_argument('-n', '--number', type=int, default=8, help='读取数量 (默认: 8)')

    # ---- 写入单个寄存器 ----
    write_reg = subparsers.add_parser('write-register', help='写入单个保持寄存器 (功能码 0x06)')
    write_reg.add_argument('-a', '--address', type=int, required=True, help='寄存器地址 (0-based)')
    write_reg.add_argument('-v', '--value', type=int, required=True, help='写入值 (0-65535)')

    # ---- 写入多个寄存器 ----
    write_regs = subparsers.add_parser('write-registers', help='写入多个保持寄存器 (功能码 0x10)')
    write_regs.add_argument('-a', '--address', type=int, required=True, help='起始地址 (0-based)')
    write_regs.add_argument('-v', '--values', type=int, nargs='+', required=True, help='写入值列表（空格分隔）')

    # ---- 写入单个线圈 ----
    write_coil = subparsers.add_parser('write-coil', help='写入单个线圈 (功能码 0x05)')
    write_coil.add_argument('-a', '--address', type=int, required=True, help='线圈地址 (0-based)')
    write_coil.add_argument('-v', '--value', type=int, choices=[0, 1], required=True, help='线圈值 (0=OFF, 1=ON)')

    # ---- 写入多个线圈 ----
    write_coils = subparsers.add_parser('write-coils', help='写入多个线圈 (功能码 0x0F)')
    write_coils.add_argument('-a', '--address', type=int, required=True, help='起始地址 (0-based)')
    write_coils.add_argument('-v', '--values', type=int, nargs='+', required=True, help='线圈值列表 (0/1 空格分隔)')

    # ---- 设备信息探测 ----
    subparsers.add_parser('identify', help='设备信息探测 (功能码 0x11 / 0x2B)')

    # ---- 网络扫描 ----
    scan_parser = subparsers.add_parser('scan', help='扫描网络中的 Modbus 设备')
    scan_parser.add_argument('-n', '--network', required=True, help='目标网络，如 192.168.1.0/24')
    scan_parser.add_argument('-p', '--port', type=int, default=502, help='目标端口 (默认: 502)')
    scan_parser.add_argument('-t', '--timeout', type=float, default=1.0, help='超时时间 (默认: 1秒)')

    args = parser.parse_args()

    # 没有指定命令
    if not args.command:
        print_banner()
        parser.print_help()
        return

    # ========================================
    #  扫描命令（不需要 host 参数）
    # ========================================
    if args.command == 'scan':
        print_banner()
        print("⚠️  警告：网络扫描可能对目标网络造成影响")
        print("⚠️  请确保已获得合法授权")
        confirm = input("确认继续？(yes/no): ").strip().lower()
        if confirm not in ('yes', 'y'):
            print("已取消")
            return

        scan_modbus_devices(args.network, args.port, args.timeout)
        return

    # ========================================
    #  其他命令（需要 host 参数）
    # ========================================
    if not args.host:
        print("[错误] 请指定目标主机地址 (-H/--host)")
        return

    print_banner()

    # 警告提示（写操作）
    write_commands = ['write-register', 'write-registers', 'write-coil', 'write-coils']
    if args.command in write_commands:
        print("⚠️  ⚠️  ⚠️  重要警告 ⚠️  ⚠️  ⚠️")
        print("您即将执行写入操作，这可能改变设备状态！")
        print("请确保：")
        print("  1. 您已获得合法的书面授权")
        print("  2. 操作不会影响正常生产")
        print("  3. 您了解操作的后果")
        confirm = input("确认继续？(输入 YES 确认): ").strip()
        if confirm != 'YES':
            print("已取消操作")
            return
        print()

    # 创建客户端并连接
    client = ModbusTCPClient(
        host=args.host,
        port=args.port,
        unit_id=args.unit_id,
        timeout=args.timeout
    )

    print(f"[信息] 连接目标：{args.host}:{args.port}")
    print(f"[信息] 从站地址：{args.unit_id}")
    print()

    if not client.connect():
        print("[错误] 连接失败")
        return

    print("[成功] 已建立连接")
    print()

    try:
        # ---- 读取保持寄存器 ----
        if args.command == 'read-holding':
            print(f"[操作] 读取保持寄存器")
            print(f"       起始地址：{args.address} (4{args.address+1:04d})")
            print(f"       数量：{args.number}")
            print()

            result = client.read_holding_registers(args.address, args.number)
            if result is not None:
                print("[结果] 寄存器值：")
                print("-" * 50)
                print(f"{'地址':<10} {'十进制':<12} {'十六进制':<12}")
                print("-" * 50)
                for i, value in enumerate(result):
                    addr = args.address + i
                    print(f"{addr:<10} {value:<12} 0x{value:04X}")
                print("-" * 50)
                print(f"共读取 {len(result)} 个寄存器")
            else:
                print("[失败] 读取失败")

        # ---- 读取输入寄存器 ----
        elif args.command == 'read-input':
            print(f"[操作] 读取输入寄存器")
            print(f"       起始地址：{args.address} (3{args.address+1:04d})")
            print(f"       数量：{args.number}")
            print()

            result = client.read_input_registers(args.address, args.number)
            if result is not None:
                print("[结果] 输入寄存器值：")
                print("-" * 50)
                print(f"{'地址':<10} {'十进制':<12} {'十六进制':<12}")
                print("-" * 50)
                for i, value in enumerate(result):
                    addr = args.address + i
                    print(f"{addr:<10} {value:<12} 0x{value:04X}")
                print("-" * 50)
            else:
                print("[失败] 读取失败")

        # ---- 读取线圈 ----
        elif args.command == 'read-coils':
            print(f"[操作] 读取线圈状态")
            print(f"       起始地址：{args.address} (0{args.address+1:04d})")
            print(f"       数量：{args.number}")
            print()

            result = client.read_coils(args.address, args.number)
            if result is not None:
                print("[结果] 线圈状态：")
                print("-" * 40)
                print(f"{'地址':<10} {'状态':<10}")
                print("-" * 40)
                for i, value in enumerate(result):
                    addr = args.address + i
                    status = "ON (1)" if value else "OFF (0)"
                    print(f"{addr:<10} {status}")
                print("-" * 40)
            else:
                print("[失败] 读取失败")

        # ---- 读取离散输入 ----
        elif args.command == 'read-discrete':
            print(f"[操作] 读取离散输入")
            print(f"       起始地址：{args.address} (1{args.address+1:04d})")
            print(f"       数量：{args.number}")
            print()

            result = client.read_discrete_inputs(args.address, args.number)
            if result is not None:
                print("[结果] 离散输入状态：")
                print("-" * 40)
                print(f"{'地址':<10} {'状态':<10}")
                print("-" * 40)
                for i, value in enumerate(result):
                    addr = args.address + i
                    status = "ON (1)" if value else "OFF (0)"
                    print(f"{addr:<10} {status}")
                print("-" * 40)
            else:
                print("[失败] 读取失败")

        # ---- 写入单个寄存器 ----
        elif args.command == 'write-register':
            print(f"[操作] 写入单个保持寄存器")
            print(f"       地址：{args.address}")
            print(f"       值：{args.value} (0x{args.value:04X})")
            print()

            if client.write_single_register(args.address, args.value):
                print("[成功] 写入成功")
            else:
                print("[失败] 写入失败")

        # ---- 写入多个寄存器 ----
        elif args.command == 'write-registers':
            print(f"[操作] 写入多个保持寄存器")
            print(f"       起始地址：{args.address}")
            print(f"       数量：{len(args.values)}")
            print(f"       值：{args.values}")
            print()

            if client.write_multiple_registers(args.address, args.values):
                print("[成功] 写入成功")
            else:
                print("[失败] 写入失败")

        # ---- 写入单个线圈 ----
        elif args.command == 'write-coil':
            status = "ON" if args.value else "OFF"
            print(f"[操作] 写入单个线圈")
            print(f"       地址：{args.address}")
            print(f"       值：{status} ({args.value})")
            print()

            if client.write_single_coil(args.address, bool(args.value)):
                print("[成功] 写入成功")
            else:
                print("[失败] 写入失败")

        # ---- 写入多个线圈 ----
        elif args.command == 'write-coils':
            print(f"[操作] 写入多个线圈")
            print(f"       起始地址：{args.address}")
            print(f"       数量：{len(args.values)}")
            print(f"       值：{args.values}")
            print()

            coil_values = [bool(v) for v in args.values]
            if client.write_multiple_coils(args.address, coil_values):
                print("[成功] 写入成功")
            else:
                print("[失败] 写入失败")

        # ---- 设备信息探测 ----
        elif args.command == 'identify':
            print("[操作] 设备信息探测")
            print()

            # 方法一：Report Slave ID (功能码 0x11)
            print("─" * 50)
            print("方法 1：Report Slave ID (功能码 0x11)")
            print("─" * 50)
            slave_info = client.report_slave_id()
            if slave_info:
                print(f"  从站 ID：{slave_info['slave_id']}")
                print(f"  运行状态：{slave_info['run_status']}")
                print(f"  附加数据（HEX）：{slave_info['additional_data']}")
                print(f"  附加数据（文本）：{slave_info['additional_text']}")
            else:
                print("  未获取到信息（设备可能不支持此功能）")

            print()

            # 方法二：Diagnostic 回环测试 (功能码 0x08, 子功能 0x0000)
            print("─" * 50)
            print("方法 2：Diagnostic 回环测试 (功能码 0x08)")
            print("─" * 50)
            test_data = struct.pack('>H', 0x1234)
            diag_result = client.diagnostic(0x0000, test_data)
            if diag_result:
                print(f"  回环测试：成功")
                print(f"  发送数据：{test_data.hex()}")
                print(f"  返回数据：{diag_result.hex()}")
            else:
                print("  回环测试失败")

            print()

            # 方法三：Read Device Identification (功能码 0x2B)
            print("─" * 50)
            print("方法 3：Read Device Identification (功能码 0x2B)")
            print("─" * 50)
            dev_info = client.read_device_identification()
            if dev_info:
                print(f"  符合级别：{dev_info['conformity_level']}")
                print(f"  对象数量：{dev_info['num_objects']}")
                print()
                for obj_name, obj_value in dev_info['objects'].items():
                    print(f"  {obj_name}：{obj_value}")
            else:
                print("  未获取到信息（设备可能不支持此功能）")

            print()
            print("─" * 50)

    finally:
        client.close()
        print()
        print("[信息] 连接已关闭")


# ============================================================================
#  程序入口
# ============================================================================

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[信息] 用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n[错误] 程序异常：{e}")
        sys.exit(1)
