// ============================================================
// Go 语言基础示例 07：正则表达式（regexp）
// 运行方式：go run 07_regex.go
// ============================================================

package main

import (
	"fmt"
	"regexp"
)

func main() {
	// -------------------- 正则基础 --------------------
	fmt.Println("========== 正则基础 ==========")

	// 方式一：Compile（可能返回错误）
	re1, err := regexp.Compile(`\d+`)
	if err != nil {
		fmt.Println("正则编译错误：", err)
	} else {
		fmt.Println("编译成功：", re1.MatchString("abc123"))
	}

	// 方式二：MustCompile（必须成功，失败则 panic，适合常量正则）
	re2 := regexp.MustCompile(`\d+`)
	fmt.Println("MustCompile：", re2.MatchString("abc123"))

	// -------------------- 匹配检测 --------------------
	fmt.Println("\n========== 匹配检测 ==========")

	// MatchString 检测是否匹配
	re := regexp.MustCompile(`go`)
	fmt.Println("'golang' 包含 'go'：", re.MatchString("golang"))
	fmt.Println("'python' 包含 'go'：", re.MatchString("python"))

	// 匹配完整字符串（^ 和 $）
	reFull := regexp.MustCompile(`^\d+$`) // 全是数字
	fmt.Println("'12345' 全是数字：", reFull.MatchString("12345"))
	fmt.Println("'12a45' 全是数字：", reFull.MatchString("12a45"))

	// -------------------- 查找匹配 --------------------
	fmt.Println("\n========== 查找匹配 ==========")

	text := "abc123def456ghi789"
	reNum := regexp.MustCompile(`\d+`)

	// FindString 查找第一个匹配
	first := reNum.FindString(text)
	fmt.Println("第一个数字串：", first)

	// FindAllString 查找所有匹配（-1 表示返回全部）
	all := reNum.FindAllString(text, -1)
	fmt.Println("所有数字串：", all)

	// 只返回前 N 个
	first2 := reNum.FindAllString(text, 2)
	fmt.Println("前2个数字串：", first2)

	// FindStringIndex 返回位置（起始和结束索引）
	idx := reNum.FindStringIndex(text)
	fmt.Println("第一个匹配的位置：", idx)
	fmt.Println("截取验证：", text[idx[0]:idx[1]])

	// -------------------- 分组捕获 --------------------
	fmt.Println("\n========== 分组捕获 ==========")

	// 日期格式：年-月-日
	reDate := regexp.MustCompile(`(\d{4})-(\d{2})-(\d{2})`)
	dateStr := "今天是 2024-01-15，明天是 2024-01-16"

	// FindStringSubmatch 返回第一个匹配的所有分组
	match := reDate.FindStringSubmatch(dateStr)
	fmt.Println("第一个日期匹配：")
	fmt.Println("  完整匹配：", match[0])
	fmt.Println("  年：", match[1])
	fmt.Println("  月：", match[2])
	fmt.Println("  日：", match[3])

	// FindAllStringSubmatch 返回所有匹配的所有分组
	allMatches := reDate.FindAllStringSubmatch(dateStr, -1)
	fmt.Println("所有日期匹配：")
	for i, m := range allMatches {
		fmt.Printf("  第%d个: %s年%s月%s日\n", i+1, m[1], m[2], m[3])
	}

	// 命名分组
	reNamed := regexp.MustCompile(`(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})`)
	match2 := reNamed.FindStringSubmatch("2024-06-01")
	fmt.Println("命名分组：")
	for i, name := range reNamed.SubexpNames() {
		if i > 0 {
			fmt.Printf("  %s: %s\n", name, match2[i])
		}
	}

	// -------------------- 替换 --------------------
	fmt.Println("\n========== 替换 ==========")

	reLetter := regexp.MustCompile(`[a-z]+`)
	text2 := "abc123def456"

	// ReplaceAllString 全部替换
	replaced := reLetter.ReplaceAllString(text2, "X")
	fmt.Println("替换字母为 X：", replaced)

	// 分组引用替换（$1, $2 等）
	rePhone := regexp.MustCompile(`(\d{3})\d{4}(\d{4})`)
	phone := "13812345678"
	masked := rePhone.ReplaceAllString(phone, "$1****$2")
	fmt.Println("手机号脱敏：", masked)

	// ReplaceAllStringFunc 用函数处理替换
	reUpper := regexp.MustCompile(`\b\w+\b`)
	text3 := "hello world go"
	result := reUpper.ReplaceAllStringFunc(text3, func(s string) string {
		// 首字母大写
		if len(s) > 0 {
			return stringsToUpper(s[:1]) + s[1:]
		}
		return s
	})
	fmt.Println("每个单词首字母大写：", result)

	// -------------------- 常用正则模式 --------------------
	fmt.Println("\n========== 常用正则模式 ==========")

	// 邮箱验证
	reEmail := regexp.MustCompile(`^[\w.-]+@[\w-]+\.[\w.-]+$`)
	emails := []string{"test@example.com", "user.name@domain.co.uk", "invalid-email"}
	fmt.Println("邮箱验证：")
	for _, e := range emails {
		fmt.Printf("  %s: %v\n", e, reEmail.MatchString(e))
	}

	// IP 地址
	reIP := regexp.MustCompile(`\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b`)
	logText := "服务器 IP: 192.168.1.100，网关: 192.168.1.1"
	fmt.Println("提取 IP：", reIP.FindAllString(logText, -1))

	// 中国手机号
	rePhone2 := regexp.MustCompile(`^1[3-9]\d{9}$`)
	phones := []string{"13812345678", "12345678901", "1381234"}
	fmt.Println("手机号验证：")
	for _, p := range phones {
		fmt.Printf("  %s: %v\n", p, rePhone2.MatchString(p))
	}

	// URL
	reURL := regexp.MustCompile(`https?://[\w.-]+(/[\w./?=%&-]*)?`)
	urlText := "访问 https://example.com/page?id=1 或 http://test.org"
	fmt.Println("提取 URL：", reURL.FindAllString(urlText, -1))

	// -------------------- 正则语法速查 --------------------
	fmt.Println("\n========== 正则语法速查 ==========")

	patterns := []struct {
		pattern string
		desc    string
	}{
		{`.`, "匹配任意单个字符（除换行）"},
		{`\d`, "匹配数字 [0-9]"},
		{`\D`, "匹配非数字"},
		{`\w`, "匹配字母数字下划线 [a-zA-Z0-9_]"},
		{`\W`, "匹配非字母数字下划线"},
		{`\s`, "匹配空白字符（空格、制表符等）"},
		{`\S`, "匹配非空白字符"},
		{`^`, "匹配字符串开头"},
		{`$`, "匹配字符串结尾"},
		{`*`, "匹配前一个字符 0 次或多次"},
		{`+`, "匹配前一个字符 1 次或多次"},
		{`?`, "匹配前一个字符 0 次或 1 次"},
		{`{n}`, "匹配前一个字符恰好 n 次"},
		{`{n,m}`, "匹配前一个字符 n 到 m 次"},
		{`[abc]`, "匹配字符集中的任意一个"},
		{`[^abc]`, "匹配不在字符集中的字符"},
		{`(abc)`, "分组捕获"},
		{`a|b`, "匹配 a 或 b"},
		{`\b`, "匹配单词边界"},
	}

	fmt.Println("常用正则语法：")
	for _, p := range patterns {
		fmt.Printf("  %-10s %s\n", p.pattern, p.desc)
	}

	// -------------------- 安全场景示例：敏感信息提取 --------------------
	fmt.Println("\n========== 安全场景：敏感信息提取 ==========")

	// 从日志中提取邮箱和手机号
	logData := `
用户注册信息：
- 邮箱：admin@example.com
- 手机：13912345678
- 备用邮箱：test@test.org
- IP：10.0.0.1
`

	emailRe := regexp.MustCompile(`[\w.-]+@[\w.-]+\.\w+`)
	phoneRe := regexp.MustCompile(`1[3-9]\d{9}`)
	ipRe := regexp.MustCompile(`\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}`)

	fmt.Println("提取的邮箱：", emailRe.FindAllString(logData, -1))
	fmt.Println("提取的手机号：", phoneRe.FindAllString(logData, -1))
	fmt.Println("提取的 IP：", ipRe.FindAllString(logData, -1))

	fmt.Println("\n========== 示例结束 ==========")
}

// 辅助函数：字符串转大写
func stringsToUpper(s string) string {
	result := ""
	for _, r := range s {
		if r >= 'a' && r <= 'z' {
			result += string(r - 32)
		} else {
			result += string(r)
		}
	}
	return result
}
