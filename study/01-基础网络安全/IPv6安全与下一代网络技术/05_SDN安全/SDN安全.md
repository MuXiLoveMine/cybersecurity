# SDN安全

### 4.1 SDN架构概述

SDN（Software-Defined Networking，软件定义网络）将网络控制平面与数据平面分离，通过集中式控制器管理网络转发行为。

```
SDN三层架构：

┌─────────────────────────────────────┐
│         应用层（Application Layer）    │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  │负载均衡  │ │防火墙   │ │QoS     │ │
│  └─────────┘ └─────────┘ └────────┘ │
│         ↑ Northbound API ↑            │
├─────────────────────────────────────┤
│         控制层（Control Layer）       │
│  ┌─────────────────────────────────┐ │
│  │     SDN控制器（Controller）       │ │
│  │  ┌─────┐ ┌─────┐ ┌─────────┐  │ │
│  │  │拓扑 │ │路由 │ │流表管理  │  │ │
│  │  └─────┘ └─────┘ └─────────┘  │ │
│  └─────────────────────────────────┘ │
│         ↓ Southbound API ↓           │
├─────────────────────────────────────┤
│         数据层（Data Layer）          │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐│
│  │SW1 │ │SW2 │ │SW3 │ │SW4 │ │SW5 ││
│  └────┘ └────┘ └────┘ └────┘ └────┘│
└─────────────────────────────────────┘
```

### 4.2 控制器安全

SDN控制器是整个网络的大脑，一旦被攻破，攻击者可以控制整个网络。

**控制器安全威胁：**

1. **未授权访问**：控制器API未做认证
2. **权限提升**：应用通过API获取超额权限
3. **DoS攻击**：大量流表请求导致控制器过载
4. **恶意应用**：SDN应用中植入恶意逻辑

**控制器安全防护：**

```python
# ONOS控制器安全配置示例

# 1. 访问控制
# org.onosproject.security配置
security {
    # 启用应用权限管理
    enabled: true
    # 应用权限白名单
    permissions {
        "org.onosproject.intent" {
            "READ": ["device", "host", "link", "topology"]
            "WRITE": ["flowrule", "intent"]
        }
    }
    # 禁止应用反射调用
    enforce: true
}

# 2. 速率限制
# 限制每个交换机的Packet-In速率
olt {
    packetInRate: 1000  # 每秒最大1000个Packet-In
    flowModRate: 500    # 每秒最大500个流表修改
}

# 3. 控制器自身安全
# 启用TLS
tls {
    enabled: true
    keyStore: "/etc/onos/keystore.jks"
    keyStorePassword: "changeit"
    trustStore: "/etc/onos/truststore.jks"
    trustStorePassword: "changeit"
}
```

**OpenDaylight安全配置：**

```xml
<!-- OpenDaylight AAA认证配置 -->
<feature-repository>
  <feature name="odl-aaa-shiro">
    <config>
      <shiro>
        <enabled>true</enabled>
        <sessionIdCookieName>JSESSIONID</sessionIdCookieName>
        <sessionTimeout>3600</sessionTimeout>
      </shiro>
      <users>
        <user>
          <name>admin</name>
          <password>{SHA}encrypted_password</password>
          <roles>admin</roles>
        </user>
      </users>
    </config>
  </feature>
</feature-repository>
```

### 4.3 南北向API安全

**北向API安全（控制器与应用之间）：**

```python
# REST API认证与授权
from flask import Flask, request, jsonify
import jwt
from functools import wraps

app = Flask(__name__)
SECRET_KEY = "your-secret-key"

# JWT认证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token missing'}), 401

        try:
            data = jwt.decode(token.replace('Bearer ', ''),
                            SECRET_KEY, algorithms=['HS256'])
            request.user = data
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)
    return decorated

# 流表安装API
@app.route('/api/v1/flows', methods=['POST'])
@token_required
def install_flow():
    # 权限检查
    if request.user.get('role') != 'admin':
        return jsonify({'error': 'Permission denied'}), 403

    flow = request.json

    # 输入验证（防止注入）
    if not validate_flow(flow):
        return jsonify({'error': 'Invalid flow'}), 400

    # 速率限制
    if rate_limit_exceeded(request.user['id']):
        return jsonify({'error': 'Rate limit exceeded'}), 429

    result = install_flow_rule(flow)
    return jsonify(result), 201

# 输入验证函数
def validate_flow(flow):
    required = ['switch_id', 'match', 'actions']
    if not all(k in flow for k in required):
        return False
    # 验证switch_id格式
    if not re.match(r'^[a-f0-9:]{1,32}$', flow['switch_id']):
        return False
    # 验证match和actions不包含恶意内容
    if ';' in str(flow) or '|' in str(flow):
        return False
    return True
```

