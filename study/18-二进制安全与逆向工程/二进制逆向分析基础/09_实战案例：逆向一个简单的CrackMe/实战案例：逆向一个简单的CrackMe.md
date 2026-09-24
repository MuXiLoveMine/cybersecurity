# 实战案例：逆向一个简单的CrackMe

### 9.1 目标程序介绍

假设有一个简单的CrackMe程序，用户需要输入正确的序列号。我们通过逆向分析找出正确的序列号。

**程序源码（模拟）：**

```c
#include <stdio.h>
#include <string.h>

int check_serial(const char *serial) {
    int i;
    int sum = 0;
    int len = strlen(serial);
    
    if (len != 8) {
        return 0;  // 序列号必须是8位
    }
    
    // 每个字符ASCII值相加
    for (i = 0; i < len; i++) {
        sum += serial[i];
    }
    
    // 和必须是800
    if (sum == 800) {
        return 1;  // 正确
    }
    return 0;
}

int main() {
    char input[64];
    printf("Enter serial: ");
    scanf("%63s", input);
    
    if (check_serial(input)) {
        printf("Correct!\n");
    } else {
        printf("Wrong!\n");
    }
    return 0;
}
```

### 9.2 分析步骤

**第一步：文件信息分析**

```bash
$ file crackme
crackme: ELF 32-bit LSB executable, Intel 80386, ...

$ checksec --file=crackme
[*] '/crackme'
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX disabled
    PIE:      No PIE
```

**第二步：字符串提取**

```bash
$ strings crackme | grep -i serial
Enter serial:
```

**第三步：IDA Pro分析**

在IDA中打开文件，定位到main函数：

```asm
; IDA反汇编视图
.text:0804846B main proc near
.text:0804846B     push ebp
.text:0804846C     mov ebp, esp
.text:0804846E     sub esp, 48h        ; 分配局部变量空间
.text:08048471     sub esp, 8
.text:08048474     lea eax, [ebp-40h]   ; input缓冲区地址
.text:08048477     push eax
.text:08048478     push offset format   ; "%63s"
.text:0804847D     call _scanf
.text:08048482     add esp, 10h
.text:08048485     lea eax, [ebp-40h]
.text:08048488     push eax             ; 参数: input
.text:08048489     call check_serial
.text:0804848E     add esp, 4
.text:08048491     test eax, eax
.text:08048493     jz short wrong       ; 返回0则跳到wrong
.text:08048495     push offset aCorrect  ; "Correct!"
.text:0804849A     call _printf
.text:0804849F     jmp short done
.text:080484A1 wrong:
.text:080484A1     push offset aWrong    ; "Wrong!"
.text:080484A6     call _printf
.text:080484AB done:
.text:080484AB     mov eax, 0
.text:080484B0     leave
.text:080484B1     retn
.text:080484B1 main endp
```

**分析check_serial函数：**

```asm
.text:08048400 check_serial proc near
.text:08048400     push ebp
.text:08048401     mov ebp, esp
.text:08048403     sub esp, 10h
.text:08048406     mov [ebp+var_C], 0    ; sum = 0
.text:0804840D     push eax              ; serial参数
.text:0804840E     call _strlen
.text:08048413     add esp, 4
.text:08048416     cmp eax, 8           ; 检查长度==8
.text:08048419     jz short loc_8048421
.text:0804841B     mov eax, 0            ; 返回0
.text:08048420     jmp short loc_804844F
.text:08048421 loc_8048421:
.text:08048421     mov [ebp-4], 0        ; i = 0
.text:08048428 loc_8048428:            ; 循环开始
.text:08048428     mov eax, [ebp-4]
.text:0804842B     cmp eax, 8           ; i < 8
.text:0804842D     jge short loc_8048440 ; 循环结束
.text:0804842F     mov eax, [ebp+arg_0] ; serial
.text:08048432     movzx eax, byte [eax]; serial[i]
.text:08048435     add eax, [ebp+var_C] ; sum += serial[i]
.text:08048438     mov [ebp+var_C], eax
.text:0804843B     add [ebp-4], 1       ; i++
.text:0804843E     jmp short loc_8048428
.text:08048440 loc_8048440:
.text:08048440     mov eax, [ebp+var_C]
.text:08048443     cmp eax, 320h        ; sum == 800 (0x320)
.text:08048448     jnz short loc_804844C
.text:0804844A     mov eax, 1           ; 返回1
.text:0804844F     retn
```

**F5反编译结果（Hex-Rays）：**

```c
int check_serial(const char *serial) {
    int i;
    int sum = 0;
    int len = strlen(serial);
    
    if (len != 8)
        return 0;
    
    for (i = 0; i < 8; ++i)
        sum += serial[i];
    
    if (sum == 0x320)  // 800
        return 1;
    
    return 0;
}
```

### 9.3 求解序列号

从分析结果可知：
1. 序列号长度为8
2. 8个字符的ASCII码之和为800
3. 800 / 8 = 100，每个字符平均ASCII值为100

ASCII 100对应的字符是'd'，所以一个可能的解是"dddddddd"。

**验证：**

```python
serial = "dddddddd"
print(f"长度: {len(serial)}")
print(f"ASCII和: {sum(ord(c) for c in serial)}")

# 输出:
# 长度: 8
# ASCII和: 800
```

### 9.4 使用动态调试验证

**使用gdb验证：**

```bash
$ gdb -q ./crackme
gdb> break *0x08048443     # 在比较sum==0x320处设断点
gdb> run
Enter serial: dddddddd

# 断点触发后
gdb> info registers eax
eax    0x320    800       # 确认sum=800
gdb> continue
Correct!
```

### 9.5 使用pwntools自动化

```python
from pwn import *

# 连接到程序
p = process('./crackme')

# 发送序列号
p.sendline(b'dddddddd')

# 接收结果
result = p.recvline()
print(f"结果: {result}")

# 验证
if b'Correct' in result:
    print("[+] 序列号正确!")
else:
    print("[-] 序列号错误")
```

### 9.6 总结

本案例展示了逆向分析的基本流程：
1. 文件格式分析了解程序基本信息
2. 字符串提取发现关键线索
3. 静态反汇编理解程序逻辑
4. 反编译获得可读伪代码
5. 数学分析求解正确输入
6. 动态调试验证分析结果

在实际分析中，程序可能会有更复杂的逻辑（加密、混淆、反调试等），但基本分析流程不变。

---

---

