# net/http - Go 语言 HTTP 包

> Go 标准库 HTTP 包，提供 HTTP 客户端和服务器功能。

---

## 一、HTTP 客户端

### 1.1 基本 GET 请求

```go
package main

import (
    "fmt"
    "io"
    "net/http"
)

func main() {
    // 简单 GET
    resp, err := http.Get("https://api.example.com/users")
    if err != nil {
        fmt.Println("请求失败:", err)
        return
    }
    defer resp.Body.Close()  // 必须关闭响应体
    
    fmt.Println("状态码:", resp.StatusCode)
    fmt.Println("状态:", resp.Status)
    
    // 读取响应体
    body, err := io.ReadAll(resp.Body)
    if err != nil {
        fmt.Println("读取失败:", err)
        return
    }
    
    fmt.Println("响应:", string(body))
}
```

### 1.2 自定义请求

```go
import (
    "bytes"
    "encoding/json"
    "net/http"
    "time"
)

// 自定义 Client
client := &http.Client{
    Timeout: 10 * time.Second,  // 请求超时
    Transport: &http.Transport{
        MaxIdleConns:       10,
        IdleConnTimeout:    30 * time.Second,
        DisableCompression: false,
    },
}

// GET 请求带 Header
req, err := http.NewRequest("GET", "https://api.example.com/data", nil)
if err != nil {
    // 处理错误
}

req.Header.Set("Authorization", "Bearer token123")
req.Header.Set("Accept", "application/json")
req.Header.Set("User-Agent", "MyApp/1.0")

resp, err := client.Do(req)

// POST JSON
data := map[string]string{"name": "John", "email": "john@example.com"}
jsonData, _ := json.Marshal(data)

req, err = http.NewRequest("POST", "https://api.example.com/users", 
    bytes.NewBuffer(jsonData))
req.Header.Set("Content-Type", "application/json")

resp, err = client.Do(req)

// POST 表单
import "net/url"

formData := url.Values{
    "username": {"john"},
    "password": {"secret"},
}
resp, err = http.PostForm("https://api.example.com/login", formData)
```

### 1.3 响应处理

```go
resp, err := http.Get("https://api.example.com/data")
if err != nil {
    // 网络错误
    return
}
defer resp.Body.Close()

// 检查状态码
if resp.StatusCode != http.StatusOK {
    fmt.Printf("HTTP 错误: %d\n", resp.StatusCode)
    return
}

// 获取响应头
contentType := resp.Header.Get("Content-Type")
contentLength := resp.ContentLength

// 遍历响应头
for key, values := range resp.Header {
    for _, value := range values {
        fmt.Printf("%s: %s\n", key, value)
    }
}

// JSON 解析
var result map[string]interface{}
err = json.NewDecoder(resp.Body).Decode(&result)

// 流式读取（大文件下载）
buf := make([]byte, 4096)
for {
    n, err := resp.Body.Read(buf)
    if n > 0 {
        // 处理 buf[:n]
    }
    if err == io.EOF {
        break
    }
    if err != nil {
        // 错误处理
        break
    }
}
```

### 1.4 下载文件

```go
import (
    "io"
    "net/http"
    "os"
)

func downloadFile(url, filepath string) error {
    resp, err := http.Get(url)
    if err != nil {
        return err
    }
    defer resp.Body.Close()
    
    if resp.StatusCode != http.StatusOK {
        return fmt.Errorf("bad status: %s", resp.Status)
    }
    
    out, err := os.Create(filepath)
    if err != nil {
        return err
    }
    defer out.Close()
    
    _, err = io.Copy(out, resp.Body)
    return err
}

// 带进度的下载
func downloadWithProgress(url, filepath string) error {
    resp, err := http.Get(url)
    if err != nil {
        return err
    }
    defer resp.Body.Close()
    
    total := resp.ContentLength
    
    out, err := os.Create(filepath)
    if err != nil {
        return err
    }
    defer out.Close()
    
    // 自定义 Reader 跟踪进度
    progressReader := &progressReader{
        Reader: resp.Body,
        Total:  total,
    }
    
    _, err = io.Copy(out, progressReader)
    return err
}

type progressReader struct {
    Reader io.Reader
    Total  int64
    Read   int64
}

func (pr *progressReader) Read(p []byte) (int, error) {
    n, err := pr.Reader.Read(p)
    if n > 0 {
        pr.Read += int64(n)
        if pr.Total > 0 {
            percent := float64(pr.Read) / float64(pr.Total) * 100
            fmt.Printf("\r下载进度: %.2f%%", percent)
        }
    }
    return n, err
}
```

---

## 二、HTTP 服务器

### 2.1 简单服务器

```go
package main

import (
    "fmt"
    "net/http"
)

func helloHandler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello, World!")
}

func main() {
    http.HandleFunc("/hello", helloHandler)
    
    fmt.Println("服务器启动在 :8080")
    http.ListenAndServe(":8080", nil)
}
```

