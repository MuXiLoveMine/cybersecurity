#!/usr/bin/env python3
"""
BLE与Zigbee协议安全分析工具
==============================

功能:
1. BLE协议数据包解析与分析
2. Zigbee协议数据包解析与分析
3. BLE安全模式检测与漏洞发现
4. Zigbee网络密钥分析
5. 蓝牙安全攻击检测(BlueBorne, KNOB等)
6. Zigbee攻击检测(Zigbee NWK Key泄露等)
7. 安全评估报告生成

作者: IoT Security Researcher
版本: 1.0.0
"""

import os
import sys
import struct
import logging
import json
import argparse
import hashlib
import time
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from collections import defaultdict, Counter
from enum import IntEnum, IntFlag

# ============================================================
# 日志配置
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('ble_zigbee_analysis.log',
                           encoding='utf-8'),
    ]
)
logger = logging.getLogger('BLEZigbeeAnalyzer')


# ============================================================
# BLE协议常量与枚举
# ============================================================

class BLEAccessAddress:
    """BLE访问地址常量"""
    ADV_ACCESS_ADDR = 0x8E89BED6  # 广播通道访问地址
    ACCESS_ADDR_RANGE = (0x10000000, 0x7FFFFFFF)  # 数据通道范围


class BLEPDUType(IntEnum):
    """BLE PDU类型"""
    ADV_IND = 0x00       # 可连接非定向广播
    ADV_DIRECT_IND = 0x01  # 可连接定向广播
    ADV_NONCONN_IND = 0x02  # 不可连接广播
    SCAN_REQ = 0x03      # 扫描请求
    SCAN_RSP = 0x04      # 扫描响应
    CONNECT_REQ = 0x05   # 连接请求
    ADV_SCAN_IND = 0x06  # 可扫描非定向广播


class BLEDataPDUType(IntEnum):
    """BLE数据PDU类型"""
    LL_CONNECTION_PARAM_REQ = 0x12
    LL_CONNECTION_PARAM_RSP = 0x15
    LL_REJECT_EXT_IND = 0x1B
    LL_ENC_REQ = 0x03
    LL_ENC_RSP = 0x04
    LL_START_ENC_REQ = 0x05
    LL_START_ENC_RSP = 0x06
    LL_PAUSE_ENC_REQ = 0x07
    LL_PAUSE_ENC_RSP = 0x08
    LL_FEATURE_REQ = 0x08
    LL_FEATURE_RSP = 0x09
    LL_VERSION_IND = 0x0C
    LL_PHY_REQ = 0x0D
    LL_PHY_RSP = 0x0E
    LL_TERMINATE_IND = 0x13
    LL_NULL = 0x00
    LL_EMPTY = 0x0F


class BLESecurityMode(IntEnum):
    """BLE安全模式"""
    MODE1_LEVEL1 = 1  # 无安全要求
    MODE1_LEVEL2 = 2  # 未认证配对+加密
    MODE1_LEVEL3 = 3  # 认证配对+加密
    MODE1_LEVEL4 = 4  # 认证LE SC配对+加密
    MODE2_LEVEL1 = 5  # 未认证数据签名
    MODE2_LEVEL2 = 6  # 认证数据签名


# ============================================================
# BLE数据包解析器
# ============================================================

