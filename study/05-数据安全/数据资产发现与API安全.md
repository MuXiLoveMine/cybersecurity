# 数据资产发现与 API 安全

> 本文档系统介绍数据资产发现方法论、数据分类分级标准、数据资产盘点工具，以及 API 数据安全（OWASP API Security Top 10）、API 安全网关、数据脱敏技术和 DSMM 成熟度评估模型。

---

## 一、数据资产发现方法论

### 1.1 数据资产发现概述

数据资产发现是数据安全治理的第一步，目标是全面掌握企业拥有的数据资产分布、类型、敏感程度和流转路径，为后续的分类分级和防护策略奠定基础。

```
数据资产发现三步法:

第一步: 自动发现（技术驱动）
├── 扫描数据库/文件系统/云存储
├── NLP 识别敏感数据字段
├── 网络流量分析发现数据流
└── API 接口自动枚举

第二步: 手动标记（业务驱动）
├── 业务部门申报数据资产
├── 数据责任人确认
├── 敏感数据人工标注
└── 业务上下文补充

第三步: 数据流映射（流转追踪）
├── 数据从哪里来（数据源）
├── 数据存哪里（存储位置）
├── 数据怎么用（使用场景）
├── 数据流向哪里（共享/外发）
└── 数据如何销毁（生命周期终末）
```

### 1.2 自动发现技术

**（1）数据库资产扫描**

```python
# 数据库敏感数据自动扫描脚本示例
import re
import pymysql

# 敏感数据特征模式
SENSITIVE_PATTERNS = {
    '身份证号': {
        'regex': r'^\d{17}[\dXx]$',
        'columns_hint': ['idcard', 'id_card', 'sfz', 'certno', 'identity']
    },
    '手机号': {
        'regex': r'^1[3-9]\d{9}$',
        'columns_hint': ['phone', 'mobile', 'tel', 'contact']
    },
    '银行卡号': {
        'regex': r'^\d{16,19}$',
        'columns_hint': ['bank', 'card', 'account', 'acctno']
    },
    '邮箱': {
        'regex': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'columns_hint': ['email', 'mail', 'mail_addr']
    }
}

def scan_database(host, port, user, password, database):
    """
    扫描数据库中的敏感数据
    """
    conn = pymysql.connect(
        host=host, port=port, user=user, 
        password=password, database=database
    )
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    
    results = []
    for table in tables:
        # 获取表结构
        cursor.execute(f"DESCRIBE `{table}`")
        columns = cursor.fetchall()
        
        sensitive_fields = []
        for col in columns:
            col_name = col[0].lower()
            col_type = col[1]
            
            # 基于列名匹配
            for data_type, pattern in SENSITIVE_PATTERNS.items():
                if any(hint in col_name for hint in pattern['columns_hint']):
                    sensitive_fields.append({
                        'table': table,
                        'column': col[0],
                        'type': data_type,
                        'match_reason': 'column_name'
                    })
        
        # 基于数据采样匹配
        if sensitive_fields:
            col_names = [f['column'] for f in sensitive_fields]
            sample_query = f"SELECT {', '.join(col_names)} FROM `{table}` LIMIT 100"
            cursor.execute(sample_query)
            
            for row in cursor.fetchall():
                for i, val in enumerate(row):
                    if val and isinstance(val, str):
                        for data_type, pattern in SENSITIVE_PATTERNS.items():
                            if re.match(pattern['regex'], str(val)):
                                if not any(
                                    f['column'] == col_names[i] and 
                                    f['type'] == data_type 
                                    for f in sensitive_fields
                                ):
                                    sensitive_fields.append({
                                        'table': table,
                                        'column': col_names[i],
                                        'type': data_type,
                                        'match_reason': 'data_sample'
                                    })
        
        if sensitive_fields:
            results.extend(sensitive_fields)
    
    conn.close()
    return results
```

**（2）文件系统敏感数据扫描**

