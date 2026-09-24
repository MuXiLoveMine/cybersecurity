<?php
/**
 * security_functions.php
 * PHP 安全函数库 - Web 安全实战
 *
 * 提供常用的安全防护函数：输入过滤、输出编码、安全加密等
 * 仅用于安全学习和授权测试
 */

// =============================================
// 一、输入安全过滤
// =============================================

/**
 * 安全获取 GET 参数
 */
function safeGet($key, $default = null, $filter = FILTER_DEFAULT) {
    return filter_input(INPUT_GET, $key, $filter) ?? $default;
}

/**
 * 安全获取 POST 参数
 */
function safePost($key, $default = null, $filter = FILTER_DEFAULT) {
    return filter_input(INPUT_POST, $key, $filter) ?? $default;
}

/**
 * 验证整数
 */
function validateInt($value, $min = null, $max = null) {
    $options = [];
    if ($min !== null) $options['min_range'] = $min;
    if ($max !== null) $options['max_range'] = $max;
    return filter_var($value, FILTER_VALIDATE_INT, ['options' => $options]) !== false;
}

/**
 * 验证邮箱
 */
function validateEmail($email) {
    return filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
}

/**
 * 验证 URL
 */
function validateUrl($url) {
    return filter_var($url, FILTER_VALIDATE_URL) !== false;
}

/**
 * 验证 IP 地址
 */
function validateIP($ip) {
    return filter_var($ip, FILTER_VALIDATE_IP) !== false;
}

/**
 * 清理字符串输入（去除危险字符）
 */
function sanitizeString($str) {
    // 去除前后空格
    $str = trim($str);
    // 去除 NULL 字节
    $str = str_replace(chr(0), '', $str);
    // 去除控制字符
    $str = preg_replace('/[\x00-\x1F\x7F]/', '', $str);
    return $str;
}

/**
 * 白名单过滤
 */
function whitelistFilter($input, array $allowed) {
    if (in_array($input, $allowed, true)) {
        return $input;
    }
    return null;
}

// =============================================
// 二、输出安全编码
// =============================================

/**
 * HTML 输出编码（防 XSS）
 */
function htmlOut($data) {
    return htmlspecialchars($data, ENT_QUOTES | ENT_HTML5, 'UTF-8');
}

/**
 * JavaScript 输出编码
 */
function jsOut($data) {
    // Unicode 编码特殊字符
    $encoded = '';
    $len = strlen($data);
    for ($i = 0; $i < $len; $i++) {
        $char = $data[$i];
        $ascii = ord($char);
        if ($ascii < 32 || $ascii > 126) {
            $encoded .= sprintf('\\u%04x', mb_ord($char, 'UTF-8'));
        } else if (in_array($char, ['<', '>', '"', "'", '\\', '/', '&'])) {
            $encoded .= sprintf('\\u%04x', $ascii);
        } else {
            $encoded .= $char;
        }
    }
    return $encoded;
}

/**
 * URL 输出编码
 */
function urlOut($data) {
    return rawurlencode($data);
}

/**
 * CSS 输出编码（防 CSS 注入）
 */
function cssOut($data) {
    // 只允许字母数字
    return preg_replace('/[^a-zA-Z0-9_-]/', '', $data);
}

// =============================================
// 三、加密与哈希
// =============================================

/**
 * 安全密码哈希（使用 bcrypt）
 */
function hashPassword($password) {
    return password_hash($password, PASSWORD_DEFAULT);
}

/**
 * 验证密码
 */
function verifyPassword($password, $hash) {
    return password_verify($password, $hash);
}

/**
 * 生成随机 Token
 */
function generateToken($length = 32) {
    return bin2hex(random_bytes($length));
}

/**
 * AES-256-CBC 加密
 */
function aesEncrypt($data, $key) {
    $iv = random_bytes(16);
    $encrypted = openssl_encrypt($data, 'AES-256-CBC', $key, OPENSSL_RAW_DATA, $iv);
    return base64_encode($iv . $encrypted);
}

/**
 * AES-256-CBC 解密
 */
function aesDecrypt($data, $key) {
    $data = base64_decode($data);
    $iv = substr($data, 0, 16);
    $encrypted = substr($data, 16);
    return openssl_decrypt($encrypted, 'AES-256-CBC', $key, OPENSSL_RAW_DATA, $iv);
}