class BLEPacketParser:
    """BLE数据包解析器"""

    # GATT UUID映射
    SERVICE_UUIDS = {
        0x1800: 'Generic Access',
        0x1801: 'Generic Attribute',
        0x180A: 'Device Information',
        0x180F: 'Battery Service',
        0x1809: 'Heart Rate',
        0x180D: 'Blood Pressure',
        0x1810: 'Blood Pressure',
        0x1811: 'Alert Notification',
        0x1812: 'Human Interface Device',
        0x1813: 'Scan Parameters',
        0x1814: 'Running Speed and Cadence',
        0x1815: 'Cycling Speed and Cadence',
        0x1816: 'Cycling Power',
        0x1818: 'Cycling Speed and Cadence',
        0x1819: 'User Data',
        0x181A: 'Environmental Sensing',
        0x181B: 'Body Composition',
        0x181C: 'User Data',
        0x181D: 'Weight Scale',
        0x181E: 'Bond Management',
        0x181F: 'Continuous Glucose Monitoring',
        0x1820: 'Internet Protocol Support',
        0x1821: 'Indoor Positioning',
        0x1822: 'Pulse Oximeter',
        0x1823: 'HTTP Proxy',
        0x1824: 'Transport Discovery',
        0x1825: 'Object Transfer',
        0xFE9F: 'Apple Continuity',
        0xFEAA: 'Google Eddystone',
        0xFEA9: 'Google',
        0xFEB0: 'Samsung',
    }

    # AD类型
    AD_TYPES = {
        0x01: 'Flags',
        0x02: 'Incomplete 16bit Service UUID',
        0x03: 'Complete 16bit Service UUID',
        0x04: 'Incomplete 32bit Service UUID',
        0x05: 'Complete 32bit Service UUID',
        0x06: 'Incomplete 128bit Service UUID',
        0x07: 'Complete 128bit Service UUID',
        0x08: 'Shortened Local Name',
        0x09: 'Complete Local Name',
        0x0A: 'TX Power',
        0x0D: 'Class of Device',
        0x0E: 'Simple Pairing Hash C',
        0x0F: 'Simple Pairing Randomizer R',
        0x10: 'Device ID',
        0x11: 'Security Manager TK Value',
        0x12: 'Security Manager Out of Band Flags',
        0x13: 'Slave Connection Interval Range',
        0x14: 'List of 16bit Service Solicitation',
        0x15: 'List of 128bit Service Solicitation',
        0x16: 'Service Data 16bit UUID',
        0x17: 'Service Data 32bit UUID',
        0x18: 'Service Data 128bit UUID',
        0x19: 'Appearance',
        0x1A: 'Public Target Address',
        0x1B: 'Random Target Address',
        0x1C: 'Advertising Interval',
        0x1D: 'LE Bluetooth Device Address',
        0x1E: 'LE Role',
        0x1F: 'Simple Pairing Hash C-256',
        0x20: 'Simple Pairing Randomizer R-256',
        0x21: '3D Information Data',
        0x22: 'Manufacturer Specific Data',
        0xFF: 'Manufacturer Specific Data',
    }

    def parse_adv_packet(self, data: bytes) -> Dict[str, Any]:
        """解析BLE广播包"""
        result = {
            'type': 'advertisement',
            'access_address': '',
            'pdu_type': '',
            'pdu_type_name': '',
            'addr_type': '',
            'peer_addr': '',
            'ad_data': [],
            'raw_length': len(data),
        }

        if len(data) < 10:
            result['error'] = '数据包过短'
            return result

        # 解析广播PDU头部
        # Access Address (4 bytes, LE)
        access_addr = struct.unpack('<I', data[:4])[0]
        result['access_address'] = f'0x{access_addr:08X}'

        # PDU Header (2 bytes)
        pdu_header = data[4] | (data[5] << 8)
        pdu_type = pdu_header & 0x0F
        chsel = (pdu_header >> 5) & 0x01
        txadd = (pdu_header >> 6) & 0x01
        rxadd = (pdu_header >> 7) & 0x01
        length = (pdu_header >> 8) & 0xFF

        result['pdu_type'] = pdu_type

        try:
            result['pdu_type_name'] = BLEPDUType(pdu_type).name
        except ValueError:
            result['pdu_type_name'] = f'Unknown({pdu_type})'

        result['addr_type'] = 'Random' if txadd else 'Public'

        # 解析地址 (6 bytes, LE)
        if length >= 6 and len(data) >= 4 + 2 + 6:
            addr_bytes = data[6:12]
            addr = ':'.join(f'{b:02X}' for b in reversed(addr_bytes))
            result['peer_addr'] = addr

        # 解析AD structures
        ad_offset = 4 + 2 + 6  # AA + Header + Addr
        ad_data = self._parse_ad_structures(data[ad_offset:ad_offset + length - 6])
        result['ad_data'] = ad_data

        return result

    def _parse_ad_structures(self, data: bytes) -> List[Dict]:
        """解析AD Structure"""
        results = []
        offset = 0

        while offset < len(data):
            if offset + 1 > len(data):
                break

            ad_len = data[offset]
            if ad_len == 0 or offset + 1 + ad_len > len(data):
                break

            if offset + 1 >= len(data):
                break

            ad_type = data[offset + 1]
            ad_value = data[offset + 2:offset + 1 + ad_len]

            ad_entry = {
                'type': ad_type,
                'type_name': self.AD_TYPES.get(ad_type, f'Unknown(0x{ad_type:02X})'),
                'value': ad_value.hex(),
                'value_decoded': self._decode_ad_value(ad_type, ad_value),
            }
            results.append(ad_entry)

            offset += 1 + ad_len

        return results

    def _decode_ad_value(self, ad_type: int, value: bytes) -> str:
        """解码AD值"""
        if ad_type in (0x08, 0x09):  # Local Name
            return value.decode('utf-8', errors='replace')

        elif ad_type == 0x01:  # Flags
            flags = value[0] if value else 0
            flag_names = []
            if flags & 0x01: flag_names.append('LE Limited Discoverable')
            if flags & 0x02: flag_names.append('LE General Discoverable')
            if flags & 0x04: flag_names.append('BR/EDR Not Supported')
            if flags & 0x08: flag_names.append('Simultaneous LE/BR/EDR')
            if flags & 0x10: flag_names.append('Simultaneous LE/BR/EDR Host')
            return ', '.join(flag_names)

        elif ad_type in (0x02, 0x03):  # 16-bit Service UUID
            uuids = []
            for i in range(0, len(value), 2):
                if i + 2 <= len(value):
                    uuid = struct.unpack('<H', value[i:i + 2])[0]
                    name = self.SERVICE_UUIDS.get(uuid, f'0x{uuid:04X}')
                    uuids.append(name)
            return ', '.join(uuids)

        elif ad_type == 0x0A:  # TX Power
            if value:
                return f'{struct.unpack("b", value[:1])[0]} dBm'

        elif ad_type in (0x16,):  # Service Data
            if len(value) >= 2:
                uuid = struct.unpack('<H', value[:2])[0]
                name = self.SERVICE_UUIDS.get(uuid, f'0x{uuid:04X}')
                return f'{name}: {value[2:].hex()}'

        elif ad_type in (0x22, 0xFF):  # Manufacturer Specific
            if len(value) >= 2:
                company_id = struct.unpack('<H', value[:2])[0]
                company_names = {
                    0x004C: 'Apple Inc.',
                    0x00E0: 'Google',
                    0x0075: 'Samsung',
                    0x0006: 'Microsoft',
                    0x000F: 'Broadcom',
                    0x0010: 'Qualcomm',
                    0x0131: 'Xiaomi',
                    0x0171: 'Huawei',
                }
                company = company_names.get(company_id, f'Unknown(0x{company_id:04X})')
                return f'{company}: {value[2:].hex()}'

        elif ad_type == 0x19:  # Appearance
            if len(value) >= 2:
                appearance = struct.unpack('<H', value[:2])[0]
                return f'Appearance: 0x{appearance:04X}'

        return value.hex()

    def parse_data_packet(self, data: bytes) -> Dict[str, Any]:
        """解析BLE数据包"""
        result = {
            'type': 'data',
            'access_address': '',
            'llid': '',
            'nesn': 0,
            'sn': 0,
            'length': 0,
            'payload': '',
        }

        if len(data) < 6:
            result['error'] = '数据包过短'
            return result

        # Access Address
        access_addr = struct.unpack('<I', data[:4])[0]
        result['access_address'] = f'0x{access_addr:08X}'

        # Data Channel PDU Header
        header = data[4] | (data[5] << 8)
        llid = header & 0x03
        nesn = (header >> 2) & 0x01
        sn = (header >> 3) & 0x01
        length = (header >> 8) & 0xFF

        llid_names = {
            0: 'Reserved',
            1: 'LL Data Continuation',
            2: 'LL Data Start',
            3: 'LL Control',
        }
        result['llid'] = llid_names.get(llid, f'Unknown({llid})')
        result['nesn'] = nesn
        result['sn'] = sn
        result['length'] = length

        # 解析LL Control PDU
        if llid == 3 and length > 0:
            payload = data[6:6 + length]
            if payload:
                opcode = payload[0]
                result['ll_opcode'] = opcode

                # 加密相关操作码
                if opcode == 0x03:  # LL_ENC_REQ
                    result['payload'] = self._parse_enc_req(payload[1:])
                elif opcode == 0x04:  # LL_ENC_RSP
                    result['payload'] = self._parse_enc_rsp(payload[1:])
                elif opcode == 0x05:  # LL_START_ENC_REQ
                    result['payload'] = 'Start Encryption Request'
                elif opcode == 0x06:  # LL_START_ENC_RSP
                    result['payload'] = 'Start Encryption Response'
                else:
                    result['payload'] = payload.hex()

        return result

    def _parse_enc_req(self, data: bytes) -> Dict:
        """解析LL_ENC_REQ"""
        result = {}
        if len(data) >= 22:
            rand = data[:8]
            ediv = struct.unpack('<H', data[8:10])[0]
            skdm = data[10:18]
            ivm = data[18:22]

            result['rand'] = rand.hex()
            result['ediv'] = ediv
            result['skdm'] = skdm.hex()
            result['ivm'] = ivm.hex()
            result['note'] = 'Master provides SKd and IVm (unencrypted)'

        return result

    def _parse_enc_rsp(self, data: bytes) -> Dict:
        """解析LL_ENC_RSP"""
        result = {}
        if len(data) >= 22:
            rands = data[:8]
            edivs = struct.unpack('<H', data[8:10])[0]
            skds = data[10:18]
            ivs = data[18:22]

            result['rands'] = rands.hex()
            result['edivs'] = edivs
            result['skds'] = skds.hex()
            result['ivs'] = ivs.hex()
            result['note'] = 'Slave provides SKd and IVs (unencrypted)'

        return result


