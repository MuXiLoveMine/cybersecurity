# Invoke-WebRequest

> **分类**：网络请求
> **说明**：发起 HTTP/HTTPS 请求

---

## 语法

```powershell
Invoke-WebRequest [-Uri] <Uri> [-Method <WebRequestMethod>] [-Headers <IDictionary>] [-Body <Object>]
```

## 别名

iwr / wget / curl

## 常用参数

-Method GET/POST/PUT/DELETE / -Headers 请求头 / -Body 请求体 / -UseBasicParsing 基础解析 / -OutFile 保存到文件 / -SessionVariable 会话变量

## 示例代码

```powershell
# 基本 GET 请求
$response = Invoke-WebRequest -Uri "https://api.example.com/data"
$response.Content
$response.StatusCode

# 使用 UseBasicParsing（无需 IE 引擎）
$resp = Invoke-WebRequest -Uri $url -UseBasicParsing
$resp.Content

# POST 请求（JSON）
$body = @{
    name = "Alice"
    age = 25
} | ConvertTo-Json

$resp = Invoke-WebRequest -Uri $url -Method Post -Body $body -ContentType "application/json"

# POST 表单
$form = @{
    username = "admin"
    password = "123456"
}
$resp = Invoke-WebRequest -Uri $loginUrl -Method Post -Body $form -SessionVariable session

# 带请求头
$headers = @{
    "Authorization" = "Bearer token123"
    "X-Custom-Header" = "value"
}
$resp = Invoke-WebRequest -Uri $url -Headers $headers

# 下载文件
Invoke-WebRequest -Uri "https://example.com/file.zip" -OutFile "file.zip"

# 会话保持（登录后继续使用）
$login = Invoke-WebRequest -Uri $loginUrl -Method Post -Body $form -SessionVariable sess
$dashboard = Invoke-WebRequest -Uri $dashUrl -WebSession $sess

# 处理 JSON 响应（更简单的方式）
$data = Invoke-RestMethod -Uri $apiUrl -Method Get
$data.name  # 直接访问属性

# 超时设置
$resp = Invoke-WebRequest -Uri $url -TimeoutSec 10

# 忽略 SSL 证书错误（仅测试用！）
[System.Net.ServicePointManager]::ServerCertificateValidationCallback = {$true}
```
