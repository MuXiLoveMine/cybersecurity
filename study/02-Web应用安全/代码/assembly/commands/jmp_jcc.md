# jmp_jcc

> **分类**：控制转移
> **说明**：跳转指令

---

## 语法

```nasm
jmp label\njcc label  ; 条件跳转
```

## 无条件跳转

jmp / call / ret

## 条件跳转

jz/je / jnz/jne / jg/jl / jge/jle / ja/jb / jae/jbe / jc/jnc / js/jns / jo/jno

## 标志位含义

ZF 零标志 / SF 符号标志 / OF 溢出标志 / CF 进位标志

## 示例代码

```nasm
; ===== 无条件跳转 =====

jmp start            ; 直接跳转
jmp eax              ; 间接跳转（跳转到 eax 中的地址）
jmp [func_ptr]       ; 内存间接跳转

; call - 调用函数
call my_function     ; 压入返回地址，跳转到函数
; 等价于:
; push eip+next
; jmp my_function

; ret - 从函数返回
ret                  ; 弹出返回地址，跳转回去
ret 8                ; 返回并弹出8字节参数（cdecl 不用）

; ===== 条件跳转（基于标志位） =====

; 零标志 ZF（相等/为零）
jz  equal_label      ; ZF=1，等于零/相等
je  equal_label      ; 同上（equal）
jnz not_equal        ; ZF=0，不等于零
jne not_equal        ; 同上

; 进位标志 CF（无符号小于/借位）
jc  carry_set        ; CF=1，有进位/借位
jnc carry_clear      ; CF=0

; 符号标志 SF（负数）
js  negative         ; SF=1，负数
jns positive         ; SF=0

; 溢出标志 OF
jo  overflow         ; OF=1，溢出
jno no_overflow      ; OF=0

; ===== 有符号数比较跳转 =====
; (假设先执行 cmp a, b)

jl  less             ; a < b  (SF != OF)
jle less_equal       ; a <= b (ZF=1 或 SF != OF)
jg  greater          ; a > b  (ZF=0 且 SF=OF)
jge greater_equal    ; a >= b (SF=OF)

; ===== 无符号数比较跳转 =====

jb  below            ; a < b  (CF=1)
jbe below_equal      ; a <= b (CF=1 或 ZF=1)
ja  above            ; a > b  (CF=0 且 ZF=0)
jae above_equal      ; a >= b (CF=0)

; ===== 示例：比较并跳转 =====

; 判断 eax == 10
cmp eax, 10
je  is_ten

; 判断 eax > ebx（有符号）
cmp eax, ebx
jg  eax_greater

; 判断 eax > ebx（无符号）
cmp eax, ebx
ja  eax_greater_unsigned

; ===== 循环指令 =====

; loop - ecx 自减，不为0则跳转
mov ecx, 10
loop_start:
    ; ... 循环体
    loop loop_start

; loope/loopz - ecx 自减，不为0且 ZF=1 则继续
; loopne/loopnz - ecx 自减，不为0且 ZF=0 则继续

; jcxz - cx 为0则跳转
; jecxz - ecx 为0则跳转
```
