/*
 * ============================================================
 * 文件名：port_scanner.go
 * 功能描述：TCP 端口扫描器（并发版）
 * 作者：网络安全学习笔记
 * 日期：2026-09-10
 * ============================================================
 *
 * 【使用说明】
 * 1. 编译运行：go run port_scanner.go
 * 2. 或先编译：go build port_scanner.go，再运行生成的可执行文件
 * 3. 命令行参数：
 *    -host   目标主机地址（默认：127.0.0.1）
 *    -start  起始端口（默认：1）
 *    -end    结束端口（默认：1024）
 *    -t      并发协程数（默认：100）
 *    -timeout 连接超时时间，单位毫秒（默认：500）
 *
 * 【示例】
 *   go run port_scanner.go -host 192.168.1.1 -start 1 -end 1000 -t 200
 *
 * 【免责声明】
 *   本工具仅供网络安全学习和授权测试使用。
 *   禁止对未授权的目标进行端口扫描，违者后果自负。
 *   使用本工具请遵守当地法律法规。
 * ============================================================
 */

package main

import (
	"flag"     // 命令行参数解析
	"fmt"      // 格式化输出
	"net"      // 网络编程
	"sort"     // 排序
	"sync"     // 并发同步
	"time"     // 时间相关
)

// ScanResult 定义扫描结果结构体
type ScanResult struct {
	Port    int    // 端口号
	State   string // 状态：open / closed / filtered
	Service string // 端口对应的常见服务名称
}

// commonPorts 常见端口对应的服务名称映射表
// 用于在扫描结果中显示服务名，方便快速识别
var commonPorts = map[int]string{
	21:   "FTP",          // 文件传输协议
	22:   "SSH",          // 安全外壳协议
	23:   "Telnet",       // 远程登录协议
	25:   "SMTP",         // 简单邮件传输协议
	53:   "DNS",          // 域名系统
	80:   "HTTP",         // 超文本传输协议
	110:  "POP3",         // 邮局协议第3版
	111:  "RPC",          // 远程过程调用
	135:  "MSRPC",        // Microsoft RPC
	139:  "NetBIOS",      // 网络基本输入输出系统
	143:  "IMAP",         // 互联网消息访问协议
	443:  "HTTPS",        // 安全超文本传输协议
	445:  "SMB",          // 服务器消息块
	465:  "SMTPS",        // SMTP over SSL
	993:  "IMAPS",        // IMAP over SSL
	995:  "POP3S",        // POP3 over SSL
	1080: "SOCKS",        // SOCKS代理
	1433: "MSSQL",        // Microsoft SQL Server
	1521: "Oracle",       // Oracle数据库
	3306: "MySQL",        // MySQL数据库
	3389: "RDP",          // 远程桌面协议
	5432: "PostgreSQL",   // PostgreSQL数据库
	5900: "VNC",          // 虚拟网络计算
	6379: "Redis",        // Redis数据库
	8080: "HTTP-Proxy",   // HTTP代理/备用HTTP
	8443: "HTTPS-Alt",    // 备用HTTPS
	9090: "WebAdmin",     // Web管理面板
	27017: "MongoDB",     // MongoDB数据库
}

// scanPort 扫描单个端口
// 参数：
//   host - 目标主机地址
//   port - 端口号
//   timeout - 连接超时时间
// 返回：ScanResult 结构体指针
func scanPort(host string, port int, timeout time.Duration) *ScanResult {
	// 构建地址字符串，格式为 "主机:端口"
	address := fmt.Sprintf("%s:%d", host, port)

	// 建立 TCP 连接
	// net.DialTimeout 会在指定超时时间内尝试连接
	conn, err := net.DialTimeout("tcp", address, timeout)

	// 获取服务名称，未知端口显示 "unknown"
	service := "unknown"
	if svc, ok := commonPorts[port]; ok {
		service = svc
	}

	// 根据连接结果判断端口状态
	if err != nil {
		// 连接失败，可能是端口关闭或被防火墙过滤
		return &ScanResult{
			Port:    port,
			State:   "closed/filtered",
			Service: service,
		}
	}
	// 连接成功，端口开放，关闭连接后返回结果
	conn.Close()
	return &ScanResult{
		Port:    port,
		State:   "open",
		Service: service,
	}
}

// worker 工作协程函数，从端口通道中取出端口进行扫描
// 参数：
//   host - 目标主机
//   portChan - 端口通道，用于接收待扫描的端口
//   resultChan - 结果通道，用于发送扫描结果
//   timeout - 连接超时
//   wg - WaitGroup，用于协程同步
func worker(host string, portChan <-chan int, resultChan chan<- *ScanResult, timeout time.Duration, wg *sync.WaitGroup) {
	// 函数结束时通知 WaitGroup 当前协程已完成
	defer wg.Done()

	// 不断从通道中读取端口，直到通道关闭
	for port := range portChan {
		result := scanPort(host, port, timeout)
		resultChan <- result
	}
}

