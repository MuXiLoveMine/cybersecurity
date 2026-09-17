# Python 代码审计

### 4.1 Flask / Django 审计要点

| 框架 | 关注点 |
|------|--------|
| **Flask** | `render_template_string` SSTI、`debug=True` 信息泄露、`send_file` 路径穿越 |
| **Django** | `extra()` / `raw()` SQL 注入、`mark_safe` XSS、模板 `|safe` 过滤器 |

### 4.2 模板注入审计

```python
# —— 漏洞代码：Flask SSTI ——
from flask import Flask, request, render_template_string
app = Flask(__name__)

@app.route('/')
def index():
    name = request.args.get('name', '')
    template = f"<h1>Hello {name}</h1>"           # [高危] 用户输入直接拼入模板
    return render_template_string(template)       # 可执行 {{ config }} / {{ ''.__class__ }}
```

```python
# —— 修复代码 ——
@app.route('/')
def index():
    name = request.args.get('name', '')
    return render_template_string("<h1>Hello {{ name }}</h1>", name=name)  # 参数化
```

审计要点：搜索 `render_template_string`、`Template(`，检查模板字符串是否包含用户输入。Jinja2 中 `{{ }}` 语法可执行 Python 表达式。

### 4.3 SQL 注入审计

```python
# —— 漏洞代码：原生 SQL 拼接 ——
cursor.execute(f"SELECT * FROM users WHERE name = '{name}'")

# —— 漏洞代码：Django raw ——
User.objects.raw("SELECT * FROM users WHERE name = '%s'" % name)

# —— 漏洞代码：Django extra ——
User.objects.extra(where=["name = '%s'" % name])
```

```python
# —— 修复代码：参数化查询 ——
cursor.execute("SELECT * FROM users WHERE name = %s", (name,))

# —— 修复代码：Django ORM ——
User.objects.filter(name=name)

# —— 修复代码：Django raw 参数化 ——
User.objects.raw("SELECT * FROM users WHERE name = %s", [name])
```

### 4.4 反序列化审计

```python
# —— 漏洞代码：pickle ——
import pickle
data = request.get_data()
obj = pickle.loads(data)  # __reduce__ 可执行任意代码

# —— 漏洞代码：yaml.load ——
import yaml
config = yaml.load(request.data, Loader=yaml.Loader)  # 默认 Loader 支持任意 Python 对象
```

```python
# —— 修复代码 ——
import json
obj = json.loads(data)  # JSON 不支持代码执行

# yaml 修复
config = yaml.load(request.data, Loader=yaml.SafeLoader)  # SafeLoader 禁止任意对象
```

审计要点：搜索 `pickle.loads`、`yaml.load(`（注意区分 `load` 和 `safe_load`），检查反序列化输入是否来自用户。

### 4.5 命令注入审计

```python
# —— 漏洞代码 ——
import os
os.system("nslookup " + request.args.get('host'))

import subprocess
subprocess.call("ping " + host, shell=True)  # shell=True 时可注入
```

```python
# —— 修复代码 ——
import subprocess
host = request.args.get('host')
if not re.match(r'^[a-zA-Z0-9.\-]+$', host):
    abort(400)
result = subprocess.run(["ping", host], capture_output=True)  # 列表参数，shell=False
```

审计要点：搜索 `os.system`、`subprocess.call`、`subprocess.Popen`、`os.popen`，重点关注 `shell=True` 和字符串拼接。

### 4.6 审计实战：模拟审计 Flask 应用

```python
from flask import Flask, request, render_template_string
import pickle, subprocess

app = Flask(__name__)

@app.route('/')
def index():
    name = request.args.get('name', 'guest')
    return render_template_string(f'<h1>Hi {name}</h1>')   # [高危] SSTI

@app.route('/exec')
def exec_cmd():
    cmd = request.args.get('cmd')
    return subprocess.check_output(cmd, shell=True)         # [高危] 命令注入

@app.route('/config')
def load_config():
    data = request.cookies.get('config')
    return str(pickle.loads(data))                          # [高危] 反序列化 RCE
```

```python
# 修复后
@app.route('/')
def index():
    name = request.args.get('name', 'guest')
    return render_template_string('<h1>Hi {{ name }}</h1>', name=name)

@app.route('/exec')
def exec_cmd():
    cmd = request.args.get('cmd')
    allowed = {'uptime', 'df'}
    if cmd not in allowed:
        abort(403)
    return subprocess.check_output(cmd.split())

@app.route('/config')
def load_config():
    import json
    data = request.cookies.get('config')
    return str(json.loads(data))
```

---

---

## 📋 内容审核与补充建议

> 针对「Python 代码审计」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

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
