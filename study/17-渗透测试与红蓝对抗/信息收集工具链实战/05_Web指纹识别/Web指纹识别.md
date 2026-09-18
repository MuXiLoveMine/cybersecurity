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

## 📋 内容审核与补充建议

> 针对「Web指纹识别」部分的内容审核结果：

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

### 🛡️ 防御方案
- ⚠️ 缺少defense相关内容

### ⚔️ 攻击技术
- ⚠️ 缺少attack相关内容

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
