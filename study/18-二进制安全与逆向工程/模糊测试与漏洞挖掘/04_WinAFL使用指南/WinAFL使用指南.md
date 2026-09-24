# WinAFL使用指南

WinAFL是AFL在Windows平台的移植版，使用DynamoRIO进行动态二进制插桩，可以对闭源Windows软件进行模糊测试。

**安装：**

```powershell
# 1. 下载DynamoRIO
# https://github.com/DynamoRIO/dynamorio/releases
# 解压到 C:\DynamoRIO

# 2. 下载WinAFL
git clone https://github.com/googleprojectzero/winafl.git
cd winafl

# 3. 编译
# 使用Visual Studio Developer Command Prompt
mkdir build64
cd build64
cmake -G"Visual Studio 17 2022" -A x64 .. -DDynamoRIO_DIR=C:\DynamoRIO\cmake
cmake --build . --config Release
```

**基本使用：**

```powershell
# 基本命令
# -target_method: 目标函数名
# -fuzz_iterations: 每次进程执行的迭代次数
# -nargs: 参数个数
# -instrumentation_type: 插桩类型

afl-fuzz.exe -in -out -t 5000 ^
    -target_method fuzz_target ^
    -fuzz_iterations 1000 ^
    -nargs 2 ^
    -instrumentation_type drmemory ^
    -- target.exe @@

# 对带参数的程序
afl-fuzz.exe -i input -o output ^
    -target_method ParseFile ^
    -fuzz_iterations 1000 ^
    -nargs 2 ^
    -- target.exe -input @@
```

**编写WinAFL Harness：**

```c
// winafl_harness.c
#include <stdio.h>
#include <stdlib.h>
#include <windows.h>

// 目标函数（AFL在每次迭代中调用此函数）
__declspec(dllexport) int fuzz_target(const char *filename) {
    FILE *f = fopen(filename, "rb");
    if (!f) return -1;
    
    // 获取文件大小
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);
    
    if (size > 1024 * 1024) {  // 限制1MB
        fclose(f);
        return -1;
    }
    
    char *buf = (char *)malloc(size);
    if (!buf) {
        fclose(f);
        return -1;
    }
    
    fread(buf, 1, size, f);
    fclose(f);
    
    // 调用实际的解析函数
    // parse_data(buf, size);
    
    free(buf);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("Usage: %s <input_file>\n", argv[0]);
        return 1;
    }
    
    // 正常模式下执行一次
    fuzz_target(argv[1]);
    return 0;
}
```

---

---

