// ============================================================
// Go 语言基础示例 04：数组和切片（slice）操作
// 运行方式：go run 04_slice.go
// ============================================================

package main

import "fmt"

func main() {
	// -------------------- 数组 --------------------
	fmt.Println("========== 数组 ==========")

	// 声明数组（长度是类型的一部分）
	var arr1 [5]int
	fmt.Println("空数组：", arr1)

	// 数组赋值
	arr1[0] = 10
	arr1[1] = 20
	fmt.Println("赋值后：", arr1)
	fmt.Println("第一个元素：", arr1[0])
	fmt.Println("数组长度：", len(arr1))

	// 初始化数组
	arr2 := [5]int{1, 2, 3, 4, 5}
	fmt.Println("初始化数组：", arr2)

	// 自动推断长度
	arr3 := [...]int{10, 20, 30}
	fmt.Println("自动推断长度：", arr3, "长度：", len(arr3))

	// 二维数组
	var matrix [3][3]int
	matrix[0][0] = 1
	matrix[1][1] = 5
	matrix[2][2] = 9
	fmt.Println("二维数组：")
	for _, row := range matrix {
		fmt.Println("  ", row)
	}

	// 注意：数组是值类型，赋值会复制整个数组
	arr4 := arr2
	arr4[0] = 100
	fmt.Println("原数组 arr2：", arr2)
	fmt.Println("副本 arr4：", arr4)

	// -------------------- 切片基础 --------------------
	fmt.Println("\n========== 切片基础 ==========")

	// 声明切片（零值为 nil）
	var s1 []int
	fmt.Println("nil 切片：", s1)
	fmt.Println("s1 == nil：", s1 == nil)
	fmt.Println("长度：", len(s1), "容量：", cap(s1))

	// 使用 make 创建切片
	// make([]类型, 长度, 容量)
	s2 := make([]int, 5)
	fmt.Println("make 切片（长度5）：", s2)
	fmt.Println("长度：", len(s2), "容量：", cap(s2))

	s3 := make([]int, 3, 10)
	fmt.Println("make 切片（长度3，容量10）：", s3)
	fmt.Println("长度：", len(s3), "容量：", cap(s3))

	// 初始化切片
	s4 := []int{1, 2, 3, 4, 5}
	fmt.Println("初始化切片：", s4)

	// -------------------- 切片操作 --------------------
	fmt.Println("\n========== 切片操作 ==========")

	s := []int{1, 2, 3, 4, 5}
	fmt.Println("原切片：", s)

	// 访问元素
	fmt.Println("第1个元素：", s[0])
	fmt.Println("最后1个元素：", s[len(s)-1])

	// 修改元素
	s[0] = 100
	fmt.Println("修改后：", s)

	// 截取切片（左闭右开）
	fmt.Println("s[1:3] =", s[1:3])  // 索引1到2
	fmt.Println("s[:3] =", s[:3])    // 前3个
	fmt.Println("s[2:] =", s[2:])    // 从索引2到末尾
	fmt.Println("s[:] =", s[:])      // 全部

	// 注意：截取后的切片和原切片共享底层数组
	sub := s[1:3]
	sub[0] = 999
	fmt.Println("修改子切片后，原切片：", s)

	// -------------------- append --------------------
	fmt.Println("\n========== append ==========")

	s5 := []int{1, 2, 3}
	fmt.Println("append 前：", s5, "len:", len(s5), "cap:", cap(s5))

	// 追加一个元素
	s5 = append(s5, 4)
	fmt.Println("append 4 后：", s5, "len:", len(s5), "cap:", cap(s5))

	// 追加多个元素
	s5 = append(s5, 5, 6, 7)
	fmt.Println("append 多个后：", s5, "len:", len(s5), "cap:", cap(s5))

	// 追加另一个切片（用 ... 展开）
	s6 := []int{10, 20, 30}
	s5 = append(s5, s6...)
	fmt.Println("append 切片后：", s5)

	// -------------------- copy --------------------
	fmt.Println("\n========== copy ==========")

	src := []int{1, 2, 3, 4, 5}
	dst := make([]int, 3) // 目标切片长度为3

	n := copy(dst, src) // 返回复制的元素个数
	fmt.Println("源切片：", src)
	fmt.Println("目标切片：", dst)
	fmt.Println("复制了", n, "个元素")

	// 完整复制
	dst2 := make([]int, len(src))
	copy(dst2, src)
	dst2[0] = 999
	fmt.Println("完整复制后修改 dst2：", dst2)
	fmt.Println("原切片不受影响：", src)

	// -------------------- 切片扩容机制 --------------------
	fmt.Println("\n========== 切片扩容机制 ==========")

	var s7 []int
	fmt.Println("初始：", s7, "len:", len(s7), "cap:", cap(s7))

	for i := 0; i < 10; i++ {
		s7 = append(s7, i)
		fmt.Printf("append %d 后：len=%d, cap=%d\n", i, len(s7), cap(s7))
	}

	// -------------------- 删除元素 --------------------
	fmt.Println("\n========== 删除元素 ==========")

	s8 := []int{1, 2, 3, 4, 5}
	fmt.Println("原切片：", s8)

	// 删除索引为 2 的元素（值为 3）
	index := 2
	s8 = append(s8[:index], s8[index+1:]...)
	fmt.Println("删除索引2后：", s8)

	// 删除第一个元素
	s8 = s8[1:]
	fmt.Println("删除第一个后：", s8)

	// 删除最后一个元素
	s8 = s8[:len(s8)-1]
	fmt.Println("删除最后一个后：", s8)

	// -------------------- 插入元素 --------------------
	fmt.Println("\n========== 插入元素 ==========")

	s9 := []int{1, 2, 3, 4, 5}
	fmt.Println("原切片：", s9)

	// 在索引 2 处插入 100
	insertIdx := 2
	s9 = append(s9[:insertIdx], append([]int{100}, s9[insertIdx:]...)...)
	fmt.Println("插入后：", s9)

	// -------------------- 遍历切片 --------------------
	fmt.Println("\n========== 遍历切片 ==========")

	fruits := []string{"apple", "banana", "orange", "grape"}

	// 方式一：for i 遍历
	fmt.Println("for i 遍历：")
	for i := 0; i < len(fruits); i++ {
		fmt.Printf("  %d: %s\n", i, fruits[i])
	}

	// 方式二：for range 遍历（推荐）
	fmt.Println("for range 遍历：")
	for idx, fruit := range fruits {
		fmt.Printf("  %d: %s\n", idx, fruit)
	}

	// -------------------- 切片的应用：栈和队列 --------------------
	fmt.Println("\n========== 栈和队列 ==========")

	// 栈（后进先出）
	var stack []int
	stack = append(stack, 1) // push
	stack = append(stack, 2)
	stack = append(stack, 3)
	fmt.Println("栈：", stack)

	// pop
	top := stack[len(stack)-1]
	stack = stack[:len(stack)-1]
	fmt.Println("弹出栈顶：", top, "剩余：", stack)

	// 队列（先进先出）
	var queue []int
	queue = append(queue, 1) // enqueue
	queue = append(queue, 2)
	queue = append(queue, 3)
	fmt.Println("队列：", queue)

	// dequeue
	front := queue[0]
	queue = queue[1:]
	fmt.Println("出队：", front, "剩余：", queue)

	fmt.Println("\n========== 示例结束 ==========")
}
