# Python 框架安全

### 3.1 Django 安全

**Django ORM SQL 注入**

Django ORM 默认使用参数化查询，安全度高。但 `QuerySet.extra()` 和 `RawSQL()` 可绕过保护，`raw()` 方法接收原始 SQL 时若拼接用户输入则可注入。CVE-2022-28346 修复了 `QuerySet.order_by()` 接受整数参数时的注入问题。

**模板注入（SSTI）**

Django 模板引擎默认开启自动转义（auto-escape），XSS 风险较低。但 `mark_safe()` 标记内容为安全后会跳过转义，若标记了用户可控数据则导致 XSS。Django 模板本身不支持任意 Python 代码执行，SSTI 风险低于 Flask/Jinja2。

**Security 中间件配置**

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    ...
]
SECURE_SSL_REDIRECT = True           # 强制 HTTPS
SECURE_HSTS_SECONDS = 31536000       # HSTS 一年
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True    # 防 MIME 嗅探
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True         # Cookie 仅 HTTPS 传输
CSRF_COOKIE_SECURE = True
```

### 3.2 Flask 安全

**Jinja2 SSTI**

Flask 默认使用 Jinja2 模板。当用户输入被直接作为模板字符串渲染时（`render_template_string(user_input)`），攻击者可注入 `{{ }}` 语法调用 Python 内置对象链实现 RCE：

```python
# 危险
return render_template_string(request.args.get('name'))
# Payload: {{ ''.__class__.__mro__[1].__subclasses__()[xxx]('id',shell=True) }}
```

安全加固：
- 使用 `render_template()` 渲染文件模板，禁止 `render_template_string` 接收用户输入
- 开启 Jinja2 沙箱模式（`SandboxedEnvironment`）
- 对用户输入做字符串级别的输出编码，而非模板渲染

**Flask debug 模式风险**

`app.run(debug=True)` 启用 Werkzeug 调试器，允许在浏览器中执行任意 Python 代码（PIN 码可被爆破或预测）。生产环境严禁开启 debug，应使用 `waitress`/`gunicorn` 部署。

**Flask 安全加固清单**
- `SESSION_COOKIE_SECURE = True`、`SESSION_COOKIE_HTTPONLY = True`、`SESSION_COOKIE_SAMESITE = 'Lax'`
- `app.config['SECRET_KEY']` 使用随机长密钥，禁止硬编码默认值
- 启用 `flask_talisman` 添加安全响应头与 CSP
- `debug=False`，生产环境用 WSGI 服务器部署

### 3.3 FastAPI 安全

**输入验证**

FastAPI 基于 Pydantic 模型进行输入校验，类型不符自动拒绝。但仍需注意：
- 正则约束字段格式（邮箱、手机号）
- 字符串长度限制防 DoS
- 嵌套对象深度限制

```python
from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=20, pattern=r'^[a-zA-Z0-9_]+$')
```

**认证与授权**

FastAPI 内置 OAuth2 与 JWT 支持。注意 `Depends(get_current_user)` 必须覆盖所有需认证的路由，避免遗漏导致未授权访问。

---

---

## 📋 内容审核与补充建议

> 针对「Python 框架安全」部分的内容审核结果：

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
