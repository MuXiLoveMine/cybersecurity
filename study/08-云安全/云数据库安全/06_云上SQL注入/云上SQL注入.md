# 云上SQL注入

### 5.1 注入风险场景

```python
# 危险代码示例 - 直接拼接SQL
def get_user(user_id):
    # 不安全：直接拼接用户输入
    sql = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(sql)
    return cursor.fetchone()

# 攻击者输入: 1 OR 1=1
# 实际执行: SELECT * FROM users WHERE id = 1 OR 1=1
# 返回所有用户数据

# NoSQL注入
def search_users(keyword):
    # 不安全：直接传递用户输入作为查询条件
    db.users.find({"$where": f"this.name == '{keyword}'"})

# 攻击者输入: '; while(1){}; '
# 导致DoS
```

### 5.2 防御措施

```python
# 安全代码 - 参数化查询
def get_user_safe(user_id):
    # 安全：使用参数化查询
    sql = "SELECT * FROM users WHERE id = %s"
    cursor.execute(sql, (user_id,))
    return cursor.fetchone()

# ORM安全使用
def get_user_orm(user_id):
    # 安全：ORM自动参数化
    return User.query.filter_by(id=user_id).first()

# 输入验证
import re

def validate_input(input_str, max_length=100):
    """验证用户输入"""
    if not input_str or len(input_str) > max_length:
        raise ValueError("Invalid input length")
    # 白名单字符检查
    if not re.match(r'^[a-zA-Z0-9_\-]+$', input_str):
        raise ValueError("Invalid characters")
    return input_str
```

---

---

## 📋 内容审核与补充建议

> 针对「云上SQL注入」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
