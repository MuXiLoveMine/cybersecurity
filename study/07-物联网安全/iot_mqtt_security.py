#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MQTT 安全测试工具 (MQTT Security Testing Tool)

功能：
    1. MQTT 连接测试 - 测试目标 MQTT Broker 是否可连接
    2. 匿名访问检测 - 检测是否允许匿名（无认证）连接
    3. 弱口令检测 - 使用常见弱口令进行暴力破解
    4. 主题嗅探 - 通过订阅常见主题和通配符发现有效主题
    5. 消息篡改测试 - 测试是否可以向敏感主题发布消息
    6. TLS 配置检测 - 检测 TLS 版本、加密套件等配置

使用方法：
    python iot_mqtt_security.py -t <目标IP> -p <端口> [选项]

依赖安装：
    pip install paho-mqtt

注意：
    本工具仅供学习和授权测试使用，严禁用于未授权的测试！
"""

import argparse
import socket
import ssl
import sys
import time
import threading
import json
from datetime import datetime

# 尝试导入 paho-mqtt 库
try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("[!] 缺少 paho-mqtt 库，请先安装：pip install paho-mqtt")
    sys.exit(1)


# ============================================================
# 全局配置
# ============================================================

# 常见弱口令字典（用户名:密码 组合）
# 参考 Mirai 僵尸网络使用的默认口令列表
DEFAULT_CREDENTIALS = [
    ("admin", "admin"),
    ("admin", "password"),
    ("admin", "12345"),
    ("admin", "123456"),
    ("admin", "admin123"),
    ("admin", ""),  # 空密码
    ("root", "root"),
    ("root", "password"),
    ("root", "123456"),
    ("root", "admin"),
    ("root", ""),
    ("user", "user"),
    ("user", "password"),
    ("guest", "guest"),
    ("guest", "guest123"),
    ("mqtt", "mqtt"),
    ("mqtt", "password"),
    ("test", "test"),
    ("test", "test123"),
    ("mosquitto", "mosquitto"),
    ("device", "device"),
    ("sensor", "sensor"),
    ("default", "default"),
    ("iot", "iot"),
    ("iot", "iot123"),
]

# 常见主题列表（用于主题嗅探）
# 涵盖智能家居、工业物联网、传感器等常见场景
COMMON_TOPICS = [
    # 通用主题
    "#",
    "+/status",
    "+/command",
    "+/data",
    "+/config",
    "test",
    "test/#",
    "hello",
    "mqtt",
    "$SYS/#",
    "$SYS/broker/clients/total",
    # 传感器相关
    "sensors/+",
    "sensors/+/temperature",
    "sensors/+/humidity",
    "sensors/+/pressure",
    "sensors/+/light",
    "sensors/+/motion",
    "sensor/+",
    "sensor/+/value",
    # 设备相关
    "devices/+",
    "devices/+/status",
    "devices/+/command",
    "devices/+/online",
    "device/+/status",
    "device/+/data",
    # 智能家居
    "home/+/status",
    "home/+/control",
    "home/light/+",
    "home/temperature",
    "smart/+",
    "smart/+/status",
    # 工业相关
    "factory/+",
    "factory/+/sensor",
    "plc/+/status",
    "plc/+/data",
    "industrial/+",
    # 告警相关
    "alarm",
    "alarms/+",
    "alert/+",
    "notification/+",
    # 固件更新
    "firmware/update",
    "firmware/+/update",
    "ota/+/status",
    # 系统管理
    "admin/+",
    "config/+",
    "server/+",
    "broker/+",
]


# ============================================================
# 工具类
# ============================================================

class MQTTScanner:
    """
    MQTT 安全扫描器类

    封装了各种 MQTT 安全测试功能
    """

    def __init__(self, target, port=1883, timeout=5, verbose=False):
        """
        初始化扫描器

        参数:
            target: 目标 MQTT Broker 的 IP 地址或域名
            port: MQTT Broker 端口号，默认 1883
            timeout: 连接超时时间（秒），默认 5 秒
            verbose: 是否显示详细输出
        """
        self.target = target
        self.port = port
        self.timeout = timeout
        self.verbose = verbose
        self.discovered_topics = []  # 存储发现的有效主题
        self.received_messages = []  # 存储接收到的消息
        self._lock = threading.Lock()  # 线程锁

    def _print(self, level, message):
        """
        格式化输出信息

        参数:
            level: 信息级别（INFO/WARN/ERROR/SUCCESS/DEBUG）
            message: 要输出的消息内容
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_prefix = {
            "INFO": "[*]",
            "WARN": "[!]",
            "ERROR": "[-]",
            "SUCCESS": "[+]",
            "DEBUG": "[DEBUG]",
        }
        prefix = color_prefix.get(level, "[*]")

        if level == "DEBUG" and not self.verbose:
            return

        print(f"{prefix} [{timestamp}] {message}")

    # ============================================================
    # 功能 1：端口连通性测试
    # ============================================================

    def test_port_connectivity(self):
        """
        测试目标端口是否开放（TCP 连接测试）

        返回:
            bool: 端口是否开放
        """
        self._print("INFO", f"正在测试 {self.target}:{self.port} 的 TCP 连通性...")

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, self.port))
            sock.close()

            if result == 0:
                self._print("SUCCESS", f"端口 {self.port} 开放，TCP 连接成功")
                return True
            else:
                self._print("ERROR", f"端口 {self.port} 未开放或被防火墙拦截")
                return False
        except socket.error as e:
            self._print("ERROR", f"连接失败: {e}")
            return False

    # ============================================================
    # 功能 2：匿名访问检测
    # ============================================================

    def test_anonymous_access(self):
        """
        检测 MQTT Broker 是否允许匿名访问（不提供用户名和密码）

        返回:
            bool: 是否允许匿名访问
        """
        self._print("INFO", "正在检测匿名访问...")

        # 创建 MQTT 客户端（不设置用户名和密码）
        client = mqtt.Client(
            client_id=f"anon_test_{int(time.time())}",
            clean_session=True
        )

        # 存储连接结果的字典
        result = {"connected": False, "return_code": -1}

        # 定义连接回调函数
        def on_connect(client, userdata, flags, rc):
            """
            连接完成回调

            参数:
                rc: 返回码
                    0 = 连接成功
                    1 = 协议版本错误
                    2 = 客户端标识符无效
                    3 = 服务器不可用
                    4 = 用户名或密码错误
                    5 = 未授权
            """
            result["return_code"] = rc
            if rc == 0:
                result["connected"] = True

        client.on_connect = on_connect

        try:
            # 连接到 Broker（不提供用户名密码）
            client.connect(self.target, self.port, keepalive=10)
            # 处理网络事件，等待回调
            client.loop(timeout=self.timeout)
            # 等待一小段时间确保回调完成
            time.sleep(1)
            client.loop(timeout=1)
            client.disconnect()
        except Exception as e:
            self._print("ERROR", f"匿名连接测试失败: {e}")
            return False

        # 根据返回码判断结果
        rc = result["return_code"]
        rc_messages = {
            0: "连接成功",
            1: "协议版本错误",
            2: "客户端标识符无效",
            3: "服务器不可用",
            4: "用户名或密码错误",
            5: "未授权",
        }

        if rc == 0:
            self._print("SUCCESS", "检测到匿名访问！Broker 允许未认证连接")
            self._print("WARN", "风险：任何人都可以连接到 Broker 并发布/订阅消息")
            return True
        elif rc == 5:
            self._print("INFO", "匿名访问被拒绝（返回码 5：未授权）")
            self._print("SUCCESS", "Broker 配置了认证机制，不允许匿名访问")
            return False
        else:
            msg = rc_messages.get(rc, f"未知返回码: {rc}")
            self._print("INFO", f"连接结果: {msg} (返回码: {rc})")
            return False

    # ============================================================
    # 功能 3：弱口令检测（暴力破解）
    # ============================================================

    def test_weak_password(self, credentials=None, delay=0.1):
        """
        使用常见弱口令进行暴力破解测试

        参数:
            credentials: 用户名密码列表，格式 [(username, password), ...]
                        如果为 None 则使用默认字典
            delay: 每次尝试之间的延迟（秒），防止触发频率限制

        返回:
            list: 发现的有效凭证列表 [(username, password), ...]
        """
        if credentials is None:
            credentials = DEFAULT_CREDENTIALS

        self._print("INFO", f"开始弱口令检测，共 {len(credentials)} 个凭证组合")
        found_credentials = []

        for username, password in credentials:
            # 创建新的客户端实例
            client = mqtt.Client(
                client_id=f"brute_{username}_{int(time.time())}",
                clean_session=True
            )

            result = {"success": False, "rc": -1}

            def on_connect(client, userdata, flags, rc, result=result):
                result["rc"] = rc
                if rc == 0:
                    result["success"] = True

            client.on_connect = on_connect

            try:
                # 设置用户名和密码
                client.username_pw_set(username, password)
                # 尝试连接
                client.connect(self.target, self.port, keepalive=10)
                client.loop(timeout=self.timeout)
                time.sleep(0.5)
                client.loop(timeout=0.5)
                client.disconnect()
            except Exception as e:
                self._print("DEBUG", f"连接 {username}/{password} 时出错: {e}")

            if result["success"]:
                self._print("SUCCESS", f"发现有效凭证: {username} / {password}")
                found_credentials.append((username, password))
            else:
                self._print("DEBUG", f"凭证失败: {username} / {password}")

            # 延迟，防止触发频率限制或被检测到
            time.sleep(delay)

        if found_credentials:
            self._print("WARN", f"共发现 {len(found_credentials)} 个弱口令凭证")
            self._print("WARN", "风险：攻击者可通过弱口令获取 Broker 访问权限")
        else:
            self._print("SUCCESS", "未发现弱口令（测试字典范围内）")

        return found_credentials

    # ============================================================
    # 功能 4：主题嗅探
    # ============================================================

    def _on_message_sniff(self, client, userdata, msg):
        """
        主题嗅探的消息回调函数

        当接收到订阅的消息时调用，记录发现的主题和消息内容

        参数:
            msg: MQTT 消息对象，包含 topic 和 payload
        """
        topic = msg.topic
        payload = msg.payload[:200]  # 只截取前 200 字节，避免输出过长

        # 线程安全地添加到发现列表
        with self._lock:
            if topic not in self.discovered_topics:
                self.discovered_topics.append(topic)
                self._print("SUCCESS", f"发现新主题: {topic}")
                # 尝试解码消息内容
                try:
                    payload_str = payload.decode('utf-8', errors='replace')
                    self._print("INFO", f"  消息内容: {payload_str}")
                except Exception:
                    self._print("INFO", f"  消息内容(二进制): {payload.hex()}")

    def sniff_topics(self, username=None, password=None, duration=30, topics=None):
        """
        主题嗅探 - 订阅常见主题，监听消息以发现活跃主题

        参数:
            username: 认证用户名（可选）
            password: 认证密码（可选）
            duration: 嗅探持续时间（秒），默认 30 秒
            topics: 要订阅的主题列表，如果为 None 则使用默认列表

        返回:
            list: 发现的有效主题列表
        """
        if topics is None:
            topics = COMMON_TOPICS

        auth_info = f" (用户: {username})" if username else " (匿名)"
        self._print("INFO", f"开始主题嗅探，持续 {duration} 秒{auth_info}")
        self._print("INFO", f"将尝试订阅 {len(topics)} 个常见主题")

        # 重置发现列表
        self.discovered_topics = []

        # 创建客户端
        client = mqtt.Client(
            client_id=f"sniff_{int(time.time())}",
            clean_session=True
        )

        # 设置认证（如果提供）
        if username:
            client.username_pw_set(username, password)

        # 设置消息回调
        client.on_message = self._on_message_sniff

        # 连接回调
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                self._print("DEBUG", "连接成功，开始订阅主题...")
                # 订阅所有主题
                for topic in topics:
                    # 使用 QoS 0 以减少开销
                    client.subscribe(topic, qos=0)
                    self._print("DEBUG", f"已订阅: {topic}")
            else:
                self._print("ERROR", f"连接失败，返回码: {rc}")

        client.on_connect = on_connect

        try:
            client.connect(self.target, self.port, keepalive=60)
        except Exception as e:
            self._print("ERROR", f"连接失败: {e}")
            return []

        # 启动网络循环（后台线程）
        client.loop_start()

        # 等待订阅完成
        time.sleep(2)

        # 等待指定的嗅探时间
        self._print("INFO", f"正在监听消息，等待 {duration} 秒...")
        time.sleep(duration)

        # 停止循环并断开连接
        client.loop_stop()
        client.disconnect()

        # 输出结果
        if self.discovered_topics:
            self._print("SUCCESS", f"共发现 {len(self.discovered_topics)} 个活跃主题:")
            for i, topic in enumerate(self.discovered_topics, 1):
                self._print("INFO", f"  {i}. {topic}")
        else:
            self._print("INFO", "未发现活跃主题（可能没有消息发布或权限不足）")

        return self.discovered_topics

    # ============================================================
    # 功能 5：消息篡改测试（发布权限测试）
    # ============================================================

    def test_publish_permission(self, username=None, password=None, test_topics=None):
        """
        测试向指定主题发布消息的权限

        参数:
            username: 认证用户名（可选）
            password: 认证密码（可选）
            test_topics: 要测试的主题列表，如果为 None 则使用默认列表

        返回:
            dict: 测试结果字典 {topic: True/False}
        """
        if test_topics is None:
            test_topics = [
                "test/security_test",
                "sensors/test/temperature",
                "devices/test/status",
                "admin/test",
                "config/test",
            ]

        auth_info = f" (用户: {username})" if username else " (匿名)"
        self._print("INFO", f"开始发布权限测试{auth_info}")

        results = {}

        for topic in test_topics:
            client = mqtt.Client(
                client_id=f"pub_test_{int(time.time())}",
                clean_session=True
            )

            # 存储发布结果
            pub_result = {"published": False}

            # 发布回调
            def on_publish(client, userdata, mid, result=pub_result):
                result["published"] = True

            client.on_publish = on_publish

            # 连接回调
            def on_connect(client, userdata, flags, rc):
                if rc == 0:
                    # 连接成功，发布测试消息
                    test_message = f"security_test_{int(time.time())}"
                    client.publish(topic, test_message, qos=0, retain=False)
                    self._print("DEBUG", f"已向 {topic} 发布测试消息")

            client.on_connect = on_connect

            # 设置认证
            if username:
                client.username_pw_set(username, password)

            try:
                client.connect(self.target, self.port, keepalive=10)
                client.loop(timeout=3)
                time.sleep(1)
                client.loop(timeout=2)
                client.disconnect()
            except Exception as e:
                self._print("DEBUG", f"发布测试 {topic} 时出错: {e}")

            # 检查是否发布成功
            if pub_result["published"]:
                results[topic] = True
                self._print("SUCCESS", f"可以发布到主题: {topic}")
            else:
                results[topic] = False
                self._print("DEBUG", f"无法发布到主题: {topic}（可能无权限或连接失败）")

        # 统计结果
        success_count = sum(1 for v in results.values() if v)
        self._print("INFO", f"发布权限测试完成: {success_count}/{len(results)} 个主题可发布")

        if success_count > 0:
            self._print("WARN", "风险：攻击者可向敏感主题发布恶意消息，控制设备或注入虚假数据")

        return results

    # ============================================================
    # 功能 6：TLS 配置检测
    # ============================================================

    def test_tls_config(self, tls_port=8883):
        """
        检测 MQTT over TLS 的配置安全性

        包括：TLS 版本、加密套件、证书验证等

        参数:
            tls_port: TLS 端口，默认 8883

        返回:
            dict: TLS 配置信息
        """
        self._print("INFO", f"正在检测 TLS 配置 (端口 {tls_port})...")

        tls_info = {
            "tls_enabled": False,
            "tls_version": None,
            "cipher": None,
            "certificate": None,
            "cert_verified": False,
            "weak_config": [],
        }

        # 首先测试 TLS 端口是否开放
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((self.target, tls_port))
            sock.close()

            if result != 0:
                self._print("WARN", f"TLS 端口 {tls_port} 未开放")
                self._print("WARN", "风险：Broker 可能未启用 TLS，数据以明文传输")
                return tls_info
        except Exception as e:
            self._print("ERROR", f"TLS 端口测试失败: {e}")
            return tls_info

        tls_info["tls_enabled"] = True
        self._print("SUCCESS", f"TLS 端口 {tls_port} 开放")

        # 测试不同的 TLS 版本
        tls_versions = [
            ("TLS 1.3", ssl.PROTOCOL_TLS_CLIENT),
            ("TLS 1.2", ssl.PROTOCOL_TLSv1_2),
            ("TLS 1.1", ssl.PROTOCOL_TLSv1_1 if hasattr(ssl, "PROTOCOL_TLSv1_1") else None),
            ("TLS 1.0", ssl.PROTOCOL_TLSv1 if hasattr(ssl, "PROTOCOL_TLSv1") else None),
            ("SSLv3", ssl.PROTOCOL_SSLv3 if hasattr(ssl, "PROTOCOL_SSLv3") else None),
        ]

        supported_versions = []

        for version_name, version_const in tls_versions:
            if version_const is None:
                continue

            try:
                context = ssl.SSLContext(version_const)
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE

                with socket.create_connection((self.target, tls_port), timeout=self.timeout) as sock:
                    with context.wrap_socket(sock, server_hostname=self.target) as ssock:
                        supported_versions.append(version_name)
                        self._print("INFO", f"支持 {version_name}")

                        # 记录第一次成功的版本信息
                        if tls_info["tls_version"] is None:
                            tls_info["tls_version"] = ssock.version()
                            tls_info["cipher"] = ssock.cipher()
                            # 获取证书
                            try:
                                cert = ssock.getpeercert(binary_form=False)
                                tls_info["certificate"] = cert
                            except Exception:
                                pass

                        break  # 找到最高支持的版本即可
            except ssl.SSLError as e:
                self._print("DEBUG", f"不支持 {version_name}: {e}")
            except Exception as e:
                self._print("DEBUG", f"{version_name} 测试失败: {e}")

        # 输出 TLS 版本信息
        if tls_info["tls_version"]:
            self._print("SUCCESS", f"协商 TLS 版本: {tls_info['tls_version']}")
            self._print("INFO", f"加密套件: {tls_info['cipher'][0]}")

        # 检查弱版本
        weak_versions = ["SSLv3", "TLS 1.0", "TLS 1.1"]
        for wv in weak_versions:
            if wv in supported_versions:
                tls_info["weak_config"].append(f"支持弱版本 {wv}")
                self._print("WARN", f"风险：支持 {wv}（存在安全漏洞，建议仅启用 TLS 1.2+）")

        # 测试证书验证（检查是否使用自签名证书）
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.target, tls_port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=self.target) as ssock:
                    tls_info["cert_verified"] = True
                    self._print("SUCCESS", "证书验证通过（受信任的 CA 签发）")
        except ssl.SSLCertVerificationError as e:
            tls_info["cert_verified"] = False
            tls_info["weak_config"].append("证书验证失败（可能是自签名证书）")
            self._print("WARN", f"证书验证失败: {e}")
            self._print("WARN", "风险：可能使用自签名证书，客户端易受中间人攻击")
        except Exception as e:
            self._print("DEBUG", f"证书验证测试出错: {e}")

        # 测试是否支持弱加密套件
        # （简化测试，实际应测试更多套件）
        weak_ciphers = ["DES", "RC4", "3DES", "NULL", "EXPORT", "MD5"]
        if tls_info["cipher"]:
            cipher_name = tls_info["cipher"][0].upper()
            for wc in weak_ciphers:
                if wc in cipher_name:
                    tls_info["weak_config"].append(f"使用弱加密套件 {cipher_name}")
                    self._print("WARN", f"风险：使用弱加密套件 {cipher_name}")
                    break

        if not tls_info["weak_config"]:
            self._print("SUCCESS", "TLS 配置看起来安全（未发现明显弱配置）")

        return tls_info

    # ============================================================
    # 功能 7：MQTT 服务版本/指纹识别
    # ============================================================

    def fingerprint_broker(self):
        """
        通过各种特征识别 MQTT Broker 的类型和版本

        返回:
            dict: Broker 指纹信息
        """
        self._print("INFO", "正在进行 Broker 指纹识别...")

        fingerprint = {
            "broker_type": "Unknown",
            "version": "Unknown",
            "features": [],
        }

        # 方法 1：通过 $SYS 主题获取信息（Mosquitto 等 Broker 支持）
        client = mqtt.Client(
            client_id=f"fingerprint_{int(time.time())}",
            clean_session=True
        )

        sys_info = {}

        def on_message(client, userdata, msg):
            topic = msg.topic
            try:
                value = msg.payload.decode('utf-8', errors='replace')
                sys_info[topic] = value
            except Exception:
                pass

        client.on_message = on_message

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                # 订阅常见的 $SYS 主题
                sys_topics = [
                    "$SYS/broker/version",
                    "$SYS/broker/uptime",
                    "$SYS/broker/clients/total",
                    "$SYS/broker/load/bytes/sent",
                ]
                for topic in sys_topics:
                    client.subscribe(topic, qos=0)

        client.on_connect = on_connect

        try:
            client.connect(self.target, self.port, keepalive=10)
            client.loop_start()
            time.sleep(3)  # 等待收集信息
            client.loop_stop()
            client.disconnect()
        except Exception as e:
            self._print("DEBUG", f"$SYS 主题获取失败: {e}")

        # 分析 $SYS 信息
        if "$SYS/broker/version" in sys_info:
            version_str = sys_info["$SYS/broker/version"]
            fingerprint["version"] = version_str
            self._print("SUCCESS", f"Broker 版本: {version_str}")

            if "mosquitto" in version_str.lower():
                fingerprint["broker_type"] = "Mosquitto"
            elif "emqx" in version_str.lower():
                fingerprint["broker_type"] = "EMQX"
            elif "hivemq" in version_str.lower():
                fingerprint["broker_type"] = "HiveMQ"
            elif "activemq" in version_str.lower():
                fingerprint["broker_type"] = "ActiveMQ"

        if sys_info:
            self._print("INFO", "获取到的 $SYS 信息:")
            for topic, value in list(sys_info.items())[:10]:  # 只显示前 10 个
                self._print("INFO", f"  {topic} = {value[:50]}")

        # 方法 2：通过 CONNACK 中的标志位判断
        # （不同 Broker 的行为可能略有不同）
        self._print("INFO", f"Broker 类型推测: {fingerprint['broker_type']}")

        return fingerprint

    # ============================================================
    # 综合扫描
    # ============================================================

    def full_scan(self, username=None, password=None, tls_port=8883):
        """
        执行完整的安全扫描

        参数:
            username: 用于认证测试的用户名（可选）
            password: 用于认证测试的密码（可选）
            tls_port: TLS 端口

        返回:
            dict: 完整扫描结果
        """
        self._print("INFO", "=" * 60)
        self._print("INFO", f"开始 MQTT 安全扫描 - 目标: {self.target}:{self.port}")
        self._print("INFO", "=" * 60)

        results = {
            "target": f"{self.target}:{self.port}",
            "scan_time": datetime.now().isoformat(),
            "port_open": False,
            "anonymous_access": False,
            "weak_credentials": [],
            "discovered_topics": [],
            "publish_permissions": {},
            "tls_info": {},
            "fingerprint": {},
            "vulnerabilities": [],
        }

        # 1. 端口连通性测试
        print()
        if not self.test_port_connectivity():
            self._print("ERROR", "端口未开放，终止扫描")
            return results

        results["port_open"] = True

        # 2. 指纹识别
        print()
        results["fingerprint"] = self.fingerprint_broker()

        # 3. 匿名访问检测
        print()
        anon_access = self.test_anonymous_access()
        results["anonymous_access"] = anon_access
        if anon_access:
            results["vulnerabilities"].append({
                "severity": "高危",
                "name": "匿名访问",
                "description": "MQTT Broker 允许未认证的匿名连接",
                "risk": "攻击者可以匿名连接并发布/订阅消息，获取敏感数据或控制设备",
                "fix": "禁用匿名访问，启用用户名密码认证或证书认证",
            })

            # 如果允许匿名，直接用匿名进行主题嗅探
            print()
            results["discovered_topics"] = self.sniff_topics(duration=20)

            # 测试发布权限
            print()
            results["publish_permissions"] = self.test_publish_permission()
            if any(results["publish_permissions"].values()):
                results["vulnerabilities"].append({
                    "severity": "高危",
                    "name": "匿名发布权限",
                    "description": "匿名用户可以向主题发布消息",
                    "risk": "攻击者可发布恶意消息控制设备或注入虚假数据",
                    "fix": "配置 ACL，限制匿名用户的发布权限",
                })

        else:
            # 4. 弱口令检测
            print()
            weak_creds = self.test_weak_password()
            results["weak_credentials"] = weak_creds
            if weak_creds:
                results["vulnerabilities"].append({
                    "severity": "高危",
                    "name": "弱口令",
                    "description": f"发现 {len(weak_creds)} 个弱口令凭证",
                    "risk": "攻击者可通过弱口令获取 Broker 访问权限",
                    "fix": "使用强密码策略，避免使用默认密码和弱密码",
                })

                # 使用发现的第一个弱口令进行进一步测试
                first_user, first_pass = weak_creds[0]
                print()
                results["discovered_topics"] = self.sniff_topics(
                    username=first_user, password=first_pass, duration=20
                )

                print()
                results["publish_permissions"] = self.test_publish_permission(
                    username=first_user, password=first_pass
                )

        # 5. TLS 配置检测
        print()
        results["tls_info"] = self.test_tls_config(tls_port)
        if results["tls_info"].get("tls_enabled"):
            if results["tls_info"].get("weak_config"):
                for weak in results["tls_info"]["weak_config"]:
                    results["vulnerabilities"].append({
                        "severity": "中危",
                        "name": "TLS 弱配置",
                        "description": weak,
                        "risk": "可能被利用进行中间人攻击或解密通信",
                        "fix": "升级 TLS 版本，使用强加密套件，配置正确的证书",
                    })
        else:
            results["vulnerabilities"].append({
                "severity": "中危",
                "name": "未启用 TLS",
                "description": "Broker 未启用 TLS 加密",
                "risk": "数据以明文传输，可被嗅探获取凭证和消息内容",
                "fix": "启用 TLS/SSL 加密传输，使用端口 8883",
            })

        # 输出扫描摘要
        print()
        self._print("INFO", "=" * 60)
        self._print("INFO", "扫描结果摘要")
        self._print("INFO", "=" * 60)
        self._print("INFO", f"目标: {results['target']}")
        self._print("INFO", f"端口开放: {'是' if results['port_open'] else '否'}")
        self._print("INFO", f"匿名访问: {'是' if results['anonymous_access'] else '否'}")
        self._print("INFO", f"弱口令数量: {len(results['weak_credentials'])}")
        self._print("INFO", f"发现主题数: {len(results['discovered_topics'])}")
        self._print("INFO", f"TLS 启用: {'是' if results['tls_info'].get('tls_enabled') else '否'}")

        if results["vulnerabilities"]:
            print()
            self._print("WARN", f"共发现 {len(results['vulnerabilities'])} 个安全问题:")
            for i, vuln in enumerate(results["vulnerabilities"], 1):
                self._print("WARN", f"  {i}. [{vuln['severity']}] {vuln['name']}")
        else:
            print()
            self._print("SUCCESS", "未发现明显的安全问题（基于本次扫描范围）")

        return results