func main() {
	// ===================== 命令行参数解析 =====================
	// 目标主机参数
	host := flag.String("host", "127.0.0.1", "目标主机地址")
	// 起始端口
	startPort := flag.Int("start", 1, "起始端口号")
	// 结束端口
	endPort := flag.Int("end", 1024, "结束端口号")
	// 并发协程数
	threads := flag.Int("t", 100, "并发协程数量")
	// 超时时间（毫秒）
	timeoutMs := flag.Int("timeout", 500, "连接超时时间（毫秒）")

	// 解析命令行参数
	flag.Parse()

	// 参数合法性校验
	if *startPort < 1 || *startPort > 65535 {
		fmt.Println("[错误] 起始端口必须在 1-65535 之间")
		return
	}
	if *endPort < 1 || *endPort > 65535 {
		fmt.Println("[错误] 结束端口必须在 1-65535 之间")
		return
	}
	if *startPort > *endPort {
		fmt.Println("[错误] 起始端口不能大于结束端口")
		return
	}
	if *threads < 1 {
		fmt.Println("[错误] 并发协程数不能小于 1")
		return
	}

	// 将超时时间转换为 Duration 类型
	timeout := time.Duration(*timeoutMs) * time.Millisecond

	// ===================== 打印扫描信息 =====================
	fmt.Println("========================================")
	fmt.Println("       TCP 端口扫描器（Go 并发版）")
	fmt.Println("========================================")
	fmt.Printf("目标主机: %s\n", *host)
	fmt.Printf("端口范围: %d - %d\n", *startPort, *endPort)
	fmt.Printf("并发数量: %d\n", *threads)
	fmt.Printf("超时时间: %d 毫秒\n", *timeoutMs)
	fmt.Println("========================================")
	fmt.Println("[*] 正在扫描，请稍候...")

	// ===================== 初始化并发结构 =====================
	// 端口通道：生产者-消费者模式，存放待扫描的端口
	// 带缓冲的通道，缓冲大小为端口总数，避免阻塞
	portChan := make(chan int, *endPort-*startPort+1)

	// 结果通道：存放扫描结果
	resultChan := make(chan *ScanResult, *endPort-*startPort+1)

	// WaitGroup 用于等待所有工作协程完成
	var wg sync.WaitGroup

	// ===================== 启动工作协程 =====================
	// 启动指定数量的工作协程
	for i := 0; i < *threads; i++ {
		wg.Add(1) // 增加 WaitGroup 计数
		go worker(*host, portChan, resultChan, timeout, &wg)
	}

	// ===================== 发送端口任务 =====================
	// 将所有待扫描的端口放入端口通道
	for port := *startPort; port <= *endPort; port++ {
		portChan <- port
	}
	// 关闭端口通道，通知工作协程没有更多任务了
	close(portChan)

	// ===================== 等待扫描完成 =====================
	// 启动一个协程来等待所有工作协程完成，然后关闭结果通道
	go func() {
		wg.Wait()         // 阻塞等待所有 worker 完成
		close(resultChan) // 所有结果都已发送，关闭结果通道
	}()

	// ===================== 收集扫描结果 =====================
	var openPorts []int      // 开放端口列表
	var closedPorts []int    // 关闭端口列表
	var results []*ScanResult // 所有结果

	// 从结果通道中读取所有结果
	for result := range resultChan {
		results = append(results, result)
		if result.State == "open" {
			openPorts = append(openPorts, result.Port)
		} else {
			closedPorts = append(closedPorts, result.Port)
		}
	}

	// 对开放端口进行排序，方便查看
	sort.Ints(openPorts)
	sort.Ints(closedPorts)

	// ===================== 输出扫描结果 =====================
	fmt.Println("\n========================================")
	fmt.Println("            扫描结果")
	fmt.Println("========================================")
	fmt.Printf("扫描端口总数: %d\n", *endPort-*startPort+1)
	fmt.Printf("开放端口数量: %d\n", len(openPorts))
	fmt.Printf("关闭/过滤端口数量: %d\n", len(closedPorts))
	fmt.Println("----------------------------------------")

	if len(openPorts) > 0 {
		fmt.Println("\n[开放端口列表]")
		fmt.Printf("%-8s %-16s %s\n", "端口", "状态", "服务")
		fmt.Println("----------------------------------------")
		for _, result := range results {
			if result.State == "open" {
				fmt.Printf("%-8d %-16s %s\n", result.Port, result.State, result.Service)
			}
		}
	} else {
		fmt.Println("\n[!] 未发现开放端口")
	}

	fmt.Println("\n========================================")
	fmt.Println("            扫描完成")
	fmt.Println("========================================")
}
