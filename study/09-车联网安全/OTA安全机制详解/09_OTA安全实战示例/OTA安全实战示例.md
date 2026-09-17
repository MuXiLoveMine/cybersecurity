# OTA安全实战示例

### 8.1 固件签名与验证代码

详见第2.1节的 `FirmwareSigner` 和 `FirmwareVerifier` 类。

### 8.2 OTA服务端安全配置

```python
"""
OTA服务端安全配置与API
"""

from flask import Flask, request, jsonify
import hashlib
import os
import json
from functools import wraps

app = Flask(__name__)

# 配置
class OTAConfig:
    # 证书
    CERT_DIR = '/etc/ota/certs'
    SERVER_CERT = f'{CERT_DIR}/server.crt'
    SERVER_KEY = f'{CERT_DIR}/server.key'
    CA_CERT = f'{CERT_DIR}/ca.crt'

    # 存储
    FIRMWARE_DIR = '/data/ota/firmware'
    METADATA_DB = 'postgresql://ota:password@localhost/ota'

    # 安全参数
    MAX_PACKAGE_SIZE = 500 * 1024 * 1024  # 500MB
    MAX_REQUEST_RATE = 100  # 每分钟100次
    SESSION_TIMEOUT = 300  # 5分钟


# API认证装饰器
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 验证JWT或mTLS
        auth_header = request.headers.get('Authorization', '')
        cert = request.headers.get('X-Client-Cert', '')

        if not auth_header and not cert:
            return jsonify({'error': '认证失败'}), 401

        # 验证JWT
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
            # 验证JWT签名
            # ...

        return f(*args, **kwargs)
    return decorated


# OTA升级包发布API
@app.route('/api/v1/ota/packages', methods=['POST'])
@require_auth
def publish_package():
    """发布OTA升级包（需要管理员权限）"""
    # 1. 验证管理员权限
    # 2. 验证升级包签名
    firmware_file = request.files.get('firmware')
    if not firmware_file:
        return jsonify({'error': '缺少固件文件'}), 400

    # 3. 读取固件
    firmware_data = firmware_file.read()
    if len(firmware_data) > OTAConfig.MAX_PACKAGE_SIZE:
        return jsonify({'error': '固件文件过大'}), 413

    # 4. 验证固件签名
    signature = request.form.get('signature', '')
    metadata = json.loads(request.form.get('metadata', '{}'))

    # 验证签名（使用OTA CA公钥）
    # ...

    # 5. 存储固件
    firmware_hash = hashlib.sha256(firmware_data).hexdigest()
    firmware_path = os.path.join(OTAConfig.FIRMWARE_DIR, firmware_hash)
    with open(firmware_path, 'wb') as f:
        f.write(firmware_data)

    # 6. 记录元数据
    metadata['hash'] = firmware_hash
    metadata['size'] = len(firmware_data)
    metadata['published_at'] = __import__('datetime').datetime.utcnow().isoformat()

    # 存储到数据库
    # db.save_metadata(metadata)

    return jsonify({
        'success': True,
        'firmware_hash': firmware_hash,
        'metadata': metadata
    })


# 车辆检查升级API
@app.route('/api/v1/ota/check', methods=['POST'])
@require_auth
def check_update():
    """车辆检查是否有可用升级"""
    data = request.json
    vehicle_id = data.get('vehicle_id')
    current_versions = data.get('current_versions', {})

    # 查询适合该车辆的升级
    # available_updates = db.query_updates(vehicle_id, current_versions)

    # 灰度发布检查
    # if vehicle_in_graylist(vehicle_id):
    #     return jsonify({'update_available': False})

    return jsonify({
        'update_available': True,
        'updates': [
            {
                'ecu': 'IVI',
                'version': '2.1.0',
                'size': 52428800,
                'hash': 'abc123...',
                'download_url': '/api/v1/ota/download/abc123',
                'mandatory': False,
                'release_notes': '修复蓝牙问题'
            }
        ]
    })


# 固件下载API
@app.route('/api/v1/ota/download/<firmware_hash>', methods=['GET'])
@require_auth
def download_firmware(firmware_hash):
    """下载固件"""
    # 1. 验证哈希格式
    if not all(c in '0123456789abcdef' for c in firmware_hash):
        return jsonify({'error': '无效的哈希值'}), 400

    # 2. 查找固件文件
    firmware_path = os.path.join(OTAConfig.FIRMWARE_DIR, firmware_hash)
    if not os.path.exists(firmware_path):
        return jsonify({'error': '固件不存在'}), 404

    # 3. 返回固件
    return __import__('send_file').send_file(
        firmware_path,
        as_attachment=True,
        download_name=f'{firmware_hash}.bin'
    )


# 升级状态上报API
@app.route('/api/v1/ota/status', methods=['POST'])
@require_auth
def report_status():
    """车辆上报升级状态"""
    data = request.json
    vehicle_id = data.get('vehicle_id')
    status = data.get('status')  # downloading/installing/success/failed
    firmware_hash = data.get('firmware_hash')
    error_message = data.get('error_message', '')

    # 记录状态
    # db.log_upgrade_status(vehicle_id, status, firmware_hash, error_message)

    return jsonify({'received': True})


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8443,
        ssl_context=(
            OTAConfig.SERVER_CERT,
            OTAConfig.SERVER_KEY
        )
    )
```

