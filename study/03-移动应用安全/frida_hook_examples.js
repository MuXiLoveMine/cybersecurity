/*
 * ============================================================================
 *  Frida Hook 实战案例集合
 *  包含详细中文注释，覆盖 Java 层、Native 层、SSL Pinning 绕过等常见场景
 *
 *  使用方法：
 *  frida -U -f com.example.app -l frida_hook_examples.js --no-pause
 *
 *  注意：使用前请根据实际情况修改包名、类名、方法名
 * ============================================================================
 */

// ==========================================
//  第一部分：Java 层 Hook 基础
// ==========================================

/**
 * 示例 1：Hook 普通方法并打印参数和返回值
 * 场景：分析登录逻辑，查看传入的用户名和密码
 */
Java.perform(function () {
    console.log("\n========== [示例1] Hook 普通方法 ==========");

    try {
        // 获取目标类
        var LoginActivity = Java.use("com.example.app.activity.LoginActivity");

        // Hook login 方法（参数为用户名和密码，返回 boolean）
        LoginActivity.login.implementation = function (username, password) {
            console.log("[*] login 方法被调用");
            console.log("    用户名: " + username);
            console.log("    密码: " + password);

            // 调用原始方法，获取返回值
            var result = this.login(username, password);
            console.log("    原始返回值: " + result);

            // 可以修改返回值（这里演示强制返回 true）
            // return true;

            // 返回原始结果
            return result;
        };

        console.log("[+] 成功 Hook LoginActivity.login");
    } catch (e) {
        console.log("[-] Hook 失败: " + e.message);
    }
});

/**
 * 示例 2：Hook 构造方法
 * 场景：跟踪某个对象的创建时机
 */
Java.perform(function () {
    console.log("\n========== [示例2] Hook 构造方法 ==========");

    try {
        var User = Java.use("com.example.app.model.User");

        // Hook 构造方法（带两个参数的构造函数）
        User.$init.overload('java.lang.String', 'java.lang.String').implementation = function (name, email) {
            console.log("[*] User 对象被创建");
            console.log("    name: " + name);
            console.log("    email: " + email);

            // 调用原始构造方法
            this.$init(name, email);

            // 构造完成后可以访问对象的属性
            console.log("    构造完成, userId: " + this.userId.value);
        };

        console.log("[+] 成功 Hook User 构造方法");
    } catch (e) {
        console.log("[-] Hook 失败: " + e.message);
    }
});

/**
 * 示例 3：Hook 重载方法（方法名相同，参数不同）
 * 场景：同一个类中有多个同名方法，需要指定参数类型
 */
Java.perform(function () {
    console.log("\n========== [示例3] Hook 重载方法 ==========");

    try {
        var EncryptUtil = Java.use("com.example.app.utils.EncryptUtil");

        // Hook encrypt(String) 方法
        EncryptUtil.encrypt.overload('java.lang.String').implementation = function (input) {
            console.log("[*] encrypt(String) 被调用");
            console.log("    输入: " + input);
            var result = this.encrypt(input);
            console.log("    输出: " + result);
            return result;
        };

        // Hook encrypt(String, String) 方法（带密钥参数）
        EncryptUtil.encrypt.overload('java.lang.String', 'java.lang.String').implementation = function (input, key) {
            console.log("[*] encrypt(String, String) 被调用");
            console.log("    输入: " + input);
            console.log("    密钥: " + key);
            var result = this.encrypt(input, key);
            console.log("    输出: " + result);
            return result;
        };

        console.log("[+] 成功 Hook EncryptUtil.encrypt 重载方法");
    } catch (e) {
        console.log("[-] Hook 失败: " + e.message);
    }
});

/**
 * 示例 4：Hook 静态方法
 * 场景：Hook 工具类中的静态方法
 */
Java.perform(function () {
    console.log("\n========== [示例4] Hook 静态方法 ==========");

    try {
        var AppUtils = Java.use("com.example.app.utils.AppUtils");

        // 静态方法直接通过类名调用，不需要 this
        AppUtils.getDeviceId.implementation = function () {
            console.log("[*] getDeviceId 静态方法被调用");

            // 调用原方法（静态方法用类名调用，不是 this）
            var result = AppUtils.getDeviceId();
            console.log("    原始设备ID: " + result);

            // 修改返回值（伪造设备ID）
            var fakeDeviceId = "fake_device_id_1234567890";
            console.log("    伪造设备ID: " + fakeDeviceId);
            return fakeDeviceId;
        };

        console.log("[+] 成功 Hook AppUtils.getDeviceId");
    } catch (e) {
        console.log("[-] Hook 失败: " + e.message);
    }
});

