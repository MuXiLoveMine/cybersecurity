# FIDO2 部署实践

### 5.1 服务端实现

**FIDO2 服务端核心组件：**

```python
# FIDO2服务端核心架构（Python示例）
import os
import json
import hashlib
from fido2.server import Fido2Server
from fido2.webauthn import PublicKeyCredentialRpEntity, Attestation

class FIDO2AuthService:
    def __init__(self):
        self.rp = PublicKeyCredentialRpEntity(
            id="security.example.com",
            name="安全学习平台"
        )
        self.server = Fido2Server(self.rp)
        self.credentials_store = {}  # 实际应使用数据库
        self.challenges = {}          # 临时存储Challenge
        
    async def begin_registration(self, user_id, username, display_name):
        """开始注册流程"""
        # 生成或获取用户信息
        user = {
            "id": user_id.encode(),
            "name": username,
            "displayName": display_name
        }
        
        # 获取已有凭据（防止重复注册）
        existing_credentials = self._get_user_credentials(user_id)
        
        # 生成注册选项
        options, state = self.server.register_begin(
            user,
            credentials=existing_credentials,
            user_verification="required",
            authenticator_attachment="platform",
            resident_key_requirement="preferred"
        )
        
        # 存储state用于后续验证
        self.challenges[user_id] = state
        
        return dict(options)
    
    async def complete_registration(self, user_id, response):
        """完成注册验证"""
        state = self.challenges.get(user_id)
        if not state:
            raise ValueError("No pending registration")
        
        # 验证Attestation
        auth_data = self.server.register_complete(
            state,
            response['clientDataJSON'],
            response['attestationObject']
        )
        
        # 存储凭据
        credential = {
            'id': auth_data.credential_id,
            'public_key': auth_data.credential_public_key,
            'sign_count': auth_data.sign_count,
            'aaguid': str(auth_data.attestation.auth_data.aaguid),
            'backup_eligible': auth_data.flags.be,
            'backup_state': auth_data.flags.bs
        }
        
        self._store_credential(user_id, credential)
        del self.challenges[user_id]
        
        return {"status": "ok", "credential_id": credential['id']}
    
    async def begin_authentication(self, username):
        """开始认证流程"""
        # 查找用户凭据
        credentials = self._get_credentials_by_username(username)
        if not credentials:
            # 防枚举：返回通用选项
            options, state = self.server.authenticate_begin()
        else:
            options, state = self.server.authenticate_begin(
                credentials=credentials
            )
        
        # 存储state
        session_id = os.urandom(32).hex()
        self.challenges[session_id] = state
        
        return dict(options), session_id
    
    async def complete_authentication(self, session_id, response):
        """完成认证验证"""
        state = self.challenges.get(session_id)
        if not state:
            raise ValueError("No pending authentication")
        
        # 验证签名
        new_sign_count = self.server.authenticate_complete(
            state,
            response['credentialId'],
            response['clientDataJSON'],
            response['authenticatorData'],
            response['signature']
        )
        
        # 更新sign count
        credential_id = response['credentialId']
        self._update_sign_count(credential_id, new_sign_count)
        
        del self.challenges[session_id]
        
        # 返回用户信息和会话token
        user = self._get_user_by_credential(credential_id)
        return {"status": "ok", "user": user}
```

### 5.2 用户体验设计

**渐进式无密码迁移策略：**

```
迁移阶段设计：

阶段1：MFA增强（1-2个月）
  └── 在现有密码登录上叠加FIDO2令牌
  └── 用户可选（不强制）
  └── 让用户熟悉认证器使用

阶段2：可选无密码（3-6个月）
  └── 注册FIDO2凭据的用户可免密登录
  └── 密码仍可用作为备用
  └── 登录页增加"使用Passkey登录"按钮

阶段3：默认无密码（6-12个月）
  └── Passkey成为默认登录方式
  └── 密码登录移至"更多选项"
  └── 新用户注册时直接注册Passkey

阶段4：完全无密码（12个月+）
  └── 移除密码登录选项
  └── 仅保留Passkey + 账号恢复流程
```

