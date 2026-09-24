// security_cases.go —— Go 安全案例集（防御/学习视角）
//
// 涵盖 4 个安全案例：
//   1. 并发端口扫描器 —— Worker Pool 模式，高可控并发
//   2. HTTP 安全头检测 —— 检测网站安全响应头配置
//   3. 文件哈希校验工具 —— MD5/SHA1/SHA256 多算法计算
//   4. TLS 证书检查 —— 证书有效期、颁发者、协议版本
//
// 运行方式:
//   go run security_cases.go              # 运行所有案例
//   go run security_cases.go --help       # 查看帮助
//   go run security_cases.go scan         # 端口扫描
//   go run security_cases.go http         # HTTP 安全头检测
//   go run security_cases.go hash         # 文件哈希校验
//   go run security_cases.go cert         # TLS 证书检查
//
// 注意：
//   - 所有工具仅限在授权的环境中学习和使用
//   - 端口扫描功能请勿用于未授权的网络
//   - 生产环境请使用专业安全工具

package main

import (
	"crypto/md5"
	"crypto/sha1"
	"crypto/sha256"
	"crypto/tls"
	"crypto/x509"
	"encoding/hex"
	"flag"
	"fmt"
	"io"
	"net"
	"net/http"
	"os"
	"sort"
	"strings"
	"sync"
	"time"
)

// ============================================================
// 辅助函数
// ============================================================

const (
	colorReset  = "\033[0m"
	colorRed    = "\033[31m"
	colorGreen  = "\033[32m"
	colorYellow = "\033[33m"
	colorBlue   = "\033[34m"
	colorCyan   = "\033[36m"
)

func info(msg string)    { fmt.Printf("%s[INFO]%s  %s\n", colorBlue, colorReset, msg) }
func success(msg string) { fmt.Printf("%s[OK]%s    %s\n", colorGreen, colorReset, msg) }
func warn(msg string)    { fmt.Printf("%s[WARN]%s  %s\n", colorYellow, colorReset, msg) }
func errorMsg(msg string) { fmt.Printf("%s[ERROR]%s %s\n", colorRed, colorReset, msg) }
func section(title string) {
	fmt.Println()
	fmt.Printf("%s=== %s ===%s\n", colorCyan, title, colorReset)
	fmt.Println()
}

// ============================================================
// 帮助信息
// ============================================================

func showHelp() {
	fmt.Println()
	fmt.Println("Go 安全案例集 - 使用帮助")
	fmt.Println("==============================")
	fmt.Println()
	fmt.Println("用法: go run security_cases.go [模式] [选项]")
	fmt.Println()
	fmt.Println("模式:")
	fmt.Println("  all        运行所有案例（默认）")
	fmt.Println("  scan       并发端口扫描")
	fmt.Println("  http       HTTP 安全头检测")
	fmt.Println("  hash       文件哈希校验")
	fmt.Println("  cert       TLS 证书检查")
	fmt.Println("  help       显示此帮助")
	fmt.Println()
	fmt.Println("端口扫描选项:")
	fmt.Println("  -target    目标主机 (默认: 127.0.0.1)")
	fmt.Println("  -ports     端口范围，如 1-1000 或 22,80,443 (默认: 1-1024)")
	fmt.Println("  -threads   并发线程数 (默认: 50)")
	fmt.Println("  -timeout   超时时间毫秒 (默认: 1000)")
	fmt.Println()
	fmt.Println("HTTP 检测选项:")
	fmt.Println("  -url       目标 URL (默认: https://example.com)")
	fmt.Println()
	fmt.Println("哈希校验选项:")
	fmt.Println("  -file      目标文件路径")
	fmt.Println()
	fmt.Println("证书检查选项:")
	fmt.Println("  -host      目标主机 (默认: example.com)")
	fmt.Println("  -port      端口 (默认: 443)")
	fmt.Println()
	fmt.Println("注意事项:")
	fmt.Println("  - 所有案例仅供学习和研究使用")
	fmt.Println("  - 端口扫描仅限在授权网络中使用")
	fmt.Println("  - 生产环境请使用专业安全工具")
	fmt.Println()
}