/**
 * 示例 5：Hook 内部类和匿名类
 * 场景：Hook 内部类的方法（内部类名用 $ 分隔）
 */
Java.perform(function () {
    console.log("\n========== [示例5] Hook 内部类 ==========");

    try {
        // 内部类的表示方式：外部类$内部类
        var InnerClass = Java.use("com.example.app.MainActivity$1");

        // 匿名内部类通常是 MainActivity$1, MainActivity$2...
        // 可以通过 jadx 反编译查看具体的类名

        console.log("[+] 成功加载内部类");
    } catch (e) {
        console.log("[-] Hook 内部类失败（示例，需要根据实际类名修改）: " + e.message);
    }
});

/**
 * 示例 6：主动调用 Java 方法
 * 场景：不通过 UI 操作，直接调用应用内的方法
 */
Java.perform(function () {
    console.log("\n========== [示例6] 主动调用 Java 方法 ==========");

    try {
        var EncryptUtil = Java.use("com.example.app.utils.EncryptUtil");

        // 直接调用静态方法
        var encrypted = EncryptUtil.encrypt("test_password");
        console.log("[*] 主动调用 encrypt 结果: " + encrypted);

        // 创建对象实例并调用方法
        var User = Java.use("com.example.app.model.User");
        var user = User.$new("admin", "admin@example.com");
        console.log("[*] 创建 User 对象: " + user.toString());

        console.log("[+] 主动调用示例完成");
    } catch (e) {
        console.log("[-] 主动调用失败（示例）: " + e.message);
    }
});

/**
 * 示例 7：修改对象字段值
 * 场景：直接修改对象的成员变量
 */
Java.perform(function () {
    console.log("\n========== [示例7] 修改对象字段 ==========");

    try {
        var User = Java.use("com.example.app.model.User");

        User.setVipLevel.implementation = function (level) {
            console.log("[*] 原始 VIP 等级: " + level);

            // 修改传入参数
            var newLevel = 99;  // 改成最高等级
            console.log("[*] 修改后 VIP 等级: " + newLevel);

            this.setVipLevel(newLevel);

            // 也可以直接修改字段
            // this.vipLevel.value = 99;  // 注意：字段访问用 .value
        };

        console.log("[+] 成功 Hook setVipLevel");
    } catch (e) {
        console.log("[-] Hook 失败（示例）: " + e.message);
    }
});

// ==========================================
//  第二部分：加密参数抓取
// ==========================================

/**
 * 示例 8：Hook AES 加密，抓取明文和密文
 * 场景：应用使用 AES 加密请求参数，需要获取加密前的明文
 */
Java.perform(function () {
    console.log("\n========== [示例8] 抓取 AES 加密参数 ==========");

    try {
        // Hook Cipher 类的 doFinal 方法（Java 标准加密库）
        var Cipher = Java.use("javax.crypto.Cipher");

        Cipher.doFinal.overload('[B').implementation = function (input) {
            // 获取加密模式（1=加密, 2=解密）
            var opmode = this.opmode.value;
            var opName = opmode === 1 ? "加密" : "解密";

            // 将 byte[] 转换为字符串或 hex
            var inputStr = bytesToHex(input);
            console.log("[*] AES " + opName);
            console.log("    输入(Hex): " + inputStr);

            // 尝试打印明文（如果是文本的话）
            try {
                var inputText = Java.use("java.lang.String").$new(input);
                console.log("    输入(文本): " + inputText);
            } catch (e) {
                // 不是文本就跳过
            }

            // 调用原方法
            var result = this.doFinal(input);

            var outputStr = bytesToHex(result);
            console.log("    输出(Hex): " + outputStr);

            return result;
        };

        console.log("[+] 成功 Hook Cipher.doFinal");
    } catch (e) {
        console.log("[-] Hook 失败: " + e.message);
    }
});

