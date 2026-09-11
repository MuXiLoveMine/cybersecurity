--[[
================================================================================
  编解码工具 - base64_xor.lua
================================================================================
  功能说明：
    本脚本提供多种编解码和简单加解密功能，用于安全研究和学习：
    1. Base64 编码与解码
    2. XOR 对称加解密（支持任意密钥）
    3. 简单哈希函数（CRC32、FNV-1a、简单求和哈希）
    4. URL 编码与解码
    5. 十六进制编码与解码

    所有功能均可作为库模块 require 使用，也可直接通过命令行调用。

  依赖说明：
    无外部依赖，纯 Lua 实现（基于 Lua 5.1 / LuaJIT）。

  使用方法：
    lua base64_xor.lua <功能> <参数...>

  示例：
    -- Base64 编码
    lua base64_xor.lua b64enc "Hello, World!"

    -- Base64 解码
    lua base64_xor.lua b64dec "SGVsbG8sIFdvcmxkIQ=="

    -- XOR 加密（需指定密钥）
    lua base64_xor.lua xor "secret data" "mykey"

    -- XOR 解密（XOR 是对称的，解密用同样的密钥）
    lua base64_xor.lua xor "7ca10d071c" "mykey" --hex

    -- URL 编码
    lua base64_xor.lua urlenc "hello world&foo=bar"

    -- URL 解码
    lua base64_xor.lua urldec "hello%20world%26foo%3Dbar"

    -- 十六进制编码
    lua base64_xor.lua hexenc "ABCD"

    -- 十六进制解码
    lua base64_xor.lua hexdec "41424344"

    -- FNV-1a 哈希
    lua base64_xor.lua fnv1a "hello"

    -- CRC32 哈希
    lua base64_xor.lua crc32 "hello"

    -- 显示帮助
    lua base64_xor.lua --help

  免责声明：
    本脚本仅供安全学习和研究使用，请勿用于非法用途。
    XOR 加密和简单哈希均为弱加密/哈希算法，仅用于学习原理，
    不可用于生产环境中的敏感数据保护或安全认证。
    使用本脚本造成的一切后果由使用者自行承担。
================================================================================
--]]

-- ============================================================
-- 模块定义
-- 可以通过 require("base64_xor") 作为库使用
-- ============================================================
local M = {}

-- ============================================================
-- Base64 编解码模块
-- ============================================================

-- Base64 字符表（标准 RFC 4648）
local b64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

-- Base64 解码反向映射表
local b64_decode_table = {}
for i = 1, #b64_chars do
    local c = b64_chars:sub(i, i)
    b64_decode_table[c] = i - 1
end
b64_decode_table["="] = 0  -- 填充字符

--- Base64 编码
-- 将二进制数据编码为 Base64 字符串
-- @param data 要编码的数据字符串
-- @return Base64 编码后的字符串
function M.base64_encode(data)
    if not data or #data == 0 then return "" end

    local result = {}
    local len = #data

    -- 每 3 字节为一组进行处理，编码为 4 个 Base64 字符
    local i = 1
    while i <= len do
        -- 读取 3 个字节（可能不足 3 个）
        local b1 = data:byte(i)
        local b2 = data:byte(i + 1) or 0
        local b3 = data:byte(i + 2) or 0

        -- 将 3 字节（24 位）拆分为 4 个 6 位组
        -- b1: AAAAAAAA  b2: BBBBBBBB  b3: CCCCCCCC
        -- 编码: AAAAAA  AABBBB  BBCCCC  CCCCCC
        local g1 = (b1 >> 2) & 0x3F
        local g2 = ((b1 & 0x03) << 4) | ((b2 >> 4) & 0x0F)
        local g3 = ((b2 & 0x0F) << 2) | ((b3 >> 6) & 0x03)
        local g4 = b3 & 0x3F

        -- 映射到 Base64 字符
        table.insert(result, b64_chars:sub(g1 + 1, g1 + 1))
        table.insert(result, b64_chars:sub(g2 + 1, g2 + 1))

        -- 处理剩余字节的填充
        if i + 1 <= len then
            table.insert(result, b64_chars:sub(g3 + 1, g3 + 1))
        else
            table.insert(result, "=")  -- 不足 3 字节，用 = 填充
        end

        if i + 2 <= len then
            table.insert(result, b64_chars:sub(g4 + 1, g4 + 1))
        else
            table.insert(result, "=")  -- 不足 3 字节，用 = 填充
        end

        i = i + 3
    end

    return table.concat(result)
