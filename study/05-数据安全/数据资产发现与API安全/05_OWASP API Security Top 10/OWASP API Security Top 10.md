# OWASP API Security Top 10

### 5.1 API1:2023 - BOLA（越权访问）

```http
# 漏洞: 用户可以访问其他用户的数据
GET /api/v2/users/12345/orders HTTP/1.1
Authorization: Bearer user_67890_token

# 如果后端未校验 user_12345 的订单是否属于 user_67890
# 则用户 67890 可以越权查看用户 12345 的订单

# 修复: 服务端验证资源所有权
# 1. 使用当前用户身份过滤数据
SELECT * FROM orders WHERE user_id = ? AND order_id = ?
# 而不是
SELECT * FROM orders WHERE order_id = ?

# 2. 使用 UUID 替代自增 ID 增加遍历难度
# /api/v2/users/550e8400-e29b/orders
# 而不是
# /api/v2/users/12345/orders
```

### 5.2 API2:2023 - 认证失败

```http
# 漏洞1: 弱密码策略
POST /api/v1/auth/login
{"username": "admin", "password": "123456"}

# 漏洞2: Token 不失效
# 用户登出后 Token 仍可使用
DELETE /api/v1/session
Authorization: Bearer still_valid_token  # 应该失效

# 漏洞3: JWT 不验证签名
# 修改 payload 后 Token 仍被接受

# 修复:
# - 密码强度策略（8+ 字符，大小写+数字+特殊字符）
# - 多因素认证（MFA）
# - Token 吊销机制（Redis 黑名单）
# - 登录失败锁定（5次失败锁定30分钟）
```

### 5.3 API3:2023 - 对象属性级授权

```http
# Mass Assignment 漏洞
PUT /api/v1/users/profile
Content-Type: application/json

{
  "nickname": "NewName",
  "role": "admin",        # 不应被修改
  "isPremium": true,       # 不应被修改
  "creditLimit": 999999    # 不应被修改
}

# 修复: 使用 DTO 白名单
class UserUpdateDTO:
    allowed_fields = ['nickname', 'avatar', 'bio']
    
    def update(self, data):
        for key in self.allowed_fields:
            if key in data:
                setattr(self.model, key, data[key])
```

### 5.4 API4:2023 - 不受限资源消耗

```http
# 漏洞: 无限制的API调用
# 缺少速率限制，可被暴力破解或DoS

POST /api/v1/auth/login   # 无限次尝试密码
GET /api/v1/users?page=1&size=1000000  # 单次返回100万条
POST /api/v1/upload       # 上传1GB文件

# 修复: 多层速率限制
# 1. API网关层 - IP级限流
# 2. 应用层 - 用户级限流
# 3. 数据层 - 分页大小限制
```

### 5.5 API5:2023 - BFLA（功能级授权失效）

```http
# 漏洞: 普通用户可访问管理功能
# 仅检查了登录状态，未检查角色权限
POST /api/v1/admin/users/create
Authorization: Bearer normal_user_token

# 修复: 角色权限校验
@app.route('/api/v1/admin/users/create', methods=['POST'])
@roles_required('admin', 'superadmin')
def create_user():
    ...
```

### 5.6 API6:2023 - 不受限敏感数据暴露

```http
# 漏洞: API 返回了多余的敏感字段
GET /api/v1/users/123
Response:
{
  "id": 123,
  "name": "张三",
  "email": "zhangsan@example.com",   # 不应返回
  "phone": "13800138000",            # 不应返回
  "passwordHash": "...",             # 不应返回
  "creditCard": "6222...",           # 不应返回
  "idCard": "110101...",             # 不应返回
}

# 修复: 响应字段白名单 + 数据脱敏
{
  "id": 123,
  "name": "张三",
  "email": "z***@example.com",
  "phone": "138****8000"
}
```

### 5.7 API7-10 概述

| 编号 | 名称 | 核心风险 | 修复要点 |
|------|------|----------|----------|
| API7 | 服务端请求伪造(SSRF) | 后端发起任意请求 | URL 白名单、禁用内网 |
| API8 | 安全配置错误 | 默认配置/暴露面 | 最小暴露、安全默认值 |
| API9 | 库存管理不当 | 废弃API仍可访问 | API生命周期管理 |
| API10 | 不安全API消费 | 第三方API不可信 | 验证响应、超时处理 |

---

---

## 📋 内容审核与补充建议

> 针对「OWASP API Security Top 10」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
