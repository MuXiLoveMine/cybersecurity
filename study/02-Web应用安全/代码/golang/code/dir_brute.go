/*
 * ============================================================
 * 文件名：dir_brute.go
 * 功能描述：Web 目录爆破工具
 * 作者：网络安全学习笔记
 * 日期：2026-09-10
 * ============================================================
 *
 * 【使用说明】
 * 1. 编译运行：go run dir_brute.go
 * 2. 命令行参数：
 *    -url    目标 URL（默认：http://127.0.0.1）
 *    -wordlist 字典文件路径（默认使用内置字典）
 *    -t      并发协程数（默认：50）
 *    -status 显示的状态码，逗号分隔（默认：200,301,302,403）
 *    -timeout 请求超时时间，单位秒（默认：5）
 *
 * 【示例】
 *   go run dir_brute.go -url http://example.com -t 100
 *   go run dir_brute.go -url http://example.com -wordlist ./dict.txt
 *
 * 【免责声明】
 *   本工具仅供网络安全学习和授权测试使用。
 *   禁止对未授权的网站进行目录爆破，违者后果自负。
 *   使用本工具请遵守当地法律法规。
 * ============================================================
 */

package main

import (
	"flag"      // 命令行参数解析
	"fmt"       // 格式化输出
	"io/ioutil" // 文件读取
	"net/http"  // HTTP 客户端
	"strings"   // 字符串处理
	"sync"      // 并发同步
	"time"      // 时间相关
)

// BruteResult 定义爆破结果结构体
type BruteResult struct {
	Path       string // 爆破的路径
	StatusCode int    // HTTP 响应状态码
	Size       int    // 响应体大小（字节）
	Found      bool   // 是否命中（根据状态码判断）
}

// defaultWordlist 默认内置字典
// 当用户没有指定字典文件时使用
var defaultWordlist = []string{
	// 常见后台路径
	"admin", "admin.php", "admin.html", "admin/login", "admin/index",
	"admin/admin", "login", "login.php", "login.html", "signin",
	"manage", "manager", "cms", "system", "member", "user",
	// 常见文件
	"index.php", "index.html", "index.asp", "index.jsp",
	"robots.txt", "sitemap.xml", "sitemap.html",
	"readme.md", "README.md", "readme.txt", "CHANGELOG.txt",
	"config.php", "config.inc.php", "database.yml", "web.config",
	".htaccess", ".htpasswd", "crossdomain.xml",
	// 备份文件
	"backup", "backup.sql", "backup.zip", "backup.tar", "backup.tar.gz",
	"www.zip", "wwwroot.zip", "web.zip", "site.zip",
	// 编辑器文件
	".git/", ".git/config", ".git/HEAD", ".svn/", ".svn/entries",
	".DS_Store", "Thumbs.db",
	// 常见目录
	"upload", "uploads", "files", "data", "static", "assets",
	"images", "img", "css", "js", "includes", "inc", "lib",
	"tmp", "temp", "cache", "logs", "log",
	// API 路径
	"api", "api/v1", "api/v2", "graphql", "swagger", "docs",
	// 常见漏洞页面
	"phpinfo.php", "test.php", "info.php", "status", "server-status",
	"actuator", "actuator/env", "actuator/health",
}

// checkStatus 检查状态码是否在关注列表中
// 参数：
//   statusCode - HTTP 响应状态码
//   targetCodes - 关注的状态码列表
// 返回：是否命中
func checkStatus(statusCode int, targetCodes []int) bool {
	for _, code := range targetCodes {
		if statusCode == code {
			return true
		}
	}
	return false
}

// brutePath 对单个路径进行爆破
// 参数：
//   baseURL - 基础 URL
//   path - 待爆破的路径
//   client - HTTP 客户端（复用连接池）
//   targetCodes - 关注的状态码列表
// 返回：BruteResult 结构体指针
func brutePath(baseURL string, path string, client *http.Client, targetCodes []int) *BruteResult {
	// 构造完整 URL
	// 确保 baseURL 结尾没有斜杠，path 开头没有斜杠
	baseURL = strings.TrimRight(baseURL, "/")
	path = strings.TrimLeft(path, "/")
	fullURL := fmt.Sprintf("%s/%s", baseURL, path)

	// 创建 GET 请求
	req, err := http.NewRequest("GET", fullURL, nil)
	if err != nil {
		return &BruteResult{
			Path:       path,
			StatusCode: 0,
			Size:       0,
			Found:      false,
		}
	}

	// 设置请求头，模拟浏览器访问
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
	req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
	req.Header.Set("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8")
	req.Header.Set("Connection", "close")

	// 发送请求
	resp, err := client.Do(req)
	if err != nil {
		// 请求失败（如连接超时、网络错误等）
		return &BruteResult{
			Path:       path,
			StatusCode: 0,
			Size:       0,
			Found:      false,
		}
	}
	defer resp.Body.Close() // 确保响应体被关闭

	// 读取响应体大小
	body, _ := ioutil.ReadAll(resp.Body)
	size := len(body)

	// 判断是否命中
	found := checkStatus(resp.StatusCode, targetCodes)

	return &BruteResult{
		Path:       path,
		StatusCode: resp.StatusCode,
		Size:       size,
		Found:      found,
	}
}

// worker 工作协程函数
// 参数：
//   baseURL - 基础 URL
//   pathChan - 路径通道
//   resultChan - 结果通道
//   client - HTTP 客户端
//   targetCodes - 关注的状态码
//   wg - WaitGroup
func worker(baseURL string, pathChan <-chan string, resultChan chan<- *BruteResult, client *http.Client, targetCodes []int, wg *sync.WaitGroup) {
	defer wg.Done() // 函数结束时减少计数

	for path := range pathChan {
		result := brutePath(baseURL, path, client, targetCodes)
		resultChan <- result
	}
}

