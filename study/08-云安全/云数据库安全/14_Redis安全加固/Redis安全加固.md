# Redis安全加固

### 14.1 Redis安全配置

```bash
# redis.conf 安全配置

# 绑定地址(仅本地和内网)
bind 10.0.1.10 127.0.0.1

# 禁用危险命令
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""
rename-command KEYS ""
rename-command DEBUG ""
rename-command SHUTDOWN ""

# 启用认证
requirepass Str0ng!Redis#Passw0rd@2026

# 配置ACL(Redis 6+)
# 在redis.conf中或使用ACL命令
user default off
user appuser on >Str0ngPassw0rd ~app:* +get +set +del +expire +ttl -@all
user admin on >AdminPassw0rd ~* +@all -flushdb -flushall

# 启用TLS
port 0
tls-port 6379
tls-cert-file /etc/redis/redis.crt
tls-key-file /etc/redis/redis.key
tls-ca-cert-file /etc/redis/ca.crt
tls-auth-clients yes

# 限制最大客户端连接
maxclients 1000

# 内存限制(防止OOM)
maxmemory 2gb
maxmemory-policy allkeys-lru

# 禁用Lua沙箱执行危险操作
lua-time-limit 5000
```

### 14.2 Redis漏洞与防护

```python
# Redis未授权访问检测脚本
import redis
import socket

def check_redis_security(host, port=6379):
    """检测Redis安全配置"""
    findings = []

    # 1. 检查未授权访问
    try:
        r = redis.Redis(host=host, port=port, socket_timeout=5)
        info = r.info()
        findings.append({
            'severity': 'CRITICAL',
            'issue': 'Redis无需认证即可访问',
            'detail': f"Redis版本: {info.get('redis_version')}"
        })
    except redis.exceptions.AuthenticationError:
        findings.append({
            'severity': 'INFO',
            'issue': 'Redis已启用认证(良好)'
        })
    except redis.exceptions.ConnectionError:
        findings.append({
            'severity': 'INFO',
            'issue': '无法连接Redis(端口关闭或防火墙)'
        })
        return findings

    # 2. 检查危险命令是否可用
    dangerous_commands = ['CONFIG', 'FLUSHDB', 'FLUSHALL', 'KEYS', 'DEBUG']
    for cmd in dangerous_commands:
        try:
            r.execute_command(cmd)
        except redis.exceptions.ResponseError as e:
            if "unknown command" in str(e).lower():
                findings.append({
                    'severity': 'GOOD',
                    'issue': f'{cmd}命令已禁用(良好)'
                })
        except:
            findings.append({
                'severity': 'HIGH',
                'issue': f'{cmd}命令可用(危险)'
            })

    # 3. 检查绑定地址
    if 'redis_version' in info:
        try:
            config_get = r.config_get('bind')
            bind = config_get.get('bind', '')
            if '0.0.0.0' in bind or not bind:
                findings.append({
                    'severity': 'CRITICAL',
                    'issue': 'Redis绑定0.0.0.0(公网可访问)'
                })
        except:
            pass

    # 4. 检查是否启用TLS
    try:
        tls_info = r.config_get('tls-port')
        if tls_info.get('tls-port', '0') == '0':
            findings.append({
                'severity': 'MEDIUM',
                'issue': 'Redis未启用TLS加密'
            })
    except:
        pass

    return findings

# 批量检测
targets = ['10.0.1.10', '10.0.1.11', '10.0.2.20']
for target in targets:
    print(f"\n检测目标: {target}")
    results = check_redis_security(target, 6379)
    for r in results:
        print(f"  [{r['severity']}] {r['issue']}")
```

---

---

