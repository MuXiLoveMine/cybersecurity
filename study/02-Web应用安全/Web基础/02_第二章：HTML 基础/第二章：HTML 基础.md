# 第二章：HTML 基础

### 2.1 什么是 HTML

HTML（HyperText Markup Language，超文本标记语言）是用于创建网页的标准标记语言。它不是编程语言，而是用标签（tag）来描述网页的结构和内容。

### 2.2 HTML 基本结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>网页标题</title>
</head>
<body>
    <h1>这是一级标题</h1>
    <p>这是一个段落。</p>
</body>
</html>
```

**结构说明**：
- `<!DOCTYPE html>`：声明文档类型为 HTML5
- `<html>`：根元素，包含整个 HTML 文档
- `<head>`：头部，包含元数据（字符集、标题、样式等）
- `<body>`：主体，包含页面可见内容

### 2.3 常用 HTML 标签

#### 2.3.1 文本标签

| 标签 | 说明 | 示例 |
|------|------|------|
| `<h1>`~`<h6>` | 标题（h1 最大，h6 最小） | `<h1>一级标题</h1>` |
| `<p>` | 段落 | `<p>这是段落</p>` |
| `<br>` | 换行 | `第一行<br>第二行` |
| `<hr>` | 水平线 | `<hr>` |
| `<strong>` | 加粗（强调） | `<strong>重要内容</strong>` |
| `<em>` | 斜体（强调） | `<em>强调文本</em>` |
| `<span>` | 行内容器 | `<span style="color:red">红色</span>` |
| `<div>` | 块级容器 | `<div>内容块</div>` |

#### 2.3.2 链接与图片

```html
<!-- 超链接 -->
<a href="https://www.example.com">访问示例网站</a>
<a href="https://example.com" target="_blank">新窗口打开</a>
<a href="#section1">跳转到页面内锚点</a>
<a href="mailto:test@example.com">发送邮件</a>

<!-- 图片 -->
<img src="image.jpg" alt="图片描述" width="200" height="100">
<img src="https://example.com/logo.png" alt="Logo">
```

#### 2.3.3 列表

```html
<!-- 无序列表 -->
<ul>
    <li>苹果</li>
    <li>香蕉</li>
    <li>樱桃</li>
</ul>

<!-- 有序列表 -->
<ol>
    <li>第一步</li>
    <li>第二步</li>
    <li>第三步</li>
</ol>

<!-- 定义列表 -->
<dl>
    <dt>HTML</dt>
    <dd>超文本标记语言</dd>
    <dt>CSS</dt>
    <dd>层叠样式表</dd>
</dl>
```

#### 2.3.4 表格

```html
<table border="1">
    <thead>
        <tr>
            <th>姓名</th>
            <th>年龄</th>
            <th>城市</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>张三</td>
            <td>25</td>
            <td>北京</td>
        </tr>
        <tr>
            <td>李四</td>
            <td>30</td>
            <td>上海</td>
        </tr>
    </tbody>
</table>
```

#### 2.3.5 表单

表单是用户输入和提交数据的重要方式，也是 Web 安全的重点关注对象。

```html
<form action="/login" method="POST">
    <!-- 文本输入 -->
    <label>用户名：</label>
    <input type="text" name="username" value="" placeholder="请输入用户名">
    <br>

    <!-- 密码输入 -->
    <label>密码：</label>
    <input type="password" name="password">
    <br>

    <!-- 单选框 -->
    <label>性别：</label>
    <input type="radio" name="gender" value="male" checked> 男
    <input type="radio" name="gender" value="female"> 女
    <br>

    <!-- 复选框 -->
    <label>爱好：</label>
    <input type="checkbox" name="hobby" value="reading"> 阅读
    <input type="checkbox" name="hobby" value="music"> 音乐
    <input type="checkbox" name="hobby" value="sports"> 运动
    <br>

    <!-- 下拉选择 -->
    <label>城市：</label>
    <select name="city">
        <option value="beijing">北京</option>
        <option value="shanghai">上海</option>
        <option value="guangzhou">广州</option>
    </select>
    <br>

    <!-- 文本域 -->
    <label>留言：</label>
    <textarea name="message" rows="4" cols="30"></textarea>
    <br>

    <!-- 隐藏字段 -->
    <input type="hidden" name="token" value="abc123">

    <!-- 按钮 -->
    <button type="submit">提交</button>
    <button type="reset">重置</button>
</form>
```

**表单重要属性**：

| 属性 | 说明 | 安全意义 |
|------|------|---------|
| `action` | 表单提交的目标 URL | - |
| `method` | 提交方式：GET 或 POST | GET 参数在 URL 中，POST 在请求体中 |
| `name` | 表单元素的名称，提交时的键 | - |
| `value` | 表单元素的默认值 | - |
| `placeholder` | 提示文字 | - |

> **安全提示**：表单是 XSS、SQL 注入、CSRF 等漏洞的常见入口，所有用户输入都需要在后端进行严格的验证和过滤。

### 2.4 HTML 全局属性

| 属性 | 说明 |
|------|------|
| `id` | 元素的唯一标识符 |
| `class` | 元素的类名（用于 CSS 和 JS） |
| `style` | 内联 CSS 样式 |
| `title` | 鼠标悬停时显示的提示 |
| `data-*` | 自定义数据属性 |
| `hidden` | 隐藏元素 |

### 2.5 语义化标签

HTML5 引入了语义化标签，使页面结构更清晰：

| 标签 | 说明 |
|------|------|
| `<header>` | 页面或区块的头部 |
| `<nav>` | 导航区域 |
| `<main>` | 主要内容 |
| `<section>` | 章节 |
| `<article>` | 独立的文章内容 |
| `<aside>` | 侧边栏 |
| `<footer>` | 页脚 |

---

---

## 📋 内容审核与补充建议

> 针对「第二章：HTML 基础」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### 📖 参考资料
- ⚠️ 缺少参考资料/延伸阅读

---

## 📌 拓展学习资源

### 推荐学习路径
- 理论基础 → 工具实践 → 实战演练 → 深度研究
- 建议搭建本地实验环境进行动手练习

### 相关工具与资源
- 在线实验平台：Hack The Box、TryHackMe、VulnHub
- 技术文档：官方文档、RFC、OWASP 指南
- 社区资源：GitHub、安全论坛、技术博客
