# 实战案例：使用AFL挖掘开源软件漏洞

### 9.1 目标选择

选择一个适合模糊测试的开源项目。以一个简单的XML解析器为例：

```c
// mini_xml_parser.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_DEPTH 100
#define MAX_ATTR_LEN 256

typedef struct {
    char name[64];
    char attributes[MAX_ATTR_LEN];
    int depth;
} XmlTag;

XmlTag tag_stack[MAX_DEPTH];
int stack_top = 0;

void parse_xml(const char *data, size_t size) {
    size_t i = 0;
    int in_tag = 0;
    int in_attr = 0;
    char tag_name[64];
    int tag_name_pos = 0;
    
    while (i < size) {
        if (data[i] == '<') {
            in_tag = 1;
            tag_name_pos = 0;
            i++;
            // 检查是否为结束标签
            if (i < size && data[i] == '/') {
                i++;
                // 弹出栈
                if (stack_top > 0) {
                    stack_top--;
                }
                // 跳过到>
                while (i < size && data[i] != '>') i++;
                if (i < size) i++;
                in_tag = 0;
                continue;
            }
        }
        
        if (in_tag) {
            if (data[i] == '>') {
                in_tag = 0;
                tag_name[tag_name_pos] = '\0';
                // 压栈
                if (stack_top < MAX_DEPTH) {
                    strncpy(tag_stack[stack_top].name, tag_name, 63);
                    tag_stack[stack_top].name[63] = '\0';
                    tag_stack[stack_top].depth = stack_top;
                    stack_top++;
                }
                i++;
                continue;
            }
            // 收集标签名
            if (tag_name_pos < 63) {
                tag_name[tag_name_pos++] = data[i];
            }
            i++;
        } else {
            // 文本内容，跳过
            i++;
        }
    }
}

// AFL入口
int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <input_file>\n", argv[0]);
        return 1;
    }
    
    FILE *f = fopen(argv[1], "rb");
    if (!f) return 1;
    
    fseek(f, 0, SEEK_END);
    long size = ftell(f);
    fseek(f, 0, SEEK_SET);
    
    char *buf = (char *)malloc(size + 1);
    if (!buf) { fclose(f); return 1; }
    
    fread(buf, 1, size, f);
    buf[size] = '\0';
    fclose(f);
    
    parse_xml(buf, size);
    
    free(buf);
    return 0;
}
```

### 9.2 编译与配置

```bash
# 1. 使用AFL编译器编译
export CC=afl-clang-fast
export CXX=afl-clang-fast++

# 启用ASan以检测内存错误
export AFL_USE_ASAN=1

# 编译
afl-clang-fast -g -O1 -o mini_xml_parser mini_xml_parser.c

# 2. 准备语料库
mkdir -p input
# 生成初始种子
cat > input/seed1.xml << 'EOF'
<root><child>text</child></root>
EOF

cat > input/seed2.xml << 'EOF'
<doc attr="value"><item id="1"/></doc>
EOF

cat > input/seed3.xml << 'EOF'
<data><a><b><c>deep</c></b></a></data>
EOF

# 3. 最小化语料库
afl-cmin -i input/ -o input_min/ -- ./mini_xml_parser @@

# 4. 创建字典
cat > xml.dict << 'EOF'
keyword_lt = "<"
keyword_gt = ">"
keyword_slash = "/"
keyword_lt_slash = "</"
keyword_xml = "<?xml"
keyword_encoding = "encoding="
keyword_utf8 = "\"UTF-8\""
keyword_version = "version="
keyword_1_0 = "\"1.0\""
keyword_cdata = "<![CDATA["
keyword_cdata_end = "]]>"
keyword_comment = "<!--"
keyword_comment_end = "-->"
EOF
```

### 9.3 启动模糊测试

```bash
# 单核运行
afl-fuzz -i input_min/ -o output/ -x xml.dict -t 500 -- ./mini_xml_parser @@

# 多核并行运行
# 终端1: 主节点
afl-fuzz -i input_min/ -o output/ -M main -x xml.dict -t 500 -- ./mini_xml_parser @@

# 终端2: 从节点
afl-fuzz -i input_min/ -o output/ -S sub1 -x xml.dict -t 500 -- ./mini_xml_parser @@

# 终端3: 从节点（启用MSan检查未初始化内存）
export AFL_USE_MSAN=1
afl-clang-fast -g -O1 -o mini_xml_parser_msan mini_xml_parser.c
afl-fuzz -i input_min/ -o output/ -S sub2 -x xml.dict -t 500 -- ./mini_xml_parser_msan @@
```