```bash
# 使用 find + grep 扫描文件系统中的敏感数据

# 查找包含身份证号的文件
find /data -type f -name "*.csv" -o -name "*.txt" -o -name "*.json" |
  xargs grep -l "[0-9]\{17\}[0-9Xx]" 2>/dev/null

# 查找包含手机号的文件
find /data -type f \( -name "*.csv" -o -name "*.txt" \) |
  xargs grep -l "1[3-9][0-9]\{9\}" 2>/dev/null

# 使用专用工具
# - TruffleHog: 扫描代码仓库中的密钥和敏感信息
trufflehog filesystem /path/to/scan

# - Gitleaks: Git 仓库敏感信息扫描
gitleaks detect --source /repo/path --report-path leaks.json

# - YARA: 自定义规则扫描文件
# rule.yar
# rule Sensitive_IDCard {
#     strings:
#         $id = /\d{17}[\dXx]/
#     condition:
#         $id
# }
yara -r rule.yar /data/
```

### 1.3 数据流映射

```
数据流映射示例 - 用户订单数据

数据源:
├── 用户注册表单（前端页面）
├── 第三方数据接入（合作伙伴API）
└── 客服录入系统（内部CRM）

存储位置:
├── 主数据库 MySQL - users表（明文存储，需加密）
├── 缓存 Redis - 用户会话数据
├── 数据仓库 HDFS - 用户行为日志
└── 备份存储 OSS - 冷备份数据

使用场景:
├── 订单系统（读取用户地址）
├── 营销系统（读取手机号推送短信）
├── 风控系统（分析用户行为数据）
└── 报表系统（统计分析）

数据流向:
├── 内部: 订单系统 → 风控系统 → 数据仓库
├── 对外: 营销系统 → 短信平台API（手机号外发）
├── 对外: 报表系统 → BI 平台（脱敏后展示）
└── 备份: 主库 → 备份存储（每日全量）

风险点:
├── 短信平台是否可信（数据外发风险）
├── 数据仓库是否做了访问控制（内部泄露风险）
├── 缓存数据是否设置过期（数据留存风险）
└── 备份数据是否加密（备份泄露风险）
```

---

## 二、数据分类分级标准

### 2.1 分级框架

根据 GB/T 35273《个人信息安全规范》和相关法规要求，数据分级通常分为四级：

| 等级 | 名称 | 说明 | 示例 | 保护要求 |
|------|------|------|------|----------|
| L1 | 公开数据 | 可公开的数据 | 官网公告、公开产品信息 | 完整性保护 |
| L2 | 内部数据 | 仅限内部使用 | 内部文档、系统配置 | 访问控制+日志审计 |
| L3 | 机密数据 | 限定授权人员 | 员工信息、经营数据 | 加密+细粒度权限+审计 |
| L4 | 绝密数据 | 极少数人知晓 | 核心源码、密钥、金融核心数据 | 强加密+物理隔离+多重认证 |

### 2.2 GB/T 35273 个人信息分类

```
个人信息分类（GB/T 35273）:

个人基本信息:
├── 姓名、性别、年龄
├── 身份证号、护照号
├── 民族、籍贯
└── 个人照片

个人敏感信息:
├── 生物识别信息（指纹、人脸、虹膜）
├── 身份证号（敏感标识）
├── 医疗健康信息（病历、体检报告）
├── 金融账户信息（银行卡号、信用分）
├── 通信记录（通话记录、短信内容）
├── 行踪轨迹信息（GPS定位、出行记录）
├── 14岁以下儿童信息（特殊保护）
└── 其他法律法规定义的敏感信息

个人财产信息:
├── 收入、存款
├── 房产、车辆信息
├── 交易记录
└── 信用记录

网络身份信息:
├── 账号、密码
├── IP地址、设备标识
├── Cookie、Session
└── 数字证书
```

### 2.3 分类分级操作指南