# ============================================================
# BLE安全分析器
# ============================================================

class BLESecurityAnalyzer:
    """BLE安全分析"""

    # 已知BLE漏洞
    KNOWN_VULNERABILITIES = {
        'BlueBorne': {
            'cve': 'CVE-2017-1000250, CVE-2017-1000251',
            'description': '远程代码执行漏洞, 无需配对',
            'affected': 'Android 4.4-7.1, iOS 9.3.5, Windows',
            'severity': 'CRITICAL',
        },
        'KNOB': {
            'cve': 'CVE-2019-9506',
            'description': 'BLE密钥协商降级攻击, 可将密钥长度降至1字节',
            'affected': '所有支持BLE的设备',
            'severity': 'HIGH',
        },
        'BLURTooth': {
            'cve': 'CVE-2020-15802',
            'description': '跨边界攻击, 可绕过BLE/BR-EDR安全隔离',
            'affected': '支持双模式的设备',
            'severity': 'HIGH',
        },
        'BrakTooth': {
            'cve': 'CVE-2021-28392 等19个CVE',
            'description': '蓝牙协议栈漏洞, 可导致DoS/RCE',
            'affected': '使用商用力泰芯片的设备',
            'severity': 'CRITICAL',
        },
        'BlueFrag': {
            'cve': 'CVE-2020-0022',
            'description': 'L2CAP分段重组漏洞, 可远程执行代码',
            'affected': 'Android 7.0-9.0',
            'severity': 'CRITICAL',
        },
        'SweynTooth': {
            'cve': 'CVE-2019-17519 等多个',
            'description': 'SoC级BLE漏洞, 可导致DoS/死锁/写入',
            'affected': '使用特定BLE SoC的设备',
            'severity': 'HIGH',
        },
    }

    def __init__(self):
        self.findings = []

    def analyze_encryption(self, packets: List[dict]) -> Dict[str, Any]:
        """分析加密配置"""
        result = {
            'encryption_used': False,
            'encryption_strength': 0,
            'key_exchange_observed': False,
            'vulnerabilities': [],
        }

        for pkt in packets:
            if pkt.get('type') == 'data':
                payload = pkt.get('payload', '')

                # 检测加密握手
                opcode = pkt.get('ll_opcode', 0)
                if opcode in (0x03, 0x04):  # LL_ENC_REQ/RSP
                    result['key_exchange_observed'] = True
                    enc_data = pkt.get('payload', {})
                    if isinstance(enc_data, dict) and enc_data.get('skdm'):
                        result['encryption_used'] = True
                        logger.warning(
                            "发现密钥交换! SKd在空中明文传输"
                        )

                elif opcode == 0x05:  # LL_START_ENC_REQ
                    result['encryption_used'] = True
                    logger.info("检测到加密启动请求")

        # 检查加密强度
        if result['encryption_used'] and result['encryption_strength'] < 16:
            result['vulnerabilities'].append({
                'name': 'Weak Encryption',
                'description': '使用弱加密密钥',
                'severity': 'HIGH',
                'recommendation': '确保使用128位AES加密',
            })

        # 检查KNOB攻击
        result['vulnerabilities'].extend(
            self._check_knob_attack(packets)
        )

        return result

    def _check_knob_attack(self, packets: List[dict]) -> List[dict]:
        """检查KNOB攻击"""
        vulns = []

        for pkt in packets:
            payload = pkt.get('payload', '')
            # 如果密钥长度协商显示小于16字节
            if isinstance(payload, str) and 'key_length' in payload:
                key_len_match = re.search(r'key_length.*?(\d+)',
                                         payload)
                if key_len_match:
                    key_len = int(key_len_match.group(1))
                    if key_len < 16:
                        vulns.append({
                            'name': 'KNOB Attack',
                            'description': f'BLE密钥长度仅{key_len}字节, '
                                          f'可被暴力破解',
                            'severity': 'HIGH',
                            'recommendation': '强制最小密钥长度为16字节',
                        })

        return vulns

    def analyze_pairing(self, packets: List[dict]) -> Dict[str, Any]:
        """分析配对过程"""
        result = {
            'pairing_method': 'unknown',
            'secure_connections': False,
            'authentication': False,
            'vulnerabilities': [],
        }

        for pkt in packets:
            if pkt.get('type') == 'advertisement':
                ad_data = pkt.get('ad_data', [])
                for ad in ad_data:
                    if ad.get('type') == 0x11:
                        # Security Manager TK Value
                        result['pairing_method'] = 'Just Works (低安全)'
                        result['vulnerabilities'].append({
                            'name': 'Insecure Pairing',
                            'description': '使用Just Works配对, 无认证',
                            'severity': 'MEDIUM',
                            'recommendation': '使用Passkey或OOB配对',
                        })

        return result

    def check_device_fingerprinting(self, packets: List[dict]) -> Dict:
        """设备指纹分析(隐私追踪风险)"""
        result = {
            'static_address': False,
            'trackable': False,
            'device_names': set(),
            'service_uuids': set(),
        }

        for pkt in packets:
            if pkt.get('type') == 'advertisement':
                addr = pkt.get('peer_addr', '')

                # 检查地址类型
                addr_type = pkt.get('addr_type', '')
                if addr_type == 'Public':
                    result['static_address'] = True
                    result['trackable'] = True

                # 收集设备名称
                for ad in pkt.get('ad_data', []):
                    if ad.get('type') in (0x08, 0x09):
                        name = ad.get('value_decoded', '')
                        if name:
                            result['device_names'].add(name)

                    # 收集服务UUID
                    if ad.get('type') in (0x02, 0x03):
                        uuids = ad.get('value_decoded', '')
                        if uuids:
                            result['service_uuids'].add(uuids)

        if result['static_address']:
            result['vulnerability'] = {
                'name': 'Device Tracking',
                'description': '使用静态/公开地址, 可被追踪',
                'severity': 'MEDIUM',
                'recommendation': '使用随机可解析私有地址(RPA)',
            }

        result['device_names'] = list(result['device_names'])
        result['service_uuids'] = list(result['service_uuids'])
        return result


