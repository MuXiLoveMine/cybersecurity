# func_go

> **分类**：函数
> **说明**：Go 函数定义和特性

---

## 语法

```golang
func functionName(param1 type1, param2 type2) returnType { ... }
```

## 特性

多返回值 / 命名返回值 / 可变参数 / 匿名函数 / 闭包 / defer / 函数作为值

## 示例代码

```golang
package main

import "fmt"

// 基本函数
func add(a int, b int) int {
    return a + b
}

// 参数类型相同时可以合并
func multiply(a, b int) int {
    return a * b
}

// 多返回值
func divide(a, b int) (int, error) {
    if b == 0 {
        return 0, fmt.Errorf("不能除以零")
    }
    return a / b, nil
}

// 命名返回值
func rectangle(width, height int) (area int, perimeter int) {
    area = width * height
    perimeter = 2 * (width + height)
    return // 自动返回命名的返回值
}

// 可变参数
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}

// defer 延迟执行（函数返回前执行）
func readFile(filename string) error {
    file, err := os.Open(filename)
    if err != nil {
        return err
    }
    defer file.Close() // 函数返回前关闭文件
    // ... 读取文件
    return nil
}

// 匿名函数
func main() {
    // 立即执行的匿名函数
    func(msg string) {
        fmt.Println(msg)
    }("Hello")

    // 函数赋值给变量
    greet := func(name string) string {
        return "Hello, " + name
    }
    fmt.Println(greet("Alice"))

    // 闭包
    counter := func() func() int {
        count := 0
        return func() int {
            count++
            return count
        }
    }()

    fmt.Println(counter()) // 1
    fmt.Println(counter()) // 2
    fmt.Println(counter()) // 3

    // 函数作为参数
    nums := []int{1, 2, 3, 4, 5}
    result := filter(nums, func(n int) bool {
        return n%2 == 0
    })
    fmt.Println(result)
}

// 函数作为参数
func filter(nums []int, predicate func(int) bool) []int {
    var result []int
    for _, n := range nums {
        if predicate(n) {
            result = append(result, n)
        }
    }
    return result
}

// 递归函数
func factorial(n int) int {
    if n <= 1 {
        return 1
    }
    return n * factorial(n-1)
}
```