```python
# 数据分类分级规则引擎示例

class DataClassificationEngine:
    """
    数据自动分类分级引擎
    """
    
    # 分类规则配置
    CLASSIFICATION_RULES = {
        'personal_sensitive': {
            'level': 'L4',  # 绝密
            'patterns': {
                'fingerprint': r'fingerprint|finger_print|fp_',
                'face': r'face_id|face_data|facial',
                'medical': r'medical|health|diagnosis|patient',
                'bank_account': r'bank_card|card_no|account_no|iban',
            }
        },
        'personal_basic': {
            'level': 'L3',  # 机密
            'patterns': {
                'id_card': r'身份证|idcard|id_card|cert_no',
                'phone': r'手机|phone|mobile|tel',
                'address': r'地址|address|addr',
                'name': r'姓名|real_name|fullname',
            }
        },
        'business_internal': {
            'level': 'L2',  # 内部
            'patterns': {
                'config': r'config|password|secret|api_key',
                'business': r'订单|order|交易|transaction',
            }
        },
        'public': {
            'level': 'L1',  # 公开
            'patterns': {
                'announcement': r'公告|notice|announcement',
            }
        }
    }
    
    # 分级后的保护措施要求
    PROTECTION_MEASURES = {
        'L4': {
            'encryption': 'AES-256 或国密SM4',
            'access_control': 'RBAC + ABAC，最小授权',
            'audit': '全量操作日志，实时告警',
            'storage': '独立加密存储，物理隔离',
            'transmission': 'TLS 1.3 + 端到端加密',
            'retention': '最短保留期，到期销毁'
        },
        'L3': {
            'encryption': 'AES-128 或国密SM4',
            'access_control': 'RBAC，角色权限',
            'audit': '操作日志记录',
            'storage': '加密存储',
            'transmission': 'TLS 1.2+',
            'retention': '合规保留期'
        },
        'L2': {
            'encryption': '可选加密',
            'access_control': '基本访问控制',
            'audit': '关键操作日志',
            'storage': '访问受控',
            'transmission': 'HTTPS',
            'retention': '按需保留'
        },
        'L1': {
            'encryption': '无需加密',
            'access_control': '公开访问',
            'audit': '变更日志',
            'storage': '普通存储',
            'transmission': 'HTTPS 推荐',
            'retention': '按需保留'
        }
    }
    
    def classify(self, data_element):
        """
        对数据元素进行分类分级
        """
        for category, rule in self.CLASSIFICATION_RULES.items():
            for field_type, pattern in rule['patterns'].items():
                if re.search(pattern, data_element.get('name', ''), re.I):
                    return {
                        'category': category,
                        'field_type': field_type,
                        'level': rule['level'],
                        'protection': self.PROTECTION_MEASURES[rule['level']]
                    }
        
        # 默认为内部级别
        return {
            'category': 'unknown',
            'level': 'L2',
            'protection': self.PROTECTION_MEASURES['L2']
        }
```

---

## 三、数据资产盘点工具

### 3.1 数据目录工具

| 工具 | 类型 | 功能 | 适用场景 |
|------|------|------|----------|
| Apache Atlas | 开源 | 数据治理+血缘分析 | Hadoop/大数据生态 |
| DataHub | 开源 | 元数据管理 | 多数据源统一管理 |
| Amundsen | 开源 | 数据发现+目录 | 数据科学家自助发现 |
| Collibra | 商业 | 全面的数据治理 | 企业级数据治理 |
| Alation | 商业 | 数据目录+协作 | 数据民主化 |
| 360数据资产地图 | 国产 | 资产盘点+分类分级 | 合规驱动 |

### 3.2 数据血缘追踪

```sql
-- 数据血缘追踪示例 - 追踪敏感数据来源

-- 查询包含手机号的表及其上下游依赖
WITH sensitive_tables AS (
    SELECT table_name, column_name 
    FROM information_schema.columns 
    WHERE column_name LIKE '%phone%' 
       OR column_name LIKE '%mobile%'
),
upstream_sources AS (
    -- 查询 ETL 作业中引用这些表的上游来源
    SELECT 
        t.table_name AS target_table,
        t.column_name AS target_column,
        s.source_table,
        s.source_column,
        s.etl_job_name,
        s.schedule
    FROM sensitive_tables t
    JOIN etl_lineage s ON s.target_table = t.table_name
    AND s.target_column = t.column_name
)
SELECT * FROM upstream_sources;

-- 输出示例:
-- target_table | target_column | source_table | source_column | etl_job
-- user_orders  | phone         | users        | mobile        | sync_users_to_orders
-- marketing_db | contact_phone | user_orders  | phone         | daily_marketing_sync
```

