# stdlib.h - C 标准库

> C 标准库头文件，提供内存分配、类型转换、程序控制等功能。

---

## 一、引入

```c
#include <stdlib.h>
```

---

## 二、内存分配

### 2.1 malloc / free

```c
// malloc - 分配指定大小的内存（未初始化）
void *malloc(size_t size);

int *p = (int *)malloc(sizeof(int) * 10);  // 分配 10 个 int
if (p == NULL) {
    // 分配失败处理
    perror("malloc failed");
    exit(1);
}

// free - 释放内存
void free(void *ptr);

free(p);
p = NULL;  // ✅ 释放后置空，防止悬空指针

// 常见错误
free(p);
free(p);  // ❌ 双重释放（double free）
// 使用已释放的内存：use-after-free
```

### 2.2 calloc / realloc

```c
// calloc - 分配并初始化为 0
void *calloc(size_t nmemb, size_t size);

int *p = (int *)calloc(10, sizeof(int));  // 10 个 int，全部为 0

// realloc - 调整已分配内存的大小
void *realloc(void *ptr, size_t size);

int *p = (int *)malloc(sizeof(int) * 10);
// 扩展为 20 个 int
int *new_p = (int *)realloc(p, sizeof(int) * 20);
if (new_p != NULL) {
    p = new_p;  // ✅ 成功才更新指针
} else {
    // 失败时原指针仍然有效，需要处理
    free(p);
    exit(1);
}

// realloc(NULL, size) 等价于 malloc(size)
// realloc(ptr, 0) 等价于 free(ptr)（不推荐使用）
```

### 2.3 内存分配注意事项

```c
// ✅ 正确：检查 malloc 返回值
int *p = malloc(sizeof(int) * 100);
if (!p) {
    // 错误处理
}

// ❌ 错误：不检查返回值直接使用
int *p = malloc(sizeof(int) * 100);
p[0] = 1;  // 可能崩溃

// ✅ 正确：使用类型大小而非硬编码
int *p = malloc(10 * sizeof(int));     // 好
int *p = malloc(10 * sizeof(*p));      // 更好，类型变化时自动适配

// ❌ 整数溢出导致分配过小
size_t count = 0x100000000;  // 很大的数
int *p = malloc(count * sizeof(int));  // count * 4 溢出，分配很小的内存
// 然后写入大量数据，导致堆溢出

// 安全的分配（检查溢出）
size_t nmemb = 1000;
size_t size = sizeof(int);
if (nmemb != 0 && size > SIZE_MAX / nmemb) {
    // 溢出，分配失败
}
```

---

## 三、类型转换

### 3.1 字符串转数字

```c
// atoi - 字符串转整数（不推荐，无错误检测）
int atoi(const char *nptr);

int n = atoi("12345");   // 12345
int m = atoi("abc");     // 0（无法区分"0"和错误）
int x = atoi("99999999999999999");  // 溢出，未定义行为

// atol / atoll - long / long long
long atol(const char *nptr);
long long atoll(const char *nptr);

// strtol - 字符串转 long（推荐，有错误检测）
long strtol(const char *nptr, char **endptr, int base);

char *end;
long val = strtol("123abc", &end, 10);
// val = 123, end 指向 'a'

// 错误检测
#include <errno.h>
#include <limits.h>

errno = 0;
long val = strtol(str, &end, 10);

if (errno == ERANGE) {
    // 溢出
    if (val == LONG_MAX) printf("上溢\n");
    if (val == LONG_MIN) printf("下溢\n");
} else if (end == str) {
    printf("没有数字\n");
} else if (*end != '\0') {
    printf("部分转换，剩余: %s\n", end);
}

// strtoul - unsigned long
// strtoll / strtoull - long long / unsigned long long
// strtof / strtod / strtold - float / double / long double

// atof - 字符串转 double（不推荐）
double atof(const char *nptr);

// strtod - 推荐
double strtod(const char *nptr, char **endptr);
```

### 3.2 整数溢出

