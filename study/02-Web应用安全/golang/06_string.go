// ============================================================
// Go 语言基础示例 06：字符串操作
// 运行方式：go run 06_string.go
// ============================================================

package main

import (
	"fmt"
	"strconv"
	"strings"
)

func main() {
	// -------------------- 字符串基础 --------------------
	fmt.Println("========== 字符串基础 ==========")

	// 双引号字符串（支持转义字符）
	s1 := "Hello, Go!"
	fmt.Println("双引号字符串：", s1)

	// 反引号字符串（原始字符串，不支持转义）
	s2 := `这是原始字符串
可以换行
支持特殊字符：\n \t`
	fmt.Println("反引号字符串：")
	fmt.Println(s2)

	// 字符串长度（字节数，不是字符数）
	s3 := "你好，世界"
	fmt.Println("字符串：", s3)
	fmt.Println("字节长度：", len(s3)) // 中文每个占 3 字节

	// 字符数（rune 数）
	fmt.Println("字符数：", len([]rune(s3)))

	// -------------------- 字符串拼接 --------------------
	fmt.Println("\n========== 字符串拼接 ==========")

	// 方式一：+ 号拼接（简单场景）
	a := "Hello"
	b := "World"
	c := a + " " + b
	fmt.Println("+ 拼接：", c)

	// 方式二：fmt.Sprintf（格式化拼接）
	name := "张三"
	age := 20
	msg := fmt.Sprintf("姓名：%s，年龄：%d", name, age)
	fmt.Println("Sprintf 拼接：", msg)

	// 方式三：strings.Join（拼接切片）
	words := []string{"apple", "banana", "orange"}
	joined := strings.Join(words, ", ")
	fmt.Println("Join 拼接：", joined)

	// 方式四：strings.Builder（大量拼接推荐，高效）
	var builder strings.Builder
	for i := 0; i < 5; i++ {
		builder.WriteString("hello ")
	}
	fmt.Println("Builder 拼接：", builder.String())

	// -------------------- 字符串比较 --------------------
	fmt.Println("\n========== 字符串比较 ==========")

	fmt.Println(`"abc" == "abc"：`, "abc" == "abc")
	fmt.Println(`"abc" == "def"：`, "abc" == "def")
	fmt.Println(`"abc" < "def"：`, "abc" < "def") // 字典序比较

	// -------------------- 常用字符串函数 --------------------
	fmt.Println("\n========== 常用字符串函数 ==========")

	s := "Hello, World! Hello, Go!"

	// Contains 是否包含
	fmt.Println("包含 'World'：", strings.Contains(s, "World"))
	fmt.Println("包含 'Python'：", strings.Contains(s, "Python"))

	// Count 出现次数
	fmt.Println("'Hello' 出现次数：", strings.Count(s, "Hello"))

	// HasPrefix / HasSuffix 前缀/后缀
	fmt.Println("以 'Hello' 开头：", strings.HasPrefix(s, "Hello"))
	fmt.Println("以 'Go!' 结尾：", strings.HasSuffix(s, "Go!"))

	// Index / LastIndex 查找位置
	fmt.Println("'World' 首次位置：", strings.Index(s, "World"))
	fmt.Println("'Hello' 最后位置：", strings.LastIndex(s, "Hello"))
	fmt.Println("不存在返回 -1：", strings.Index(s, "Python"))

	// -------------------- 大小写转换 --------------------
	fmt.Println("\n========== 大小写转换 ==========")

	lower := "hello world"
	upper := "HELLO WORLD"
	fmt.Println("转大写：", strings.ToUpper(lower))
	fmt.Println("转小写：", strings.ToLower(upper))
	fmt.Println("首字母大写（Title）：", strings.Title("hello world"))

	// -------------------- 去除空白 --------------------
	fmt.Println("\n========== 去除空白 ==========")

	trimStr := "  hello world  "
	fmt.Println("原始：", "[", trimStr, "]")
	fmt.Println("去除两端空格：", "[", strings.TrimSpace(trimStr), "]")
	fmt.Println("去除左侧空格：", "[", strings.TrimLeft(trimStr, " "), "]")
	fmt.Println("去除右侧空格：", "[", strings.TrimRight(trimStr, " "), "]")

	// Trim 去除指定字符
	path := "/usr/local/bin/"
	fmt.Println("去除两端斜杠：", strings.Trim(path, "/"))

	// -------------------- 字符串分割 --------------------
	fmt.Println("\n========== 字符串分割 ==========")

	// Split 分割
	csv := "apple,banana,orange,grape"
	parts := strings.Split(csv, ",")
	fmt.Println("Split 分割：", parts)

	// SplitN 限制分割次数
	parts2 := strings.SplitN("a=b=c=d", "=", 2) // 只分割成2部分
	fmt.Println("SplitN 分割：", parts2)

	// Fields 按空白分割（自动处理多个空格）
	text := "hello   world   go"
	fields := strings.Fields(text)
	fmt.Println("Fields 分割：", fields)

	// -------------------- 字符串替换 --------------------
	fmt.Println("\n========== 字符串替换 ==========")

	s4 := "hello world hello hello"

	// Replace 替换（最后一个参数是替换次数，-1 表示全部）
	replaced := strings.Replace(s4, "hello", "hi", -1)
	fmt.Println("全部替换：", replaced)

	replaced2 := strings.Replace(s4, "hello", "hi", 1)
	fmt.Println("只替换1次：", replaced2)

	// -------------------- 字符串和数字转换 --------------------
	fmt.Println("\n========== 字符串和数字转换 ==========")

	// 字符串转整数
	numStr := "12345"
	num, err := strconv.Atoi(numStr)
	if err != nil {
		fmt.Println("转换失败：", err)
	} else {
		fmt.Println("字符串转整数：", num)
	}

	// 整数转字符串
	num2 := 6789
	str := strconv.Itoa(num2)
	fmt.Println("整数转字符串：", str, "，类型：", fmt.Sprintf("%T", str))

	// 字符串转浮点数
	floatStr := "3.14159"
	f, _ := strconv.ParseFloat(floatStr, 64)
	fmt.Println("字符串转 float64：", f)

	// 浮点数转字符串
	floatNum := 2.71828
	floatStr2 := strconv.FormatFloat(floatNum, 'f', 2, 64) // 保留2位小数
	fmt.Println("浮点数转字符串（2位小数）：", floatStr2)

	// -------------------- Unicode 与 rune --------------------
	fmt.Println("\n========== Unicode 与 rune ==========")

	zh := "你好，Go语言"

	// 按字节遍历（中文会乱）
	fmt.Println("按字节遍历：")
	for i := 0; i < len(zh); i++ {
		fmt.Printf("  %d: %c\n", i, zh[i])
	}

	// 按 rune 遍历（正确处理中文）
	fmt.Println("按 rune 遍历：")
	for i, r := range zh {
		fmt.Printf("  位置%d: %c (Unicode: %U)\n", i, r, r)
	}

	// rune 切片
	runes := []rune(zh)
	fmt.Println("rune 切片长度（字符数）：", len(runes))
	fmt.Println("第一个字符：", string(runes[0]))
	fmt.Println("最后一个字符：", string(runes[len(runes)-1]))

	// 修改字符串（字符串是不可变的，需要转成 rune 切片）
	runes[0] = '您'
	newStr := string(runes)
	fmt.Println("修改后：", newStr)

	// -------------------- 字符串截取（中文安全） --------------------
	fmt.Println("\n========== 字符串截取（中文安全） ==========")

	s5 := "你好，世界Hello"
	runes2 := []rune(s5)

	// 截取前 3 个字符
	if len(runes2) >= 3 {
		fmt.Println("前3个字符：", string(runes2[:3]))
	}

	// 截取第 2 到第 5 个字符
	if len(runes2) >= 5 {
		fmt.Println("第2到5个字符：", string(runes2[1:5]))
	}

	// -------------------- 综合示例：IP 地址验证基础版 --------------------
	fmt.Println("\n========== 综合示例：简单 IP 验证 ==========")

	isValidIP := func(ip string) bool {
		parts := strings.Split(ip, ".")
		if len(parts) != 4 {
			return false
		}
		for _, part := range parts {
			num, err := strconv.Atoi(part)
			if err != nil || num < 0 || num > 255 {
				return false
			}
		}
		return true
	}

	testIPs := []string{"192.168.1.1", "256.1.1.1", "1.2.3", "abc.def.ghi.jkl"}
	for _, ip := range testIPs {
		fmt.Printf("  %s: %v\n", ip, isValidIP(ip))
	}

	fmt.Println("\n========== 示例结束 ==========")
}