// loadWordlist 加载字典文件
// 参数：
//   filePath - 字典文件路径
// 返回：路径列表和错误信息
func loadWordlist(filePath string) ([]string, error) {
	// 读取文件内容
	content, err := ioutil.ReadFile(filePath)
	if err != nil {
		return nil, err
	}

	// 按行分割，去除空行和注释行
	var wordlist []string
	lines := strings.Split(string(content), "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		// 跳过空行和注释行（以 # 开头）
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		wordlist = append(wordlist, line)
	}

	return wordlist, nil
}

func main() {
	// ===================== 命令行参数解析 =====================
	url := flag.String("url", "http://127.0.0.1", "目标 URL")
	wordlistFile := flag.String("wordlist", "", "字典文件路径（留空使用内置字典）")
	threads := flag.Int("t", 50, "并发协程数量")
	statusStr := flag.String("status", "200,301,302,403", "显示的状态码，逗号分隔")
	timeoutSec := flag.Int("timeout", 5, "请求超时时间（秒）")

	flag.Parse()

	// 解析状态码
	var targetCodes []int
	statusParts := strings.Split(*statusStr, ",")
	for _, s := range statusParts {
		s = strings.TrimSpace(s)
		var code int
		fmt.Sscanf(s, "%d", &code)
		if code > 0 {
			targetCodes = append(targetCodes, code)
		}
	}

	// ===================== 加载字典 =====================
	var wordlist []string
	var err error

	if *wordlistFile != "" {
		// 用户指定了字典文件
		wordlist, err = loadWordlist(*wordlistFile)
		if err != nil {
			fmt.Printf("[错误] 加载字典文件失败: %v\n", err)
			return
		}
		fmt.Printf("[*] 已加载字典文件: %s (共 %d 条)\n", *wordlistFile, len(wordlist))
	} else {
		// 使用内置字典
		wordlist = defaultWordlist
		fmt.Printf("[*] 使用内置字典 (共 %d 条)\n", len(wordlist))
	}

	if len(wordlist) == 0 {
		fmt.Println("[错误] 字典为空")
		return
	}

	// ===================== 打印扫描信息 =====================
	fmt.Println("========================================")
	fmt.Println("       Web 目录爆破工具（Go 版）")
	fmt.Println("========================================")
	fmt.Printf("目标 URL: %s\n", *url)
	fmt.Printf("字典数量: %d\n", len(wordlist))
	fmt.Printf("并发数量: %d\n", *threads)
	fmt.Printf("关注状态码: %v\n", targetCodes)
	fmt.Printf("超时时间: %d 秒\n", *timeoutSec)
	fmt.Println("========================================")
	fmt.Println("[*] 正在爆破，请稍候...")
	fmt.Println("----------------------------------------")

	// ===================== 初始化 HTTP 客户端 =====================
	// 创建自定义 HTTP 客户端，设置超时
	client := &http.Client{
		Timeout: time.Duration(*timeoutSec) * time.Second,
		// 不自动跟随重定向，方便观察 301/302
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			return http.ErrUseLastResponse
		},
	}

	// ===================== 初始化并发结构 =====================
	pathChan := make(chan string, *threads*2)   // 路径通道
	resultChan := make(chan *BruteResult, *threads*2) // 结果通道

	var wg sync.WaitGroup

	// ===================== 启动工作协程 =====================
	for i := 0; i < *threads; i++ {
		wg.Add(1)
		go worker(*url, pathChan, resultChan, client, targetCodes, &wg)
	}

	// ===================== 发送路径任务 =====================
	go func() {
		for _, path := range wordlist {
			pathChan <- path
		}
		close(pathChan) // 所有路径发送完毕，关闭通道
	}()

	// ===================== 等待并收集结果 =====================
	// 在单独协程中等待所有 worker 完成，然后关闭结果通道
	go func() {
		wg.Wait()
		close(resultChan)
	}()

	// 实时收集并显示命中结果
	var foundResults []*BruteResult
	var totalRequests int

	for result := range resultChan {
		totalRequests++
		// 实时显示命中的路径
		if result.Found {
			foundResults = append(foundResults, result)
			statusStr := fmt.Sprintf("[%d]", result.StatusCode)
			fmt.Printf("  %-8s  %-10d字节  /%s\n", statusStr, result.Size, result.Path)
		}
		// 显示进度（每请求 100 条显示一次）
		if totalRequests%100 == 0 {
			fmt.Printf("  ... 进度: %d/%d\n", totalRequests, len(wordlist))
		}
	}

	// ===================== 输出最终结果 =====================
	fmt.Println("----------------------------------------")
	fmt.Println("\n========================================")
	fmt.Println("            爆破结果汇总")
	fmt.Println("========================================")
	fmt.Printf("请求总数: %d\n", totalRequests)
	fmt.Printf("命中数量: %d\n", len(foundResults))

	if len(foundResults) > 0 {
		fmt.Println("\n[命中路径列表]")
		fmt.Printf("%-8s %-12s %s\n", "状态码", "响应大小", "路径")
		fmt.Println("----------------------------------------")
		for _, result := range foundResults {
			fmt.Printf("%-8d %-12d /%s\n", result.StatusCode, result.Size, result.Path)
		}
	} else {
		fmt.Println("\n[!] 未发现可访问的路径")
	}

	fmt.Println("\n========================================")
	fmt.Println("            爆破完成")
	fmt.Println("========================================")
}