end

--- Base64 解码
-- 将 Base64 字符串解码为原始二进制数据
-- @param b64_str Base64 编码字符串
-- @return 解码后的原始数据字符串
function M.base64_decode(b64_str)
    if not b64_str or #b64_str == 0 then return "" end

    -- 去除可能的换行和空白
    b64_str = b64_str:gsub("[%s\r\n]", "")

    local result = {}
    local len = #b64_str

    -- 每 4 个 Base64 字符为一组进行解码
    local i = 1
    while i <= len do
        -- 读取 4 个字符
        local c1 = b64_str:sub(i, i)
        local c2 = b64_str:sub(i + 1, i + 1)
        local c3 = b64_str:sub(i + 2, i + 2)
        local c4 = b64_str:sub(i + 3, i + 3)

        -- 解码为 6 位值
        local g1 = b64_decode_table[c1] or 0
        local g2 = b64_decode_table[c2] or 0
        local g3 = b64_decode_table[c3] or 0
        local g4 = b64_decode_table[c4] or 0

        -- 合并为 3 字节
        -- g1: AAAAAA  g2: BBBBBB  g3: CCCCCC  g4: DDDDDD
        -- 解码: AAAAAABB  BBBBCCCC  DDFFFFFF
        local b1 = (g1 << 2) | (g2 >> 4)
        local b2 = ((g2 & 0x0F) << 4) | (g3 >> 2)
        local b3 = ((g3 & 0x03) << 6) | g4

        -- 添加解码后的字节（跳过填充部分）
        table.insert(result, string.char(b1))
        if c3 ~= "=" then
            table.insert(result, string.char(b2))
        end
        if c4 ~= "=" then
            table.insert(result, string.char(b3))
        end

        i = i + 4
    end

    return table.concat(result)
end

-- ============================================================
-- XOR 加解密模块
-- XOR 是对称加密：加密和解密使用相同的操作
-- 密钥循环使用以匹配数据长度
-- ============================================================

--- XOR 加密/解密
-- 使用密钥对数据进行 XOR 运算
-- 由于 XOR 的对称性，加密和解密使用同一函数
--
-- @param data 要加解密的数据字符串
-- @param key  密钥字符串
-- @return 加解密后的数据字符串
function M.xor_cipher(data, key)
    if not data or #data == 0 then return "" end
    if not key or #key == 0 then return data end

    local result = {}
    local key_len = #key
    local data_len = #data

    -- 逐字节进行 XOR 运算
    -- 密钥循环使用：当数据比密钥长时，密钥从头开始重复
    for i = 1, data_len do
        local data_byte = data:byte(i)
        local key_byte = key:byte((i - 1) % key_len + 1)
        -- XOR 运算
        local encrypted_byte = data_byte ~ key_byte
        table.insert(result, string.char(encrypted_byte))
    end

    return table.concat(result)
end

-- ============================================================
-- URL 编解码模块
-- ============================================================

--- URL 编码（百分号编码）
-- 将特殊字符编码为 %XX 格式
-- @param str 要编码的字符串
-- @return URL 编码后的字符串
function M.url_encode(str)
    if not str then return "" end

    -- 将每个非安全字符编码为 %XX
    -- 安全字符：字母、数字、- _ . ~
    local result = {}
    for i = 1, #str do
        local c = str:sub(i, i)
        local byte = c:byte()

        -- 判断是否为不需要编码的安全字符
        -- A-Z, a-z, 0-9, -, _, ., ~
        if (byte >= 65 and byte <= 90) or    -- A-Z
           (byte >= 97 and byte <= 122) or   -- a-z
           (byte >= 48 and byte <= 57) or    -- 0-9
           c == "-" or c == "_" or c == "." or c == "~" then
            table.insert(result, c)
        else
            -- 编码为 %XX（大写十六进制）
            table.insert(result, string.format("%%%02X", byte))
        end
    end

    return table.concat(result)
end

--- URL 解码
-- 将 %XX 格式的编码还原为原始字符
-- @param str URL 编码字符串
-- @return 解码后的字符串
function M.url_decode(str)
    if not str then return "" end

    -- 将 %XX 替换为对应字符
    -- + 替换为空格
    str = str:gsub("+", " ")
    str = str:gsub("%%(%x%x)", function(hex)
        return string.char(tonumber(hex, 16))
    end)

    return str
