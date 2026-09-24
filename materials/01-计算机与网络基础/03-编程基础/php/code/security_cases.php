<?php
/**
 * security_cases.php —— PHP 安全案例集
 *
 * 涵盖内容（均从原理理解和防御角度）：
 *   案例 1：SQL 注入防御（危险版本 vs PDO 参数化查询）
 *   案例 2：XSS 防护（输出编码 + 输入验证 + CSP）
 *   案例 3：文件上传安全（白名单 + MIME + 文件头 + 随机文件名）
 *   案例 4：反序列化安全（JSON 替代 + 白名单类限制）
 *   案例 5：CSRF 防护（Token 验证机制）
 *
 * 运行方式：
 *   命令行: php security_cases.php [案例编号]
 *   浏览器: php -S 127.0.0.1:8000
 *           访问 http://127.0.0.1:8000/security_cases.php?case=1
 *
 * 重要提示：
 *   - 本文件仅用于安全学习和防御研究
 *   - 所有漏洞演示用于理解原理，不提供利用代码
 *   - 请在授权测试环境中运行
 *   - 重点关注每个案例的"修复方案"和"安全编码实践"
 */

ini_set('display_errors', 1);
error_reporting(E_ALL);

// ============================================================
// 辅助函数
// ============================================================

function printSection(string $title): void {
    echo PHP_EOL;
    echo "============================================================" . PHP_EOL;
    echo "  {$title}" . PHP_EOL;
    echo "============================================================" . PHP_EOL;
    echo PHP_EOL;
}

function printSubsection(string $title): void {
    echo PHP_EOL;
    echo "  --- {$title} ---" . PHP_EOL;
    echo PHP_EOL;
}

function printSafe(string $msg): void {
    echo "  ✅ {$msg}" . PHP_EOL;
}

function printWarn(string $msg): void {
    echo "  ⚠️  {$msg}" . PHP_EOL;
}

function printDanger(string $msg): void {
    echo "  🔴 {$msg}" . PHP_EOL;
}

/**
 * HTML 转义函数（防止 XSS）
 */
function e(string $str): string {
    return htmlspecialchars($str, ENT_QUOTES, 'UTF-8');
}

// ============================================================
// 案例 1：SQL 注入防御
// ============================================================

