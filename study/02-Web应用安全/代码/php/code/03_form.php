<?php
// 03_form.php
// 表单处理示例

$error = "";
$success = "";

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = trim($_POST["username"] ?? "");
    $password = $_POST["password"] ?? "";
    $gender = $_POST["gender"] ?? "";
    $hobby = $_POST["hobby"] ?? [];
    $city = $_POST["city"] ?? "";
    $message = trim($_POST["message"] ?? "");

    if (empty($username)) {
        $error = "用户名不能为空";
    } elseif (strlen($password) < 6) {
        $error = "密码至少 6 位";
    } else {
        $success = "表单提交成功！";
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>表单示例</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: inline-block; width: 80px; }
        input, select, textarea { padding: 5px; }
        .error { color: red; }
        .success { color: green; }
    </style>
</head>
<body>
    <h2>用户注册表单</h2>

    <?php if ($error): ?>
        <p class="error"><?php echo htmlspecialchars($error); ?></p>
    <?php endif; ?>

    <?php if ($success): ?>
        <p class="success"><?php echo htmlspecialchars($success); ?></p>
        <ul>
            <li>用户名: <?php echo htmlspecialchars($username); ?></li>
            <li>性别: <?php echo htmlspecialchars($gender); ?></li>
            <li>爱好: <?php echo htmlspecialchars(implode(", ", $hobby)); ?></li>
            <li>城市: <?php echo htmlspecialchars($city); ?></li>
            <li>留言: <?php echo nl2br(htmlspecialchars($message)); ?></li>
        </ul>
    <?php endif; ?>

    <form method="POST" action="">
        <div class="form-group">
            <label>用户名：</label>
            <input type="text" name="username" value="<?php echo htmlspecialchars($username ?? ''); ?>">
        </div>
        <div class="form-group">
            <label>密码：</label>
            <input type="password" name="password">
        </div>
        <div class="form-group">
            <label>性别：</label>
            <input type="radio" name="gender" value="male" <?php echo ($gender ?? '') == 'male' ? 'checked' : ''; ?>> 男
            <input type="radio" name="gender" value="female" <?php echo ($gender ?? '') == 'female' ? 'checked' : ''; ?>> 女
        </div>
        <div class="form-group">
            <label>爱好：</label>
            <input type="checkbox" name="hobby[]" value="reading"> 阅读
            <input type="checkbox" name="hobby[]" value="music"> 音乐
            <input type="checkbox" name="hobby[]" value="sports"> 运动
        </div>
        <div class="form-group">
            <label>城市：</label>
            <select name="city">
                <option value="">请选择</option>
                <option value="beijing">北京</option>
                <option value="shanghai">上海</option>
                <option value="guangzhou">广州</option>
            </select>
        </div>
        <div class="form-group">
            <label>留言：</label>
            <textarea name="message" rows="4" cols="30"><?php echo htmlspecialchars($message ?? ''); ?></textarea>
        </div>
        <button type="submit">提交</button>
        <button type="reset">重置</button>
    </form>
</body>
</html>
