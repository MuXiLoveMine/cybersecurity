--[[
================================================================================
  字符串加密工具 - string_encrypt.lua
================================================================================
  功能说明：
    本脚本提供多种字符串加密/编码功能，用于安全研究和学习：
    1. XOR 异或加解密（对称加密）
    2. Base64 编解码
    3. 凯撒密码（Caesar Cipher）

  使用方法：
    lua string_encrypt.lua <功能> <参数...>

  示例：
    -- XOR 加密
    lua string_encrypt.lua xor "hello world" "secretkey"

    -- XOR 解密（XOR 是对称的，加密解密用同一个方法）
    lua string_encrypt.lua xor <加密结果> "secretkey"

    -- Base64 编码
    lua string_encrypt.lua base64_encode "hello world"

    -- Base64 解码
    lua string_encrypt.lua base64_decode "aGVsbG8gd29ybGQ="

    -- 凯撒密码加密（偏移量为 3）
    lua string_encrypt.lua caesar "hello world" 3

    -- 凯撒密码解密（偏移量为 -3）
    lua string_encrypt.lua caesar "khoor zruog" -3

  免责声明：
    本脚本仅供安全学习和研究使用，请勿用于非法用途。
    XOR 加密和凯撒密码均为弱加密算法，仅用于学习加密原理，
    不可用于生产环境中的敏感数据保护。
    使用本脚本造成的一切后果由使用者自行承担。
================================================================================
--]]

-- ============================================================
-- 工具函数：字符串转十六进制表示
-- ============================================================
function string_to_hex(str)
    local hex = ""
    for i = 1, #str do
        hex = hex .. string.format("%02x", string.byte(str, i))
    end
    return hex
end

-- ============================================================
-- 工具函数：十六进制字符串转普通字符串
-- ============================================================
function hex_to_string(hex)
    local str = ""
    for i = 1, #hex, 2 do
        local byte = tonumber(string.sub(hex, i, i + 1), 16)
        if byte then
            str = str .. string.char(byte)
        end
    end
    return str
end

-- ============================================================
-- XOR 异或加解密
-- 原理：将明文的每个字节与密钥的对应字节进行异或运算
--       因为 XOR 的对称性，加密和解密使用相同的算法
-- 参数：
--   plaintext - 明文/密文字符串
--   key       - 密钥字符串
-- 返回：加密/解密后的字符串
-- ============================================================
function xor_encrypt(plaintext, key)
    if #key == 0 then
        error("密钥不能为空")
    end

    local result = ""
    local key_len = #key

    -- 遍历明文字符串的每个字符
    for i = 1, #plaintext do
        -- 获取当前明文字符的 ASCII 值
        local plain_byte = string.byte(plaintext, i)
        -- 获取对应密钥字符的 ASCII 值（循环使用密钥）
        local key_byte = string.byte(key, ((i - 1) % key_len) + 1)
        -- 异或运算
        local cipher_byte = bitXOR(plain_byte, key_byte)
        -- 转换为字符并拼接到结果中
        result = result .. string.char(cipher_byte)
    end

    return result
end

-- ============================================================
-- Base64 编码表
-- ============================================================
local base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

