# Cycript动态分析

### 3.1 Cycript基础语法

Cycript允许在运行时与Objective-C对象交互：

```javascript
// 连接到进程
cycript -p SpringBoard

// 获取当前应用的keyWindow
UIWindow *keyWindow = (UIWindow *)[[UIApplication sharedApplication] keyWindow];

// 获取rootViewController
UIViewController *rootVC = [keyWindow rootViewController];
console.log([rootVC description]);

// 列出所有视图
[rootVC.view.subviews enumerateObjectsUsingBlock:^(UIView *view, NSUInteger idx, BOOL *stop) {
    console.log([view description]);
}];

// 获取当前显示的视图控制器
UIViewController *visibleVC = rootVC;
while ([visibleVC presentedViewController]) {
    visibleVC = [visibleVC presentedViewController];
}
console.log([visibleVC description]);
```

### 3.2 实例变量与方法Hook

```javascript
// 获取类实例变量
#import "<头文件名>"
MyClass *instance = [MyClass new];

// 查看实例变量
MyClass *obj = [[MyClass alloc] init];
console.log([obj ivarList]);

// Hook方法实现
%hook MyClass
- (void)sensitiveMethod:(NSString *)param {
    console.log(@"调用了sensitiveMethod: %@", param);
    %orig; // 调用原始实现
}
%end

// 动态修改实例变量值
MyClass *obj = [someInstance];
[obj setValue:@"hacked" forKey:@"secretValue"];

// 遍历当前所有对象
// 使用objc_getClassList获取所有类
unsigned int count = 0;
Class *classes = objc_copyClassList(&count);
for (int i = 0; i < count; i++) {
    console.log(class_getName(classes[i]));
}
```

### 3.3 消息转发分析

```javascript
// 分析消息转发机制
// Hook forwardingTargetForSelector:
%hook NSObject
- (id)forwardingTargetForSelector:(SEL)sel {
    console.log(@"forwardingTargetForSelector: %@", NSStringFromSelector(sel));
    return %orig;
}
%end

// Hook methodSignatureForSelector:
%hook NSObject
- (NSMethodSignature *)methodSignatureForSelector:(SEL)sel {
    console.log(@"methodSignatureForSelector: %@", NSStringFromSelector(sel));
    return %orig;
}
%end

// Hook forwardInvocation:
%hook NSObject
- (void)forwardInvocation:(NSInvocation *)invocation {
    console.log(@"forwardInvocation: %@", NSStringFromSelector([invocation selector]));
    %orig;
}
%end
```

---

---

## 📋 内容审核与补充建议

> 针对「Cycript动态分析」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

### ⌨️ 命令帮助
- ⚠️ 缺少commands相关内容

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