# ============================================================
# Zigbee协议常量
# ============================================================

class ZigbeeFrameType(IntEnum):
    """Zigbee帧类型"""
    DATA = 0x00
    COMMAND = 0x01
    ACK = 0x02
    MAC_COMMAND = 0x03
    RESERVED = 0x04


class ZigbeeSecurityLevel(IntEnum):
    """Zigbee安全级别"""
    NONE = 0x00          # 无安全
    MIC_32 = 0x01        # 32位MAC
    MIC_64 = 0x02        # 64位MAC
    MIC_128 = 0x03       # 128位MAC
    ENC_MIC_32 = 0x04    # 加密+32位MAC
    ENC_MIC_64 = 0x05    # 加密+64位MAC
    ENC_MIC_128 = 0x06   # 加密+128位MAC


class ZigbeeCommandType(IntEnum):
    """Zigbee网络层命令"""
    ROUTE_REQUEST = 0x01
    ROUTE_REPLY = 0x02
    TABLE_SIZE = 0x03
    LINK_STATUS = 0x04
    NETWORK_STATUS = 0x05
    REJOIN_REQUEST = 0x06
    REJOIN_RESPONSE = 0x07
    LEAVE = 0x08
    ROUTE_RECORD = 0x09
    REJOIN_REQUEST_ROUTER = 0x0A
    LINK_REQUEST = 0x0B
    LINK_REPLY = 0x0C


# ============================================================
# Zigbee数据包解析器
# ============================================================