```c
/*
    整数溢出类型：
    1. 上溢 (overflow) - 超过最大值
    2. 下溢 (underflow) - 低于最小值
    3. 符号问题 - unsigned 和 signed 转换
*/

#include <limits.h>
#include <stdint.h>

// 无符号整数溢出：定义为模运算
unsigned int a = UINT_MAX;
a++;  // a = 0（回绕）

// 有符号整数溢出：未定义行为！
int b = INT_MAX;
b++;  // ❌ 未定义行为，可能崩溃或产生任意值

// 安全加法检查
int safe_add(int a, int b, int *result) {
    if ((b > 0 && a > INT_MAX - b) || 
        (b < 0 && a < INT_MIN - b)) {
        return -1;  // 溢出
    }
    *result = a + b;
    return 0;
}

// 安全乘法检查
int safe_mul(int a, int b, int *result) {
    if (a == 0 || b == 0) {
        *result = 0;
        return 0;
    }
    if (a > 0) {
        if (b > 0) {
            if (a > INT_MAX / b) return -1;
        } else {
            if (b < INT_MIN / a) return -1;
        }
    } else {
        if (b > 0) {
            if (a < INT_MIN / b) return -1;
        } else {
            if (a < INT_MAX / b) return -1;
        }
    }
    *result = a * b;
    return 0;
}
```

---

## 四、程序控制

### 4.1 exit / abort

```c
// exit - 正常退出程序
void exit(int status);

exit(0);    // 正常退出（EXIT_SUCCESS）
exit(1);    // 异常退出（EXIT_FAILURE）

// atexit - 注册退出时执行的函数
int atexit(void (*function)(void));

void cleanup1(void) { printf("清理 1\n"); }
void cleanup2(void) { printf("清理 2\n"); }

int main() {
    atexit(cleanup1);
    atexit(cleanup2);  // 先注册的后执行
    exit(0);
    // 输出：
    // 清理 2
    // 清理 1
}

// abort - 异常终止（产生 SIGABRT 信号）
void abort(void);
// 通常用于严重错误，不执行 atexit 注册的函数

// _Exit - 立即退出（不执行清理）
void _Exit(int status);
```

### 4.2 system / getenv

```c
// system - 执行 shell 命令
int system(const char *command);

system("ls -l");
system("pause");  // Windows 下暂停

// ❌ 安全警告：如果 command 包含用户输入，可能导致命令注入
// 例如：
// char cmd[100];
// sprintf(cmd, "ping %s", user_input);  // 危险！
// system(cmd);  // 可能被注入

// getenv - 获取环境变量
char *getenv(const char *name);

char *path = getenv("PATH");
if (path) {
    printf("PATH = %s\n", path);
}

// 安全注意：环境变量不可信，可能被攻击者控制
// 例如：LD_PRELOAD, LD_LIBRARY_PATH 等可用于提权
```

---

## 五、其他函数

### 5.1 排序与查找

```c
// qsort - 快速排序
void qsort(void *base, size_t nmemb, size_t size,
           int (*compar)(const void *, const void *));

int compare_ints(const void *a, const void *b) {
    return (*(int*)a - *(int*)b);
}

int arr[] = {5, 2, 8, 1, 9};
int n = sizeof(arr) / sizeof(arr[0]);
qsort(arr, n, sizeof(int), compare_ints);

// bsearch - 二分查找（数组必须已排序）
void *bsearch(const void *key, const void *base,
              size_t nmemb, size_t size,
              int (*compar)(const void *, const void *));

int key = 8;
int *found = bsearch(&key, arr, n, sizeof(int), compare_ints);
if (found) {
    printf("找到: %d\n", *found);
}
```

### 5.2 随机数

```c
// rand - 伪随机数（0 到 RAND_MAX）
int rand(void);

// srand - 设置随机种子
void srand(unsigned int seed);

// 用时间作为种子
#include <time.h>
srand(time(NULL));
int r = rand();

// 生成指定范围的随机数
int rand_range(int min, int max) {
    return min + rand() % (max - min + 1);
}

/*
    安全注意：
    - rand() 不是加密安全的随机数生成器
    - 不要用于安全相关的场景（密码、令牌等）
    - 安全场景用：arc4random (BSD), getrandom (Linux), CryptGenRandom (Windows)
*/
```