// ============================================================
// 案例 1：并发端口扫描器
// ============================================================

// ScanResult 扫描结果
type ScanResult struct {
	Port    int
	State   string // open / closed / filtered
	Service string
	Reason  string
}

// PortScanner 端口扫描器
type PortScanner struct {
	Target  string
	Ports   []int
	Timeout time.Duration
	Threads int
	Results []ScanResult
	mu      sync.Mutex
}

// NewPortScanner 创建扫描器
func NewPortScanner(target string, ports []int, timeout time.Duration, threads int) *PortScanner {
	return &PortScanner{
		Target:  target,
		Ports:   ports,
		Timeout: timeout,
		Threads: threads,
		Results: make([]ScanResult, 0),
	}
}

// Scan 执行扫描（Worker Pool 模式）
func (s *PortScanner) Scan() {
	jobs := make(chan int, s.Threads)
	var wg sync.WaitGroup

	// 启动 worker
	for i := 0; i < s.Threads; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for port := range jobs {
				result := s.scanPort(port)
				s.mu.Lock()
				s.Results = append(s.Results, result)
				s.mu.Unlock()
			}
		}()
	}

	// 发送任务
	for _, port := range s.Ports {
		jobs <- port
	}
	close(jobs)

	wg.Wait()

	// 按端口排序
	sort.Slice(s.Results, func(i, j int) bool {
		return s.Results[i].Port < s.Results[j].Port
	})
}

// scanPort 扫描单个端口
func (s *PortScanner) scanPort(port int) ScanResult {
	address := fmt.Sprintf("%s:%d", s.Target, port)
	conn, err := net.DialTimeout("tcp", address, s.Timeout)

	result := ScanResult{
		Port:    port,
		Service: getServiceName(port),
	}

	if err != nil {
		result.State = "closed/filtered"
		result.Reason = err.Error()
	} else {
		result.State = "open"
		result.Reason = "TCP 连接成功"
		conn.Close()
	}

	return result
}

// getServiceName 常见端口服务名
func getServiceName(port int) string {
	services := map[int]string{
		21:   "FTP",
		22:   "SSH",
		23:   "Telnet",
		25:   "SMTP",
		53:   "DNS",
		80:   "HTTP",
		110:  "POP3",
		143:  "IMAP",
		443:  "HTTPS",
		445:  "SMB",
		3306: "MySQL",
		3389: "RDP",
		5432: "PostgreSQL",
		6379: "Redis",
		8080: "HTTP-Proxy",
		8443: "HTTPS-Alt",
	}
	if svc, ok := services[port]; ok {
		return svc
	}
	return "Unknown"
}

// parsePorts 解析端口字符串（支持 "1-1000" 或 "22,80,443" 格式）
func parsePorts(portStr string) ([]int, error) {
	var ports []int

	// 逗号分隔
	if strings.Contains(portStr, ",") {
		parts := strings.Split(portStr, ",")
		for _, p := range parts {
			p = strings.TrimSpace(p)
			var port int
			_, err := fmt.Sscanf(p, "%d", &port)
			if err != nil {
				return nil, fmt.Errorf("无效端口: %s", p)
			}
			ports = append(ports, port)
		}
		return ports, nil
	}

	// 范围格式
	if strings.Contains(portStr, "-") {
		var start, end int
		_, err := fmt.Sscanf(portStr, "%d-%d", &start, &end)
		if err != nil {
			return nil, fmt.Errorf("无效端口范围: %s", portStr)
		}
		if start > end || start < 1 || end > 65535 {
			return nil, fmt.Errorf("端口范围无效: %d-%d", start, end)
		}
		for i := start; i <= end; i++ {
			ports = append(ports, i)
		}
		return ports, nil
	}

	// 单个端口
	var port int
	_, err := fmt.Sscanf(portStr, "%d", &port)
	if err != nil {
		return nil, fmt.Errorf("无效端口: %s", portStr)
	}
	return []int{port}, nil
}

