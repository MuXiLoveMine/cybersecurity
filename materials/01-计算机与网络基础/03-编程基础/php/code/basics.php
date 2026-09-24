<?php
/**
 * basics.php —— PHP 基础语法示例（安全从业者视角）
 *
 * 涵盖内容：
 *   1. 变量与数据类型
 *   2. 运算符与比较（弱类型安全注意）
 *   3. 流程控制
 *   4. 函数
 *   5. 数组
 *   6. 字符串操作
 *   7. 表单处理（GET/POST）
 *   8. Session 与 Cookie
 *   9. 数据库操作（PDO）
 *   10. 文件操作
 *
 * 运行方式：
 *   命令行: php basics.php
 *   浏览器: php -S 127.0.0.1:8000 后访问 http://127.0.0.1:8000/basics.php
 *
 * 注意：本脚本用于学习参考，包含安全视角的注释说明。
 */

// 配置错误显示（学习环境开启，生产环境关闭）
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

// ============================================================
// 1. 变量与数据类型
// ============================================================

function demoVariablesAndTypes(): void {
    printSection("【1. 变量与数据类型】");

    printSubsection("1.1 基本变量");

    // PHP 变量以 $ 开头
    $name = "Alice";
    $age = 25;
    $height = 1.68;
    $is_student = true;
    $nothing = null;

    echo "  name = {$name} (类型: " . gettype($name) . ")" . PHP_EOL;
    echo "  age = {$age} (类型: " . gettype($age) . ")" . PHP_EOL;
    echo "  height = {$height} (类型: " . gettype($height) . ")" . PHP_EOL;
    echo "  is_student = " . ($is_student ? "true" : "false") . " (类型: " . gettype($is_student) . ")" . PHP_EOL;
    echo "  nothing = " . var_export($nothing, true) . " (类型: " . gettype($nothing) . ")" . PHP_EOL;

    printSubsection("1.2 类型检查函数");

    echo "  is_int(\$age): " . (is_int($age) ? "true" : "false") . PHP_EOL;
    echo "  is_string(\$name): " . (is_string($name) ? "true" : "false") . PHP_EOL;
    echo "  is_bool(\$is_student): " . (is_bool($is_student) ? "true" : "false") . PHP_EOL;
    echo "  is_null(\$nothing): " . (is_null($nothing) ? "true" : "false") . PHP_EOL;

    printSubsection("1.3 常量");

    define("SITE_NAME", "安全学习平台");
    const MAX_LOGIN_ATTEMPTS = 5;

    echo "  SITE_NAME = " . SITE_NAME . PHP_EOL;
    echo "  MAX_LOGIN_ATTEMPTS = " . MAX_LOGIN_ATTEMPTS . PHP_EOL;

    printSubsection("1.4 弱类型与安全注意");

    echo "  PHP 是弱类型语言，变量类型可以自动转换。" . PHP_EOL;
    echo "  这种灵活性带来便利，但也可能导致安全问题。" . PHP_EOL;
    echo PHP_EOL;

    $num = "42";
    echo "  \"42\" + 1 = " . ($num + 1) . " (字符串自动转数字)" . PHP_EOL;
    echo "  \"42abc\" + 1 = " . ("42abc" + 1) . " (从字符串开头提取数字)" . PHP_EOL;
    echo "  \"abc\" + 1 = " . ("abc" + 1) . " (非数字字符串转 0)" . PHP_EOL;

    echo PHP_EOL;
    printWarn("弱类型是很多 PHP 漏洞的根源（MD5 比较绕过、switch 绕过等）");
    echo "  💡 推荐使用严格比较 === 和 !== " . PHP_EOL;
}

// ============================================================
// 2. 运算符与比较
// ============================================================

