// basics.go —— Go 语言基础语法示例（安全从业者视角）
//
// 涵盖内容：
//   1. 变量与数据类型
//   2. 流程控制
//   3. 函数
//   4. 结构体与方法
//   5. 接口
//   6. 错误处理
//   7. 并发编程（goroutine / channel / sync）
//   8. 标准库常用操作
//
// 运行方式：
//   go run basics.go
//
// 注意：本脚本用于学习参考，可以直接运行查看输出。

package main

import (
	"crypto/md5"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net"
	"net/http"
	"os"
	"regexp"
	"sort"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

// ============================================================
// 辅助函数
// ============================================================

func printSection(title string) {
	fmt.Println()
	fmt.Println("=" + strings.Repeat("=", 58))
	fmt.Println("  " + title)
	fmt.Println("=" + strings.Repeat("=", 58))
	fmt.Println()
}

func printSubsection(title string) {
	fmt.Println()
	fmt.Println("  --- " + title + " ---")
	fmt.Println()
}

// ============================================================
// 1. 变量与数据类型
// ============================================================

func demoVariables() {
	printSection("【1. 变量与数据类型】")

	// 1.1 变量声明
	printSubsection("1.1 变量声明方式")
	var name string = "Alice"
	var age int = 25
	var isActive = true // 类型推导

	ip := "192.168.1.100" // 短变量声明（最常用）
	port := 443

	fmt.Println("  var 声明: name =", name)
	fmt.Println("  类型推导: age =", age)
	fmt.Println("  短变量: ip =", ip, ", port =", port)
	fmt.Println("  isActive =", isActive)

	// 1.2 常量
	printSubsection("1.2 常量与 iota")
	const AppName = "SecurityTool"
	const Version = "1.0.0"
	const MaxConnections = 1024

	fmt.Println("  AppName:", AppName)
	fmt.Println("  Version:", Version)
	fmt.Println("  MaxConnections:", MaxConnections)

	// iota 常量生成器
	const (
		Sunday    = iota // 0
		Monday           // 1
		Tuesday          // 2
		Wednesday        // 3
		Thursday         // 4
		Friday           // 5
		Saturday         // 6
	)
	fmt.Println("  Sunday =", Sunday, ", Monday =", Monday, ", Friday =", Friday)

	// 1.3 基本数据类型
	printSubsection("1.3 基本数据类型")
	var (
		boolVal    bool      = true
		strVal     string    = "hello 安全"
		intVal     int       = 42
		floatVal   float64   = 3.14159
		byteVal    byte      = 0x41 // = 'A'
		runeVal    rune      = '安'  // Unicode 字符
	)

	fmt.Printf("  bool:    %v (type: %T)\n", boolVal, boolVal)
	fmt.Printf("  string:  %v (type: %T, len: %d)\n", strVal, strVal, len(strVal))
	fmt.Printf("  int:     %v (type: %T)\n", intVal, intVal)
	fmt.Printf("  float64: %v (type: %T)\n", floatVal, floatVal)
	fmt.Printf("  byte:    %v = '%c' (type: %T)\n", byteVal, byteVal, byteVal)
	fmt.Printf("  rune:    %v = '%c' (type: %T)\n", runeVal, runeVal, runeVal)

	// 1.4 数组与切片
	printSubsection("1.4 数组与切片")

	// 数组（固定长度，不常用）
	var ipArray [3]string = [3]string{"192.168.1.1", "10.0.0.1", "172.16.0.1"}
	fmt.Println("  数组:", ipArray)
	fmt.Println("  数组长度:", len(ipArray))

	// 切片（动态长度，最常用）
	portSlice := []int{22, 80, 443, 3389, 8080}
	fmt.Println("  切片:", portSlice)
	fmt.Println("  切片长度:", len(portSlice))
	fmt.Println("  切片容量:", cap(portSlice))

	// append 添加元素
	portSlice = append(portSlice, 21, 25)
	fmt.Println("  append 后:", portSlice)

	// 切片操作
	fmt.Println("  portSlice[1:3]:", portSlice[1:3]) // [80 443]
	fmt.Println("  portSlice[:3]:", portSlice[:3])
	fmt.Println("  portSlice[3:]:", portSlice[3:])

	// make 创建切片
	targets := make([]string, 0, 100) // 长度0，容量100
	targets = append(targets, "target1.com", "target2.com")
	fmt.Println("  make 创建的切片:", targets)

	// 1.5 Map
	printSubsection("1.5 Map（键值对）")

	// 常见端口服务映射
	services := map[int]string{
		22:   "SSH",
		80:   "HTTP",
		443:  "HTTPS",
		3389: "RDP",
		21:   "FTP",
		25:   "SMTP",
		53:   "DNS",
	}

	fmt.Println("  端口服务映射:")
	for port, service := range services {
		fmt.Printf("    %5d -> %s\n", port, service)
	}

	// 读取（带存在检查）
	service, ok := services[443]
	if ok {
		fmt.Println("  443 端口服务:", service)
	} else {
		fmt.Println("  443 端口未找到")
	}

	// 添加
	services[3306] = "MySQL"
	fmt.Println("  添加 3306 后数量:", len(services))

	// 删除
	delete(services, 21)
	fmt.Println("  删除 21 后数量:", len(services))

	// 1.6 结构体
	printSubsection("1.6 结构体（struct）")

	type User struct {
		Username string
		Email    string
		Role     string
		IsActive bool
	}

	user1 := User{
		Username: "alice",
		Email:    "alice@example.com",
		Role:     "admin",
		IsActive: true,
	}

	user2 := User{"bob", "bob@example.com", "user", true} // 按顺序赋值（不推荐）

	fmt.Println("  user1:", user1)
	fmt.Println("  user1.Username:", user1.Username)
	fmt.Println("  user2:", user2)

	// 1.7 指针
	printSubsection("1.7 指针（pointer）")

	x := 10
	p := &x
	fmt.Println("  x =", x)
	fmt.Println("  &x =", p)
	fmt.Println("  *p =", *p)

	*p = 20
	fmt.Println("  修改 *p 后 x =", x)

	// 指针在结构体中的应用
	userPtr := &user1
	userPtr.Role = "superadmin" // 自动解引用
	fmt.Println("  通过指针修改后 user1.Role:", user1.Role)
}

// ============================================================
// 2. 流程控制
// ============================================================

func demoControlFlow() {
	printSection("【2. 流程控制】")

	// 2.1 if/else
	printSubsection("2.1 if / else if / else")

	score := 85
	if score >= 90 {
		fmt.Println("  优秀")
	} else if score >= 60 {
		fmt.Println("  及格")
	} else {
		fmt.Println("  不及格")
	}

	// if 带初始化语句
	if ip := "192.168.1.1"; strings.HasPrefix(ip, "192.168.") {
		fmt.Println("  内网 IP:", ip)
	}

	// 2.2 for 循环
	printSubsection("2.2 for 循环")

	fmt.Print("  经典 for: ")
	for i := 0; i < 5; i++ {
		fmt.Printf("%d ", i)
	}
	fmt.Println()

	// while 风格
	count := 0
	fmt.Print("  while 风格: ")
	for count < 5 {
		fmt.Printf("%d ", count)
		count++
	}
	fmt.Println()

	// range 遍历切片
	ports := []int{22, 80, 443, 3389}
	fmt.Println("  range 遍历切片:")
	for i, port := range ports {
		fmt.Printf("    %d: %d\n", i, port)
	}

	// range 遍历 map
	fmt.Println("  range 遍历 map:")
	services := map[int]string{22: "SSH", 80: "HTTP", 443: "HTTPS"}
	for port, name := range services {
		fmt.Printf("    %d -> %s\n", port, name)
	}

	// range 遍历字符串（按 rune）
	fmt.Print("  range 遍历字符串: ")
	for i, r := range "Go安全" {
		fmt.Printf("[%d:%c] ", i, r)
	}
	fmt.Println()

	// 2.3 switch
	printSubsection("2.3 switch")

	role := "admin"
	switch role {
	case "admin":
		fmt.Println("  管理员权限")
	case "editor":
		fmt.Println("  编辑权限")
	case "user":
		fmt.Println("  普通用户")
	default:
		fmt.Println("  未知角色")
	}

	// switch 不带表达式（替代 if/else 链）
	riskScore := 75
	switch {
	case riskScore >= 80:
		fmt.Println("  风险等级: 高危")
	case riskScore >= 50:
		fmt.Println("  风险等级: 中危")
	case riskScore >= 20:
		fmt.Println("  风险等级: 低危")
	default:
		fmt.Println("  风险等级: 无")
	}

	// 2.4 break / continue
	printSubsection("2.4 break / continue")

	fmt.Print("  continue 示例（只打印偶数）: ")
	for i := 1; i <= 10; i++ {
		if i%2 != 0 {
			continue // 跳过奇数
		}
		fmt.Printf("%d ", i)
	}
	fmt.Println()

	fmt.Print("  break 示例（到 5 停止）: ")
	for i := 1; i <= 10; i++ {
		if i > 5 {
			break
		}
		fmt.Printf("%d ", i)
	}
	fmt.Println()
}

// ============================================================
// 3. 函数
// ============================================================

func demoFunctions() {
	printSection("【3. 函数】")

	// 3.1 基本函数
	printSubsection("3.1 基本函数与多返回值")

	result := add(3, 5)
	fmt.Println("  add(3, 5) =", result)

	// 多返回值（Go 的特色）
	quotient, err := safeDivide(10, 3)
	if err != nil {
		fmt.Println("  错误:", err)
	} else {
		fmt.Println("  safeDivide(10, 3) =", quotient)
	}

	_, err2 := safeDivide(10, 0)
	if err2 != nil {
		fmt.Println("  safeDivide(10, 0) 错误:", err2)
	}

	// 3.2 命名返回值
	printSubsection("3.2 命名返回值")

	area, perimeter := rectInfo(5, 3)
	fmt.Println("  矩形 5x3:")
	fmt.Println("    面积 =", area)
	fmt.Println("    周长 =", perimeter)

	// 3.3 可变参数
	printSubsection("3.3 可变参数")

	fmt.Println("  sum(1, 2, 3) =", sum(1, 2, 3))
	fmt.Println("  sum(1, 2, 3, 4, 5) =", sum(1, 2, 3, 4, 5))

	// 展开切片
	nums := []int{10, 20, 30}
	fmt.Println("  sum(nums...) =", sum(nums...))

	// 3.4 闭包
	printSubsection("3.4 闭包")

	counter := makeCounter()
	fmt.Println("  counter() =", counter()) // 1
	fmt.Println("  counter() =", counter()) // 2
	fmt.Println("  counter() =", counter()) // 3

	counter2 := makeCounter()
	fmt.Println("  counter2() =", counter2()) // 1（独立的计数器）

	// 3.5 defer
	printSubsection("3.5 defer（延迟执行）")

	// defer 会在函数返回前执行，常用于资源清理
	// 执行顺序是后进先出（LIFO）
	fmt.Println("  defer 演示（实际场景中用于关闭文件、连接等）:")
	fmt.Println("    打开资源 A")
	defer fmt.Println("    关闭资源 A")
	fmt.Println("    打开资源 B")
	defer fmt.Println("    关闭资源 B")
	fmt.Println("    使用资源...")
	// 函数返回时会先关闭 B，再关闭 A
}

// 基本函数
func add(a, b int) int {
	return a + b
}

// 多返回值
func safeDivide(a, b float64) (float64, error) {
	if b == 0 {
		return 0, fmt.Errorf("除数不能为零")
	}
	return a / b, nil
}

// 命名返回值
func rectInfo(width, height float64) (area float64, perimeter float64) {
	area = width * height
	perimeter = 2 * (width + height)
	return // 裸返回
}

// 可变参数
func sum(nums ...int) int {
	total := 0
	for _, n := range nums {
		total += n
	}
	return total
}

// 闭包
func makeCounter() func() int {
	count := 0
	return func() int {
		count++
		return count
	}
}

// ============================================================
// 4. 结构体与方法
// ============================================================

// PortScanner 端口扫描器（结构体）
type PortScanner struct {
	Target  string
	Ports   []int
	Timeout time.Duration
	Threads int
}

// Scan 方法（指针接收者，可以修改原对象）
func (s *PortScanner) Scan() []int {
	// 简化版扫描，实际在 security_cases.go 中有完整实现
	var openPorts []int
	for _, port := range s.Ports {
		address := fmt.Sprintf("%s:%d", s.Target, port)
		conn, err := net.DialTimeout("tcp", address, s.Timeout)
		if err == nil {
			openPorts = append(openPorts, port)
			conn.Close()
		}
	}
	sort.Ints(openPorts)
	return openPorts
}

// GetTarget 方法（值接收者，不修改原对象）
func (s PortScanner) GetTarget() string {
	return s.Target
}

// 构造函数（Go 没有构造函数，约定俗成用 NewXxx）
func NewPortScanner(target string, ports []int) *PortScanner {
	return &PortScanner{
		Target:  target,
		Ports:   ports,
		Timeout: 2 * time.Second,
		Threads: 50,
	}
}

func demoStructsAndMethods() {
	printSection("【4. 结构体与方法】")

	// 创建结构体实例
	scanner := &PortScanner{
		Target:  "127.0.0.1",
		Ports:   []int{22, 80, 443, 3306, 8080},
		Timeout: 500 * time.Millisecond,
		Threads: 10,
	}

	fmt.Println("  扫描目标:", scanner.GetTarget())
	fmt.Println("  扫描端口:", scanner.Ports)
	fmt.Println("  超时时间:", scanner.Timeout)
	fmt.Println("  线程数:", scanner.Threads)

	// 使用构造函数
	scanner2 := NewPortScanner("localhost", []int{22, 80, 443})
	fmt.Println()
	fmt.Println("  构造函数创建的扫描器:")
	fmt.Println("    目标:", scanner2.Target)
	fmt.Println("    默认超时:", scanner2.Timeout)
	fmt.Println("    默认线程:", scanner2.Threads)

	fmt.Println()
	fmt.Println("  💡 方法的接收者可以是值或指针：")
	fmt.Println("    - 需要修改原对象 → 指针接收者")
	fmt.Println("    - 只读操作 → 值接收者（大结构体建议还是用指针避免拷贝）")
}

// ============================================================
// 5. 接口
// ============================================================

// Scanner 扫描器接口
type Scanner interface {
	Scan() ([]string, error)
	SetTarget(target string)
	GetTarget() string
}

// TCPScanner TCP 扫描器（实现 Scanner 接口）
type TCPScanner struct {
	target string
}

func (t *TCPScanner) Scan() ([]string, error) {
	return []string{"TCP scan result for " + t.target}, nil
}

func (t *TCPScanner) SetTarget(target string) {
	t.target = target
}

func (t *TCPScanner) GetTarget() string {
	return t.target
}

// HTTPScanner HTTP 扫描器（也实现 Scanner 接口）
type HTTPScanner struct {
	target string
}

func (h *HTTPScanner) Scan() ([]string, error) {
	return []string{"HTTP scan result for " + h.target}, nil
}

func (h *HTTPScanner) SetTarget(target string) {
	h.target = target
}

func (h *HTTPScanner) GetTarget() string {
	return h.target
}

// runScan 多态函数，接受任何 Scanner
func runScan(s Scanner) ([]string, error) {
	fmt.Println("  正在扫描:", s.GetTarget())
	return s.Scan()
}

func demoInterfaces() {
	printSection("【5. 接口与多态】")

	fmt.Println("  Go 接口是鸭子类型：只要实现了所有方法，就自动实现了接口")
	fmt.Println()

	// TCP 扫描器
	tcpScanner := &TCPScanner{target: "192.168.1.1"}
	result, _ := runScan(tcpScanner)
	fmt.Println("  结果:", result)

	fmt.Println()

	// HTTP 扫描器
	httpScanner := &HTTPScanner{target: "example.com"}
	result2, _ := runScan(httpScanner)
	fmt.Println("  结果:", result2)

	fmt.Println()
	fmt.Println("  💡 接口的好处：")
	fmt.Println("    - 解耦：调用方只依赖接口，不依赖具体实现")
	fmt.Println("    - 多态：不同实现可以互换使用")
	fmt.Println("    - 易测试：可以用 Mock 实现替换真实实现")
	fmt.Println()

	// 空接口 interface{} 可以接受任何类型
	fmt.Println("  空接口 interface{} 示例:")
	var anything interface{}
	anything = "hello"
	fmt.Println("    字符串:", anything)
	anything = 42
	fmt.Println("    整数:", anything)
	anything = []int{1, 2, 3}
	fmt.Println("    切片:", anything)

	// 类型断言
	fmt.Println()
	fmt.Println("  类型断言:")
	str, ok := anything.(string)
	if ok {
		fmt.Println("    是字符串:", str)
	} else {
		fmt.Println("    不是字符串")
	}

	// type switch
	fmt.Println()
	fmt.Println("  type switch:")
	printType("hello")
	printType(42)
	printType(true)
	printType([]int{1, 2, 3})
}

func printType(v interface{}) {
	switch v.(type) {
	case string:
		fmt.Printf("    %v 是字符串\n", v)
	case int:
		fmt.Printf("    %v 是整数\n", v)
	case bool:
		fmt.Printf("    %v 是布尔值\n", v)
	default:
		fmt.Printf("    %v 是其他类型 (%T)\n", v, v)
	}
}

// ============================================================
// 6. 错误处理
// ============================================================

// SecurityError 自定义安全错误
type SecurityError struct {
	Code    string
	Message string
	Details string
}

func (e *SecurityError) Error() string {
	return fmt.Sprintf("[%s] %s: %s", e.Code, e.Message, e.Details)
}

// NewSecurityError 创建安全错误
func NewSecurityError(code, message, details string) error {
	return &SecurityError{
		Code:    code,
		Message: message,
		Details: details,
	}
}

func demoErrorHandling() {
	printSection("【6. 错误处理】")

	// 6.1 基本错误处理模式
	printSubsection("6.1 基本错误处理")

	fmt.Println("  Go 没有 try/catch，错误通过返回值传递")
	fmt.Println()

	// 正常情况
	result, err := safeDivide(10, 2)
	if err != nil {
		fmt.Println("  错误:", err)
	} else {
		fmt.Println("  结果:", result)
	}

	// 错误情况
	result, err = safeDivide(10, 0)
	if err != nil {
		fmt.Println("  错误:", err)
	} else {
		fmt.Println("  结果:", result)
	}

	// 6.2 自定义错误
	printSubsection("6.2 自定义错误")

	err = NewSecurityError("AUTH-001", "认证失败", "密码错误次数过多")
	fmt.Println("  自定义错误:", err)

	// 类型断言判断错误类型
	if secErr, ok := err.(*SecurityError); ok {
		fmt.Println("  错误代码:", secErr.Code)
		fmt.Println("  错误消息:", secErr.Message)
		fmt.Println("  详细信息:", secErr.Details)
	}

	// 6.3 errors.Is 和 errors.As（Go 1.13+）
	printSubsection("6.3 错误包装与解包")

	// fmt.Errorf + %w 包装错误
	innerErr := fmt.Errorf("原始错误")
	wrappedErr := fmt.Errorf("外层错误: %w", innerErr)
	fmt.Println("  包装错误:", wrappedErr)

	// 6.4 panic 和 recover（尽量少用）
	printSubsection("6.4 panic 和 recover（仅用于不可恢复错误）")

	// 模拟一个会 panic 的函数
	safeCall := func() {
		defer func() {
			if r := recover(); r != nil {
				fmt.Println("  恢复 panic:", r)
			}
		}()
		// 模拟 panic
		panic("模拟严重错误")
	}

	safeCall()
	fmt.Println("  程序继续运行...")

	fmt.Println()
	fmt.Println("  💡 错误处理最佳实践：")
	fmt.Println("    1. 永远检查错误，不要忽略（用 _ 丢弃）")
	fmt.Println("    2. 错误信息要有上下文")
	fmt.Println("    3. 库函数不要 panic，应该返回 error")
	fmt.Println("    4. 只有真正不可恢复的错误才用 panic")
}

// ============================================================
// 7. 并发编程
// ============================================================

func demoConcurrency() {
	printSection("【7. 并发编程（goroutine + channel）】")

	// 7.1 goroutine 基础
	printSubsection("7.1 goroutine 基础")

	fmt.Println("  启动 5 个 goroutine:")
	var wg sync.WaitGroup

	for i := 1; i <= 5; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			time.Sleep(time.Duration(id) * 100 * time.Millisecond)
			fmt.Printf("    goroutine %d 完成\n", id)
		}(i)
	}

	wg.Wait()
	fmt.Println("  所有 goroutine 完成")

	// 7.2 channel
	printSubsection("7.2 channel（通道）")

	// 无缓冲 channel
	fmt.Println("  无缓冲 channel 示例:")
	ch := make(chan string)

	go func() {
		ch <- "来自 goroutine 的消息"
	}()

	msg := <-ch
	fmt.Println("  收到消息:", msg)

	// 带缓冲 channel
	fmt.Println()
	fmt.Println("  带缓冲 channel 示例:")
	bufferedCh := make(chan int, 3)
	bufferedCh <- 1
	bufferedCh <- 2
	bufferedCh <- 3
	fmt.Println("  缓冲大小: 3, 已放入 3 个值")
	fmt.Println("  取出:", <-bufferedCh)
	fmt.Println("  取出:", <-bufferedCh)
	bufferedCh <- 4
	fmt.Println("  再放入 1 个，取出:", <-bufferedCh)
	fmt.Println("  最后一个:", <-bufferedCh)
	close(bufferedCh)

	// 7.3 Worker Pool 模式
	printSubsection("7.3 Worker Pool 模式（安全工具常用）")

	tasks := make(chan int, 10)
	results := make(chan string, 10)
	var wp sync.WaitGroup

	workerCount := 3
	fmt.Printf("  启动 %d 个 worker 处理任务:\n", workerCount)

	// 启动 worker
	for w := 1; w <= workerCount; w++ {
		wp.Add(1)
		go func(workerID int) {
			defer wp.Done()
			for task := range tasks {
				time.Sleep(50 * time.Millisecond) // 模拟工作
				results <- fmt.Sprintf("worker %d 处理任务 %d", workerID, task)
			}
		}(w)
	}

	// 发送任务
	for i := 1; i <= 6; i++ {
		tasks <- i
	}
	close(tasks)

	// 等待完成
	go func() {
		wp.Wait()
		close(results)
	}()

	// 收集结果
	for result := range results {
		fmt.Println("    " + result)
	}

	// 7.4 select 多路复用
	printSubsection("7.4 select 多路复用")

	ch1 := make(chan string)
	ch2 := make(chan string)

	go func() {
		time.Sleep(100 * time.Millisecond)
		ch1 <- "来自 ch1"
	}()

	go func() {
		time.Sleep(200 * time.Millisecond)
		ch2 <- "来自 ch2"
	}()

	// select 会选择第一个就绪的
	for i := 0; i < 2; i++ {
		select {
		case msg1 := <-ch1:
			fmt.Println("  select 收到:", msg1)
		case msg2 := <-ch2:
			fmt.Println("  select 收到:", msg2)
		case <-time.After(500 * time.Millisecond):
			fmt.Println("  超时！")
		}
	}

	// 7.5 sync.Mutex 互斥锁
	printSubsection("7.5 sync.Mutex 互斥锁")

	var counter int
	var mu sync.Mutex

	increment := func() {
		mu.Lock()
		defer mu.Unlock()
		counter++
	}

	var wg2 sync.WaitGroup
	for i := 0; i < 1000; i++ {
		wg2.Add(1)
		go func() {
			defer wg2.Done()
			increment()
		}()
	}
	wg2.Wait()
	fmt.Println("  1000 个 goroutine 并发计数结果:", counter)
	fmt.Println("  (如果没有锁，结果可能不是 1000)")

	// 7.6 sync.Map 并发安全 Map
	printSubsection("7.6 sync.Map 并发安全 Map")

	var safeMap sync.Map
	var wg3 sync.WaitGroup

	for i := 0; i < 100; i++ {
		wg3.Add(1)
		go func(i int) {
			defer wg3.Done()
			key := fmt.Sprintf("key_%d", i)
			safeMap.Store(key, i*10)
		}(i)
	}
	wg3.Wait()

	count := 0
	safeMap.Range(func(key, value interface{}) bool {
		count++
		return true // 继续遍历
	})
	fmt.Println("  sync.Map 元素数量:", count)

	// 7.7 atomic 原子操作
	printSubsection("7.7 atomic 原子操作")

	var atomicCounter int64

	var wg4 sync.WaitGroup
	for i := 0; i < 1000; i++ {
		wg4.Add(1)
		go func() {
			defer wg4.Done()
			atomic.AddInt64(&atomicCounter, 1)
		}()
	}
	wg4.Wait()
	fmt.Println("  atomic 计数结果:", atomicCounter)
}

