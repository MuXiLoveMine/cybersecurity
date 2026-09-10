// ============================================================
// Go 语言基础示例 08：HTTP 网络请求（net/http）
// 运行方式：go run 08_http.go
// ============================================================

package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
	"strings"
	"time"
)

func main() {
	// -------------------- GET 请求 --------------------
	fmt.Println("========== GET 请求 ==========")

	// 最简单的 GET 请求
	resp, err := http.Get("https://httpbin.org/get")
	if err != nil {
		fmt.Println("请求失败：", err)
	} else {
		defer resp.Body.Close() // 必须关闭响应体

		// 读取响应体
		body, err := ioutil.ReadAll(resp.Body)
		if err != nil {
			fmt.Println("读取失败：", err)
		} else {
			fmt.Println("状态码：", resp.Status)
			fmt.Println("响应内容：")
			fmt.Println(string(body))
		}
	}

	// -------------------- 带参数的 GET 请求 --------------------
	fmt.Println("\n========== 带参数的 GET 请求 ==========")

	// 构造 URL 参数
	params := url.Values{}
	params.Set("name", "张三")
	params.Set("age", "25")
	params.Set("city", "北京")

	fullURL := "https://httpbin.org/get?" + params.Encode()
	fmt.Println("请求 URL：", fullURL)

	resp2, err := http.Get(fullURL)
	if err != nil {
		fmt.Println("请求失败：", err)
	} else {
		defer resp2.Body.Close()
		body, _ := ioutil.ReadAll(resp2.Body)
		fmt.Println("响应：")
		fmt.Println(string(body))
	}

	// -------------------- POST 表单请求 --------------------
	fmt.Println("\n========== POST 表单请求 ==========")

	formData := url.Values{}
	formData.Set("username", "admin")
	formData.Set("password", "123456")
	formData.Set("remember", "1")

	resp3, err := http.PostForm("https://httpbin.org/post", formData)
	if err != nil {
		fmt.Println("请求失败：", err)
	} else {
		defer resp3.Body.Close()
		body, _ := ioutil.ReadAll(resp3.Body)
		fmt.Println("POST 表单响应：")
		fmt.Println(string(body))
	}

	// -------------------- POST JSON 请求 --------------------
	fmt.Println("\n========== POST JSON 请求 ==========")

	jsonData := `{"name":"张三","age":25,"email":"test@example.com"}`

	resp4, err := http.Post(
		"https://httpbin.org/post",
		"application/json",
		strings.NewReader(jsonData),
	)
	if err != nil {
		fmt.Println("请求失败：", err)
	} else {
		defer resp4.Body.Close()
		body, _ := ioutil.ReadAll(resp4.Body)
		fmt.Println("POST JSON 响应：")
		fmt.Println(string(body))
	}

	// -------------------- 自定义请求（设置 Header、Cookie 等） --------------------
	fmt.Println("\n========== 自定义请求 ==========")

	// 创建请求对象
	req, err := http.NewRequest("GET", "https://httpbin.org/headers", nil)
	if err != nil {
		fmt.Println("创建请求失败：", err)
		return
	}

	// 设置请求头
	req.Header.Set("User-Agent", "MyGoBot/1.0 (Security Tool)")
	req.Header.Set("Accept", "application/json")
	req.Header.Set("X-Custom-Header", "custom-value")

	// 设置 Cookie
	req.AddCookie(&http.Cookie{
		Name:  "session",
		Value: "abc123xyz789",
	})
	req.AddCookie(&http.Cookie{
		Name:  "token",
		Value: "secret-token-001",
	})

	// 创建自定义客户端（设置超时等）
	client := &http.Client{
		Timeout: 10 * time.Second, // 超时时间
	}

	// 发送请求
	resp5, err := client.Do(req)
	if err != nil {
		fmt.Println("请求失败：", err)
	} else {
		defer resp5.Body.Close()

		// 查看响应头
		fmt.Println("响应头：")
		for key, values := range resp5.Header {
			fmt.Printf("  %s: %s\n", key, strings.Join(values, ", "))
		}

		body, _ := ioutil.ReadAll(resp5.Body)
		fmt.Println("\n响应内容：")
		fmt.Println(string(body))
	}

	// -------------------- 响应状态码处理 --------------------
	fmt.Println("\n========== 响应状态码处理 ==========")

	checkStatus := func(url string) {
		resp, err := http.Get(url)
		if err != nil {
			fmt.Printf("  %s 请求失败: %v\n", url, err)
			return
		}
		defer resp.Body.Close()

		switch {
		case resp.StatusCode >= 200 && resp.StatusCode < 300:
			fmt.Printf("  %s -> %d (成功)\n", url, resp.StatusCode)
		case resp.StatusCode >= 300 && resp.StatusCode < 400:
			fmt.Printf("  %s -> %d (重定向)\n", url, resp.StatusCode)
		case resp.StatusCode >= 400 && resp.StatusCode < 500:
			fmt.Printf("  %s -> %d (客户端错误)\n", url, resp.StatusCode)
		case resp.StatusCode >= 500:
			fmt.Printf("  %s -> %d (服务器错误)\n", url, resp.StatusCode)
		}
	}

	checkStatus("https://httpbin.org/status/200")
	checkStatus("https://httpbin.org/status/301")
	checkStatus("https://httpbin.org/status/404")
	checkStatus("https://httpbin.org/status/500")

	// -------------------- 下载文件示例 --------------------
	fmt.Println("\n========== 下载文件示例 ==========")

	downloadURL := "https://httpbin.org/image/jpeg"
	resp6, err := http.Get(downloadURL)
	if err != nil {
		fmt.Println("下载失败：", err)
	} else {
		defer resp6.Body.Close()
		fmt.Println("下载响应状态：", resp6.Status)
		fmt.Println("Content-Type：", resp6.Header.Get("Content-Type"))
		fmt.Println("Content-Length：", resp6.Header.Get("Content-Length"))

		// 读取内容（实际使用中可以写入文件）
		data, _ := ioutil.ReadAll(resp6.Body)
		fmt.Printf("下载数据大小：%d 字节\n", len(data))
	}

	// -------------------- 安全场景：目录爆破基础版 --------------------
	fmt.Println("\n========== 安全场景：简单目录探测 ==========")

	baseURL := "https://httpbin.org/"
	paths := []string{
		"get",
		"post",
		"headers",
		"admin",
		"backup",
		"status/200",
		"status/404",
	}

	fmt.Println("目录探测结果：")
	for _, path := range paths {
		target := baseURL + path
		resp, err := http.Get(target)
		if err != nil {
			fmt.Printf("  [ERR]  %s - %v\n", path, err)
			continue
		}
		defer resp.Body.Close()

		status := ""
		switch resp.StatusCode {
		case 200:
			status = "存在"
		case 403:
			status = "禁止访问"
		case 404:
			status = "不存在"
		default:
			status = fmt.Sprintf("状态码%d", resp.StatusCode)
		}
		fmt.Printf("  [%d] %s - %s\n", resp.StatusCode, path, status)
	}

	// -------------------- 注意事项 --------------------
	fmt.Println("\n========== 注意事项 ==========")
	fmt.Println("1. 必须调用 resp.Body.Close() 释放连接")
	fmt.Println("2. 生产环境建议设置超时，避免挂起")
	fmt.Println("3. http.Get 使用默认客户端，不建议用于生产")
	fmt.Println("4. 大规模请求建议使用连接池和并发控制")
	fmt.Println("5. 安全测试请遵守法律法规，仅在授权范围内进行")

	fmt.Println("\n========== 示例结束 ==========")
}