function demoOperators(): void {
    printSection("【2. 运算符与比较】");

    printSubsection("2.1 算术运算符");

    $a = 10;
    $b = 3;

    echo "  \$a = {$a}, \$b = {$b}" . PHP_EOL;
    echo "  \$a + \$b = " . ($a + $b) . PHP_EOL;
    echo "  \$a - \$b = " . ($a - $b) . PHP_EOL;
    echo "  \$a * \$b = " . ($a * $b) . PHP_EOL;
    echo "  \$a / \$b = " . ($a / $b) . PHP_EOL;
    echo "  \$a % \$b = " . ($a % $b) . " (取余)" . PHP_EOL;
    echo "  \$a ** \$b = " . ($a ** $b) . " (幂运算)" . PHP_EOL;

    printSubsection("2.2 == vs === （重点！）");

    echo "  ==  松散比较：只比较值，自动类型转换" . PHP_EOL;
    echo "  === 严格比较：比较类型和值" . PHP_EOL;
    echo PHP_EOL;

    $tests = [
        [0, "0"],
        [0, "abc"],
        ["admin", 0],
        [null, false],
        [null, ""],
        ["0e123", "0e456"],
        [true, 1],
        [true, "abc"],
    ];

    printf("  %-15s %-15s %-8s %-8s\n", "左值", "右值", "==", "===");
    echo "  " . str_repeat("-", 50) . PHP_EOL;

    foreach ($tests as [$left, $right]) {
        $loose = $left == $right ? "true" : "false";
        $strict = $left === $right ? "true" : "false";
        $left_str = var_export($left, true);
        $right_str = var_export($right, true);
        printf("  %-15s %-15s %-8s %-8s\n", $left_str, $right_str, $loose, $strict);
    }

    echo PHP_EOL;
    printWarn("注意 \"0e123\" == \"0e456\" 为 true！");
    echo "     因为 PHP 把科学计数法字符串当数字比较，都等于 0" . PHP_EOL;
    echo "     这是经典的 MD5 比较绕过漏洞的原理" . PHP_EOL;
    echo PHP_EOL;
    printSafe("安全编码建议：尽可能使用 === 进行比较");
}

// ============================================================
// 3. 流程控制
// ============================================================

function demoControlFlow(): void {
    printSection("【3. 流程控制】");

    printSubsection("3.1 if-else");

    $score = 85;
    echo "  分数: {$score}" . PHP_EOL;

    if ($score >= 90) {
        echo "  等级: 优秀" . PHP_EOL;
    } elseif ($score >= 80) {
        echo "  等级: 良好" . PHP_EOL;
    } elseif ($score >= 60) {
        echo "  等级: 及格" . PHP_EOL;
    } else {
        echo "  等级: 不及格" . PHP_EOL;
    }

    // 三元运算符
    $result = $score >= 60 ? "及格" : "不及格";
    echo "  三元运算结果: {$result}" . PHP_EOL;

    // null 合并运算符（PHP 7+）
    $username = $_GET["user"] ?? "默认用户";
    echo "  用户名（null 合并）: {$username}" . PHP_EOL;

    printSubsection("3.2 switch");

    $day = "Monday";
    echo "  今天是: {$day}" . PHP_EOL;

    switch ($day) {
        case "Monday":
            echo "  switch 结果: 星期一" . PHP_EOL;
            break;
        case "Friday":
            echo "  switch 结果: 星期五" . PHP_EOL;
            break;
        default:
            echo "  switch 结果: 其他" . PHP_EOL;
    }

    echo PHP_EOL;
    printWarn("switch 使用松散比较（==），可能导致意外匹配");
    echo '     例如: switch("1abc") { case 1: echo "匹配"; } 会匹配成功' . PHP_EOL;

    printSubsection("3.3 循环");

    echo "  for 循环 (1-5): ";
    for ($i = 1; $i <= 5; $i++) {
        echo $i . " ";
    }
    echo PHP_EOL;

    echo "  while 循环 (5-1): ";
    $i = 5;
    while ($i >= 1) {
        echo $i . " ";
        $i--;
    }
    echo PHP_EOL;

    $fruits = ["apple", "banana", "orange"];
    echo "  foreach 遍历数组: ";
    foreach ($fruits as $fruit) {
        echo $fruit . " ";
    }
    echo PHP_EOL;
}

// ============================================================
// 4. 函数
// ============================================================

// 基本函数
function add(int $a, int $b): int {
    return $a + $b;
}

// 默认参数
function greet(string $name = "World"): string {
    return "Hello, " . $name . "!";
}

// 可变参数
function sum(int ...$numbers): int {
    $total = 0;
    foreach ($numbers as $n) {
        $total += $n;
    }
    return $total;
}