class ZigbeePacketParser:
    """Zigbee数据包解析器"""

    # 厂商代码
    VENDOR_CODES = {
        0x0000: 'Texas Instruments',
        0x0C43: 'Samsung',
        0x1131: 'NXP Semiconductors',
        0x1037: 'Atmel',
        0x1041: 'Silicon Labs',
        0x119C: 'Ember',
        0x1247: 'Microchip',
        0xC0D3: 'Digi International',
    }

    # Zigbee Profile IDs
    PROFILE_IDS = {
        0x0000: 'Zigbee Device Profile (ZDP)',
        0x0104: 'Home Automation (HA)',
        0x0101: 'Commercial Building Automation',
        0x0105: 'Smart Energy (SE)',
        0x0107: 'Advanced Metering Initiative (AMI)',
        0x0108: 'Lighting',
        0x0109: 'Health Care',
        0x010A: 'Industrial Monitoring',
        0x010B: 'Retail',
        0x010C: 'Telecom',
        0x7F01: 'Test Profile',
    }

    def parse_packet(self, data: bytes) -> Dict[str, Any]:
        """解析Zigbee数据包"""
        result = {
            'protocol': 'Zigbee',
            'raw_length': len(data),
            'frame_type': '',
            'security': False,
            'source_addr': '',
            'dest_addr': '',
            'source_panid': '',
            'dest_panid': '',
            'payload': '',
        }

        if len(data) < 2:
            result['error'] = '数据包过短'
            return result

        # 解析MAC帧控制字段 (2 bytes)
        fcf = struct.unpack('<H', data[:2])[0]
        frame_type = fcf & 0x07
        security_enabled = (fcf >> 3) & 0x01
        frame_pending = (fcf >> 4) & 0x01
        ack_request = (fcf >> 5) & 0x01
        pan_compression = (fcf >> 6) & 0x01
        dest_addr_mode = (fcf >> 10) & 0x03
        source_addr_mode = (fcf >> 14) & 0x03

        try:
            result['frame_type'] = ZigbeeFrameType(frame_type).name
        except ValueError:
            result['frame_type'] = f'Unknown({frame_type})'

        result['security'] = bool(security_enabled)
        result['frame_pending'] = bool(frame_pending)
        result['ack_request'] = bool(ack_request)
        result['pan_compression'] = bool(pan_compression)
        result['dest_addr_mode'] = dest_addr_mode
        result['source_addr_mode'] = source_addr_mode

        offset = 2

        # 序列号
        if offset < len(data):
            seq_num = data[offset]
            result['sequence'] = seq_num
            offset += 1

        # 目标PAN ID
        if dest_addr_mode > 0 and offset + 2 <= len(data):
            dest_pan = struct.unpack('<H', data[offset:offset + 2])[0]
            result['dest_panid'] = f'0x{dest_pan:04X}'
            offset += 2

        # 目标地址
        if dest_addr_mode == 2 and offset + 2 <= len(data):  # Short
            dest_addr = struct.unpack('<H', data[offset:offset + 2])[0]
            result['dest_addr'] = f'0x{dest_addr:04X}'
            offset += 2
        elif dest_addr_mode == 3 and offset + 8 <= len(data):  # Extended
            dest_addr = data[offset:offset + 8]
            result['dest_addr'] = ':'.join(
                f'{b:02X}' for b in dest_addr
            )
            offset += 8

        # 源PAN ID (如果pan_compression=0)
        if not pan_compression and source_addr_mode > 0 and offset + 2 <= len(data):
            src_pan = struct.unpack('<H', data[offset:offset + 2])[0]
            result['source_panid'] = f'0x{src_pan:04X}'
            offset += 2

        # 源地址
        if source_addr_mode == 2 and offset + 2 <= len(data):  # Short
            src_addr = struct.unpack('<H', data[offset:offset + 2])[0]
            result['source_addr'] = f'0x{src_addr:04X}'
            offset += 2
        elif source_addr_mode == 3 and offset + 8 <= len(data):  # Extended
            src_addr = data[offset:offset + 8]
            result['source_addr'] = ':'.join(
                f'{b:02X}' for b in src_addr
            )
            offset += 8

        # 剩余为NWK层负载
        if offset < len(data):
            nwk_data = data[offset:]
            result['nwk_payload'] = nwk_data.hex()
            result.update(self._parse_nwk_header(nwk_data))

        return result

    def _parse_nwk_header(self, data: bytes) -> Dict[str, Any]:
        """解析NWK层头部"""
        result = {}

        if len(data) < 2:
            return result

        # NWK帧控制字段 (2 bytes)
        nfc = struct.unpack('<H', data[:2])[0]
        frame_type = nfc & 0x03
        protocol_version = (nfc >> 2) & 0x0F
        discover_route = (nfc >> 6) & 0x03
        multicast = (nfc >> 8) & 0x01
        security = (nfc >> 9) & 0x01
        source_route = (nfc >> 10) & 0x01
        dest_ieee = (nfc >> 11) & 0x01
        end_device_initiator = (nfc >> 12) & 0x01

        result['nwk_frame_type'] = frame_type
        result['nwk_protocol_version'] = protocol_version
        result['nwk_security'] = bool(security)
        result['nwk_source_route'] = bool(source_route)

        offset = 2

        # 目标地址
        if offset + 2 <= len(data):
            dest = struct.unpack('<H', data[offset:offset + 2])[0]
            result['nwk_dest'] = f'0x{dest:04X}'
            offset += 2

        # 源地址
        if offset + 2 <= len(data):
            src = struct.unpack('<H', data[offset:offset + 2])[0]
            result['nwk_source'] = f'0x{src:04X}'
            offset += 2

        # 距离
        if offset + 1 <= len(data):
            radius = data[offset]
            result['nwk_radius'] = radius
            offset += 1

        # 序列号
        if offset + 1 <= len(data):
            seq = data[offset]
            result['nwk_sequence'] = seq
            offset += 1

        # 安全负载
        if security and offset < len(data):
            security_data = data[offset:]
            result.update(self._parse_security_header(security_data))

        return result

    def _parse_security_header(self, data: bytes) -> Dict[str, Any]:
        """解析安全头部"""
        result = {}

        if len(data) < 5:
            return result

        # 安全控制字节
        sec_ctrl = data[0]
        security_level = sec_ctrl & 0x07
        key_identifier = (sec_ctrl >> 3) & 0x03

        key_names = {
            0: 'Data Key',
            1: 'Network Key',
            2: 'Key Transport Key',
            3: 'Key Load Key',
        }

        result['security_level'] = security_level
        try:
            result['security_level_name'] = ZigbeeSecurityLevel(
                security_level
            ).name
        except ValueError:
            result['security_level_name'] = 'Unknown'

        result['key_identifier'] = key_identifier
        result['key_type'] = key_names.get(key_identifier, 'Unknown')

        # 帧计数器 (4 bytes)
        if len(data) >= 5:
            frame_counter = struct.unpack(
                '<I', data[1:5]
            )[0]
            result['frame_counter'] = frame_counter

        return result