func runPortScanner(target, portStr string, threads int, timeoutMs int) {
	section("案例 1：并发端口扫描器")

	ports, err := parsePorts(portStr)
	if err != nil {
		errorMsg("端口解析失败: " + err.Error())
		return
	}

	timeout := time.Duration(timeoutMs) * time.Millisecond

	info(fmt.Sprintf("目标: %s", target))
	info(fmt.Sprintf("端口数: %d (%s)", len(ports), portStr))
	info(fmt.Sprintf("并发数: %d", threads))
	info(fmt.Sprintf("超时: %dms", timeoutMs))
	fmt.Println()

	scanner := NewPortScanner(target, ports, timeout, threads)

	info("开始扫描...")
	startTime := time.Now()
	scanner.Scan()
	elapsed := time.Since(startTime)

	// 统计结果
	openCount := 0
	closedCount := 0
	for _, r := range scanner.Results {
		if r.State == "open" {
			openCount++
		} else {
			closedCount++
		}
	}

	fmt.Println()
	success(fmt.Sprintf("扫描完成！耗时: %.2f 秒", elapsed.Seconds()))
	info(fmt.Sprintf("开放端口: %d  关闭/过滤: %d  总计: %d", openCount, closedCount, len(ports)))
	fmt.Println()

	// 显示开放端口
	if openCount > 0 {
		fmt.Println("  开放端口列表:")
		fmt.Printf("  %-8s %-10s %-15s %s\n", "端口", "状态", "服务", "说明")
		fmt.Println("  " + strings.Repeat("-", 60))
		for _, r := range scanner.Results {
			if r.State == "open" {
				fmt.Printf("  %-8d %-10s %-15s %s\n", r.Port, r.State, r.Service, r.Reason)
			}
		}
	} else {
		warn("未发现开放端口（可能目标不可达或全部端口关闭）")
	}

	fmt.Println()
	warn("⚠️  端口扫描仅限在授权的网络环境中使用！")
	warn("   未经授权的扫描可能违反法律，请确保您有适当的权限。")
	fmt.Println()
}

// ============================================================
// 案例 2：HTTP 安全头检测
// ============================================================

// SecurityHeaderCheck 安全头检查结果
type SecurityHeaderCheck struct {
	Header      string
	Description string
	Present     bool
	Value       string
	Status      string // good / warn / missing / info
}

// HTTP 安全头配置建议
var securityHeaders = []SecurityHeaderCheck{
	{
		Header:      "Strict-Transport-Security",
		Description: "强制 HTTPS（HSTS）",
		Status:      "missing",
	},
	{
		Header:      "X-Content-Type-Options",
		Description: "禁止 MIME 类型嗅探",
		Status:      "missing",
	},
	{
		Header:      "X-Frame-Options",
		Description: "防止点击劫持",
		Status:      "missing",
	},
	{
		Header:      "Content-Security-Policy",
		Description: "内容安全策略（防 XSS）",
		Status:      "missing",
	},
	{
		Header:      "X-XSS-Protection",
		Description: "XSS 防护（旧浏览器，已废弃）",
		Status:      "info",
	},
	{
		Header:      "Referrer-Policy",
		Description: "Referrer 策略（隐私保护）",
		Status:      "missing",
	},
	{
		Header:      "Permissions-Policy",
		Description: "权限策略（限制浏览器功能）",
		Status:      "missing",
	},
	{
		Header:      "Server",
		Description: "服务器信息（建议隐藏）",
		Status:      "info",
	},
	{
		Header:      "X-Powered-By",
		Description: "技术栈信息（建议隐藏）",
		Status:      "info",
	},
}