### 9.4 崩溃分析

假设AFL发现了一个崩溃：

```bash
# 查看崩溃
ls output/crashes/

# 重现崩溃
./mini_xml_parser output/crashes/id:000001,sig:06,src:000002,op:havoc,rep:4

# 使用gdb分析
gdb -ex run -ex bt --args ./mini_xml_parser output/crashes/id:000001,sig:06

# 使用ASan版本重现
./mini_xml_parser_asan output/crashes/id:000001,sig:06

# 最小化崩溃输入
afl-tmin -i output/crashes/id:000001,sig:06 -o crash_min -- ./mini_xml_parser @@
```

**ASan报告分析：**

```
==12345==ERROR: AddressSanitizer: heap-buffer-overflow
READ of size 1 at 0x602000000020

#0 0x4f5b28 in parse_xml mini_xml_parser.c:35
#1 0x4f5c10 in main mini_xml_parser.c:80

0x602000000020 is located 0 bytes to the right of 32-byte region [0x602000000000,0x602000000020)
allocated by thread T0 here:
    #0 0x4b6a90 in malloc
    #1 0x4f5a00 in main mini_xml_parser.c:76

SUMMARY: AddressSanitizer: heap-buffer-overflow
```

分析结果：`tag_name`数组在收集标签名时没有正确检查边界，导致堆缓冲区溢出。

### 9.5 修复漏洞

```c
// 修复：添加边界检查
void parse_xml(const char *data, size_t size) {
    size_t i = 0;
    int in_tag = 0;
    char tag_name[64];
    size_t tag_name_pos = 0;  // 改为size_t
    
    while (i < size) {
        if (data[i] == '<') {
            in_tag = 1;
            tag_name_pos = 0;  // 重置
            i++;
            if (i < size && data[i] == '/') {
                i++;
                if (stack_top > 0) stack_top--;
                while (i < size && data[i] != '>') i++;
                if (i < size) i++;
                in_tag = 0;
                continue;
            }
        }
        
        if (in_tag) {
            if (data[i] == '>') {
                in_tag = 0;
                // 修复：确保null终止
                tag_name[tag_name_pos] = '\0';
                if (stack_top < MAX_DEPTH) {
                    // 修复：使用安全的拷贝
                    strncpy(tag_stack[stack_top].name, tag_name, 63);
                    tag_stack[stack_top].name[63] = '\0';
                    tag_stack[stack_top].depth = stack_top;
                    stack_top++;
                }
                i++;
                continue;
            }
            // 修复：严格边界检查
            if (tag_name_pos < 63) {
                tag_name[tag_name_pos++] = data[i];
            }
            // 不再在超出边界时继续写入
            i++;
        } else {
            i++;
        }
    }
}
```

### 9.6 持续模糊测试

将模糊测试集成到开发流程中：

```bash
# CI/CD集成示例（.gitlab-ci.yml）
fuzz_test:
  stage: test
  script:
    # 编译ASan版本
    - export CC=afl-clang-fast
    - export AFL_USE_ASAN=1
    - afl-clang-fast -g -O1 -o mini_xml_parser_asan mini_xml_parser.c
    
    # 运行模糊测试（限时5分钟）
    - timeout 300 afl-fuzz -i input/ -o output/ -x xml.dict -V 300 -- ./mini_xml_parser_asan @@
    
    # 检查是否有崩溃
    - |
      if [ -n "$(ls output/crashes/ 2>/dev/null)" ]; then
        echo "发现崩溃！"
        ls output/crashes/
        exit 1
      fi
  artifacts:
    paths:
      - output/
    when: always
```

---

---

## 📋 内容审核与补充建议

> 针对「实战案例：使用AFL挖掘开源软件漏洞」部分的内容审核结果：

### 🔧 工具推荐
- ⚠️ 缺少tools相关内容

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
