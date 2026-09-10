/*
 * ============================================================
 * 文件名：http_header_check.go
 * 功能描述：HTTP 安全头检测工具
 * 作者：网络安全学习笔记
 * 日期：2026-09-10
 * ============================================================
 *
 * 【使用说明】
 * 1. 编译运行：go run http_header_check.go
 * 2. 命令行参数：
 *    -url    目标 URL（默认：http://127.0.0.1）
 *    -timeout 请求超时时间，单位秒（默认：10）
 *
 * 【示例】
 *   go run http_header_check.go -url https://example.com
 *   go run http_header_check.go -url http://192.168.1.1:8080 -timeout 5
 *
 * 【检测的 7 大安全头】
 *   1. X-Content-Type-Options    - 防止 MIME 类型嗅探
 *   2. X-Frame-Options           - 防止点击劫持攻击
 *   3. X-XSS-Protection          - 启用浏览器 XSS 防护
 *   4. Content-Security-Policy   - 内容安全策略（防XSS等）
 *   5. Strict-Transport-Security - 强制使用 HTTPS
 *   6. Referrer-Policy           - 控制 Referer 信息泄露
 *   7. Permissions-Policy        - 控制浏览器功能权限
 *
 * 【评分规则】
 *   - 每个安全头最高 1 分，共 7 分
 *   - 根据配置的严格程度给予部分分数
 *   - 最终给出总分和等级评定
 *
 * 【免责声明】
 *   本工具仅供网络安全学习和授权测试使用。
 *   仅用于检测目标网站的 HTTP 安全头配置情况。
 *   使用本工具请遵守当地法律法规。
 * ============================================================
 */

package main

import (
	"crypto/tls"   // TLS 配置
	"flag"         // 命令行参数解析
	"fmt"          // 格式化输出
	"net/http"     // HTTP 客户端
	"strings"      // 字符串处理
	"time"         // 时间相关
)

// HeaderCheckResult 定义单个安全头的检测结果
type HeaderCheckResult struct {
	Name        string  // 安全头名称
	Present     bool    // 是否存在
	Value       string  // 头的值
	Score       float64 // 得分（0-1）
	Description string  // 头的作用说明
	Advice      string  // 改进建议
}

// SecurityHeader 定义安全头的配置信息
type SecurityHeader struct {
	Name        string // 头名称
	Description string // 作用说明
	BestValue   string // 推荐配置值
}

// securityHeaders 定义要检测的 7 大安全头
var securityHeaders = []SecurityHeader{
	{
		Name:        "X-Content-Type-Options",
		Description: "防止浏览器进行 MIME 类型嗅探，强制使用 Content-Type 声明的类型",
		BestValue:   "nosniff",
	},
	{
		Name:        "X-Frame-Options",
		Description: "防止页面被嵌入到 iframe 中，抵御点击劫持攻击",
		BestValue:   "DENY 或 SAMEORIGIN",
	},
	{
		Name:        "X-XSS-Protection",
		Description: "启用浏览器内置的 XSS 防护机制",
		BestValue:   "1; mode=block",
	},
	{
		Name:        "Content-Security-Policy",
		Description: "内容安全策略，限制资源加载来源，有效防御 XSS 等注入攻击",
		BestValue:   "严格的 CSP 策略",
	},
	{
		Name:        "Strict-Transport-Security",
		Description: "强制浏览器使用 HTTPS 访问，防止协议降级攻击",
		BestValue:   "max-age=31536000; includeSubDomains",
	},
	{
		Name:        "Referrer-Policy",
		Description: "控制 Referer 头信息的发送，防止敏感信息泄露",
		BestValue:   "strict-origin-when-cross-origin 或 no-referrer",
	},
	{
		Name:        "Permissions-Policy",
		Description: "控制浏览器功能（如摄像头、麦克风、地理位置等）的使用权限",
		BestValue:   "限制不必要的功能权限",
	},
}