---

## 四、API 数据安全概述

### 4.1 API 数据流

```
API 数据流转全景:

数据存储层
├── 数据库（MySQL/PostgreSQL/MongoDB）
├── 缓存（Redis/Memcached）
├── 对象存储（OSS/S3）
└── 数据仓库

API 后端层
├── API 网关（认证/限流/路由）
├── 微服务（业务逻辑）
├── 数据访问层（ORM/查询）
└── 数据脱敏中间件

网络传输层
├── HTTPS/TLS 加密传输
├── 证书绑定（移动端）
└── API 签名验证

客户端层
├── Web 前端（浏览器）
├── 移动 App
├── 第三方接入方
└── 内部系统调用

数据暴露面风险:
├── API 返回过多数据字段（过度暴露）
├── 缺乏字段级权限控制
├── 分页不当导致全量数据遍历
├── 搜索/导出接口无限制
└── API 文档泄露数据结构
```

---

## 五、OWASP API Security Top 10

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

## 六、API 安全网关

### 6.1 网关安全能力

```
API 安全网关架构:

客户端请求 → [API网关] → 后端服务
                │
    ┌───────────┼───────────┐
    │           │           │
认证鉴权     限流控制     请求过滤
├─ JWT验证   ├─ 令牌桶     ├─ WAF规则
├─ OAuth2    ├─ 滑动窗口   ├─ SQL注入防护
├─ API Key   ├─ 并发控制   ├─ XSS过滤
└─ 签名验证   └─ 熔断降级   └─ CSRF防护
    │
响应处理
├─ 数据脱敏
├─ 字段过滤
├─ 响应签名
└─ 日志审计
```

### 6.2 限流配置示例

```yaml
# API 限流策略配置 (Kong网关)

plugins:
  # IP级限流 - 防暴力破解
  - name: rate-limiting
    config:
      minute: 30           # 每IP每分钟30次
      hour: 500            # 每IP每小时500次
      policy: redis
      redis:
        host: redis.internal
        port: 6379
      fault_tolerant: true  # Redis宕机时降级为本地限流

  # 用户级限流 - 防滥用
  - name: rate-limiting
    route: user-api
    config:
      minute: 60           # 每用户每分钟60次
      limit_by: credential  # 按认证凭据限流
      policy: redis

  # 请求大小限制
  - name: request-size-limiting
    config:
      allowed_payload_size: 5  # 最大5MB

  # IP黑白名单
  - name: ip-restriction
    config:
      blacklist:
        - 10.0.0.0/8       # 禁止内网段(防SSRF)
```

```python
# 自定义限流中间件示例 (Python Flask)
from functools import wraps
from redis import Redis
from flask import request, jsonify

redis = Redis(host='redis.internal', port=6379, decode_responses=True)

def rate_limit(limit=100, window=60, key_func=None):
    """
    API 速率限制装饰器
    limit: 窗口内最大请求数
    window: 时间窗口(秒)
    key_func: 限流键函数(默认IP+用户)
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # 生成限流键
            if key_func:
                key = key_func()
            else:
                # 默认: IP + 用户Token
                ip = request.headers.get('X-Forwarded-For', 
                                        request.remote_addr)
                token = request.headers.get('Authorization', 'anonymous')
                key = f"rate_limit:{ip}:{token}"
            
            # 滑动窗口计数
            pipe = redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, window)
            count, _ = pipe.execute()
            
            if count > limit:
                # 返回429 Too Many Requests
                return jsonify({
                    'error': 'Too Many Requests',
                    'message': f'请求频率超过限制: {limit}次/{window}秒',
                    'retry_after': window
                }), 429
            
            # 添加限流头
            response = f(*args, **kwargs)
            response.headers['X-RateLimit-Limit'] = str(limit)
            response.headers['X-RateLimit-Remaining'] = str(
                max(0, limit - count)
            )
            return response
        return wrapper
    return decorator

# 使用示例
@app.route('/api/v1/orders', methods=['GET'])
@auth_required
@rate_limit(limit=60, window=60)  # 每分钟60次
def list_orders():
    ...
```

