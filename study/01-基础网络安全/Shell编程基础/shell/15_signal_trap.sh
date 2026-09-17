#!/bin/bash
# 15_signal_trap.sh
# 信号与 trap 示例

echo "=========================================="
echo "1. 基本信号捕获"
echo "=========================================="

# 定义清理函数
cleanup() {
    echo ""
    echo "【trap 触发】正在清理临时文件..."
    rm -f /tmp/signal_demo_$$.tmp
    echo "清理完成，脚本退出"
    exit 0
}

# 注册信号处理
trap cleanup SIGINT SIGTERM SIGQUIT

# 创建临时文件
echo "临时数据" > /tmp/signal_demo_$$.tmp
echo "临时文件已创建：/tmp/signal_demo_$$.tmp"
echo "当前脚本 PID：$$"
echo ""
echo "请按 Ctrl+C 测试 SIGINT 信号捕获..."
echo "（也可以用 kill -INT $$ 发送信号）"
echo ""

# 循环等待
for i in {10..1}; do
    echo -ne "倒计时：$i 秒 \r"
    sleep 1
done
echo ""
echo "倒计时结束，脚本正常退出"

# 正常清理
cleanup_normal() {
    rm -f /tmp/signal_demo_$$.tmp
    echo "（正常退出时也会清理）"
}
trap cleanup_normal EXIT

echo ""
echo "=========================================="
echo "2. 忽略信号"
echo "=========================================="

echo "现在尝试忽略 SIGINT（Ctrl+C）..."
trap '' SIGINT   # 空字符串表示忽略

echo "按 Ctrl+C 不会中断，5 秒后恢复..."
for i in {5..1}; do
    echo -ne "  剩余 $i 秒（Ctrl+C 被忽略）\r"
    sleep 1
done
echo ""

# 恢复默认行为
trap - SIGINT
echo "SIGINT 已恢复正常处理"

echo ""
echo "=========================================="
echo "3. 捕获多个信号"
echo "=========================================="

handle_signal() {
    local sig=$1
    echo ""
    echo "收到信号：$sig"
}

trap 'handle_signal "SIGUSR1"' SIGUSR1
trap 'handle_signal "SIGUSR2"' SIGUSR2

echo "当前 PID：$$"
echo "请尝试：kill -USR1 $$"
echo "请尝试：kill -USR2 $$"
echo "等待 10 秒..."
sleep 10 &
wait $!
echo "等待结束"

echo ""
echo "=========================================="
echo "4. EXIT 陷阱（脚本退出时执行）"
echo "=========================================="

on_exit() {
    echo ""
    echo "【EXIT 陷阱】脚本即将退出，退出码：$?"
    echo "感谢使用本脚本！"
}
trap on_exit EXIT

echo "脚本即将结束..."