// evaluateHeader 评估单个安全头的配置质量
// 参数：
//   header - 安全头配置信息
//   value - 实际的头值（空字符串表示不存在）
// 返回：得分（0-1）和改进建议
func evaluateHeader(header SecurityHeader, value string) (float64, string) {
	// 如果值为空，表示头不存在
	if value == "" {
		return 0, fmt.Sprintf("未设置 %s 头，建议添加：%s", header.Name, header.BestValue)
	}

	valueLower := strings.ToLower(value)

	// 根据不同的头进行评分
	switch header.Name {
	case "X-Content-Type-Options":
		if strings.Contains(valueLower, "nosniff") {
			return 1, "配置正确"
		}
		return 0.3, "建议设置为 nosniff"

	case "X-Frame-Options":
		if strings.Contains(valueLower, "deny") {
			return 1, "配置严格（DENY）"
		} else if strings.Contains(valueLower, "sameorigin") {
			return 0.8, "配置较好（SAMEORIGIN）"
		} else if strings.Contains(valueLower, "allow-from") {
			return 0.5, "配置了白名单（ALLOW-FROM）"
		}
		return 0.2, "配置值不正确"

	case "X-XSS-Protection":
		if strings.Contains(valueLower, "1; mode=block") {
			return 1, "配置正确，启用强制拦截模式"
		} else if strings.Contains(valueLower, "1") {
			return 0.6, "启用了 XSS 防护，但建议添加 mode=block"
		} else if strings.Contains(valueLower, "0") {
			return 0, "已禁用 XSS 防护，建议启用"
		}
		return 0.3, "建议设置为 1; mode=block"

	case "Content-Security-Policy":
		// CSP 的评分比较复杂，这里做简单评估
		if strings.Contains(valueLower, "default-src 'self'") {
			return 1, "配置了严格的默认源策略"
		} else if strings.Contains(valueLower, "default-src") {
			return 0.8, "配置了 default-src，建议限制为 'self'"
		} else if strings.Contains(valueLower, "script-src") {
			return 0.7, "配置了 script-src，建议也配置 default-src"
		} else if len(value) > 10 {
			return 0.5, "已配置 CSP，但策略可能不够严格"
		}
		return 0.3, "CSP 配置过于简单"

	case "Strict-Transport-Security":
		// HSTS 评分
		if strings.Contains(valueLower, "max-age=") {
			// 提取 max-age 值
			if strings.Contains(valueLower, "includesubdomains") &&
				strings.Contains(valueLower, "preload") {
				return 1, "配置完整，包含子域名和 preload"
			} else if strings.Contains(valueLower, "includesubdomains") {
				return 0.85, "配置较好，包含子域名"
			}
			return 0.7, "已配置 HSTS，建议添加 includeSubDomains"
		}
		return 0.2, "HSTS 配置不正确"

	case "Referrer-Policy":
		if strings.Contains(valueLower, "no-referrer") {
			return 1, "配置最严格（no-referrer）"
		} else if strings.Contains(valueLower, "strict-origin-when-cross-origin") {
			return 0.9, "配置较好，平衡安全与可用性"
		} else if strings.Contains(valueLower, "same-origin") {
			return 0.7, "同源策略，跨域不发送 referrer"
		} else if strings.Contains(valueLower, "origin") {
			return 0.5, "仅发送 origin 信息"
		}
		return 0.3, "建议设置为 strict-origin-when-cross-origin"

	case "Permissions-Policy":
		// 权限策略评分
		if strings.Contains(valueLower, "geolocation=()") ||
			strings.Contains(valueLower, "camera=()") ||
			strings.Contains(valueLower, "microphone=()") {
			return 1, "已限制敏感权限"
		} else if len(value) > 10 {
			return 0.6, "已配置权限策略，建议进一步限制"
		}
		return 0.3, "权限策略配置过于简单"

	default:
		return 0.5, "已配置"
	}
}

// getGrade 根据总分获取等级评定
func getGrade(score float64) string {
	switch {
	case score >= 6.5:
		return "A (优秀)"
	case score >= 5.5:
		return "B (良好)"
	case score >= 4.0:
		return "C (一般)"
	case score >= 2.5:
		return "D (较差)"
	default:
		return "F (危险)"
	}
}

