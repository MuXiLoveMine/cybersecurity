
---

## 四、高级实战案例

### 4.1 并发端口扫描器

利用 Go 的 goroutine 实现高性能并发端口扫描。

```go
package main

import (
    "fmt"
    "net"
    "sort"
    "sync"
    "time"
)

// 端口扫描器
type PortScanner struct {
    Host        string
    Timeout     time.Duration
    Concurrency int
}

func NewPortScanner(host string) *PortScanner {
    return &PortScanner{
        Host:        host,
        Timeout:     800 * time.Millisecond,
        Concurrency: 100,
    }
}

// 扫描单个端口
func (ps *PortScanner) ScanPort(port int) bool {
    conn, err := net.DialTimeout("tcp", fmt.Sprintf("%s:%d", ps.Host, port), ps.Timeout)
    if err != nil {
        return false
    }
    conn.Close()
    return true
}

// 批量扫描（带并发控制）
func (ps *PortScanner) ScanRange(start, end int) []int {
    var wg sync.WaitGroup
    var mu sync.Mutex
    openPorts := []int{}
    
    // 信号量模式：使用缓冲通道控制并发
    semaphore := make(chan struct{}, ps.Concurrency)
    
    for port := start; port <= end; port++ {
        wg.Add(1)
        go func(p int) {
            defer wg.Done()
            semaphore <- struct{}{}        // 获取信号量
            defer func() { <-semaphore }() // 释放信号量
            
            if ps.ScanPort(p) {
                mu.Lock()
                openPorts = append(openPorts, p)
                mu.Unlock()
            }
        }(port)
    }
    
    wg.Wait()
    sort.Ints(openPorts)
    return openPorts
}

// 服务版本探测
func (ps *PortScanner) BannerGrab(port int) string {
    conn, err := net.DialTimeout("tcp", fmt.Sprintf("%s:%d", ps.Host, port), ps.Timeout)
    if err != nil {
        return ""
    }
    defer conn.Close()
    
    // 发送一些数据触发响应
    conn.Write([]byte("HEAD / HTTP/1.0\r\n\r\n"))
    
    buf := make([]byte, 1024)
    conn.SetReadDeadline(time.Now().Add(ps.Timeout))
    n, _ := conn.Read(buf)
    
    return string(buf[:n])
}

func main() {
    scanner := NewPortScanner("127.0.0.1")
    scanner.Concurrency = 200
    
    fmt.Println("开始扫描...")
    start := time.Now()
    
    openPorts := scanner.ScanRange(1, 1000)
    
    fmt.Printf("扫描完成，用时 %v\n", time.Since(start))
    fmt.Printf("发现 %d 个开放端口:\n", len(openPorts))
    
    for _, port := range openPorts {
        banner := scanner.BannerGrab(port)
        if len(banner) > 50 {
            banner = banner[:50] + "..."
        }
        fmt.Printf("  端口 %d: %s\n", port, banner)
    }
}
```

### 4.2 Web 漏洞扫描器

使用 Go 标准库实现的轻量级 Web 漏洞扫描器。

