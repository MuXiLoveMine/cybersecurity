# Native 层逆向（SO 分析）

### 6.1 JNI 基础

#### JNI 函数命名

静态注册（按命名规则）：
```
Java_包名_类名_方法名(参数列表)
```

示例：
```c
// Java 层
package com.example;
public class NativeLib {
    public native String getSign(String input);
}

// Native 层对应的函数名
Java_com_example_NativeLib_getSign(JNIEnv *env, jobject thiz, jstring input)
```

动态注册（使用 RegisterNatives）：
```c
// 方法映射表
static JNINativeMethod methods[] = {
    {"getSign", "(Ljava/lang/String;)Ljava/lang/String;", (void *)native_getSign},
    {"encrypt", "([B)[B", (void *)native_encrypt}
};

// 在 JNI_OnLoad 中注册
jint JNI_OnLoad(JavaVM *vm, void *reserved) {
    JNIEnv *env = NULL;
    (*vm)->GetEnv(vm, (void **)&env, JNI_VERSION_1_6);
    
    jclass clazz = (*env)->FindClass(env, "com/example/NativeLib");
    (*env)->RegisterNatives(env, clazz, methods, sizeof(methods)/sizeof(methods[0]));
    
    return JNI_VERSION_1_6;
}
```

#### JNI 类型映射

| Java 类型 | Native 类型 | 签名 |
|-----------|------------|------|
| boolean | jboolean | Z |
| byte | jbyte | B |
| char | jchar | C |
| short | jshort | S |
| int | jint | I |
| long | jlong | J |
| float | jfloat | F |
| double | jdouble | D |
| String | jstring | Ljava/lang/String; |
| int[] | jintArray | [I |
| byte[] | jbyteArray | [B |

### 6.2 SO 文件分析步骤

#### 1. 确定目标 SO
- 查看 APK 的 lib/ 目录
- 搜索 Java 层的 `System.loadLibrary()` 调用
- 查看 native 方法声明

#### 2. 加载到 IDA
- 打开 IDA Pro
- 拖入 .so 文件
- 选择 ARM/ARM64 架构
- 等待自动分析完成

#### 3. 查找关键函数

**方法1：搜索导出函数**
- 打开 Exports 窗口（Shift+F4）
- 查找 Java_ 开头的函数（静态注册）
- 查找 JNI_OnLoad 函数

**方法2：搜索字符串**
- 打开 Strings 窗口（Shift+F12）
- 搜索关键词（key、sign、encrypt 等）
- 交叉引用找到使用该字符串的函数

**方法3：搜索导入函数**
- 查看 Imports 窗口
- 关注加密相关函数（如 OpenSSL 的函数）

#### 4. 分析函数逻辑
- 使用 F5 反编译为伪 C 代码
- 分析函数参数和返回值
- 识别加密算法
- 理解业务逻辑

### 6.3 常见 Native 安全问题

#### 1. 密钥硬编码
```c
// 密钥直接写在代码中，容易被提取
const char *SECRET_KEY = "my_secret_key_12345";
```

#### 2. 不校验调用者
```c
// 危险：Native 函数不校验调用者是否为合法应用
// 任何应用加载这个 so 都能调用
jstring Java_com_example_NativeLib_getSign(JNIEnv *env, jobject thiz, jstring input) {
    // 没有校验调用者的签名、包名等
    return encrypt(input, SECRET_KEY);
}
```

#### 3. 缓冲区溢出
```c
// 危险：没有检查输入长度
void process_data(char *input) {
    char buffer[64];
    strcpy(buffer, input);  // 输入过长会溢出
}
```

### 6.4 Native 层 Hook

#### 使用 Frida Hook Native 函数

```javascript
// Hook 导出函数
var nativeFunc = Module.findExportByName("libnative.so", "Java_com_example_NativeLib_getSign");

Interceptor.attach(nativeFunc, {
    onEnter: function(args) {
        // args[0] = JNIEnv*
        // args[1] = jobject
        // args[2] = jstring input
        console.log("[*] getSign 被调用");
        var inputStr = Java.vm.getEnv().getStringUtfChars(args[2], null).readCString();
        console.log("    input: " + inputStr);
    },
    onLeave: function(retval) {
        console.log("    返回值地址: " + retval);
        // 解析返回的 jstring
        var resultStr = Java.vm.getEnv().getStringUtfChars(retval, null).readCString();
        console.log("    返回值: " + resultStr);
    }
});

// Hook 内部函数（通过地址偏移）
var baseAddr = Module.findBaseAddress("libnative.so");
var funcAddr = baseAddr.add(0x1234);  // 函数在 so 中的偏移

Interceptor.attach(funcAddr, {
    onEnter: function(args) {
        console.log("[*] 内部函数被调用");
        console.log("    arg0: " + args[0]);
        console.log("    arg1: " + args[1]);
    },
    onLeave: function(retval) {
        console.log("    return: " + retval);
    }
});
```

---

---