/**
 * 示例 9：Hook MD5/SHA 哈希计算
 * 场景：抓取签名计算的输入和结果
 */
Java.perform(function () {
    console.log("\n========== [示例9] 抓取 MD5/SHA 哈希 ==========");

    try {
        var MessageDigest = Java.use("java.security.MessageDigest");

        // Hook digest() 方法，获取最终的哈希结果
        MessageDigest.digest.overload().implementation = function () {
            var algorithm = this.getAlgorithm();
            console.log("[*] " + algorithm + " 计算完成");

            var result = this.digest();
            console.log("    结果(Hex): " + bytesToHex(result));

            return result;
        };

        // Hook update 方法，获取输入数据
        MessageDigest.update.overload('[B').implementation = function (input) {
            var algorithm = this.getAlgorithm();
            console.log("[*] " + algorithm + " update");
            try {
                var inputStr = Java.use("java.lang.String").$new(input);
                console.log("    输入: " + inputStr);
            } catch (e) {
                console.log("    输入(Hex): " + bytesToHex(input));
            }
            this.update(input);
        };

        console.log("[+] 成功 Hook MessageDigest");
    } catch (e) {
        console.log("[-] Hook 失败: " + e.message);
    }
});

/**
 * 示例 10：Hook OkHttp 请求，抓取请求参数
 * 场景：应用使用 OkHttp 进行网络请求，需要查看请求和响应
 */
Java.perform(function () {
    console.log("\n========== [示例10] Hook OkHttp 请求 ==========");

    try {
        var Request = Java.use("okhttp3.Request");
        var Response = Java.use("okhttp3.Response");
        var RealCall = Java.use("okhttp3.RealCall");

        // Hook 同步请求
        RealCall.execute.implementation = function () {
            var request = this.request();
            console.log("[*] OkHttp 请求");
            console.log("    方法: " + request.method());
            console.log("    URL: " + request.url().toString());

            // 打印请求头
            var headers = request.headers();
            console.log("    请求头:");
            for (var i = 0; i < headers.size(); i++) {
                console.log("      " + headers.name(i) + ": " + headers.value(i));
            }

            // 打印请求体（POST 请求）
            if (request.body() !== null) {
                console.log("    请求体存在（如需查看可进一步 Hook）");
            }

            // 执行请求
            var response = this.execute();

            console.log("    响应码: " + response.code());

            return response;
        };

        console.log("[+] 成功 Hook OkHttp");
    } catch (e) {
        console.log("[-] Hook OkHttp 失败（可能版本不同）: " + e.message);
    }
});

// ==========================================
//  第三部分：SSL Pinning 绕过
// ==========================================

/**
 * 示例 11：绕过 SSL Pinning（通用方法 - Unpinning）
 * 场景：应用使用了 SSL Pinning，导致无法正常抓包
 * 原理：Hook 证书校验相关的类，让所有证书都通过验证
 */
