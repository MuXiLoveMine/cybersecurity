# variable_go

> **分类**：变量与类型
> **说明**：Go 变量声明和基本类型

---

## 语法

```golang
var name type = value  /  name := value (短变量声明)
```

## 基本类型

bool / string / int int8 int16 int32 int64 / uint uint8 uint16 uint32 uint64 / float32 float64 / complex64 complex128 / byte / rune

## 零值

数值: 0 / bool: false / string: "" / 指针/切片/映射/函数/通道/接口: nil

## 示例代码

```golang
package main

import "fmt"

func main() {
    // var 声明
    var name string = "Alice"
    var age int = 25

    // 类型推断
    var city = "Beijing"
    var price = 9.99

    // 短变量声明（只能在函数内）
    count := 100
    flag := true

    // 多变量声明
    var a, b, c int = 1, 2, 3
    x, y := 10, 20

    // 变量块
    var (
        width  int = 100
        height int = 200
        color      = "red"
    )

    // 常量
    const PI = 3.14159
    const MAX_SIZE = 100
    const (
        Monday = 1
        Tuesday = 2
        Sunday = 7
    )

    // iota 枚举
    const (
        Red = iota    // 0
        Green         // 1
        Blue          // 2
    )

    // 类型转换
    var i int = 42
    var f float64 = float64(i)
    var u uint = uint(f)

    // 字符串
    s := "Hello, 世界"
    len(s)              // 长度（字节数）
    len([]rune(s))      // 字符数
    s[0]                // 第0个字节

    // 字符串遍历
    for i, r := range s {
        fmt.Printf("%d: %c\n", i, r)
    }

    // 指针
    value := 42
    ptr := &value
    fmt.Println(*ptr)  // 42
    *ptr = 100
    fmt.Println(value) // 100

    // 类型别名
    type MyInt int
    var num MyInt = 42
}
```
