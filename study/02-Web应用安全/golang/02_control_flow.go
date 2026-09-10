// ============================================================
// Go 语言基础示例 02：控制流（if/else、for、switch）
// 运行方式：go run 02_control_flow.go
// ============================================================

package main

import "fmt"

func main() {
	// -------------------- if / else --------------------
	fmt.Println("========== if / else ==========")

	age := 18
	if age >= 18 {
		fmt.Println("你是成年人")
	} else {
		fmt.Println("你是未成年人")
	}

	// if 带初始化语句（score 只在 if 作用域内有效）
	if score := 85; score >= 90 {
		fmt.Println("优秀")
	} else if score >= 80 {
		fmt.Println("良好")
	} else if score >= 60 {
		fmt.Println("及格")
	} else {
		fmt.Println("不及格")
	}

	// 多条件判断
	isVIP := true
	money := 100
	if isVIP && money > 50 {
		fmt.Println("VIP 用户，可以购买")
	}

	// -------------------- for 循环 --------------------
	fmt.Println("\n========== for 循环 ==========")

	// 基本 for 循环（类 C 风格）
	fmt.Println("基本 for 循环：")
	for i := 0; i < 5; i++ {
		fmt.Printf("  i = %d\n", i)
	}

	// while 风格（Go 没有 while 关键字，用 for 实现）
	fmt.Println("while 风格：")
	j := 0
	for j < 3 {
		fmt.Printf("  j = %d\n", j)
		j++
	}

	// 无限循环
	fmt.Println("无限循环（用 break 退出）：")
	k := 0
	for {
		if k >= 2 {
			break
		}
		fmt.Printf("  k = %d\n", k)
		k++
	}

	// continue 跳过本次循环
	fmt.Println("continue 跳过偶数：")
	for i := 0; i < 10; i++ {
		if i%2 == 0 {
			continue
		}
		fmt.Printf("  %d ", i)
	}
	fmt.Println()

	// -------------------- for range 遍历 --------------------
	fmt.Println("\n========== for range 遍历 ==========")

	// 遍历数组/切片
	arr := []string{"a", "b", "c"}
	fmt.Println("遍历切片：")
	for index, value := range arr {
		fmt.Printf("  索引 %d: %s\n", index, value)
	}

	// 只需要值，用 _ 忽略索引
	fmt.Println("只取 value：")
	for _, v := range arr {
		fmt.Printf("  %s ", v)
	}
	fmt.Println()

	// 遍历字符串（正确处理中文）
	fmt.Println("遍历字符串：")
	s := "你好Go"
	for i, r := range s {
		fmt.Printf("  位置 %d: %c\n", i, r)
	}

	// 遍历 map
	m := map[string]int{"apple": 5, "banana": 3}
	fmt.Println("遍历 map：")
	for key, value := range m {
		fmt.Printf("  %s: %d\n", key, value)
	}

	// -------------------- switch 语句 --------------------
	fmt.Println("\n========== switch 语句 ==========")

	// 基本 switch
	day := "Monday"
	switch day {
	case "Monday":
		fmt.Println("星期一")
	case "Tuesday":
		fmt.Println("星期二")
	case "Wednesday":
		fmt.Println("星期三")
	default:
		fmt.Println("其他")
	}

	// 一个 case 匹配多个值
	num := 5
	switch num {
	case 1, 3, 5, 7, 9:
		fmt.Println("奇数")
	case 2, 4, 6, 8, 10:
		fmt.Println("偶数")
	}

	// switch 不带表达式（相当于 if-else 链）
	score := 75
	switch {
	case score >= 90:
		fmt.Println("A 级")
	case score >= 80:
		fmt.Println("B 级")
	case score >= 70:
		fmt.Println("C 级")
	case score >= 60:
		fmt.Println("D 级")
	default:
		fmt.Println("F 级")
	}

	// fallthrough 穿透（继续执行下一个 case）
	fmt.Println("fallthrough 演示：")
	switch 2 {
	case 1:
		fmt.Println("  case 1")
	case 2:
		fmt.Println("  case 2")
		fallthrough // 继续执行下一个 case
	case 3:
		fmt.Println("  case 3")
		fallthrough
	case 4:
		fmt.Println("  case 4")
	}

	// -------------------- 综合练习：打印九九乘法表 --------------------
	fmt.Println("\n========== 九九乘法表 ==========")
	for i := 1; i <= 9; i++ {
		for j := 1; j <= i; j++ {
			fmt.Printf("%d*%d=%d\t", j, i, i*j)
		}
		fmt.Println()
	}

	// -------------------- 综合练习：冒泡排序 --------------------
	fmt.Println("\n========== 冒泡排序 ==========")
	nums := []int{5, 2, 8, 1, 9, 3}
	fmt.Println("排序前：", nums)

	for i := 0; i < len(nums)-1; i++ {
		for j := 0; j < len(nums)-1-i; j++ {
			if nums[j] > nums[j+1] {
				nums[j], nums[j+1] = nums[j+1], nums[j] // Go 支持直接交换
			}
		}
	}
	fmt.Println("排序后：", nums)

	fmt.Println("\n========== 示例结束 ==========")
}