### 6.3 API 数据脱敏

```python
# 动态数据脱敏中间件

class DataMasker:
    """
    响应数据动态脱敏
    根据用户角色和数据敏感级别，对API响应中的敏感字段进行脱敏
    """
    
    MASK_RULES = {
        'phone': lambda x: x[:3] + '****' + x[-4:] if len(x) >= 8 else '****',
        'email': lambda x: x[0] + '***@' + x.split('@')[1] if '@' in x else '***',
        'id_card': lambda x: x[:6] + '********' + x[-4:] if len(x) >= 18 else '****',
        'bank_card': lambda x: x[:4] + '********' + x[-4:] if len(x) >= 16 else '****',
        'name': lambda x: x[0] + '*' * (len(x) - 1) if len(x) > 1 else '*',
        'address': lambda x: x[:6] + '***' if len(x) > 6 else '***',
    }
    
    # 角色级别的脱敏策略
    ROLE_POLICIES = {
        'admin': {
            # 管理员可看到更多数据
            'phone': 'partial',     # 138****8000
            'email': 'partial',     # z***@example.com
            'id_card': 'masked',    # 110101********1234
        },
        'customer_service': {
            'phone': 'masked',      # 138****8000
            'email': 'masked',      # z***@example.com
            'id_card': 'hidden',    # ***
        },
        'external_partner': {
            'phone': 'hidden',      # ***
            'email': 'masked',      # z***@example.com
            'id_card': 'hidden',    # ***
        }
    }
    
    def mask_response(self, data, user_role, field_types):
        """
        根据用户角色对响应数据进行脱敏
        data: 原始数据
        user_role: 用户角色
        field_types: {字段名: 数据类型}
        """
        policy = self.ROLE_POLICIES.get(user_role, 
                                         self.ROLE_POLICIES['external_partner'])
        
        if isinstance(data, dict):
            masked = {}
            for key, value in data.items():
                field_type = field_types.get(key)
                if field_type and field_type in self.MASK_RULES:
                    action = policy.get(field_type, 'masked')
                    if action == 'hidden':
                        masked[key] = '***'
                    elif action == 'partial':
                        masked[key] = value  # 部分角色可看原始数据
                    else:  # masked
                        masked[key] = self.MASK_RULES[field_type](str(value))
                else:
                    masked[key] = value
            return masked
        elif isinstance(data, list):
            return [self.mask_response(item, user_role, field_types) 
                    for item in data]
        return data


# 使用示例 - API 响应中间件
@app.route('/api/v1/users/<int:user_id>')
@auth_required
def get_user(user_id):
    user = get_user_from_db(user_id)
    
    # 当前用户角色
    role = g.current_user.role
    
    # 字段类型映射
    field_types = {
        'phone': 'phone',
        'email': 'email',
        'id_card': 'id_card',
        'name': 'name',
        'address': 'address'
    }
    
    # 动态脱敏
    masker = DataMasker()
    masked_user = masker.mask_response(
        user.to_dict(), role, field_types
    )
    
    return jsonify(masked_user)
```

---

## 七、数据安全成熟度评估模型（DSMM）

### 7.1 DSMM 概述

**DSMM（Data Security capability Maturity Model，数据安全能力成熟度模型）** 是 GB/T 37988 国家标准，为企业数据安全能力提供评估框架。

### 7.2 成熟度等级

| 等级 | 名称 | 特征 | 典型表现 |
|------|------|------|----------|
| L1 | 非正式执行 | 临时性、个人化 | 依赖个人能力，无统一标准 |
| L2 | 计划跟踪 | 基本规范 | 有流程文档，按计划执行 |
| L3 | 充分定义 | 标准化、体系化 | 全组织统一流程和标准 |
| L4 | 量化控制 | 可度量、可优化 | 有量化指标，持续改进 |
| L5 | 持续优化 | 自适应、智能化 | 自动化运营，行业标杆 |

### 7.3 DSMM 能力维度

