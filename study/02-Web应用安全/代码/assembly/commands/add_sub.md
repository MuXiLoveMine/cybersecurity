# add_sub

> **分类**：算术运算
> **说明**：加法和减法指令

---

## 语法

```nasm
add dest, src   ; dest += src\nsub dest, src   ; dest -= src
```

## 相关指令

inc / dec / adc / sbb / mul / imul / div / idiv / neg

## 标志位

影响 OF/SF/ZF/AF/PF/CF

## 示例代码

```nasm
; ===== 加法 =====

; add - 加法
add eax, 10          ; eax += 10
add al, bl           ; al += bl
add [var], ecx       ; var += ecx
add dword [num], 1   ; num += 1

; adc - 带进位加法（用于多精度运算）
; 64位加法：edx:eax += ebx:ecx
add eax, ecx         ; 低32位相加
adc edx, ebx         ; 高32位相加 + 进位

; inc - 自增1
inc eax              ; eax++
inc byte [counter]   ; counter++
; inc 不影响 CF 标志

; ===== 减法 =====

; sub - 减法
sub eax, 5           ; eax -= 5
sub al, bl           ; al -= bl
sub [var], edx       ; var -= edx

; sbb - 带借位减法
; 64位减法：edx:eax -= ebx:ecx
sub eax, ecx         ; 低32位相减
sbb edx, ebx         ; 高32位相减 - 借位

; dec - 自减1
dec eax              ; eax--
dec dword [count]    ; count--
; dec 不影响 CF 标志

; neg - 取负
neg eax              ; eax = -eax
; 0 - eax，影响所有标志位

; cmp - 比较（sub 但不保存结果，只改标志）
cmp eax, 10          ; eax - 10
jz equal_label       ; 相等则跳转
jg greater_label     ; 大于则跳转

; ===== 乘法 =====

; mul - 无符号乘法
; 8位: al * src -> ax
; 16位: ax * src -> dx:ax
; 32位: eax * src -> edx:eax
mov al, 10
mov bl, 20
mul bl               ; ax = 200

; imul - 有符号乘法
imul ebx             ; eax * ebx -> edx:eax
imul eax, ebx, 100   ; eax = ebx * 100（三操作数形式）
imul eax, ebx        ; eax *= ebx

; ===== 除法 =====

; div - 无符号除法
; 被除数: ax / dx:ax / edx:eax
; 除数: src
; 商: al / ax / eax
; 余数: ah / dx / edx
mov eax, 100
mov ebx, 7
xor edx, edx         ; edx 清0（高32位）
div ebx              ; eax = 14, edx = 2

; idiv - 有符号除法
; 符号扩展
mov eax, -100
cdq                  ; 把 eax 符号扩展到 edx:eax
mov ebx, 7
idiv ebx             ; eax = -14, edx = -2

; cbw: al -> ax
; cwde: ax -> eax
; cdq: eax -> edx:eax
```