end

-- ============================================================
-- 十六进制编解码模块
-- ============================================================

--- 十六进制编码
-- 将数据的每个字节编码为两位十六进制
-- @param data 原始数据字符串
-- @return 十六进制字符串
function M.hex_encode(data)
    if not data or #data == 0 then return "" end

    local result = {}
    for i = 1, #data do
        table.insert(result, string.format("%02x", data:byte(i)))
    end

    return table.concat(result)
end

--- 十六进制解码
-- 将十六进制字符串还原为原始数据
-- @param hex_str 十六进制字符串
-- @return 原始数据字符串
function M.hex_decode(hex_str)
    if not hex_str or #hex_str == 0 then return "" end

    -- 去除可能的空格和 0x 前缀
    hex_str = hex_str:gsub("%s+", ""):gsub("^0x", "")

    local result = {}
    -- 每两个十六进制字符转换为一个字节
    for i = 1, #hex_str, 2 do
        local hex_byte = hex_str:sub(i, i + 1)
        if #hex_byte == 2 then
            local byte = tonumber(hex_byte, 16)
            if byte then
                table.insert(result, string.char(byte))
            end
        end
    end

    return table.concat(result)
end

-- ============================================================
-- 简单哈希函数模块
-- 这些哈希函数仅用于学习，不适用于密码学安全场景
-- ============================================================

--- FNV-1a 哈希（32 位）
-- Fowler-Noll-Vo 哈希函数，简单快速的非加密哈希
-- 算法：hash = (hash ^ byte) * FNV_prime
--
-- @param data 要哈希的数据字符串
-- @return 32 位哈希值（整数）
function M.fnv1a_32(data)
    if not data or #data == 0 then return 0 end

    -- FNV-1a 32 位参数
    local hash = 0x811C9DC5  -- FNV offset basis (32-bit)
    local prime = 0x01000193  -- FNV prime (32-bit)

    for i = 1, #data do
        -- XOR 当前字节
        hash = hash ~ data:byte(i)
        -- 乘以素数（使用位运算模拟 32 位乘法，避免溢出）
        hash = (hash * prime) & 0xFFFFFFFF
    end

    return hash
end

--- CRC32 计算函数
-- 使用标准 CRC-32 算法（与 zlib/PNG 兼容）
-- 多项式: 0xEDB88320（反向多项式）
--
-- @param data 要计算的数据字符串
-- @return 32 位 CRC 值（整数）
function M.crc32(data)
    if not data or #data == 0 then return 0 end

    -- 构建 CRC32 查找表（256 个条目）
    -- 使用反向多项式 0xEDB88320
    if not M._crc32_table then
        M._crc32_table = {}
        for i = 0, 255 do
            local crc = i
            for _ = 1, 8 do
                if (crc & 1) == 1 then
                    crc = (crc >> 1) ~ 0xEDB88320
                else
                    crc = crc >> 1
                end
            end
            M._crc32_table[i] = crc
        end
    end

    -- 初始值为 0xFFFFFFFF
    local crc = 0xFFFFFFFF

    -- 逐字节处理
    for i = 1, #data do
        local byte = data:byte(i)
        -- 查表更新 CRC
        local idx = (crc ~ byte) & 0xFF
        crc = (crc >> 8) ~ M._crc32_table[idx]
    end

    -- 最终异或
    return crc ~ 0xFFFFFFFF
end

--- 简单求和哈希
-- 最简单的哈希：将所有字节值相加，取模
-- 仅用于演示哈希原理，碰撞率极高
--
-- @param data 要哈希的数据字符串
-- @return 哈希值（整数）
function M.simple_hash(data)
    if not data or #data == 0 then return 0 end

    local sum = 0
    for i = 1, #data do
        sum = sum + data:byte(i)
    end

    -- 乘以质数增加分散性
    return (sum * 31) & 0xFFFFFFFF
end

--- DJB2 哈希
-- Daniel J. Bernstein 的字符串哈希函数
-- 简单但分散性较好的非加密哈希
--
-- @param data 要哈希的数据字符串
-- @return 32 位哈希值（整数）
function M.djb2_hash(data)
    if not data or #data == 0 then return 0 end

    -- 初始值为 5381
    local hash = 5381

    for i = 1, #data do
        -- hash = hash * 33 + byte
        -- 使用位运算优化：hash * 33 = (hash << 5) + hash
        hash = ((hash << 5) + hash + data:byte(i)) & 0xFFFFFFFF
    end

    return hash
