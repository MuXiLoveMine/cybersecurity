# if_go

> **分类**：条件与循环
> **说明**：Go 的条件判断和循环

---

## 语法

```golang
if condition { ... } else if cond { ... } else { ... }\nfor init; condition; post { ... }
```

## 特点

if 条件可以包含简短声明语句\nGo 只有 for 一种循环，但形式多样\nswitch 不需要 break，默认不穿透

## 示例代码

```golang
package main

import "fmt"

func main() {
    // if/else
    age := 18
    if age >= 18 {
        fmt.Println("成年")
    } else if age >= 6 {
        fmt.Println("少年")
    } else {
        fmt.Println("儿童")
    }

    // if 带简短声明
    if n := len("hello"); n > 3 {
        fmt.Println("字符串长度大于3:", n)
    }

    // 简单 for 循环
    for i := 0; i < 5; i++ {
        fmt.Println(i)
    }

    // while 风格（Go 没有 while）
    count := 0
    for count < 5 {
        fmt.Println(count)
        count++
    }

    // 死循环
    // for {
    //     fmt.Println("无限循环")
    // }

    // for-range 遍历数组/切片/映射/字符串
    nums := []int{1, 2, 3, 4, 5}
    for i, v := range nums {
        fmt.Printf("索引: %d, 值: %d\n", i, v)
    }

    // 只需要值
    for _, v := range nums {
        fmt.Println(v)
    }

    // 遍历 map
    m := map[string]int{"a": 1, "b": 2}
    for k, v := range m {
        fmt.Println(k, v)
    }

    // switch（不需要 break）
    day := "Monday"
    switch day {
    case "Monday":
        fmt.Println("星期一")
    case "Tuesday":
        fmt.Println("星期二")
    default:
        fmt.Println("其他")
    }

    // switch 多条件
    switch day {
    case "Monday", "Tuesday", "Wednesday", "Thursday", "Friday":
        fmt.Println("工作日")
    case "Saturday", "Sunday":
        fmt.Println("周末")
    }

    // switch 无表达式（类似 if/else）
    score := 85
    switch {
    case score >= 90:
        fmt.Println("优秀")
    case score >= 60:
        fmt.Println("及格")
    default:
        fmt.Println("不及格")
    }

    // break 和 continue
    for i := 0; i < 10; i++ {
        if i == 3 {
            continue // 跳过3
        }
        if i == 7 {
            break // 到7停止
        }
        fmt.Println(i)
    }

    // 标签（跳出外层循环）
outer:
    for i := 0; i < 3; i++ {
        for j := 0; j < 3; j++ {
            if i == 1 && j == 1 {
                break outer
            }
            fmt.Println(i, j)
        }
    }
}
```