function case_sqlInjection(): void {
    printSection("【案例 1：SQL 注入防御】");

    echo "  SQL 注入（SQL Injection）是最经典的 Web 安全漏洞之一。" . PHP_EOL;
    echo "  当用户输入被直接拼接到 SQL 语句中时，攻击者可以" . PHP_EOL;
    echo "  构造恶意输入修改 SQL 逻辑，从而读取、修改、删除数据。" . PHP_EOL;

    printSubsection("1.1 危险写法（仅演示，不要这么写！）");

    // 模拟用户输入
    $username = "admin";
    $password = "123456";

    echo "  正常登录场景:" . PHP_EOL;
    echo "    用户名: {$username}" . PHP_EOL;
    echo "    密码: {$password}" . PHP_EOL;
    echo PHP_EOL;

    // ⚠️ 危险：直接拼接 SQL
    $sql = "SELECT * FROM users WHERE username = '{$username}' AND password = '{$password}'";
    echo "  生成的 SQL: {$sql}" . PHP_EOL;
    echo "  (正常情况下，查询匹配用户记录)" . PHP_EOL;

    echo PHP_EOL;
    echo "  攻击场景（经典的 ' OR '1'='1 绕过）:" . PHP_EOL;

    // 攻击者构造的输入
    $hacker_username = "' OR '1'='1";
    $hacker_password = "' OR '1'='1";

    $sql_injected = "SELECT * FROM users WHERE username = '{$hacker_username}' AND password = '{$hacker_password}'";
    echo "    攻击者输入的用户名: " . e($hacker_username) . PHP_EOL;
    echo "    生成的 SQL: {$sql_injected}" . PHP_EOL;
    echo "    结果：WHERE 条件永远为真，返回所有用户 → 登录绕过！" . PHP_EOL;

    echo PHP_EOL;
    printDanger("SQL 注入的危害：数据泄露、数据篡改、权限绕过、甚至获取服务器权限");

    printSubsection("1.2 安全写法：PDO 参数化查询");

    echo "  参数化查询（Prepared Statements）是防御 SQL 注入的最佳方法。" . PHP_EOL;
    echo "  SQL 结构和数据分离，用户输入永远作为数据处理。" . PHP_EOL;
    echo PHP_EOL;

    echo "  代码示例:" . PHP_EOL;
    echo '    // 1. 建立 PDO 连接（关键配置）' . PHP_EOL;
    echo '    $pdo = new PDO(' . PHP_EOL;
    echo '        "mysql:host=localhost;dbname=mydb;charset=utf8mb4",' . PHP_EOL;
    echo '        "user", "pass",' . PHP_EOL;
    echo '        [' . PHP_EOL;
    echo '            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,' . PHP_EOL;
    echo '            PDO::ATTR_EMULATE_PREPARES => false, // 禁用模拟预处理！' . PHP_EOL;
    echo '        ]' . PHP_EOL;
    echo '    );' . PHP_EOL;
    echo PHP_EOL;
    echo '    // 2. 预处理 SQL（结构固定）' . PHP_EOL;
    echo '    $stmt = $pdo->prepare(' . PHP_EOL;
    echo '        "SELECT * FROM users WHERE username = ? AND password = ?"' . PHP_EOL;
    echo '    );' . PHP_EOL;
    echo PHP_EOL;
    echo '    // 3. 绑定参数并执行（数据与结构分离）' . PHP_EOL;
    echo '    $stmt->execute([$username, $password]);' . PHP_EOL;
    echo '    $user = $stmt->fetch();' . PHP_EOL;

    echo PHP_EOL;
    printSafe("参数化查询下，攻击者输入只会被当作用户名/密码的值处理");
    echo "     不会改变 SQL 结构，因此无法注入" . PHP_EOL;

    printSubsection("1.3 其他安全措施");

    echo "  1. 使用参数化查询（PDO / MySQLi prepared）" . PHP_EOL;
    echo "  2. PDO 设置 ATTR_EMULATE_PREPARES = false" . PHP_EOL;
    echo "  3. 数据库账号最小权限原则" . PHP_EOL;
    echo "  4. 生产环境不显示数据库错误信息" . PHP_EOL;
    echo "  5. 输入验证（类型、长度、格式）" . PHP_EOL;
    echo "  6. 敏感数据加密存储（密码用 password_hash）" . PHP_EOL;
    echo "  7. 定期备份数据库" . PHP_EOL;

    printSubsection("1.4 密码安全存储");

    echo "  正确的密码存储方式：使用 password_hash（bcrypt/argon2）" . PHP_EOL;
    echo PHP_EOL;

    $password = "MySecurePass123!";
    $hash = password_hash($password, PASSWORD_DEFAULT);
    echo "  原文密码: {$password}" . PHP_EOL;
    echo "  哈希结果: {$hash}" . PHP_EOL;
    echo "  (每次哈希结果都不一样，因为有随机 salt)" . PHP_EOL;
    echo PHP_EOL;

    $is_valid = password_verify($password, $hash);
    echo "  验证正确密码: " . ($is_valid ? "✅ 通过" : "❌ 失败") . PHP_EOL;

    $is_invalid = password_verify("WrongPassword", $hash);
    echo "  验证错误密码: " . ($is_invalid ? "✅ 通过" : "❌ 失败") . PHP_EOL;

    echo PHP_EOL;
    printWarn("绝对不要用 MD5、SHA1 等快速哈希算法存储密码");
    echo "     也不要自己拼接 salt，直接用 password_hash 就好" . PHP_EOL;
}

// ============================================================
// 案例 2：XSS 防护
// ============================================================