# ============================================================
# Zigbee安全分析器
# ============================================================

class ZigbeeSecurityAnalyzer:
    """Zigbee安全分析"""

    # 已知Zigbee漏洞
    KNOWN_VULNERABILITIES = {
        'ZigBeeOverdrive': {
            'description': '通过远程重置加入Zigbee网络',
            'severity': 'HIGH',
            'affected': '使用Touchlink的设备',
        },
        'Zigbee NWK Key Attack': {
            'description': '通过网络密钥分发漏洞获取密钥',
            'severity': 'CRITICAL',
            'affected': '使用Touchlink或touchlink的设备',
        },
        'Key Transport Attack': {
            'description': '劫持密钥传输, 获取网络密钥',
            'severity': 'CRITICAL',
            'affected': '使用不安全密钥传输的设备',
        },
        'Replay Attack': {
            'description': '重放已捕获的加密数据包',
            'severity': 'MEDIUM',
            'affected': '未实现防重放的设备',
        },
        'Routing Attack': {
            'description': '通过操纵路由表实施MITM',
            'severity': 'HIGH',
            'affected': '路由器节点',
        },
    }

    def __init__(self):
        self.findings = []
        self.captured_keys = []

    def analyze_packet(self, packet: Dict) -> List[Dict]:
        """分析单个数据包"""
        findings = []

        # 检查安全配置
        if not packet.get('security', False) and \
           not packet.get('nwk_security', False):
            findings.append({
                'severity': 'HIGH',
                'category': 'no_encryption',
                'description': '数据包未加密传输',
                'recommendation': '启用网络层加密',
                'packet': packet,
            })

        # 检查安全级别
        sec_level = packet.get('security_level', 0)
        sec_name = packet.get('security_level_name', '')

        if sec_level == 0:
            findings.append({
                'severity': 'HIGH',
                'category': 'no_security',
                'description': f'安全级别: {sec_name} (无安全保护)',
                'recommendation': '使用ENC-MIC-128安全级别',
                'packet': packet,
            })
        elif sec_level < 4:
            findings.append({
                'severity': 'MEDIUM',
                'category': 'weak_security',
                'description': f'安全级别: {sec_name} (仅认证无加密)',
                'recommendation': '使用ENC-MIC-128安全级别',
                'packet': packet,
            })

        # 检查密钥类型
        key_type = packet.get('key_type', '')
        if 'Transport' in key_type or 'Load' in key_type:
            findings.append({
                'severity': 'CRITICAL',
                'category': 'key_transport',
                'description': f'检测到密钥传输: {key_type}',
                'recommendation': '验证密钥传输是否已加密',
                'packet': packet,
            })

        self.findings.extend(findings)
        return findings

    def analyze_network(self, packets: List[dict]) -> Dict[str, Any]:
        """分析整个Zigbee网络"""
        result = {
            'devices': set(),
            'coordinator': '',
            'routers': set(),
            'end_devices': set(),
            'security_config': {},
            'vulnerabilities': [],
            'statistics': {},
        }

        for pkt in packets:
            src = pkt.get('source_addr', '')
            dst = pkt.get('dest_addr', '')

            if src:
                result['devices'].add(src)
            if dst and dst != '0xFFFF':  # 广播地址
                result['devices'].add(dst)

            # 分析安全配置
            if pkt.get('security'):
                result['security_config']['encryption'] = True
                sec_level = pkt.get('security_level', 0)
                if sec_level not in result['security_config']:
                    result['security_config']['sec_levels'] = set()
                result['security_config']['sec_levels'].add(
                    pkt.get('security_level_name', 'Unknown')
                )

        # 统计
        result['statistics']['device_count'] = len(result['devices'])
        result['statistics']['packet_count'] = len(packets)

        # 检查已知漏洞
        if not result['security_config'].get('encryption'):
            result['vulnerabilities'].append({
                'name': 'No Encryption',
                'severity': 'CRITICAL',
                'description': '网络未使用加密',
                'recommendation': '启用网络层加密',
            })

        # 转换集合为列表
        result['devices'] = list(result['devices'])
        result['routers'] = list(result['routers'])
        result['end_devices'] = list(result['end_devices'])
        if 'sec_levels' in result['security_config']:
            result['security_config']['sec_levels'] = list(
                result['security_config']['sec_levels']
            )

        return result


# ============================================================
# 综合分析器
# ============================================================