func checkSecurityHeaders(rawURL string) {
	section("案例 2：HTTP 安全头检测")

	// 确保 URL 有协议
	if !strings.HasPrefix(rawURL, "http://") && !strings.HasPrefix(rawURL, "https://") {
		rawURL = "https://" + rawURL
	}

	info("目标 URL: " + rawURL)
	fmt.Println()

	// 创建 HTTP 客户端
	client := &http.Client{
		Timeout: 10 * time.Second,
		Transport: &http.Transport{
			TLSClientConfig: &tls.Config{
				InsecureSkipVerify: false, // 必须验证证书
			},
			MaxIdleConns:    10,
			IdleConnTimeout: 30 * time.Second,
		},
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			if len(via) >= 5 {
				return http.ErrUseLastResponse
			}
			return nil
		},
	}

	resp, err := client.Get(rawURL)
	if err != nil {
		errorMsg("请求失败: " + err.Error())
		return
	}
	defer resp.Body.Close()

	info(fmt.Sprintf("响应状态: %s", resp.Status))
	info(fmt.Sprintf("响应头数量: %d", len(resp.Header)))
	fmt.Println()

	// 检查安全头
	results := make([]SecurityHeaderCheck, len(securityHeaders))
	copy(results, securityHeaders)

	for i := range results {
		value := resp.Header.Get(results[i].Header)
		results[i].Value = value
		results[i].Present = value != ""

		if !results[i].Present {
			if results[i].Status == "info" {
				results[i].Status = "info" // 信息项缺失不报警
			} else {
				results[i].Status = "missing"
			}
		} else {
			// 评估配置是否合理
			switch results[i].Header {
			case "Strict-Transport-Security":
				if strings.Contains(value, "max-age=") {
					results[i].Status = "good"
				} else {
					results[i].Status = "warn"
				}
			case "X-Content-Type-Options":
				if strings.EqualFold(value, "nosniff") {
					results[i].Status = "good"
				} else {
					results[i].Status = "warn"
				}
			case "X-Frame-Options":
				if strings.Contains(strings.ToUpper(value), "DENY") ||
					strings.Contains(strings.ToUpper(value), "SAMEORIGIN") {
					results[i].Status = "good"
				} else {
					results[i].Status = "warn"
				}
			case "Content-Security-Policy":
				if strings.Contains(value, "default-src") ||
					strings.Contains(value, "script-src") {
					results[i].Status = "good"
				} else {
					results[i].Status = "warn"
				}
			case "Server", "X-Powered-By":
				results[i].Status = "warn" // 泄露信息
			default:
				results[i].Status = "good"
			}
		}
	}

	// 输出结果
	fmt.Println("  安全头检测结果:")
	fmt.Println("  " + strings.Repeat("-", 80))
	fmt.Printf("  %-35s %-8s %-8s %s\n", "安全头", "状态", "评分", "说明")
	fmt.Println("  " + strings.Repeat("-", 80))

	goodCount := 0
	warnCount := 0
	missingCount := 0

	for _, r := range results {
		var statusIcon, statusColor string
		switch r.Status {
		case "good":
			statusIcon = "✅"
			statusColor = colorGreen
			goodCount++
		case "warn":
			statusIcon = "⚠️ "
			statusColor = colorYellow
			warnCount++
		case "missing":
			statusIcon = "❌"
			statusColor = colorRed
			missingCount++
		default:
			statusIcon = "ℹ️ "
			statusColor = colorBlue
		}

		shortDesc := r.Description
		if len(shortDesc) > 18 {
			shortDesc = shortDesc[:18] + "..."
		}

		fmt.Printf("  %s%-35s%s %-8s %-8s %s\n",
			statusColor, r.Header, colorReset,
			statusIcon, r.Status,
			shortDesc)

		if r.Present && len(r.Value) > 50 {
			fmt.Printf("    值: %s...\n", r.Value[:50])
		} else if r.Present {
			fmt.Printf("    值: %s\n", r.Value)
		}
	}

	fmt.Println()
	fmt.Println("  统计:")
	fmt.Printf("    ✅ 配置良好: %d\n", goodCount)
	fmt.Printf("    ⚠️  需要改进: %d\n", warnCount)
	fmt.Printf("    ❌ 缺失: %d\n", missingCount)
	fmt.Println()

	// 建议
	info("改进建议:")
	for _, r := range results {
		if r.Status == "missing" {
			fmt.Printf("    - 添加 %s 头（%s）\n", r.Header, r.Description)
		}
	}
	fmt.Println()
}