// =============================================
// 四、CSRF 防护
// =============================================

/**
 * 生成 CSRF Token
 */
function csrfToken() {
    if (empty($_SESSION['csrf_token'])) {
        $_SESSION['csrf_token'] = generateToken(32);
    }
    return $_SESSION['csrf_token'];
}

/**
 * 输出 CSRF 隐藏字段
 */
function csrfField() {
    $token = csrfToken();
    echo '<input type="hidden" name="csrf_token" value="' . htmlOut($token) . '">';
}

/**
 * 验证 CSRF Token
 */
function csrfVerify() {
    $token = $_POST['csrf_token'] ?? '';
    $sessionToken = $_SESSION['csrf_token'] ?? '';
    if (!hash_equals($sessionToken, $token)) {
        http_response_code(403);
        die('CSRF Token 验证失败');
    }
}

// =============================================
// 五、文件上传安全
// =============================================

/**
 * 安全的文件上传处理
 */
function safeUpload($file, $uploadDir, $allowedTypes = ['jpg', 'jpeg', 'png', 'gif']) {
    // 检查上传错误
    if ($file['error'] !== UPLOAD_ERR_OK) {
        return ['success' => false, 'error' => '上传失败'];
    }

    // 检查文件大小（5MB 限制）
    if ($file['size'] > 5 * 1024 * 1024) {
        return ['success' => false, 'error' => '文件过大'];
    }

    // 白名单检查后缀
    $ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
    if (!in_array($ext, $allowedTypes)) {
        return ['success' => false, 'error' => '不允许的文件类型'];
    }

    // 检测真实文件类型
    $finfo = finfo_open(FILEINFO_MIME_TYPE);
    $mimeType = finfo_file($finfo, $file['tmp_name']);
    finfo_close($finfo);

    $allowedMimes = [
        'jpg' => 'image/jpeg', 'jpeg' => 'image/jpeg',
        'png' => 'image/png', 'gif' => 'image/gif'
    ];
    if (!isset($allowedMimes[$ext]) || $mimeType !== $allowedMimes[$ext]) {
        return ['success' => false, 'error' => '文件类型不匹配'];
    }

    // 随机重命名
    $newName = generateToken(16) . '.' . $ext;
    $destPath = rtrim($uploadDir, '/') . '/' . $newName;

    if (!move_uploaded_file($file['tmp_name'], $destPath)) {
        return ['success' => false, 'error' => '文件保存失败'];
    }

    return ['success' => true, 'filename' => $newName, 'path' => $destPath];
}

// =============================================
// 使用示例
// =============================================

session_start();

echo "===== PHP 安全函数库 =====\n\n";

// 密码哈希示例
$pwd = 'MyPassword123';
$hash = hashPassword($pwd);
echo "密码哈希示例:\n";
echo "  原文: $pwd\n";
echo "  哈希: $hash\n";
echo "  验证: " . (verifyPassword($pwd, $hash) ? '通过' : '失败') . "\n\n";

// Token 生成
echo "CSRF Token: " . csrfToken() . "\n\n";

// AES 加解密
$key = str_repeat('a', 32); // 256 位密钥
$plain = '这是一段敏感数据';
$encrypted = aesEncrypt($plain, $key);
$decrypted = aesDecrypt($encrypted, $key);
echo "AES-256-CBC 加解密:\n";
echo "  原文: $plain\n";
echo "  密文: $encrypted\n";
echo "  解密: $decrypted\n\n";

// 输入验证
echo "输入验证示例:\n";
echo "  邮箱 admin@test.com: " . (validateEmail('admin@test.com') ? '有效' : '无效') . "\n";
echo "  邮箱 invalid: " . (validateEmail('invalid') ? '有效' : '无效') . "\n";
echo "  整数 42(1-100): " . (validateInt('42', 1, 100) ? '有效' : '无效') . "\n";
echo "  整数 999(1-100): " . (validateInt('999', 1, 100) ? '有效' : '无效') . "\n";

// XSS 防护
$dangerous = '<script>alert("XSS")</script>';
echo "\nXSS 防护:\n";
echo "  原始: $dangerous\n";
echo "  编码: " . htmlOut($dangerous) . "\n";

echo "\n===== 安全函数库演示完成 =====\n";
