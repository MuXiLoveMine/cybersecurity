# struct_method_go

> **分类**：结构体与方法
> **说明**：Go 的结构体和方法（面向对象）

---

## 语法

```golang
type StructName struct { field type }\nfunc (receiver Type) methodName() { ... }
```

## 特性

结构体组合（替代继承）/ 方法接收者值或指针 / 接口 / 嵌入

## 示例代码

```golang
package main

import "fmt"

// 结构体定义
type Person struct {
    Name string
    Age  int
    City string
}

// 值接收者方法（不修改原对象）
func (p Person) Greet() string {
    return fmt.Sprintf("Hello, I'm %s, %d years old", p.Name, p.Age)
}

// 指针接收者方法（可以修改原对象）
func (p *Person) Birthday() {
    p.Age++
}

// 结构体嵌套（组合）
type Student struct {
    Person          // 嵌入 Person
    StudentID string
    Major     string
}

// 接口定义
type Speaker interface {
    Speak() string
}

type Dog struct {
    Name string
}

func (d Dog) Speak() string {
    return d.Name + " says woof!"
}

type Cat struct {
    Name string
}

func (c Cat) Speak() string {
    return c.Name + " says meow!"
}

// 空接口（可以接收任何类型）
func printAnything(v interface{}) {
    fmt.Println(v)
}

func main() {
    // 创建结构体
    p := Person{Name: "Alice", Age: 25, City: "Beijing"}
    fmt.Println(p.Name)
    fmt.Println(p.Greet())

    // 指针接收者方法
    p.Birthday()
    fmt.Println(p.Age) // 26

    // 嵌套结构体
    s := Student{
        Person:    Person{Name: "Bob", Age: 20},
        StudentID: "2024001",
        Major:     "Computer Science",
    }
    fmt.Println(s.Name)       // 直接访问嵌入字段
    fmt.Println(s.Greet())    // 继承 Person 的方法

    // 接口
    var speaker Speaker
    speaker = Dog{Name: "Rex"}
    fmt.Println(speaker.Speak())

    speaker = Cat{Name: "Whiskers"}
    fmt.Println(speaker.Speak())

    // 类型断言
    var i interface{} = "hello"
    s, ok := i.(string)
    if ok {
        fmt.Println("字符串:", s)
    }

    // 类型选择
    switch v := i.(type) {
    case int:
        fmt.Println("整数:", v)
    case string:
        fmt.Println("字符串:", v)
    default:
        fmt.Println("其他类型")
    }
}
```
