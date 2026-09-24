# push_pop

> **分类**：栈操作
> **说明**：入栈和出栈指令

---

## 语法

```nasm
push source\npop destination
```

## 栈方向

栈从高地址向低地址增长

## 相关指令

pushad/popad / pushfd/popfd / leave / enter

## 示例代码

```nasm
; ===== 基本栈操作 =====

; push - 入栈
push eax             ; eax 入栈（esp -= 4, [esp] = eax）
push 123             ; 立即数入栈
push dword [var]     ; 内存值入栈
push ebp             ; 寄存器入栈

; pop - 出栈
pop eax              ; eax = [esp], esp += 4
pop ebx              ; ebx = [esp]
pop dword [buf]      ; 出栈到内存

; ===== 栈帧结构 =====

; 标准函数序言（prologue）
my_function:
    push ebp         ; 保存旧的 ebp
    mov  ebp, esp    ; ebp 指向当前栈顶
    sub  esp, 16     ; 分配16字节局部变量空间
    push ebx         ; 保存被调用者保存寄存器
    push esi
    push edi

    ; 函数体...
    ; [ebp+8]  = 第一个参数
    ; [ebp+12] = 第二个参数
    ; [ebp-4]  = 第一个局部变量
    ; [ebp-8]  = 第二个局部变量

    ; 函数尾声（epilogue）
    pop  edi
    pop  esi
    pop  ebx
    mov  esp, ebp    ; 释放局部变量空间
    pop  ebp         ; 恢复 ebp
    ret              ; 返回

; leave 指令等价于:
;   mov esp, ebp
;   pop ebp
leave
ret

; ===== pushad / popad =====
; 保存/恢复所有通用寄存器（顺序: EAX, ECX, EDX, EBX, ESP, EBP, ESI, EDI）
pushad               ; 所有寄存器入栈
; ... 修改寄存器 ...
popad                ; 恢复所有寄存器

; ===== pushfd / popfd =====
; 保存/恢复 EFLAGS 寄存器
pushfd               ; 标志寄存器入栈
pop eax              ; 弹出到 eax
or eax, 0x100        ; 设置 TF 位（陷阱标志）
push eax
popfd                ; 恢复标志寄存器

; ===== enter 指令 =====
; enter N, 0 等价于:
;   push ebp
;   mov ebp, esp
;   sub esp, N
enter 16, 0
; ... 函数体
leave
ret

; ===== 栈使用示例 =====

; 调用有参数的函数（cdecl 调用约定）
push 3               ; 参数2
push 2               ; 参数1
call add_numbers     ; 调用函数
add esp, 8           ; 调用者清理栈（cdecl）

add_numbers:
    push ebp
    mov ebp, esp
    mov eax, [ebp+8]   ; 第一个参数
    add eax, [ebp+12]  ; 加上第二个参数
    pop ebp
    ret

; ===== 栈增长方向验证 =====
; 栈从高地址向低地址增长
; push 时 esp 减小
; pop 时 esp 增大
; ebp 指向栈帧底部（高地址）
; esp 指向栈顶（低地址）
```