func main() {
	// ===================== 命令行参数解析 =====================
	targetURL := flag.String("url", "http://127.0.0.1", "目标 URL")
	timeoutSec := flag.Int("timeout", 10, "请求超时时间（秒）")

	flag.Parse()

	// 参数校验
	if *targetURL == "" {
		fmt.Println("[错误] 请指定目标 URL")
		return
	}

	// 确保 URL 有协议前缀
	if !strings.HasPrefix(*targetURL, "http://") && !strings.HasPrefix(*targetURL, "https://") {
		*targetURL = "http://" + *targetURL
	}

	// ===================== 打印检测信息 =====================
	fmt.Println("========================================")
	fmt.Println("     HTTP 安全头检测工具（Go 版）")
	fmt.Println("========================================")
	fmt.Printf("目标 URL: %s\n", *targetURL)
	fmt.Printf("超时时间: %d 秒\n", *timeoutSec)
	fmt.Println("========================================")
	fmt.Println("[*] 正在检测，请稍候...")

	// ===================== 初始化 HTTP 客户端 =====================
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{
		Timeout:   time.Duration(*timeoutSec) * time.Second,
		Transport: tr,
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			return http.ErrUseLastResponse // 不跟随重定向
		},
	}

	// ===================== 发送请求 =====================
	req, err := http.NewRequest("GET", *targetURL, nil)
	if err != nil {
		fmt.Printf("[错误] 创建请求失败: %v\n", err)
		return
	}

	// 设置请求头
	req.Header.Set("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
	req.Header.Set("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")

	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("[错误] 请求失败: %v\n", err)
		return
	}
	defer resp.Body.Close()

	fmt.Printf("[*] 响应状态码: %d\n", resp.StatusCode)
	fmt.Println("----------------------------------------")

	// ===================== 检测安全头 =====================
	var results []*HeaderCheckResult
	totalScore := 0.0

	for _, header := range securityHeaders {
		// 获取响应头的值（不区分大小写）
		value := resp.Header.Get(header.Name)

		// 评估该头的配置
		score, advice := evaluateHeader(header, value)

		result := &HeaderCheckResult{
			Name:        header.Name,
			Present:     value != "",
			Value:       value,
			Score:       score,
			Description: header.Description,
			Advice:      advice,
		}

		results = append(results, result)
		totalScore += score
	}

	// ===================== 输出检测结果 =====================
	fmt.Println("\n========================================")
	fmt.Println("            检测结果详情")
	fmt.Println("========================================")

	for i, result := range results {
		status := "[未设置]"
		if result.Present {
			status = "[已设置]"
		}

		fmt.Printf("\n%d. %s %s\n", i+1, result.Name, status)
		fmt.Printf("   作用: %s\n", result.Description)
		fmt.Printf("   得分: %.1f / 1.0\n", result.Score)

		if result.Present {
			fmt.Printf("   当前值: %s\n", result.Value)
		}
		fmt.Printf("   建议: %s\n", result.Advice)
	}

	// ===================== 输出评分汇总 =====================
	fmt.Println("\n========================================")
	fmt.Println("           安全评分汇总")
	fmt.Println("========================================")
	fmt.Printf("总得分: %.1f / 7.0\n", totalScore)
	fmt.Printf("安全等级: %s\n", getGrade(totalScore))

	// 计算百分比
	percentage := (totalScore / 7.0) * 100
	fmt.Printf("完成度: %.1f%%\n", percentage)

	// 显示进度条
	fmt.Print("进度条: [")
	filled := int(totalScore)
	for i := 0; i < filled; i++ {
		fmt.Print("=")
	}
	for i := filled; i < 7; i++ {
		fmt.Print("-")
	}
	fmt.Println("]")

	fmt.Println("\n========================================")
	fmt.Println("            检测完成")
	fmt.Println("========================================")
	fmt.Println("\n[提示] 以上评分仅供参考，实际安全性还需结合其他因素综合评估。")
}
