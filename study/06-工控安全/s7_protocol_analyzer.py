#!/usr/bin/env python3
"""
S7协议分析器
===========

用于解析S7协议数据包、检测异常行为、记录S7通信会话的综合工具。

功能:
1. S7协议数据包解析 (TPKT/COTP/S7Comm)
2. 异常行为检测 (未授权写入、CPU控制、暴力破解等)
3. 通信会话记录与重建
4. 实时网络流量监控
5. 离线PCAP文件分析
6. 安全告警生成

作者: ICS Security Researcher
版本: 1.0.0
"""

import socket
import struct
import logging
import json
import os
import sys
import time
import argparse
from datetime import datetime
from collections import defaultdict, Counter
from enum import IntEnum
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

# ============================================================
# 日志配置
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('s7_analyzer.log', encoding='utf-8'),
    ]
)
logger = logging.getLogger('S7Analyzer')

# ============================================================
# 常量定义
# ============================================================

class TPKT:
    """TPKT协议常量"""
    VERSION = 0x03
    HEADER_SIZE = 4

class COTP:
    """COTP协议常量"""
    # PDU类型
    CONNECT_REQUEST = 0xE0
    CONNECT_CONFIRM = 0xD0
    DATA_TRANSFER = 0xF0
    DISCONNECT_REQUEST = 0x80
    REJECT = 0x50
    
    # 参数代码
    TPDU_SIZE = 0xC2
    CALLED_TSAP = 0xC0
    CALLING_TSAP = 0xC1
    
    # TPDU大小映射
    TPDU_SIZES = {
        0x0A: 1024,
        0x0B: 2048,
        0x0C: 4096,
        0x0D: 8192,
        0x0E: 16384,
        0x0F: 32768,
    }

class S7Protocol:
    """S7协议常量"""
    PROTOCOL_ID = 0x32
    
    # PDU类型
    PDU_REQUEST = 0x01
    PDU_ACK = 0x02
    PDU_ACK_DATA = 0x03
    PDU_USER_DATA = 0x04
    PDU_DISCARD = 0x05
    PDU_PASSWORD = 0x28
    
    # 功能组
    FUNC_READ_VARIABLES = 0x04
    FUNC_WRITE_VARIABLES = 0x05
    FUNC_CPU_CONTROL = 0x28
    FUNC_PASSWORD = 0x28
    FUNC_COMM_SETUP = 0xF0
    FUNC_PROGRAM_TRANSFER = 0x28
    FUNC_CYCLIC_READ = 0x09
    
    # 区域类型
    AREA_PROCESS_IMAGE_INPUT = 0x81
    AREA_PROCESS_IMAGE_OUTPUT = 0x82
    AREA_FLAGS = 0x83
    AREA_DATA_BLOCKS = 0x84
    AREA_INSTANCE_DB = 0x85
    AREA_COUNTER = 0x86
    AREA_TIMER = 0x87
    AREA_PERIPHERAL_INPUT = 0x88
    AREA_PERIPHERAL_OUTPUT = 0x89
    
    AREA_NAMES = {
        0x81: 'I (过程映像输入)',
        0x82: 'Q (过程映像输出)',
        0x83: 'M (标志位区)',
        0x84: 'DB (数据块)',
        0x85: 'DI (背景数据块)',
        0x86: 'C (计数器)',
        0x87: 'T (定时器)',
        0x88: 'PI (外设输入)',
        0x89: 'PQ (外设输出)',
    }
    
    # 数据传输大小
    TRANSPORT_SIZE = {
        0x01: 'BIT',
        0x02: 'BYTE',
        0x03: 'CHAR',
        0x04: 'WORD',
        0x05: 'INT',
        0x06: 'DWORD',
        0x07: 'DINT',
        0x08: 'REAL',
        0x09: 'DATE',
        0x0A: 'TIME',
        0x0B: 'S5TIME',
        0x0C: 'DATE_AND_TIME',
        0x0E: 'DWORD64',
        0x0F: 'BOOL',
        0x10: 'BYTE_STR',
        0x13: 'LWORD',
        0x14: 'LINT',
        0x15: 'LREAL',
        0x16: 'LTIME',
        0xFF: 'BYTE_STR_VAR',
    }
    
    # CPU控制子功能
    CPU_SUBFUNC_START = 0x00
    CPU_SUBFUNC_STOP = 0x01
    CPU_SUBFUNC_COMPRESS = 0x04
    CPU_SUBFUNC_READ_PROTECTION = 0x02
    
    # 返回码
    RETURN_CODES = {
        0x00: '无错误',
        0x01: '硬件错误',
        0x02: '对象不存在',
        0x03: '对象没有数据',
        0x05: '地址越界',
        0x06: '数据类型不匹配',
        0x07: '数据不匹配',
        0x0A: '对象不存在',
        0xD2: '冲突',
        0xD5: '违反访问权限',
        0xD6: '访问被拒绝',
        0xD7: '区域已存在',
        0xDA: '块不存在',
        0xDC: '块已存在',
        0xFF: '成功',
    }