Java.perform(function () {
    console.log("\n========== [示例11] SSL Pinning 绕过 ==========");

    // 方法 1：Hook X509TrustManager，信任所有证书
    try {
        var X509TrustManager = Java.use('javax.net.ssl.X509TrustManager');
        var SSLContext = Java.use('javax.net.ssl.SSLContext');

        // 创建一个信任所有证书的 TrustManager
        var TrustManager = Java.registerClass({
            name: 'com.example.TrustAllManager',
            implements: [X509TrustManager],
            methods: {
                checkClientTrusted: function (chain, authType) {
                    console.log("[*] 跳过客户端证书校验");
                },
                checkServerTrusted: function (chain, authType) {
                    console.log("[*] 跳过服务器证书校验");
                },
                getAcceptedIssuers: function () {
                    return [];
                }
            }
        });

        var TrustManagers = [TrustManager.$new()];

        // Hook SSLContext.init，替换 TrustManager
        SSLContext.init.overload('[Ljavax.net.ssl.TrustManager;', 'java.security.SecureRandom').implementation = function (tm, sr) {
            console.log("[*] SSLContext.init 被调用，替换为信任所有证书的 TrustManager");
            this.init(null, TrustManagers, sr);
        };

        console.log("[+] SSL Pinning 绕过方案1 (TrustManager) 已生效");
    } catch (e) {
        console.log("[-] 方案1失败: " + e.message);
    }

    // 方法 2：Hook HostnameVerifier，跳过主机名校验
    try {
        var HostnameVerifier = Java.use('javax.net.ssl.HostnameVerifier');
        var HttpsURLConnection = Java.use('javax.net.ssl.HttpsURLConnection');

        // 创建一个永远返回 true 的 HostnameVerifier
        var FakeVerifier = Java.registerClass({
            name: 'com.example.FakeHostnameVerifier',
            implements: [HostnameVerifier],
            methods: {
                verify: function (hostname, session) {
                    console.log("[*] 跳过主机名校验: " + hostname);
                    return true;
                }
            }
        });

        // Hook setDefaultHostnameVerifier
        HttpsURLConnection.setDefaultHostnameVerifier(FakeVerifier.$new());

        console.log("[+] SSL Pinning 绕过方案2 (HostnameVerifier) 已生效");
    } catch (e) {
        console.log("[-] 方案2失败: " + e.message);
    }

    // 方法 3：Hook OkHttp 的 CertificatePinner
    try {
        var CertificatePinner = Java.use('okhttp3.CertificatePinner');

        CertificatePinner.check.overload('java.lang.String', 'java.util.List').implementation = function (hostname, peerCertificates) {
            console.log("[*] 跳过 OkHttp CertificatePinner 校验: " + hostname);
            // 直接返回，不抛异常就是通过
            return;
        };

        console.log("[+] SSL Pinning 绕过方案3 (OkHttp CertificatePinner) 已生效");
    } catch (e) {
        console.log("[-] 方案3失败: " + e.message);
    }

    // 方法 4：Hook WebView 的 onReceivedSslError
    try {
        var WebViewClient = Java.use('android.webkit.WebViewClient');
        var SslErrorHandler = Java.use('android.webkit.SslErrorHandler');

        // 注意：Hook 匿名类比较困难，这里用 frida 的 android ssl unpinning 脚本效果更好
        console.log("[+] SSL Pinning 绕过方案4 (WebView) 说明：建议使用 objection 或 frida-android-unpinning");
    } catch (e) {
        console.log("[-] 方案4失败: " + e.message);
    }
});

// ==========================================
//  第四部分：Native 层 Hook
// ==========================================

/**
 * 示例 12：Hook Native 导出函数
 * 场景：Hook so 文件中的导出函数，查看参数和返回值
 */
function hookNativeExport() {
    console.log("\n========== [示例12] Hook Native 导出函数 ==========");

    // 目标 so 库名
    var libName = "libnative-lib.so";
    // 目标函数名（导出符号）
    var funcName = "Java_com_example_native_MainActivity_stringFromJNI";

    // 查找模块基址
    var baseAddr = Module.findBaseAddress(libName);
    if (baseAddr === null) {
        console.log("[-] 未找到模块: " + libName);
        console.log("    可能 so 还未加载，可以等加载后再 Hook");
        return;
    }
    console.log("[+] " + libName + " 基址: " + baseAddr);

    // 查找导出函数
    var funcAddr = Module.findExportByName(libName, funcName);
    if (funcAddr === null) {
        console.log("[-] 未找到函数: " + funcName);
        return;
    }
    console.log("[+] " + funcName + " 地址: " + funcAddr);

    // Hook 函数
    Interceptor.attach(funcAddr, {
        onEnter: function (args) {
            console.log("[*] " + funcName + " 被调用");
            // JNI 函数的前两个参数固定为 JNIEnv* 和 jobject/jclass
            // args[0] = JNIEnv*
            // args[1] = jobject (this 或 class)
            // args[2...] = 实际参数

            // 如果参数是 jstring，可以这样解析
            if (args[2] !== undefined) {
                try {
                    var env = Java.vm.getEnv();
                    var jstring = args[2];
                    var str = env.getStringUtfChars(jstring, null);
                    console.log("    参数: " + str.readCString());
                } catch (e) {
                    console.log("    参数地址: " + args[2]);
                }
            }
        },
        onLeave: function (retval) {
            console.log("    返回值地址: " + retval);

            // 如果返回值是 jstring
            try {
                var env = Java.vm.getEnv();
                var result = env.getStringUtfChars(retval, null);
                console.log("    返回值: " + result.readCString());
            } catch (e) {
                // 不是 jstring 就打印地址
            }
        }
    });

    console.log("[+] 成功 Hook " + funcName);
}

