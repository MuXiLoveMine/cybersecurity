// ============================================================
// Go 语言基础示例 05：map（字典）操作
// 运行方式：go run 05_map.go
// ============================================================

package main

import "fmt"

func main() {
	// -------------------- map 基础 --------------------
	fmt.Println("========== map 基础 ==========")

	// 声明 map（零值为 nil）
	var m1 map[string]int
	fmt.Println("nil map：", m1)
	fmt.Println("m1 == nil：", m1 == nil)

	// 使用 make 创建 map
	// make(map[键类型]值类型)
	m2 := make(map[string]int)
	fmt.Println("make 创建的 map：", m2)

	// 初始化 map
	m3 := map[string]int{
		"apple":  5,
		"banana": 3,
		"orange": 7,
	}
	fmt.Println("初始化 map：", m3)

	// -------------------- 添加和修改 --------------------
	fmt.Println("\n========== 添加和修改 ==========")

	fruits := make(map[string]int)
	fmt.Println("空 map：", fruits)

	// 添加键值对
	fruits["apple"] = 5
	fruits["banana"] = 3
	fmt.Println("添加后：", fruits)

	// 修改值
	fruits["apple"] = 10
	fmt.Println("修改 apple 后：", fruits)

	// -------------------- 取值和判断存在性 --------------------
	fmt.Println("\n========== 取值和判断存在性 ==========")

	prices := map[string]float64{
		"apple":  5.5,
		"banana": 3.2,
		"grape":  12.8,
	}

	// 直接取值（如果 key 不存在，返回值类型的零值）
	price1 := prices["apple"]
	fmt.Println("apple 价格：", price1)

	price2 := prices["orange"] // 不存在，返回 0
	fmt.Println("orange 价格（不存在）：", price2)

	// 判断 key 是否存在（推荐方式）
	price, ok := prices["apple"]
	if ok {
		fmt.Println("apple 存在，价格：", price)
	} else {
		fmt.Println("apple 不存在")
	}

	price, ok = prices["orange"]
	if ok {
		fmt.Println("orange 存在，价格：", price)
	} else {
		fmt.Println("orange 不存在")
	}

	// -------------------- 删除 --------------------
	fmt.Println("\n========== 删除 ==========")

	scores := map[string]int{
		"张三": 90,
		"李四": 85,
		"王五": 95,
	}
	fmt.Println("删除前：", scores)

	// 删除键值对
	delete(scores, "李四")
	fmt.Println("删除李四后：", scores)

	// 删除不存在的 key 不会报错
	delete(scores, "赵六")
	fmt.Println("删除不存在的赵六后：", scores)

	// -------------------- 长度 --------------------
	fmt.Println("\n========== 长度 ==========")
	fmt.Println("scores 长度：", len(scores))

	// -------------------- 遍历 map --------------------
	fmt.Println("\n========== 遍历 map ==========")

	capitals := map[string]string{
		"中国":   "北京",
		"美国":   "华盛顿",
		"英国":   "伦敦",
		"法国":   "巴黎",
		"日本":   "东京",
	}

	// 遍历 key 和 value
	fmt.Println("遍历所有键值对：")
	for country, capital := range capitals {
		fmt.Printf("  %s 的首都是 %s\n", country, capital)
	}

	// 只遍历 key
	fmt.Println("遍历所有 key：")
	for country := range capitals {
		fmt.Println("  ", country)
	}

	// 只遍历 value（用 _ 忽略 key）
	fmt.Println("遍历所有 value：")
	for _, capital := range capitals {
		fmt.Println("  ", capital)
	}

	// 注意：map 的遍历顺序是不确定的

	// -------------------- map 作为函数参数 --------------------
	fmt.Println("\n========== map 作为函数参数 ==========")

	// map 是引用类型，函数内修改会影响原 map
	incrementAll := func(m map[string]int, delta int) {
		for k := range m {
			m[k] += delta
		}
	}

	points := map[string]int{"a": 1, "b": 2, "c": 3}
	fmt.Println("调用前：", points)
	incrementAll(points, 10)
	fmt.Println("调用后：", points)

	// -------------------- 复杂 map 结构 --------------------
	fmt.Println("\n========== 复杂 map 结构 ==========")

	// map 的 value 可以是切片
	students := map[string][]string{
		"一班": {"张三", "李四", "王五"},
		"二班": {"赵六", "钱七"},
	}
	fmt.Println("一班学生：", students["一班"])
	fmt.Println("二班学生数：", len(students["二班"]))

	// 嵌套 map
	userRoles := map[string]map[string]bool{
		"admin": {
			"read":  true,
			"write": true,
			"delete": true,
		},
		"user": {
			"read":  true,
			"write": false,
			"delete": false,
		},
	}
	fmt.Println("admin 的 delete 权限：", userRoles["admin"]["delete"])
	fmt.Println("user 的 write 权限：", userRoles["user"]["write"])

	// -------------------- 统计词频 --------------------
	fmt.Println("\n========== 应用：统计词频 ==========")

	text := []string{"apple", "banana", "apple", "orange", "banana", "apple"}
	freq := make(map[string]int)

	for _, word := range text {
		freq[word]++
	}

	fmt.Println("词频统计：")
	for word, count := range freq {
		fmt.Printf("  %s: %d 次\n", word, count)
	}

	// -------------------- map 的 key 限制 --------------------
	fmt.Println("\n========== map 的 key 限制 ==========")

	// map 的 key 必须是可比较的类型
	// 可以用：int、string、bool、结构体（字段都是可比较的）
	// 不可以用：slice、map、function

	// 结构体作为 key
	type Point struct {
		X, Y int
	}
	pointMap := make(map[Point]string)
	pointMap[Point{0, 0}] = "原点"
	pointMap[Point{1, 1}] = "(1,1)"
	fmt.Println("原点坐标对应：", pointMap[Point{0, 0}])

	fmt.Println("\n========== 示例结束 ==========")
}