### 2.2 路由与处理函数

```go
package main

import (
    "encoding/json"
    "net/http"
)

type User struct {
    ID   int    `json:"id"`
    Name string `json:"name"`
}

func main() {
    mux := http.NewServeMux()
    
    // GET /users
    mux.HandleFunc("GET /users", func(w http.ResponseWriter, r *http.Request) {
        users := []User{
            {ID: 1, Name: "Alice"},
            {ID: 2, Name: "Bob"},
        }
        w.Header().Set("Content-Type", "application/json")
        json.NewEncoder(w).Encode(users)
    })
    
    // POST /users
    mux.HandleFunc("POST /users", func(w http.ResponseWriter, r *http.Request) {
        var user User
        if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
            http.Error(w, "无效的请求体", http.StatusBadRequest)
            return
        }
        
        w.Header().Set("Content-Type", "application/json")
        w.WriteHeader(http.StatusCreated)
        json.NewEncoder(w).Encode(user)
    })
    
    // 路径参数 (Go 1.22+)
    mux.HandleFunc("GET /users/{id}", func(w http.ResponseWriter, r *http.Request) {
        id := r.PathValue("id")
        fmt.Fprintf(w, "用户 ID: %s", id)
    })
    
    http.ListenAndServe(":8080", mux)
}
```

### 2.3 自定义服务器配置

```go
server := &http.Server{
    Addr:         ":8080",
    Handler:      mux,
    ReadTimeout:  10 * time.Second,   // 读超时
    WriteTimeout: 10 * time.Second,   // 写超时
    IdleTimeout:  120 * time.Second,  // 空闲超时
    MaxHeaderBytes: 1 << 20,          // 最大请求头 1MB
}

server.ListenAndServe()

// HTTPS 服务器
server.ListenAndServeTLS("cert.pem", "key.pem")

// 优雅关闭
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
server.Shutdown(ctx)
```

### 2.4 中间件

```go
// 日志中间件
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        fmt.Printf("开始: %s %s\n", r.Method, r.URL.Path)
        
        next.ServeHTTP(w, r)
        
        fmt.Printf("完成: %s %s (耗时: %v)\n", 
            r.Method, r.URL.Path, time.Since(start))
    })
}

// 认证中间件
func authMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        token := r.Header.Get("Authorization")
        if token == "" {
            http.Error(w, "未授权", http.StatusUnauthorized)
            return
        }
        
        // 验证 token...
        if !validToken(token) {
            http.Error(w, "无效的 token", http.StatusUnauthorized)
            return
        }
        
        next.ServeHTTP(w, r)
    })
}

// 恢复中间件（防止 panic 导致崩溃）
func recoveryMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if err := recover(); err != nil {
                fmt.Println("Panic:", err)
                http.Error(w, "服务器内部错误", http.StatusInternalServerError)
            }
        }()
        next.ServeHTTP(w, r)
    })
}

// 使用中间件
mux := http.NewServeMux()
mux.HandleFunc("/", handler)

// 链式应用
handler := recoveryMiddleware(loggingMiddleware(authMiddleware(mux)))
http.ListenAndServe(":8080", handler)
```

---

## 三、安全相关内容

### 3.1 常见 Web 安全问题

```go
/*
    Go Web 开发常见安全问题：
    
    1. SQL 注入 - 使用 database/sql 的参数化查询
    2. XSS - 模板自动转义（html/template）
    3. CSRF - 验证 CSRF Token
    4. 路径遍历 - 路径清理和验证
    5. SSRF - URL 白名单和内网 IP 检查
    6. 认证绕过 - 正确的中间件实现
    7. 敏感信息泄露 - 错误信息脱敏
*/

// ===== XSS 防护 =====
// html/template 包自动转义
import "html/template"

tmpl := template.Must(template.New("test").Parse(`<h1>{{.Name}}</h1>`))
// 即使 Name 是 <script>alert(1)</script>，也会被转义

// 但要注意：
// {{.Name}}      - 自动转义（安全）
// {{.Name | html}} - 显式转义
// {{.Name | safeHTML}} - 不转义（危险，要确保内容安全）
```

### 3.2 输入验证

```go
import (
    "net/http"
    "strconv"
    "strings"
)

// 验证用户 ID
func validateUserID(idStr string) (int, error) {
    id, err := strconv.Atoi(idStr)
    if err != nil {
        return 0, fmt.Errorf("无效的用户 ID")
    }
    if id <= 0 {
        return 0, fmt.Errorf("用户 ID 必须大于 0")
    }
    return id, nil
}

// 验证邮箱
func validateEmail(email string) bool {
    // 简单验证
    if len(email) > 254 {
        return false
    }
    atIndex := strings.Index(email, "@")
    return atIndex > 0 && atIndex < len(email)-1
}

// 限制请求体大小（防止大请求攻击）
func maxBytesMiddleware(maxBytes int64, next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        r.Body = http.MaxBytesReader(w, r.Body, maxBytes)
        next.ServeHTTP(w, r)
    })
}

// 使用
handler := maxBytesMiddleware(10*1024*1024, mux)  // 限制 10MB
```