-- ============================================================
-- Base64 编码
-- 原理：将 3 个 8 位字节转换为 4 个 6 位字符，不足时用 = 填充
-- 参数：
--   data - 待编码的字符串
-- 返回：Base64 编码后的字符串
-- ============================================================
function base64_encode(data)
    local result = ""
    local len = #data
    local padding = 0

    -- 每 3 个字节为一组进行处理
    for i = 1, len, 3 do
        -- 获取 3 个字节（不足时补 0）
        local b1 = string.byte(data, i)
        local b2 = i + 1 <= len and string.byte(data, i + 1) or 0
        local b3 = i + 2 <= len and string.byte(data, i + 2) or 0

        -- 计算剩余字节数，用于确定填充数量
        local remaining = len - i + 1
        if remaining == 1 then
            padding = 2
        elseif remaining == 2 then
            padding = 1
        end

        -- 将 3 个 8 位字节组合成 24 位整数
        local n = b1 * 65536 + b2 * 256 + b3

        -- 拆分成 4 个 6 位索引
        local c1 = math.floor(n / 262144) % 64  -- 第 1 个 6 位
        local c2 = math.floor(n / 4096) % 64    -- 第 2 个 6 位
        local c3 = math.floor(n / 64) % 64      -- 第 3 个 6 位
        local c4 = n % 64                        -- 第 4 个 6 位

        -- 根据索引从编码表中取出字符
        result = result .. string.sub(base64_chars, c1 + 1, c1 + 1)
        result = result .. string.sub(base64_chars, c2 + 1, c2 + 1)

        -- 根据填充情况添加后两个字符或 =
        if padding < 2 then
            result = result .. string.sub(base64_chars, c3 + 1, c3 + 1)
        else
            result = result .. "="
        end

        if padding < 1 then
            result = result .. string.sub(base64_chars, c4 + 1, c4 + 1)
        else
            result = result .. "="
        end
    end

    return result
end

-- ============================================================
-- Base64 解码
-- 参数：
--   data - Base64 编码的字符串
-- 返回：解码后的原始字符串
-- ============================================================
function base64_decode(data)
    -- 移除所有空白字符
    data = string.gsub(data, "%s", "")

    -- 构建反向查找表（字符 -> 索引值）
    local reverse_table = {}
    for i = 1, #base64_chars do
        reverse_table[string.sub(base64_chars, i, i)] = i - 1
    end

    local result = ""
    local len = #data
    local padding = 0

    -- 统计填充字符数量
    if string.sub(data, -1) == "=" then
        padding = padding + 1
    end
    if string.sub(data, -2, -2) == "=" then
        padding = padding + 1
    end

    -- 每 4 个字符为一组进行处理
    for i = 1, len, 4 do
        -- 获取 4 个字符的索引值
        local c1 = reverse_table[string.sub(data, i, i)] or 0
        local c2 = reverse_table[string.sub(data, i + 1, i + 1)] or 0
        local c3 = reverse_table[string.sub(data, i + 2, i + 2)] or 0
        local c4 = reverse_table[string.sub(data, i + 3, i + 3)] or 0

        -- 将 4 个 6 位值组合成 24 位整数
        local n = c1 * 262144 + c2 * 4096 + c3 * 64 + c4

        -- 拆分成 3 个 8 位字节
        local b1 = math.floor(n / 65536) % 256
        local b2 = math.floor(n / 256) % 256
        local b3 = n % 256

        -- 根据填充情况决定输出多少字节
        result = result .. string.char(b1)
        if i + 2 <= len - padding then
            result = result .. string.char(b2)
        end
        if i + 3 <= len - padding then
            result = result .. string.char(b3)
        end
    end

    return result
end

-- ============================================================
-- 凯撒密码
-- 原理：将字母表中的每个字母偏移指定数量的位置
--       非字母字符保持不变
-- 参数：
--   text  - 明文/密文字符串
--   shift - 偏移量（正数加密，负数解密）
-- 返回：加密/解密后的字符串
-- ============================================================
function caesar_cipher(text, shift)
    local result = ""

    -- 确保偏移量在 0-25 范围内
    shift = shift % 26

    for i = 1, #text do
        local char = string.sub(text, i, i)
        local byte = string.byte(char)

        if byte >= string.byte("A") and byte <= string.byte("Z") then
            -- 大写字母
            local new_byte = ((byte - string.byte("A") + shift) % 26) + string.byte("A")
            result = result .. string.char(new_byte)
        elseif byte >= string.byte("a") and byte <= string.byte("z") then
            -- 小写字母
            local new_byte = ((byte - string.byte("a") + shift) % 26) + string.byte("a")
            result = result .. string.char(new_byte)
        else
            -- 非字母字符保持不变
            result = result .. char
        end
    end

    return result
