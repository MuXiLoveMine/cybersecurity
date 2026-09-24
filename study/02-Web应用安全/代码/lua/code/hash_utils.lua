--[[
================================================================================
  哈希与编码工具 - hash_utils.lua
================================================================================
  功能说明：
    本脚本提供多种哈希和编码功能，用于安全研究和学习：
    1. MD5 摘要计算（纯 Lua 实现）
    2. SHA1 摘要计算（纯 Lua 实现）
    3. URL 编码/解码
    4. HTML 编码/解码
    5. 字符串转十六进制/十六进制转字符串

  使用方法：
    lua hash_utils.lua <功能> <参数...>

  示例：
    -- MD5 哈希
    lua hash_utils.lua md5 "hello world"

    -- SHA1 哈希
    lua hash_utils.lua sha1 "hello world"

    -- URL 编码
    lua hash_utils.lua url_encode "hello world?a=1&b=2"

    -- URL 解码
    lua hash_utils.lua url_decode "hello%20world%3Fa%3D1%26b%3D2"

    -- HTML 编码
    lua hash_utils.lua html_encode "<script>alert(1)</script>"

    -- HTML 解码
    lua hash_utils.lua html_decode "&lt;script&gt;alert(1)&lt;/script&gt;"

    -- 字符串转十六进制
    lua hash_utils.lua str2hex "hello"

    -- 十六进制转字符串
    lua hash_utils.lua hex2str "68656c6c6f"

  免责声明：
    本脚本仅供安全学习和研究使用，请勿用于非法用途。
    MD5 和 SHA1 已被证明存在碰撞漏洞，不可用于密码存储等安全场景。
    本实现为纯 Lua 教学版本，性能和安全性不适合生产环境。
    使用本脚本造成的一切后果由使用者自行承担。
================================================================================
--]]

-- ============================================================
-- 位运算工具函数（兼容 Lua 5.1+）
-- ============================================================
local bit = {}

function bit.band(a, b)
    if _VERSION >= "Lua 5.3" then return a & b end
    local result = 0
    local bitval = 1
    while a > 0 or b > 0 do
        if a % 2 == 1 and b % 2 == 1 then
            result = result + bitval
        end
        a = math.floor(a / 2)
        b = math.floor(b / 2)
        bitval = bitval * 2
    end
    return result
end

function bit.bor(a, b)
    if _VERSION >= "Lua 5.3" then return a | b end
    local result = 0
    local bitval = 1
    while a > 0 or b > 0 do
        if a % 2 == 1 or b % 2 == 1 then
            result = result + bitval
        end
        a = math.floor(a / 2)
        b = math.floor(b / 2)
        bitval = bitval * 2
    end
    return result
end

function bit.bxor(a, b)
    if _VERSION >= "Lua 5.3" then return a ~ b end
    local result = 0
    local bitval = 1
    while a > 0 or b > 0 do
        if a % 2 ~= b % 2 then
            result = result + bitval
        end
        a = math.floor(a / 2)
        b = math.floor(b / 2)
        bitval = bitval * 2
    end
    return result
end

function bit.bnot(a)
    if _VERSION >= "Lua 5.3" then return ~a & 0xFFFFFFFF end
    return 0xFFFFFFFF - a
end

function bit.lshift(a, n)
    if _VERSION >= "Lua 5.3" then return (a << n) & 0xFFFFFFFF end
    return (a * 2^n) % 2^32
end

function bit.rshift(a, n)
    if _VERSION >= "Lua 5.3" then return a >> n end
    return math.floor(a / 2^n)
end

function bit.rol(a, n)
    n = n % 32
    return bit.bor(bit.lshift(a, n), bit.rshift(a, 32 - n))
end