function case_xss(): void {
    printSection("【案例 2：XSS 跨站脚本防护】");

    echo "  XSS（Cross-Site Scripting）：攻击者在网页中注入恶意脚本，" . PHP_EOL;
    echo "  当其他用户访问时脚本执行，窃取 Cookie、钓鱼、篡改页面等。" . PHP_EOL;

    echo PHP_EOL;
    echo "  XSS 三种类型:" . PHP_EOL;
    echo "    1. 反射型 XSS：注入的脚本在 URL 参数中，需要诱导用户点击" . PHP_EOL;
    echo "    2. 存储型 XSS：注入的脚本存储在数据库中，所有访问者都会中招" . PHP_EOL;
    echo "    3. DOM 型 XSS：前端 JavaScript 直接操作 DOM 导致" . PHP_EOL;

    printSubsection("2.1 反射型 XSS 演示");

    // 模拟用户输入（URL 参数）
    $name = $_GET["name"] ?? "<script>alert('XSS')</script>";

    echo "  用户输入: " . e($name) . PHP_EOL;
    echo PHP_EOL;

    // ⚠️ 危险：直接输出用户输入
    echo "  ❌ 危险输出（直接 echo）:" . PHP_EOL;
    echo "     代码: echo '欢迎, ' . \$name;" . PHP_EOL;
    echo "     结果: 欢迎, <script>alert('XSS')</script>" . PHP_EOL;
    echo "     浏览器会执行这段脚本！" . PHP_EOL;

    echo PHP_EOL;
    // ✅ 安全：使用 htmlspecialchars 转义
    echo "  ✅ 安全输出（htmlspecialchars 转义）:" . PHP_EOL;
    echo "     代码: echo '欢迎, ' . htmlspecialchars(\$name, ENT_QUOTES, 'UTF-8');" . PHP_EOL;
    echo "     结果: 欢迎, " . e($name) . PHP_EOL;
    echo "     特殊字符被转义为 HTML 实体，浏览器不会执行" . PHP_EOL;

    printSubsection("2.2 不同上下文的输出编码");

    $user_input = '<script>alert("xss")</script>';

    echo "  用户输入: " . e($user_input) . PHP_EOL;
    echo PHP_EOL;

    echo "  输出到 HTML 内容: htmlspecialchars()" . PHP_EOL;
    echo "    结果: " . e($user_input) . PHP_EOL;
    echo PHP_EOL;

    echo "  输出到 HTML 属性: htmlspecialchars(ENT_QUOTES)" . PHP_EOL;
    echo '    <input value="' . e($user_input) . '">' . PHP_EOL;
    echo PHP_EOL;

    echo "  输出到 JavaScript: json_encode()" . PHP_EOL;
    echo "    var data = " . json_encode($user_input) . ";" . PHP_EOL;
    echo PHP_EOL;

    echo "  输出到 URL: urlencode()" . PHP_EOL;
    echo "    ?q=" . urlencode($user_input) . PHP_EOL;

    printSubsection("2.3 输入验证（白名单）");

    echo "  除了输出编码，输入验证也是重要防线。" . PHP_EOL;
    echo PHP_EOL;

    // 示例：用户名验证
    $username = "user_123";
    $is_valid = preg_match('/^[a-zA-Z0-9_]{3,20}$/', $username);
    echo "  用户名 '{$username}' 验证: " . ($is_valid ? "✅ 有效" : "❌ 无效") . PHP_EOL;
    echo "    规则：3-20 位字母数字下划线" . PHP_EOL;
    echo PHP_EOL;

    $bad_username = "<script>";
    $is_valid_bad = preg_match('/^[a-zA-Z0-9_]{3,20}$/', $bad_username);
    echo "  用户名 '" . e($bad_username) . "' 验证: " . ($is_valid_bad ? "✅ 有效" : "❌ 无效") . PHP_EOL;

    printSubsection("2.4 HTTP 安全头");

    echo "  CSP (Content-Security-Policy): 限制资源加载来源" . PHP_EOL;
    echo "    header('Content-Security-Policy: default-src \'self\''); " . PHP_EOL;
    echo "    只允许加载同源资源，内联脚本不会执行" . PHP_EOL;
    echo PHP_EOL;

    echo "  其他安全头:" . PHP_EOL;
    echo "    X-Content-Type-Options: nosniff" . PHP_EOL;
    echo "    X-Frame-Options: DENY" . PHP_EOL;
    echo "    X-XSS-Protection: 1; mode=block" . PHP_EOL;
    echo "    Set-Cookie: ... HttpOnly Secure SameSite=Strict" . PHP_EOL;

    echo PHP_EOL;
    printSafe("XSS 防护三层防线：");
    echo "     1. 输入验证（白名单校验）" . PHP_EOL;
    echo "     2. 输出编码（根据上下文转义）" . PHP_EOL;
    echo "     3. CSP 安全头（纵深防御）" . PHP_EOL;
}

// ============================================================
// 案例 3：文件上传安全
// ============================================================

