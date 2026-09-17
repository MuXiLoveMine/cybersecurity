# Node.js 框架安全

### 5.1 Express 安全

**原型链污染**

JavaScript 中对象默认继承自 `Object.prototype`。当使用不安全的合并函数（如 `merge`/`extend`/`defaultsDeep`）处理用户 JSON 输入时，攻击者可注入 `{"__proto__": {"isAdmin": true}}` 污染原型，影响所有对象实例。

```javascript
// 危险：不安全的递归合并
function merge(target, source) {
  for (let key in source) {
    target[key] = (typeof source[key] === 'object') ? merge(target[key], source[key]) : source[key];
  }
  return target;
}
// Payload: {"__proto__": {"isAdmin": true}}
```

加固方案：使用 `Object.create(null)` 创建无原型对象；使用 `Object.getOwnPropertyNames` 替代 `for...in`；使用已修复原型链污染的库版本（lodash >= 4.17.20）。

**中间件安全**

Express 中间件执行顺序决定安全边界。常见误区：`bodyParser` 全局启用解析大文件导致 DoS；静态文件中间件未限制路径导致目录穿越；`cors` 中间件配置 `origin: '*'` 与 `credentials: true` 同时使用导致 CORS 失控。

### 5.2 Vue / React 服务端渲染安全

SSR（服务端渲染）将模板在服务端执行，若模板中插入了未转义的用户数据，XSS 风险从客户端迁移到服务端。Vue 的 `v-html` 和 React 的 `dangerouslySetInnerHTML` 是主要危险点。SSR 场景下还可能将服务端变量（如数据库连接信息）渲染进 HTML 源码导致泄露。

---

---

## 📋 内容审核与补充建议

> 针对「Node.js 框架安全」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

### 📚 知识点补充
- ⚠️ 缺少knowledge相关内容

### 🎯 实战练习
- ⚠️ 缺少practice相关内容

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