```go
package main

import (
    "crypto/tls"
    "fmt"
    "io"
    "net/http"
    "net/url"
    "strings"
    "sync"
    "time"
)

// 漏洞信息
type Vulnerability struct {
    Name        string
    Severity    string // critical/high/medium/low/info
    URL         string
    Description string
    Evidence    string
}

// Web 扫描器
type WebScanner struct {
    BaseURL string
    Client  *http.Client
    vulns   []Vulnerability
    mu      sync.Mutex
}

func NewWebScanner(baseURL string) *WebScanner {
    return &WebScanner{
        BaseURL: strings.TrimRight(baseURL, "/"),
        Client: &http.Client{
            Timeout: 5 * time.Second,
            Transport: &http.Transport{
                TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
            },
            CheckRedirect: func(req *http.Request, via []*http.Request) error {
                return http.ErrUseLastResponse // 不跟随重定向
            },
        },
    }
}

// 发送请求
func (ws *WebScanner) SendRequest(method, path string) (*http.Response, string, error) {
    fullURL := ws.BaseURL + path
    req, err := http.NewRequest(method, fullURL, nil)
    if err != nil {
        return nil, "", err
    }
    
    req.Header.Set("User-Agent", "Mozilla/5.0 (compatible; GoScanner/1.0)")
    
    resp, err := ws.Client.Do(req)
    if err != nil {
        return nil, "", err
    }
    defer resp.Body.Close()
    
    body, _ := io.ReadAll(resp.Body)
    return resp, string(body), nil
}

// SQL 注入检测插件
func (ws *WebScanner) CheckSQLi(path string, param string) {
    payloads := []string{
        "'",
        "' OR '1'='1",
        "' AND 1=2 UNION SELECT 1,2,3--",
        "' AND SLEEP(3)--",
    }
    
    u, _ := url.Parse(ws.BaseURL + path)
    q := u.Query()
    
    for _, payload := range payloads {
        q.Set(param, payload)
        u.RawQuery = q.Encode()
        
        resp, body, err := ws.SendRequest("GET", "?"+u.RawQuery)
        if err != nil {
            continue
        }
        
        // 检查 SQL 错误特征
        errors := []string{
            "MySQL syntax", "SQL syntax", "ORA-",
            "PostgreSQL", "Microsoft SQL Server",
            "Warning: mysql_", "unclosed quotation mark",
        }
        
        for _, errMsg := range errors {
            if strings.Contains(strings.ToLower(body), strings.ToLower(errMsg)) {
                ws.addVuln(Vulnerability{
                    Name:        "SQL Injection",
                    Severity:    "critical",
                    URL:         u.String(),
                    Description: fmt.Sprintf("参数 %s 可能存在 SQL 注入", param),
                    Evidence:    errMsg,
                })
                break
            }
        }
        
        _ = resp
    }
}

// XSS 检测插件
func (ws *WebScanner) CheckXSS(path string, param string) {
    payload := "<script>alert('xss_test')</script>"
    
    u, _ := url.Parse(ws.BaseURL + path)
    q := u.Query()
    q.Set(param, payload)
    u.RawQuery = q.Encode()
    
    _, body, err := ws.SendRequest("GET", "?"+u.RawQuery)
    if err != nil {
        return
    }
    
    if strings.Contains(body, payload) {
        ws.addVuln(Vulnerability{
            Name:        "Reflected XSS",
            Severity:    "high",
            URL:         u.String(),
            Description: fmt.Sprintf("参数 %s 存在反射型 XSS", param),
            Evidence:    payload,
        })
    }
}

// 目录爆破
func (ws *WebScanner) DirBrute(wordlist []string) []string {
    var found []string
    var wg sync.WaitGroup
    var mu sync.Mutex
    
    semaphore := make(chan struct{}, 30)
    
    for _, path := range wordlist {
        wg.Add(1)
        go func(p string) {
            defer wg.Done()
            semaphore <- struct{}{}
            defer func() { <-semaphore }()
            
            resp, _, err := ws.SendRequest("GET", "/"+p)
            if err != nil {
                return
            }
            
            if resp.StatusCode != 404 {
                mu.Lock()
                found = append(found, fmt.Sprintf("[%d] /%s", resp.StatusCode, p))
                mu.Unlock()
            }
        }(path)
    }
    
    wg.Wait()
    return found
}

func (ws *WebScanner) addVuln(v Vulnerability) {
    ws.mu.Lock()
    ws.vulns = append(ws.vulns, v)
    ws.mu.Unlock()
}

func (ws *WebScanner) Vulnerabilities() []Vulnerability {
    ws.mu.Lock()
    defer ws.mu.Unlock()
    return ws.vulns
}

func main() {
    scanner := NewWebScanner("http://example.com")
    
    // 检查 SQL 注入
    scanner.CheckSQLi("/page", "id")
    
    // 检查 XSS
    scanner.CheckXSS("/search", "q")
    
    // 输出结果
    for _, v := range scanner.Vulnerabilities() {
        fmt.Printf("[%s] %s: %s\n", v.Severity, v.Name, v.URL)
    }
}
```

### 4.3 加密与证书工具

Go 语言加密库高级用法和 TLS 安全配置。