### 5.3 绝对值与除法

```c
// abs / labs / llabs - 整数绝对值
int abs(int j);
long labs(long j);
long long llabs(long long j);

abs(-5);  // 5

// div / ldiv / lldiv - 除法（返回商和余数）
div_t div(int numer, int denom);

div_t result = div(10, 3);
printf("商: %d, 余: %d\n", result.quot, result.rem);
// 商: 3, 余: 1
```

---

## 六、安全相关使用案例

### 6.1 检测堆溢出风险

```c
/*
    常见的堆相关漏洞：
    1. 堆溢出 (Heap Overflow) - 写入超出分配的大小
    2. Use-After-Free - 释放后继续使用
    3. Double Free - 重复释放
    4. 未初始化读取 - 读取未初始化的内存
*/

// ===== Use-After-Free 示例 =====
void uaf_example() {
    char *buf = malloc(64);
    strcpy(buf, "hello");
    free(buf);       // 释放
    
    printf("%s\n", buf);  // ❌ Use-After-Free！未定义行为
    // 攻击者可能在 free 后重新分配这块内存并控制内容
}

// ===== 安全写法 =====
void safe_example() {
    char *buf = malloc(64);
    if (!buf) return;
    
    strcpy(buf, "hello");
    free(buf);
    buf = NULL;  // ✅ 释放后置空
    
    // 现在使用 buf 会崩溃（空指针解引用）而不是 UAF
}

// ===== Double Free 示例 =====
void double_free_example() {
    char *p = malloc(64);
    free(p);
    // ... 一些代码 ...
    free(p);  // ❌ 双重释放！可能导致任意地址写
}

// ===== 未初始化内存 =====
void uninit_example() {
    char *buf = malloc(64);
    printf("%s\n", buf);  // ❌ 读取未初始化内存（信息泄露）
    // malloc 不会清零内存，可能包含之前的数据
    
    char *buf2 = calloc(1, 64);  // ✅ calloc 会清零
}
```

### 6.2 安全的内存分配包装

```c
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <errno.h>

// 安全的 malloc 包装
void *safe_malloc(size_t size) {
    if (size == 0) {
        return NULL;  // 避免零大小分配
    }
    
    void *p = malloc(size);
    if (!p) {
        perror("malloc failed");
        exit(EXIT_FAILURE);
    }
    return p;
}

// 安全的 realloc 包装
void *safe_realloc(void *ptr, size_t size) {
    void *new_ptr = realloc(ptr, size);
    if (!new_ptr && size != 0) {
        free(ptr);  // 失败时释放原内存（根据需要）
        perror("realloc failed");
        exit(EXIT_FAILURE);
    }
    return new_ptr;
}

// 带溢出检查的分配
void *safe_array_alloc(size_t nmemb, size_t size) {
    if (nmemb != 0 && size > SIZE_MAX / nmemb) {
        // 整数溢出
        errno = ENOMEM;
        return NULL;
    }
    return malloc(nmemb * size);
}

// 安全释放（自动置空）
#define SAFE_FREE(p) do { free(p); (p) = NULL; } while(0)

// 使用
void example() {
    int *p = safe_malloc(sizeof(int) * 10);
    // 使用 p...
    SAFE_FREE(p);  // 释放并置空
    // p 现在是 NULL
}
```

---

## 七、常见错误速查

| 错误 | 说明 |
|------|------|
| 不检查 malloc 返回值 | 可能空指针解引用 |
| 使用未初始化的内存 | 信息泄露、未定义行为 |
| 缓冲区溢出 | 覆盖相邻内存，可能被利用 |
| Use-After-Free | 释放后仍使用，堆利用 |
| Double Free | 重复释放，堆利用 |
| 内存泄漏 | 未 free，资源耗尽 |
| 整数溢出 | 分配过小，后续溢出 |
| 错误的 realloc 使用 | 失败时丢失原指针 |