function demoFunctions(): void {
    printSection("【4. 函数】");

    printSubsection("4.1 基本函数");

    echo "  add(3, 5) = " . add(3, 5) . PHP_EOL;
    echo "  greet() = " . greet() . PHP_EOL;
    echo "  greet('Alice') = " . greet("Alice") . PHP_EOL;
    echo "  sum(1, 2, 3, 4, 5) = " . sum(1, 2, 3, 4, 5) . PHP_EOL;

    printSubsection("4.2 匿名函数与箭头函数");

    $double = function($n) {
        return $n * 2;
    };
    echo "  匿名函数 double(5) = " . $double(5) . PHP_EOL;

    $triple = fn($n) => $n * 3;  // PHP 7.4+
    echo "  箭头函数 triple(5) = " . $triple(5) . PHP_EOL;

    // 闭包（use 关键字）
    $factor = 10;
    $multiply = function($n) use ($factor) {
        return $n * $factor;
    };
    echo "  闭包 multiply(5) = " . $multiply(5) . PHP_EOL;

    printSubsection("4.3 常用内置函数");

    echo "  strlen('hello') = " . strlen("hello") . PHP_EOL;
    echo "  count([1,2,3]) = " . count([1, 2, 3]) . PHP_EOL;
    echo "  max(3, 7, 2) = " . max(3, 7, 2) . PHP_EOL;
    echo "  min(3, 7, 2) = " . min(3, 7, 2) . PHP_EOL;
    echo "  round(3.14159, 2) = " . round(3.14159, 2) . PHP_EOL;
    echo "  rand(1, 100) = " . rand(1, 100) . PHP_EOL;
    echo "  date('Y-m-d H:i:s') = " . date("Y-m-d H:i:s") . PHP_EOL;
    echo "  md5('test') = " . md5("test") . " (MD5 已不安全，仅用于校验)" . PHP_EOL;
    echo "  password_hash('test', PASSWORD_DEFAULT) = " . password_hash("test", PASSWORD_DEFAULT) . " (安全的密码哈希)" . PHP_EOL;
}

// ============================================================
// 5. 数组
// ============================================================

function demoArrays(): void {
    printSection("【5. 数组】");

    printSubsection("5.1 索引数组");

    $nums = [1, 2, 3, 4, 5];
    echo "  数组: [" . implode(", ", $nums) . "]" . PHP_EOL;
    echo "  长度: " . count($nums) . PHP_EOL;
    echo "  第一个元素: " . $nums[0] . PHP_EOL;
    echo "  最后一个元素: " . $nums[count($nums) - 1] . PHP_EOL;

    printSubsection("5.2 关联数组");

    $user = [
        "name" => "Alice",
        "age" => 25,
        "email" => "alice@example.com"
    ];

    echo "  姓名: " . $user["name"] . PHP_EOL;
    echo "  年龄: " . $user["age"] . PHP_EOL;
    echo "  邮箱: " . $user["email"] . PHP_EOL;

    echo PHP_EOL . "  遍历关联数组:" . PHP_EOL;
    foreach ($user as $key => $value) {
        echo "    {$key}: {$value}" . PHP_EOL;
    }

    printSubsection("5.3 常用数组函数");

    $arr = [3, 1, 4, 1, 5, 9, 2, 6];

    echo "  原数组: [" . implode(", ", $arr) . "]" . PHP_EOL;

    sort($arr);
    echo "  sort 后: [" . implode(", ", $arr) . "]" . PHP_EOL;

    echo "  in_array(5, \$arr): " . (in_array(5, $arr) ? "true" : "false") . PHP_EOL;
    echo "  array_search(9, \$arr): " . array_search(9, $arr) . PHP_EOL;

    $merged = array_merge([1, 2], [3, 4]);
    echo "  array_merge: [" . implode(", ", $merged) . "]" . PHP_EOL;

    $sliced = array_slice($arr, 0, 3);
    echo "  array_slice(前3个): [" . implode(", ", $sliced) . "]" . PHP_EOL;

    // array_map
    $doubled = array_map(fn($n) => $n * 2, $arr);
    echo "  array_map (翻倍): [" . implode(", ", $doubled) . "]" . PHP_EOL;

    // array_filter
    $filtered = array_filter($arr, fn($n) => $n > 3);
    echo "  array_filter (>3): [" . implode(", ", $filtered) . "]" . PHP_EOL;

    echo PHP_EOL;
    printWarn("in_array 和 array_search 默认使用松散比较（==）");
    echo "     第三个参数设为 true 才是严格比较" . PHP_EOL;
    echo "     in_array(0, ['abc'], true) = " .
        (in_array(0, ['abc'], true) ? "true" : "false") . " (严格)" . PHP_EOL;
    echo "     in_array(0, ['abc']) = " .
        (in_array(0, ['abc']) ? "true" : "false") . " (松散)" . PHP_EOL;
}