```go
package main

import (
    "crypto/aes"
    "crypto/cipher"
    "crypto/ecdsa"
    "crypto/elliptic"
    "crypto/rand"
    "crypto/rsa"
    "crypto/sha256"
    "crypto/tls"
    "crypto/x509"
    "crypto/x509/pkix"
    "encoding/base64"
    "encoding/pem"
    "fmt"
    "math/big"
    "net/http"
    "os"
    "time"
)

// ===== 加密工具类 =====

// AES 加密（GCM 模式）
func AESGCMEncrypt(plaintext, key []byte) ([]byte, error) {
    block, err := aes.NewCipher(key)
    if err != nil {
        return nil, err
    }
    
    gcm, err := cipher.NewGCM(block)
    if err != nil {
        return nil, err
    }
    
    nonce := make([]byte, gcm.NonceSize())
    if _, err := rand.Read(nonce); err != nil {
        return nil, err
    }
    
    ciphertext := gcm.Seal(nonce, nonce, plaintext, nil)
    return ciphertext, nil
}

func AESGCMDecrypt(ciphertext, key []byte) ([]byte, error) {
    block, err := aes.NewCipher(key)
    if err != nil {
        return nil, err
    }
    
    gcm, err := cipher.NewGCM(block)
    if err != nil {
        return nil, err
    }
    
    nonceSize := gcm.NonceSize()
    nonce, ciphertext := ciphertext[:nonceSize], ciphertext[nonceSize:]
    
    return gcm.Open(nil, nonce, ciphertext, nil)
}

// 哈希计算
func Sha256(data string) string {
    h := sha256.Sum256([]byte(data))
    return fmt.Sprintf("%x", h)
}

// Base64
func B64Encode(data string) string {
    return base64.StdEncoding.EncodeToString([]byte(data))
}

func B64Decode(data string) (string, error) {
    b, err := base64.StdEncoding.DecodeString(data)
    return string(b), err
}

// ===== RSA 非对称加密 =====

func GenerateRSAKey(bits int) (*rsa.PrivateKey, error) {
    return rsa.GenerateKey(rand.Reader, bits)
}

func RSAEncrypt(publicKey *rsa.PublicKey, plaintext []byte) ([]byte, error) {
    return rsa.EncryptOAEP(sha256.New(), rand.Reader, publicKey, plaintext, nil)
}

func RSADecrypt(privateKey *rsa.PrivateKey, ciphertext []byte) ([]byte, error) {
    return privateKey.Decrypt(rand.Reader, ciphertext, &rsa.OAEPOptions{Hash: sha256.New()})
}

// ===== ECDSA 签名 =====

func GenerateECDSAKey() (*ecdsa.PrivateKey, error) {
    return ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
}

func ECDSASign(privateKey *ecdsa.PrivateKey, data []byte) (r, s *big.Int, err error) {
    hash := sha256.Sum256(data)
    return ecdsa.Sign(rand.Reader, privateKey, hash[:])
}

func ECDSAVerify(publicKey *ecdsa.PublicKey, data []byte, r, s *big.Int) bool {
    hash := sha256.Sum256(data)
    return ecdsa.Verify(publicKey, hash[:], r, s)
}

// ===== 自签名证书生成 =====

func GenerateSelfSignedCert() (tls.Certificate, error) {
    // 生成私钥
    priv, err := rsa.GenerateKey(rand.Reader, 2048)
    if err != nil {
        return tls.Certificate{}, err
    }
    
    // 证书模板
    template := x509.Certificate{
        SerialNumber: big.NewInt(1),
        Subject: pkix.Name{
            Organization: []string{"Test Org"},
            CommonName:   "localhost",
        },
        NotBefore: time.Now(),
        NotAfter:  time.Now().Add(365 * 24 * time.Hour),
        KeyUsage:  x509.KeyUsageKeyEncipherment | x509.KeyUsageDigitalSignature,
        ExtKeyUsage: []x509.ExtKeyUsage{
            x509.ExtKeyUsageServerAuth,
        },
        DNSNames: []string{"localhost", "127.0.0.1"},
    }
    
    // 自签名
    certDER, err := x509.CreateCertificate(rand.Reader, &template, &template, &priv.PublicKey, priv)
    if err != nil {
        return tls.Certificate{}, err
    }
    
    // 编码为 PEM
    certPEM := pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: certDER})
    keyPEM := pem.EncodeToMemory(&pem.Block{Type: "RSA PRIVATE KEY", Bytes: x509.MarshalPKCS1PrivateKey(priv)})
    
    return tls.X509KeyPair(certPEM, keyPEM)
}

// ===== 安全 TLS 配置 =====

func secureTLSConfig() *tls.Config {
    return &tls.Config{
        MinVersion: tls.VersionTLS12,
        CipherSuites: []uint16{
            tls.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,
            tls.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
            tls.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305,
            tls.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305,
        },
        CurvePreferences: []tls.CurveID{
            tls.CurveP256,
            tls.X25519,
        },
        InsecureSkipVerify: false, // 必须验证证书！
    }
}

func main() {
    // AES 示例
    key := make([]byte, 32) // 256位密钥
    rand.Read(key)
    
    encrypted, _ := AESGCMEncrypt([]byte("Hello, Go!"), key)
    decrypted, _ := AESGCMDecrypt(encrypted, key)
    fmt.Printf("AES 解密结果: %s\n", decrypted)
    
    // 哈希示例
    fmt.Printf("SHA256: %s\n", Sha256("test"))
}
```