-- ============================================================
-- MD5 哈希算法（纯 Lua 实现）
-- 参考 RFC 1321 标准实现
-- 参数：
--   msg - 输入字符串
-- 返回：32 位十六进制 MD5 哈希值
-- ============================================================
function md5(msg)
    -- 初始化常量
    local s = {
        7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,
        5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,
        4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,
        6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21
    }

    local K = {}
    for i = 0, 63 do
        K[i + 1] = math.floor(math.abs(math.sin(i + 1)) * 2^32) % 2^32
    end

    -- 初始化哈希值
    local a0 = 0x67452301
    local b0 = 0xEFCDAB89
    local c0 = 0x98BADCFE
    local d0 = 0x10325476

    -- 预处理：添加填充位
    local orig_len = #msg
    msg = msg .. string.char(0x80)  -- 添加 1 位和 0 填充

    -- 填充到 56 mod 64 字节
    while (#msg % 64) ~= 56 do
        msg = msg .. string.char(0)
    end

    -- 添加原始长度（小端序，64 位）
    local bit_len = orig_len * 8
    for i = 0, 7 do
        msg = msg .. string.char(bit.band(bit.rshift(bit_len, i * 8), 0xFF))
    end

    -- 处理每个 512 位（64 字节）分组
    for offset = 0, #msg - 1, 64 do
        -- 将分组拆分为 16 个 32 位小端字
        local M = {}
        for i = 0, 15 do
            local idx = offset + i * 4 + 1
            M[i + 1] = string.byte(msg, idx)
                     + bit.lshift(string.byte(msg, idx + 1), 8)
                     + bit.lshift(string.byte(msg, idx + 2), 16)
                     + bit.lshift(string.byte(msg, idx + 3), 24)
        end

        local A = a0
        local B = b0
        local C = c0
        local D = d0

        -- 主循环（64 轮）
        for i = 0, 63 do
            local F, g
            if i < 16 then
                F = bit.bor(bit.band(B, C), bit.band(bit.bnot(B), D))
                g = i
            elseif i < 32 then
                F = bit.bor(bit.band(D, B), bit.band(bit.bnot(D), C))
                g = (5 * i + 1) % 16
            elseif i < 48 then
                F = bit.bxor(bit.bxor(B, C), D)
                g = (3 * i + 5) % 16
            else
                F = bit.bxor(C, bit.bor(B, bit.bnot(D)))
                g = (7 * i) % 16
            end

            F = bit.band(F + D + K[i + 1] + M[g + 1], 0xFFFFFFFF)
            D = C
            C = B
            B = bit.band(B + bit.rol(F, s[i + 1]), 0xFFFFFFFF)
            A = D
        end

        a0 = bit.band(a0 + A, 0xFFFFFFFF)
        b0 = bit.band(b0 + B, 0xFFFFFFFF)
        c0 = bit.band(c0 + C, 0xFFFFFFFF)
        d0 = bit.band(d0 + D, 0xFFFFFFFF)
    end

    -- 将结果转换为小端序十六进制字符串
    local function to_hex_le(val)
        local hex = ""
        for i = 0, 3 do
            hex = hex .. string.format("%02x", bit.band(bit.rshift(val, i * 8), 0xFF))
        end
        return hex
    end

    return to_hex_le(a0) .. to_hex_le(b0) .. to_hex_le(c0) .. to_hex_le(d0)
end

-- ============================================================
-- SHA1 哈希算法（纯 Lua 实现）
-- 参考 RFC 3174 标准实现
-- 参数：
--   msg - 输入字符串
-- 返回：40 位十六进制 SHA1 哈希值
-- ============================================================
function sha1(msg)
    -- 初始化哈希值（大端序）
    local h0 = 0x67452301
    local h1 = 0xEFCDAB89
    local h2 = 0x98BADCFE
    local h3 = 0x10325476
    local h4 = 0xC3D2E1F0

    -- 预处理
    local orig_len = #msg
    msg = msg .. string.char(0x80)

    while (#msg % 64) ~= 56 do
        msg = msg .. string.char(0)
    end

    -- 添加长度（大端序，64 位）
    local bit_len = orig_len * 8
    local high_len = math.floor(bit_len / 2^32)
    local low_len = bit_len % 2^32
    for i = 3, 0, -1 do
        msg = msg .. string.char(bit.band(bit.rshift(high_len, i * 8), 0xFF))
    end
    for i = 3, 0, -1 do
        msg = msg .. string.char(bit.band(bit.rshift(low_len, i * 8), 0xFF))
    end

    -- 处理每个 512 位分组
    for offset = 0, #msg - 1, 64 do
        -- 将分组拆分为 16 个 32 位大端字
        local w = {}
        for i = 0, 15 do
            local idx = offset + i * 4 + 1
            w[i + 1] = bit.lshift(string.byte(msg, idx), 24)
                     + bit.lshift(string.byte(msg, idx + 1), 16)
                     + bit.lshift(string.byte(msg, idx + 2), 8)
                     + string.byte(msg, idx + 3)
        end

        -- 扩展到 80 个字
        for i = 17, 80 do
            w[i] = bit.rol(bit.bxor(bit.bxor(bit.bxor(w[i-3], w[i-8]), w[i-14]), w[i-16]), 1)
        end

        local A = h0
        local B = h1
        local C = h2
        local D = h3
        local E = h4

        -- 主循环（80 轮）
        for i = 1, 80 do
            local F, K
            if i <= 20 then
                F = bit.bor(bit.band(B, C), bit.band(bit.bnot(B), D))
                K = 0x5A827999
            elseif i <= 40 then
                F = bit.bxor(bit.bxor(B, C), D)
                K = 0x6ED9EBA1
            elseif i <= 60 then
                F = bit.bor(bit.bor(bit.band(B, C), bit.band(B, D)), bit.band(C, D))
                K = 0x8F1BBCDC
            else
                F = bit.bxor(bit.bxor(B, C), D)
                K = 0xCA62C1D6
            end

            local temp = bit.band(bit.rol(A, 5) + F + E + K + w[i], 0xFFFFFFFF)
            E = D
            D = C
            C = bit.rol(B, 30)
            B = A
            A = temp
        end

        h0 = bit.band(h0 + A, 0xFFFFFFFF)
        h1 = bit.band(h1 + B, 0xFFFFFFFF)
        h2 = bit.band(h2 + C, 0xFFFFFFFF)
        h3 = bit.band(h3 + D, 0xFFFFFFFF)
        h4 = bit.band(h4 + E, 0xFFFFFFFF)
    end

    -- 转换为大端序十六进制字符串
    local function to_hex_be(val)
        return string.format("%08x", val)
    end

    return to_hex_be(h0) .. to_hex_be(h1) .. to_hex_be(h2) .. to_hex_be(h3) .. to_hex_be(h4)
end

-- ============================================================
-- URL 编码
-- 将特殊字符转换为 %XX 形式
-- 参数：
--   str - 输入字符串
-- 返回：URL 编码后的字符串
-- ============================================================
function url_encode(str)
    local result = string.gsub(str, "([^%w%.%-_%~ ])", function(c)
        return string.format("%%%02X", string.byte(c))
    end)
    -- 空格替换为 +
    result = string.gsub(result, " ", "+")
    return result
end

-- ============================================================
-- URL 解码
-- 将 %XX 和 + 转换回原始字符
-- 参数：
--   str - URL 编码的字符串
-- 返回：解码后的字符串
-- ============================================================
function url_decode(str)
    -- + 替换为空格
    str = string.gsub(str, "+", " ")
    -- 解码 %XX
    str = string.gsub(str, "%%(%x%x)", function(hex)
        return string.char(tonumber(hex, 16))
    end)
    return str
end

-- ============================================================
-- HTML 编码
-- 将特殊 HTML 字符转换为实体
-- 参数：
--   str - 输入字符串
-- 返回：HTML 编码后的字符串
-- ============================================================
function html_encode(str)
    local entities = {
        ["&"] = "&amp;",
        ["<"] = "&lt;",
        [">"] = "&gt;",
        ['"'] = "&quot;",
        ["'"] = "&#39;",
        ["/"] = "&#47;",
    }
    return string.gsub(str, "[&<>\"'/]", function(c)
        return entities[c] or c
    end)
end

-- ============================================================
-- HTML 解码
-- 将 HTML 实体转换回原始字符
-- 参数：
--   str - HTML 编码的字符串
-- 返回：解码后的字符串
-- ============================================================
function html_decode(str)
    -- 解码命名实体
    local named_entities = {
        ["&amp;"] = "&",
        ["&lt;"] = "<",
        ["&gt;"] = ">",
        ["&quot;"] = '"',
        ["&apos;"] = "'",
        ["&#39;"] = "'",
        ["&#47;"] = "/",
        ["&nbsp;"] = " ",
    }

    for name, char in pairs(named_entities) do
        str = string.gsub(str, name, char)
    end

    -- 解码数字实体 &#NNN;
    str = string.gsub(str, "&#(%d+);", function(num)
        return string.char(tonumber(num))
    end)

    -- 解码十六进制实体 &#xHH;
    str = string.gsub(str, "&#x(%x+);", function(hex)
        return string.char(tonumber(hex, 16))
    end)

    return str
end

-- ============================================================
-- 字符串转十六进制
-- ============================================================
function str_to_hex(str)
    local hex = ""
    for i = 1, #str do
        hex = hex .. string.format("%02x", string.byte(str, i))
    end
    return hex
end

-- ============================================================
-- 十六进制转字符串
-- ============================================================
function hex_to_str(hex)
    -- 移除非十六进制字符
    hex = string.gsub(hex, "%s", "")
    if #hex % 2 ~= 0 then
        error("十六进制字符串长度必须为偶数")
    end

    local str = ""
    for i = 1, #hex, 2 do
        local byte = tonumber(string.sub(hex, i, i + 1), 16)
        if byte then
            str = str .. string.char(byte)
        else
            error("无效的十六进制字符: " .. string.sub(hex, i, i + 1))
        end
    end
    return str
end

-- ============================================================
-- 打印帮助信息
-- ============================================================
function print_help()
    print("================================================")
    print("  哈希与编码工具 - 安全研究用")
    print("================================================")
    print("")
    print("用法: lua hash_utils.lua <功能> <参数...>")
    print("")
    print("可用功能:")
    print("  md5 <字符串>              - 计算 MD5 哈希")
    print("  sha1 <字符串>             - 计算 SHA1 哈希")
    print("  url_encode <字符串>       - URL 编码")
    print("  url_decode <字符串>       - URL 解码")
    print("  html_encode <字符串>      - HTML 实体编码")
    print("  html_decode <字符串>      - HTML 实体解码")
    print("  str2hex <字符串>          - 字符串转十六进制")
    print("  hex2str <十六进制>        - 十六进制转字符串")
    print("  help                      - 显示帮助信息")
    print("")
    print("示例:")
    print("  lua hash_utils.lua md5 \"hello world\"")
    print("  lua hash_utils.lua url_encode \"a=1&b=2\"")
    print("  lua hash_utils.lua html_encode \"<script>alert(1)</script>\"")
    print("================================================")
end

-- ============================================================
-- 主程序入口
-- ============================================================
function main(...)
    local args = {...}

    if #args == 0 or args[1] == "help" or args[1] == "-h" or args[1] == "--help" then
        print_help()
        return
    end

    local command = args[1]
    local text = args[2]

    if not text and command ~= "help" then
        print("[错误] 请提供要处理的字符串")
        return
    end

    if command == "md5" then
        print("[MD5 哈希]")
        print("  输入: " .. text)
        print("  结果: " .. md5(text))

    elseif command == "sha1" then
        print("[SHA1 哈希]")
        print("  输入: " .. text)
        print("  结果: " .. sha1(text))

    elseif command == "url_encode" then
        print("[URL 编码]")
        print("  输入: " .. text)
        print("  结果: " .. url_encode(text))

    elseif command == "url_decode" then
        print("[URL 解码]")
        print("  输入: " .. text)
        print("  结果: " .. url_decode(text))

    elseif command == "html_encode" then
        print("[HTML 编码]")
        print("  输入: " .. text)
        print("  结果: " .. html_encode(text))

    elseif command == "html_decode" then
        print("[HTML 解码]")
        print("  输入: " .. text)
        print("  结果: " .. html_decode(text))

    elseif command == "str2hex" then
        print("[字符串转十六进制]")
        print("  输入: " .. text)
        print("  结果: " .. str_to_hex(text))

    elseif command == "hex2str" then
        print("[十六进制转字符串]")
        local ok, result = pcall(hex_to_str, text)
        if ok then
            print("  输入: " .. text)
            print("  结果: " .. result)
        else
            print("  错误: " .. result)
        end

    else
        print("[错误] 未知功能: " .. command)
        print("输入 'lua hash_utils.lua help' 查看帮助")
    end
end

-- 运行主程序
main(...)