# ============================================================
# 命令行参数解析
# ============================================================

def parse_args():
    """
    解析命令行参数

    返回:
        解析后的参数对象
    """
    parser = argparse.ArgumentParser(
        description="MQTT 安全测试工具 - 用于检测 MQTT Broker 的安全性",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 完整扫描
  python iot_mqtt_security.py -t 192.168.1.100 --full-scan

  # 仅测试匿名访问
  python iot_mqtt_security.py -t 192.168.1.100 --anonymous

  # 弱口令检测
  python iot_mqtt_security.py -t 192.168.1.100 --brute-force

  # 主题嗅探（需要认证）
  python iot_mqtt_security.py -t 192.168.1.100 --sniff -u admin -p admin123

  # TLS 配置检测
  python iot_mqtt_security.py -t 192.168.1.100 --tls --tls-port 8883

免责声明:
  本工具仅供学习和授权测试使用，严禁用于未授权的测试！
  使用本工具进行测试前请确保已获得合法授权。
        """,
    )

    # 目标参数
    parser.add_argument("-t", "--target", required=True, help="目标 MQTT Broker IP 或域名")
    parser.add_argument("-p", "--port", type=int, default=1883, help="MQTT 端口 (默认: 1883)")
    parser.add_argument("--timeout", type=int, default=5, help="连接超时时间（秒）(默认: 5)")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细调试信息")

    # 认证参数
    parser.add_argument("-u", "--username", help="用户名（用于需要认证的测试）")
    parser.add_argument("-P", "--password", help="密码（用于需要认证的测试）")

    # 功能选项
    parser.add_argument("--full-scan", action="store_true", help="执行完整安全扫描")
    parser.add_argument("--connect", action="store_true", help="测试 TCP 连接")
    parser.add_argument("--anonymous", action="store_true", help="检测匿名访问")
    parser.add_argument("--brute-force", action="store_true", help="弱口令暴力破解")
    parser.add_argument("--sniff", action="store_true", help="主题嗅探")
    parser.add_argument("--publish-test", action="store_true", help="发布权限测试")
    parser.add_argument("--tls", action="store_true", help="TLS 配置检测")
    parser.add_argument("--fingerprint", action="store_true", help="Broker 指纹识别")

    # TLS 端口
    parser.add_argument("--tls-port", type=int, default=8883, help="TLS 端口 (默认: 8883)")

    # 嗅探相关
    parser.add_argument("--sniff-duration", type=int, default=30, help="主题嗅探持续时间（秒）(默认: 30)")

    # 输出格式
    parser.add_argument("--json-output", help="将结果保存为 JSON 文件")

    return parser.parse_args()


# ============================================================
# 主函数
# ============================================================

def main():
    """
    主函数 - 解析参数并执行相应的测试
    """
    args = parse_args()

    # 打印横幅
    print("=" * 60)
    print("  MQTT 安全测试工具 v1.0")
    print("  MQTT Security Testing Tool")
    print("=" * 60)
    print()

    # 免责声明
    print("[!] 免责声明：本工具仅供学习和授权测试使用")
    print("[!] 使用前请确保已获得合法授权")
    print()

    # 创建扫描器实例
    scanner = MQTTScanner(
        target=args.target,
        port=args.port,
        timeout=args.timeout,
        verbose=args.verbose,
    )

    results = {}

    # 根据参数执行相应功能
    if args.full_scan:
        results = scanner.full_scan(
            username=args.username,
            password=args.password,
            tls_port=args.tls_port,
        )

    else:
        # 单个功能测试
        if args.connect:
            scanner.test_port_connectivity()

        if args.anonymous:
            scanner.test_anonymous_access()

        if args.brute_force:
            scanner.test_weak_password()

        if args.sniff:
            scanner.sniff_topics(
                username=args.username,
                password=args.password,
                duration=args.sniff_duration,
            )

        if args.publish_test:
            scanner.test_publish_permission(
                username=args.username,
                password=args.password,
            )

        if args.tls:
            scanner.test_tls_config(tls_port=args.tls_port)

        if args.fingerprint:
            scanner.fingerprint_broker()

        # 如果没有指定任何功能，显示帮助
        if not any([
            args.connect, args.anonymous, args.brute_force,
            args.sniff, args.publish_test, args.tls, args.fingerprint,
        ]):
            print("[!] 未指定任何测试功能，请使用 --full-scan 或选择单个功能")
            print("[!] 使用 -h 查看帮助信息")
            return

    # 保存结果到 JSON 文件
    if args.json_output and results:
        try:
            with open(args.json_output, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            print(f"\n[+] 结果已保存到: {args.json_output}")
        except Exception as e:
            print(f"[-] 保存结果失败: {e}")

    print()
    print("[*] 扫描完成")


# ============================================================
# 程序入口
# ============================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] 用户中断，退出程序")
        sys.exit(0)
    except Exception as e:
        print(f"\n[-] 程序异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