class AnomalyType:
    """异常类型"""
    UNAUTHORIZED_READ = 'unauthorized_read'
    UNAUTHORIZED_WRITE = 'unauthorized_write'
    CPU_STOP = 'cpu_stop'
    CPU_START = 'cpu_start'
    PASSWORD_BRUTE_FORCE = 'password_brute_force'
    EXCESSIVE_READS = 'excessive_reads'
    EXCESSIVE_WRITES = 'excessive_reads'
    UNAUTHORIZED_ACCESS = 'unauthorized_access'
    ABNORMAL_PACKET = 'abnormal_packet'
    PROTOCOL_DEVIATION = 'protocol_deviation'
    SUSPICIOUS_CONNECTION = 'suspicious_connection'
    DATA_EXFILTRATION = 'data_exfiltration'
    PROGRAM_DOWNLOAD = 'program_download'

# ============================================================
# 数据结构
# ============================================================

@dataclass
class TPKTHeader:
    """TPKT头"""
    version: int
    reserved: int
    length: int
    
    @classmethod
    def parse(cls, data: bytes, offset: int = 0) -> 'TPKTHeader':
        if len(data) - offset < 4:
            raise ValueError("数据不足以解析TPKT头")
        version = data[offset]
        reserved = data[offset + 1]
        length = struct.unpack('>H', data[offset + 2:offset + 4])[0]
        return cls(version, reserved, length)

@dataclass
class COTPHeader:
    """COTP头"""
    length: int
    pdu_type: int
    dest_ref: int = 0
    src_ref: int = 0
    class_field: int = 0
    params: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def parse(cls, data: bytes, offset: int = 0) -> 'COTPHeader':
        if len(data) - offset < 2:
            raise ValueError("数据不足以解析COTP头")
        
        length = data[offset]
        pdu_type = data[offset + 1] & 0xF0
        
        header = cls(length=length, pdu_type=pdu_type)
        
        if pdu_type in (COTP.CONNECT_REQUEST, COTP.CONNECT_CONFIRM):
            # 连接请求/确认
            if len(data) - offset >= 7:
                header.dest_ref = struct.unpack('>H', data[offset + 2:offset + 4])[0]
                header.src_ref = struct.unpack('>H', data[offset + 4:offset + 6])[0]
                header.class_field = data[offset + 6]
                
                # 解析可变参数
                param_offset = offset + 7
                while param_offset < offset + 1 + length:
                    if param_offset + 2 > len(data):
                        break
                    param_code = data[param_offset]
                    param_len = data[param_offset + 1]
                    param_value = data[param_offset + 2:param_offset + 2 + param_len]
                    
                    if param_code == COTP.TPDU_SIZE and param_len == 1:
                        header.params['tpdu_size'] = COTP.TPDU_SIZES.get(
                            param_value[0], param_value[0]
                        )
                    elif param_code == COTP.CALLED_TSAP and param_len == 2:
                        header.params['called_tsap'] = struct.unpack('>H', param_value)[0]
                    elif param_code == COTP.CALLING_TSAP and param_len == 2:
                        header.params['calling_tsap'] = struct.unpack('>H', param_value)[0]
                    
                    param_offset += 2 + param_len
        
        elif pdu_type == COTP.DATA_TRANSFER:
            # 数据传输
            header.length = 2
            if offset + 2 < len(data):
                eot = data[offset + 2] & 0x80
                header.params['eot'] = bool(eot)
        
        return header

@dataclass
class S7Header:
    """S7协议头"""
    protocol_id: int
    pdu_type: int
    reserved: int
    pdu_ref: int
    param_length: int
    data_length: int
    
    @classmethod
    def parse(cls, data: bytes, offset: int = 0) -> 'S7Header':
        if len(data) - offset < 10:
            raise ValueError("数据不足以解析S7头")
        
        return cls(
            protocol_id=data[offset],
            pdu_type=data[offset + 1],
            reserved=struct.unpack('>H', data[offset + 2:offset + 4])[0],
            pdu_ref=struct.unpack('>H', data[offset + 4:offset + 6])[0],
            param_length=struct.unpack('>H', data[offset + 6:offset + 8])[0],
            data_length=struct.unpack('>H', data[offset + 8:offset + 10])[0],
        )

@dataclass
class S7VariableSpec:
    """S7变量规格"""
    item_type: int
    item_length: int
    syntax_id: int
    transport_size: int
    db_number: int
    area_type: int
    address: int
    length: int
    
    @classmethod
    def parse(cls, data: bytes, offset: int = 0) -> 'S7VariableSpec':
        if len(data) - offset < 12:
            raise ValueError("数据不足以解析变量规格")
        
        item_type = data[offset]
        item_length = data[offset + 1]
        syntax_id = data[offset + 2]
        transport_size = data[offset + 3]
        db_number = struct.unpack('>H', data[offset + 4:offset + 6])[0]
        area_type = data[offset + 6]
        address = (data[offset + 7] << 16) | (data[offset + 8] << 8) | data[offset + 9]
        length = struct.unpack('>H', data[offset + 10:offset + 12])[0]
        
        return cls(item_type, item_length, syntax_id, transport_size,
                   db_number, area_type, address, length)
    
    def to_dict(self) -> dict:
        return {
            'area': S7Protocol.AREA_NAMES.get(self.area_type, f'Unknown(0x{self.area_type:02X})'),
            'db_number': self.db_number,
            'address': self.address,
            'length': self.length,
            'transport_size': S7Protocol.TRANSPORT_SIZE.get(
                self.transport_size, f'Unknown(0x{self.transport_size:02X})'
            ),
        }