// ============================================================
// 6. 字符串操作
// ============================================================

function demoStrings(): void {
    printSection("【6. 字符串操作】");

    $str = "Hello, World!";

    echo "  原字符串: {$str}" . PHP_EOL;
    echo "  长度: " . strlen($str) . PHP_EOL;
    echo "  转小写: " . strtolower($str) . PHP_EOL;
    echo "  转大写: " . strtoupper($str) . PHP_EOL;
    echo "  查找 'World' 位置: " . strpos($str, "World") . PHP_EOL;
    echo "  替换 World->PHP: " . str_replace("World", "PHP", $str) . PHP_EOL;
    echo "  截取前5个: " . substr($str, 0, 5) . PHP_EOL;
    echo "  去除首尾空白: '" . trim("  hello  ") . "'" . PHP_EOL;

    echo PHP_EOL . "  字符串分割与合并:" . PHP_EOL;
    $csv = "apple,banana,orange";
    $fruits = explode(",", $csv);
    echo "    explode 分割: [" . implode(" | ", $fruits) . "]" . PHP_EOL;
    echo "    implode 合并: " . implode("-", $fruits) . PHP_EOL;

    echo PHP_EOL . "  格式化字符串:" . PHP_EOL;
    $formatted = sprintf("用户 %s 今年 %d 岁，身高 %.2f 米", "Alice", 25, 1.68);
    echo "    {$formatted}" . PHP_EOL;

    echo PHP_EOL . "  字符串拼接方式:" . PHP_EOL;
    $name = "Alice";
    echo '    单引号拼接: Hello, ' . $name . '!' . PHP_EOL;
    echo "    双引号解析: Hello, {$name}!" . PHP_EOL;

    echo PHP_EOL;
    printWarn("双引号字符串中变量会被解析，输出用户输入要小心 XSS");
}

// ============================================================
// 7. 表单处理
// ============================================================