function case_fileUpload(): void {
    printSection("【案例 3：文件上传安全】");

    echo "  文件上传漏洞：当上传校验不严格时，攻击者可以上传" . PHP_EOL;
    echo "  WebShell 或其他恶意文件，进而获取服务器权限。" . PHP_EOL;
    echo "  这是 PHP 网站最常见的高危漏洞之一。" . PHP_EOL;

    printSubsection("3.1 常见上传绕过方式");

    echo "  1. 扩展名绕过: " . PHP_EOL;
    echo "     - 黑名单绕过: .php3 .php4 .php5 .phtml .pHp (大小写)" . PHP_EOL;
    echo "     - 双写绕过: .php.jpg (解析漏洞)" . PHP_EOL;
    echo "     - 点号空格: shell.php. (Windows 自动去掉末尾的点)" . PHP_EOL;
    echo PHP_EOL;
    echo "  2. MIME 类型绕过: 修改 Content-Type 为 image/jpeg" . PHP_EOL;
    echo "  3. %00 截断: shell.php%00.jpg (PHP 5.3.4 以下)" . PHP_EOL;
    echo "  4. .htaccess: 上传 .htaccess 改变解析规则" . PHP_EOL;
    echo "  5. 图片马: 图片文件末尾拼接 PHP 代码" . PHP_EOL;
    echo "  6. 解析漏洞: Apache/Nginx 特定版本的解析问题" . PHP_EOL;

    printSubsection("3.2 安全的文件上传函数");

    echo "  安全的文件上传需要多层校验：" . PHP_EOL;
    echo PHP_EOL;

    echo "  function safe_upload(\$file, \$upload_dir) {" . PHP_EOL;
    echo "    // 1. 检查上传错误" . PHP_EOL;
    echo "    if (\$file['error'] !== UPLOAD_ERR_OK) return false;" . PHP_EOL;
    echo PHP_EOL;
    echo "    // 2. 检查文件大小 (如 2MB)" . PHP_EOL;
    echo "    if (\$file['size'] > 2 * 1024 * 1024) return false;" . PHP_EOL;
    echo PHP_EOL;
    echo "    // 3. 白名单校验扩展名（最关键！）" . PHP_EOL;
    echo "    \$allowed = ['jpg', 'jpeg', 'png', 'gif'];" . PHP_EOL;
    echo "    \$ext = strtolower(pathinfo(\$file['name'], PATHINFO_EXTENSION));" . PHP_EOL;
    echo "    if (!in_array(\$ext, \$allowed, true)) return false;" . PHP_EOL;
    echo PHP_EOL;
    echo "    // 4. 校验 MIME 类型（辅助）" . PHP_EOL;
    echo "    \$finfo = new Finfo(FILEINFO_MIME_TYPE);" . PHP_EOL;
    echo "    \$mime = \$finfo->file(\$file['tmp_name']);" . PHP_EOL;
    echo "    \$allowed_mime = ['image/jpeg', 'image/png', 'image/gif'];" . PHP_EOL;
    echo "    if (!in_array(\$mime, \$allowed_mime, true)) return false;" . PHP_EOL;
    echo PHP_EOL;
    echo "    // 5. 校验图片内容（图片专用）" . PHP_EOL;
    echo "    \$img_info = @getimagesize(\$file['tmp_name']);" . PHP_EOL;
    echo "    if (!\$img_info) return false;" . PHP_EOL;
    echo PHP_EOL;
    echo "    // 6. 随机文件名（防止覆盖、防止路径猜测）" . PHP_EOL;
    echo "    \$new_name = uniqid() . '.' . \$ext;" . PHP_EOL;
    echo PHP_EOL;
    echo "    // 7. 移动到上传目录" . PHP_EOL;
    echo "    \$dest = \$upload_dir . '/' . \$new_name;" . PHP_EOL;
    echo "    return move_uploaded_file(\$file['tmp_name'], \$dest) ? \$new_name : false;" . PHP_EOL;
    echo "  }" . PHP_EOL;

    printSubsection("3.3 上传安全检查清单");

    echo "  ✅ 白名单校验扩展名（不要用黑名单）" . PHP_EOL;
    echo "  ✅ 文件名转小写后比较" . PHP_EOL;
    echo "  ✅ 校验 MIME 类型（辅助，不能单独依赖）" . PHP_EOL;
    echo "  ✅ 校验文件内容/文件头（图片类）" . PHP_EOL;
    echo "  ✅ 文件大小限制" . PHP_EOL;
    echo "  ✅ 随机生成文件名" . PHP_EOL;
    echo "  ✅ 上传目录禁止脚本执行（Apache/Nginx 配置）" . PHP_EOL;
    echo "  ✅ 上传目录放 Web 根目录之外更好" . PHP_EOL;
    echo "  ✅ 上传文件通过专门的 URL 访问（不暴露真实路径）" . PHP_EOL;
    echo "  ✅ 防止路径遍历（文件名不能包含 ../）" . PHP_EOL;

    printSubsection("3.4 服务器配置加固");

    echo "  Apache:" . PHP_EOL;
    echo "    <Directory /path/to/uploads>" . PHP_EOL;
    echo "        php_flag engine off" . PHP_EOL;
    echo "        AddType text/plain .php .php3 .phtml" . PHP_EOL;
    echo "    </Directory>" . PHP_EOL;
    echo PHP_EOL;

    echo "  Nginx:" . PHP_EOL;
    echo "    location ^~ /uploads/ {" . PHP_EOL;
    echo "        location ~ \.php$ { deny all; }" . PHP_EOL;
    echo "    }" . PHP_EOL;
}

