# mov

> **分类**：数据传送
> **说明**：数据传送指令（最常用）

---

## 语法

```nasm
mov destination, source
```

## 操作数类型

寄存器 / 内存 / 立即数

## 注意

两个操作数不能同时是内存\n大小必须匹配\n不影响标志位

## 示例代码

```nasm
; ===== 基本 mov 指令 =====

; 立即数 -> 寄存器
mov eax, 10          ; eax = 10
mov al, 'A'          ; al = 0x41
mov ebx, 0x8048000   ; ebx = 地址

; 寄存器 -> 寄存器
mov eax, ebx         ; eax = ebx
mov al, bl           ; al = bl

; 内存 -> 寄存器
mov eax, [var]       ; eax = var 的值
mov eax, [ebx]       ; eax = ebx 指向的内存值
mov eax, [esi+4]     ; 基址+偏移
mov eax, [ebx+ecx]   ; 基址+索引
mov eax, [ebx+ecx*4] ; 基址+索引*比例

; 寄存器 -> 内存
mov [var], eax       ; var = eax
mov [ebx], al        ; ebx 指向的字节 = al
mov [esi+8], ecx     ; esi+8 处 = ecx

; 立即数 -> 内存
mov dword [var], 100 ; var = 100（双字）
mov byte [buf], 0    ; buf 处清0

; ===== 其他数据传送指令 =====

; xchg - 交换
xchg eax, ebx        ; 交换 eax 和 ebx
xchg [var], ecx      ; 交换内存和寄存器

; push / pop
push eax             ; eax 入栈
pop ebx              ; 栈顶弹出到 ebx

pushad               ; 所有通用寄存器入栈
popad                ; 弹出所有通用寄存器

pushfd               ; 标志寄存器入栈
popfd                ; 弹出标志寄存器

; lea - 加载有效地址（计算地址，不访问内存）
lea eax, [ebx+ecx*4+8]  ; eax = ebx + ecx*4 + 8
; 常用于算术计算，如 lea ebx, [eax+eax*2] = ebx = eax*3

; movsx / movzx - 带扩展传送
movsx eax, al        ; 符号扩展（有符号数扩展）
movzx eax, al        ; 零扩展（无符号数扩展）

; xlat - 查表转换
; al = 表[ebx + al]
mov ebx, table
mov al, 2
xlat                 ; al = table[2]
```
