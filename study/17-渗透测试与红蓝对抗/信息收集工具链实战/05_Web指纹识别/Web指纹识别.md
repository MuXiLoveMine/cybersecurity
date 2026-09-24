# Web指纹识别

### 5.1 Wappalyzer

```bash
# Wappalyzer - 技术栈识别
# CLI版本安装
npm install -g wappalyzer

# 使用
wappalyzer https://example.com

# JSON输出
wappalyzer https://example.com --pretty

# 批量扫描
cat urls.txt | while read url; do
    echo "=== $url ==="
    wappalyzer "$url"
done
```

### 5.2 whatweb

```bash
# whatweb - Web指纹识别工具
# 安装
gem install whatweb

# 基本使用
whatweb example.com

# 详细模式
whatweb -a 3 example.com

# 批量扫描
whatweb -i urls.txt

# 输出格式
whatweb example.com --log-verbose=verbose.txt
whatweb example.com --log-json=json.txt

# 自定义插件
whatweb -p custom_plugin example.com

# 常见输出字段
# - HTTP状态码
# - 服务器类型和版本
# - CMS类型
# - 编程语言
# - JavaScript库
# - CDN
# - Web框架
# - 分析工具
```

---

---