```
DSMM 六大能力域:

1. 数据采集安全
   ├── 数据分类分级
   ├── 数据源安全评估
   └── 合法合规采集

2. 数据传输安全
   ├── 加密传输
   ├── 传输通道安全
   └── 传输内容保护

3. 数据存储安全
   ├── 存储加密
   ├── 访问控制
   └── 存储介质安全

4. 数据处理安全
   ├── 数据脱敏
   ├── 数据分析安全
   └── 数据导出控制

5. 数据交换安全
   ├── 数据共享安全
   ├── 数据发布安全
   └── 数据接口安全

6. 数据销毁安全
   ├── 数据删除
   ├── 介质销毁
   └── 销毁审计
```

---

## 八、实战案例：企业数据资产盘点与分级实践

### 8.1 案例背景

某电商企业拥有用户数据 5000 万条，涉及多个业务系统（用户中心、订单系统、支付系统、营销系统），需要进行全面数据资产盘点和安全分级。

### 8.2 实施步骤

```
阶段1: 资产清点（2周）
├── 自动扫描
│   ├── 数据库扫描 → 发现 320 张表
│   ├── API 接口枚举 → 发现 156 个API
│   ├── 文件存储扫描 → 发现 45TB 数据文件
│   └── 日志系统扫描 → 发现 12 类日志
├── 手动补充
│   ├── 各业务部门申报数据资产
│   ├── 确认数据责任人和使用人
│   └── 标注业务上下文
└── 输出: 数据资产清单（v1.0）

阶段2: 分类分级（2周）
├── 自动分级引擎执行
│   ├── 基于列名匹配 → 标记 1850 个敏感字段
│   ├── 基于数据采样 → 补充发现 320 个敏感字段
│   └── 人工复核 → 确认 2170 个敏感字段
├── 分级结果
│   ├── L4 绝密: 68 字段（密码哈希、支付密钥、核心算法）
│   ├── L3 机密: 542 字段（手机号、地址、订单金额）
│   ├── L2 内部: 980 字段（商品信息、运营数据）
│   └── L1 公开: 580 字段（公告、产品介绍）
└── 输出: 数据分类分级表

阶段3: 风险评估（1周）
├── 识别数据暴露面
│   ├── 12个API返回了过多敏感字段
│   ├── 5个导出接口缺少权限控制
│   ├── 3个第三方数据共享未签协议
│   └── 2个数据库未加密存储
├── 评估风险等级
│   ├── 高风险: 8项（需立即修复）
│   ├── 中风险: 15项（限期修复）
│   └── 低风险: 22项（计划修复）
└── 输出: 数据安全风险评估报告

阶段4: 整改实施（4周）
├── API 安全改造
│   ├── 响应字段白名单过滤
│   ├── 敏感字段动态脱敏
│   ├── 导出接口增加审批流程
│   └── API 网关限流配置
├── 存储安全加固
│   ├── 数据库字段级加密
│   ├── 文件存储加密
│   └── 访问权限收敛
└── 第三方数据共享治理
    ├── 签订数据处理协议
    ├── 建立共享审计机制
    └── 最小化数据提供

阶段5: 持续运营
├── 建立数据资产台账（动态更新）
├── 定期扫描（每月增量）
├── 分级标签自动化
└── DSMM 成熟度评估（年度）
```

### 8.3 关键成果

```
项目成果总结:

数据资产清单:
├── 数据库表: 320 张
├── API 接口: 156 个
├── 数据文件: 45TB
├── 敏感字段: 2170 个
└── 数据责任人: 28 人

安全改进:
├── 高风险整改: 8/8 (100%)
├── 中风险整改: 15/15 (100%)
├── API 过度暴露减少: 80%
├── 敏感数据加密覆盖: 95%
└── DSMM 成熟度: L2 → L3
```

---

> **学习建议**：数据资产发现和 API 安全是数据安全治理的核心环节。建议学习者熟悉 GB/T 35273 和 OWASP API Security Top 10 标准，在实验环境中搭建 API 服务并练习越权漏洞挖掘、数据脱敏配置等实操技能。理解 DSMM 框架，思考如何将安全要求落地到企业实际数据管理流程中。
