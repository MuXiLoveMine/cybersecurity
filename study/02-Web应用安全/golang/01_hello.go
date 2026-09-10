// ============================================================
// Go 语言基础示例 01：Hello World、变量、数据类型
// 运行方式：go run 01_hello.go
// ============================================================

package main

import "fmt"

// main 函数是程序的入口
func main() {
	// -------------------- Hello World --------------------
	fmt.Println("========== Hello World ==========")
	fmt.Println("Hello, Go!") // 输出 Hello, Go!

	// -------------------- 变量声明 --------------------
	fmt.Println("\n========== 变量声明 ==========")

	// 方式一：var 声明，指定类型
	var name string = "张三"
	var age int = 20
	fmt.Println("姓名：", name)
	fmt.Println("年龄：", age)

	// 方式二：var 声明，类型推导
	var score = 95.5 // 自动推导为 float64
	fmt.Println("分数：", score)

	// 方式三：短变量声明（最常用，只能在函数内使用）
	city := "北京"
	isStudent := true
	fmt.Println("城市：", city)
	fmt.Println("是学生：", isStudent)

	// 多变量声明
	var a, b, c int = 1, 2, 3
	fmt.Println("a, b, c =", a, b, c)

	x, y := 10, "hello"
	fmt.Println("x =", x, ", y =", y)

	// -------------------- 常量 --------------------
	fmt.Println("\n========== 常量 ==========")

	const Pi = 3.14159
	const AppName = "安全工具"
	fmt.Println("Pi =", Pi)
	fmt.Println("应用名：", AppName)

	// 常量组
	const (
		StatusOK       = 200
		StatusNotFound = 404
		StatusError    = 500
	)
	fmt.Println("状态码：", StatusOK, StatusNotFound, StatusError)

	// iota 常量生成器
	const (
		Sunday = iota // 0
		Monday        // 1
		Tuesday       // 2
		Wednesday     // 3
	)
	fmt.Println("星期：", Sunday, Monday, Tuesday, Wednesday)

	// -------------------- 基本数据类型 --------------------
	fmt.Println("\n========== 基本数据类型 ==========")

	// 布尔类型
	var isTrue bool = true
	var isFalse bool = false
	fmt.Println("布尔：", isTrue, isFalse)

	// 整数类型
	var i int = 100
	var ui uint = 200
	var by byte = 255 // byte 等价于 uint8
	fmt.Println("整数：", i, ui, by)

	// 浮点数
	var f32 float32 = 3.14
	var f64 float64 = 2.71828
	fmt.Println("浮点数：", f32, f64)

	// 字符串
	var s string = "Hello, 世界"
	fmt.Println("字符串：", s)
	fmt.Println("字符串长度（字节）：", len(s))

	// rune（Unicode 字符）
	var r rune = '中'
	fmt.Printf("rune: %c, 编码: %d\n", r, r)

	// -------------------- 零值 --------------------
	fmt.Println("\n========== 零值 ==========")

	var zeroInt int
	var zeroFloat float64
	var zeroBool bool
	var zeroString string
	fmt.Println("int 零值：", zeroInt)
	fmt.Println("float 零值：", zeroFloat)
	fmt.Println("bool 零值：", zeroBool)
	fmt.Println("string 零值：", zeroString)

	// -------------------- 类型转换 --------------------
	fmt.Println("\n========== 类型转换 ==========")

	var num1 int = 10
	var num2 float64 = float64(num1) // int 转 float64
	fmt.Println("int 转 float64：", num2)

	var num3 float64 = 3.14
	var num4 int = int(num3) // float64 转 int（截断小数）
	fmt.Println("float64 转 int：", num4)

	// -------------------- 运算符 --------------------
	fmt.Println("\n========== 运算符 ==========")

	// 算术运算符
	m, n := 10, 3
	fmt.Println("加法：", m+n)
	fmt.Println("减法：", m-n)
	fmt.Println("乘法：", m*n)
	fmt.Println("除法：", m/n)
	fmt.Println("取余：", m%n)

	// 自增自减
	cnt := 0
	cnt++
	fmt.Println("自增后：", cnt)
	cnt--
	fmt.Println("自减后：", cnt)

	// 比较运算符
	fmt.Println("10 > 3：", 10 > 3)
	fmt.Println("10 == 10：", 10 == 10)
	fmt.Println("10 != 3：", 10 != 3)

	// 逻辑运算符
	fmt.Println("true && false：", true && false)
	fmt.Println("true || false：", true || false)
	fmt.Println("!true：", !true)

	// 位运算符
	fmt.Println("5 & 3 =", 5&3)   // 101 & 011 = 001 = 1
	fmt.Println("5 | 3 =", 5|3)   // 101 | 011 = 111 = 7
	fmt.Println("5 ^ 3 =", 5^3)   // 101 ^ 011 = 110 = 6
	fmt.Println("5 << 1 =", 5<<1) // 左移1位 = 10
	fmt.Println("5 >> 1 =", 5>>1) // 右移1位 = 2

	fmt.Println("\n========== 示例结束 ==========")
}