end

-- ============================================================
-- 便捷函数：XOR 加密并输出十六进制
-- 用于安全测试中快速加密数据
-- ============================================================
function M.xor_encrypt_hex(data, key)
    local encrypted = M.xor_cipher(data, key)
    return M.hex_encode(encrypted)
end

--- 从十六进制解码后用 XOR 解密
function M.xor_decrypt_hex(hex_data, key)
    local data = M.hex_decode(hex_data)
    return M.xor_cipher(data, key)
end

-- ============================================================
-- 函数：打印帮助信息
-- ============================================================
local function print_help()
    print([[
============================================
  编解码工具 - base64_xor.lua
============================================

用法:
  lua base64_xor.lua <功能> <参数...>

功能列表:
  b64enc <字符串>            Base64 编码
  b64dec <Base64字符串>      Base64 解码
  xor <数据> <密钥> [hex]    XOR 加解密（hex 表示输入/输出为十六进制）
  urlenc <字符串>            URL 编码
  urldec <URL字符串>         URL 解码
  hexenc <字符串>            十六进制编码
  hexdec <十六进制字符串>    十六进制解码
  fnv1a <字符串>             FNV-1a 哈希（32位）
  crc32 <字符串>             CRC32 哈希
  djb2 <字符串>              DJB2 哈希
  simplehash <字符串>        简单求和哈希

示例:
  lua base64_xor.lua b64enc "Hello"
  lua base64_xor.lua b64dec "SGVsbG8="
  lua base64_xor.lua xor "secret" "key"
  lua base64_xor.lua xor "7ca10d071c" "key" hex
  lua base64_xor.lua urlenc "a b&c=d"
  lua base64_xor.lua hexenc "AB"
  lua base64_xor.lua fnv1a "hello"
  lua base64_xor.lua crc32 "hello"
]])
end

-- ============================================================
-- 主函数：命令行入口
-- ============================================================
local function main()
    local args = arg
    if #args == 0 or args[1] == "--help" or args[1] == "-h" then
        print_help()
        return
    end

    local func = args[1]

    -- 根据功能名分发
    if func == "b64enc" then
        -- Base64 编码
        local input = args[2] or ""
        print(M.base64_encode(input))

    elseif func == "b64dec" then
        -- Base64 解码
        local input = args[2] or ""
        print(M.base64_decode(input))

    elseif func == "xor" then
        -- XOR 加解密
        local data = args[2] or ""
        local key = args[3] or ""
        local use_hex = args[4] == "hex"

        if use_hex then
            -- 十六进制模式：输入为 hex，解密后输出原文
            local result = M.xor_decrypt_hex(data, key)
            print(result)
        else
            -- 普通模式：加密并输出十六进制
            local result = M.xor_encrypt_hex(data, key)
            print(result)
        end

    elseif func == "urlenc" then
        -- URL 编码
        local input = args[2] or ""
        print(M.url_encode(input))

    elseif func == "urldec" then
        -- URL 解码
        local input = args[2] or ""
        print(M.url_decode(input))

    elseif func == "hexenc" then
        -- 十六进制编码
        local input = args[2] or ""
        print(M.hex_encode(input))

    elseif func == "hexdec" then
        -- 十六进制解码
        local input = args[2] or ""
        print(M.hex_decode(input))

    elseif func == "fnv1a" then
        -- FNV-1a 哈希
        local input = args[2] or ""
        print(string.format("0x%08X (%d)", M.fnv1a_32(input), M.fnv1a_32(input)))

    elseif func == "crc32" then
        -- CRC32 哈希
        local input = args[2] or ""
        print(string.format("0x%08X (%d)", M.crc32(input), M.crc32(input)))

    elseif func == "djb2" then
        -- DJB2 哈希
        local input = args[2] or ""
        print(string.format("0x%08X (%d)", M.djb2_hash(input), M.djb2_hash(input)))

    elseif func == "simplehash" then
        -- 简单求和哈希
        local input = args[2] or ""
        print(string.format("0x%08X (%d)", M.simple_hash(input), M.simple_hash(input)))

    else
        print("未知功能: " .. func)
        print_help()
    end
end

-- ============================================================
-- 执行主函数
-- ============================================================
main()

-- ============================================================
-- 模块返回（支持 require 使用）
-- 如果通过 require 加载，返回模块表 M
-- ============================================================
return M
