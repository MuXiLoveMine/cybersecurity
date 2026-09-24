# goroutine_channel

> **分类**：并发
> **说明**：Go 并发编程：goroutine 和 channel

---

## 语法

```golang
go function()  // 启动 goroutine\nch := make(chan type)  // 创建通道
```

## 关键字

go / chan / select / default

## 同步原语

sync.WaitGroup / sync.Mutex / sync.Once / sync.Map

## 示例代码

```golang
package main

import (
    "fmt"
    "sync"
    "time"
)

// 基本 goroutine
func sayHello(name string) {
    fmt.Println("Hello,", name)
}

func main() {
    // 启动 goroutine
    go sayHello("Alice")
    go sayHello("Bob")

    // 等待一下（实际中用 WaitGroup）
    time.Sleep(100 * time.Millisecond)

    // ===== channel =====
    // 创建通道
    ch := make(chan int)

    // 发送数据到通道
    go func() {
        ch <- 42
    }()

    // 从通道接收
    value := <-ch
    fmt.Println(value) // 42

    // 带缓冲的通道
    bufCh := make(chan string, 2)
    bufCh <- "first"
    bufCh <- "second"
    fmt.Println(<-bufCh)
    fmt.Println(<-bufCh)

    // 关闭通道
    close(ch)

    // 遍历通道（通道关闭后自动结束）
    nums := make(chan int, 5)
    go func() {
        for i := 0; i < 5; i++ {
            nums <- i
        }
        close(nums)
    }()

    for n := range nums {
        fmt.Println(n)
    }

    // ===== select =====
    ch1 := make(chan string)
    ch2 := make(chan string)

    go func() {
        time.Sleep(100 * time.Millisecond)
        ch1 <- "from ch1"
    }()

    go func() {
        time.Sleep(200 * time.Millisecond)
        ch2 <- "from ch2"
    }()

    for i := 0; i < 2; i++ {
        select {
        case msg1 := <-ch1:
            fmt.Println("收到:", msg1)
        case msg2 := <-ch2:
            fmt.Println("收到:", msg2)
        case <-time.After(500 * time.Millisecond):
            fmt.Println("超时")
        }
    }

    // ===== WaitGroup =====
    var wg sync.WaitGroup
    for i := 0; i < 5; i++ {
        wg.Add(1)
        go func(n int) {
            defer wg.Done()
            fmt.Println("goroutine", n)
        }(i)
    }
    wg.Wait() // 等待所有 goroutine 完成

    // ===== Mutex =====
    var mu sync.Mutex
    counter := 0
    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            mu.Lock()
            counter++
            mu.Unlock()
        }()
    }
    wg.Wait()
    fmt.Println("counter:", counter) // 1000
}
```