**前端登录页交互示例：**

```html
<!-- 登录页面 -->
<div class="login-container">
    <!-- 主要：Passkey登录 -->
    <button id="passkey-login" class="btn-primary">
        <svg>...</svg> 使用Passkey登录
    </button>
    
    <!-- 次要：传统方式 -->
    <details>
        <summary>更多登录方式</summary>
        <button id="password-login">密码登录</button>
        <button id="sms-login">短信验证码</button>
    </details>
</div>

<script>
document.getElementById('passkey-login').addEventListener('click', async () => {
    try {
        // 1. 从服务端获取认证选项
        const optionsResp = await fetch('/api/auth/webauthn/options');
        const options = await optionsResp.json();
        
        // 2. 调用WebAuthn API
        const credential = await navigator.credentials.get({
            publicKey: {
                challenge: base64ToArrayBuffer(options.challenge),
                rpId: options.rpId,
                allowCredentials: options.allowCredentials.map(c => ({
                    type: c.type,
                    id: base64ToArrayBuffer(c.id)
                })),
                userVerification: options.userVerification,
                timeout: options.timeout
            }
        });
        
        // 3. 发送认证数据到服务端
        const authResp = await fetch('/api/auth/webauthn/verify', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                credentialId: credential.id,
                authenticatorData: credential.response.authenticatorData,
                clientDataJSON: credential.response.clientDataJSON,
                signature: credential.response.signature
            })
        });
        
        if (authResp.ok) {
            window.location.href = '/dashboard';
        }
    } catch (e) {
        if (e.name === 'NotAllowedError') {
            // 用户取消或认证器不支持
            showFallbackLogin();
        }
    }
});

// 检测浏览器是否支持Passkey
async function isPasskeySupported() {
    if (!window.PublicKeyCredential) return false;
    return await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()
        .then(result => result);
}
</script>
```

### 5.3 备份与恢复

**设备丢失场景的恢复策略：**

```
恢复策略矩阵：

场景1：用户注册了多个Passkey设备
  └── 其他设备直接可用
  └── 无需恢复

场景2：Passkey已云端同步
  └── 新设备登录云账号后自动同步
  └── 可立即使用

场景3：唯一的设备且Passkey未同步
  └── 需要账号恢复流程
  └── 通过预设恢复方式（备用邮箱、客服验证等）
  └── 恢复后重新注册Passkey

场景4：企业环境
  └── IT管理员可重置用户FIDO2凭据
  └── 使用临时恢复码
  └── 或使用管理员恢复令牌
```

**企业级恢复方案：**

```python
# 企业FIDO2恢复方案
class FIDO2RecoveryService:
    def __init__(self):
        self.recovery_keys = {}  # 恢复密钥库
        
    def generate_recovery_code(self, user_id):
        """用户注册时生成恢复码"""
        recovery_code = os.urandom(20).hex()
        # 存储恢复码的哈希值
        self.recovery_keys[user_id] = {
            'hash': hashlib.sha256(recovery_code.encode()).hexdigest(),
            'created_at': time.time(),
            'used': False
        }
        return recovery_code  # 只返回一次
        
    def recover_account(self, user_id, recovery_code, new_device_info):
        """使用恢复码恢复账号"""
        stored = self.recovery_keys.get(user_id)
        if not stored or stored['used']:
            raise ValueError("Invalid recovery code")
        
        # 验证恢复码
        code_hash = hashlib.sha256(recovery_code.encode()).hexdigest()
        if code_hash != stored['hash']:
            raise ValueError("Recovery code mismatch")
        
        # 标记已使用
        stored['used'] = True
        
        # 删除旧凭据
        self._delete_all_credentials(user_id)
        
        # 返回临时Token用于新设备注册
        temp_token = self._generate_temp_token(user_id, expires=300)
        return temp_token
```

---

---