function demoFormHandling(): void {
    printSection("【7. 表单处理】");

    echo "  PHP 超全局变量（Superglobals）:" . PHP_EOL;
    echo PHP_EOL;
    echo "    \$_GET      - URL 查询参数" . PHP_EOL;
    echo "    \$_POST     - POST 表单数据" . PHP_EOL;
    echo "    \$_REQUEST  - GET + POST + Cookie（不推荐，来源不明确）" . PHP_EOL;
    echo "    \$_FILES    - 上传的文件" . PHP_EOL;
    echo "    \$_SERVER   - 服务器和环境信息" . PHP_EOL;
    echo "    \$_SESSION  - Session 数据" . PHP_EOL;
    echo "    \$_COOKIE   - Cookie 数据" . PHP_EOL;

    printSubsection("7.1 GET 参数");

    // 模拟 GET 参数（命令行运行时没有真实的 $_GET）
    $_GET["name"] = "Alice";
    $_GET["id"] = "123";

    $name = $_GET["name"] ?? "默认值";  // PHP 7+ null 合并运算符
    $id = isset($_GET["id"]) ? intval($_GET["id"]) : 0; // 旧写法 + 类型转换

    echo "  name = {$name}" . PHP_EOL;
    echo "  id = {$id} (转整数后)" . PHP_EOL;

    printSubsection("7.2 输入验证");

    echo "  永远不要信任用户输入！所有输入必须验证。" . PHP_EOL;
    echo PHP_EOL;

    // 邮箱验证
    $email = "user@example.com";
    $is_valid_email = filter_var($email, FILTER_VALIDATE_EMAIL);
    echo "  邮箱验证 {$email}: " . ($is_valid_email ? "✅ 有效" : "❌ 无效") . PHP_EOL;

    // IP 验证
    $ip = "192.168.1.1";
    $is_valid_ip = filter_var($ip, FILTER_VALIDATE_IP);
    echo "  IP 验证 {$ip}: " . ($is_valid_ip ? "✅ 有效" : "❌ 无效") . PHP_EOL;

    // URL 验证
    $url = "https://example.com";
    $is_valid_url = filter_var($url, FILTER_VALIDATE_URL);
    echo "  URL 验证 {$url}: " . ($is_valid_url ? "✅ 有效" : "❌ 无效") . PHP_EOL;

    // 整数范围验证
    $age = 25;
    $is_valid_age = filter_var($age, FILTER_VALIDATE_INT, [
        "options" => ["min_range" => 0, "max_range" => 150]
    ]);
    echo "  年龄验证 {$age}: " . ($is_valid_age ? "✅ 有效" : "❌ 无效") . PHP_EOL;

    printSubsection("7.3 文件上传基础");

    echo "  \$_FILES 数组结构:" . PHP_EOL;
    echo "    \$_FILES['field_name']['name']     - 原始文件名" . PHP_EOL;
    echo "    \$_FILES['field_name']['type']     - MIME 类型（不可靠）" . PHP_EOL;
    echo "    \$_FILES['field_name']['size']     - 文件大小" . PHP_EOL;
    echo "    \$_FILES['field_name']['tmp_name'] - 临时文件路径" . PHP_EOL;
    echo "    \$_FILES['field_name']['error']    - 错误码" . PHP_EOL;
    echo PHP_EOL;
    printWarn("文件上传是高危操作，必须严格校验（见 security_cases.php）");
}

// ============================================================
// 8. Session 与 Cookie
// ============================================================

function demoSessionAndCookie(): void {
    printSection("【8. Session 与 Cookie】");

    // 注意：session_start() 需要在任何输出之前调用
    // 因为这里已经有输出了，我们用 @ 抑制错误（仅演示用）
    if (session_status() === PHP_SESSION_NONE) {
        @session_start();
    }

    printSubsection("8.1 Session");

    // 设置 Session
    $_SESSION["user_id"] = 123;
    $_SESSION["username"] = "alice";
    $_SESSION["is_login"] = true;
    $_SESSION["login_time"] = time();

    echo "  Session ID: " . session_id() . PHP_EOL;
    echo "  user_id: " . ($_SESSION["user_id"] ?? "未设置") . PHP_EOL;
    echo "  username: " . ($_SESSION["username"] ?? "未设置") . PHP_EOL;
    echo "  is_login: " . ($_SESSION["is_login"] ? "true" : "false") . PHP_EOL;

    echo PHP_EOL;
    echo "  登录验证示例:" . PHP_EOL;
    if (isset($_SESSION["is_login"]) && $_SESSION["is_login"] === true) {
        echo "    ✅ 用户已登录: " . $_SESSION["username"] . PHP_EOL;
    } else {
        echo "    ❌ 用户未登录" . PHP_EOL;
    }

    printSubsection("8.2 Cookie");

    // 设置 Cookie（实际运行时可能因为 header 已发送而失败）
    // 这里仅演示语法
    echo "  setcookie 语法:" . PHP_EOL;
    echo "    setcookie(name, value, expire, path, domain, secure, httponly)" . PHP_EOL;
    echo PHP_EOL;
    echo "  安全配置建议:" . PHP_EOL;
    echo "    httponly  = true  (防止 XSS 窃取 Cookie)" . PHP_EOL;
    echo "    secure    = true  (仅 HTTPS 传输)" . PHP_EOL;
    echo "    samesite  = Strict (防止 CSRF)" . PHP_EOL;

    printSubsection("8.3 Session 安全要点");

    echo "  1. 登录后调用 session_regenerate_id() 防止会话固定" . PHP_EOL;
    echo "  2. Cookie 设置 httponly、secure、samesite" . PHP_EOL;
    echo "  3. 重要操作需要二次验证（密码、验证码）" . PHP_EOL;
    echo "  4. 设置合理的会话超时时间" . PHP_EOL;
    echo "  5. 不要在 Session 中存储敏感信息（明文密码等）" . PHP_EOL;
}

