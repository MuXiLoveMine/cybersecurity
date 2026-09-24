# PHP 框架安全

### 4.1 Laravel 安全特性

Laravel 内置 CSRF 令牌（`@csrf`）、Eloquent ORM 参数绑定、Blade 模板自动转义，安全基线较高。主要风险点：
- `unserialize()` 调用链导致的反序列化 RCE（Laravel CVE-2018-15133 通过 API Token 触发）
- `.env` 文件泄露（调试模式开启时 `whoops` 页面会暴露环境变量）

### 4.2 ThinkPHP RCE 漏洞系列分析

ThinkPHP 因框架路由与控制器调度机制缺陷，多次出现 RCE 漏洞：

- **ThinkPHP 5.x RCE**：路由解析时未过滤 `controller` 与 `method` 参数，可通过 `s=index/\think\app/invokefunction` 调用任意类的任意方法。Payload 形如 `?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo`
- **ThinkPHP 5.0.23/5.1.30 RCE**：方法名中可注入 `\think\` 命名空间路径调用系统类
- **ThinkPHP 6.x**：改进了路由与控制器调度，但 `composer` 依赖与中间件配置仍需审计

加固方案：升级至最新稳定版；生产环境关闭 `app_debug` 与 `app_trace`；限制路由调度范围，使用严格路由匹配。

### 4.3 Symfony 组件漏洞

Symfony 的 `VarDumper`、`Serializer` 等组件被广泛复用（Laravel 也依赖部分 Symfony 组件）。CVE-2022-23614 中 `Uid` 组件的反序列化缺陷影响了所有依赖该组件的项目。这体现了"组件级供应链风险"——漏洞不在你直接使用的框架中，而在其传递依赖中。

---

---