@dataclass
class S7Packet:
    """完整的S7数据包"""
    timestamp: float
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    tpkt: Optional[TPKTHeader] = None
    cotp: Optional[COTPHeader] = None
    s7_header: Optional[S7Header] = None
    func_group: int = 0
    sub_func: int = 0
    variables: List[S7VariableSpec] = field(default_factory=list)
    data: bytes = b''
    raw_data: bytes = b''
    is_response: bool = False
    return_code: int = 0

@dataclass
class Anomaly:
    """安全异常"""
    type: str
    severity: str
    description: str
    src_ip: str
    dst_ip: str
    timestamp: str
    details: dict
    raw_data: str = ''

# ============================================================
# S7协议解析器
# ============================================================

class S7PacketParser:
    """S7协议数据包解析器"""
    
    def parse(self, raw_data: bytes, src_ip: str = '', dst_ip: str = '',
              src_port: int = 0, dst_port: int = 0) -> Optional[S7Packet]:
        """解析原始数据包"""
        if len(raw_data) < 4:
            return None
        
        packet = S7Packet(
            timestamp=time.time(),
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=src_port,
            dst_port=dst_port,
            raw_data=raw_data,
        )
        
        try:
            # 解析TPKT
            offset = 0
            packet.tpkt = TPKTHeader.parse(raw_data, offset)
            
            if packet.tpkt.version != TPKT.VERSION:
                logger.debug(f"非标准TPKT版本: {packet.tpkt.version}")
                return None
            
            offset += TPKT.HEADER_SIZE
            
            # 解析COTP
            packet.cotp = COTPHeader.parse(raw_data, offset)
            
            # 如果是连接请求/确认, 没有S7数据
            if packet.cotp.pdu_type in (COTP.CONNECT_REQUEST, COTP.CONNECT_CONFIRM,
                                         COTP.DISCONNECT_REQUEST):
                return packet
            
            # 数据传输
            if packet.cotp.pdu_type == COTP.DATA_TRANSFER:
                offset += 3  # COTP数据传输头 (2字节 + EOT)
                
                if offset >= len(raw_data):
                    return packet
                
                # 检查是否为S7协议
                if raw_data[offset] != S7Protocol.PROTOCOL_ID:
                    return packet
                
                # 解析S7头
                packet.s7_header = S7Header.parse(raw_data, offset)
                offset += 10  # S7头长度
                
                # 判断是否为响应
                if packet.s7_header.pdu_type == S7Protocol.PDU_ACK_DATA:
                    packet.is_response = True
                
                # 解析参数区
                if packet.s7_header.param_length > 0:
                    param_end = offset + packet.s7_header.param_length
                    
                    if packet.s7_header.param_length >= 2:
                        packet.func_group = raw_data[offset]
                        packet.sub_func = raw_data[offset + 1]
                        
                        # 解析变量规格
                        if packet.func_group in (S7Protocol.FUNC_READ_VARIABLES,
                                                  S7Protocol.FUNC_WRITE_VARIABLES):
                            item_count = packet.sub_func
                            var_offset = offset + 2
                            
                            for i in range(item_count):
                                if var_offset + 12 <= len(raw_data):
                                    var = S7VariableSpec.parse(raw_data, var_offset)
                                    packet.variables.append(var)
                                    var_offset += 12
                    
                    offset = param_end
                
                # 解析数据区
                if packet.s7_header.data_length > 0 and offset < len(raw_data):
                    packet.data = raw_data[offset:offset + packet.s7_header.data_length]
                    
                    # 对于响应, 解析返回码
                    if packet.is_response and len(packet.data) > 0:
                        packet.return_code = packet.data[0]
            
            return packet
            
        except Exception as e:
            logger.debug(f"解析错误: {e}")
            return None
    
    def format_packet(self, packet: S7Packet) -> str:
        """格式化数据包为可读字符串"""
        lines = []
        
        # 基本信息
        lines.append(f"[{datetime.fromtimestamp(packet.timestamp).isoformat()}] "
                      f"{packet.src_ip}:{packet.src_port} -> "
                      f"{packet.dst_ip}:{packet.dst_port}")
        
        if packet.tpkt:
            lines.append(f"  TPKT: Version={packet.tpkt.version}, "
                          f"Length={packet.tpkt.length}")
        
        if packet.cotp:
            cotp_types = {
                COTP.CONNECT_REQUEST: 'Connect Request',
                COTP.CONNECT_CONFIRM: 'Connect Confirm',
                COTP.DATA_TRANSFER: 'Data Transfer',
                COTP.DISCONNECT_REQUEST: 'Disconnect Request',
            }
            cotp_name = cotp_types.get(packet.cotp.pdu_type, 
                                        f'Unknown(0x{packet.cotp.pdu_type:02X})')
            lines.append(f"  COTP: Type={cotp_name}, Length={packet.cotp.length}")
            
            if 'called_tsap' in packet.cotp.params:
                lines.append(f"        Called TSAP=0x{packet.cotp.params['called_tsap']:04X}")
            if 'calling_tsap' in packet.cotp.params:
                lines.append(f"        Calling TSAP=0x{packet.cotp.params['calling_tsap']:04X}")
            if 'tpdu_size' in packet.cotp.params:
                lines.append(f"        TPDU Size={packet.cotp.params['tpdu_size']}")
        
        if packet.s7_header:
            pdu_types = {
                S7Protocol.PDU_REQUEST: 'Request',
                S7Protocol.PDU_ACK: 'Ack',
                S7Protocol.PDU_ACK_DATA: 'Ack-Data',
                S7Protocol.PDU_USER_DATA: 'User Data',
            }
            pdu_name = pdu_types.get(packet.s7_header.pdu_type,
                                      f'Unknown(0x{packet.s7_header.pdu_type:02X})')
            lines.append(f"  S7: Protocol=0x{packet.s7_header.protocol_id:02X}, "
                          f"PDU={pdu_name}, Ref={packet.s7_header.pdu_ref}")
            lines.append(f"      ParamLen={packet.s7_header.param_length}, "
                          f"DataLen={packet.s7_header.data_length}")
            
            func_names = {
                S7Protocol.FUNC_READ_VARIABLES: 'Read Variables',
                S7Protocol.FUNC_WRITE_VARIABLES: 'Write Variables',
                S7Protocol.FUNC_CPU_CONTROL: 'CPU Control',
                S7Protocol.FUNC_COMM_SETUP: 'Communication Setup',
            }
            func_name = func_names.get(packet.func_group,
                                        f'Unknown(0x{packet.func_group:02X})')
            lines.append(f"      Function: {func_name}")
            
            if packet.func_group == S7Protocol.FUNC_CPU_CONTROL:
                sub_funcs = {
                    0x00: 'START CPU',
                    0x01: 'STOP CPU',
                    0x02: 'READ PROTECTION',
                    0x04: 'COMPRESS',
                }
                sub_name = sub_funcs.get(packet.sub_func,
                                          f'Unknown(0x{packet.sub_func:02X})')
                lines.append(f"      SubFunction: {sub_name}")
            
            for i, var in enumerate(packet.variables):
                var_info = var.to_dict()
                lines.append(f"      Variable[{i}]: Area={var_info['area']}, "
                              f"DB={var_info['db_number']}, "
                              f"Addr={var_info['address']}, "
                              f"Len={var_info['length']}, "
                              f"Type={var_info['transport_size']}")
            
            if packet.is_response:
                ret_name = S7Protocol.RETURN_CODES.get(
                    packet.return_code, f'Unknown(0x{packet.return_code:02X})'
                )
                lines.append(f"      Return Code: {ret_name}")
            
            if packet.data:
                lines.append(f"      Data: {packet.data[:64].hex()}"
                             f"{'...' if len(packet.data) > 64 else ''}")
        
        return '\n'.join(lines)