end

-- ============================================================
-- 位运算：XOR（兼容 Lua 5.1/5.2/5.3）
-- ============================================================
function bitXOR(a, b)
    -- Lua 5.3+ 内置了位运算
    if _VERSION >= "Lua 5.3" then
        return a ~ b
    end

    -- 低版本 Lua 手动实现 XOR
    local result = 0
    local bitval = 1
    while a > 0 or b > 0 do
        local a_bit = a % 2
        local b_bit = b % 2
        if a_bit ~= b_bit then
            result = result + bitval
        end
        a = math.floor(a / 2)
        b = math.floor(b / 2)
        bitval = bitval * 2
    end
    return result
end

-- ============================================================
-- 打印帮助信息
-- ============================================================
function print_help()
    print("================================================")
    print("  字符串加密工具 - 安全研究用")
    print("================================================")
    print("")
    print("用法: lua string_encrypt.lua <功能> <参数...>")
    print("")
    print("可用功能:")
    print("  xor <字符串> <密钥>           - XOR 异或加解密")
    print("  base64_encode <字符串>         - Base64 编码")
    print("  base64_decode <字符串>         - Base64 解码")
    print("  caesar <字符串> <偏移量>       - 凯撒密码加解密")
    print("  help                           - 显示帮助信息")
    print("")
    print("示例:")
    print("  lua string_encrypt.lua xor \"hello\" \"key\"")
    print("  lua string_encrypt.lua base64_encode \"hello world\"")
    print("  lua string_encrypt.lua caesar \"hello\" 3")
    print("================================================")
end

-- ============================================================
-- 主程序入口
-- ============================================================
function main()
    local args = {...}

    -- 没有参数时显示帮助
    if #args == 0 or args[1] == "help" or args[1] == "-h" or args[1] == "--help" then
        print_help()
        return
    end

    local command = args[1]

    if command == "xor" then
        -- XOR 加解密
        if #args < 3 then
            print("[错误] XOR 功能需要两个参数：字符串和密钥")
            print("用法: lua string_encrypt.lua xor <字符串> <密钥>")
            return
        end
        local text = args[2]
        local key = args[3]
        local result = xor_encrypt(text, key)
        print("[XOR 加解密结果]")
        print("  原始字符串: " .. text)
        print("  密钥:       " .. key)
        print("  结果(十六进制): " .. string_to_hex(result))
        print("  提示: XOR 是对称加密，用相同密钥再次运算可还原明文")

    elseif command == "base64_encode" then
        -- Base64 编码
        if #args < 2 then
            print("[错误] 请提供要编码的字符串")
            return
        end
        local text = args[2]
        local result = base64_encode(text)
        print("[Base64 编码结果]")
        print("  原始字符串: " .. text)
        print("  编码结果:   " .. result)

    elseif command == "base64_decode" then
        -- Base64 解码
        if #args < 2 then
            print("[错误] 请提供要解码的字符串")
            return
        end
        local text = args[2]
        local result = base64_decode(text)
        print("[Base64 解码结果]")
        print("  编码字符串: " .. text)
        print("  解码结果:   " .. result)

    elseif command == "caesar" then
        -- 凯撒密码
        if #args < 3 then
            print("[错误] 凯撒密码需要两个参数：字符串和偏移量")
            print("用法: lua string_encrypt.lua caesar <字符串> <偏移量>")
            return
        end
        local text = args[2]
        local shift = tonumber(args[3])
        if not shift then
            print("[错误] 偏移量必须是数字")
            return
        end
        local result = caesar_cipher(text, shift)
        print("[凯撒密码结果]")
        print("  原始字符串: " .. text)
        print("  偏移量:     " .. shift)
        print("  结果:       " .. result)

    else
        print("[错误] 未知功能: " .. command)
        print("输入 'lua string_encrypt.lua help' 查看帮助")
    end
end

-- 运行主程序
main(...)