// ============================================================
// 8. 标准库常用操作
// ============================================================

func demoStandardLibrary() {
	printSection("【8. 标准库常用操作】")

	// 8.1 字符串处理
	printSubsection("8.1 strings 包")

	s := "  Hello, Security World!  "
	fmt.Println("  原始字符串:", s)
	fmt.Println("  ToUpper:", strings.ToUpper(s))
	fmt.Println("  ToLower:", strings.ToLower(s))
	fmt.Println("  Trim:", strings.TrimSpace(s))
	fmt.Println("  Contains 'Security':", strings.Contains(s, "Security"))
	fmt.Println("  HasPrefix 'Hello':", strings.HasPrefix(strings.TrimSpace(s), "Hello"))
	fmt.Println("  Index 'World':", strings.Index(s, "World"))
	fmt.Println("  Replace: ", strings.Replace(s, "World", "Go", 1))
	fmt.Println("  Split by ',':", strings.Split(s, ","))
	fmt.Println("  Join:", strings.Join([]string{"a", "b", "c"}, "-"))

	// 8.2 正则表达式
	printSubsection("8.2 regexp 正则表达式")

	emailPattern := `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
	re := regexp.MustCompile(emailPattern)

	testEmails := []string{"alice@example.com", "invalid@", "bob@test.org"}
	for _, email := range testEmails {
		fmt.Printf("  %-25s -> %v\n", email, re.MatchString(email))
	}

	// IP 地址匹配
	ipPattern := `^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$`
	ipRe := regexp.MustCompile(ipPattern)
	fmt.Println()
	fmt.Println("  IP 格式验证:")
	fmt.Println("    192.168.1.1 ->", ipRe.MatchString("192.168.1.1"))
	fmt.Println("    10.0.0.256 ->", ipRe.MatchString("10.0.0.256"))
	fmt.Println("    (这只是简单格式验证，不检查 0-255 范围)")

	// 8.3 加密哈希
	printSubsection("8.3 加密哈希（crypto 包）")

	data := "password123"

	// MD5（不推荐用于安全场景）
	md5Hash := md5.Sum([]byte(data))
	fmt.Println("  MD5:  ", hex.EncodeToString(md5Hash[:]))

	// SHA-256（推荐）
	sha256Hash := sha256.Sum256([]byte(data))
	fmt.Println("  SHA256:", hex.EncodeToString(sha256Hash[:]))

	// 8.4 JSON 处理
	printSubsection("8.4 JSON 处理")

	type UserInfo struct {
		Username string `json:"username"`
		Email    string `json:"email"`
		Role     string `json:"role"`
		Age      int    `json:"age,omitempty"` // 零值时省略
		Secret   string `json:"-"`            // 始终忽略
	}

	user := UserInfo{
		Username: "alice",
		Email:    "alice@example.com",
		Role:     "admin",
		Secret:   "secret-value", // 不会被序列化
	}

	// 序列化
	jsonData, err := json.MarshalIndent(user, "", "  ")
	if err != nil {
		fmt.Println("  JSON 序列化错误:", err)
	} else {
		fmt.Println("  JSON 序列化:")
		fmt.Println("   " + strings.ReplaceAll(string(jsonData), "\n", "\n    "))
	}

	// 反序列化
	jsonStr := `{"username":"bob","email":"bob@example.com","role":"user","age":30}`
	var user2 UserInfo
	err = json.Unmarshal([]byte(jsonStr), &user2)
	if err != nil {
		fmt.Println("  JSON 反序列化错误:", err)
	} else {
		fmt.Println("  JSON 反序列化:")
		fmt.Printf("    Username: %s, Email: %s, Role: %s\n", user2.Username, user2.Email, user2.Role)
	}

	// 8.5 文件操作
	printSubsection("8.5 文件操作（os/io）")

	tmpFile, err := os.CreateTemp("", "go-security-*.txt")
	if err != nil {
		fmt.Println("  创建临时文件失败:", err)
		return
	}
	defer os.Remove(tmpFile.Name())
	defer tmpFile.Close()

	content := []byte("这是安全测试文件\n包含敏感数据测试\n")
	n, err := tmpFile.Write(content)
	if err != nil {
		fmt.Println("  写入失败:", err)
		return
	}
	fmt.Println("  临时文件:", tmpFile.Name())
	fmt.Println("  写入字节数:", n)

	// 读取文件
	dataBytes, err := os.ReadFile(tmpFile.Name())
	if err != nil {
		fmt.Println("  读取失败:", err)
		return
	}
	fmt.Println("  文件内容:")
	for _, line := range strings.Split(string(dataBytes), "\n") {
		if line != "" {
			fmt.Println("    " + line)
		}
	}

	// 8.6 HTTP 客户端
	printSubsection("8.6 net/http 客户端")

	// 简单 GET 请求（带超时）
	client := &http.Client{
		Timeout: 5 * time.Second,
	}

	resp, err := client.Get("https://example.com")
	if err != nil {
		fmt.Println("  HTTP 请求失败:", err)
		fmt.Println("  (这是正常的，可能网络不可达)")
	} else {
		defer resp.Body.Close()
		body, _ := io.ReadAll(resp.Body)
		fmt.Println("  响应状态:", resp.Status)
		fmt.Println("  响应长度:", len(body), "字节")
	}
}

// ============================================================
// 主函数
// ============================================================

func main() {
	fmt.Println()
	fmt.Println("============================================================")
	fmt.Println("  Go 语言基础语法示例（安全从业者视角）")
	fmt.Println("  Go Basics for Security Practitioners")
	fmt.Println("============================================================")

	// 1. 变量与数据类型
	demoVariables()

	// 2. 流程控制
	demoControlFlow()

	// 3. 函数
	demoFunctions()

	// 4. 结构体与方法
	demoStructsAndMethods()

	// 5. 接口
	demoInterfaces()

	// 6. 错误处理
	demoErrorHandling()

	// 7. 并发编程
	demoConcurrency()

	// 8. 标准库
	demoStandardLibrary()

	fmt.Println()
	fmt.Println("============================================================")
	fmt.Println("  所有示例执行完毕")
	fmt.Println("  涵盖：变量、流程控制、函数、结构体、接口、")
	fmt.Println("  错误处理、并发编程、标准库")
	fmt.Println("============================================================")
	fmt.Println()
}