# ============================================================
# 异常检测引擎
# ============================================================

class AnomalyDetector:
    """S7协议异常检测引擎"""
    
    def __init__(self, authorized_ips: Optional[set] = None,
                 max_reads_per_min: int = 100,
                 max_writes_per_min: int = 50,
                 max_password_attempts: int = 5):
        self.authorized_ips = authorized_ips or set()
        self.max_reads_per_min = max_reads_per_min
        self.max_writes_per_min = max_writes_per_min
        self.max_password_attempts = max_password_attempts
        
        self.read_counts = defaultdict(list)
        self.write_counts = defaultdict(list)
        self.password_attempts = defaultdict(list)
        self.connection_attempts = defaultdict(list)
        self.anomalies: List[Anomaly] = []
    
    def analyze(self, packet: S7Packet) -> List[Anomaly]:
        """分析数据包, 返回检测到的异常"""
        new_anomalies = []
        now = packet.timestamp
        
        # 清理过期记录
        self._cleanup_old_records(now)
        
        # 1. 检查未授权访问
        if (packet.src_ip and self.authorized_ips and
                packet.src_ip not in self.authorized_ips):
            if (packet.cotp and 
                    packet.cotp.pdu_type == COTP.CONNECT_REQUEST):
                anomaly = Anomaly(
                    type=AnomalyType.UNAUTHORIZED_ACCESS,
                    severity='HIGH',
                    description=f'未授权IP {packet.src_ip} 尝试连接PLC',
                    src_ip=packet.src_ip,
                    dst_ip=packet.dst_ip,
                    timestamp=datetime.fromtimestamp(now).isoformat(),
                    details={
                        'src_port': packet.src_port,
                        'dst_port': packet.dst_port,
                        'called_tsap': packet.cotp.params.get('called_tsap'),
                    },
                    raw_data=packet.raw_data.hex()[:200],
                )
                new_anomalies.append(anomaly)
        
        # 2. 检查未授权读取
        if (packet.s7_header and 
                packet.func_group == S7Protocol.FUNC_READ_VARIABLES and
                not packet.is_response):
            self.read_counts[packet.src_ip].append(now)
            
            if self.authorized_ips and packet.src_ip not in self.authorized_ips:
                anomaly = Anomaly(
                    type=AnomalyType.UNAUTHORIZED_READ,
                    severity='HIGH',
                    description=f'未授权读取: {packet.src_ip} 读取PLC数据',
                    src_ip=packet.src_ip,
                    dst_ip=packet.dst_ip,
                    timestamp=datetime.fromtimestamp(now).isoformat(),
                    details={
                        'variables': [v.to_dict() for v in packet.variables],
                        'pdu_ref': packet.s7_header.pdu_ref,
                    },
                    raw_data=packet.raw_data.hex()[:200],
                )
                new_anomalies.append(anomaly)
            
            # 检查过量读取
            recent_reads = len([t for t in self.read_counts[packet.src_ip]
                                if now - t < 60])
            if recent_reads > self.max_reads_per_min:
                anomaly = Anomaly(
                    type=AnomalyType.EXCESSIVE_READS,
                    severity='MEDIUM',
                    description=f'过量读取: {packet.src_ip} 在1分钟内读取{recent_reads}次',
                    src_ip=packet.src_ip,
                    dst_ip=packet.dst_ip,
                    timestamp=datetime.fromtimestamp(now).isoformat(),
                    details={'read_count': recent_reads,
                             'threshold': self.max_reads_per_min},
                )
                new_anomalies.append(anomaly)
        
        # 3. 检查未授权写入
        if (packet.s7_header and 
                packet.func_group == S7Protocol.FUNC_WRITE_VARIABLES and
                not packet.is_response):
            self.write_counts[packet.src_ip].append(now)
            
            severity = 'CRITICAL' if (self.authorized_ips and
                                       packet.src_ip not in self.authorized_ips) else 'HIGH'
            
            anomaly = Anomaly(
                type=AnomalyType.UNAUTHORIZED_WRITE,
                severity=severity,
                description=f'写入操作: {packet.src_ip} 写入PLC数据',
                src_ip=packet.src_ip,
                dst_ip=packet.dst_ip,
                timestamp=datetime.fromtimestamp(now).isoformat(),
                details={
                    'variables': [v.to_dict() for v in packet.variables],
                    'data': packet.data.hex()[:200] if packet.data else '',
                    'pdu_ref': packet.s7_header.pdu_ref,
                },
                raw_data=packet.raw_data.hex()[:200],
            )
            new_anomalies.append(anomaly)
            
            # 检查过量写入
            recent_writes = len([t for t in self.write_counts[packet.src_ip]
                                 if now - t < 60])
            if recent_writes > self.max_writes_per_min:
                anomaly = Anomaly(
                    type=AnomalyType.EXCESSIVE_WRITES,
                    severity='HIGH',
                    description=f'过量写入: {packet.src_ip} 在1分钟内写入{recent_writes}次',
                    src_ip=packet.src_ip,
                    dst_ip=packet.dst_ip,
                    timestamp=datetime.fromtimestamp(now).isoformat(),
                    details={'write_count': recent_writes,
                             'threshold': self.max_writes_per_min},
                )
                new_anomalies.append(anomaly)
        
        # 4. 检查CPU控制命令
        if (packet.s7_header and 
                packet.func_group == S7Protocol.FUNC_CPU_CONTROL):
            sub_func = packet.sub_func
            
            if sub_func == S7Protocol.CPU_SUBFUNC_STOP:
                anomaly = Anomaly(
                    type=AnomalyType.CPU_STOP,
                    severity='CRITICAL',
                    description=f'CPU停止命令: {packet.src_ip} 请求停止CPU',
                    src_ip=packet.src_ip,
                    dst_ip=packet.dst_ip,
                    timestamp=datetime.fromtimestamp(now).isoformat(),
                    details={
                        'sub_func': sub_func,
                        'pdu_ref': packet.s7_header.pdu_ref,
                    },
                    raw_data=packet.raw_data.hex()[:200],
                )
                new_anomalies.append(anomaly)
            
            elif sub_func == S7Protocol.CPU_SUBFUNC_START:
                anomaly = Anomaly(
                    type=AnomalyType.CPU_START,
                    severity='HIGH',
                    description=f'CPU启动命令: {packet.src_ip} 请求启动CPU',
                    src_ip=packet.src_ip,
                    dst_ip=packet.dst_ip,
                    timestamp=datetime.fromtimestamp(now).isoformat(),
                    details={
                        'sub_func': sub_func,
                        'pdu_ref': packet.s7_header.pdu_ref,
                    },
                    raw_data=packet.raw_data.hex()[:200],
                )
                new_anomalies.append(anomaly)
        
        # 5. 检查密码验证 (可能的暴力破解)
        if (packet.s7_header and 
                packet.func_group == S7Protocol.FUNC_PASSWORD):
            self.password_attempts[packet.src_ip].append(now)
            
            recent_attempts = len([t for t in self.password_attempts[packet.src_ip]
                                    if now - t < 300])  # 5分钟窗口
            
            if recent_attempts > self.max_password_attempts:
                anomaly = Anomaly(
                    type=AnomalyType.PASSWORD_BRUTE_FORCE,
                    severity='HIGH',
                    description=f'密码暴力破解: {packet.src_ip} 在5分钟内尝试{recent_attempts}次',
                    src_ip=packet.src_ip,
                    dst_ip=packet.dst_ip,
                    timestamp=datetime.fromtimestamp(now).isoformat(),
                    details={
                        'attempt_count': recent_attempts,
                        'threshold': self.max_password_attempts,
                    },
                )
                new_anomalies.append(anomaly)
        
        # 6. 检查程序下载
        if (packet.s7_header and 
                packet.func_group == S7Protocol.FUNC_PROGRAM_TRANSFER):
            anomaly = Anomaly(
                type=AnomalyType.PROGRAM_DOWNLOAD,
                severity='CRITICAL',
                description=f'程序下载: {packet.src_ip} 正在向PLC下载程序',
                src_ip=packet.src_ip,
                dst_ip=packet.dst_ip,
                timestamp=datetime.fromtimestamp(now).isoformat(),
                details={
                    'pdu_ref': packet.s7_header.pdu_ref,
                    'data_size': packet.s7_header.data_length,
                },
                raw_data=packet.raw_data.hex()[:200],
            )
            new_anomalies.append(anomaly)
        
        # 7. 检查协议异常
        if packet.tpkt and packet.tpkt.version != TPKT.VERSION:
            anomaly = Anomaly(
                type=AnomalyType.ABNORMAL_PACKET,
                severity='MEDIUM',
                description=f'异常TPKT版本: {packet.tpkt.version}',
                src_ip=packet.src_ip,
                dst_ip=packet.dst_ip,
                timestamp=datetime.fromtimestamp(now).isoformat(),
                details={'tpkt_version': packet.tpkt.version},
            )
            new_anomalies.append(anomaly)
        
        if packet.tpkt and packet.tpkt.length > 8192:
            anomaly = Anomaly(
                type=AnomalyType.ABNORMAL_PACKET,
                severity='MEDIUM',
                description=f'异常大数据包: {packet.tpkt.length} bytes',
                src_ip=packet.src_ip,
                dst_ip=packet.dst_ip,
                timestamp=datetime.fromtimestamp(now).isoformat(),
                details={'tpkt_length': packet.tpkt.length},
            )
            new_anomalies.append(anomaly)
        
        # 添加到总列表
        self.anomalies.extend(new_anomalies)
        
        return new_anomalies
    
    def _cleanup_old_records(self, now: float, window: int = 300):
        """清理过期记录"""
        cutoff = now - window
        for ip in list(self.read_counts.keys()):
            self.read_counts[ip] = [t for t in self.read_counts[ip] if t > cutoff]
            if not self.read_counts[ip]:
                del self.read_counts[ip]
        
        for ip in list(self.write_counts.keys()):
            self.write_counts[ip] = [t for t in self.write_counts[ip] if t > cutoff]
            if not self.write_counts[ip]:
                del self.write_counts[ip]
        
        for ip in list(self.password_attempts.keys()):
            self.password_attempts[ip] = [t for t in self.password_attempts[ip] if t > cutoff]
            if not self.password_attempts[ip]:
                del self.password_attempts[ip]
    
    def get_statistics(self) -> dict:
        """获取统计信息"""
        return {
            'total_anomalies': len(self.anomalies),
            'by_type': dict(Counter(a.type for a in self.anomalies)),
            'by_severity': dict(Counter(a.severity for a in self.anomalies)),
            'unique_src_ips': len(set(a.src_ip for a in self.anomalies)),
            'active_read_ips': len(self.read_counts),
            'active_write_ips': len(self.write_counts),
        }

