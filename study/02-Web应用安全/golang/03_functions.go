// ============================================================
// Go 语言基础示例 03：函数、多返回值、闭包、defer
// 运行方式：go run 03_functions.go
// ============================================================

package main

import (
	"errors"
	"fmt"
)

// -------------------- 基本函数 --------------------

// add 计算两个整数的和
// 函数定义：func 函数名(参数列表) 返回值类型 { ... }
func add(a int, b int) int {
	return a + b
}

// 参数类型相同时可以简写
func add3(a, b, c int) int {
	return a + b + c
}

// -------------------- 多返回值 --------------------

// divide 除法运算，返回结果和错误
// Go 中函数可以返回多个值，常用于返回 (结果, error)
func divide(a, b float64) (float64, error) {
	if b == 0 {
		return 0, errors.New("除数不能为0")
	}
	return a / b, nil
}

// swap 交换两个值
func swap(a, b string) (string, string) {
	return b, a
}

// -------------------- 命名返回值 --------------------

// calc 计算两个数的和与差
// 命名返回值可以直接使用 return（裸返回）
func calc(a, b int) (sum int, diff int) {
	sum = a + b
	diff = a - b
	return // 裸返回，返回 sum 和 diff
}

// -------------------- 可变参数 --------------------

// sum 计算多个整数的和
// nums ...int 表示可以接收任意数量的 int 参数
func sum(nums ...int) int {
	total := 0
	for _, n := range nums {
		total += n
	}
	return total
}

// -------------------- 函数作为参数 --------------------

// apply 对数组中每个元素应用一个函数
func apply(nums []int, f func(int) int) []int {
	result := make([]int, len(nums))
	for i, n := range nums {
		result[i] = f(n)
	}
	return result
}

// -------------------- 闭包 --------------------

// counter 返回一个计数器函数
// 闭包可以捕获外层函数的变量
func counter() func() int {
	count := 0
	return func() int {
		count++ // 引用了外层的 count 变量
		return count
	}
}

// makeSuffix 返回一个添加后缀的函数
func makeSuffix(suffix string) func(string) string {
	return func(name string) string {
		return name + suffix
	}
}

// -------------------- defer 演示函数 --------------------

// deferDemo 演示 defer 的使用
func deferDemo() {
	fmt.Println("函数开始")

	// defer 语句会延迟到函数返回前执行
	// 多个 defer 按后进先出（LIFO）顺序执行
	defer fmt.Println("defer 1")
	defer fmt.Println("defer 2")
	defer fmt.Println("defer 3")

	fmt.Println("函数中间")
	fmt.Println("函数结束")
}

// fileDemo 模拟文件操作中 defer 的使用
func fileDemo() {
	fmt.Println("\n--- defer 模拟文件操作 ---")
	fmt.Println("打开文件")
	defer fmt.Println("关闭文件") // 函数结束时自动关闭

	fmt.Println("读取文件内容")
	fmt.Println("处理文件内容")
	// 即使中间出错，defer 也会执行
}

// -------------------- 递归函数 --------------------

// factorial 计算阶乘（递归）
func factorial(n int) int {
	if n <= 1 {
		return 1
	}
	return n * factorial(n-1)
}

// fibonacci 斐波那契数列（递归）
func fibonacci(n int) int {
	if n <= 1 {
		return n
	}
	return fibonacci(n-1) + fibonacci(n-2)
}

// -------------------- 主函数 --------------------

func main() {
	// -------------------- 基本函数调用 --------------------
	fmt.Println("========== 基本函数 ==========")
	fmt.Println("add(3, 5) =", add(3, 5))
	fmt.Println("add3(1, 2, 3) =", add3(1, 2, 3))

	// -------------------- 多返回值 --------------------
	fmt.Println("\n========== 多返回值 ==========")

	result, err := divide(10, 3)
	if err != nil {
		fmt.Println("错误：", err)
	} else {
		fmt.Println("10 / 3 =", result)
	}

	result, err = divide(10, 0)
	if err != nil {
		fmt.Println("错误：", err)
	}

	// 交换两个值
	x, y := swap("hello", "world")
	fmt.Println("swap 结果：", x, y)

	// 忽略某个返回值（用 _）
	_, diff := calc(10, 3)
	fmt.Println("只取差值：", diff)

	// -------------------- 命名返回值 --------------------
	fmt.Println("\n========== 命名返回值 ==========")
	sumVal, diffVal := calc(10, 3)
	fmt.Println("和：", sumVal, "，差：", diffVal)

	// -------------------- 可变参数 --------------------
	fmt.Println("\n========== 可变参数 ==========")
	fmt.Println("sum(1, 2) =", sum(1, 2))
	fmt.Println("sum(1, 2, 3) =", sum(1, 2, 3))
	fmt.Println("sum(1, 2, 3, 4, 5) =", sum(1, 2, 3, 4, 5))

	// 将切片展开作为参数
	nums := []int{10, 20, 30}
	fmt.Println("sum 切片展开：", sum(nums...))

	// -------------------- 函数作为参数 --------------------
	fmt.Println("\n========== 函数作为参数 ==========")

	// 定义一个加倍函数
	double := func(n int) int {
		return n * 2
	}

	arr := []int{1, 2, 3, 4, 5}
	doubled := apply(arr, double)
	fmt.Println("原数组：", arr)
	fmt.Println("加倍后：", doubled)

	// 直接传入匿名函数
	squared := apply(arr, func(n int) int {
		return n * n
	})
	fmt.Println("平方后：", squared)

	// -------------------- 闭包 --------------------
	fmt.Println("\n========== 闭包 ==========")

	// 计数器示例
	c1 := counter()
	fmt.Println("c1 计数器：")
	fmt.Println("  第1次：", c1()) // 1
	fmt.Println("  第2次：", c1()) // 2
	fmt.Println("  第3次：", c1()) // 3

	// 每个闭包有独立的环境
	c2 := counter()
	fmt.Println("c2 计数器（独立）：")
	fmt.Println("  第1次：", c2()) // 1

	// 添加后缀示例
	addJpg := makeSuffix(".jpg")
	addPng := makeSuffix(".png")
	fmt.Println("添加 jpg 后缀：", addJpg("photo"))
	fmt.Println("添加 png 后缀：", addPng("image"))

	// -------------------- defer --------------------
	fmt.Println("\n========== defer ==========")
	deferDemo()

	// 文件操作示例
	fileDemo()

	// -------------------- 递归 --------------------
	fmt.Println("\n========== 递归 ==========")
	fmt.Println("5的阶乘：", factorial(5))

	fmt.Print("斐波那契数列前10项：")
	for i := 0; i < 10; i++ {
		fmt.Printf("%d ", fibonacci(i))
	}
	fmt.Println()

	fmt.Println("\n========== 示例结束 ==========")
}
