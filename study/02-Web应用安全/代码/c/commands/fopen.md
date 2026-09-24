# fopen

> **分类**：文件操作
> **说明**：打开文件，返回文件指针
> **头文件**：`<stdio.h>`

---

## 语法

```c
FILE *fopen(const char *filename, const char *mode);
```

## 打开模式

- "r" - 只读（文件必须存在）
- "w" - 只写（清空已有内容）
- "a" - 追加（文件不存在则创建）
- "r+" - 读写（文件必须存在）
- "w+" - 读写（清空后读写）
- "a+" - 读写追加
- "rb" - 二进制读
- "wb" - 二进制写

## 示例代码

```c
#include <stdio.h>
#include <stdlib.h>

int main() {
    // 写入文件
    FILE *fw = fopen("test.txt", "w");
    if (fw == NULL) {
        perror("打开文件失败");
        return 1;
    }
    fprintf(fw, "Hello, World!\n");
    fprintf(fw, "第二行\n");
    fclose(fw);

    // 读取文件
    FILE *fr = fopen("test.txt", "r");
    if (fr == NULL) {
        perror("打开文件失败");
        return 1;
    }

    // 逐行读取
    char line[256];
    while (fgets(line, sizeof(line), fr)) {
        printf("%s", line);
    }
    fclose(fr);

    // 二进制文件
    // 写入
    int data[] = {1, 2, 3, 4, 5};
    FILE *fbw = fopen("data.bin", "wb");
    fwrite(data, sizeof(int), 5, fbw);
    fclose(fbw);

    // 读取
    int read_data[5];
    FILE *fbr = fopen("data.bin", "rb");
    fread(read_data, sizeof(int), 5, fbr);
    fclose(fbr);

    // 文件指针操作
    FILE *f = fopen("test.txt", "r");
    fseek(f, 0, SEEK_END);  // 移到末尾
    long size = ftell(f);   // 获取当前位置（即文件大小）
    printf("文件大小: %ld 字节\n", size);
    rewind(f);              // 回到开头
    fclose(f);

    return 0;
}
```