**南向API安全（控制器与交换机之间）：**

```
# OpenFlow TLS配置
# 控制器端（OVS示例）
ovs-vsctl set-manager ptcp:6640
ovs-vsctl set-manager ssl:0.0.0.0:6653

# 配置证书
ovs-vsctl set-ssl /etc/openvswitch/ctl-privkey.pem \
                   /etc/openvswitch/ctl-cert.pem \
                   /etc/openvswitch/cacert.pem

# 交换机端配置
ovs-vsctl set-controller br0 \
  ssl:192.168.1.100:6653 \
  --certificate=/etc/openvswitch/sc-cert.pem \
  --private-key=/etc/openvswitch/sc-privkey.pem \
  --ca-cert=/etc/openvswitch/cacert.pem

# 流表安全规则
# 限制控制器可安装的流表优先级范围
ovs-vsctl set bridge br0 \
  flow-limit=1000 \
  flow-table-miss-handling=true
```

### 4.4 流表安全

流表是SDN交换机的转发规则，攻击者可能通过注入恶意流表规则来劫持流量。

**流表攻击场景：**

```
1. 流表泛洪攻击：
   攻击者通过控制器安装大量流表规则
   → 交换机TCAM溢出 → 正常流表被驱逐

2. 流表劫持：
   安装高优先级恶意流表规则
   → 将流量重定向到攻击者

3. 流表时序攻击：
   利用流表超时时间差异
   → 在规则过期后劫持流量
```

**流表安全防护策略：**

```python
# 流表安全验证模块

class FlowTableValidator:
    def __init__(self):
        self.max_flows_per_switch = 1000
        self.max_flows_per_tenant = 100
        self.allowed_match_fields = [
            'in_port', 'eth_src', 'eth_dst',
            'ipv4_src', 'ipv4_dst',
            'ipv6_src', 'ipv6_dst',
            'tcp_src', 'tcp_dst',
            'udp_src', 'udp_dst'
        ]
        self.blocked_actions = [
            'output:CONTROLLER',  # 阻止转发到控制器（防止packet-in攻击）
        ]

    def validate_flow(self, flow, tenant_id, switch_id):
        """验证流表规则安全性"""
        # 1. 检查流表数量限制
        if self.get_flow_count(switch_id) >= self.max_flows_per_switch:
            return False, "Flow table full"

        if self.get_tenant_flow_count(tenant_id, switch_id) >= self.max_flows_per_tenant:
            return False, "Tenant flow limit exceeded"

        # 2. 验证match字段
        for field in flow.get('match', {}):
            if field not in self.allowed_match_fields:
                return False, f"Field {field} not allowed"

        # 3. 验证action安全性
        for action in flow.get('actions', []):
            if any(blocked in str(action) for blocked in self.blocked_actions):
                return False, f"Blocked action: {action}"

            # 检查output端口是否合法
            if action.startswith('output:'):
                port = action.split(':')[1]
                if not self.is_valid_port(switch_id, port):
                    return False, f"Invalid port: {port}"

        # 4. 检查优先级范围
        priority = flow.get('priority', 0)
        if priority > 100 or priority < 0:
            return False, "Priority out of range"

        # 5. 检查超时设置
        idle_timeout = flow.get('idle_timeout', 0)
        hard_timeout = flow.get('hard_timeout', 0)
        if idle_timeout == 0 and hard_timeout == 0:
            return False, "Must have timeout"

        return True, "Valid"

    def detect_flow_injection(self, switch_id):
        """检测异常流表注入"""
        # 统计最近1分钟新增流表数
        recent_flows = self.get_recent_flows(switch_id, window=60)
        if len(recent_flows) > 50:  # 每分钟超过50条
            # 触发告警
            self.alert("Possible flow injection attack", switch_id)
            return True

        # 检测异常模式
        for flow in recent_flows:
            # 检测全通配流表（转发所有流量）
            if self.is_wildcard_flow(flow):
                self.alert("Wildcard flow detected", switch_id, flow)
            # 检测镜像端口流表
            if self.is_mirror_flow(flow):
                self.alert("Mirror flow detected", switch_id, flow)

        return False
```

---

---

## 📋 内容审核与补充建议

> 针对「SDN安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
