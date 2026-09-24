# 第三章：CSS 基础

### 3.1 什么是 CSS

CSS（Cascading Style Sheets，层叠样式表）用于描述 HTML 元素的样式和布局，控制网页的外观（颜色、字体、间距、位置等）。

### 3.2 CSS 的引入方式

```html
<!-- 方式一：内联样式（不推荐） -->
<p style="color: red; font-size: 16px;">红色文字</p>

<!-- 方式二：内部样式表 -->
<head>
    <style>
        p {
            color: blue;
            font-size: 14px;
        }
    </style>
</head>

<!-- 方式三：外部样式表（推荐） -->
<head>
    <link rel="stylesheet" href="style.css">
</head>
```

### 3.3 CSS 选择器

选择器用于选中需要应用样式的 HTML 元素。

#### 3.3.1 基本选择器

| 选择器 | 说明 | 示例 |
|--------|------|------|
| 元素选择器 | 选中所有指定元素 | `p { color: red; }` |
| ID 选择器 | 选中指定 ID 的元素（唯一） | `#header { ... }` |
| 类选择器 | 选中指定类的元素 | `.active { ... }` |
| 通配符选择器 | 选中所有元素 | `* { margin: 0; }` |

#### 3.3.2 组合选择器

| 选择器 | 说明 | 示例 |
|--------|------|------|
| `A, B` | 群组选择器（同时选中 A 和 B） | `h1, h2 { ... }` |
| `A B` | 后代选择器（A 内部所有 B） | `.nav a { ... }` |
| `A > B` | 子选择器（A 的直接子元素 B） | `ul > li { ... }` |
| `A + B` | 相邻兄弟选择器 | `h1 + p { ... }` |

#### 3.3.3 伪类选择器

| 选择器 | 说明 |
|--------|------|
| `:hover` | 鼠标悬停时 |
| `:active` | 被点击时 |
| `:focus` | 获得焦点时 |
| `:visited` | 已访问的链接 |
| `:first-child` | 第一个子元素 |
| `:last-child` | 最后一个子元素 |
| `:nth-child(n)` | 第 n 个子元素 |

### 3.4 常用 CSS 属性

#### 3.4.1 文本与字体

```css
p {
    color: #333;                /* 文字颜色 */
    font-size: 16px;            /* 字体大小 */
    font-family: Arial, sans-serif; /* 字体 */
    font-weight: bold;          /* 字重（粗体） */
    font-style: italic;         /* 斜体 */
    text-align: center;         /* 文字对齐：left/center/right */
    text-decoration: underline; /* 下划线 */
    line-height: 1.5;           /* 行高 */
    letter-spacing: 2px;        /* 字间距 */
}
```

#### 3.4.2 背景与边框

```css
.box {
    background-color: #f0f0f0;  /* 背景色 */
    background-image: url(bg.png); /* 背景图片 */
    background-size: cover;     /* 背景大小 */
    background-position: center; /* 背景位置 */
    background-repeat: no-repeat; /* 不重复 */

    border: 1px solid #ccc;     /* 边框 */
    border-radius: 8px;         /* 圆角 */
    border-color: red;          /* 边框颜色 */
    border-width: 2px;          /* 边框宽度 */
    border-style: dashed;       /* 边框样式：solid/dashed/dotted */
}
```

#### 3.4.3 盒子模型

每个 HTML 元素都可以看作一个盒子，由内到外包括：

```
┌───────────────────────────────┐
│          margin (外边距)        │
│  ┌─────────────────────────┐  │
│  │    border (边框)         │  │
│  │  ┌───────────────────┐  │  │
│  │  │  padding (内边距)  │  │  │
│  │  │  ┌─────────────┐  │  │  │
│  │  │  │   content   │  │  │  │
│  │  │  │   (内容)    │  │  │  │
│  │  │  └─────────────┘  │  │  │
│  │  └───────────────────┘  │  │
│  └─────────────────────────┘  │
└───────────────────────────────┘
```

```css
.box {
    width: 200px;               /* 宽度 */
    height: 100px;              /* 高度 */
    padding: 20px;              /* 内边距 */
    padding-top: 10px;
    padding-right: 20px;
    padding-bottom: 10px;
    padding-left: 20px;
    margin: 10px auto;          /* 外边距（auto 可水平居中） */
    border: 1px solid #000;
    box-sizing: border-box;     /* 宽高包含 padding 和 border */
}
```

#### 3.4.4 布局

```css
/* 显示模式 */
display: block;        /* 块级元素（独占一行） */
display: inline;       /* 行内元素（不换行，不支持宽高） */
display: inline-block; /* 行内块（不换行，支持宽高） */
display: none;         /* 隐藏元素（不占空间） */
visibility: hidden;    /* 隐藏元素（仍占空间） */

/* 浮动 */
float: left;
float: right;
clear: both;           /* 清除浮动 */

/* Flexbox 弹性布局 */
display: flex;
justify-content: center;    /* 主轴对齐 */
align-items: center;        /* 交叉轴对齐 */
flex-direction: row;        /* 方向：row/column */
flex-wrap: wrap;            /* 换行 */

/* 定位 */
position: static;     /* 默认定位 */
position: relative;   /* 相对定位（相对于自身原位置） */
position: absolute;   /* 绝对定位（相对于最近的非 static 祖先） */
position: fixed;      /* 固定定位（相对于视口） */
top: 10px;
left: 20px;
z-index: 100;         /* 层叠顺序，数值越大越靠上 */
```

#### 3.4.5 颜色表示

```css
/* 颜色名 */
color: red;

/* 十六进制 */
color: #ff0000;
color: #f00;    /* 简写 */

/* RGB */
color: rgb(255, 0, 0);

/* RGBA（带透明度） */
color: rgba(255, 0, 0, 0.5);  /* 50% 不透明 */
```

### 3.5 CSS 优先级

当多个样式作用于同一元素时，按以下优先级决定：

1. **!important**（最高，尽量避免使用）
2. **内联样式**（style 属性）
3. **ID 选择器**
4. **类选择器 / 伪类 / 属性选择器**
5. **元素选择器 / 伪元素**
6. **通配符 / 继承**（最低）

> 记忆口诀：**行内 > ID > 类 > 标签**

---

---