// 等 Java 层就绪后再执行 Native Hook（推荐做法）
Java.perform(function () {
    setTimeout(hookNativeExport, 1000);  // 延迟 1 秒，等待 so 加载
});

/**
 * 示例 13：Hook Native 内部函数（通过偏移）
 * 场景：目标函数不是导出函数，需要通过偏移量计算地址
 */
function hookNativeByOffset() {
    console.log("\n========== [示例13] Hook Native 内部函数（偏移） ==========");

    var libName = "libnative-lib.so";
    // 函数在 so 文件中的偏移（需要通过 IDA 分析得到）
    var funcOffset = 0x1234;  // 示例偏移，需根据实际情况修改

    var baseAddr = Module.findBaseAddress(libName);
    if (baseAddr === null) {
        console.log("[-] 未找到模块: " + libName);
        return;
    }

    // 计算函数实际地址 = 基址 + 偏移
    var funcAddr = baseAddr.add(funcOffset);
    console.log("[+] 函数地址: " + funcAddr);

    Interceptor.attach(funcAddr, {
        onEnter: function (args) {
            console.log("[*] 内部函数被调用");
            // ARM 32位: 参数在 R0-R3
            // ARM 64位: 参数在 X0-X7
            console.log("    R0/X0: " + args[0]);
            console.log("    R1/X1: " + args[1]);
            console.log("    R2/X2: " + args[2]);
            console.log("    R3/X3: " + args[3]);

            // 如果第一个参数是字符串指针
            try {
                var str = args[0].readCString();
                console.log("    参数字符串: " + str);
            } catch (e) {
                // 不是有效字符串
            }
        },
        onLeave: function (retval) {
            console.log("    返回值: " + retval);

            // 如果返回值是字符串
            try {
                var str = retval.readCString();
                console.log("    返回字符串: " + str);
            } catch (e) {
                // 不是有效字符串
            }
        }
    });

    console.log("[+] 成功 Hook 内部函数");
}

/**
 * 示例 14：Hook 系统 Native 函数（如 open、read 等）
 * 场景：监控文件操作，查看应用读写了哪些文件
 */
function hookSystemNative() {
    console.log("\n========== [示例14] Hook 系统 Native 函数 ==========");

    // Hook open 函数，监控文件打开
    var openPtr = Module.findExportByName(null, "open");
    if (openPtr) {
        Interceptor.attach(openPtr, {
            onEnter: function (args) {
                var path = args[0].readCString();
                // 只打印应用相关的文件，过滤掉系统文件
                if (path.indexOf("com.example") !== -1 ||
                    path.indexOf("/sdcard/") !== -1 ||
                    path.indexOf("/data/data/") !== -1) {
                    console.log("[*] open 文件: " + path);
                }
            }
        });
        console.log("[+] 成功 Hook open 函数");
    }

    // Hook __android_log_print，打印 native 日志
    var logPrintPtr = Module.findExportByName(null, "__android_log_print");
    if (logPrintPtr) {
        Interceptor.attach(logPrintPtr, {
            onEnter: function (args) {
                var prio = args[0].toInt32();
                var tag = args[1].readCString();
                var fmt = args[2].readCString();
                // 注意：可变参数处理比较复杂，这里只打印 tag 和 format
                console.log("[Native Log] [" + tag + "] " + fmt);
            }
        });
        console.log("[+] 成功 Hook __android_log_print");
    }
}

Java.perform(function () {
    setTimeout(hookSystemNative, 1500);
});

// ==========================================
//  第五部分：内存数据 Dump
// ==========================================

/**
 * 示例 15：Dump 内存中的 DEX 文件（简单的脱壳思路）
 * 场景：加固应用在内存中加载了解密后的 DEX，可以 dump 出来
 */