// ============================================================
// 案例 3：文件哈希校验工具
// ============================================================

// FileHashResult 文件哈希结果
type FileHashResult struct {
	FilePath string
	Size     int64
	MD5      string
	SHA1     string
	SHA256   string
}

func calculateFileHash(filePath string) (*FileHashResult, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return nil, fmt.Errorf("打开文件失败: %w", err)
	}
	defer file.Close()

	fileInfo, err := file.Stat()
	if err != nil {
		return nil, fmt.Errorf("获取文件信息失败: %w", err)
	}

	if fileInfo.IsDir() {
		return nil, fmt.Errorf("目标是目录，不是文件")
	}

	// 同时计算多种哈希
	md5Hash := md5.New()
	sha1Hash := sha1.New()
	sha256Hash := sha256.New()

	// 使用 MultiWriter 一次写入多个哈希器
	writer := io.MultiWriter(md5Hash, sha1Hash, sha256Hash)

	buf := make([]byte, 64*1024) // 64KB 缓冲区
	if _, err := io.CopyBuffer(writer, file, buf); err != nil {
		return nil, fmt.Errorf("计算哈希失败: %w", err)
	}

	return &FileHashResult{
		FilePath: filePath,
		Size:     fileInfo.Size(),
		MD5:      hex.EncodeToString(md5Hash.Sum(nil)),
		SHA1:     hex.EncodeToString(sha1Hash.Sum(nil)),
		SHA256:   hex.EncodeToString(sha256Hash.Sum(nil)),
	}, nil
}

func runFileHashChecker(filePath string) {
	section("案例 3：文件哈希校验工具")

	if filePath == "" {
		// 默认检查自身程序
		info("未指定文件，计算当前源文件哈希...")
		filePath = os.Args[0]
	}

	info("目标文件: " + filePath)
	fmt.Println()

	result, err := calculateFileHash(filePath)
	if err != nil {
		errorMsg(err.Error())
		return
	}

	// 格式化文件大小
	var sizeStr string
	if result.Size < 1024 {
		sizeStr = fmt.Sprintf("%d B", result.Size)
	} else if result.Size < 1024*1024 {
		sizeStr = fmt.Sprintf("%.2f KB", float64(result.Size)/1024)
	} else if result.Size < 1024*1024*1024 {
		sizeStr = fmt.Sprintf("%.2f MB", float64(result.Size)/(1024*1024))
	} else {
		sizeStr = fmt.Sprintf("%.2f GB", float64(result.Size)/(1024*1024*1024))
	}

	fmt.Println("  文件信息:")
	fmt.Printf("    路径: %s\n", result.FilePath)
	fmt.Printf("    大小: %s (%d bytes)\n", sizeStr, result.Size)
	fmt.Println()

	fmt.Println("  哈希值:")
	fmt.Printf("    MD5:    %s\n", result.MD5)
	fmt.Printf("    SHA1:   %s\n", result.SHA1)
	fmt.Printf("    SHA256: %s\n", result.SHA256)
	fmt.Println()

	// 安全性提示
	warn("安全提示:")
	fmt.Println("    - MD5 和 SHA1 已被破解，不推荐用于安全场景")
	fmt.Println("    - SHA-256 目前仍然安全，推荐用于完整性校验")
	fmt.Println("    - 密码存储请使用 bcrypt/Argon2 等慢哈希算法")
	fmt.Println("    - 验证文件完整性时，确保哈希值来源可信")
	fmt.Println()
}

// ============================================================
// 案例 4：TLS 证书检查
// ============================================================

// CertInfo 证书信息
type CertInfo struct {
	Host           string
	Port           int
	Connected      bool
	Version        string
	CipherSuite    string
	ServerCert     *x509.Certificate
	IssuerCert     *x509.Certificate
	Err            error
}