class BLEZigbeeAnalyzer:
    """BLE与Zigbee综合分析工具"""

    def __init__(self):
        self.ble_parser = BLEPacketParser()
        self.ble_analyzer = BLESecurityAnalyzer()
        self.zigbee_parser = ZigbeePacketParser()
        self.zigbee_analyzer = ZigbeeSecurityAnalyzer()
        self.report = {
            'ble_findings': [],
            'zigbee_findings': [],
            'summary': {},
        }

    def analyze_pcap(self, pcap_path: str) -> Dict[str, Any]:
        """分析PCAP文件"""
        logger.info(f"分析PCAP文件: {pcap_path}")

        # 尝试使用scapy读取PCAP
        try:
            from scapy.all import rdpcap, Dot15d4, BT_LE
            packets = rdpcap(pcap_path)
        except ImportError:
            logger.warning("scapy未安装, 尝试原始解析")
            packets = self._read_pcap_raw(pcap_path)

        ble_packets = []
        zigbee_packets = []

        for pkt in packets:
            try:
                if hasattr(pkt, 'PDUType') or str(pkt.__class__) \
                   .find('BT') >= 0:
                    # BLE数据包
                    raw_data = bytes(pkt)
                    parsed = self.ble_parser.parse_adv_packet(raw_data)
                    if parsed.get('type') == 'advertisement':
                        ble_packets.append(parsed)
                    else:
                        parsed = self.ble_parser.parse_data_packet(
                            raw_data
                        )
                        ble_packets.append(parsed)

                elif hasattr(pkt, 'fcf') or str(pkt.__class__) \
                     .find('15d4') >= 0:
                    # Zigbee数据包
                    raw_data = bytes(pkt)
                    parsed = self.zigbee_parser.parse_packet(raw_data)
                    zigbee_packets.append(parsed)

            except Exception as e:
                logger.debug(f"解析数据包失败: {e}")

        # 分析BLE
        if ble_packets:
            logger.info(f"分析 {len(ble_packets)} 个BLE数据包")
            ble_enc = self.ble_analyzer.analyze_encryption(
                ble_packets
            )
            ble_pair = self.ble_analyzer.analyze_pairing(
                ble_packets
            )
            ble_fp = self.ble_analyzer.check_device_fingerprinting(
                ble_packets
            )

            self.report['ble_findings'] = {
                'packet_count': len(ble_packets),
                'encryption': ble_enc,
                'pairing': ble_pair,
                'fingerprinting': ble_fp,
                'known_vulnerabilities': self.ble_analyzer.KNOWN_VULNERABILITIES,
            }

        # 分析Zigbee
        if zigbee_packets:
            logger.info(f"分析 {len(zigbee_packets)} 个Zigbee数据包")
            zig_net = self.zigbee_analyzer.analyze_network(
                zigbee_packets
            )

            self.report['zigbee_findings'] = {
                'packet_count': len(zigbee_packets),
                'network': zig_net,
                'known_vulnerabilities': self.zigbee_analyzer.KNOWN_VULNERABILITIES,
            }

        # 生成摘要
        self._generate_summary()

        return self.report

    def _read_pcap_raw(self, pcap_path: str) -> list:
        """原始PCAP读取"""
        packets = []

        try:
            with open(pcap_path, 'rb') as f:
                # PCAP全局头 (24 bytes)
                magic = f.read(4)
                if magic == b'\xd4\xc3\xb2\xa1':  # LE
                    endian = '<'
                elif magic == b'\xa1\xb2\xc3\xd4':  # BE
                    endian = '>'
                else:
                    logger.error("无效的PCAP文件")
                    return []

                # 读取全局头
                f.read(20)  # 剩余20字节

                # 读取数据包
                while True:
                    header = f.read(16)
                    if len(header) < 16:
                        break

                    ts_sec, ts_usec, incl_len, orig_len = struct.unpack(
                        f'{endian}IIII', header
                    )
                    data = f.read(incl_len)
                    if len(data) < incl_len:
                        break

                    packets.append(data)

        except Exception as e:
            logger.error(f"读取PCAP失败: {e}")

        return packets

    def _generate_summary(self):
        """生成分析摘要"""
        ble_findings = self.report.get('ble_findings', {})
        zig_findings = self.report.get('zigbee_findings', {})

        summary = {
            'protocols_analyzed': [],
            'total_vulnerabilities': 0,
            'critical_findings': 0,
            'high_findings': 0,
            'medium_findings': 0,
            'recommendations': [],
        }

        if ble_findings:
            summary['protocols_analyzed'].append('BLE')
            ble_enc = ble_findings.get('encryption', {})
            ble_vulns = ble_enc.get('vulnerabilities', [])

            for vuln in ble_vulns:
                sev = vuln.get('severity', 'LOW')
                if sev == 'CRITICAL':
                    summary['critical_findings'] += 1
                elif sev == 'HIGH':
                    summary['high_findings'] += 1
                elif sev == 'MEDIUM':
                    summary['medium_findings'] += 1
                summary['total_vulnerabilities'] += 1

            if not ble_enc.get('encryption_used'):
                summary['recommendations'].append(
                    "BLE: 启用加密配对和连接加密"
                )

            if ble_findings.get('pairing', {}).get(
                'pairing_method'
            ) == 'Just Works (低安全)':
                summary['recommendations'].append(
                    "BLE: 使用更安全的配对方式(Passkey/OOB)"
                )

        if zig_findings:
            summary['protocols_analyzed'].append('Zigbee')
            zig_net = zig_findings.get('network', {})
            zig_vulns = zig_net.get('vulnerabilities', [])

            for vuln in zig_vulns:
                sev = vuln.get('severity', 'LOW')
                if sev == 'CRITICAL':
                    summary['critical_findings'] += 1
                elif sev == 'HIGH':
                    summary['high_findings'] += 1
                elif sev == 'MEDIUM':
                    summary['medium_findings'] += 1
                summary['total_vulnerabilities'] += 1

            if not zig_net.get('security_config', {}).get(
                'encryption'
            ):
                summary['recommendations'].append(
                    "Zigbee: 启用网络层加密"
                )

        self.report['summary'] = summary

    def print_report(self):
        """打印报告"""
        print("\n" + "=" * 60)
        print("BLE与Zigbee安全分析报告")
        print("=" * 60)

        summary = self.report.get('summary', {})
        print(f"\n分析协议: {', '.join(summary.get('protocols_analyzed', []))}")
        print(f"漏洞总数: {summary.get('total_vulnerabilities', 0)}")
        print(f"  严重: {summary.get('critical_findings', 0)}")
        print(f"  高危: {summary.get('high_findings', 0)}")
        print(f"  中危: {summary.get('medium_findings', 0)}")

        if self.report.get('ble_findings'):
            print("\n--- BLE分析结果 ---")
            ble = self.report['ble_findings']
            print(f"数据包数量: {ble.get('packet_count', 0)}")

            enc = ble.get('encryption', {})
            print(f"加密使用: {enc.get('encryption_used', False)}")
            print(f"密钥交换: {enc.get('key_exchange_observed', False)}")

            pair = ble.get('pairing', {})
            print(f"配对方式: {pair.get('pairing_method', '未知')}")

            if enc.get('vulnerabilities'):
                print("加密漏洞:")
                for v in enc['vulnerabilities']:
                    print(f"  [{v['severity']}] {v['name']}: {v['description']}")

        if self.report.get('zigbee_findings'):
            print("\n--- Zigbee分析结果 ---")
            zig = self.report['zigbee_findings']
            print(f"数据包数量: {zig.get('packet_count', 0)}")

            net = zig.get('network', {})
            print(f"设备数量: {net.get('statistics', {}).get('device_count', 0)}")

            sec = net.get('security_config', {})
            print(f"加密: {sec.get('encryption', False)}")

            if net.get('vulnerabilities'):
                print("网络漏洞:")
                for v in net['vulnerabilities']:
                    print(f"  [{v['severity']}] {v['name']}: {v['description']}")

        print("\n--- 建议 ---")
        for i, rec in enumerate(summary.get('recommendations', []), 1):
            print(f"  {i}. {rec}")

        print("\n" + "=" * 60)

    def save_report(self, output_path: str):
        """保存报告到文件"""
        # 序列化
        report_data = json.loads(json.dumps(
            self.report, default=str, ensure_ascii=False
        ))

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        logger.info(f"报告已保存: {output_path}")