// ============================================================
// 案例 4：反序列化安全
// ============================================================

// 演示用的类（实际漏洞中是已存在的类）
class User {
    public $name;
    public $email;

    public function __construct($name, $email) {
        $this->name = $name;
        $this->email = $email;
    }
}

// 有危险魔术方法的类（仅演示 POP 链原理）
class Logger {
    public $log_file;

    public function __destruct() {
        // 这里只是演示，实际中危险类的魔术方法可能调用危险函数
        // 比如 file_put_contents、system 等
        // 攻击者通过构造序列化数据控制这些方法的参数
        echo "    [Logger::__destruct] 日志文件: " . ($this->log_file ?? "未设置") . PHP_EOL;
    }
}

function case_deserialization(): void {
    printSection("【案例 4：反序列化安全】");

    echo "  PHP 反序列化漏洞：当 unserialize() 接受用户可控的输入时，" . PHP_EOL;
    echo "  攻击者可以构造特定的序列化数据，实例化任意类。" . PHP_EOL;
    echo "  如果类中有 __destruct()、__wakeup()、__toString() 等" . PHP_EOL;
    echo "  魔术方法，且方法中有危险操作，就可能导致 RCE。" . PHP_EOL;
    echo "  这就是所谓的 POP 链（Property-Oriented Programming）。" . PHP_EOL;

    printSubsection("4.1 序列化 / 反序列化基础");

    $user = new User("Alice", "alice@example.com");
    $serialized = serialize($user);

    echo "  原始对象: User(name=Alice, email=alice@example.com)" . PHP_EOL;
    echo "  序列化后: " . e($serialized) . PHP_EOL;
    echo PHP_EOL;

    $restored = unserialize($serialized);
    echo "  反序列化后: User(name={$restored->name}, email={$restored->email})" . PHP_EOL;

    printSubsection("4.2 反序列化漏洞原理");

    echo "  ⚠️ 危险代码（绝对不要这么写！）:" . PHP_EOL;
    echo "    unserialize(\$_GET['data']);  // 用户可控的反序列化！" . PHP_EOL;
    echo PHP_EOL;

    echo "  攻击者构造序列化数据，实例化危险类：" . PHP_EOL;
    echo "    O:6:\"Logger\":1:{s:8:\"log_file\";s:9:\"/tmp/pwn\";}" . PHP_EOL;
    echo PHP_EOL;
    echo "  反序列化后，Logger 对象被创建，脚本结束时 __destruct 被调用" . PHP_EOL;
    echo "  如果 __destruct 中有危险操作（写文件、执行命令等），就被利用了" . PHP_EOL;

    // 演示 Logger 析构
    $logger_data = 'O:6:"Logger":1:{s:8:"log_file";s:12:"/tmp/test.log";}';
    echo PHP_EOL . "  演示：反序列化 Logger 对象" . PHP_EOL;
    $logger = unserialize($logger_data);
    // 脚本结束时会调用 __destruct

    printSubsection("4.3 防御方法");

    echo "  1. ✅ 最佳方案：完全避免反序列化不可信数据" . PHP_EOL;
    echo "     使用 JSON、XML（禁用外部实体）等纯数据格式" . PHP_EOL;
    echo PHP_EOL;

    echo "  JSON 替代示例:" . PHP_EOL;
    echo '    // 编码' . PHP_EOL;
    echo '    $data = json_encode($user);' . PHP_EOL;
    echo '    // 解码' . PHP_EOL;
    echo '    $user = json_decode($data, true);  // 数组' . PHP_EOL;
    echo '    // JSON 只能解析数据，不会实例化对象，没有 RCE 风险' . PHP_EOL;
    echo PHP_EOL;

    // 演示 JSON
    $user_data = ["name" => "Bob", "email" => "bob@example.com"];
    $json = json_encode($user_data);
    echo "  JSON 编码: {$json}" . PHP_EOL;
    $decoded = json_decode($json, true);
    echo "  JSON 解码: name={$decoded['name']}, email={$decoded['email']}" . PHP_EOL;
    echo PHP_EOL;

    echo "  2. 如果必须使用序列化，使用白名单限制类（PHP 7+）" . PHP_EOL;
    echo '    $data = unserialize($input, [' . PHP_EOL;
    echo '        "allowed_classes" => ["User", "Product"]  // 只允许这些类' . PHP_EOL;
    echo '    ]);' . PHP_EOL;
    echo PHP_EOL;

    // 演示白名单
    echo "  白名单测试：只允许 User 类" . PHP_EOL;
    $safe_user = unserialize(serialize(new User("Test", "test@test.com")), [
        "allowed_classes" => ["User"]
    ]);
    echo "    User 类反序列化: " . ($safe_user !== false ? "✅ 成功" : "❌ 失败") . PHP_EOL;

    $malicious = 'O:6:"Logger":1:{s:8:"log_file";s:1:"/";}';
    $blocked = @unserialize($malicious, ["allowed_classes" => ["User"]]);
    echo "    Logger 类反序列化: " .
        (is_object($blocked) && get_class($blocked) === "__PHP_Incomplete_Class" ?
            "✅ 被阻止（不完整类）" : "❌ 未阻止") . PHP_EOL;

    echo PHP_EOL;
    echo "  3. 其他措施:" . PHP_EOL;
    echo "     - 使用签名/加密保护序列化数据完整性" . PHP_EOL;
    echo "     - 定期审计代码中的 unserialize 调用" . PHP_EOL;
    echo "     - 关注 PHP 反序列化相关的 CVE" . PHP_EOL;
}

