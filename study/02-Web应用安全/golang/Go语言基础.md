# Go 语言基础

## 目录
- [Go 语言简介](#go-语言简介)
- [环境安装](#环境安装)
- [基础语法](#基础语法)
- [控制流](#控制流)
- [函数](#函数)
- [数组与切片](#数组与切片slice)
- [map（字典）](#map字典)
- [字符串操作](#字符串操作)
- [结构体与方法](#结构体与方法)
- [接口](#接口)
- [错误处理](#错误处理)
- [并发](#并发)
- [包管理](#包管理go-mod)
- [网络请求](#网络请求nethttp-客户端)
- [正则表达式](#正则表达式regexp)
- [文件操作](#文件操作)
- [Go 在安全领域的应用](#go-在安全领域的应用)

---

## Go 语言简介

### 什么是 Go 语言
Go（又称 Golang）是 Google 于 2009 年开源的一种静态强类型、编译型、并发型编程语言。Go 语言语法接近 C 语言，但增加了垃圾回收（GC）、内存安全、并发编程等特性。

### Go 语言的特点
- **简洁高效**：语法简洁，编译速度快，执行效率高
- **静态类型 + 垃圾回收**：既有静态语言的性能，又有垃圾回收的便利
- **原生并发支持**：goroutine 和 channel 让并发编程变得简单
- **跨平台编译**：支持交叉编译，一次编写，多平台运行
- **丰富的标准库**：内置大量标准库，涵盖网络、加密、文件处理等
- **部署简单**：编译后生成单个二进制文件，无依赖问题

### 使用场景
- 云原生 / 微服务开发（Docker、Kubernetes 均用 Go 编写）
- 网络编程 / 后端服务
- 命令行工具
- 分布式系统
- 安全工具开发

### Go 和安全的关系
- Go 语言的内存安全特性减少了缓冲区溢出等传统漏洞
- 标准库提供了丰富的加密算法（crypto 包）
- 很多安全工具（如 Nmap 替代品、漏洞扫描器）使用 Go 开发
- 网络安全工具（代理、扫描器、爬虫）开发效率高

---

## 环境安装

### Windows 安装
1. 访问 [Go 官网](https://golang.org/dl/) 下载 Windows 安装包
2. 运行安装程序，默认安装到 `C:\Go`
3. 安装完成后，打开命令行验证：
   ```bash
   go version
   ```

### 环境变量
- `GOROOT`：Go 安装目录（一般无需手动设置）
- `GOPATH`：工作目录，存放 Go 项目代码
- `GOBIN`：编译后的可执行文件存放目录
- `PATH`：添加 `%GOROOT%\bin` 和 `%GOPATH%\bin`

### 常用命令
```bash
go version      # 查看版本
go env          # 查看环境变量
go run main.go  # 直接运行
go build main.go # 编译为可执行文件
go mod init      # 初始化模块
go mod tidy      # 整理依赖
```

---

## 基础语法

### 变量声明
```go
// 方式一：var 声明
var name string = "Go"
var age int

// 方式二：类型推导
var name = "Go"

// 方式三：短变量声明（只能在函数内使用）
name := "Go"
age := 10

// 多变量声明
var a, b, c int
var x, y = 1, "hello"
```

### 常量
```go
const Pi = 3.14159
const (
    StatusOK   = 200
    StatusNotFound = 404
)

// iota 常量生成器
const (
    Sunday = iota // 0
    Monday        // 1
    Tuesday       // 2
)
```

### 数据类型

#### 基本类型
| 类型 | 说明 |
|------|------|
| bool | 布尔值：true/false |
| string | 字符串 |
| int, int8, int16, int32, int64 | 有符号整数 |
| uint, uint8, uint16, uint32, uint64 | 无符号整数 |
| byte | 字节，等价于 uint8 |
| rune | Unicode 字符，等价于 int32 |
| float32, float64 | 浮点数 |
| complex64, complex128 | 复数 |

#### 零值
变量声明后如果没有初始化，会被赋予零值：
- 数值类型：0
- 布尔类型：false
- 字符串：""
- 指针、切片、map、函数：nil

### 运算符

#### 算术运算符
```go
+  加
-  减
*  乘
/  除
%  取余
++ 自增
-- 自减
```

#### 比较运算符
```go
== 等于
!= 不等于
>  大于
<  小于
>= 大于等于
<= 小于等于
```

#### 逻辑运算符
```go
&& 与
|| 或
!  非
```

#### 位运算符
```go
&  按位与
|  按位或
^  按位异或
<< 左移
>> 右移
```

---

## 控制流

### if / else
```go
age := 18
if age >= 18 {
    fmt.Println("成年人")
} else {
    fmt.Println("未成年人")
}

// if 可带初始化语句
if score := 90; score >= 60 {
    fmt.Println("及格")
} else if score >= 80 {
    fmt.Println("良好")
} else {
    fmt.Println("不及格")
}
```

### for 循环
```go
// 基本 for 循环
for i := 0; i < 10; i++ {
    fmt.Println(i)
}

// while 风格
i := 0
for i < 10 {
    fmt.Println(i)
    i++
}

// 无限循环
for {
    // do something
    break
}

// for range 遍历
arr := []int{1, 2, 3}
for index, value := range arr {
    fmt.Println(index, value)
}
```

### switch
```go
day := "Monday"
switch day {
case "Monday":
    fmt.Println("周一")
case "Tuesday":
    fmt.Println("周二")
default:
    fmt.Println("其他")
}

// switch 不带表达式（相当于 if-else 链）
score := 85
switch {
case score >= 90:
    fmt.Println("优秀")
case score >= 80:
    fmt.Println("良好")
default:
    fmt.Println("一般")
}

// fallthrough 穿透
switch 2 {
case 1:
    fmt.Println(1)
case 2:
    fmt.Println(2)
    fallthrough // 继续执行下一个 case
case 3:
    fmt.Println(3)
}
```

---

## 函数

### 函数定义
```go
func add(a int, b int) int {
    return a + b
}

// 参数类型相同可简写
func add(a, b int) int {
    return a + b
}
```

### 多返回值
```go
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("除数不能为0")
    }
    return a / b, nil
}

result, err := divide(10, 3)
```

### 命名返回值
```go
func calc(a, b int) (sum int, diff int) {
    sum = a + b
    diff = a - b
    return // 裸返回，返回命名变量
}
```

### 可变参数
```go
func sum(nums ...int) int {
    total := 0
    for _, n := range nums {
        total += n
    }
    return total
}

sum(1, 2, 3, 4)
```

### 闭包
```go
func counter() func() int {
    count := 0
    return func() int {
        count++
        return count
    }
}

c := counter()
fmt.Println(c()) // 1
fmt.Println(c()) // 2
```

### defer
defer 语句会将函数延迟到外层函数返回之前执行，常用于资源清理。
```go
func readFile(filename string) {
    file, err := os.Open(filename)
    if err != nil {
        return
    }
    defer file.Close() // 函数结束时自动关闭文件
    // 读取文件...
}
```
多个 defer 按后进先出（LIFO）顺序执行。

---

## 数组与切片（slice）

### 数组
```go
// 声明数组
var arr [5]int
arr[0] = 1

// 初始化
arr := [5]int{1, 2, 3, 4, 5}
arr := [...]int{1, 2, 3} // 自动推断长度

// 数组长度是类型的一部分，[3]int 和 [5]int 是不同类型
```

### 切片（slice）
切片是动态数组，长度可变，是 Go 中最常用的数据结构之一。

```go
// 声明切片
var s []int

// 使用 make 创建
s := make([]int, 5)        // 长度5，容量5
s := make([]int, 5, 10)    // 长度5，容量10

// 初始化
s := []int{1, 2, 3, 4, 5}

// 切片操作
s[0] = 10        // 访问元素
len(s)           // 长度
cap(s)           // 容量

// 追加元素
s = append(s, 6)
s = append(s, 7, 8, 9)

// 切片截取
s[1:3]    // 索引1到2
s[:3]     // 前3个
s[2:]     // 从索引2到末尾

// 复制切片
dst := make([]int, len(s))
copy(dst, s)
```

### 切片扩容
当切片容量不足时，append 会自动扩容，通常扩容为原来的 2 倍。

---

## map（字典）

### map 基本操作
```go
// 声明 map
var m map[string]int

// 使用 make 创建
m := make(map[string]int)

// 初始化
m := map[string]int{
    "apple":  5,
    "banana": 3,
}

// 添加/修改
m["orange"] = 7

// 取值
price := m["apple"]

// 判断 key 是否存在
price, ok := m["apple"]
if ok {
    fmt.Println("存在，价格：", price)
} else {
    fmt.Println("不存在")
}

// 删除
delete(m, "banana")

// 遍历
for key, value := range m {
    fmt.Println(key, value)
}

// map 长度
len(m)
```

### 注意事项
- map 是引用类型，传递时传递的是引用
- map 的 key 必须是可比较的类型（不能是 slice、map、function）
- map 是无序的

---

## 字符串操作

### 基本操作
```go
s := "Hello, 世界"

// 长度（字节数）
len(s)

// 字符串连接
s2 := "Go" + "语言"

// 字符串包含
strings.Contains(s, "Hello")

// 前缀/后缀
strings.HasPrefix(s, "Hello")
strings.HasSuffix(s, "界")

// 查找
strings.Index(s, "llo")    // 首次出现位置
strings.LastIndex(s, "l")  // 最后出现位置

// 替换
strings.Replace(s, "l", "L", -1) // -1 表示全部替换

// 分割
strings.Split("a,b,c", ",")

// 大小写转换
strings.ToUpper("hello")
strings.ToLower("HELLO")

// 去除空格
strings.TrimSpace("  hello  ")

// 字符串转数字
strconv.Atoi("123")
strconv.Itoa(123)
```

### rune 与 Unicode
```go
s := "你好，世界"

// 按 rune 遍历（正确处理中文）
for _, r := range s {
    fmt.Printf("%c ", r)
}

// rune 切片
runes := []rune(s)
fmt.Println(len(runes)) // 字符数
```

---

## 结构体与方法

### 结构体定义
```go
type Person struct {
    Name string
    Age  int
    Sex  string
}

// 创建结构体实例
p := Person{Name: "张三", Age: 20, Sex: "男"}
p2 := Person{"李四", 25, "女"} // 按顺序赋值

// 访问字段
p.Name = "王五"
fmt.Println(p.Age)

// 指针
p3 := &Person{Name: "赵六", Age: 30}
p3.Age = 31 // 自动解引用
```

### 方法
方法是作用在特定类型上的函数。
```go
type Person struct {
    Name string
    Age  int
}

// 值接收者（不修改原对象）
func (p Person) SayHello() {
    fmt.Printf("你好，我是%s\n", p.Name)
}

// 指针接收者（可修改原对象）
func (p *Person) Birthday() {
    p.Age++
}

p := Person{Name: "张三", Age: 20}
p.SayHello()   // 你好，我是张三
p.Birthday()   // Age 变为 21
```

### 结构体嵌入
```go
type Student struct {
    Person // 嵌入 Person
    School string
}

s := Student{
    Person: Person{Name: "小明", Age: 15},
    School: "第一中学",
}
s.SayHello() // 可直接调用嵌入类型的方法
```

---

## 接口

### 接口定义
```go
type Writer interface {
    Write(data []byte) (int, error)
}

type Reader interface {
    Read(data []byte) (int, error)
}

// 接口组合
type ReadWriter interface {
    Reader
    Writer
}
```

### 接口实现
Go 中接口是隐式实现的，只要类型实现了接口的所有方法，就自动实现了该接口。
```go
type File struct {
    Name string
}

func (f *File) Write(data []byte) (int, error) {
    fmt.Printf("写入文件 %s: %s\n", f.Name, string(data))
    return len(data), nil
}

// File 自动实现了 Writer 接口
var w Writer = &File{Name: "test.txt"}
w.Write([]byte("hello"))
```

### 空接口
空接口 `interface{}` 可以接收任意类型。
```go
func printAny(v interface{}) {
    fmt.Println(v)
}

printAny(123)
printAny("hello")
printAny(true)
```

### 类型断言
```go
var v interface{} = "hello"

// 类型断言
s, ok := v.(string)
if ok {
    fmt.Println("是字符串：", s)
}

// type switch
switch v := v.(type) {
case int:
    fmt.Println("整数：", v)
case string:
    fmt.Println("字符串：", v)
default:
    fmt.Println("未知类型")
}
```

---

## 错误处理

### error 接口
```go
// errors 包创建错误
import "errors"

err := errors.New("出错了")

// fmt.Errorf 创建带格式的错误
err = fmt.Errorf("错误码：%d", 404)
```

### 错误处理惯例
```go
func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, errors.New("除数不能为0")
    }
    return a / b, nil
}

result, err := divide(10, 0)
if err != nil {
    fmt.Println("错误：", err)
    return
}
fmt.Println("结果：", result)
```

### 自定义错误类型
```go
type MyError struct {
    Code int
    Msg  string
}

func (e *MyError) Error() string {
    return fmt.Sprintf("错误码%d: %s", e.Code, e.Msg)
}

func doSomething() error {
    return &MyError{Code: 500, Msg: "服务器内部错误"}
}
```

### panic 和 recover
```go
// panic 抛出异常（一般用于严重错误）
panic("严重错误")

// recover 捕获 panic
func safeFunc() {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("捕获到 panic:", r)
        }
    }()
    panic("出错了")
}
```

---

## 并发

### goroutine
goroutine 是 Go 中的轻量级线程，由 Go 运行时调度。
```go
func sayHello(name string) {
    fmt.Println("Hello,", name)
}

// 使用 go 关键字启动 goroutine
go sayHello("World")

// 匿名 goroutine
go func(msg string) {
    fmt.Println(msg)
}("hello")
```

### channel
channel 用于 goroutine 之间的通信。
```go
// 创建 channel
ch := make(chan int)

// 无缓冲 channel（同步）
ch := make(chan int)

// 有缓冲 channel（异步）
ch := make(chan int, 10)

// 发送
ch <- 10

// 接收
value := <-ch

// 关闭 channel
close(ch)

// 遍历 channel（直到关闭）
for v := range ch {
    fmt.Println(v)
}
```

### select
select 用于同时监听多个 channel。
```go
ch1 := make(chan int)
ch2 := make(chan string)

select {
case v := <-ch1:
    fmt.Println("从 ch1 收到：", v)
case v := <-ch2:
    fmt.Println("从 ch2 收到：", v)
default:
    fmt.Println("没有数据") // 非阻塞
}
```

### sync 包
```go
// WaitGroup 等待多个 goroutine 完成
var wg sync.WaitGroup
for i := 0; i < 5; i++ {
    wg.Add(1)
    go func(n int) {
        defer wg.Done()
        fmt.Println(n)
    }(i)
}
wg.Wait()

// Mutex 互斥锁
var mu sync.Mutex
var count int

func increment() {
    mu.Lock()
    count++
    mu.Unlock()
}
```

---

## 包管理（go mod）

### 初始化模块
```bash
go mod init example.com/myproject
```

### go.mod 文件
```
module example.com/myproject

go 1.21

require (
    github.com/gin-gonic/gin v1.9.1
)
```

### 常用命令
```bash
go mod init <module-name>    # 初始化模块
go mod tidy                  # 整理依赖（添加需要的，删除不需要的）
go mod download              # 下载依赖到本地缓存
go get <package>             # 添加/更新依赖
go get <package>@version     # 指定版本
go build                      # 编译
go run main.go               # 运行
```

### 导入包
```go
import (
    "fmt"                    // 标准库
    "net/http"               // 标准库
    "github.com/gin-gonic/gin" // 第三方包
)
```

---

## 网络请求（net/http 客户端）

### GET 请求
```go
resp, err := http.Get("https://example.com")
if err != nil {
    // 处理错误
}
defer resp.Body.Close()

body, err := ioutil.ReadAll(resp.Body)
fmt.Println(string(body))
```

### POST 请求
```go
data := url.Values{}
data.Set("username", "admin")
data.Set("password", "123456")

resp, err := http.PostForm("https://example.com/login", data)
```

### 自定义请求
```go
req, err := http.NewRequest("GET", "https://example.com", nil)
if err != nil {
    // 处理错误
}

// 设置请求头
req.Header.Set("User-Agent", "MyBot/1.0")
req.Header.Set("Cookie", "session=abc123")

client := &http.Client{
    Timeout: 10 * time.Second,
}
resp, err := client.Do(req)
```

---

## 正则表达式（regexp）

### 基本用法
```go
import "regexp"

// 编译正则
re := regexp.MustCompile(`\d+`)

// 匹配检测
matched := re.MatchString("abc123def") // true

// 查找第一个匹配
result := re.FindString("abc123def456") // "123"

// 查找所有匹配
results := re.FindAllString("abc123def456", -1) // ["123", "456"]

// 替换
replaced := re.ReplaceAllString("abc123def", "X") // "abcXdef"

// 分组捕获
re = regexp.MustCompile(`(\d{4})-(\d{2})-(\d{2})`)
matches := re.FindStringSubmatch("2024-01-15")
// matches[0] = "2024-01-15"
// matches[1] = "2024"
// matches[2] = "01"
// matches[3] = "15"
```

### 常用正则模式
```go
// 邮箱
`[\w.-]+@[\w-]+\.[\w.-]+`

// IP 地址
`\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}`

// URL
`https?://[\w.-]+(/[\w./?=%&-]*)?`

// 手机号（中国）
`1[3-9]\d{9}`
```

---

## 文件操作

### 读取文件
```go
import (
    "os"
    "bufio"
    "io/ioutil"
)

// 一次性读取全部
data, err := ioutil.ReadFile("test.txt")
fmt.Println(string(data))

// 逐行读取
file, err := os.Open("test.txt")
if err != nil {
    // 处理错误
}
defer file.Close()

scanner := bufio.NewScanner(file)
for scanner.Scan() {
    line := scanner.Text()
    fmt.Println(line)
}
```

### 写入文件
```go
// 一次性写入
err := ioutil.WriteFile("test.txt", []byte("hello world"), 0644)

// 追加写入
file, err := os.OpenFile("test.txt", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
if err != nil {
    // 处理错误
}
defer file.Close()

file.WriteString("追加内容\n")
```

### 文件信息
```go
info, err := os.Stat("test.txt")
if err == nil {
    fmt.Println("文件名：", info.Name())
    fmt.Println("大小：", info.Size())
    fmt.Println("是目录：", info.IsDir())
}

// 判断文件是否存在
if _, err := os.Stat("test.txt"); os.IsNotExist(err) {
    fmt.Println("文件不存在")
}
```

### 目录操作
```go
// 创建目录
os.Mkdir("mydir", 0755)
os.MkdirAll("a/b/c", 0755) // 递归创建

// 读取目录
files, err := ioutil.ReadDir(".")
for _, f := range files {
    fmt.Println(f.Name(), f.IsDir())
}

// 删除
os.Remove("test.txt")
os.RemoveAll("mydir") // 递归删除
```

---

## Go 在安全领域的应用

### 1. 安全扫描器开发
- 端口扫描器
- Web 漏洞扫描器
- 目录爆破工具

### 2. 渗透测试工具
- 密码爆破工具
- SQL 注入测试工具
- XSS 扫描工具

### 3. 网络安全工具
- 代理服务器
- 流量分析工具
- DNS 工具

### 4. 加密与解密
- Go 标准库 crypto 包提供丰富的加密算法
  - AES、DES、RSA
  - SHA-1、SHA-256、MD5
  - HMAC、TLS

### 5. 恶意代码分析
- PE/ELF 文件解析
- 沙箱工具

### 6. 云安全
- 云环境安全扫描
- 容器安全工具

### 安全开发常用库
| 库名 | 用途 |
|------|------|
| `crypto/*` | 各种加密算法 |
| `net/http` | HTTP 客户端/服务端 |
| `net` | 网络编程（TCP/UDP） |
| `encoding/hex` | 十六进制编解码 |
| `encoding/base64` | Base64 编解码 |
| `regexp` | 正则表达式 |
| `bufio` | 缓冲 IO |
| `golang.org/x/crypto` | 扩展加密库 |

---

## 参考资源
- [Go 官方文档](https://golang.org/doc/)
- [Go by Example](https://gobyexample.com/)
- [Go 语言圣经](https://books.studygolang.com/gopl-zh/)