function dumpDexFromMemory() {
    console.log("\n========== [示例15] Dump 内存 DEX ==========");

    // 遍历内存中的 dex 文件
    var ranges = Process.enumerateRanges('r--');  // 只读内存段
    var dexCount = 0;

    for (var i = 0; i < ranges.length; i++) {
        var range = ranges[i];
        try {
            // 读取前 8 个字节，检查是否是 dex 魔数
            var magic = range.base.readByteArray(8);
            if (magic === null) continue;

            // DEX 魔数: dex\n035\0 (即 64 65 78 0A 30 33 35 00)
            if (magic[0] === 0x64 && magic[1] === 0x65 &&
                magic[2] === 0x78 && magic[3] === 0x0A) {

                console.log("[+] 找到 DEX 于: " + range.base);
                console.log("    大小: " + range.size);

                // 从 DEX 头中获取真实大小（地址偏移 0x20 处是 file_size）
                var dexSize = range.base.add(0x20).readU32();
                console.log("    DEX 真实大小: " + dexSize);

                // Dump 到文件（需要写文件权限，通常 /data/local/tmp/ 可以）
                var dexData = range.base.readByteArray(dexSize);
                var fileName = "/data/local/tmp/dump_" + dexCount + ".dex";
                var file = new File(fileName, "wb");
                file.write(dexData);
                file.flush();
                file.close();

                console.log("    已保存到: " + fileName);
                dexCount++;
            }
        } catch (e) {
            // 读取失败，跳过
        }
    }

    console.log("[+] 共找到 " + dexCount + " 个 DEX 文件");
}

// 导出到全局，方便在 frida 交互中手动调用
global.dumpDex = dumpDexFromMemory;

/**
 * 示例 16：搜索内存中的字符串
 * 场景：在内存中搜索特定的字符串（如密钥、密码等）
 */
function searchMemoryString(searchStr) {
    console.log("\n========== [示例16] 内存字符串搜索 ==========");
    console.log("[*] 搜索关键词: " + searchStr);

    var ranges = Process.enumerateRanges('r--');
    var matches = [];

    for (var i = 0; i < ranges.length; i++) {
        var range = ranges[i];
        try {
            // 在内存段中搜索
            var results = Memory.scanSync(range.base, range.size, searchStr);
            for (var j = 0; j < results.length; j++) {
                matches.push(results[j].address);
                console.log("[+] 找到匹配: " + results[j].address);
            }
        } catch (e) {
            // 跳过不可读的内存
        }
    }

    console.log("[+] 共找到 " + matches.length + " 处匹配");
    return matches;
}

global.searchStr = searchMemoryString;

// ==========================================
//  第六部分：绕过检测与反调试
// ==========================================

/**
 * 示例 17：绕过 Root 检测
 * 场景：应用检测设备是否 Root，检测到就退出或限制功能
 */
Java.perform(function () {
    console.log("\n========== [示例17] 绕过 Root 检测 ==========");

    // 方法 1：Hook 文件存在检测
    try {
        var File = Java.use("java.io.File");
        var originalExists = File.exists.implementation;

        File.exists.implementation = function () {
            var path = this.getPath();

            // 常见的 Root 相关文件
            var rootFiles = [
                "/system/app/Superuser.apk",
                "/sbin/su",
                "/system/bin/su",
                "/system/xbin/su",
                "/data/local/xbin/su",
                "/data/local/bin/su",
                "/system/sd/xbin/su",
                "/system/bin/failsafe/su",
                "/data/local/su",
                "/su/bin/su",
                "/system/bin/.ext/.su",
                "/system/usr/we-need-root/su-backup",
                "/system/xbin/mu"
            ];

            for (var i = 0; i < rootFiles.length; i++) {
                if (path.indexOf(rootFiles[i]) !== -1) {
                    console.log("[*] 检测到 Root 文件检查: " + path + "，返回 false");
                    return false;
                }
            }

            return originalExists.call(this);
        };

        console.log("[+] Root 检测绕过方案1 (File.exists) 已生效");
    } catch (e) {
        console.log("[-] 方案1失败: " + e.message);
    }

    // 方法 2：Hook 执行命令检测（which su 等）
    try {
        var Runtime = Java.use("java.lang.Runtime");

        Runtime.exec.overload('java.lang.String').implementation = function (cmd) {
            console.log("[*] 执行命令: " + cmd);

            // 如果是检测 su 的命令，返回空结果
            if (cmd.indexOf("su") !== -1 || cmd.indexOf("which") !== -1) {
                console.log("    疑似 Root 检测命令，返回空结果");
                // 构造一个假的 Process，模拟命令执行失败
                // 实际处理比较复杂，这里简化处理
            }

            return this.exec(cmd);
        };

        console.log("[+] Root 检测绕过方案2 (Runtime.exec) 已生效");
    } catch (e) {
        console.log("[-] 方案2失败: " + e.message);
    }

    // 方法 3：Hook Build.TAGS 检测
    try {
        var Build = Java.use("android.os.Build");

        // 检查 TAGS 是否包含 test-keys
        console.log("[+] 当前 Build.TAGS: " + Build.TAGS.value);
        // 可以直接修改，但要在应用检查前修改
        // Build.TAGS.value = "release-keys";

        console.log("[+] Root 检测绕过方案3 (Build.TAGS) 说明：可直接修改 Build.TAGS");
    } catch (e) {
        console.log("[-] 方案3失败: " + e.message);
    }
});