// ============================================================
// 案例 5：CSRF 防护
// ============================================================

function case_csrf(): void {
    printSection("【案例 5：CSRF 跨站请求伪造防护】");

    echo "  CSRF（Cross-Site Request Forgery）：攻击者诱导已登录用户" . PHP_EOL;
    echo "  在不知情的情况下向目标网站发送请求，执行非本意的操作。" . PHP_EOL;
    echo "  例如：修改密码、转账、删除数据等。" . PHP_EOL;

    printSubsection("5.1 CSRF 攻击原理");

    echo "  攻击场景:" . PHP_EOL;
    echo "    1. 用户登录了 bank.com，Cookie 保存在浏览器中" . PHP_EOL;
    echo "    2. 用户访问了 attacker.com 的恶意页面" . PHP_EOL;
    echo "    3. 恶意页面自动向 bank.com 发送转账请求" . PHP_EOL;
    echo "    4. 浏览器自动带上 bank.com 的 Cookie" . PHP_EOL;
    echo "    5. bank.com 认为是用户本人操作，执行转账" . PHP_EOL;
    echo PHP_EOL;

    echo "  攻击前提:" . PHP_EOL;
    echo "    - 用户已登录目标网站" . PHP_EOL;
    echo "    - 目标网站仅靠 Cookie 验证身份" . PHP_EOL;
    echo "    - 请求参数可预测" . PHP_EOL;

    printSubsection("5.2 防御方法：CSRF Token");

    echo "  Token 验证机制:" . PHP_EOL;
    echo "    1. 服务器生成随机 Token，存在 Session 中" . PHP_EOL;
    echo "    2. 表单页面中包含这个 Token（隐藏字段）" . PHP_EOL;
    echo "    3. 用户提交表单时带上 Token" . PHP_EOL;
    echo "    4. 服务器验证 Token 是否匹配" . PHP_EOL;
    echo "    5. 攻击者无法获取 Token，因此无法伪造请求" . PHP_EOL;
    echo PHP_EOL;

    echo "  代码示例:" . PHP_EOL;
    echo PHP_EOL;
    echo "    // 生成 Token（放在表单页面）" . PHP_EOL;
    echo "    session_start();" . PHP_EOL;
    echo "    if (empty(\$_SESSION['csrf_token'])) {" . PHP_EOL;
    echo "        \$_SESSION['csrf_token'] = bin2hex(random_bytes(32));" . PHP_EOL;
    echo "    }" . PHP_EOL;
    echo "    \$token = \$_SESSION['csrf_token'];" . PHP_EOL;
    echo PHP_EOL;
    echo "    // 表单中包含 Token" . PHP_EOL;
    echo '    <form method="POST" action="/change-password">' . PHP_EOL;
    echo '        <input type="hidden" name="csrf_token" value="<?= $token ?>">' . PHP_EOL;
    echo '        <input type="password" name="new_password">' . PHP_EOL;
    echo '        <button type="submit">修改密码</button>' . PHP_EOL;
    echo '    </form>' . PHP_EOL;
    echo PHP_EOL;
    echo "    // 验证 Token（处理请求时）" . PHP_EOL;
    echo "    if (!isset(\$_POST['csrf_token']) || " . PHP_EOL;
    echo "        !isset(\$_SESSION['csrf_token']) || " . PHP_EOL;
    echo "        !hash_equals(\$_SESSION['csrf_token'], \$_POST['csrf_token'])) {" . PHP_EOL;
    echo "        die('CSRF 验证失败');" . PHP_EOL;
    echo "    }" . PHP_EOL;

    printSubsection("5.3 完整演示");

    // 启动 session
    if (session_status() === PHP_SESSION_NONE) {
        @session_start();
    }

    // 生成 Token
    if (empty($_SESSION["csrf_token"])) {
        $_SESSION["csrf_token"] = bin2hex(random_bytes(32));
    }
    $token = $_SESSION["csrf_token"];

    echo "  生成的 CSRF Token: " . substr($token, 0, 16) . "..." . PHP_EOL;
    echo "  (64 位十六进制，32 字节随机数)" . PHP_EOL;
    echo PHP_EOL;

    // 模拟正确的 Token 验证
    $valid_request = $token;  // 正确的 Token
    $is_valid = isset($_SESSION["csrf_token"]) &&
        hash_equals($_SESSION["csrf_token"], $valid_request);
    echo "  正确 Token 验证: " . ($is_valid ? "✅ 通过" : "❌ 失败") . PHP_EOL;

    // 模拟错误的 Token 验证
    $invalid_request = "0000000000000000000000000000000000000000000000000000000000000000";
    $is_invalid = isset($_SESSION["csrf_token"]) &&
        hash_equals($_SESSION["csrf_token"], $invalid_request);
    echo "  错误 Token 验证: " . ($is_invalid ? "✅ 通过" : "❌ 失败") . PHP_EOL;

    echo PHP_EOL;
    printSafe("使用 hash_equals() 进行时序安全的字符串比较");
    echo "     防止时序攻击（Timing Attack）" . PHP_EOL;

    printSubsection("5.4 其他 CSRF 防御措施");

    echo "  1. CSRF Token（主要方法）" . PHP_EOL;
    echo "  2. SameSite Cookie 属性" . PHP_EOL;
    echo "     - Strict: 完全不发送第三方 Cookie" . PHP_EOL;
    echo "     - Lax: 顶级导航 GET 请求才发送（默认）" . PHP_EOL;
    echo "     - None: 都发送（需要配合 Secure）" . PHP_EOL;
    echo "  3. 验证 Referer / Origin 头（辅助，不太可靠）" . PHP_EOL;
    echo "  4. 重要操作二次验证（密码、验证码）" . PHP_EOL;
    echo "  5. 验证码（人机验证）" . PHP_EOL;
}