### 8.3 车辆端OTA客户端

```python
"""
车辆端OTA客户端
"""

import os
import time
import hashlib
import json
import requests
from enum import Enum


class OTAState(Enum):
    IDLE = "idle"
    CHECKING = "checking"
    DOWNLOADING = "downloading"
    VERIFYING = "verifying"
    INSTALLING = "installing"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLBACK = "rollback"


class VehicleOTAClient:
    """车辆端OTA客户端"""

    def __init__(self, vehicle_id, server_url, cert_path=None, key_path=None):
        self.vehicle_id = vehicle_id
        self.server_url = server_url
        self.cert_path = cert_path  # mTLS客户端证书
        self.key_path = key_path
        self.state = OTAState.IDLE
        self.current_versions = {}  # ECU → 当前版本
        self.download_dir = '/tmp/ota_downloads'
        self.max_retries = 3
        self.chunk_size = 1024 * 1024  # 1MB

        os.makedirs(self.download_dir, exist_ok=True)

    def check_for_updates(self):
        """检查是否有可用升级"""
        self.state = OTAState.CHECKING

        session = self._create_session()
        response = session.post(
            f'{self.server_url}/api/v1/ota/check',
            json={
                'vehicle_id': self.vehicle_id,
                'current_versions': self.current_versions
            }
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('update_available'):
                return data.get('updates', [])

        return []

    def download_update(self, update_info):
        """下载升级包"""
        self.state = OTAState.DOWNLOADING
        download_url = update_info['download_url']
        expected_hash = update_info['hash']
        firmware_path = os.path.join(self.download_dir, expected_hash + '.bin')

        session = self._create_session()

        # 支持断点续传
        downloaded = 0
        if os.path.exists(firmware_path):
            downloaded = os.path.getsize(firmware_path)

        headers = {}
        if downloaded > 0:
            headers['Range'] = f'bytes={downloaded}-'

        response = session.get(
            f'{self.server_url}{download_url}',
            headers=headers,
            stream=True
        )

        if response.status_code in (200, 206):
            mode = 'ab' if downloaded > 0 else 'wb'
            with open(firmware_path, mode) as f:
                for chunk in response.iter_content(self.chunk_size):
                    f.write(chunk)

            # 验证下载完整性
            actual_hash = self._calculate_hash(firmware_path)
            if actual_hash != expected_hash:
                os.remove(firmware_path)
                self.state = OTAState.FAILED
                return False, "固件哈希不匹配"

            return True, firmware_path
        else:
            self.state = OTAState.FAILED
            return False, f"下载失败: HTTP {response.status_code}"

    def verify_update(self, firmware_path, update_info):
        """验证升级包"""
        self.state = OTAState.VERIFYING

        # 1. 验证固件哈希
        actual_hash = self._calculate_hash(firmware_path)
        if actual_hash != update_info['hash']:
            return False, "固件哈希验证失败"

        # 2. 验证签名
        # 从升级包中提取签名和元数据
        # 验证签名（使用预置的OTA CA公钥）
        # ...

        # 3. 验证版本兼容性
        target_ecu = update_info.get('ecu')
        new_version = update_info.get('version')
        current_version = self.current_versions.get(target_ecu, '0.0.0')
        if not self._version_ge(new_version, current_version):
            return False, f"版本不满足升级要求: {current_version} → {new_version}"

        return True, "验证通过"

    def install_update(self, firmware_path, update_info):
        """安装升级"""
        self.state = OTAState.INSTALLING

        target_ecu = update_info.get('ecu')

        try:
            # 1. 写入备用分区
            partition = self._get_inactive_partition(target_ecu)
            self._write_to_partition(firmware_path, partition)

            # 2. 设置下次启动从新分区
            self._set_boot_partition(target_ecu, partition)

            # 3. 重启验证（实际需要车辆重启）
            # reboot_and_verify()

            # 4. 验证成功后提交
            self._commit_upgrade(target_ecu, update_info['version'])

            self.state = OTAState.SUCCESS
            return True, "升级成功"

        except Exception as e:
            # 回滚
            self.state = OTAState.ROLLBACK
            self._rollback(target_ecu)
            self.state = OTAState.FAILED
            return False, f"升级失败，已回滚: {str(e)}"

    def run_ota_cycle(self):
        """完整OTA周期"""
        print(f"[OTA] 开始OTA检查, 车辆ID={self.vehicle_id}")

        # 1. 检查升级
        updates = self.check_for_updates()
        if not updates:
            print("[OTA] 无可用升级")
            return

        for update in updates:
            print(f"[OTA] 发现升级: {update['ecu']} v{update['version']}")

            # 2. 下载
            success, result = self.download_update(update)
            if not success:
                print(f"[OTA] 下载失败: {result}")
                self._report_status(update, 'failed', result)
                continue

            # 3. 验证
            success, result = self.verify_update(result, update)
            if not success:
                print(f"[OTA] 验证失败: {result}")
                self._report_status(update, 'failed', result)
                continue

            # 4. 安装
            success, result = self.install_update(result, update)
            if success:
                print(f"[OTA] 升级成功: {update['ecu']} → v{update['version']}")
                self._report_status(update, 'success')
                self.current_versions[update['ecu']] = update['version']
            else:
                print(f"[OTA] 升级失败: {result}")
                self._report_status(update, 'failed', result)

    def _create_session(self):
        """创建HTTP会话"""
        session = requests.Session()
        if self.cert_path and self.key_path:
            session.cert = (self.cert_path, self.key_path)
        session.verify = True  # 验证服务器证书
        return session

    @staticmethod
    def _calculate_hash(file_path):
        """计算文件哈希"""
        h = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def _version_ge(v1, v2):
        """版本号比较 v1 >= v2"""
        parts1 = [int(x) for x in v1.split('.')]
        parts2 = [int(x) for x in v2.split('.')]
        return parts1 >= parts2

    def _get_inactive_partition(self, ecu):
        """获取非活动分区"""
        return 'B'  # 简化

    def _write_to_partition(self, firmware, partition):
        """写入分区"""
        pass

    def _set_boot_partition(self, ecu, partition):
        """设置启动分区"""
        pass

    def _commit_upgrade(self, ecu, version):
        """提交升级"""
        pass

    def _rollback(self, ecu):
        """回滚"""
        pass

    def _report_status(self, update, status, message=''):
        """上报状态"""
        try:
            session = self._create_session()
            session.post(
                f'{self.server_url}/api/v1/ota/status',
                json={
                    'vehicle_id': self.vehicle_id,
                    'status': status,
                    'firmware_hash': update.get('hash'),
                    'error_message': message
                }
            )
        except Exception:
            pass


# 演示
def demo_ota_client():
    print("=" * 50)
    print("车辆端OTA客户端演示")
    print("=" * 50)

    client = VehicleOTAClient(
        vehicle_id='VIN123456789',
        server_url='https://ota.example.com'
    )

    # 设置当前版本
    client.current_versions = {
        'IVI': '1.0.0',
        'TBOX': '1.2.0'
    }

    # 运行OTA周期（模拟）
    print("\n[模拟] 检查升级...")
    print("  当前版本:")
    for ecu, ver in client.current_versions.items():
        print(f"    {ecu}: v{ver}")

    # 模拟发现升级
    update = {
        'ecu': 'IVI',
        'version': '2.0.0',
        'hash': 'a' * 64,
        'download_url': '/api/v1/ota/download/aaa',
        'size': 52428800,
        'release_notes': '新增语音助手功能'
    }

    print(f"\n[模拟] 发现升级:")
    print(f"  ECU: {update['ecu']}")
    print(f"  版本: {update['version']}")
    print(f"  大小: {update['size'] / 1024 / 1024:.1f} MB")
    print(f"  说明: {update['release_notes']}")


if __name__ == "__main__":
    demo_ota_client()
```

---

---

## 📋 内容审核与补充建议

> 针对「OTA安全实战示例」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