/**
 * 示例 18：绕过反调试检测（ptrace 检测）
 * 场景：应用通过 ptrace 或其他方式检测是否被调试
 */
function bypassAntiDebug() {
    console.log("\n========== [示例18] 绕过反调试检测 ==========");

    // 方法 1：Hook ptrace 函数
    var ptracePtr = Module.findExportByName(null, "ptrace");
    if (ptracePtr) {
        Interceptor.replace(ptracePtr, new NativeCallback(function (request, pid, addr, data) {
            // PTRACE_TRACEME = 0
            // 如果应用调用 ptrace(PTRACE_TRACEME, 0, 0, 0) 检测自身是否被调试
            // 直接返回 0（成功），假装没有被调试
            console.log("[*] ptrace 被调用, request=" + request + "，返回成功");
            return 0;  // 返回 0 表示成功
        }, 'int', ['int', 'int', 'pointer', 'pointer']));

        console.log("[+] 反调试绕过方案1 (ptrace) 已生效");
    }

    // 方法 2：Hook /proc/self/status 读取（检测 TracerPid）
    // 原理：读取 /proc/self/status 时，修改 TracerPid 为 0
    var fopenPtr = Module.findExportByName(null, "fopen");
    if (fopenPtr) {
        Interceptor.attach(fopenPtr, {
            onEnter: function (args) {
                var path = args[0].readCString();
                if (path.indexOf("/proc/self/status") !== -1 ||
                    path.indexOf("/proc/") !== -1 && path.indexOf("/status") !== -1) {
                    this.isStatusFile = true;
                    console.log("[*] 读取 status 文件: " + path);
                }
            }
        });
        console.log("[+] 反调试绕过方案2 (proc status) 说明：可进一步 Hook fgets 修改内容");
    }
}

Java.perform(function () {
    setTimeout(bypassAntiDebug, 2000);
});

// ==========================================
//  第七部分：工具函数
// ==========================================

/**
 * 工具函数：byte[] 转 hex 字符串
 */
function bytesToHex(bytes) {
    var hex = "";
    for (var i = 0; i < bytes.length; i++) {
        var b = bytes[i] & 0xFF;
        if (b < 0x10) {
            hex += "0";
        }
        hex += b.toString(16);
    }
    return hex;
}

/**
 * 工具函数：hex 字符串转 byte[]
 */
function hexToBytes(hex) {
    var bytes = [];
    for (var i = 0; i < hex.length; i += 2) {
        bytes.push(parseInt(hex.substr(i, 2), 16));
    }
    return bytes;
}

/**
 * 工具函数：打印 Java 堆栈
 * 用途：查看方法是被谁调用的，分析调用链
 */
function printStackTrace() {
    var Exception = Java.use("java.lang.Exception");
    var stack = Exception.$new().getStackTrace();
    console.log("    调用堆栈:");
    for (var i = 0; i < stack.length; i++) {
        console.log("        at " + stack[i].toString());
    }
}

/**
 * 工具函数：获取当前 Activity
 */