# ============================================================
# 会话记录器
# ============================================================

class SessionLogger:
    """S7通信会话记录器"""
    
    def __init__(self, log_file: str = 's7_sessions.jsonl'):
        self.log_file = log_file
        self.sessions = defaultdict(list)
    
    def log_packet(self, packet: S7Packet):
        """记录数据包"""
        session_key = f"{packet.src_ip}:{packet.src_port}-{packet.dst_ip}:{packet.dst_port}"
        
        entry = {
            'timestamp': datetime.fromtimestamp(packet.timestamp).isoformat(),
            'src_ip': packet.src_ip,
            'dst_ip': packet.dst_ip,
            'src_port': packet.src_port,
            'dst_port': packet.dst_port,
            'raw_data': packet.raw_data.hex(),
            'size': len(packet.raw_data),
        }
        
        if packet.tpkt:
            entry['tpkt_length'] = packet.tpkt.length
        
        if packet.cotp:
            cotp_types = {
                COTP.CONNECT_REQUEST: 'CONNECT_REQ',
                COTP.CONNECT_CONFIRM: 'CONNECT_CONF',
                COTP.DATA_TRANSFER: 'DATA',
                COTP.DISCONNECT_REQUEST: 'DISCONNECT',
            }
            entry['cotp_type'] = cotp_types.get(
                packet.cotp.pdu_type, f'UNKNOWN_0x{packet.cotp.pdu_type:02X}'
            )
        
        if packet.s7_header:
            entry['pdu_type'] = packet.s7_header.pdu_type
            entry['pdu_ref'] = packet.s7_header.pdu_ref
            entry['func_group'] = packet.func_group
            entry['sub_func'] = packet.sub_func
            entry['param_length'] = packet.s7_header.param_length
            entry['data_length'] = packet.s7_header.data_length
            entry['is_response'] = packet.is_response
            
            if packet.variables:
                entry['variables'] = [v.to_dict() for v in packet.variables]
            
            if packet.data:
                entry['s7_data'] = packet.data.hex()[:200]
        
        self.sessions[session_key].append(entry)
        
        # 写入日志文件
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"写入日志失败: {e}")
    
    def get_session_summary(self) -> dict:
        """获取会话摘要"""
        summary = {}
        for key, packets in self.sessions.items():
            summary[key] = {
                'packet_count': len(packets),
                'start_time': packets[0]['timestamp'] if packets else None,
                'end_time': packets[-1]['timestamp'] if packets else None,
                'total_bytes': sum(p['size'] for p in packets),
            }
        return summary