func checkTLSCertificate(host string, port int) *CertInfo {
	result := &CertInfo{
		Host: host,
		Port: port,
	}

	address := fmt.Sprintf("%s:%d", host, port)

	conn, err := tls.Dial("tcp", address, &tls.Config{
		InsecureSkipVerify: false,
		ServerName:         host,
		MinVersion:         tls.VersionTLS12,
	})
	if err != nil {
		result.Err = err
		return result
	}
	defer conn.Close()

	result.Connected = true
	state := conn.ConnectionState()

	// TLS 版本
	switch state.Version {
	case tls.VersionTLS13:
		result.Version = "TLS 1.3"
	case tls.VersionTLS12:
		result.Version = "TLS 1.2"
	case tls.VersionTLS11:
		result.Version = "TLS 1.1 (不安全)"
	case tls.VersionTLS10:
		result.Version = "TLS 1.0 (不安全)"
	default:
		result.Version = fmt.Sprintf("未知 (0x%04x)", state.Version)
	}

	result.CipherSuite = tls.CipherSuiteName(state.CipherSuite)

	// 证书链
	certs := state.PeerCertificates
	if len(certs) > 0 {
		result.ServerCert = certs[0]
	}
	if len(certs) > 1 {
		result.IssuerCert = certs[1]
	}

	return result
}

func runCertificateChecker(host string, port int) {
	section("案例 4：TLS 证书检查")

	info(fmt.Sprintf("目标: %s:%d", host, port))
	fmt.Println()

	result := checkTLSCertificate(host, port)

	if result.Err != nil {
		errorMsg("连接失败: " + result.Err.Error())
		fmt.Println()
		return
	}

	success("连接成功")
	fmt.Println()

	// 协议信息
	fmt.Println("  连接信息:")
	fmt.Printf("    TLS 版本: %s\n", result.Version)
	fmt.Printf("    加密套件: %s\n", result.CipherSuite)
	fmt.Println()

	// 服务器证书
	if result.ServerCert != nil {
		cert := result.ServerCert

		fmt.Println("  服务器证书:")
		fmt.Printf("    主题 (CN): %s\n", cert.Subject.CommonName)
		fmt.Printf("    主题备用名 (SAN): %v\n", cert.DNSNames)
		fmt.Printf("    颁发者: %s\n", cert.Issuer.CommonName)
		fmt.Printf("    颁发机构: %s\n", cert.Issuer.Organization)
		fmt.Printf("    序列号: %X\n", cert.SerialNumber)
		fmt.Printf("    生效时间: %s\n", cert.NotBefore.Format("2006-01-02 15:04:05"))
		fmt.Printf("    过期时间: %s\n", cert.NotAfter.Format("2006-01-02 15:04:05"))

		// 有效期检查
		now := time.Now()
		daysLeft := int(cert.NotAfter.Sub(now).Hours() / 24)

		fmt.Println()
		fmt.Println("  有效期检查:")
		if now.Before(cert.NotBefore) {
			fmt.Printf("    ⚠️  证书尚未生效\n")
		} else if now.After(cert.NotAfter) {
			fmt.Printf("    ❌ 证书已过期 (过期 %d 天)\n", -daysLeft)
		} else if daysLeft <= 7 {
			fmt.Printf("    ⚠️  即将过期 (剩余 %d 天)\n", daysLeft)
		} else if daysLeft <= 30 {
			fmt.Printf("    ⚠️  剩余 %d 天，建议尽快续签\n", daysLeft)
		} else {
			fmt.Printf("    ✅ 证书有效 (剩余 %d 天)\n", daysLeft)
		}

		// 密钥信息
		fmt.Println()
		fmt.Println("  密钥信息:")
		fmt.Printf("    公钥算法: %s\n", cert.PublicKeyAlgorithm.String())
		fmt.Printf("    签名算法: %s\n", cert.SignatureAlgorithm.String())

		// 用途
		fmt.Println()
		fmt.Println("  证书用途:")
		for _, usage := range cert.ExtKeyUsage {
			switch usage {
			case x509.ExtKeyUsageServerAuth:
				fmt.Println("    - 服务器身份验证 ✅")
			case x509.ExtKeyUsageClientAuth:
				fmt.Println("    - 客户端身份验证")
			case x509.ExtKeyUsageCodeSigning:
				fmt.Println("    - 代码签名")
			}
		}
	}

	// 颁发者证书
	if result.IssuerCert != nil {
		fmt.Println()
		fmt.Println("  颁发者证书:")
		fmt.Printf("    主题: %s\n", result.IssuerCert.Subject.CommonName)
		fmt.Printf("    组织: %v\n", result.IssuerCert.Issuer.Organization)
	}

	fmt.Println()

	// TLS 版本评估
	fmt.Println("  安全评估:")
	switch result.Version {
	case "TLS 1.3":
		fmt.Println("    ✅ TLS 1.3：最新最安全的版本")
	case "TLS 1.2":
		fmt.Println("    ✅ TLS 1.2：当前主流安全版本")
	default:
		fmt.Println("    ❌ 旧版 TLS：存在安全风险，建议升级")
	}
	fmt.Println()

	// 建议
	warn("安全建议:")
	fmt.Println("    - 确保证书有效期充足，提前续签")
	fmt.Println("    - 使用 TLS 1.2 及以上版本")
	fmt.Println("    - 禁用 TLS 1.0 和 1.1")
	fmt.Println("    - 选择强加密套件（AES-GCM、ChaCha20-Poly1305）")
	fmt.Println("    - 配置 HSTS 强制 HTTPS")
	fmt.Println("    - 启用 OCSP Stapling 加快验证速度")
	fmt.Println()
}

