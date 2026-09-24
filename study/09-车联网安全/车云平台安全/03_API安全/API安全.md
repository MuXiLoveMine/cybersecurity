# API安全

### 3.1 API网关架构

```text
API网关安全架构

                     ┌──────────────────┐
                     │   客户端请求      │
                     │ (车辆/用户/App)   │
                     └────────┬─────────┘
                              │
                     ┌────────▼─────────┐
                     │   负载均衡器      │
                     │ (L4/L7 LB)      │
                     └────────┬─────────┘
                              │
                     ┌────────▼─────────┐
                     │   API网关         │
                     │                  │
┌─────────────────── ┼──────────────────┼───────────────────┐
│  WAF              ││  速率限制         │  JWT验证          │
│  (Web Application ││  (Rate Limiting) │  (Token Verify)   │
│   Firewall)      ││                  │                   │
└─────────────────── ┼──────────────────┼───────────────────┘
                     │                  │
┌─────────────────── ┼──────────────────┼───────────────────┐
│  API路由           ││  请求转换         │  响应过滤          │
│  (Routing)        ││  (Transform)    │  (Filter)         │
└─────────────────── ┼──────────────────┼───────────────────┘
                     │                  │
                     └────────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │ 车辆管理    │  │ 用户管理    │  │ OTA管理     │
     │ 服务      │  │ 服务       │  │ 服务       │
     └────────────┘  └────────────┘  └────────────┘
```

### 3.2 API认证与授权