---

## 五、进阶学习资源

### 5.1 Go 安全资源

- **Go 官方安全文档**：https://go.dev/doc/security
- **Go 安全最佳实践**：https://github.com/guardrailsio/awesome-golang-security
- **OWASP Go 安全**：https://cheatsheetseries.owasp.org/cheatsheets/Go_Security_Cheat_Sheet.html
- **Golang 安全指南**：https://github.com/0xInfection/Awesome-Go-Security

### 5.2 安全工具与库

- **加密库**：
  - crypto 标准库
  - golang.org/x/crypto — 扩展加密库
  - github.com/secure-io/sio-go — 安全 I/O

- **网络安全**：
  - crypto/tls — TLS/SSL
  - net/http — HTTP 安全配置
  - github.com/labstack/echo — 高性能 Web 框架
  - github.com/gin-gonic/gin — 流行 Web 框架

- **安全工具**：
  - gfuzz — Go Fuzzing
  - gosec — Go 安全检查器
  - staticcheck — 静态分析
  - golangci-lint — Linter 集合

### 5.3 Go 安全审计

常见 Go 漏洞类型：
- SQL 注入（database/sql 拼接）
- 命令注入（os/exec 用户输入）
- 路径遍历（filepath 操作）
- 整数溢出
- 并发安全问题（race condition）
- 内存安全（unsafe 包）
- JSON 反序列化
- 模板注入（html/template）

审计工具：
- **gosec**：https://github.com/securecodewarrior/gosec — Go 安全检查
- **golangci-lint**：https://golangci-lint.run/ — 包含安全检查
- **govulncheck**：https://go.dev/security/vuln/ — Go 官方漏洞检测

### 5.4 CTF 与练习平台

- **Hack The Box**：https://www.hackthebox.com/
- **TryHackMe**：https://tryhackme.com/
- **picoCTF**：https://picoctf.org/
- **Bugku**：https://ctf.bugku.com/
- **攻防世界**：https://adworld.xctf.org.cn/
- **BUUCTF**：https://buuoj.cn/

### 5.5 推荐书籍

- **Go 语言**：
  - 《Go 语言圣经》（The Go Programming Language）
  - 《Go 语言高级编程》
  - 《Go 并发编程实战》

- **Web 安全**：
  - 《白帽子讲 Web 安全》
  - 《Web 安全深度剖析》
  - 《Go 语言实战》

### 5.6 社区与博客

- **Go 官方博客**：https://go.dev/blog/
- **Go 安全公告**：https://go.dev/security/
- **FreeBuf**：https://www.freebuf.com/
- **安全客**：https://www.anquanke.com/
- **先知社区**：https://xz.aliyun.com/

### 5.7 进阶学习路线

**第 1 阶段：Go 深入（1-2月）**
- 并发编程（goroutine/channel/context）
- 接口、反射、泛型
- 内存管理与 GC
- 标准库深入

**第 2 阶段：Web 开发（2-3月）**
- Gin/Echo 等框架
- RESTful API 开发
- 中间件与认证
- 数据库操作

**第 3 阶段：安全基础（2-3月）**
- Web 常见漏洞
- Go 特有安全问题
- 代码审计方法

**第 4 阶段：工具开发（2-3月）**
- 并发安全工具开发
- 网络编程与协议分析
- 高性能扫描器开发

**第 5 阶段：实战与 CTF（持续）**
- 参加 CTF 比赛
- 开发安全工具
- 研究 Go 相关漏洞