// ============================================================
// 主程序入口
// ============================================================

func main() {
	fmt.Println()
	fmt.Println("============================================================")
	fmt.Println("  Go 安全案例集")
	fmt.Println("  Security Cases for Go")
	fmt.Println("============================================================")
	fmt.Println()

	// 解析参数
	if len(os.Args) < 2 {
		showHelp()
		return
	}

	mode := os.Args[1]

	// 定义 flag
	flagSet := flag.NewFlagSet("security_cases", flag.ExitOnError)

	// 端口扫描选项
	targetPtr := flagSet.String("target", "127.0.0.1", "目标主机")
	portsPtr := flagSet.String("ports", "1-1024", "端口范围")
	threadsPtr := flagSet.Int("threads", 50, "并发线程数")
	timeoutPtr := flagSet.Int("timeout", 1000, "超时时间(毫秒)")

	// HTTP 检测选项
	urlPtr := flagSet.String("url", "https://example.com", "目标 URL")

	// 哈希校验选项
	filePtr := flagSet.String("file", "", "目标文件路径")

	// 证书检查选项
	hostPtr := flagSet.String("host", "example.com", "目标主机")
	portPtr := flagSet.Int("port", 443, "端口号")

	// 解析 flag（跳过第一个参数即模式）
	flagSet.Parse(os.Args[2:])

	switch mode {
	case "help":
		showHelp()

	case "scan":
		runPortScanner(*targetPtr, *portsPtr, *threadsPtr, *timeoutPtr)

	case "http":
		checkSecurityHeaders(*urlPtr)

	case "hash":
		runFileHashChecker(*filePtr)

	case "cert":
		runCertificateChecker(*hostPtr, *portPtr)

	case "all":
		info("运行所有安全案例...")
		fmt.Println()

		runPortScanner(*targetPtr, *portsPtr, *threadsPtr, *timeoutPtr)
		checkSecurityHeaders(*urlPtr)
		runFileHashChecker(*filePtr)
		runCertificateChecker(*hostPtr, *portPtr)

		section("全部案例执行完毕")
		success("所有安全案例已运行完成")
		fmt.Println()

	default:
		errorMsg("未知模式: " + mode)
		fmt.Println()
		showHelp()
		os.Exit(1)
	}

	fmt.Println()
	fmt.Println("============================================================")
	fmt.Println("  免责声明")
	fmt.Println("============================================================")
	fmt.Println()
	fmt.Println("  本脚本仅供学习、研究和授权环境下的安全测试使用。")
	fmt.Println("  任何未经授权的测试或攻击行为均属违法。")
	fmt.Println("  使用者应遵守所在地区法律法规，对自己的行为负责。")
	fmt.Println()
}
