// ============================================================
// 02_control_flow.c —— 条件语句与循环结构
// 编译命令：gcc 02_control_flow.c -o 02_control_flow
// ============================================================

#include <stdio.h>

int main() {
    // ---------- 1. if 语句 ----------
    printf("========== if 语句 ==========\n");

    int score = 85;
    printf("分数: %d\n", score);

    if (score >= 90) {
        printf("等级：优秀\n");
    } else if (score >= 80) {
        printf("等级：良好\n");
    } else if (score >= 60) {
        printf("等级：及格\n");
    } else {
        printf("等级：不及格\n");
    }


    // ---------- 2. switch 语句 ----------
    printf("\n========== switch 语句 ==========\n");

    int day = 3;
    printf("星期 %d 是：", day);
    switch (day) {
        case 1:
            printf("星期一\n");
            break;
        case 2:
            printf("星期二\n");
            break;
        case 3:
            printf("星期三\n");
            break;
        case 4:
            printf("星期四\n");
            break;
        case 5:
            printf("星期五\n");
            break;
        case 6:
            printf("星期六\n");
            break;
        case 7:
            printf("星期日\n");
            break;
        default:
            printf("无效的星期数\n");
            break;
    }

    // switch 穿透现象（不加 break 会继续执行后续 case）
    printf("\nswitch 穿透示例：\n");
    int level = 2;
    switch (level) {
        case 3:
            printf("  高级功能已解锁\n");
            // 没有 break，继续向下执行
        case 2:
            printf("  中级功能已解锁\n");
            // 没有 break，继续向下执行
        case 1:
            printf("  基础功能已解锁\n");
            break;
        default:
            printf("  未解锁任何功能\n");
    }


    // ---------- 3. while 循环 ----------
    printf("\n========== while 循环 ==========\n");

    int i = 1;
    printf("1 到 5 的累加：");
    int sum = 0;
    while (i <= 5) {
        sum += i;
        printf("%d ", i);
        i++;
    }
    printf("\n累加和 = %d\n", sum);


    // ---------- 4. do-while 循环 ----------
    printf("\n========== do-while 循环 ==========\n");

    int j = 1;
    printf("do-while 输出 1-3：");
    do {
        printf("%d ", j);
        j++;
    } while (j <= 3);
    printf("\n");

    // do-while 至少执行一次循环体
    int k = 10;
    printf("k=10，条件 k<=3，do-while 仍执行一次：");
    do {
        printf("%d ", k);
        k++;
    } while (k <= 3);
    printf("\n");


    // ---------- 5. for 循环 ----------
    printf("\n========== for 循环 ==========\n");

    printf("for 循环输出 1-10 的偶数：");
    for (int m = 1; m <= 10; m++) {
        if (m % 2 == 0) {
            printf("%d ", m);
        }
    }
    printf("\n");

    // 嵌套 for 循环 - 打印乘法表
    printf("\n九九乘法表（部分）：\n");
    for (int row = 1; row <= 5; row++) {
        for (int col = 1; col <= row; col++) {
            printf("%d*%d=%-2d ", col, row, row * col);
        }
        printf("\n");
    }


    // ---------- 6. break 与 continue ----------
    printf("\n========== break 与 continue ==========\n");

    // break：跳出整个循环
    printf("break 示例（遇到 5 就停止）：");
    for (int n = 1; n <= 10; n++) {
        if (n == 5) {
            break;
        }
        printf("%d ", n);
    }
    printf("\n");

    // continue：跳过本次循环，继续下一次
    printf("continue 示例（跳过偶数）：");
    for (int n = 1; n <= 10; n++) {
        if (n % 2 == 0) {
            continue;
        }
        printf("%d ", n);
    }
    printf("\n");


    // ---------- 7. goto 语句 ----------
    printf("\n========== goto 语句 ==========\n");

    int num = 0;
loop_start:  // 标签
    printf("num = %d\n", num);
    num++;
    if (num < 3) {
        goto loop_start;  // 跳转到标签处
    }

    // goto 常用于错误处理，统一跳转到清理代码
    printf("\ngoto 错误处理示例：\n");
    int *ptr = NULL;
    int error_code = 0;

    ptr = (int *)malloc(sizeof(int) * 10);
    if (ptr == NULL) {
        error_code = 1;
        goto cleanup;
    }

    // 模拟一些操作...
    printf("  内存分配成功\n");
    free(ptr);
    printf("  内存已释放\n");
    printf("  操作完成\n");
    return 0;

cleanup:
    printf("  错误码：%d，清理资源中...\n", error_code);
    if (ptr != NULL) {
        free(ptr);
    }
    return error_code;
}
