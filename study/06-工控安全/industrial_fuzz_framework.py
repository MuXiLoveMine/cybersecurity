#!/usr/bin/env python3
"""
工业协议模糊测试框架
====================

支持Modbus/S7/Profinet/CAN协议的变异型和生成型模糊测试框架。

功能:
1. 多协议支持 (Modbus TCP, S7Comm, Profinet, CAN)
2. 基于变异的模糊测试 (对正常报文进行随机修改)
3. 基于生成的模糊测试 (根据协议规范从零构造报文)
4. 崩溃检测与恢复
5. 覆盖率追踪
6. 测试结果报告生成

作者: ICS Security Researcher
版本: 1.0.0
"""

import socket
import struct
import random
import time
import json
import os
import sys
import logging
import hashlib
import traceback
from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from enum import IntEnum
from collections import defaultdict

# ============================================================
# 日志配置
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('fuzz_framework.log', encoding='utf-8'),
    ]
)
logger = logging.getLogger('FuzzFramework')

# ============================================================
# 常量定义
# ============================================================

class ProtocolType(IntEnum):
    """支持的协议类型"""
    MODBUS_TCP = 1
    S7COMM = 2
    PROFINE = 3
    CAN = 4

class FuzzMethod(IntEnum):
    """模糊测试方法"""
    MUTATION = 1      # 基于变异
    GENERATION = 2    # 基于生成
    HYBRID = 3        # 混合

class TestResult(IntEnum):
    """测试结果"""
    NORMAL = 0        # 正常响应
    EXCEPTION = 1     # 异常响应
    TIMEOUT = 2       # 超时 (可能崩溃)
    REFUSED = 3       # 连接拒绝
    CRASH = 4         # 确认崩溃
    ERROR = 5         # 其他错误

# ============================================================
# 数据结构
# ============================================================

@dataclass
class FuzzTestcase:
    """模糊测试用例"""
    testcase_id: int
    protocol: ProtocolType
    method: FuzzMethod
    description: str
    raw_data: bytes
    timestamp: str = ''
    result: Optional[TestResult] = None
    response: bytes = b''
    response_time: float = 0.0
    is_crash: bool = False
    is_interesting: bool = False
    hash: str = ''
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.hash:
            self.hash = hashlib.md5(self.raw_data).hexdigest()[:16]

@dataclass
class FuzzStats:
    """模糊测试统计"""
    total_tests: int = 0
    normal_responses: int = 0
    exception_responses: int = 0
    timeouts: int = 0
    crashes: int = 0
    errors: int = 0
    unique_crashes: int = 0
    interesting_findings: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    
    def coverage_percent(self):
        """计算测试覆盖率"""
        if self.total_tests == 0:
            return 0.0
        return (self.normal_responses + self.exception_responses) / self.total_tests * 100

# ============================================================
# 变异策略
# ============================================================

