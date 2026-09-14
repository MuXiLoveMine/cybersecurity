#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 无线网络安全 - 攻防实战案例集
================================================================================
 本文件面向安全学习者，系统展示五类无线安全攻防技术。

 学习目标:
   1. 掌握 802.11 帧解析与 WPA2 四次握手分析
   2. 理解 Evil Twin 攻击原理与防御方法
   3. 学习 BLE 协议安全分析与攻击面
   4. 掌握企业 WiFi 安全审计方法
   5. 了解 Zigbee 协议安全分析

 声明: 所有代码均为教学模拟，在受控环境中运行。
       严禁用于非法用途，请遵守当地法律法规。
================================================================================
"""

import struct
import hashlib
import hmac
import os
import random
import binascii
from collections import OrderedDict

# ==============================================================================
# 通用工具函数
# ==============================================================================

def mac_str_to_bytes(mac):
    """将 MAC 地址字符串转换为字节 (如 'AA:BB:CC:DD:EE:FF' → 6字节)"""
    return bytes(int(b, 16) for b in mac.split(':'))

def mac_bytes_to_str(mac_bytes):
    """将 MAC 字节转换为字符串"""
    return ':'.join(f'{b:02X}' for b in mac_bytes)

def hexdump(data, prefix='    '):
    """十六进制转储"""
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f'{prefix}{i:04x}  {hex_part:<48s}  |{ascii_part}|')
    return '\n'.join(lines)

def pbkdf2_password_to_pmk(password, ssid):
    """
    将 WPA2 密码 + SSID 转换为 PMK (Pairwise Master Key)
    使用 PBKDF2-HMAC-SHA1, 迭代4096次, 输出32字节
    这就是 WPA2 密码离线破解的核心计算
    """
    return hashlib.pbkdf2_hmac('sha1', password.encode('utf-8'),
                               ssid.encode('utf-8'), 4096, 32)

def compute_ptk(pmk, aa, spa, anonce, snonce):
    """
    计算 PTK (Pairwise Transient Key)
    输入: PMK, AP地址, STA地址, ANonce, SNonce
    输出: 64字节 PTK (用于加密单播数据)
    
    WPA2 使用 PRF-512 函数:
      PTK = PRF(PMK, "Pairwise key expansion", min(AA,SPA)||max(AA,SPA)||min(AN,SN)||max(AN,SN))
    """
    # 按大小排序地址和nonce
    if aa < spa:
        addr_min, addr_max = aa, spa
    else:
        addr_min, addr_max = spa, aa

    if anonce < snonce:
        nonce_min, nonce_max = anonce, snonce
    else:
        nonce_min, nonce_max = snonce, anonce

    # PRF-512: 使用 HMAC-SHA1 生成64字节
    label = b"Pairwise key expansion"
    b = b""
    ptk = b""
    for i in range(4):  # 4轮 * 20字节 = 80字节 (取前64字节)
        b = bytes([i])
        input_data = label + b'\x00' + addr_min + addr_max + nonce_min + nonce_max + b
        ptk += hmac.new(pmk, input_data, hashlib.sha1).digest()

    return ptk[:64]

def compute_mic(ptk, frame_data, key_version=2):
    """
    计算 MIC (Message Integrity Code)
    key_version=2 使用 AES-CMAC (WPA2)
    key_version=1 使用 HMAC-MD5 (WPA1)
    """
    if key_version == 2:
        # WPA2: AES-128-CMAC (简化为 HMAC-SHA256 前16字节)
        mic_key = ptk[:16]
        return hmac.new(mic_key, frame_data, hashlib.sha256).digest()[:16]
    else:
        # WPA1: HMAC-MD5
        mic_key = ptk[:16]
        return hmac.new(mic_key, frame_data, hashlib.md5).digest()[:16]


# ==============================================================================
# 案例一: WiFi 渗透测试全流程
# ==============================================================================
# 原理说明:
#   WiFi 渗透测试的核心是捕获 WPA2 四次握手包，然后离线暴力破解。
#
#   802.11 帧类型:
#     - Beacon (类型0, 子类型8): AP 定期广播，包含 SSID/加密/信道等
#     - Probe (类型0, 子类型4): 客户端主动探测
#     - Authentication (类型0, 子类型11): 开放/共享密钥认证
#     - Association (类型0, 子类型0/1): 关联请求/响应
#     - EAPOL (类型2, 子类型0): 802.1X 认证 (四次握手在此帧上)
#     - Deauth (类型0, 子类型12): 取消认证帧
#
#   WPA2 四次握手:
#     AP → STA:  ANonce          (握手1)
#     STA → AP:  SNonce + MIC    (握手2) ← 最关键，含MIC可用于离线破解
#     AP → STA:  加密密钥+MIC     (握手3)
#     STA → AP:  ACK             (握手4)
#
#   离线破解原理:
#     PMK = PBKDF2(password, SSID, 4096, 32)
#     PTK = PRF(PMK, AA, SPA, ANonce, SNonce)
#     MIC = HMAC(PTK, frame_data)
#     → 逐个尝试密码，计算MIC，与捕获的MIC比对
# ==============================================================================

class Dot11Frame:
    """802.11 帧解析器"""

    # 帧类型常量
    TYPE_MANAGEMENT = 0
    TYPE_CONTROL = 1
    TYPE_DATA = 2

    # 管理帧子类型
    SUBTYPE_BEACON = 8
    SUBTYPE_PROBE_REQ = 4
    SUBTYPE_PROBE_RESP = 5
    SUBTYPE_AUTH = 11
    SUBTYPE_DEAUTH = 12
    SUBTYPE_ASSOC_REQ = 0
    SUBTYPE_ASSOC_RESP = 1

    @staticmethod
    def parse(frame_bytes):
        """解析 802.11 帧头部"""
        if len(frame_bytes) < 24:
            return None

        # 帧控制字段 (2字节)
        fc = struct.unpack('<H', frame_bytes[0:2])[0]
        protocol_version = fc & 0x03
        frame_type = (fc >> 2) & 0x03
        frame_subtype = (fc >> 4) & 0x0F
        to_ds = (fc >> 8) & 0x01
        from_ds = (fc >> 9) & 0x01

        # 地址字段 (各6字节)
        addr1 = frame_bytes[4:10]    # 接收地址
        addr2 = frame_bytes[10:16]   # 发送地址
        addr3 = frame_bytes[16:22]   # 目标地址 (BSSID)

        # 序列控制 (2字节)
        seq_ctrl = struct.unpack('<H', frame_bytes[22:24])[0]
        frag_num = seq_ctrl & 0x0F
        seq_num = (seq_ctrl >> 4) & 0x0FFF

        parsed = {
            'protocol_version': protocol_version,
            'type': frame_type,
            'subtype': frame_subtype,
            'to_ds': to_ds,
            'from_ds': from_ds,
            'addr1': addr1,
            'addr2': addr2,
            'addr3': addr3,
            'bssid': addr3,
            'frag_num': frag_num,
            'seq_num': seq_num,
            'body': frame_bytes[24:],
        }

        parsed['type_name'] = Dot11Frame._type_name(frame_type, frame_subtype)
        return parsed

    @staticmethod
    def _type_name(ftype, fsubtype):
        """返回帧类型描述"""
        names = {
            (0, 0): "Association Request",
            (0, 1): "Association Response",
            (0, 4): "Probe Request",
            (0, 5): "Probe Response",
            (0, 8): "Beacon",
            (0, 11): "Authentication",
            (0, 12): "Deauthentication",
            (2, 0): "Data",
        }
        return names.get((ftype, fsubtype), f"Type={ftype} Subtype={fsubtype}")


class BeaconFrame:
    """Beacon 帧解析 (AP 广播帧)"""

    @staticmethod
    def parse(parsed_frame):
        """解析 Beacon 帧体"""
        body = parsed_frame['body']
        info = {}

        # Timestamp (8字节)
        info['timestamp'] = struct.unpack('<Q', body[0:8])[0]
        # Beacon Interval (2字节)
        info['beacon_interval'] = struct.unpack('<H', body[8:10])[0]
        # Capability Info (2字节)
        cap = struct.unpack('<H', body[10:12])[0]
        info['privacy'] = bool(cap & 0x0010)  # 隐私位 (加密)
        info['ibss'] = bool(cap & 0x0001)      # 独立基本服务集

        # 解析信息元素 (IE)
        offset = 12
        while offset + 2 < len(body):
            ie_id = body[offset]
            ie_len = body[offset + 1]
            ie_data = body[offset + 2:offset + 2 + ie_len]

            if ie_id == 0:          # SSID
                info['ssid'] = ie_data.decode('utf-8', errors='replace')
            elif ie_id == 1:        # Supported Rates
                info['rates'] = [r & 0x7F for r in ie_data]
            elif ie_id == 3:        # DS Parameter Set (Channel)
                info['channel'] = ie_data[0] if ie_data else 0
            elif ie_id == 7:        # Country
                info['country'] = ie_data[:3].decode('ascii', errors='replace')
            elif ie_id == 48:       # RSN (WPA2)
                info['rsn'] = BeaconFrame._parse_rsn(ie_data)
            elif ie_id == 221:      # Vendor Specific (WPA)
                if b'\x00P\xf2' in ie_data[:4]:
                    info['wpa'] = BeaconFrame._parse_wpa(ie_data)

            offset += 2 + ie_len

        return info

    @staticmethod
    def _parse_rsn(data):
        """解析 RSN (WPA2) 信息元素"""
        if len(data) < 4:
            return {}
        version = struct.unpack('<H', data[0:2])[0]
        group_cipher = data[2:6].decode('ascii', errors='replace')
        # 简化解析
        return {
            'version': version,
            'group_cipher': group_cipher,
            'pairwise_cipher': 'CCMP',  # 简化
            'auth_suite': 'PSK',        # 简化
            'wpa2': True,
        }

    @staticmethod
    def _parse_wpa(data):
        """解析 WPA (旧版) 信息元素"""
        return {'wpa': True, 'cipher': 'TKIP'}


class EAPOLFrame:
    """EAPOL (802.1X) 帧解析 - 四次握手"""

    @staticmethod
    def parse(data):
        """解析 EAPOL-Key 帧"""
        if len(data) < 95:
            return None

        # 802.1X Header (4字节)
        version = data[0]
        packet_type = data[1]  # 3 = EAPOL-Key
        packet_length = struct.unpack('>H', data[2:4])[0]

        # Key Descriptor Type (1字节)
        key_type = data[4]  # 2 = WPA2 Key

        # Key Information (2字节, 大端)
        key_info = struct.unpack('>H', data[5:7])[0]
        key_length = struct.unpack('>H', data[7:9])[0]

        # Replay Counter (8字节)
        replay_counter = data[9:17]

        # Key Nonce (32字节) - ANonce 或 SNonce
        key_nonce = data[17:49]

        # Key IV (16字节)
        key_iv = data[49:65]

        # Key RSC (8字节)
        key_rsc = data[65:73]

        # Key ID (8字节)
        key_id = data[73:81]

        # Key MIC (16字节)
        key_mic = data[81:97]

        # Key Data (变长)
        key_data_length = struct.unpack('>H', data[93:95])[0]
        key_data = data[95:95+key_data_length]

        # 解析握手消息编号
        install = (key_info >> 6) & 1
        key_ack = (key_info >> 7) & 1
        key_mic_flag = (key_info >> 8) & 1
        secure = (key_info >> 9) & 1
        error = (key_info >> 10) & 1
        request = (key_info >> 11) & 1
        encrypted = (key_info >> 12) & 1
        pairwise = (key_info >> 3) & 1

        # 判断握手消息编号 (1-4)
        if key_ack and not key_mic_flag and not secure:
            msg_num = 1  # AP → STA: ANonce
        elif key_mic_flag and not key_ack and not secure and pairwise:
            msg_num = 2  # STA → AP: SNonce + MIC ← 破解关键!
        elif key_mic_flag and key_ack and secure:
            msg_num = 3  # AP → STA: GTK + MIC
        elif key_mic_flag and not key_ack and secure:
            msg_num = 4  # STA → AP: ACK
        else:
            msg_num = 0

        return {
            'version': version,
            'key_type': key_type,
            'key_info': key_info,
            'key_length': key_length,
            'replay_counter': replay_counter,
            'key_nonce': key_nonce,     # ANonce (msg1/3) 或 SNonce (msg2/4)
            'key_iv': key_iv,
            'key_mic': key_mic,
            'key_data': key_data,
            'msg_num': msg_num,
            'install': install,
            'secure': secure,
        }


class WPA2Cracker:
    """WPA2 握手包离线破解框架"""

    def __init__(self, ssid, bssid):
        self.ssid = ssid
        self.bssid = bssid
        self.handshake = {}  # 存储握手包数据

    def set_handshake(self, aa, spa, anonce, snonce, mic, eapol_frame):
        """设置四次握手捕获数据"""
        self.handshake = {
            'aa': aa,           # AP MAC
            'spa': spa,         # STA MAC
            'anonce': anonce,   # AP Nonce
            'snonce': snonce,   # STA Nonce
            'mic': mic,         # 捕获的 MIC
            'eapol': eapol_frame,  # 用于 MIC 计算的 EAPOL 帧
        }

    def try_password(self, password):
        """
        尝试用给定密码计算 MIC
        如果 MIC 匹配则密码正确
        """
        # 步骤1: 密码 + SSID → PMK
        pmk = pbkdf2_password_to_pmk(password, self.ssid)

        # 步骤2: PMK + 地址 + Nonce → PTK
        ptk = compute_ptk(
            pmk,
            self.handshake['aa'],
            self.handshake['spa'],
            self.handshake['anonce'],
            self.handshake['snonce']
        )

        # 步骤3: PTK + EAPOL帧 → MIC
        computed_mic = compute_mic(ptk, self.handshake['eapol'])

        # 步骤4: 比对 MIC
        return computed_mic == self.handshake['mic']

    def crack_with_wordlist(self, wordlist):
        """使用字典进行离线破解"""
        for password in wordlist:
            if self.try_password(password):
                return password
        return None


def generate_sample_capture():
    """生成模拟的 802.11 捕获数据 (自构造帧)"""

    # AP 信息
    ap_mac = mac_str_to_bytes('AA:BB:CC:11:22:33')
    sta_mac = mac_str_to_bytes('11:22:33:AA:BB:CC')
    ssid = "HomeWiFi_5G"

    frames = []

    # --- Beacon 帧 ---
    beacon = bytearray()
    # Frame Control: Management + Beacon
    fc = (Dot11Frame.TYPE_MANAGEMENT << 2) | (Dot11Frame.SUBTYPE_BEACON << 4)
    beacon.extend(struct.pack('<H', fc))
    beacon.extend(b'\x00\x00\x00\x00')           # Duration
    beacon.extend(b'\xff\xff\xff\xff\xff\xff')    # DA: 广播
    beacon.extend(ap_mac)                         # SA: AP
    beacon.extend(ap_mac)                         # BSSID: AP
    beacon.extend(struct.pack('<H', 0x0000))       # Seq Control

    # Beacon Body
    beacon.extend(struct.pack('<Q', 1234567890))  # Timestamp
    beacon.extend(struct.pack('<H', 100))          # Beacon Interval (100 TU)
    cap = 0x0411  # Privacy + ESS
    beacon.extend(struct.pack('<H', cap))          # Capability
    # IE: SSID
    beacon.extend(bytes([0, len(ssid)]))
    beacon.extend(ssid.encode())
    # IE: DS Parameter (Channel 6)
    beacon.extend(bytes([3, 1, 6]))
    # IE: RSN (WPA2)
    rsn_data = struct.pack('<H', 1) + b'CCMP' + struct.pack('<HH', 1, 0) + b'CCMP'
    beacon.extend(bytes([48, len(rsn_data)]))
    beacon.extend(rsn_data)

    frames.append(('Beacon', bytes(beacon)))

    # --- EAPOL 四次握手帧 (模拟) ---
    anonce = os.urandom(32)
    snonce = os.urandom(32)
    password = "password123"
    pmk = pbkdf2_password_to_pmk(password, ssid)
    ptk = compute_ptk(pmk, ap_mac, sta_mac, anonce, snonce)

    # 构造 EAPOL-Key 帧 (握手消息2)
    eapol = bytearray()
    eapol.extend(bytes([2, 3]))                    # Version, Type=3 (Key)
    eapol.extend(struct.pack('>H', 95))            # Packet Length
    eapol.extend(bytes([2]))                       # Key Descriptor Type (WPA2)
    key_info = 0x0101  # MIC + Pairwise
    eapol.extend(struct.pack('>H', key_info))
    eapol.extend(struct.pack('>H', 16))            # Key Length
    eapol.extend(struct.pack('>Q', 1))             # Replay Counter
    eapol.extend(snonce)                           # Key Nonce (SNonce)
    eapol.extend(b'\x00' * 16)                    # Key IV
    eapol.extend(b'\x00' * 8)                     # Key RSC
    eapol.extend(b'\x00' * 8)                     # Key ID
    eapol.extend(b'\x00' * 16)                    # MIC placeholder
    eapol.extend(struct.pack('>H', 0))             # Key Data Length

    # 计算 MIC
    mic = compute_mic(ptk, bytes(eapol))
    eapol[81:97] = mic  # 填入 MIC

    # 封装为 Data 帧
    data_frame = bytearray()
    fc_data = (Dot11Frame.TYPE_DATA << 2)
    data_frame.extend(struct.pack('<H', fc_data))
    data_frame.extend(b'\x00\x00\x00\x00')        # Duration
    data_frame.extend(ap_mac)                     # DA
    data_frame.extend(sta_mac)                     # SA
    data_frame.extend(ap_mac)                     # BSSID
    data_frame.extend(struct.pack('<H', 0x0000))   # Seq Control
    data_frame.extend(bytes(eapol))                # EAPOL body

    frames.append(('EAPOL-M2', bytes(data_frame)))

    return frames, {
        'ssid': ssid,
        'ap_mac': ap_mac,
        'sta_mac': sta_mac,
        'anonce': anonce,
        'snonce': snonce,
        'mic': mic,
        'eapol': bytes(eapol),
        'password': password,
        'pmk': pmk,
        'ptk': ptk,
    }


def case1_wifi_penetration():
    """案例1: WiFi 渗透测试全流程"""

    print("=" * 72)
    print("  案例一: WiFi 渗透测试全流程")
    print("=" * 72)

    # -------------------------------------------------------------------------
    # 步骤1: 捕获并解析 802.11 帧
    # -------------------------------------------------------------------------
    print(f"\n[1] 802.11 帧捕获与分析")

    frames, meta = generate_sample_capture()

    print(f"    捕获帧数: {len(frames)}")
    for name, frame_data in frames:
        parsed = Dot11Frame.parse(frame_data)
        if parsed:
            print(f"\n    --- {name} ---")
            print(f"    类型: {parsed['type_name']}")
            print(f"    发送方: {mac_bytes_to_str(parsed['addr2'])}")
            print(f"    接收方: {mac_bytes_to_str(parsed['addr1'])}")
            print(f"    BSSID:  {mac_bytes_to_str(parsed['addr3'])}")

    # -------------------------------------------------------------------------
    # 步骤2: Beacon 帧解析
    # -------------------------------------------------------------------------
    print(f"\n[2] Beacon 帧解析")
    beacon_parsed = Dot11Frame.parse(frames[0][1])
    beacon_info = BeaconFrame.parse(beacon_parsed)

    print(f"    SSID:          {beacon_info.get('ssid', 'N/A')}")
    print(f"    信道:          Ch.{beacon_info.get('channel', '?')}")
    print(f"    加密:          {'WPA2' if beacon_info.get('rsn') else 'Open' if not beacon_info.get('privacy') else 'WEP'}")
    print(f"    Beacon间隔:   {beacon_info.get('beacon_interval', '?')} TU")

    # -------------------------------------------------------------------------
    # 步骤3: 四次握手包识别
    # -------------------------------------------------------------------------
    print(f"\n[3] WPA2 四次握手包识别")
    eapol_parsed = Dot11Frame.parse(frames[1][1])
    if eapol_parsed:
        eapol_data = eapol_parsed['body']
        eapol_info = EAPOLFrame.parse(eapol_data)
        if eapol_info:
            print(f"    握手消息编号: {eapol_info['msg_num']}")
            print(f"    Key Nonce:    {eapol_info['key_nonce'][:8].hex()}...")
            print(f"    MIC:          {eapol_info['key_mic'][:8].hex()}...")
            print(f"    安装标志:     {eapol_info['install']}")
            print(f"    安全标志:     {eapol_info['secure']}")

    # -------------------------------------------------------------------------
    # 步骤4: 离线破解
    # -------------------------------------------------------------------------
    print(f"\n[4] WPA2 握手包离线破解")

    cracker = WPA2Cracker(meta['ssid'], meta['ap_mac'])
    cracker.set_handshake(
        meta['ap_mac'], meta['sta_mac'],
        meta['anonce'], meta['snonce'],
        meta['mic'], meta['eapol']
    )

    # 模拟字典攻击
    wordlist = ["12345678", "password", "admin123", meta['password'],
                "letmein", "qwerty", "password123"]
    print(f"    字典大小: {len(wordlist)} 个密码")
    print(f"    正在破解...")

    found = cracker.crack_with_wordlist(wordlist)
    if found:
        print(f"    [破解成功!] 密码: {found}")
    else:
        print(f"    [破解失败] 字典中未找到匹配密码")

    # -------------------------------------------------------------------------
    # 步骤5: 安全评估报告
    # -------------------------------------------------------------------------
    print(f"\n[5] WiFi 安全评估报告")
    print(f"    {'=' .ljust(50, '=')}")
    print(f"    SSID:          {meta['ssid']}")
    print(f"    BSSID:         {mac_bytes_to_str(meta['ap_mac'])}")
    print(f"    加密方式:      WPA2-PSK (CCMP)")
    print(f"    密码强度:      {'弱' if len(meta['password']) < 12 else '中等'} ({len(meta['password'])}字符)")
    print(f"    破解耗时:      < 1秒 (字典命中)")
    print(f"    风险等级:      {'高' if len(meta['password']) < 12 else '中'}")

    # -------------------------------------------------------------------------
    # 防御建议
    # -------------------------------------------------------------------------
    print(f"\n[防御建议]")
    print("  1. 使用强密码: 至少12位，包含大小写字母、数字、特殊字符")
    print("  2. 升级到 WPA3 (SAE 替代 PSK, 抗离线破解)")
    print("  3. 禁用 WPS (存在 Pixie-Dust 攻击)")
    print("  4. 启用管理帧保护 (PMF / 802.11w)")
    print("  5. 定期检查是否有未授权 AP (Rogue AP 检测)")
    print("  6. 企业环境使用 802.1X + RADIUS 认证")


# ==============================================================================
# 案例二: Evil Twin 攻击模拟
# ==============================================================================
# 原理说明:
#   Evil Twin (邪恶双子) 攻击是指部署一个与合法 AP 相同 SSID 的伪造 AP，
#   诱使客户端连接到伪造 AP，从而进行中间人攻击。
#
#   攻击流程:
#     1. 侦测目标 AP 信息 (SSID/BSSID/信道/加密)
#     2. 构造伪造 Beacon 帧 (相同 SSID, 不同 BSSID)
#     3. 发送 Deauth 帧强制客户端断开合法连接
#     4. 客户端自动重连到信号更强的伪造 AP
#     5. 在伪造 AP 上部署钓鱼页面或中间人监听
#
#   Deauth 帧结构:
#     Frame Control: Management + Deauth (0x00C0)
#     Duration: 0
#     DA: 客户端 MAC (或广播)
#     SA: 伪造的 AP MAC (伪装为合法 AP)
#     BSSID: 合法 AP 的 BSSID
#     Reason Code: 7 (Class 3 frame from non-associated STA)
# ==============================================================================

class EvilTwinAttack:
    """Evil Twin 攻击模拟"""

    def __init__(self, target_ssid, target_bssid, target_channel):
        self.target_ssid = target_ssid
        self.target_bssid = target_bssid
        self.target_channel = target_channel
        # 攻击者 AP 使用不同的 MAC
        self.evil_bssid = mac_str_to_bytes('00:DE:AD:BE:EF:00')

    def craft_fake_beacon(self):
        """构造伪造 Beacon 帧 (与目标相同 SSID)"""
        beacon = bytearray()

        # Frame Control: Management + Beacon
        fc = (Dot11Frame.TYPE_MANAGEMENT << 2) | (Dot11Frame.SUBTYPE_BEACON << 4)
        beacon.extend(struct.pack('<H', fc))
        beacon.extend(b'\x00\x00\x00\x00')           # Duration
        beacon.extend(b'\xff\xff\xff\xff\xff\xff')    # DA: 广播
        beacon.extend(self.evil_bssid)               # SA: Evil Twin MAC
        beacon.extend(self.evil_bssid)               # BSSID: Evil Twin
        beacon.extend(struct.pack('<H', 0x0000))      # Seq Control

        # Beacon Body
        beacon.extend(struct.pack('<Q', 0))           # Timestamp
        beacon.extend(struct.pack('<H', 100))         # Beacon Interval
        beacon.extend(struct.pack('<H', 0x0411))      # Capability: Privacy + ESS

        # IE: SSID (与目标相同)
        ssid_bytes = self.target_ssid.encode()
        beacon.extend(bytes([0, len(ssid_bytes)]))
        beacon.extend(ssid_bytes)

        # IE: DS Parameter (与目标相同信道)
        beacon.extend(bytes([3, 1, self.target_channel]))

        return bytes(beacon)

    def craft_deauth(self, target_sta, reason_code=7):
        """
        构造 Deauth 帧 (伪装为合法 AP 发送给客户端)
        reason_code: 7=非关联站点发送数据帧
        """
        deauth = bytearray()

        # Frame Control: Management + Deauth
        fc = (Dot11Frame.TYPE_MANAGEMENT << 2) | (Dot11Frame.SUBTYPE_DEAUTH << 4)
        deauth.extend(struct.pack('<H', fc))
        deauth.extend(b'\x00\x00\x00\x00')           # Duration
        deauth.extend(target_sta)                      # DA: 目标客户端
        deauth.extend(self.target_bssid)               # SA: 伪装为合法 AP
        deauth.extend(self.target_bssid)               # BSSID: 合法 AP
        deauth.extend(struct.pack('<H', 0x0000))       # Seq Control

        # Fixed Parameters
        deauth.extend(struct.pack('<H', reason_code))  # Reason Code

        return bytes(deauth)

    def craft_deauth_broadcast(self, reason_code=7):
        """构造广播 Deauth 帧 (断开所有客户端)"""
        return self.craft_deauth(b'\xff\xff\xff\xff\xff\xff', reason_code)

    def phishing_page(self):
        """生成钓鱼页面 HTML 框架"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{self.target_ssid} - 登录认证</title>
    <style>
        body {{ font-family: Arial; background: #f0f0f0; text-align: center; }}
        .login-box {{ width: 350px; margin: 100px auto; padding: 30px;
                      background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        input {{ width: 280px; padding: 10px; margin: 8px 0; border: 1px solid #ccc; }}
        button {{ width: 300px; padding: 12px; background: #0078d4;
                 color: white; border: none; cursor: pointer; }}
    </style>
</head>
<body>
    <div class="login-box">
        <h2>{self.target_ssid}</h2>
        <p>请输入您的 WiFi 密码以完成认证</p>
        <form method="POST" action="/auth">
            <input type="password" name="password" placeholder="WiFi密码">
            <button type="submit">连接</button>
        </form>
    </div>
</body>
</html>"""
        return html


def case2_evil_twin():
    """案例2: Evil Twin 攻击模拟"""

    print("\n" + "=" * 72)
    print("  案例二: Evil Twin 攻击模拟")
    print("=" * 72)

    target_ssid = "CompanyWiFi"
    target_bssid = mac_str_to_bytes('AA:BB:CC:11:22:33')
    target_channel = 6

    attack = EvilTwinAttack(target_ssid, target_bssid, target_channel)

    # -------------------------------------------------------------------------
    # 步骤1: 构造伪造 Beacon 帧
    # -------------------------------------------------------------------------
    print(f"\n[1] 伪造 Beacon 帧构造")
    fake_beacon = attack.craft_fake_beacon()
    parsed = Dot11Frame.parse(fake_beacon)

    print(f"    SSID:         {target_ssid}")
    print(f"    合法 BSSID:   {mac_bytes_to_str(target_bssid)}")
    print(f"    伪造 BSSID:   {mac_bytes_to_str(attack.evil_bssid)}")
    print(f"    信道:         Ch.{target_channel}")
    print(f"    帧类型:       {parsed['type_name']}")
    print(f"    帧长度:       {len(fake_beacon)} 字节")

    # -------------------------------------------------------------------------
    # 步骤2: Deauth 帧构造
    # -------------------------------------------------------------------------
    print(f"\n[2] Deauth 帧构造")
    target_sta = mac_str_to_bytes('11:22:33:44:55:66')
    deauth = attack.craft_deauth(target_sta, reason_code=7)
    deauth_parsed = Dot11Frame.parse(deauth)

    print(f"    帧类型:       {deauth_parsed['type_name']}")
    print(f"    目标:         {mac_bytes_to_str(deauth_parsed['addr1'])}")
    print(f"    伪装来源:     {mac_bytes_to_str(deauth_parsed['addr2'])}")
    print(f"    Reason Code:  7 (非关联站点发送数据帧)")

    # 广播 Deauth
    deauth_bcast = attack.craft_deauth_broadcast()
    print(f"\n    广播 Deauth:")
    print(f"    目标:         ff:ff:ff:ff:ff:ff (所有客户端)")

    # -------------------------------------------------------------------------
    # 步骤3: 钓鱼页面
    # -------------------------------------------------------------------------
    print(f"\n[3] 钓鱼页面框架")
    page = attack.phishing_page()
    print(f"    页面标题: {target_ssid} - 登录认证")
    print(f"    页面大小: {len(page)} 字节")
    print(f"    (钓鱼页面将收集用户输入的 WiFi 密码)")

    # -------------------------------------------------------------------------
    # 步骤4: 检测与防御
    # -------------------------------------------------------------------------
    print(f"\n[4] Evil Twin 检测方法")
    print(f"    1. BSSID 异常: 同一 SSID 出现不同 BSSID")
    print(f"    2. 信道变化: AP 突然切换信道")
    print(f"    3. 信号强度: 多个相同 SSID 的 AP 竞争")
    print(f"    4. 证书异常: TLS 证书指纹不匹配")
    print(f"    5. 行为异常: 频繁收到 Deauth 帧")

    # -------------------------------------------------------------------------
    # 防御建议
    # -------------------------------------------------------------------------
    print(f"\n[防御建议]")
    print("  1. 启用管理帧保护 (PMF/802.11w) - 防止伪造 Deauth")
    print("  2. 使用 EAP-TLS 证书认证 - 客户端验证 AP 身份")
    print("  3. 部署 WIDS/WIPS 检测伪造 AP")
    print("  4. 配置客户端不自动连接开放网络")
    print("  5. 使用 VPN 加密所有流量 (即使连接到恶意 AP)")
    print("  6. 定期扫描环境中的 Rogue AP")


# ==============================================================================
# 案例三: BLE 设备扫描与攻击
# ==============================================================================
# 原理说明:
#   BLE (Bluetooth Low Energy) 是低功耗蓝牙协议，广泛用于物联网设备。
#
#   BLE 协议栈:
#     Physical Layer:    2.4GHz, 40个信道 (37个数据 + 3个广播)
#     Link Layer:        广播态/连接态切换, 状态机
#     L2CAP:             逻辑链路控制
#     ATT:               属性协议 (读写特征值)
#     GATT:              通用属性配置文件 (Service/Characteristic)
#     GAP:               通用访问配置文件 (广播/扫描/连接)
#
#   攻击面:
#     - 被动嗅探: 捕获广播/连接数据
#     - 主动扫描: 枚举 GATT 服务和特征值
#     - 重放攻击: 录制并重放 GATT 写入操作
#     - 密钥爆破: 针对 Just Works 配对的密钥暴力破解
#     - 中间人: 在配对过程中拦截密钥
#
#   广播帧 (Advertising PDU) 结构:
#     Preamble (1字节) + Access Address (4字节) + PDU Header (2字节)
#     + Payload (6-37字节) + CRC (3字节)
#
#   GATT 层级:
#     Profile → Service → Characteristic → Descriptor
# ==============================================================================

class BLEAdvertiser:
    """BLE 广播帧模拟"""

    # 广播类型
    ADV_IND = 0       # 可连接非定向广播
    ADV_DIRECT_IND = 1  # 可连接定向广播
    ADV_SCAN_IND = 2  # 不可连接广播
    ADV_NONCONN_IND = 3  # 不可连接非定向广播
    SCAN_REQ = 4      # 扫描请求
    SCAN_RSP = 5      # 扫描响应

    @staticmethod
    def generate_advertisement(mac_addr, name, service_uuids=None):
        """生成模拟 BLE 广播数据"""
        adv_data = bytearray()

        # AD Type: Flags (0x01)
        flags = 0x05  # LE General + BR/EDR Not Supported
        adv_data.extend(bytes([2, 1, flags]))

        # AD Type: Complete Local Name (0x09)
        name_bytes = name.encode('utf-8')
        adv_data.extend(bytes([len(name_bytes) + 1, 9]))
        adv_data.extend(name_bytes)

        # AD Type: Service UUIDs (0x03 for 16-bit, 0x07 for 128-bit)
        if service_uuids:
            for uuid in service_uuids:
                if len(uuid) == 4:  # 16-bit UUID
                    adv_data.extend(bytes([3, 3]))
                    adv_data.extend(bytes.fromhex(uuid[2:4] + uuid[0:2]))

        # AD Type: TX Power Level (0x0A)
        adv_data.extend(bytes([2, 0x0A, 0x00]))

        # Manufacturer Specific (0xFF)
        adv_data.extend(bytes([4, 0xFF]))
        adv_data.extend(b'\x4c\x00')  # Apple
        adv_data.extend(bytes([0x02]))  #subtype

        return bytes(adv_data)

    @staticmethod
    def parse_advertisement(adv_data):
        """解析 BLE 广播数据"""
        result = {}
        offset = 0

        while offset < len(adv_data):
            if offset + 1 >= len(adv_data):
                break
            ad_len = adv_data[offset]
            if ad_len == 0 or offset + 1 + ad_len > len(adv_data):
                break
            ad_type = adv_data[offset + 1]
            ad_value = adv_data[offset + 2:offset + 1 + ad_len]

            if ad_type == 0x01:         # Flags
                result['flags'] = ad_value[0] if ad_value else 0
            elif ad_type == 0x09:       # Complete Local Name
                result['name'] = ad_value.decode('utf-8', errors='replace')
            elif ad_type == 0x02:       # Incomplete 16-bit UUID
                result['uuids_16bit_inc'] = [ad_value[i:i+2][::-1].hex() for i in range(0, len(ad_value), 2)]
            elif ad_type == 0x03:       # Complete 16-bit UUID
                result['uuids_16bit'] = [ad_value[i:i+2][::-1].hex() for i in range(0, len(ad_value), 2)]
            elif ad_type == 0x0A:       # TX Power Level
                val = ad_value[0] if ad_value else 0
                result['tx_power'] = val - 256 if val > 127 else val
            elif ad_type == 0xFF:       # Manufacturer Specific
                if len(ad_value) >= 2:
                    result['manufacturer'] = struct.unpack('<H', ad_value[0:2])[0]
                    result['manufacturer_data'] = ad_value[2:]

            offset += 1 + ad_len

        return result


class GATTService:
    """GATT 服务模拟"""

    def __init__(self, uuid, name):
        self.uuid = uuid
        self.name = name
        self.characteristics = []  # 特征值列表

    def add_characteristic(self, char):
        self.characteristics.append(char)


class GATTCharacteristic:
    """GATT 特征值模拟"""

    # 权限标志
    PROP_READ = 0x02
    PROP_WRITE = 0x08
    PROP_NOTIFY = 0x10
    PROP_INDICATE = 0x20

    def __init__(self, uuid, name, properties=PROP_READ, value=b''):
        self.uuid = uuid
        self.name = name
        self.properties = properties
        self.value = bytearray(value)
        self.descriptors = {}

    def read(self):
        """读取特征值"""
        if self.properties & self.PROP_READ:
            return bytes(self.value)
        return None

    def write(self, data):
        """写入特征值"""
        if self.properties & self.PROP_WRITE:
            self.value = bytearray(data)
            return True
        return False


class BLEDevice:
    """BLE 设备模拟"""

    def __init__(self, name, mac_addr):
        self.name = name
        self.mac_addr = mac_addr
        self.services = []
        self.paired = False
        self.pair_key = None
        self.connected = False
        self.write_history = []  # 用于重放攻击检测

        # 模拟安全等级
        self.security_level = 0  # 0=无, 1=Just Works, 2=Passkey, 3=OOB

    def add_service(self, service):
        self.services.append(service)

    def enumerate_gatt(self):
        """GATT 服务枚举"""
        result = []
        for svc in self.services:
            svc_info = {
                'uuid': svc.uuid,
                'name': svc.name,
                'characteristics': []
            }
            for char in svc.characteristics:
                perms = []
                if char.properties & char.PROP_READ: perms.append('READ')
                if char.properties & char.PROP_WRITE: perms.append('WRITE')
                if char.properties & char.PROP_NOTIFY: perms.append('NOTIFY')
                if char.properties & char.PROP_INDICATE: perms.append('INDICATE')
                svc_info['characteristics'].append({
                    'uuid': char.uuid,
                    'name': char.name,
                    'permissions': perms,
                    'value_preview': bytes(char.read()[:16]).hex() if char.read() else 'N/A'
                })
            result.append(svc_info)
        return result

    def write_characteristic(self, char_uuid, data):
        """写入特征值 (记录用于重放检测)"""
        for svc in self.services:
            for char in svc.characteristics:
                if char.uuid == char_uuid:
                    self.write_history.append({
                        'uuid': char_uuid,
                        'data': bytes(data),
                        'timestamp': len(self.write_history),
                    })
                    return char.write(data)
        return False

    def pair_just_works(self):
        """Just Works 配对 (无认证)"""
        self.security_level = 1
        self.pair_key = os.urandom(16)  # 随机密钥
        self.paired = True
        return self.pair_key

    def pair_passkey(self, passkey):
        """Passkey 配对 (需要输入6位数字)"""
        if len(str(passkey)) != 6:
            return False
        self.security_level = 2
        self.pair_key = hashlib.sha256(str(passkey).encode()).digest()[:16]
        self.paired = True
        return self.pair_key


class BLEAttacker:
    """BLE 攻击框架"""

    @staticmethod
    def crack_passkey(target_device):
        """配对密钥暴力破解 (6位数字: 000000-999999)"""
        print(f"    开始暴力破解 6 位 Passkey...")
        for attempt in range(1000000):
            passkey = f"{attempt:06d}"
            # 真实场景: 需要捕获配对过程并验证
            # 这里简化: 假设正确密钥是某个特定值
            if attempt == 123456:
                return passkey
            if attempt % 100000 == 0 and attempt > 0:
                print(f"    已尝试 {attempt}/1000000...")
        return None

    @staticmethod
    def replay_write(target_device, char_uuid, original_data):
        """重放攻击: 重新发送之前捕获的写入操作"""
        print(f"    重放写入: UUID={char_uuid}, Data={original_data[:16].hex()}...")
        return target_device.write_characteristic(char_uuid, original_data)


def case3_ble():
    """案例3: BLE 设备扫描与攻击"""

    print("\n" + "=" * 72)
    print("  案例三: BLE 设备扫描与攻击")
    print("=" * 72)

    # -------------------------------------------------------------------------
    # 步骤1: BLE 设备扫描 (广播帧解析)
    # -------------------------------------------------------------------------
    print(f"\n[1] BLE 设备扫描 (广播帧解析)")

    # 模拟多个 BLE 设备广播
    devices = [
        ("Smart Lock", "01:23:45:67:89:AB", ["1809"]),   # 温度服务
        ("Heart Rate", "02:34:56:78:9A:BC", ["180D"]),   # 心率服务
        ("Smart Bulb", "03:45:67:89:AB:CD", ["FFE0"]),   # 自定义服务
    ]

    for name, mac, uuids in devices:
        adv_data = BLEAdvertiser.generate_advertisement(
            mac_str_to_bytes(mac), name, uuids
        )
        parsed = BLEAdvertiser.parse_advertisement(adv_data)
        print(f"\n    设备: {parsed.get('name', 'N/A')}")
        print(f"    MAC:  {mac}")
        print(f"    UUID: {parsed.get('uuids_16bit', [])}")
        print(f"    TX:   {parsed.get('tx_power', 'N/A')} dBm")
        print(f"    MFR:  0x{parsed.get('manufacturer', 0):04x}")

    # -------------------------------------------------------------------------
    # 步骤2: GATT 服务枚举
    # -------------------------------------------------------------------------
    print(f"\n[2] GATT 服务枚举")

    # 创建智能锁设备
    lock = BLEDevice("Smart Lock", "01:23:45:67:89:AB")

    # 添加锁控制服务
    lock_svc = GATTService("00001809-0000-1000-8000-00805f9b34fb", "Device Information")
    lock_svc.add_characteristic(GATTCharacteristic(
        "00002a29-0000-1000-8000-00805f9b34fb", "Manufacturer Name",
        GATTCharacteristic.PROP_READ, b"AcmeLock"
    ))
    lock_svc.add_characteristic(GATTCharacteristic(
        "00002a24-0000-1000-8000-00805f9b34fb", "Model Number",
        GATTCharacteristic.PROP_READ, b"AL-2024"
    ))
    lock.add_service(lock_svc)

    # 添加锁控制服务
    lock_ctrl = GATTService("0000fff0-0000-1000-8000-00805f9b34fb", "Lock Control")
    lock_ctrl.add_characteristic(GATTCharacteristic(
        "0000fff1-0000-1000-8000-00805f9b34fb", "Lock State",
        GATTCharacteristic.PROP_READ | GATTCharacteristic.PROP_NOTIFY, b"\x00"
    ))
    lock_ctrl.add_characteristic(GATTCharacteristic(
        "0000fff2-0000-1000-8000-00805f9b34fb", "Lock Command",
        GATTCharacteristic.PROP_WRITE, b""
    ))
    lock.add_service(lock_ctrl)

    # 枚举 GATT
    gatt_info = lock.enumerate_gatt()
    for svc in gatt_info:
        print(f"\n    Service: {svc['name']} ({svc['uuid'][:8]}...)")
        for char in svc['characteristics']:
            print(f"      [{', '.join(char['permissions']):<20s}] "
                  f"{char['name']:<20s} UUID={char['uuid'][:8]}... "
                  f"Value={char['value_preview']}")

    # -------------------------------------------------------------------------
    # 步骤3: 特征值读写模拟
    # -------------------------------------------------------------------------
    print(f"\n[3] BLE 特征值读写模拟")

    # 读取锁状态
    state_svc = lock.services[1].characteristics[0]
    print(f"    读取锁状态: {state_svc.read().hex()} (0x00=锁定)")

    # 写入开锁命令
    cmd_char = lock.services[1].characteristics[1]
    lock.write_characteristic(cmd_char.uuid, b'\x01')  # 0x01=开锁
    print(f"    写入开锁命令: 0x01")
    print(f"    锁状态更新: {state_svc.read().hex()} (0x01=已开锁)")

    # -------------------------------------------------------------------------
    # 步骤4: 配对密钥爆破
    # -------------------------------------------------------------------------
    print(f"\n[4] 配对密钥暴力破解 (Just Works / Passkey)")

    # Just Works 配对 (无认证 - 最不安全)
    key = lock.pair_just_works()
    print(f"    Just Works 配对:")
    print(f"      安全等级: {lock.security_level} (低 - 无认证)")
    print(f"      密钥: {key.hex()[:16]}... (随机生成, 易被窃听)")

    # Passkey 配对暴力破解
    print(f"\n    Passkey 配对暴力破解:")
    attacker = BLEAttacker()
    found_key = attacker.crack_passkey(lock)
    if found_key:
        print(f"    [破解成功!] Passkey: {found_key}")
        print(f"    破解速度: ~{1000000}次/秒 (6位数字空间仅100万)")

    # -------------------------------------------------------------------------
    # 步骤5: 重放攻击模拟
    # -------------------------------------------------------------------------
    print(f"\n[5] 重放攻击模拟")

    # 记录之前的写入操作
    print(f"    捕获写入历史: {len(lock.write_history)} 条")
    for entry in lock.write_history:
        print(f"      #{entry['timestamp']}: UUID={entry['uuid'][:8]}... "
              f"Data={entry['data'].hex()}")

    # 重放第一条写入
    if lock.write_history:
        replay_entry = lock.write_history[0]
        print(f"\n    重放 #{replay_entry['timestamp']} 的写入操作:")
        BLEAttacker.replay_write(lock, replay_entry['uuid'], replay_entry['data'])
        print(f"    [重放成功!] 设备状态可能被非授权修改")

    # -------------------------------------------------------------------------
    # 防御建议
    # -------------------------------------------------------------------------
    print(f"\n[防御建议]")
    print("  1. 使用 LE Secure Connections (蓝牙4.2+) 替代 Legacy Pairing")
    print("  2. 避免使用 Just Works 配对 (安全等级最低)")
    print("  3. 使用 OOB (带外) 配对方式 (如NFC)")
    print("  4. 在应用层加密敏感数据 (不依赖链路层加密)")
    print("  5. 对写入操作添加时间戳/序号防重放")
    print("  6. 限制 GATT 服务发现范围 (避免信息泄露)")
    print("  7. 配置特征值权限 (需要认证/授权才能写入)")


# ==============================================================================
# 案例四: 无线安全审计工具
# ==============================================================================
# 原理说明:
#   企业 WiFi 安全审计需要系统性地检查配置项, 包括:
#     - 加密方式 (WPA2/WPA3, CCMP/TKIP)
#     - 认证方式 (PSK/802.1X/EAP)
#     - SSID 广播策略
#     - MAC 地址过滤
#     - WPS 功能状态
#     - 管理帧保护 (PMF/802.11w)
#     - 信号泄露 (超出物理边界)
#
#   无线入侵检测 (WIDS) 规则可输出为 Snort/Suricata 格式,
#   用于检测异常无线行为:
#     - Rogue AP 检测
#     - Deauth 攻击检测
#     - Evil Twin 检测
#     - 未授权客户端
# ==============================================================================

class WiFiSecurityAuditor:
    """企业 WiFi 安全审计工具"""

    def __init__(self, config):
        self.config = config
        self.findings = []

    def check_encryption(self):
        """检查加密方式"""
        enc = self.config.get('encryption', 'unknown')
        if enc == 'WPA3':
            self.findings.append(('PASS', '加密方式', 'WPA3-SAE', '使用最新加密标准'))
        elif enc == 'WPA2-CCMP':
            self.findings.append(('PASS', '加密方式', 'WPA2-CCMP', '安全'))
        elif enc == 'WPA2-TKIP':
            self.findings.append(('WARN', '加密方式', 'WPA2-TKIP', 'TKIP 已过时, 建议升级CCMP'))
        elif enc == 'WPA':
            self.findings.append(('FAIL', '加密方式', 'WPA', 'WPA存在已知漏洞, 必须升级'))
        elif enc == 'WEP':
            self.findings.append(('FAIL', '加密方式', 'WEP', 'WEP可在数秒内破解!'))
        else:
            self.findings.append(('FAIL', '加密方式', enc, '无加密或未知!'))

    def check_authentication(self):
        """检查认证方式"""
        auth = self.config.get('authentication', 'unknown')
        if auth == '802.1X':
            self.findings.append(('PASS', '认证方式', '802.1X+EAP', '企业级认证'))
        elif auth == 'WPA3-SAE':
            self.findings.append(('PASS', '认证方式', 'WPA3-SAE', '抗离线破解'))
        elif auth == 'WPA2-PSK':
            self.findings.append(('WARN', '认证方式', 'WPA2-PSK', '共享密钥, 离线可破解'))
        else:
            self.findings.append(('FAIL', '认证方式', auth, '认证方式不安全'))

    def check_ssid_broadcast(self):
        """检查 SSID 广播策略"""
        hidden = self.config.get('ssid_hidden', False)
        if hidden:
            self.findings.append(('INFO', 'SSID广播', '隐藏', '隐藏SSID不提供实质安全, 可能影响连接体验'))
        else:
            self.findings.append(('INFO', 'SSID广播', '广播', '正常, SSID公开可见'))

    def check_mac_filter(self):
        """检查 MAC 过滤"""
        mac_filter = self.config.get('mac_filter', False)
        if mac_filter:
            self.findings.append(('INFO', 'MAC过滤', '已启用', 'MAC地址可伪造, 仅作为辅助控制'))
        else:
            self.findings.append(('INFO', 'MAC过滤', '未启用', 'MAC过滤安全性有限'))

    def check_wps(self):
        """检查 WPS 状态"""
        wps = self.config.get('wps_enabled', True)
        if wps:
            self.findings.append(('FAIL', 'WPS功能', '已启用', 'WPS存在PIN码爆破漏洞, 建议禁用'))
        else:
            self.findings.append(('PASS', 'WPS功能', '已禁用', '安全'))

    def check_pmf(self):
        """检查管理帧保护"""
        pmf = self.config.get('pmf', 'disabled')
        if pmf == 'required':
            self.findings.append(('PASS', '管理帧保护', '强制启用', '可防止Deauth等攻击'))
        elif pmf == 'capable':
            self.findings.append(('WARN', '管理帧保护', '支持但非强制', '建议设为强制模式'))
        else:
            self.findings.append(('FAIL', '管理帧保护', '未启用', '易受Deauth/Evil Twin攻击'))

    def check_signal_leakage(self):
        """检查信号泄露"""
        signal = self.config.get('signal_dbm', -30)
        if signal > -50:
            self.findings.append(('WARN', '信号覆盖', f'{signal}dBm', '信号过强, 可能超出办公区域'))
        elif signal > -65:
            self.findings.append(('PASS', '信号覆盖', f'{signal}dBm', '信号覆盖适当'))
        else:
            self.findings.append(('INFO', '信号覆盖', f'{signal}dBm', '信号较弱'))

    def run_full_audit(self):
        """执行完整安全审计"""
        self.check_encryption()
        self.check_authentication()
        self.check_ssid_broadcast()
        self.check_mac_filter()
        self.check_wps()
        self.check_pmf()
        self.check_signal_leakage()

    def generate_report(self):
        """生成审计报告"""
        report = []
        report.append("=" * 65)
        report.append("        企业 WiFi 安全审计报告")
        report.append("=" * 65)
        report.append(f"\n  审计对象: {self.config.get('ssid', 'N/A')}")
        report.append(f"  BSSID:   {self.config.get('bssid', 'N/A')}")
        report.append(f"  审计时间: 2026-09-11")

        report.append(f"\n  {'检查项':<16s} {'状态':<8s} {'当前配置':<16s} {'说明'}")
        report.append(f"  {'-' * 120}")

        pass_count = warn_count = fail_count = info_count = 0
        for status, item, value, desc in self.findings:
            report.append(f"  {item:<16s} [{status:<4s}] {value:<16s} {desc}")
            if status == 'PASS': pass_count += 1
            elif status == 'WARN': warn_count += 1
            elif status == 'FAIL': fail_count += 1
            else: info_count += 1

        report.append(f"\n  审计结果汇总:")
        report.append(f"    通过 (PASS): {pass_count}")
        report.append(f"    警告 (WARN): {warn_count}")
        report.append(f"    失败 (FAIL): {fail_count}")
        report.append(f"    信息 (INFO): {info_count}")

        # 综合风险评级
        if fail_count > 0:
            risk = "高危 - 存在严重安全问题, 需立即修复"
        elif warn_count > 2:
            risk = "中危 - 存在潜在风险, 建议优化"
        elif warn_count > 0:
            risk = "低危 - 存在少量建议项"
        else:
            risk = "安全 - 配置符合最佳实践"

        report.append(f"    综合评级: {risk}")

        # 修复建议
        if fail_count > 0 or warn_count > 0:
            report.append(f"\n  修复建议:")
            for status, item, value, desc in self.findings:
                if status in ('FAIL', 'WARN'):
                    report.append(f"    [{item}] {desc}")

        return '\n'.join(report)


class WIDSRuleGenerator:
    """无线入侵检测规则生成器 (Snort/Suricata格式)"""

    @staticmethod
    def generate_deauth_rule(bssid=None):
        """生成 Deauth 攻击检测规则"""
        bssid_filter = f"content:\"{bssid}\"; " if bssid else ""
        rule = (
            f"alert wlan 192.168.1.0/24 any -> any any "
            f"(msg:\"WiFi Deauth 攻击检测\"; "
            f"{bssid_filter}"
            f"type:management, subtype:deauth; "
            f"threshold:type both, track by_src, count 5, seconds 10; "
            f"sid:1000001; rev:1;)"
        )
        return rule

    @staticmethod
    def generate_evil_twin_rule(ssid):
        """生成 Evil Twin 检测规则"""
        rule = (
            f"alert wlan any any -> any any "
            f"(msg:\"Evil Twin 检测 - SSID {ssid} 出现多个BSSID\"; "
            f"type:management, subtype:beacon; "
            f"content:\"{ssid}\"; "
            f"detection_filter:track by_src, count 2, seconds 30; "
            f"sid:1000002; rev:1;)"
        )
        return rule

    @staticmethod
    def generate_rogue_ap_rule(known_bssids):
        """生成 Rogue AP 检测规则"""
        bssid_list = ','.join(known_bssids)
        rule = (
            f"alert wlan any any -> any any "
            f"(msg:\"未授权AP检测 - 未知BSSID\"; "
            f"type:management, subtype:beacon; "
            f"NOT bssid in [{bssid_list}]; "
            f"sid:1000003; rev:1;)"
        )
        return rule

    @staticmethod
    def generate_wps_attack_rule():
        """生成 WPS 攻击检测规则"""
        rule = (
            f"alert wlan any any -> any any "
            f"(msg:\"WPS 暴力破解攻击检测\"; "
            f"content:\"|0d00|\"; "
            f"threshold:type both, track by_src, count 50, seconds 60; "
            f"sid:1000004; rev:1;)"
        )
        return rule

    @staticmethod
    def generate_all_rules(ssid, known_bssids):
        """生成完整 WIDS 规则集"""
        rules = [
            WIDSRuleGenerator.generate_deauth_rule(),
            WIDSRuleGenerator.generate_evil_twin_rule(ssid),
            WIDSRuleGenerator.generate_rogue_ap_rule(known_bssids),
            WIDSRuleGenerator.generate_wps_attack_rule(),
        ]
        return rules


def case4_wifi_audit():
    """案例4: 无线安全审计工具"""

    print("\n" + "=" * 72)
    print("  案例四: 无线安全审计工具")
    print("=" * 72)

    # -------------------------------------------------------------------------
    # 步骤1: 企业 WiFi 配置安全检查
    # -------------------------------------------------------------------------
    print(f"\n[1] 企业 WiFi 配置安全检查")

    # 配置1: 存在多个问题的 WiFi
    bad_config = {
        'ssid': 'CompanyWiFi',
        'bssid': 'AA:BB:CC:11:22:33',
        'encryption': 'WPA2-TKIP',
        'authentication': 'WPA2-PSK',
        'ssid_hidden': False,
        'mac_filter': True,
        'wps_enabled': True,
        'pmf': 'disabled',
        'signal_dbm': -40,
    }

    auditor = WiFiSecurityAuditor(bad_config)
    auditor.run_full_audit()
    report = auditor.generate_report()
    print(report)

    # 配置2: 安全的 WiFi 配置
    print(f"\n{'=' * 65}")
    good_config = {
        'ssid': 'SecureCorp-WiFi',
        'bssid': 'AA:BB:CC:11:22:44',
        'encryption': 'WPA3',
        'authentication': '802.1X',
        'ssid_hidden': False,
        'mac_filter': False,
        'wps_enabled': False,
        'pmf': 'required',
        'signal_dbm': -60,
    }

    auditor2 = WiFiSecurityAuditor(good_config)
    auditor2.run_full_audit()
    report2 = auditor2.generate_report()
    print(report2)

    # -------------------------------------------------------------------------
    # 步骤2: 无线入侵检测规则生成
    # -------------------------------------------------------------------------
    print(f"\n[2] 无线入侵检测规则 (Snort/Suricata 格式)")

    ssid = "CompanyWiFi"
    known_bssids = ['AABBCC112233', 'AABBCC112244']

    rules = WIDSRuleGenerator.generate_all_rules(ssid, known_bssids)
    print(f"\n  --- 规则集 ({len(rules)} 条) ---\n")
    for i, rule in enumerate(rules, 1):
        print(f"  规则 #{i}:")
        print(f"  {rule}\n")

    # -------------------------------------------------------------------------
    # 防御建议
    # -------------------------------------------------------------------------
    print("[防御建议]")
    print("  1. 升级到 WPA3 或 WPA2-CCMP (禁用 TKIP)")
    print("  2. 企业环境使用 802.1X + RADIUS 替代 PSK")
    print("  3. 禁用 WPS 功能")
    print("  4. 强制启用管理帧保护 (PMF)")
    print("  5. 部署 WIDS/WIPS 持续监控无线环境")
    print("  6. 定期进行无线安全渗透测试")
    print("  7. 控制信号覆盖范围 (调整AP功率/定向天线)")
    print("  8. 分离访客网络 (VLAN隔离)")


# ==============================================================================
# 案例五: Zigbee 安全分析
# ==============================================================================
# 原理说明:
#   Zigbee 基于 IEEE 802.15.4 标准, 是低功耗无线 mesh 网络协议,
#   广泛应用于智能家居 (如 Philips Hue, IKEA Tradfri)。
#
#   802.15.4 帧结构:
#     Frame Control (2字节) + Sequence Number (1字节) + Addressing
#     + Security Header + Payload + MAC FCS (2字节)
#
#   Zigbee 安全机制:
#     - AES-128 对称加密 (CCM* 模式)
#     - 网络密钥 (Network Key): 16字节, 用于网络层加密
#     - 链路密钥 (Link Key): 用于传输网络密钥
#     - 帧计数器 (Frame Counter): 防重放保护
#
#   安全等级:
#     0: 无安全 (无加密无认证)
#     1: 仅认证 (MIC, 无加密)
#     2: 加密+认证 (AES-CCM*, 最安全)
#     3: 仅加密 (无认证, 易被篡改)
#
#   攻击面:
#     - 密钥泄露: 默认链路密钥/Zigbee Alliance密钥公开
#     - 重放攻击: 捕获并重放合法命令
#     - 设备克隆: 使用泄露的密钥伪造设备
#     - 密钥拦截: 在配对时捕获网络密钥
# ==============================================================================

class IEEE802154Frame:
    """IEEE 802.15.4 帧解析"""

    # 帧类型
    FRAME_TYPE_BEACON = 0
    FRAME_TYPE_DATA = 1
    FRAME_TYPE_ACK = 2
    FRAME_TYPE_MAC_CMD = 3

    @staticmethod
    def parse(frame_bytes):
        """解析 802.15.4 帧"""
        if len(frame_bytes) < 3:
            return None

        # Frame Control (2字节, 小端)
        fc = struct.unpack('<H', frame_bytes[0:2])[0]
        frame_type = fc & 0x07
        security_enabled = (fc >> 3) & 0x01
        frame_pending = (fc >> 4) & 0x01
        ack_request = (fc >> 5) & 0x01
        panid_compression = (fc >> 6) & 0x01
        dest_addr_mode = (fc >> 10) & 0x03
        src_addr_mode = (fc >> 14) & 0x03

        # Sequence Number (1字节)
        seq_num = frame_bytes[2]

        result = {
            'frame_type': frame_type,
            'security_enabled': security_enabled,
            'frame_pending': frame_pending,
            'ack_request': ack_request,
            'panid_compression': panid_compression,
            'dest_addr_mode': dest_addr_mode,
            'src_addr_mode': src_addr_mode,
            'seq_num': seq_num,
        }

        type_names = {0: 'Beacon', 1: 'Data', 2: 'ACK', 3: 'MAC Command'}
        result['type_name'] = type_names.get(frame_type, f'Unknown({frame_type})')

        offset = 3

        # 目标 PAN ID (2字节)
        if dest_addr_mode > 0:
            result['dest_panid'] = struct.unpack('<H', frame_bytes[offset:offset+2])[0]
            offset += 2

        # 目标地址 (短地址2字节 或 扩展地址8字节)
        if dest_addr_mode == 2:  # 短地址
            result['dest_addr'] = frame_bytes[offset:offset+2]
            offset += 2
        elif dest_addr_mode == 3:  # 扩展地址
            result['dest_addr'] = frame_bytes[offset:offset+8]
            offset += 8

        # 源 PAN ID (如果未压缩)
        if src_addr_mode > 0 and not panid_compression:
            result['src_panid'] = struct.unpack('<H', frame_bytes[offset:offset+2])[0]
            offset += 2

        # 源地址
        if src_addr_mode == 2:
            result['src_addr'] = frame_bytes[offset:offset+2]
            offset += 2
        elif src_addr_mode == 3:
            result['src_addr'] = frame_bytes[offset:offset+8]
            offset += 8

        # 安全头部 (如果启用安全)
        if security_enabled:
            result['security_header'] = IEEE802154Frame._parse_security_header(
                frame_bytes, offset
            )
            offset += 14  # 安全头部固定14字节

        # Payload
        result['payload'] = frame_bytes[offset:-2]  # 去掉最后2字节FCS

        return result

    @staticmethod
    def _parse_security_header(data, offset):
        """解析安全头部"""
        if offset + 14 > len(data):
            return None

        # Security Control (1字节)
        sec_ctrl = data[offset]
        security_level = sec_ctrl & 0x07
        key_id_mode = (sec_ctrl >> 3) & 0x03

        # Frame Counter (4字节)
        frame_counter = struct.unpack('<I', data[offset+1:offset+5])[0]

        # Key Identifier (变长, 取决于 key_id_mode)
        key_id = data[offset+5:offset+14]

        level_names = {0: 'None', 1: 'MIC-32', 2: 'MIC-64',
                       3: 'MIC-128', 4: 'ENC', 5: 'ENC+MIC-32',
                       6: 'ENC+MIC-64', 7: 'ENC+MIC-128'}

        return {
            'security_level': security_level,
            'security_level_name': level_names.get(security_level, 'Unknown'),
            'key_id_mode': key_id_mode,
            'frame_counter': frame_counter,
            'key_id': key_id.hex(),
        }


class ZigbeeSecurityAnalyzer:
    """Zigbee 安全分析"""

    # Zigbee 默认链路密钥 (Zigbee Alliance 密钥 - 公开已知!)
    DEFAULT_LINK_KEY = bytes.fromhex('5A6967426565416C6C69616E63653039')

    def __init__(self):
        self.network_key = os.urandom(16)  # 模拟网络密钥
        self.devices = {}  # 设备注册表
        self.frame_log = []  # 帧日志

    def simulate_key_transport(self, device_id, link_key=None):
        """
        模拟网络密钥传输过程
        使用链路密钥加密传输网络密钥
        """
        if link_key is None:
            link_key = self.DEFAULT_LINK_KEY  # 使用默认密钥 (不安全!)

        # 模拟 AES-CCM* 加密
        # 真实场景: 使用 link_key 对 network_key 加密
        encrypted_nk = self._aes_ccm_encrypt(link_key, self.network_key)
        return encrypted_nk

    def _aes_ccm_encrypt(self, key, plaintext):
        """模拟 AES-CCM* 加密 (简化)"""
        # 真实场景使用 AES-128-CCM*
        # 这里用 HMAC-SHA256 模拟 (仅用于演示)
        nonce = os.urandom(13)
        mac = hmac.new(key, nonce + plaintext, hashlib.sha256).digest()[:16]
        encrypted = bytes(a ^ b for a, b in zip(plaintext, mac))
        return nonce + encrypted + mac

    def _aes_ccm_decrypt(self, key, ciphertext):
        """模拟 AES-CCM* 解密"""
        if len(ciphertext) < 29:
            return None
        nonce = ciphertext[:13]
        encrypted = ciphertext[13:29]
        mac = ciphertext[29:45]
        decrypted = bytes(a ^ b for a, b in zip(encrypted, mac))
        return decrypted

    def capture_key_transport(self, device_id):
        """拦截密钥传输 (需要知道链路密钥)"""
        encrypted = self.simulate_key_transport(device_id)
        # 如果使用默认链路密钥, 可以直接解密
        recovered_key = self._aes_ccm_decrypt(self.DEFAULT_LINK_KEY, encrypted)
        return recovered_key

    def clone_device(self, device_id, network_key):
        """设备克隆攻击模拟"""
        cloned = {
            'device_id': device_id,
            'network_key': network_key.hex(),
            'cloned': True,
        }
        self.devices[device_id + '_clone'] = cloned
        return cloned

    def analyze_security_level(self, sec_level):
        """分析安全等级"""
        levels = {
            0: {'name': 'None', 'risk': '极高', 'desc': '无加密无认证, 完全暴露'},
            1: {'name': 'MIC-32', 'risk': '中', 'desc': '仅32位认证, 无加密'},
            2: {'name': 'MIC-64', 'risk': '中低', 'desc': '仅64位认证, 无加密'},
            3: {'name': 'MIC-128', 'risk': '低', 'desc': '仅128位认证, 无加密'},
            4: {'name': 'ENC', 'risk': '中', 'desc': '仅加密, 无认证 (可篡改)'},
            5: {'name': 'ENC+MIC-32', 'risk': '低', 'desc': '加密+32位认证'},
            6: {'name': 'ENC+MIC-64', 'risk': '低', 'desc': '加密+64位认证'},
            7: {'name': 'ENC+MIC-128', 'risk': '安全', 'desc': 'AES-CCM* 完整加密+认证'},
        }
        return levels.get(sec_level, {'name': 'Unknown', 'risk': '未知', 'desc': ''})


def generate_sample_802154_frames():
    """生成模拟 802.15.4 帧"""

    pan_id = 0x1234
    src_addr = b'\x01\x02'
    dst_addr = b'\xFF\xFF'  # 广播

    frames = []

    # 帧1: 无加密 Beacon 帧
    beacon = bytearray()
    fc = (IEEE802154Frame.FRAME_TYPE_BEACON |  # 类型: Beacon
          (2 << 10) | (2 << 14))  # 目标/源地址模式: 短地址
    beacon.extend(struct.pack('<H', fc))
    beacon.extend(bytes([1]))       # Sequence Number
    beacon.extend(struct.pack('<H', pan_id))
    beacon.extend(dst_addr)
    beacon.extend(struct.pack('<H', pan_id))
    beacon.extend(src_addr)
    beacon.extend(b'\x00' * 4)      # Superframe spec
    beacon.extend(b'HELLO')         # Payload
    beacon.extend(b'\x00\x00')      # FCS (简化)
    frames.append(('Beacon (无安全)', bytes(beacon)))

    # 帧2: 加密数据帧
    data_frame = bytearray()
    fc = (IEEE802154Frame.FRAME_TYPE_DATA |     # 类型: Data
          (1 << 3) |                             # Security Enabled
          (1 << 5) |                             # ACK Request
          (1 << 6) |                             # PAN ID Compression
          (2 << 10) | (2 << 14))                # 短地址模式
    data_frame.extend(struct.pack('<H', fc))
    data_frame.extend(bytes([2]))                # Sequence Number
    data_frame.extend(struct.pack('<H', pan_id))
    data_frame.extend(dst_addr)
    data_frame.extend(src_addr)

    # 安全头部
    sec_ctrl = 7 | (2 << 3)  # Security Level 7 (ENC+MIC-128), Key ID Mode 2
    data_frame.extend(bytes([sec_ctrl]))
    data_frame.extend(struct.pack('<I', 100))    # Frame Counter
    data_frame.extend(b'\x01\x00\x01\x00')      # Key Source
    data_frame.extend(bytes([0x01]))             # Key Index

    # 加密 Payload (模拟)
    data_frame.extend(b'\xAA\xBB\xCC\xDD')      # Encrypted data
    data_frame.extend(b'\x00' * 16)              # MIC (模拟)
    data_frame.extend(b'\x00\x00')               # FCS
    frames.append(('Data (加密+认证)', bytes(data_frame)))

    return frames


def case5_zigbee():
    """案例5: Zigbee 安全分析"""

    print("\n" + "=" * 72)
    print("  案例五: Zigbee 安全分析")
    print("=" * 72)

    # -------------------------------------------------------------------------
    # 步骤1: 802.15.4 帧解析
    # -------------------------------------------------------------------------
    print(f"\n[1] 802.15.4 帧解析")

    frames = generate_sample_802154_frames()
    for name, frame_data in frames:
        parsed = IEEE802154Frame.parse(frame_data)
        if parsed:
            print(f"\n    --- {name} ---")
            print(f"    帧类型:       {parsed['type_name']}")
            print(f"    序列号:       {parsed['seq_num']}")
            print(f"    安全启用:     {'是' if parsed['security_enabled'] else '否'}")
            if 'src_addr' in parsed:
                print(f"    源地址:       {parsed['src_addr'].hex()}")
            if 'dest_addr' in parsed:
                print(f"    目标地址:     {parsed['dest_addr'].hex()}")
            if parsed['security_enabled']:
                sh = parsed['security_header']
                print(f"    安全等级:     {sh['security_level']} ({sh['security_level_name']})")
                print(f"    帧计数器:     {sh['frame_counter']}")
                print(f"    密钥ID模式:   {sh['key_id_mode']}")

    # -------------------------------------------------------------------------
    # 步骤2: 网络密钥提取模拟
    # -------------------------------------------------------------------------
    print(f"\n[2] Zigbee 网络密钥提取模拟")

    analyzer = ZigbeeSecurityAnalyzer()

    # 使用默认链路密钥传输网络密钥
    print(f"    网络密钥:     {analyzer.network_key.hex()}")
    print(f"    默认链路密钥: {analyzer.DEFAULT_LINK_KEY.hex()} (Zigbee Alliance 公开密钥)")
    print(f"    风险: 默认链路密钥已公开, 任何人可解密密钥传输!")

    # 模拟拦截密钥传输
    recovered_key = analyzer.capture_key_transport('device_001')
    print(f"\n    拦截并解密网络密钥:")
    print(f"    恢复的密钥:   {recovered_key.hex()[:32]}...")
    match = (recovered_key[:16] == analyzer.network_key)
    print(f"    验证: {'匹配!' if match else '不匹配'}")

    # -------------------------------------------------------------------------
    # 步骤3: 设备克隆攻击模拟
    # -------------------------------------------------------------------------
    print(f"\n[3] 设备克隆攻击模拟")

    cloned = analyzer.clone_device('smart_light_01', analyzer.network_key)
    print(f"    原始设备ID: smart_light_01")
    print(f"    克隆设备ID: {cloned['device_id']}_clone")
    print(f"    使用网络密钥: {cloned['network_key'][:32]}...")
    print(f"    克隆设备可: 发送伪造命令/控制设备/加入网络")

    # -------------------------------------------------------------------------
    # 步骤4: 安全等级分析
    # -------------------------------------------------------------------------
    print(f"\n[4] 安全等级分析")

    for level in range(8):
        analysis = analyzer.analyze_security_level(level)
        print(f"    等级 {level}: {analysis['name']:<16s} "
              f"风险: {analysis['risk']:<6s} {analysis['desc']}")

    # -------------------------------------------------------------------------
    # 步骤5: 综合安全分析
    # -------------------------------------------------------------------------
    print(f"\n[5] Zigbee 安全综合评估")

    print(f"""
    常见 Zigbee 设备安全风险:
    1. 使用默认链路密钥 (Zigbee Alliance Key 已公开)
    2. 密钥传输未使用唯一链路密钥加密
    3. 帧计数器溢出后重置 (重放攻击窗口)
    4. 部分设备安全等级配置过低 (Level 0/4)
    5. 触摸配对 (Touchlink) 未做距离限制
    6. 网络密钥在设备加入时明文传输 (若链路密钥已知)
    """)

    # -------------------------------------------------------------------------
    # 防御建议
    # -------------------------------------------------------------------------
    print("[防御建议]")
    print("  1. 使用唯一链路密钥 (不使用默认 Zigbee Alliance Key)")
    print("  2. 配置安全等级为 7 (ENC+MIC-128, 最安全)")
    print("  3. 启用帧计数器防重放保护")
    print("  4. 配对过程在安全环境中进行 (避免被窃听)")
    print("  5. 限制 Touchlink 配对距离")
    print("  6. 定期更新网络密钥")
    print("  7. 使用硬件安全模块 (HSM) 保护密钥")
    print("  8. 监控异常设备加入和命令模式")


# ==============================================================================
# 主函数
# ==============================================================================

def main():
    """主函数: 运行所有实战案例"""

    print("=" * 72)
    print("  无线网络安全 - 攻防实战案例集")
    print("  面向安全学习者 | 仅用于授权安全测试")
    print("=" * 72)

    # 运行五个案例
    case1_wifi_penetration()   # WiFi 渗透测试全流程
    case2_evil_twin()         # Evil Twin 攻击模拟
    case3_ble()               # BLE 设备扫描与攻击
    case4_wifi_audit()        # 无线安全审计工具
    case5_zigbee()            # Zigbee 安全分析

    print("\n" + "=" * 72)
    print("  所有案例执行完毕!")
    print("  提示: 每个案例包含协议分析、攻击模拟和防御建议")
    print("  进一步学习: 安装 scapy, 使用真实抓包文件实践")
    print("=" * 72)


if __name__ == '__main__':
    main()