function getCurrentActivity() {
    var ActivityThread = Java.use("android.app.ActivityThread");
    var currentActivityThread = ActivityThread.currentActivityThread();
    var mActivities = currentActivityThread.mActivities.value;
    var keys = mActivities.keySet().toArray();

    for (var i = 0; i < keys.length; i++) {
        var record = mActivities.get(keys[i]);
        var activity = record.activity.value;
        if (activity !== null) {
            console.log("[*] 当前 Activity: " + activity.getClass().getName());
        }
    }
}

global.printStack = printStackTrace;
global.getCurrentActivity = getCurrentActivity;

/**
 * 工具函数：遍历所有已加载的类，搜索包含关键词的类
 */
function searchClasses(keyword) {
    console.log("[*] 搜索包含 '" + keyword + "' 的类...");
    var classes = Java.enumerateLoadedClassesSync();
    var count = 0;

    for (var i = 0; i < classes.length; i++) {
        if (classes[i].toLowerCase().indexOf(keyword.toLowerCase()) !== -1) {
            console.log("    " + classes[i]);
            count++;
        }
    }

    console.log("[+] 共找到 " + count + " 个类");
}

global.searchClasses = searchClasses;

/**
 * 工具函数：Hook 类的所有方法（调试用）
 */
function hookAllMethods(className) {
    console.log("[*] Hook 类 " + className + " 的所有方法");

    try {
        var clazz = Java.use(className);
        var methods = clazz.class.getDeclaredMethods();

        for (var i = 0; i < methods.length; i++) {
            var methodName = methods[i].getName();
            console.log("    Hook 方法: " + methodName);

            // 注意：这里简化处理，实际中需要处理重载方法
            // 可以使用 clazz[methodName].overloads 遍历所有重载
        }
    } catch (e) {
        console.log("[-] 失败: " + e.message);
    }
}

global.hookAllMethods = hookAllMethods;

// ==========================================
//  第八部分：综合实战案例 - 抓取登录签名
// ==========================================

/**
 * 综合案例：抓取 APP 的请求签名算法
 * 场景：APP 请求参数中有 sign 字段，需要找到签名算法并还原
 *
 * 分析思路：
 * 1. 抓包看到 sign 参数
 * 2. 搜索代码中的 "sign" 关键词
 * 3. Hook 可能的加密函数（MD5/SHA/AES/RSA）
 * 4. 对比加密结果和 sign 值
 * 5. 找到签名算法和密钥
 */
Java.perform(function () {
    console.log("\n========== [综合案例] 抓取请求签名 ==========");
    console.log("[*] 已加载所有 Hook 脚本，开始运行...");
    console.log("[*] 提示：可以在 frida 交互中调用以下函数：");
    console.log("    dumpDex()           - Dump 内存中的 DEX");
    console.log("    searchStr('关键词')  - 搜索内存字符串");
    console.log("    printStack()        - 打印当前 Java 堆栈");
    console.log("    getCurrentActivity() - 获取当前 Activity");
    console.log("    searchClasses('关键词') - 搜索类名");
    console.log("");
});

/*
 * ============================================================================
 *  使用说明总结
 *
 *  1. 基础使用：
 *     frida -U -f com.example.app -l frida_hook_examples.js --no-pause
 *
 *  2. Spawn 模式（启动时注入）：
 *     frida -U -f com.example.app -l script.js --no-pause
 *
 *  3. Attach 模式（附加到已运行进程）：
 *     frida -U com.example.app -l script.js
 *
 *  4. 常用 frida 命令：
 *     frida-ps -U           - 列出 USB 设备上的进程
 *     frida-ls-devices      - 列出所有设备
 *     frida-discover        - 发现目标进程的模块和函数
 *
 *  5. 注意事项：
 *     - 本脚本仅用于学习和安全研究，请勿用于非法用途
 *     - 使用前请修改包名、类名、方法名为目标应用的实际值
 *     - 不同版本的 Frida API 可能有差异，注意兼容性
 *     - 加固应用可能需要先脱壳才能 Hook 到目标类
 *
 *  6. 进阶学习：
 *     - Frida 官方文档: https://frida.re/docs/home/
 *     - Frida JavaScript API: https://frida.re/docs/javascript-api/
 *     - objection (Frida 封装工具): https://github.com/sensepost/objection
 *
 * ============================================================================
 */