### 3.3 SSRF 防护

```go
import (
    "net"
    "net/http"
    "net/url"
    "time"
)

// 检查是否是内网/保留 IP
func isPrivateIP(ipStr string) bool {
    ip := net.ParseIP(ipStr)
    if ip == nil {
        return true
    }
    
    privateRanges := []string{
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "127.0.0.0/8",
        "169.254.0.0/16",
        "::1/128",
        "fc00::/7",
        "fe80::/10",
    }
    
    for _, cidr := range privateRanges {
        _, network, _ := net.ParseCIDR(cidr)
        if network.Contains(ip) {
            return true
        }
    }
    
    return false
}

// 安全的 HTTP 客户端（防止 SSRF）
func safeHTTPClient() *http.Client {
    transport := &http.Transport{
        DialContext: func(ctx context.Context, network, addr string) (net.Conn, error) {
            // 解析地址
            host, port, err := net.SplitHostPort(addr)
            if err != nil {
                return nil, err
            }
            
            // 解析 IP
            ips, err := net.LookupIP(host)
            if err != nil {
                return nil, err
            }
            
            // 检查每个 IP
            for _, ip := range ips {
                if isPrivateIP(ip.String()) {
                    return nil, fmt.Errorf("禁止访问内网 IP: %s", ip)
                }
            }
            
            // 使用默认 Dialer
            dialer := &net.Dialer{
                Timeout:   5 * time.Second,
                KeepAlive: 30 * time.Second,
            }
            return dialer.DialContext(ctx, network, addr)
        },
    }
    
    return &http.Client{
        Transport: transport,
        Timeout:   10 * time.Second,
    }
}
```

### 3.4 安全头设置

```go
func securityHeadersMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // 防止 MIME 类型嗅探
        w.Header().Set("X-Content-Type-Options", "nosniff")
        
        // 防止点击劫持
        w.Header().Set("X-Frame-Options", "DENY")
        
        // XSS 防护（现代浏览器用 CSP 替代）
        w.Header().Set("X-XSS-Protection", "1; mode=block")
        
        // 内容安全策略
        w.Header().Set("Content-Security-Policy", 
            "default-src 'self'; script-src 'self'")
        
        // Referrer 策略
        w.Header().Set("Referrer-Policy", "strict-origin-when-cross-origin")
        
        // HSTS（HTTPS 时）
        // w.Header().Set("Strict-Transport-Security", 
        //     "max-age=31536000; includeSubDomains")
        
        next.ServeHTTP(w, r)
    })
}
```

---

## 四、net/url 包

```go
import "net/url"

// 解析 URL
u, err := url.Parse("https://user:pass@example.com:8080/path?q=value#frag")
if err != nil { /* ... */ }

fmt.Println(u.Scheme)   // https
fmt.Println(u.User)     // user:pass
fmt.Println(u.Host)     // example.com:8080
fmt.Println(u.Hostname()) // example.com
fmt.Println(u.Port())   // 8080
fmt.Println(u.Path)     // /path
fmt.Println(u.RawQuery) // q=value
fmt.Println(u.Fragment) // frag

// 查询参数
params := u.Query()
fmt.Println(params.Get("q"))  // value

// 构造 URL 查询
params := url.Values{}
params.Set("page", "1")
params.Set("limit", "10")
params.Add("tag", "go")
params.Add("tag", "web")

u.RawQuery = params.Encode()
// ?limit=10&page=1&tag=go&tag=web

// URL 编码
encoded := url.QueryEscape("hello world")  // hello+world
decoded, _ := url.QueryUnescape("hello+world")  // hello world

// 路径拼接
base, _ := url.Parse("https://example.com/api/")
ref, _ := url.Parse("users")
full := base.ResolveReference(ref)
// https://example.com/api/users
```

---

## 五、常用状态码

| 常量 | 值 | 含义 |
|------|----|------|
| `http.StatusOK` | 200 | 成功 |
| `http.StatusCreated` | 201 | 已创建 |
| `http.StatusNoContent` | 204 | 无内容 |
| `http.StatusMovedPermanently` | 301 | 永久重定向 |
| `http.StatusFound` | 302 | 临时重定向 |
| `http.StatusBadRequest` | 400 | 错误请求 |
| `http.StatusUnauthorized` | 401 | 未授权 |
| `http.StatusForbidden` | 403 | 禁止访问 |
| `http.StatusNotFound` | 404 | 未找到 |
| `http.StatusMethodNotAllowed` | 405 | 方法不允许 |
| `http.StatusInternalServerError` | 500 | 服务器错误 |
| `http.StatusServiceUnavailable` | 503 | 服务不可用 |