```python
"""
车云平台API认证与授权系统
"""

import jwt
import time
import hashlib
import hmac
from functools import wraps
from flask import request, jsonify, g

class APIAuthSystem:
    """API认证授权系统"""

    # JWT配置
    JWT_SECRET = 'your-256-bit-secret'  # 实际从KMS获取
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRY = 3600  # 1小时

    # API Key配置
    API_KEYS = {}  # api_key → {tenant_id, permissions, rate_limit}

    @classmethod
    def authenticate_vehicle(cls, vin, signature, timestamp, nonce):
        """车辆认证"""
        # 1. 验证时间戳新鲜性（5分钟内）
        now = int(time.time())
        if abs(now - timestamp) > 300:
            return None, "时间戳过期"

        # 2. 验证nonce唯一性（防重放）
        if cls._is_nonce_used(nonce):
            return None, "Nonce已被使用"

        # 3. 验证签名
        # 车辆使用预置私钥对 vin + timestamp + nonce 签名
        message = f"{vin}{timestamp}{nonce}".encode()
        if not cls._verify_vehicle_signature(vin, message, signature):
            return None, "签名验证失败"

        # 4. 生成车辆JWT
        token = cls._generate_vehicle_jwt(vin)

        return token, None

    @classmethod
    def authenticate_user(cls, username, password, mfa_code=None):
        """用户认证"""
        # 1. 验证用户名密码
        user = cls._verify_user_credentials(username, password)
        if not user:
            return None, "用户名或密码错误"

        # 2. 检查账户锁定状态
        if cls._is_account_locked(username):
            return None, "账户已锁定，请稍后重试"

        # 3. 高权限操作需要MFA
        if user.get('requires_mfa', False):
            if not mfa_code:
                return None, "需要多因素认证"
            if not cls._verify_mfa(user['mfa_secret'], mfa_code):
                return None, "MFA验证码错误"

        # 4. 生成用户JWT
        token = cls._generate_user_jwt(user)

        return token, None

    @classmethod
    def verify_api_key(cls, api_key):
        """API Key验证"""
        if api_key not in cls.API_KEYS:
            return None, "无效的API Key"

        key_info = cls.API_KEYS[api_key]
        return key_info, None

    @classmethod
    def require_permission(cls, permission):
        """权限检查装饰器"""
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                token = request.headers.get('Authorization', '')
                if not token.startswith('Bearer '):
                    return jsonify({'error': '缺少认证Token'}), 401

                token = token[7:]

                try:
                    payload = jwt.decode(
                        token, cls.JWT_SECRET,
                        algorithms=[cls.JWT_ALGORITHM]
                    )
                except jwt.ExpiredSignatureError:
                    return jsonify({'error': 'Token已过期'}), 401
                except jwt.InvalidTokenError:
                    return jsonify({'error': '无效Token'}), 401

                # 检查权限
                user_permissions = payload.get('permissions', [])
                if permission not in user_permissions:
                    return jsonify({'error': '权限不足'}), 403

                # 注入用户上下文
                g.user = payload

                return f(*args, **kwargs)
            return decorated
        return decorator

    @classmethod
    def _generate_vehicle_jwt(cls, vin):
        """生成车辆JWT"""
        payload = {
            'sub': vin,
            'type': 'vehicle',
            'iat': int(time.time()),
            'exp': int(time.time()) + cls.JWT_EXPIRY,
            'permissions': ['vehicle:read', 'vehicle:report'],
            'vehicle_id': vin
        }
        return jwt.encode(payload, cls.JWT_SECRET, algorithm=cls.JWT_ALGORITHM)

    @classmethod
    def _generate_user_jwt(cls, user):
        """生成用户JWT"""
        payload = {
            'sub': user['id'],
            'type': 'user',
            'iat': int(time.time()),
            'exp': int(time.time()) + cls.JWT_EXPIRY,
            'permissions': user['permissions'],
            'tenant_id': user.get('tenant_id'),
            'role': user.get('role')
        }
        return jwt.encode(payload, cls.JWT_SECRET, algorithm=cls.JWT_ALGORITHM)

    @staticmethod
    def _is_nonce_used(nonce):
        """检查nonce是否已使用（简化版）"""
        # 实际使用Redis存储已使用的nonce
        return False

    @staticmethod
    def _verify_vehicle_signature(vin, message, signature):
        """验证车辆签名"""
        # 实际从数据库获取车辆公钥进行验证
        return True

    @staticmethod
    def _verify_user_credentials(username, password):
        """验证用户凭据"""
        # 实际从数据库查询并验证密码哈希
        if username == 'admin' and password == 'password':
            return {
                'id': 'user_001',
                'permissions': ['vehicle:read', 'vehicle:write',
                                'ota:manage', 'user:manage'],
                'tenant_id': 'tenant_001',
                'role': 'oem_admin',
                'requires_mfa': True
            }
        return None

    @staticmethod
    def _is_account_locked(username):
        """检查账户锁定"""
        return False

    @staticmethod
    def _verify_mfa(secret, code):
        """验证MFA"""
        # 实际使用TOTP算法
        return code == '123456'


# API路由示例
from flask import Flask
app = Flask(__name__)

@app.route('/api/v1/vehicles/<vin>/status')
@APIAuthSystem.require_permission('vehicle:read')
def get_vehicle_status(vin):
    """获取车辆状态"""
    # 验证用户是否有权访问该车辆
    user_tenant = g.user.get('tenant_id')
    if not _check_vehicle_ownership(vin, g.user.get('sub'), user_tenant):
        return jsonify({'error': '无权访问该车辆'}), 403

    # 返回车辆状态
    return jsonify({
        'vin': vin,
        'status': 'online',
        'battery': 85,
        'mileage': 12345,
        'location': {'lat': 31.23, 'lon': 121.47}
    })


@app.route('/api/v1/vehicles/<vin>/unlock', methods=['POST'])
@APIAuthSystem.require_permission('vehicle:write')
def remote_unlock(vin):
    """远程开锁"""
    # 高敏感操作，需要额外验证
    user_id = g.user.get('sub')
    if not _check_vehicle_ownership(vin, user_id, g.user.get('tenant_id')):
        return jsonify({'error': '无权操作该车辆'}), 403

    # 检查操作频率限制
    if _is_rate_limited(user_id, 'unlock'):
        return jsonify({'error': '操作过于频繁'}), 429

    # 记录操作审计
    _log_audit(user_id, 'remote_unlock', vin)

    # 下发开锁指令
    result = _send_vehicle_command(vin, 'unlock')

    return jsonify({'success': True, 'command_id': result.get('id')})


@app.route('/api/v1/ota/publish', methods=['POST'])
@APIAuthSystem.require_permission('ota:manage')
def publish_ota():
    """发布OTA升级"""
    # 仅OEM管理员可操作
    if g.user.get('role') not in ('oem_admin', 'platform_admin'):
        return jsonify({'error': '权限不足'}), 403

    # 验证升级包签名
    # 灰度发布配置
    # 创建升级任务

    return jsonify({'success': True, 'task_id': 'ota_task_001'})


def _check_vehicle_ownership(vin, user_id, tenant_id):
    """检查车辆所有权"""
    return True

def _is_rate_limited(user_id, action):
    return False

def _log_audit(user_id, action, target):
    pass

def _send_vehicle_command(vin, command):
    return {'id': 'cmd_001'}


if __name__ == '__main__':
    app.run(ssl_context='adhoc', port=8443)
```