class MutationStrategy:
    """报文变异策略"""
    
    @staticmethod
    def bit_flip(data: bytes) -> bytes:
        """位翻转变异"""
        if not data:
            return data
        result = bytearray(data)
        byte_idx = random.randint(0, len(result) - 1)
        bit_idx = random.randint(0, 7)
        result[byte_idx] ^= (1 << bit_idx)
        return bytes(result)
    
    @staticmethod
    def byte_flip(data: bytes) -> bytes:
        """字节翻转变异"""
        if not data:
            return data
        result = bytearray(data)
        idx = random.randint(0, len(result) - 1)
        result[idx] ^= 0xFF
        return bytes(result)
    
    @staticmethod
    def byte_random(data: bytes) -> bytes:
        """随机字节替换"""
        if not data:
            return data
        result = bytearray(data)
        num_changes = random.randint(1, max(1, len(result) // 10))
        for _ in range(num_changes):
            idx = random.randint(0, len(result) - 1)
            result[idx] = random.randint(0, 255)
        return bytes(result)
    
    @staticmethod
    def insert_bytes(data: bytes) -> bytes:
        """插入随机字节"""
        if not data:
            return data
        position = random.randint(0, len(data))
        insert_len = random.randint(1, 100)
        insert_data = bytes(random.randint(0, 255) for _ in range(insert_len))
        return data[:position] + insert_data + data[position:]
    
    @staticmethod
    def delete_bytes(data: bytes) -> bytes:
        """删除字节"""
        if len(data) < 2:
            return data
        start = random.randint(0, len(data) - 1)
        delete_len = random.randint(1, min(10, len(data) - start))
        return data[:start] + data[start + delete_len:]
    
    @staticmethod
    def extend_data(data: bytes) -> bytes:
        """扩展数据到超大长度"""
        extensions = [100, 500, 1000, 5000, 10000, 50000]
        ext_len = random.choice(extensions)
        ext_data = bytes(random.randint(0, 255) for _ in range(ext_len))
        return data + ext_data
    
    @staticmethod
    def boundary_values(data: bytes) -> bytes:
        """边界值替换"""
        if not data:
            return data
        result = bytearray(data)
        boundary_values = [0x00, 0x01, 0x7F, 0x80, 0xFE, 0xFF]
        idx = random.randint(0, len(result) - 1)
        result[idx] = random.choice(boundary_values)
        return bytes(result)
    
    @staticmethod
    def magic_values(data: bytes) -> bytes:
        """魔数替换"""
        magic_bytes = [
            b'\x00\x00\x00\x00',
            b'\xFF\xFF\xFF\xFF',
            b'\x7F\xFF\xFF\xFF',
            b'\x80\x00\x00\x00',
            b'\xDE\xAD\xBE\xEF',
            b'\xCA\xFE\xBA\xBE',
            b'\xFE\xED\xFA\xCE',
            b'\x41\x41\x41\x41',
        ]
        if len(data) < 4:
            return data
        magic = random.choice(magic_bytes)
        position = random.randint(0, len(data) - 4)
        return data[:position] + magic + data[position + 4:]
    
    @staticmethod
    def truncate(data: bytes) -> bytes:
        """截断报文"""
        if len(data) < 2:
            return data
        cut_len = random.randint(1, len(data) - 1)
        return data[:cut_len]
    
    @staticmethod
    def duplicate(data: bytes) -> bytes:
        """复制部分数据"""
        if not data:
            return data
        start = random.randint(0, max(0, len(data) - 1))
        end = random.randint(start + 1, len(data))
        segment = data[start:end]
        insert_pos = random.randint(0, len(data))
        return data[:insert_pos] + segment + data[insert_pos:]
    
    @staticmethod
    def apply_random_mutation(data: bytes) -> bytes:
        """随机应用一种变异策略"""
        mutations = [
            MutationStrategy.bit_flip,
            MutationStrategy.byte_flip,
            MutationStrategy.byte_random,
            MutationStrategy.insert_bytes,
            MutationStrategy.delete_bytes,
            MutationStrategy.boundary_values,
            MutationStrategy.magic_values,
            MutationStrategy.truncate,
            MutationStrategy.duplicate,
        ]
        mutation = random.choice(mutations)
        return mutation(data)

# ============================================================
# 协议模板基类
# ============================================================

class ProtocolTemplate(ABC):
    """协议模板基类"""
    
    def __init__(self):
        self.protocol_type = ProtocolType.MODBUS_TCP
        self.default_port = 0
    
    @abstractmethod
    def generate_valid_packet(self) -> bytes:
        """生成一个有效的协议报文"""
        pass
    
    @abstractmethod
    def get_protocol_fields(self) -> List[Dict]:
        """获取协议字段定义"""
        pass
    
    @abstractmethod
    def parse_response(self, response: bytes) -> dict:
        """解析响应"""
        pass
    
    def generate_fuzzed_packet(self, method: FuzzMethod = FuzzMethod.MUTATION) -> bytes:
        """生成模糊测试报文"""
        if method == FuzzMethod.MUTATION:
            base_packet = self.generate_valid_packet()
            return MutationStrategy.apply_random_mutation(base_packet)
        elif method == FuzzMethod.GENERATION:
            return self._generate_from_spec()
        else:
            if random.random() < 0.5:
                base_packet = self.generate_valid_packet()
                return MutationStrategy.apply_random_mutation(base_packet)
            else:
                return self._generate_from_spec()
    
    def _generate_from_spec(self) -> bytes:
        """根据协议规范生成报文"""
        return self.generate_valid_packet()

# ============================================================
# Modbus TCP协议模板
# ============================================================

class ModbusTcpTemplate(ProtocolTemplate):
    """Modbus TCP协议模板"""
    
    def __init__(self):
        super().__init__()
        self.protocol_type = ProtocolType.MODBUS_TCP
        self.default_port = 502
        self.transaction_id = 0
        self.unit_id = 1
    
    def generate_valid_packet(self) -> bytes:
        """生成有效的Modbus TCP报文"""
        self.transaction_id += 1
        
        func_code = random.choice([0x01, 0x02, 0x03, 0x04])
        start_addr = random.randint(0, 1000)
        quantity = random.randint(1, 100)
        
        data = struct.pack('>HH', start_addr, quantity)
        
        mbap_header = struct.pack('>HHHB',
            self.transaction_id,
            0x0000,  # 协议ID
            len(data) + 2,
            self.unit_id
        )
        
        return mbap_header + bytes([func_code]) + data
    
    def get_protocol_fields(self) -> List[Dict]:
        return [
            {'name': 'transaction_id', 'offset': 0, 'size': 2, 'type': 'uint16'},
            {'name': 'protocol_id', 'offset': 2, 'size': 2, 'type': 'uint16'},
            {'name': 'length', 'offset': 4, 'size': 2, 'type': 'uint16'},
            {'name': 'unit_id', 'offset': 6, 'size': 1, 'type': 'uint8'},
            {'name': 'function_code', 'offset': 7, 'size': 1, 'type': 'uint8'},
            {'name': 'data', 'offset': 8, 'size': -1, 'type': 'bytes'},
        ]
    
    def parse_response(self, response: bytes) -> dict:
        if len(response) < 8:
            return {'valid': False, 'reason': '响应过短'}
        
        trans_id = struct.unpack('>H', response[0:2])[0]
        proto_id = struct.unpack('>H', response[2:4])[0]
        length = struct.unpack('>H', response[4:6])[0]
        unit_id = response[6]
        func_code = response[7]
        
        is_exception = bool(func_code & 0x80)
        
        return {
            'valid': True,
            'transaction_id': trans_id,
            'protocol_id': proto_id,
            'length': length,
            'unit_id': unit_id,
            'function_code': func_code,
            'is_exception': is_exception,
            'exception_code': response[8] if is_exception and len(response) > 8 else None,
        }
    
    def _generate_from_spec(self) -> bytes:
        """根据规范生成测试报文"""
        test_type = random.choice([
            'all_func_codes', 'boundary_addr', 'large_data',
            'invalid_length', 'all_units', 'special_values'
        ])
        
        if test_type == 'all_func_codes':
            return self._gen_all_func_codes()
        elif test_type == 'boundary_addr':
            return self._gen_boundary_addr()
        elif test_type == 'large_data':
            return self._gen_large_data()
        elif test_type == 'invalid_length':
            return self._gen_invalid_length()
        elif test_type == 'all_units':
            return self._gen_all_units()
        else:
            return self._gen_special_values()
    
    def _gen_all_func_codes(self):
        """测试所有功能码"""
        self.transaction_id += 1
        func_code = random.randint(0, 255)
        data = struct.pack('>HH', 0, 1)
        header = struct.pack('>HHHB', self.transaction_id, 0, len(data) + 2, 1)
        return header + bytes([func_code]) + data
    
    def _gen_boundary_addr(self):
        """边界地址测试"""
        self.transaction_id += 1
        addresses = [0, 1, 0x7FFF, 0x8000, 0xFFFE, 0xFFFF]
        addr = random.choice(addresses)
        data = struct.pack('>HH', addr, 1)
        header = struct.pack('>HHHB', self.transaction_id, 0, len(data) + 2, 1)
        return header + bytes([0x03]) + data
    
    def _gen_large_data(self):
        """大数据量测试"""
        self.transaction_id += 1
        data_len = random.choice([100, 500, 1000, 5000, 10000])
        data = bytes(random.randint(0, 255) for _ in range(data_len))
        header = struct.pack('>HHHB', self.transaction_id, 0, len(data) + 2, 1)
        return header + bytes([0x10]) + data
    
    def _gen_invalid_length(self):
        """无效长度字段"""
        self.transaction_id += 1
        data = struct.pack('>HH', 0, 1)
        length = random.choice([0, 1, 255, 0xFFFF])
        header = struct.pack('>HHHB', self.transaction_id, 0, length, 1)
        return header + bytes([0x03]) + data
    
    def _gen_all_units(self):
        """所有单元ID"""
        self.transaction_id += 1
        unit = random.randint(0, 255)
        data = struct.pack('>HH', 0, 1)
        header = struct.pack('>HHHB', self.transaction_id, 0, len(data) + 2, unit)
        return header + bytes([0x03]) + data
    
    def _gen_special_values(self):
        """特殊值"""
        self.transaction_id += 1
        special_data = [
            b'\x00' * 100,
            b'\xFF' * 100,
            b'\x7F' * 100,
            b'\x80' * 100,
            b'\xDE\xAD\xBE\xEF' * 25,
            b'\x41' * 1000,
        ]
        data = random.choice(special_data)
        header = struct.pack('>HHHB', self.transaction_id, 0, len(data) + 2, 1)
        return header + bytes([0x03]) + data

# ============================================================
# S7Comm协议模板
# ============================================================

class S7CommTemplate(ProtocolTemplate):
    """S7Comm协议模板"""
    
    def __init__(self):
        super().__init__()
        self.protocol_type = ProtocolType.S7COMM
        self.default_port = 102
        self.pdu_ref = 0
    
    def generate_valid_packet(self) -> bytes:
        """生成有效的S7Comm报文"""
        self.pdu_ref += 1
        
        # TPKT + COTP数据传输
        tpkt_cotp = struct.pack('>BBH', 3, 0, 0x1F) + bytes([0x02, 0xF0, 0x80])
        
        # S7头
        s7_header = struct.pack('>BBHHHH',
            0x32, 0x01, 0x0000, self.pdu_ref, 0x000E, 0x0000)
        
        # 参数: 读变量, 1个Item
        param = bytes([0x04, 0x01])
        
        # Item: 读取MW0
        item = struct.pack('>BBBB',
            0x12, 0x0A, 0x10, 0x04)  # 变量, 长度10, 语法, WORD
        item += struct.pack('>H', 0)  # DB号
        item += bytes([0x83])  # M区
        item += struct.pack('>I', 0)[1:]  # 地址
        item += struct.pack('>H', 1)  # 数量
        
        # 更新TPKT长度
        total_len = 7 + 10 + len(param) + len(item)
        tpkt_cotp = struct.pack('>BBH', 3, 0, total_len) + bytes([0x02, 0xF0, 0x80])
        
        return tpkt_cotp + s7_header + param + item[2:]
    
    def get_protocol_fields(self) -> List[Dict]:
        return [
            {'name': 'tpkt_version', 'offset': 0, 'size': 1, 'type': 'uint8'},
            {'name': 'tpkt_reserved', 'offset': 1, 'size': 1, 'type': 'uint8'},
            {'name': 'tpkt_length', 'offset': 2, 'size': 2, 'type': 'uint16'},
            {'name': 'cotp_length', 'offset': 4, 'size': 1, 'type': 'uint8'},
            {'name': 'cotp_type', 'offset': 5, 'size': 1, 'type': 'uint8'},
            {'name': 's7_protocol_id', 'offset': 7, 'size': 1, 'type': 'uint8'},
            {'name': 's7_pdu_type', 'offset': 8, 'size': 1, 'type': 'uint8'},
            {'name': 's7_reserved', 'offset': 9, 'size': 2, 'type': 'uint16'},
            {'name': 's7_pdu_ref', 'offset': 11, 'size': 2, 'type': 'uint16'},
            {'name': 's7_param_len', 'offset': 13, 'size': 2, 'type': 'uint16'},
            {'name': 's7_data_len', 'offset': 15, 'size': 2, 'type': 'uint16'},
        ]
    
    def parse_response(self, response: bytes) -> dict:
        if len(response) < 12:
            return {'valid': False, 'reason': '响应过短'}
        
        if response[0] != 0x03:
            return {'valid': False, 'reason': '非TPKT'}
        
        if response[7] != 0x32:
            return {'valid': False, 'reason': '非S7协议'}
        
        return {
            'valid': True,
            'tpkt_length': struct.unpack('>H', response[2:4])[0],
            's7_protocol_id': response[7],
            's7_pdu_type': response[8],
            's7_pdu_ref': struct.unpack('>H', response[10:12])[0],
            'param_length': struct.unpack('>H', response[12:14])[0] if len(response) > 13 else 0,
            'data_length': struct.unpack('>H', response[14:16])[0] if len(response) > 15 else 0,
        }
    
    def _generate_from_spec(self) -> bytes:
        """根据规范生成测试报文"""
        test_type = random.choice([
            'all_pdu_types', 'all_areas', 'cpu_control',
            'password', 'large_param', 'zero_length'
        ])
        
        self.pdu_ref += 1
        
        if test_type == 'all_pdu_types':
            return self._gen_all_pdu_types()
        elif test_type == 'all_areas':
            return self._gen_all_areas()
        elif test_type == 'cpu_control':
            return self._gen_cpu_control()
        elif test_type == 'password':
            return self._gen_password_attempt()
        elif test_type == 'large_param':
            return self._gen_large_param()
        else:
            return self._gen_zero_length()
    
    def _gen_all_pdu_types(self):
        """测试所有PDU类型"""
        pdu_type = random.randint(0, 255)
        s7_header = struct.pack('>BBHHHH', 0x32, pdu_type, 0, self.pdu_ref, 4, 0)
        param = bytes([0x04, 0x01, 0x12, 0x0A])
        tpkt_cotp = struct.pack('>BBH', 3, 0, 7 + 10 + len(param)) + bytes([0x02, 0xF0, 0x80])
        return tpkt_cotp + s7_header + param
    
    def _gen_all_areas(self):
        """测试所有区域"""
        area = random.choice([0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89])
        item = struct.pack('>BBBB', 0x12, 0x0A, 0x10, 0x04)
        item += struct.pack('>H', 0) + bytes([area])
        item += struct.pack('>I', 0)[1:] + struct.pack('>H', 1)
        
        param = bytes([0x04, 0x01]) + item
        s7_header = struct.pack('>BBHHHH', 0x32, 0x01, 0, self.pdu_ref, len(param), 0)
        tpkt_cotp = struct.pack('>BBH', 3, 0, 7 + 10 + len(param)) + bytes([0x02, 0xF0, 0x80])
        return tpkt_cotp + s7_header + param
    
    def _gen_cpu_control(self):
        """CPU控制"""
        sub_func = random.choice([0x00, 0x01, 0x02, 0x04])
        param = bytes([0x28, sub_func, 0x00, 0x00])
        s7_header = struct.pack('>BBHHHH', 0x32, 0x01, 0, self.pdu_ref, len(param), 0)
        tpkt_cotp = struct.pack('>BBH', 3, 0, 7 + 10 + len(param)) + bytes([0x02, 0xF0, 0x80])
        return tpkt_cotp + s7_header + param
    
    def _gen_password_attempt(self):
        """密码验证"""
        pwd = bytes(random.randint(0, 255) for _ in range(8))
        param = bytes([0x28, 0x02]) + pwd
        s7_header = struct.pack('>BBHHHH', 0x32, 0x28, 0, self.pdu_ref, len(param), 0)
        tpkt_cotp = struct.pack('>BBH', 3, 0, 7 + 10 + len(param)) + bytes([0x02, 0xF0, 0x80])
        return tpkt_cotp + s7_header + param
    
    def _gen_large_param(self):
        """大参数"""
        param_len = random.choice([100, 500, 1000, 5000])
        param = bytes(random.randint(0, 255) for _ in range(param_len))
        s7_header = struct.pack('>BBHHHH', 0x32, 0x01, 0, self.pdu_ref, len(param), 0)
        tpkt_cotp = struct.pack('>BBH', 3, 0, 7 + 10 + len(param)) + bytes([0x02, 0xF0, 0x80])
        return tpkt_cotp + s7_header + param
    
    def _gen_zero_length(self):
        """零长度"""
        s7_header = struct.pack('>BBHHHH', 0x32, 0x01, 0, self.pdu_ref, 0, 0)
        tpkt_cotp = struct.pack('>BBH', 3, 0, 7 + 10) + bytes([0x02, 0xF0, 0x80])
        return tpkt_cotp + s7_header

# ============================================================
# Profinet协议模板
# ============================================================

class ProfinetTemplate(ProtocolTemplate):
    """Profinet协议模板"""
    
    def __init__(self):
        super().__init__()
        self.protocol_type = ProtocolType.PROFINE
        self.default_port = 0x8892  # Profinet RT 使用以太网类型而非端口
    
    def generate_valid_packet(self) -> bytes:
        """生成有效的Profinet报文"""
        # Profinet DCP (Discovery and Configuration Protocol)
        # 以太网帧头
        dst_mac = b'\x01\x0e\xcf\x00\x00\x00'  # Profinet多播MAC
        src_mac = b'\x00\x11\x22\x33\x44\x55'
        eth_type = struct.pack('>H', 0x8892)  # Profinet
        
        # Profinet DCP帧
        frame_id = struct.pack('>H', 0xFEFE)  # DCP
        service_id = 0x05  # Identify
        service_type = 0x00  # Request
        
        # DCP数据
        dcp_data = struct.pack('>BBBBBB',
            service_id, service_type,
            0x00, 0x00,  # XID
            0x00, 0x01,  # Response延迟因子
        )
        dcp_data += struct.pack('>H', 0x0004)  # DCP数据长度
        
        # 选项: 设备选项
        dcp_data += bytes([0x05, 0x00, 0x00, 0x04])  # 设备选项, 子选项=设备ID
        
        return dst_mac + src_mac + eth_type + frame_id + dcp_data
    
    def get_protocol_fields(self) -> List[Dict]:
        return [
            {'name': 'dst_mac', 'offset': 0, 'size': 6, 'type': 'mac'},
            {'name': 'src_mac', 'offset': 6, 'size': 6, 'type': 'mac'},
            {'name': 'eth_type', 'offset': 12, 'size': 2, 'type': 'uint16'},
            {'name': 'frame_id', 'offset': 14, 'size': 2, 'type': 'uint16'},
            {'name': 'service_id', 'offset': 16, 'size': 1, 'type': 'uint8'},
            {'name': 'service_type', 'offset': 17, 'size': 1, 'type': 'uint8'},
        ]
    
    def parse_response(self, response: bytes) -> dict:
        return {'valid': len(response) > 14, 'size': len(response)}
    
    def _generate_from_spec(self) -> bytes:
        """生成Profinet测试报文"""
        test_type = random.choice(['dcp_identify', 'dcp_set', 'mrp', 'ptcp'])
        
        dst_mac = b'\x01\x0e\xcf\x00\x00\x00'
        src_mac = bytes(random.randint(0, 255) for _ in range(6))
        eth_type = struct.pack('>H', 0x8892)
        
        if test_type == 'dcp_identify':
            frame_id = struct.pack('>H', 0xFEFE)
            svc = bytes([random.randint(0, 255), 0x00, 0x00, 0x00, 0x00, 0x01])
            svc += struct.pack('>H', random.randint(0, 0xFFFF))
            return dst_mac + src_mac + eth_type + frame_id + svc
        
        elif test_type == 'dcp_set':
            frame_id = struct.pack('>H', 0xFEFE)
            svc = bytes([0x04, 0x00, 0x00, 0x00, 0x00, 0x01])
            svc += struct.pack('>H', 100)
            svc += bytes(random.randint(0, 255) for _ in range(100))
            return dst_mac + src_mac + eth_type + frame_id + svc
        
        elif test_type == 'mrp':
            dst_mac_mrp = b'\x01\x15\x4e\x00\x00\x00'
            frame_id = struct.pack('>H', 0xFF00)
            return dst_mac_mrp + src_mac + eth_type + frame_id
        
        else:  # ptcp
            frame_id = struct.pack('>H', 0x00DC)
            return dst_mac + src_mac + eth_type + frame_id

# ============================================================
# CAN协议模板
# ============================================================

class CANTemplate(ProtocolTemplate):
    """CAN总线协议模板"""
    
    def __init__(self):
        super().__init__()
        self.protocol_type = ProtocolType.CAN
        self.default_port = 0
    
    def generate_valid_packet(self) -> bytes:
        """生成有效的CAN帧"""
        # 标准CAN帧 (11位ID)
        can_id = random.randint(0, 0x7FF)
        dlc = random.randint(0, 8)
        data = bytes(random.randint(0, 255) for _ in range(dlc))
        
        # CAN帧格式 (简化)
        frame = struct.pack('>HB', can_id, dlc) + data
        # CAN ID (11位), DLC, 数据
        
        return frame
    
    def get_protocol_fields(self) -> List[Dict]:
        return [
            {'name': 'can_id', 'offset': 0, 'size': 2, 'type': 'uint16'},
            {'name': 'dlc', 'offset': 2, 'size': 1, 'type': 'uint8'},
            {'name': 'data', 'offset': 3, 'size': 8, 'type': 'bytes'},
        ]
    
    def parse_response(self, response: bytes) -> dict:
        return {'valid': True, 'size': len(response)}
    
    def _generate_from_spec(self) -> bytes:
        """生成CAN测试帧"""
        test_type = random.choice([
            'standard_id', 'extended_id', 'remote_frame',
            'overload_dlc', 'zero_dlc', 'max_data'
        ])
        
        if test_type == 'standard_id':
            can_id = random.randint(0, 0x7FF)
            dlc = random.randint(0, 8)
        elif test_type == 'extended_id':
            can_id = random.randint(0x800, 0x1FFFFFFF)
            dlc = random.randint(0, 8)
        elif test_type == 'remote_frame':
            can_id = random.randint(0, 0x7FF) | 0x100  # RTR位
            dlc = random.randint(0, 8)
        elif test_type == 'overload_dlc':
            can_id = random.randint(0, 0x7FF)
            dlc = random.randint(9, 255)  # 超过8字节
        elif test_type == 'zero_dlc':
            can_id = random.randint(0, 0x7FF)
            dlc = 0
        else:  # max_data
            can_id = random.randint(0, 0x7FF)
            dlc = 8
        
        data = bytes(random.randint(0, 255) for _ in range(min(dlc, 64)))
        return struct.pack('>HB', can_id, dlc) + data

# ============================================================
# 目标管理器
# ============================================================

class FuzzTarget:
    """模糊测试目标"""
    
    def __init__(self, ip: str, port: int, protocol: ProtocolType):
        self.ip = ip
        self.port = port
        self.protocol = protocol
        self.sock: Optional[socket.socket] = None
        self.is_alive = True
        self.crash_count = 0
        self.last_response_time = 0.0
    
    def connect(self) -> bool:
        """连接目标"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)
            self.sock.connect((self.ip, self.port))
            self.is_alive = True
            return True
        except Exception as e:
            logger.debug(f"连接失败: {e}")
            self.is_alive = False
            return False
    
    def send_and_recv(self, data: bytes, timeout: float = 3.0) -> tuple:
        """发送数据并接收响应
        
        返回: (TestResult, response_bytes, response_time)
        """
        if not self.sock and not self.connect():
            return (TestResult.REFUSED, b'', 0.0)
        
        start_time = time.time()
        
        try:
            self.sock.settimeout(timeout)
            self.sock.send(data)
            response = self.sock.recv(4096)
            elapsed = time.time() - start_time
            self.last_response_time = elapsed
            return (TestResult.NORMAL, response, elapsed)
        except socket.timeout:
            elapsed = time.time() - start_time
            self.last_response_time = elapsed
            return (TestResult.TIMEOUT, b'', elapsed)
        except ConnectionResetError:
            elapsed = time.time() - start_time
            self.is_alive = False
            self.crash_count += 1
            return (TestResult.CRASH, b'', elapsed)
        except Exception as e:
            elapsed = time.time() - start_time
            return (TestResult.ERROR, b'', elapsed)
    
    def check_alive(self, retries: int = 3) -> bool:
        """检查目标是否存活"""
        for i in range(retries):
            try:
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_sock.settimeout(3)
                test_sock.connect((self.ip, self.port))
                test_sock.close()
                self.is_alive = True
                return True
            except:
                time.sleep(2)
        
        self.is_alive = False
        return False
    
    def disconnect(self):
        """断开连接"""
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None

# ============================================================
# 模糊测试引擎
# ============================================================

class FuzzEngine:
    """模糊测试引擎"""
    
    def __init__(self, target: FuzzTarget, template: ProtocolTemplate,
                 method: FuzzMethod = FuzzMethod.MUTATION,
                 max_tests: int = 10000,
                 timeout: float = 3.0,
                 delay: float = 0.1):
        self.target = target
        self.template = template
        self.method = method
        self.max_tests = max_tests
        self.timeout = timeout
        self.delay = delay
        
        self.stats = FuzzStats()
        self.testcases: List[FuzzTestcase] = []
        self.crash_hashes: set = set()
        self.interesting_hashes: set = set()
        self.testcase_id = 0
        
        self.crash_file = 'fuzz_crashes.txt'
        self.report_file = 'fuzz_report.txt'
    
    def run(self):
        """运行模糊测试"""
        logger.info("=" * 60)
        logger.info("工业协议模糊测试框架")
        logger.info("=" * 60)
        logger.info(f"目标: {self.target.ip}:{self.target.port}")
        logger.info(f"协议: {self.template.protocol_type.name}")
        logger.info(f"方法: {self.method.name}")
        logger.info(f"最大测试数: {self.max_tests}")
        logger.info(f"超时: {self.timeout}秒")
        logger.info(f"延迟: {self.delay}秒")
        logger.info("=" * 60)
        
        self.stats.start_time = time.time()
        
        try:
            for i in range(self.max_tests):
                if not self.target.is_alive and not self.target.check_alive():
                    logger.error("目标不可用, 等待恢复...")
                    time.sleep(10)
                    if not self.target.check_alive():
                        logger.error("目标无法恢复, 停止测试")
                        break
                    logger.info("目标已恢复, 继续测试")
                
                self._run_single_test()
                
                if (i + 1) % 100 == 0:
                    self._print_progress()
                
                time.sleep(self.delay)
        
        except KeyboardInterrupt:
            logger.info("用户中断测试")
        
        self.stats.end_time = time.time()
        self.generate_report()
    
    def _run_single_test(self):
        """运行单个测试用例"""
        self.testcase_id += 1
        self.stats.total_tests += 1
        
        # 生成测试数据
        fuzzed_data = self.template.generate_fuzzed_packet(self.method)
        
        testcase = FuzzTestcase(
            testcase_id=self.testcase_id,
            protocol=self.template.protocol_type,
            method=self.method,
            description=f"Test #{self.testcase_id}",
            raw_data=fuzzed_data,
        )
        
        # 发送并接收
        result, response, resp_time = self.target.send_and_recv(
            fuzzed_data, self.timeout
        )
        
        testcase.result = result
        testcase.response = response
        testcase.response_time = resp_time
        
        # 更新统计
        if result == TestResult.NORMAL:
            # 检查是否为异常响应
            parsed = self.template.parse_response(response)
            if parsed.get('is_exception') or parsed.get('valid') is False:
                testcase.result = TestResult.EXCEPTION
                self.stats.exception_responses += 1
                testcase.is_interesting = True
            else:
                self.stats.normal_responses += 1
        elif result == TestResult.TIMEOUT:
            self.stats.timeouts += 1
            testcase.is_crash = True
            testcase.is_interesting = True
            
            # 检查是否崩溃
            time.sleep(2)
            if not self.target.check_alive():
                testcase.result = TestResult.CRASH
                self.stats.crashes += 1
                
                if testcase.hash not in self.crash_hashes:
                    self.crash_hashes.add(testcase.hash)
                    self.stats.unique_crashes += 1
                    self._log_crash(testcase)
        elif result == TestResult.CRASH:
            self.stats.crashes += 1
            testcase.is_crash = True
            testcase.is_interesting = True
            
            if testcase.hash not in self.crash_hashes:
                self.crash_hashes.add(testcase.hash)
                self.stats.unique_crashes += 1
                self._log_crash(testcase)
        else:
            self.stats.errors += 1
        
        if testcase.is_interesting:
            self.stats.interesting_findings += 1
            self._log_interesting(testcase)
        
        self.testcases.append(testcase)
    
    def _log_crash(self, testcase: FuzzTestcase):
        """记录崩溃"""
        logger.critical(f"[CRASH] 测试 #{testcase.testcase_id} 导致目标崩溃!")
        logger.critical(f"  数据: {testcase.raw_data.hex()[:200]}")
        logger.critical(f"  哈希: {testcase.hash}")
        
        with open(self.crash_file, 'a', encoding='utf-8') as f:
            f.write(f"{'='*60}\n")
            f.write(f"崩溃 #{testcase.testcase_id}\n")
            f.write(f"时间: {testcase.timestamp}\n")
            f.write(f"协议: {testcase.protocol.name}\n")
            f.write(f"方法: {testcase.method.name}\n")
            f.write(f"哈希: {testcase.hash}\n")
            f.write(f"数据 ({len(testcase.raw_data)} bytes):\n")
            f.write(f"  HEX: {testcase.raw_data.hex()}\n")
            f.write(f"  ASCII: {testcase.raw_data.decode('ascii', errors='replace')}\n")
            f.write(f"响应时间: {testcase.response_time:.3f}秒\n")
            f.write(f"{'='*60}\n\n")
    
    def _log_interesting(self, testcase: FuzzTestcase):
        """记录有趣的发现"""
        if testcase.result == TestResult.EXCEPTION:
            logger.warning(f"[EXCEPTION] 测试 #{testcase.testcase_id} 返回异常响应")
            logger.warning(f"  数据: {testcase.raw_data.hex()[:100]}")
            logger.warning(f"  响应: {testcase.response.hex()[:100]}")
    
    def _print_progress(self):
        """打印进度"""
        elapsed = time.time() - self.stats.start_time
        tests = self.stats.total_tests
        rate = tests / elapsed if elapsed > 0 else 0
        
        logger.info(
            f"进度: {tests}/{self.max_tests} "
            f"({tests/self.max_tests*100:.1f}%) | "
            f"正常: {self.stats.normal_responses} | "
            f"异常: {self.stats.exception_responses} | "
            f"超时: {self.stats.timeouts} | "
            f"崩溃: {self.stats.crashes} (唯一: {self.stats.unique_crashes}) | "
            f"速率: {rate:.1f}/秒"
        )
    
    def generate_report(self):
        """生成测试报告"""
        elapsed = self.stats.end_time - self.stats.start_time
        
        with open(self.report_file, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("工业协议模糊测试报告\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"测试配置:\n")
            f.write(f"  目标: {self.target.ip}:{self.target.port}\n")
            f.write(f"  协议: {self.template.protocol_type.name}\n")
            f.write(f"  方法: {self.method.name}\n")
            f.write(f"  最大测试数: {self.max_tests}\n")
            f.write(f"  超时: {self.timeout}秒\n")
            f.write(f"  延迟: {self.delay}秒\n\n")
            
            f.write(f"测试统计:\n")
            f.write(f"  总测试数: {self.stats.total_tests}\n")
            f.write(f"  正常响应: {self.stats.normal_responses}\n")
            f.write(f"  异常响应: {self.stats.exception_responses}\n")
            f.write(f"  超时: {self.stats.timeouts}\n")
            f.write(f"  崩溃: {self.stats.crashes}\n")
            f.write(f"  唯一崩溃: {self.stats.unique_crashes}\n")
            f.write(f"  错误: {self.stats.errors}\n")
            f.write(f"  有趣发现: {self.stats.interesting_findings}\n")
            f.write(f"  覆盖率: {self.stats.coverage_percent():.1f}%\n\n")
            
            f.write(f"时间统计:\n")
            f.write(f"  总耗时: {elapsed:.1f}秒 ({elapsed/3600:.1f}小时)\n")
            rate = self.stats.total_tests / elapsed if elapsed > 0 else 0
            f.write(f"  测试速率: {rate:.1f} 次/秒\n\n")
            
            # 崩溃详情
            crashes = [t for t in self.testcases if t.is_crash]
            if crashes:
                f.write(f"崩溃详情 ({len(crashes)} 个):\n")
                f.write("-" * 70 + "\n")
                for tc in crashes[:50]:
                    f.write(f"\n  崩溃 #{tc.testcase_id}\n")
                    f.write(f"    时间: {tc.timestamp}\n")
                    f.write(f"    响应时间: {tc.response_time:.3f}秒\n")
                    f.write(f"    数据({len(tc.raw_data)} bytes): {tc.raw_data.hex()[:200]}\n")
                    f.write(f"    哈希: {tc.hash}\n")
            
            # 安全建议
            f.write(f"\n{'='*70}\n")
            f.write("安全建议:\n")
            f.write("-" * 70 + "\n")
            
            if self.stats.unique_crashes > 0:
                f.write(f"  [!] 发现 {self.stats.unique_crashes} 个唯一崩溃!\n")
                f.write(f"      建议深入分析崩溃原因, 可能存在安全漏洞\n")
            
            if self.stats.exception_responses > 0:
                f.write(f"  [!] 发现 {self.stats.exception_responses} 个异常响应\n")
                f.write(f"      建议分析异常响应模式\n")
            
            if self.stats.timeouts > 0:
                f.write(f"  [!] 发现 {self.stats.timeouts} 次超时\n")
                f.write(f"      超时可能表示设备处理异常\n")
            
            if self.stats.unique_crashes == 0 and self.stats.exception_responses == 0:
                f.write(f"  [*] 未发现明显安全问题\n")
                f.write(f"      建议增加测试用例数量或调整变异策略\n")
        
        logger.info(f"报告已生成: {self.report_file}")
        logger.info(f"崩溃记录: {self.crash_file}")

# ============================================================
# 工厂函数
# ============================================================

def create_template(protocol: ProtocolType) -> ProtocolTemplate:
    """创建协议模板"""
    templates = {
        ProtocolType.MODBUS_TCP: ModbusTcpTemplate,
        ProtocolType.S7COMM: S7CommTemplate,
        ProtocolType.PROFINE: ProfinetTemplate,
        ProtocolType.CAN: CANTemplate,
    }
    template_class = templates.get(protocol)
    if template_class is None:
        raise ValueError(f"不支持的协议类型: {protocol}")
    return template_class()

# ============================================================
# 主程序
# ============================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='工业协议模糊测试框架 - 支持Modbus/S7/Profinet/CAN协议',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument('target', help='目标IP地址')
    parser.add_argument('-p', '--port', type=int, help='目标端口 (默认使用协议默认端口)')
    parser.add_argument('--protocol', choices=['modbus', 's7', 'profinet', 'can'],
                        default='modbus', help='测试协议 (默认: modbus)')
    parser.add_argument('--method', choices=['mutation', 'generation', 'hybrid'],
                        default='mutation', help='模糊测试方法 (默认: mutation)')
    parser.add_argument('-n', '--max-tests', type=int, default=10000,
                        help='最大测试用例数 (默认: 10000)')
    parser.add_argument('-t', '--timeout', type=float, default=3.0,
                        help='超时时间秒 (默认: 3.0)')
    parser.add_argument('-d', '--delay', type=float, default=0.1,
                        help='测试间隔秒 (默认: 0.1)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='详细输出')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # 协议映射
    protocol_map = {
        'modbus': ProtocolType.MODBUS_TCP,
        's7': ProtocolType.S7COMM,
        'profinet': ProtocolType.PROFINE,
        'can': ProtocolType.CAN,
    }
    method_map = {
        'mutation': FuzzMethod.MUTATION,
        'generation': FuzzMethod.GENERATION,
        'hybrid': FuzzMethod.HYBRID,
    }
    
    protocol = protocol_map[args.protocol]
    method = method_map[args.method]
    
    # 创建模板
    template = create_template(protocol)
    
    # 确定端口
    port = args.port or template.default_port
    
    # 创建目标
    target = FuzzTarget(args.target, port, protocol)
    
    # 创建并运行引擎
    engine = FuzzEngine(
        target=target,
        template=template,
        method=method,
        max_tests=args.max_tests,
        timeout=args.timeout,
        delay=args.delay,
    )
    
    engine.run()

if __name__ == '__main__':
    main()
