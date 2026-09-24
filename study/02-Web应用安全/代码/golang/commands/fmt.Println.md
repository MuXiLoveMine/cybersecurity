# fmt.Println

> **分类**：输出
> **说明**：格式化输出到标准输出并换行

---

## 语法

```golang
fmt.Println(a ...interface{}) (n int, err error)
```

## 常用函数

fmt.Print / fmt.Println / fmt.Printf / fmt.Sprintf / fmt.Fprintf / fmt.Scanf

## 格式化动词

%v 值 / %T 类型 / %d 整数 / %f 浮点数 / %s 字符串 / %p 指针 / %t 布尔

## 示例代码

```golang
package main

import "fmt"

func main() {
    // 基本输出
    fmt.Println("Hello, World!")
    fmt.Println(42)
    fmt.Println(3.14, "abc", true)

    // 不换行
    fmt.Print("输入: ")

    // 格式化输出
    name := "Alice"
    age := 25
    fmt.Printf("姓名: %s, 年龄: %d\n", name, age)
    fmt.Printf("浮点数: %.2f\n", 3.14159)

    // 格式化动词
    fmt.Printf("值: %v\n", name)      // Alice
    fmt.Printf("类型: %T\n", name)    // string
    fmt.Printf("指针: %p\n", &name)   // 内存地址
    fmt.Printf("布尔: %t\n", true)    // true
    fmt.Printf("十六进制: %x\n", 255) // ff

    // 错误输出
    fmt.Fprintln(os.Stderr, "错误信息")

    // 格式化到字符串
    s := fmt.Sprintf("姓名: %s, 年龄: %d", name, age)
    fmt.Println(s)

    // 读取输入
    var input string
    fmt.Scanln(&input)
    fmt.Println("你输入了:", input)

    // 结构体输出
    type Person struct {
        Name string
        Age  int
    }
    p := Person{"Bob", 30}
    fmt.Printf("%v\n", p)   // {Bob 30}
    fmt.Printf("%+v\n", p)  // {Name:Bob Age:30}
    fmt.Printf("%#v\n", p)  // main.Person{Name:"Bob", Age:30}
}
```
