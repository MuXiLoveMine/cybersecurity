/*
 * ============================================================
 * 文件名：simple_shell.c
 * 功能描述：简单的 Shell 程序（支持命令执行、管道、重定向）
 * 作者：网络安全学习笔记
 * 日期：2026-09-21
 * ============================================================
 *
 * 【使用说明】
 * 1. 编译方式（Linux）：
 *    gcc simple_shell.c -o simple_shell
 * 2. 编译方式（Windows + MinGW）：
 *    gcc simple_shell.c -o simple_shell.exe
 * 3. 运行后进入交互式 Shell，输入命令执行
 *
 * 【支持功能】
 *   - 基本命令执行（ls, dir, cd, pwd, echo 等）
 *   - 内置命令：cd, exit, help, pwd, clear
 *   - 命令历史（简单实现）
 *   - 输入输出重定向（>、<）
 *   - 管道（|）
 *
 * 【原理说明】
 *   使用 fork/exec（Linux）或 _spawn（Windows）创建子进程执行命令，
 *   模拟一个简单的命令行 Shell 环境。
 *
 * 【免责声明】
 *   本工具仅供网络安全学习使用。
 *   理解 Shell 原理有助于理解 Webshell、命令注入等安全问题。
 * ============================================================
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#ifdef _WIN32
    #include <windows.h>
    #include <process.h>
    #include <direct.h>
    #define getcwd _getcwd
    #define chdir  _chdir
    #define MAX_ARGS 64
    #define MAX_LINE 1024
    #define PATH_MAX 260
#else
    #include <unistd.h>
    #include <sys/wait.h>
    #include <fcntl.h>
    #include <limits.h>
    #define MAX_ARGS 64
    #define MAX_LINE 1024
    #define PATH_MAX 4096
#endif

// 内置命令列表
char *builtin_cmds[] = {
    "cd",
    "exit",
    "help",
    "pwd",
    "clear",
    "history",
    NULL
};

// 命令历史
#define MAX_HISTORY 100
char history[MAX_HISTORY][MAX_LINE];
int history_count = 0;

// 添加到历史记录
void add_history(const char *line) {
    if (history_count < MAX_HISTORY) {
        strncpy(history[history_count], line, MAX_LINE - 1);
        history[history_count][MAX_LINE - 1] = '\0';
        history_count++;
    }
}

// 显示历史记录
void show_history() {
    printf("命令历史（最近 %d 条）：\n", history_count);
    for (int i = 0; i < history_count; i++) {
        printf("  %d  %s\n", i + 1, history[i]);
    }
}

// 显示帮助
void print_help() {
    printf("Simple Shell - 简单 Shell 程序\n");
    printf("\n内置命令：\n");
    printf("  cd <目录>    切换当前工作目录\n");
    printf("  pwd          显示当前工作目录\n");
    printf("  exit / quit  退出 Shell\n");
    printf("  help         显示帮助信息\n");
    printf("  clear        清屏\n");
    printf("  history      显示命令历史\n");
    printf("\n使用示例：\n");
    printf("  ls -la              列出文件\n");
    printf("  cd /tmp             切换目录\n");
    printf("  cat file.txt        查看文件\n");
    printf("  echo hello > a.txt  输出重定向\n");
    printf("  cat < a.txt         输入重定向\n");
    printf("  ls | grep txt       管道\n");
}

// 解析命令行，拆分参数
int parse_args(char *line, char **args) {
    int argc = 0;
    char *token = strtok(line, " \t\n");
    while (token != NULL && argc < MAX_ARGS - 1) {
        args[argc++] = token;
        token = strtok(NULL, " \t\n");
    }
    args[argc] = NULL;
    return argc;
}

// 检查是否为重定向
int check_redirect(char **args, char **infile, char **outfile) {
    *infile = NULL;
    *outfile = NULL;
    int new_argc = 0;

    for (int i = 0; args[i] != NULL; i++) {
        if (strcmp(args[i], ">") == 0 && args[i+1] != NULL) {
            *outfile = args[i+1];
            i++;  // 跳过文件名
        } else if (strcmp(args[i], "<") == 0 && args[i+1] != NULL) {
            *infile = args[i+1];
            i++;
        } else {
            args[new_argc++] = args[i];
        }
    }
    args[new_argc] = NULL;
    return new_argc;
}

// 检查管道
int check_pipe(char *line, char **cmd1, char **cmd2) {
    char *pipe_pos = strchr(line, '|');
    if (pipe_pos == NULL) return 0;

    *pipe_pos = '\0';
    *cmd1 = line;
    *cmd2 = pipe_pos + 1;

    // 去掉两端空格
    while (*cmd2 == ' ' || *cmd2 == '\t') (*cmd2)++;

    return 1;
}

#ifndef _WIN32
// 执行单个命令（Linux 版本）
int execute_command(char *line) {
    char *args[MAX_ARGS];
    char *infile, *outfile;

    // 解析参数
    char line_copy[MAX_LINE];
    strncpy(line_copy, line, MAX_LINE - 1);
    line_copy[MAX_LINE - 1] = '\0';

    parse_args(line_copy, args);

    if (args[0] == NULL) return 0;

    // 检查重定向
    check_redirect(args, &infile, &outfile);

    // 内置命令
    if (strcmp(args[0], "exit") == 0 || strcmp(args[0], "quit") == 0) {
        return -1;  // 返回 -1 表示退出
    }
    if (strcmp(args[0], "cd") == 0) {
        if (args[1] == NULL) {
            fprintf(stderr, "cd: 缺少参数\n");
        } else {
            if (chdir(args[1]) != 0) {
                perror("cd");
            }
        }
        return 0;
    }
    if (strcmp(args[0], "pwd") == 0) {
        char cwd[PATH_MAX];
        if (getcwd(cwd, sizeof(cwd)) != NULL) {
            printf("%s\n", cwd);
        } else {
            perror("pwd");
        }
        return 0;
    }
    if (strcmp(args[0], "help") == 0) {
        print_help();
        return 0;
    }
    if (strcmp(args[0], "clear") == 0) {
        printf("\033[H\033[J");
        return 0;
    }
    if (strcmp(args[0], "history") == 0) {
        show_history();
        return 0;
    }

    // 外部命令
    pid_t pid = fork();
    if (pid == 0) {
        // 子进程
        // 输入重定向
        if (infile != NULL) {
            int fd = open(infile, O_RDONLY);
            if (fd < 0) {
                perror("open");
                exit(1);
            }
            dup2(fd, 0);
            close(fd);
        }
        // 输出重定向
        if (outfile != NULL) {
            int fd = open(outfile, O_WRONLY | O_CREAT | O_TRUNC, 0644);
            if (fd < 0) {
                perror("open");
                exit(1);
            }
            dup2(fd, 1);
            close(fd);
        }

        execvp(args[0], args);
        perror("execvp");
        exit(1);
    } else if (pid > 0) {
        // 父进程等待子进程
        int status;
        waitpid(pid, &status, 0);
        return WEXITSTATUS(status);
    } else {
        perror("fork");
        return 1;
    }
}

// 执行带管道的命令
int execute_pipe(char *cmd1_str, char *cmd2_str) {
    int pipefd[2];
    if (pipe(pipefd) < 0) {
        perror("pipe");
        return 1;
    }

    pid_t pid1 = fork();
    if (pid1 == 0) {
        // 第一个命令：输出到管道写端
        close(pipefd[0]);
        dup2(pipefd[1], 1);
        close(pipefd[1]);

        char *args[MAX_ARGS];
        char cmd_copy[MAX_LINE];
        strncpy(cmd_copy, cmd1_str, MAX_LINE - 1);
        cmd_copy[MAX_LINE - 1] = '\0';
        parse_args(cmd_copy, args);

        execvp(args[0], args);
        perror("execvp");
        exit(1);
    }

    pid_t pid2 = fork();
    if (pid2 == 0) {
        // 第二个命令：从管道读端输入
        close(pipefd[1]);
        dup2(pipefd[0], 0);
        close(pipefd[0]);

        char *args[MAX_ARGS];
        char cmd_copy[MAX_LINE];
        strncpy(cmd_copy, cmd2_str, MAX_LINE - 1);
        cmd_copy[MAX_LINE - 1] = '\0';
        parse_args(cmd_copy, args);

        execvp(args[0], args);
        perror("execvp");
        exit(1);
    }

    close(pipefd[0]);
    close(pipefd[1]);

    int status;
    waitpid(pid1, &status, 0);
    waitpid(pid2, &status, 0);

    return WEXITSTATUS(status);
}
#endif

#ifdef _WIN32
// Windows 版本的命令执行
int execute_command(char *line) {
    char *args[MAX_ARGS];
    char *infile, *outfile;

    char line_copy[MAX_LINE];
    strncpy(line_copy, line, MAX_LINE - 1);
    line_copy[MAX_LINE - 1] = '\0';

    parse_args(line_copy, args);

    if (args[0] == NULL) return 0;

    check_redirect(args, &infile, &outfile);

    // 内置命令
    if (strcmp(args[0], "exit") == 0 || strcmp(args[0], "quit") == 0) {
        return -1;
    }
    if (strcmp(args[0], "cd") == 0) {
        if (args[1] == NULL) {
            fprintf(stderr, "cd: 缺少参数\n");
        } else {
            if (chdir(args[1]) != 0) {
                perror("cd");
            }
        }
        return 0;
    }
    if (strcmp(args[0], "pwd") == 0) {
        char cwd[PATH_MAX];
        if (getcwd(cwd, sizeof(cwd)) != NULL) {
            printf("%s\n", cwd);
        } else {
            perror("pwd");
        }
        return 0;
    }
    if (strcmp(args[0], "help") == 0) {
        print_help();
        return 0;
    }
    if (strcmp(args[0], "clear") == 0 || strcmp(args[0], "cls") == 0) {
        system("cls");
        return 0;
    }
    if (strcmp(args[0], "history") == 0) {
        show_history();
        return 0;
    }

    // 外部命令：使用 system 函数
    char cmd_line[MAX_LINE + 10];
    snprintf(cmd_line, sizeof(cmd_line), "%s", line);
    return system(cmd_line);
}
#endif

// 打印提示符
void print_prompt() {
    char cwd[PATH_MAX];
    if (getcwd(cwd, sizeof(cwd)) != NULL) {
        // 只显示最后一级目录
        char *last = strrchr(cwd, '/');
#ifdef _WIN32
        char *last_win = strrchr(cwd, '\\');
        if (last_win > last) last = last_win;
#endif
        if (last != NULL) {
            printf("[%s] $ ", last + 1);
        } else {
            printf("[%s] $ ", cwd);
        }
    } else {
        printf("$ ");
    }
    fflush(stdout);
}

int main() {
    char line[MAX_LINE];

    printf("========================================\n");
    printf("    Simple Shell - 简单 Shell 程序\n");
    printf("========================================\n");
    printf("输入 help 查看帮助，输入 exit 退出\n\n");

    while (1) {
        print_prompt();

        // 读取输入
        if (fgets(line, sizeof(line), stdin) == NULL) {
            printf("\n");
            break;
        }

        // 去掉换行符
        int len = (int)strlen(line);
        while (len > 0 && (line[len-1] == '\n' || line[len-1] == '\r')) {
            line[len-1] = '\0';
            len--;
        }

        // 跳过空行
        if (len == 0) continue;

        // 添加到历史
        add_history(line);

        // 检查是否有管道
        char line_copy[MAX_LINE];
        strncpy(line_copy, line, MAX_LINE - 1);
        line_copy[MAX_LINE - 1] = '\0';

#ifndef _WIN32
        char *cmd1, *cmd2;
        if (check_pipe(line_copy, &cmd1, &cmd2)) {
            execute_pipe(cmd1, cmd2);
        } else
#endif
        {
            int result = execute_command(line_copy);
            if (result == -1) {
                break;  // 退出
            }
        }
    }

    printf("\n再见！\n");
    return 0;
}