// ============================================================
// 9. 数据库操作（PDO）
// ============================================================

function demoDatabase(): void {
    printSection("【9. 数据库操作（PDO）】");

    printSubsection("9.1 PDO 连接");

    echo "  PDO (PHP Data Objects) 是 PHP 数据库操作的推荐方式" . PHP_EOL;
    echo "  支持多种数据库（MySQL、PostgreSQL、SQLite 等）" . PHP_EOL;
    echo PHP_EOL;

    echo "  连接示例代码:" . PHP_EOL;
    echo '    try {' . PHP_EOL;
    echo '        $pdo = new PDO(' . PHP_EOL;
    echo '            "mysql:host=localhost;dbname=mydb;charset=utf8mb4",' . PHP_EOL;
    echo '            "username",' . PHP_EOL;
    echo '            "password",' . PHP_EOL;
    echo '            [' . PHP_EOL;
    echo '                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,' . PHP_EOL;
    echo '                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,' . PHP_EOL;
    echo '                PDO::ATTR_EMULATE_PREPARES => false, // 禁用模拟预处理' . PHP_EOL;
    echo '            ]' . PHP_EOL;
    echo '        );' . PHP_EOL;
    echo '    } catch (PDOException $e) {' . PHP_EOL;
    echo '        die("数据库连接失败");' . PHP_EOL;
    echo '    }' . PHP_EOL;

    printSubsection("9.2 参数化查询（防止 SQL 注入）");

    echo "  ✅ 安全写法（参数化查询）:" . PHP_EOL;
    echo '    $stmt = $pdo->prepare("SELECT * FROM users WHERE id = :id");' . PHP_EOL;
    echo '    $stmt->execute(["id" => $_GET["id"]]);' . PHP_EOL;
    echo '    $user = $stmt->fetch();' . PHP_EOL;
    echo PHP_EOL;

    echo "  ❌ 危险写法（SQL 注入）:" . PHP_EOL;
    echo '    $sql = "SELECT * FROM users WHERE id = " . $_GET["id"];' . PHP_EOL;
    echo '    $user = $pdo->query($sql)->fetch();' . PHP_EOL;
    echo PHP_EOL;

    printSubsection("9.3 常见操作示例");

    echo "  查询单条记录:" . PHP_EOL;
    echo '    $stmt = $pdo->prepare("SELECT * FROM users WHERE email = ?");' . PHP_EOL;
    echo '    $stmt->execute([$email]);' . PHP_EOL;
    echo '    $user = $stmt->fetch();' . PHP_EOL;
    echo PHP_EOL;

    echo "  查询多条记录:" . PHP_EOL;
    echo '    $stmt = $pdo->prepare("SELECT * FROM users WHERE age > ?");' . PHP_EOL;
    echo '    $stmt->execute([18]);' . PHP_EOL;
    echo '    $users = $stmt->fetchAll();' . PHP_EOL;
    echo '    foreach ($users as $user) { ... }' . PHP_EOL;
    echo PHP_EOL;

    echo "  插入数据:" . PHP_EOL;
    echo '    $stmt = $pdo->prepare(' . PHP_EOL;
    echo '        "INSERT INTO users (username, email) VALUES (:u, :e)"' . PHP_EOL;
    echo '    );' . PHP_EOL;
    echo '    $stmt->execute(["u" => $name, "e" => $email]);' . PHP_EOL;
    echo '    $new_id = $pdo->lastInsertId();' . PHP_EOL;

    echo PHP_EOL;
    printSafe("关键配置：ATTR_EMULATE_PREPARES => false");
    echo "     确保使用真正的预处理语句，而不是模拟的" . PHP_EOL;
}

// ============================================================
// 10. 文件操作
// ============================================================