// ============================================================
// 附：PHP 安全编码检查清单
// ============================================================

function printSecurityChecklist(): void {
    printSection("【附：PHP 安全编码检查清单】");

    echo "  输入验证:" . PHP_EOL;
    echo "    [ ] 所有外部输入都验证（\$_GET/\$_POST/\$_COOKIE/\$_SERVER/上传）" . PHP_EOL;
    echo "    [ ] 使用白名单验证，而非黑名单" . PHP_EOL;
    echo "    [ ] 验证数据类型、长度、范围、格式" . PHP_EOL;
    echo "    [ ] 使用 filter_var 验证邮箱/URL/IP" . PHP_EOL;
    echo "    [ ] 整数使用 intval 或类型声明" . PHP_EOL;
    echo PHP_EOL;

    echo "  数据库安全:" . PHP_EOL;
    echo "    [ ] 所有查询使用参数化查询（PDO prepared statements）" . PHP_EOL;
    echo "    [ ] ATTR_EMULATE_PREPARES = false" . PHP_EOL;
    echo "    [ ] 数据库账号最小权限" . PHP_EOL;
    echo "    [ ] 生产环境不显示数据库错误" . PHP_EOL;
    echo "    [ ] 密码使用 password_hash 存储" . PHP_EOL;
    echo PHP_EOL;

    echo "  输出安全:" . PHP_EOL;
    echo "    [ ] HTML 输出用 htmlspecialchars 转义" . PHP_EOL;
    echo "    [ ] JavaScript 输出用 json_encode" . PHP_EOL;
    echo "    [ ] URL 参数用 urlencode" . PHP_EOL;
    echo "    [ ] 设置 Content-Security-Policy 头" . PHP_EOL;
    echo "    [ ] 设置 X-Content-Type-Options: nosniff" . PHP_EOL;
    echo PHP_EOL;

    echo "  文件上传:" . PHP_EOL;
    echo "    [ ] 白名单校验扩展名" . PHP_EOL;
    echo "    [ ] 校验 MIME 类型（辅助）" . PHP_EOL;
    echo "    [ ] 校验文件内容/文件头" . PHP_EOL;
    echo "    [ ] 文件大小限制" . PHP_EOL;
    echo "    [ ] 随机文件名" . PHP_EOL;
    echo "    [ ] 上传目录禁止脚本执行" . PHP_EOL;
    echo PHP_EOL;

    echo "  会话安全:" . PHP_EOL;
    echo "    [ ] 登录后 session_regenerate_id()" . PHP_EOL;
    echo "    [ ] Cookie 设置 httponly" . PHP_EOL;
    echo "    [ ] HTTPS 站点设置 secure" . PHP_EOL;
    echo "    [ ] 设置 SameSite 属性" . PHP_EOL;
    echo "    [ ] 会话超时机制" . PHP_EOL;
    echo PHP_EOL;

    echo "  CSRF 防护:" . PHP_EOL;
    echo "    [ ] 重要操作使用 CSRF Token" . PHP_EOL;
    echo "    [ ] Token 使用 random_bytes 生成" . PHP_EOL;
    echo "    [ ] 使用 hash_equals 验证" . PHP_EOL;
    echo PHP_EOL;

    echo "  PHP 配置:" . PHP_EOL;
    echo "    [ ] expose_php = Off" . PHP_EOL;
    echo "    [ ] display_errors = Off（生产环境）" . PHP_EOL;
    echo "    [ ] allow_url_include = Off" . PHP_EOL;
    echo "    [ ] disable_functions 禁用不必要的危险函数" . PHP_EOL;
    echo "    [ ] open_basedir 限制文件访问" . PHP_EOL;
    echo "    [ ] 使用 PHP 8.x（受支持的版本）" . PHP_EOL;
    echo PHP_EOL;

    echo "  代码质量:" . PHP_EOL;
    echo "    [ ] 严格比较使用 === 而非 ==" . PHP_EOL;
    echo "    [ ] 避免使用 extract()、parse_str()" . PHP_EOL;
    echo "    [ ] 不使用 eval()、assert() 等危险函数" . PHP_EOL;
    echo "    [ ] Composer 依赖定期更新" . PHP_EOL;
    echo "    [ ] composer audit 检查依赖漏洞" . PHP_EOL;
    echo "    [ ] 静态分析（PHPStan/Psalm）" . PHP_EOL;
}

