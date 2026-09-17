# Python 数据库安全检查脚本示例

### 9.1 MySQL 安全配置检查脚本

```python
import pymysql

def check_mysql_security(host, port, user, password):
    """MySQL 安全配置检查"""
    findings = []
    try:
        conn = pymysql.connect(
            host=host, port=port, user=user, password=password
        )
        cursor = conn.cursor()

        # 检查 1: 匿名用户
        cursor.execute("SELECT COUNT(*) FROM mysql.user WHERE User=''")
        count = cursor.fetchone()[0]
        if count > 0:
            findings.append("[高危] 存在匿名用户账户")
        else:
            findings.append("[正常] 无匿名用户")

        # 检查 2: root 远程登录
        cursor.execute(
            "SELECT Host FROM mysql.user WHERE User='root' "
            "AND Host NOT IN ('localhost','127.0.0.1','::1')"
        )
        remote_roots = cursor.fetchall()
        if remote_roots:
            findings.append(f"[高危] root 允许远程登录: {remote_roots}")
        else:
            findings.append("[正常] root 仅限本地登录")

        # 检查 3: test 数据库
        cursor.execute("SHOW DATABASES LIKE 'test'")
        if cursor.fetchone():
            findings.append("[中危] 存在 test 测试数据库")
        else:
            findings.append("[正常] 无 test 数据库")

        # 检查 4: 密码强度
        cursor.execute(
            "SELECT User, Host FROM mysql.user "
            "WHERE authentication_string='' OR authentication_string IS NULL"
        )
        empty_pwd = cursor.fetchall()
        if empty_pwd:
            findings.append(f"[高危] 空密码用户: {empty_pwd}")
        else:
            findings.append("[正常] 所有用户均已设置密码")

        # 检查 5: secure_file_priv 配置
        cursor.execute("SHOW VARIABLES LIKE 'secure_file_priv'")
        result = cursor.fetchone()
        if result and result[1] == '':
            findings.append("[中危] secure_file_priv 为空，存在文件读写风险")
        else:
            findings.append(f"[正常] secure_file_priv = {result[1] if result else 'N/A'}")

        # 检查 6: 是否启用审计日志
        cursor.execute("SHOW VARIABLES LIKE 'general_log%'")
        log_status = cursor.fetchone()
        if log_status and log_status[2] == 'ON':
            findings.append("[正常] General Log 已启用")
        else:
            findings.append("[低危] General Log 未启用")

        cursor.close()
        conn.close()
    except Exception as e:
        findings.append(f"[错误] 连接失败: {e}")

    return findings


if __name__ == '__main__':
    results = check_mysql_security(
        host='127.0.0.1', port=3306,
        user='root', password='your_password'
    )
    print("=" * 60)
    print("MySQL 安全配置检查报告")
    print("=" * 60)
    for r in results:
        print(f"  {r}")
    print("=" * 60)
```

### 9.2 MongoDB 未授权访问检测脚本

```python
import socket
from pymongo import MongoClient

def check_mongodb_unauth(host, port=27017, timeout=3):
    """检测 MongoDB 未授权访问"""
    result = {"host": host, "port": port, "vulnerable": False, "details": []}

    # 步骤 1: 检查端口是否开放
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
    except (socket.timeout, ConnectionRefusedError):
        result["details"].append("端口未开放或连接超时")
        return result

    # 步骤 2: 尝试无认证连接
    try:
        client = MongoClient(
            host, port,
            serverSelectionTimeoutMS=timeout * 1000,
            directConnection=True
        )

        # 尝试执行管理员命令（无需认证）
        try:
            info = client.server_info()
            result["details"].append(
                f"版本: {info.get('version', 'unknown')}"
            )
        except Exception:
            pass

        # 尝试列出所有数据库
        try:
            db_list = client.list_database_names()
            if db_list:
                result["vulnerable"] = True
                result["details"].append(
                    f"[高危] 无认证即可访问，发现数据库: {db_list}"
                )
            else:
                result["details"].append("无认证连接成功但未发现数据库")
        except Exception as e:
            if "not authorized" in str(e).lower():
                result["details"].append("[正常] 需要认证，未授权访问被拒绝")
            else:
                result["details"].append(f"认证检查异常: {e}")

        client.close()
    except Exception as e:
        result["details"].append(f"连接异常: {e}")

    return result


if __name__ == '__main__':
    print("=" * 60)
    print("MongoDB 未授权访问检测")
    print("=" * 60)

    target = input("请输入目标 IP（默认 127.0.0.1）: ").strip()
    if not target:
        target = "127.0.0.1"

    report = check_mongodb_unauth(target)

    print(f"\n目标: {report['host']}:{report['port']}")
    print(f"存在未授权访问: {'是 [高危]' if report['vulnerable'] else '否'}")
    print("详情:")
    for d in report["details"]:
        print(f"  - {d}")
    print("=" * 60)

    if report["vulnerable"]:
        print("\n修复建议:")
        print("  1. 在 mongod.conf 中设置 security.authorization: enabled")
        print("  2. 创建管理员用户并设置强密码")
        print("  3. 绑定内网 IP: net.bindIp")
        print("  4. 启用 TLS 加密传输")
```

---

---

## 📋 内容审核与补充建议

> 针对「Python 数据库安全检查脚本示例」部分的内容审核结果：

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
