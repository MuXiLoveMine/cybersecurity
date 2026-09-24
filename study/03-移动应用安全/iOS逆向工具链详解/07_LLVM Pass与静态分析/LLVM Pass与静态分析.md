# LLVM Pass与静态分析

```python
# LLVM Pass用于静态分析iOS二进制文件
# 可以分析Mach-O文件中的安全漏洞

# 编写自定义LLVM Pass
# MyAnalysisPass.cpp
'''
#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Module.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

struct SecurityAnalysisPass : public ModulePass {
    static char ID;
    SecurityAnalysisPass() : ModulePass(ID) {}

    bool runOnModule(Module &M) override {
        for (auto &F : M) {
            // 检查危险函数调用
            if (F.getName().contains("system")) {
                errs() << "[!] Found system() call in: " << F.getName() << "\n";
            }
            if (F.getName().contains("exec")) {
                errs() << "[!] Found exec() call in: " << F.getName() << "\n";
            }
            if (F.getName().contains("sprintf")) {
                errs() << "[!] Found sprintf() (buffer overflow risk) in: " << F.getName() << "\n";
            }
        }
        return false;
    }
};
'''

# 使用静态分析工具
# 使用otool分析Mach-O
otool -L MyApp              # 查看链接库
otool -ov MyApp              # 查看ObjC类信息
otool -IV MyApp             # 查看符号表
otool -tv MyApp              # 反汇编text段

# 使用nm查看符号
nm -g MyApp                  # 全局符号
nm -m MyApp                  # Mach-O格式符号

# 使用strings提取字符串
strings -n 8 MyApp | grep -i 'password\|secret\|key\|token\|api'
strings -n 8 MyApp | grep -i 'http'
strings -n 8 MyApp | grep -i 'AES\|SHA\|RSA\|encrypt'

# 使用MachOView可视化分析
# 1. 加载二进制文件
# 2. 浏览Mach-O头部
# 3. 查看Load Commands
# 4. 分析段和节
# 5. 查看符号表
# 6. 分析动态绑定信息
```

---

---