// ============================================================
// 主函数
// ============================================================

function main(): void {
    echo PHP_EOL;
    echo "============================================================" . PHP_EOL;
    echo "  PHP 安全案例集" . PHP_EOL;
    echo "  PHP Security Cases" . PHP_EOL;
    echo "============================================================" . PHP_EOL;
    echo PHP_EOL;
    echo "  本程序从防御角度演示常见 PHP Web 安全漏洞的" . PHP_EOL;
    echo "  原理与防护方法。所有案例均用于学习研究，" . PHP_EOL;
    echo "  请在授权环境中使用。" . PHP_EOL;

    // 获取案例编号（支持命令行和 GET 参数）
    $caseNum = 0;
    global $argc, $argv;
    if (isset($argc) && $argc > 1) {
        $caseNum = intval($argv[1]);
    } elseif (isset($_GET["case"])) {
        $caseNum = intval($_GET["case"]);
    }

    switch ($caseNum) {
        case 0:
            // 运行所有案例
            case_sqlInjection();
            case_xss();
            case_fileUpload();
            case_deserialization();
            case_csrf();
            printSecurityChecklist();
            break;
        case 1:
            case_sqlInjection();
            break;
        case 2:
            case_xss();
            break;
        case 3:
            case_fileUpload();
            break;
        case 4:
            case_deserialization();
            break;
        case 5:
            case_csrf();
            break;
        case 6:
            printSecurityChecklist();
            break;
        default:
            echo PHP_EOL;
            echo "  用法: php security_cases.php [案例编号]" . PHP_EOL;
            echo "  或:   ?case=编号（浏览器访问）" . PHP_EOL;
            echo PHP_EOL;
            echo "  案例:" . PHP_EOL;
            echo "    1 = SQL 注入防御" . PHP_EOL;
            echo "    2 = XSS 防护" . PHP_EOL;
            echo "    3 = 文件上传安全" . PHP_EOL;
            echo "    4 = 反序列化安全" . PHP_EOL;
            echo "    5 = CSRF 防护" . PHP_EOL;
            echo "    6 = 安全编码检查清单" . PHP_EOL;
            echo "    0 或不指定 = 全部运行" . PHP_EOL;
            return;
    }

    echo PHP_EOL;
    echo "============================================================" . PHP_EOL;
    echo "  演示完成。记住：理解漏洞原理是为了更好地防御。" . PHP_EOL;
    echo "  请遵守法律法规，仅在授权环境中进行安全测试。" . PHP_EOL;
    echo "============================================================" . PHP_EOL;
    echo PHP_EOL;
}

// 运行主函数
main();