### 3.3 API输入验证与防护

```text
API输入验证层级

第1层: API网关
├── 请求大小限制
├── 速率限制（每IP/每用户）
├── IP黑白名单
├── WAF规则（SQL注入/XSS/路径遍历）
└── 请求方法限制

第2层: 认证层
├── JWT验证
├── API Key验证
├── 权限检查
└── 租户隔离验证

第3层: 输入验证层
├── 参数类型验证
├── 参数范围验证
├── 参数格式验证
├── 参数长度限制
└── 白名单验证

第4层: 业务逻辑层
├── 业务规则验证
├── 状态机验证
└── 资源访问验证
```

```python
# API输入验证示例
import re
from marshmallow import Schema, fields, validate

class VehicleStatusQuery(Schema):
    """车辆状态查询参数验证"""
    vin = fields.Str(
        required=True,
        validate=validate.Regexp(r'^[A-HJ-NPR-Z0-9]{17}$'),  # VIN格式
        metadata={'description': '车辆识别码（17位）'}
    )
    fields = fields.List(
        fields.Str(validate=validate.OneOf([
            'battery', 'mileage', 'location', 'speed',
            'tire_pressure', 'door_status'
        ])),
        metadata={'description': '请求的状态字段'}
    )
    since = fields.Int(
        validate=validate.Range(min=0, max=int(time.time())),
        metadata={'description': '起始时间戳'}
    )

class RemoteCommandSchema(Schema):
    """远程指令参数验证"""
    command = fields.Str(
        required=True,
        validate=validate.OneOf([
            'unlock', 'lock', 'horn', 'lights',
            'engine_start', 'engine_stop', 'ac_on', 'ac_off'
        ])
    )
    parameters = fields.Dict(
        keys=fields.Str(),
        values=fields.Raw(),
        validate=validate.Length(max=10)  # 最多10个参数
    )
    timeout = fields.Int(
        validate=validate.Range(min=5, max=60),
        load_default=30
    )

# 使用示例
def handle_remote_command(data):
    """处理远程指令"""
    try:
        validated = RemoteCommandSchema().load(data)
    except Exception as e:
        return {'error': f'参数验证失败: {e}'}, 400

    command = validated['command']
    params = validated.get('parameters', {})

    # 指令参数白名单
    allowed_params = {
        'unlock': {'door': ['all', 'driver', 'trunk']},
        'ac_on': {'temperature': (16, 32), 'mode': ['auto', 'manual']},
        'engine_start': {'duration': (1, 15)}
    }

    if command in allowed_params:
        for key, value in params.items():
            if key not in allowed_params[command]:
                return {'error': f'不允许的参数: {key}'}, 400
            # 进一步验证参数值...

    return {'success': True, 'command': command}
```

---

---