# ============================================================
# 实时监控器
# ============================================================

class LiveMonitor:
    """BLE/Zigbee实时监控"""

    def __init__(self, interface: str = 'hci0',
                 protocol: str = 'ble'):
        self.interface = interface
        self.protocol = protocol
        self.analyzer = BLEZigbeeAnalyzer()
        self.running = False

    def start_ble_capture(self, duration: int = 60):
        """开始BLE捕获"""
        logger.info(f"开始BLE捕获 (接口: {self.interface}, "
                    f"时长: {duration}s)")

        try:
            import subprocess

            # 使用hcitool进行扫描
            logger.info("使用hcitool扫描BLE设备...")
            result = subprocess.run(
                ['hcitool', '-i', self.interface, 'lescan',
                 '--duplicates'],
                capture_output=True, timeout=duration, text=True
            )

            devices = set()
            for line in result.stdout.split('\n'):
                parts = line.split()
                if len(parts) >= 2:
                    addr = parts[0]
                    name = ' '.join(parts[1:]) if len(parts) > 2 else ''
                    devices.add((addr, name))

            logger.info(f"发现 {len(devices)} 个BLE设备")
            for addr, name in devices:
                logger.info(f"  {addr}: {name}")

        except FileNotFoundError:
            logger.error("hcitool未安装, 请安装bluez工具包")
        except subprocess.TimeoutExpired:
            logger.info("扫描超时, 停止")
        except Exception as e:
            logger.error(f"BLE扫描失败: {e}")

    def start_zigbee_capture(self, channel: int = 11,
                             duration: int = 60):
        """开始Zigbee捕获"""
        logger.info(f"开始Zigbee捕获 (通道: {channel}, "
                    f"时长: {duration}s)")

        try:
            # 使用killerbee或api-mote
            import subprocess

            result = subprocess.run(
                ['zbid'],
                capture_output=True, timeout=10, text=True
            )
            logger.info(f"Zigbee设备: {result.stdout}")

        except FileNotFoundError:
            logger.error("Zigbee工具未安装, 请安装KillerBee")
        except Exception as e:
            logger.error(f"Zigbee扫描失败: {e}")


# ============================================================
# 主入口
# ============================================================

def main():
    import re  # 模块级导入在文件顶部也需要

    parser = argparse.ArgumentParser(
        description='BLE与Zigbee协议安全分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 分析PCAP文件
  python ble_zigbee_analyzer.py -f capture.pcap

  # 指定协议
  python ble_zigbee_analyzer.py -f capture.pcap --protocol ble

  # 实时BLE扫描
  python ble_zigbee_analyzer.py --live-scan --interface hci0

  # 生成报告
  python ble_zigbee_analyzer.py -f capture.pcap -o report.json
        """
    )

    parser.add_argument('-f', '--file', help='PCAP文件路径')
    parser.add_argument('-o', '--output', default='ble_zigbee_report.json',
                        help='输出报告文件路径')
    parser.add_argument('--protocol', choices=['ble', 'zigbee', 'both'],
                        default='both', help='分析协议')
    parser.add_argument('--live-scan', action='store_true',
                        help='实时扫描BLE设备')
    parser.add_argument('--interface', default='hci0',
                        help='BLE接口 (默认: hci0)')
    parser.add_argument('--duration', type=int, default=60,
                        help='扫描时长(秒)')

    args = parser.parse_args()

    if args.live_scan:
        monitor = LiveMonitor(args.interface, 'ble')
        monitor.start_ble_capture(args.duration)
        return

    if not args.file:
        parser.print_help()
        return

    if not os.path.exists(args.file):
        logger.error(f"文件不存在: {args.file}")
        sys.exit(1)

    analyzer = BLEZigbeeAnalyzer()
    analyzer.analyze_pcap(args.file)
    analyzer.print_report()
    analyzer.save_report(args.output)


if __name__ == '__main__':
    main()