# ============================================================
# 实时网络监控
# ============================================================

class S7NetworkMonitor:
    """S7协议实时网络监控"""
    
    def __init__(self, interface: str = '', port: int = 102,
                 authorized_ips: Optional[set] = None):
        self.interface = interface
        self.port = port
        self.parser = S7PacketParser()
        self.detector = AnomalyDetector(authorized_ips=authorized_ips)
        self.logger = SessionLogger()
        self.running = False
        self.packet_count = 0
    
    def start_live_capture(self):
        """开始实时抓包"""
        try:
            from scapy.all import sniff, IP, TCP
        except ImportError:
            logger.error("需要安装scapy: pip install scapy")
            return
        
        logger.info(f"开始监控端口 {self.port}...")
        logger.info(f"授权IP: {self.detector.authorized_ips or '无(全部告警)'}")
        
        self.running = True
        
        def packet_handler(pkt):
            if not self.running:
                return
            
            if IP in pkt and TCP in pkt:
                payload = bytes(pkt[TCP].payload)
                if len(payload) > 0 and (pkt[TCP].dport == self.port or
                                          pkt[TCP].sport == self.port):
                    self._process_packet(
                        payload,
                        pkt[IP].src,
                        pkt[IP].dst,
                        pkt[TCP].sport,
                        pkt[TCP].dport,
                    )
        
        try:
            sniff(iface=self.interface, prn=packet_handler,
                  filter=f"tcp port {self.port}", store=False)
        except KeyboardInterrupt:
            logger.info("停止监控")
            self.stop()
    
    def analyze_pcap(self, pcap_file: str):
        """分析PCAP文件"""
        try:
            from scapy.all import rdpcap, IP, TCP
        except ImportError:
            logger.error("需要安装scapy: pip install scapy")
            return
        
        logger.info(f"分析PCAP文件: {pcap_file}")
        
        try:
            packets = rdpcap(pcap_file)
            logger.info(f"加载 {len(packets)} 个数据包")
            
            for pkt in packets:
                if IP in pkt and TCP in pkt:
                    payload = bytes(pkt[TCP].payload)
                    if len(payload) > 0 and (pkt[TCP].dport == self.port or
                                              pkt[TCP].sport == self.port):
                        self._process_packet(
                            payload,
                            pkt[IP].src,
                            pkt[IP].dst,
                            pkt[TCP].sport,
                            pkt[TCP].dport,
                        )
            
            self.generate_report()
            
        except Exception as e:
            logger.error(f"分析失败: {e}")
    
    def _process_packet(self, raw_data: bytes, src_ip: str, dst_ip: str,
                        src_port: int, dst_port: int):
        """处理单个数据包"""
        self.packet_count += 1
        
        # 解析数据包
        packet = self.parser.parse(raw_data, src_ip, dst_ip, src_port, dst_port)
        
        if packet is None:
            return
        
        # 记录到会话日志
        self.logger.log_packet(packet)
        
        # 打印数据包详情
        formatted = self.parser.format_packet(packet)
        print(formatted)
        print("-" * 60)
        
        # 检测异常
        anomalies = self.detector.analyze(packet)
        for anomaly in anomalies:
            self._alert(anomaly)
    
    def _alert(self, anomaly: Anomaly):
        """生成告警"""
        severity_colors = {
            'CRITICAL': '\033[91m',
            'HIGH': '\033[93m',
            'MEDIUM': '\033[94m',
            'LOW': '\033[92m',
        }
        reset = '\033[0m'
        color = severity_colors.get(anomaly.severity, '')
        
        print(f"\n{color}[!] 告警 [{anomaly.severity}] {anomaly.type}{reset}")
        print(f"    {anomaly.description}")
        print(f"    时间: {anomaly.timestamp}")
        print(f"    来源: {anomaly.src_ip} -> {anomaly.dst_ip}")
        if anomaly.details:
            print(f"    详情: {json.dumps(anomaly.details, ensure_ascii=False, indent=6)}")
        
        logger.warning(f"告警: {anomaly.type} - {anomaly.description}")
    
    def stop(self):
        """停止监控"""
        self.running = False
        self.generate_report()
    
    def generate_report(self):
        """生成分析报告"""
        print("\n" + "=" * 70)
        print("S7协议分析报告")
        print("=" * 70)
        
        print(f"\n[1] 数据包统计")
        print(f"    总数据包数: {self.packet_count}")
        
        stats = self.detector.get_statistics()
        print(f"\n[2] 异常统计")
        print(f"    总异常数: {stats['total_anomalies']}")
        
        if stats['by_type']:
            print(f"    按类型:")
            for atype, count in sorted(stats['by_type'].items(),
                                        key=lambda x: x[1], reverse=True):
                print(f"      {atype}: {count}")
        
        if stats['by_severity']:
            print(f"    按严重程度:")
            for sev, count in sorted(stats['by_severity'].items(),
                                      key=lambda x: x[1], reverse=True):
                print(f"      {sev}: {count}")
        
        if stats['unique_src_ips']:
            print(f"    涉及IP数: {stats['unique_src_ips']}")
        
        sessions = self.logger.get_session_summary()
        print(f"\n[3] 会话统计")
        print(f"    活跃会话数: {len(sessions)}")
        
        for session, info in sorted(sessions.items(),
                                     key=lambda x: x[1]['packet_count'],
                                     reverse=True)[:10]:
            print(f"    {session}:")
            print(f"      数据包: {info['packet_count']}")
            print(f"      总字节: {info['total_bytes']}")
            if info['start_time']:
                print(f"      开始: {info['start_time']}")
            if info['end_time']:
                print(f"      结束: {info['end_time']}")
        
        # 安全建议
        if stats['total_anomalies'] > 0:
            print(f"\n[4] 安全建议")
            if stats['by_type'].get(AnomalyType.CPU_STOP, 0) > 0:
                print("    [!] 检测到CPU停止命令, 检查是否为合法操作")
            if stats['by_type'].get(AnomalyType.UNAUTHORIZED_WRITE, 0) > 0:
                print("    [!] 检测到未授权写入, 加强访问控制")
            if stats['by_type'].get(AnomalyType.PASSWORD_BRUTE_FORCE, 0) > 0:
                print("    [!] 检测到密码暴力破解, 更改密码并限制访问")
            if stats['by_type'].get(AnomalyType.PROGRAM_DOWNLOAD, 0) > 0:
                print("    [!] 检测到程序下载, 验证是否为授权变更")
        
        print("\n" + "=" * 70)
        print(f"详细日志: s7_sessions.jsonl")
        print(f"告警日志: s7_analyzer.log")
        print("=" * 70)