function demoFileIO(): void {
    printSection("【10. 文件操作】");

    printSubsection("10.1 文件读写");

    $test_file = __DIR__ . "/php_basics_test.txt";

    // 写入文件
    $content = "Hello, PHP!\n这是第二行\n第三行数字: 42\n";
    file_put_contents($test_file, $content);
    echo "  已写入文件: {$test_file}" . PHP_EOL;

    // 读取整个文件
    $read_content = file_get_contents($test_file);
    echo "  文件大小: " . strlen($read_content) . " 字节" . PHP_EOL;
    echo "  文件内容:" . PHP_EOL;
    foreach (explode("\n", trim($read_content)) as $line) {
        echo "    {$line}" . PHP_EOL;
    }

    // 按行读取
    echo PHP_EOL . "  按行读取 (file() 函数):" . PHP_EOL;
    $lines = file($test_file);
    foreach ($lines as $i => $line) {
        echo "    行 " . ($i + 1) . ": " . trim($line) . PHP_EOL;
    }

    printSubsection("10.2 文件检查");

    echo "  file_exists: " . (file_exists($test_file) ? "✅ 存在" : "❌ 不存在") . PHP_EOL;
    echo "  is_file: " . (is_file($test_file) ? "✅ 是文件" : "❌ 不是文件") . PHP_EOL;
    echo "  is_dir: " . (is_dir(__DIR__) ? "✅ 是目录" : "❌ 不是目录") . PHP_EOL;
    echo "  filesize: " . filesize($test_file) . " 字节" . PHP_EOL;
    echo "  filemtime: " . date("Y-m-d H:i:s", filemtime($test_file)) . PHP_EOL;
    echo "  is_readable: " . (is_readable($test_file) ? "✅ 可读" : "❌ 不可读") . PHP_EOL;
    echo "  is_writable: " . (is_writable($test_file) ? "✅ 可写" : "❌ 不可写") . PHP_EOL;

    printSubsection("10.3 目录操作");

    echo "  当前目录: " . __DIR__ . PHP_EOL;
    echo "  脚本文件名: " . basename(__FILE__) . PHP_EOL;
    echo PHP_EOL;

    $files = scandir(__DIR__);
    echo "  目录文件列表 (前 10 个):" . PHP_EOL;
    $count = 0;
    foreach ($files as $file) {
        if ($file === "." || $file === "..") continue;
        if ($count >= 10) break;
        echo "    - {$file}" . PHP_EOL;
        $count++;
    }
    if (count($files) > 12) {
        echo "    ... 还有 " . (count($files) - 12) . " 个" . PHP_EOL;
    }

    // 清理测试文件
    unlink($test_file);
    echo PHP_EOL . "  已清理测试文件" . PHP_EOL;

    printSubsection("10.4 安全注意");

    printWarn("文件包含函数（include/require）如果路径可控，可能导致 RCE");
    echo "  文件操作函数（file_get_contents 等）如果路径可控，可能导致任意文件读取" . PHP_EOL;
    echo "  始终验证文件路径，防止路径遍历（../）" . PHP_EOL;
}

// ============================================================
// 主函数
// ============================================================

function main(): void {
    echo PHP_EOL;
    echo "============================================================" . PHP_EOL;
    echo "  PHP 基础语法示例（安全从业者视角）" . PHP_EOL;
    echo "  PHP Basics for Security Practitioners" . PHP_EOL;
    echo "============================================================" . PHP_EOL;
    echo PHP_EOL;
    echo "  PHP 版本: " . PHP_VERSION . PHP_EOL;
    echo "  运行模式: " . PHP_SAPI . PHP_EOL;

    // 1. 变量与数据类型
    demoVariablesAndTypes();

    // 2. 运算符与比较
    demoOperators();

    // 3. 流程控制
    demoControlFlow();

    // 4. 函数
    demoFunctions();

    // 5. 数组
    demoArrays();

    // 6. 字符串操作
    demoStrings();

    // 7. 表单处理
    demoFormHandling();

    // 8. Session 与 Cookie
    demoSessionAndCookie();

    // 9. 数据库操作
    demoDatabase();

    // 10. 文件操作
    demoFileIO();

    echo PHP_EOL;
    echo "============================================================" . PHP_EOL;
    echo "  所有示例执行完毕" . PHP_EOL;
    echo "  涵盖：变量、数据类型、运算符、流程控制、函数、" . PHP_EOL;
    echo "  数组、字符串、表单、Session、数据库、文件操作" . PHP_EOL;
    echo "============================================================" . PHP_EOL;
    echo PHP_EOL;
}

// 运行主函数
main();