# ============================================================
# 主程序
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description='S7协议分析器 - 解析、监控和检测S7协议通信',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  实时监控:
    python3 s7_protocol_analyzer.py --live --interface eth0

  分析PCAP文件:
    python3 s7_protocol_analyzer.py --pcap capture.pcap

  带授权IP列表:
    python3 s7_protocol_analyzer.py --live --auth 192.168.1.10,192.168.1.20
"""
    )
    
    parser.add_argument('--live', action='store_true',
                        help='实时监控网络流量')
    parser.add_argument('--pcap', type=str,
                        help='分析PCAP文件')
    parser.add_argument('--interface', '-i', type=str, default='',
                        help='网络接口名称')
    parser.add_argument('--port', '-p', type=int, default=102,
                        help='S7协议端口 (默认: 102)')
    parser.add_argument('--auth', type=str,
                        help='授权IP列表 (逗号分隔)')
    parser.add_argument('--max-reads', type=int, default=100,
                        help='每分钟最大读取次数阈值')
    parser.add_argument('--max-writes', type=int, default=50,
                        help='每分钟最大写入次数阈值')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='详细输出')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # 解析授权IP
    authorized_ips = set()
    if args.auth:
        authorized_ips = set(ip.strip() for ip in args.auth.split(','))
    
    monitor = S7NetworkMonitor(
        interface=args.interface,
        port=args.port,
        authorized_ips=authorized_ips,
    )
    
    # 设置阈值
    monitor.detector.max_reads_per_min = args.max_reads
    monitor.detector.max_writes_per_min = args.max_writes
    
    if args.live:
        print("=" * 70)
        print("S7协议实时监控")
        print(f"网络接口: {args.interface or '默认'}")
        print(f"监控端口: {args.port}")
        print(f"授权IP: {authorized_ips or '无 (全部告警)'}")
        print("=" * 70)
        print()
        
        monitor.start_live_capture()
    
    elif args.pcap:
        if not os.path.exists(args.pcap):
            print(f"文件不存在: {args.pcap}")
            sys.exit(1)
        
        print("=" * 70)
        print("S7协议PCAP分析")
        print(f"分析文件: {args.pcap}")
        print(f"授权IP: {authorized_ips or '无 (全部告警)'}")
        print("=" * 70)
        print()
        
        monitor.analyze_pcap(args.pcap)
    
    else:
        parser.print_help()
        print("\n请选择 --live 或 --pcap 模式")

if __name__ == '__main__':
    main()
