# 搞嵌入式，谁不想拥有一组拿来就用的实用代码？

> **来源**: 嵌入式大杂烩 / 电子工程专辑  
> **日期**: 2026-03-05  
> **原链接**: https://www.eet-china.com/mp/a478293.html

## 概述

本文分享几个嵌入式Linux开发中高频用到的代码片段，基于 Linux + GCC 环境验证：
- 终端进度条
- 结构体内存布局分析
- 文件读写封装
- core dump 调试

---

## 1. 终端进度条

做 OTA 升级、固件烧写、批量文件拷贝的时候，光看日志刷屏心里没底，加个进度条一目了然。

**核心原理**：`\r` 回车符不换行，配合 `fflush` 刷新输出缓冲区实现同行刷新。

```c
#include <stdio.h>
#include <string.h>
#include <unistd.h>

typedef struct _progress
{
    int cur_size;
    int sum_size;
} progress_t;

void progress_bar(progress_t *progress_data)
{
    int percentage = 0;
    int cnt = 0;
    char proc[102];  // 100个字符位 + '#' + '\0'

    memset(proc, '\0', sizeof(proc));
    percentage = (int)((long long)progress_data->cur_size * 100 / progress_data->sum_size);

    if (percentage <= 100)
    {
        while (cnt <= percentage)
        {
            printf("[%-100s] [%d%%]\r", proc, cnt);
            fflush(stdout);
            proc[cnt] = '#';
            usleep(100000);
            cnt++;
        }
    }
    printf("\n");
}
```

---

## 2. 快速获取结构体成员大小及偏移量

搞嵌入式的应该都知道，结构体的内存布局、对齐方式这些细节经常要关注——通信协议解析、共享内存操作的时候一不注意就踩坑。

**自定义实现**（不依赖标准库）：

```c
#include <stdio.h>

#define GET_MEMBER_SIZE(type, member)   sizeof(((type*)0)->member)
#define GET_MEMBER_OFFSET(type, member) ((size_t)(&(((type*)0)->member)))

typedef struct _test_struct1
{
    char a;
    char c;
    short b;   // 注意：偏移是2，不是1+1=2，内存对齐在起作用
    int d;     // 偏移是4，int需4字节对齐
} test_struct1;

int main(int arc, char *argv[])
{
    printf("GET_MEMBER_SIZE(test_struct1, b) = %zu\n", GET_MEMBER_SIZE(test_struct1, b));
    printf("GET_MEMBER_OFFSET(b): %zu\n", GET_MEMBER_OFFSET(test_struct1, b));
    printf("GET_MEMBER_OFFSET(d): %zu\n", GET_MEMBER_OFFSET(test_struct1, d));
    return 0;
}
```

**关键原理**：
- 把 0 地址强转成结构体指针，再去取成员的地址
- 这个地址的值就是偏移量（因为基地址是0）
- 编译器为了让 int 对齐到4字节边界，会在成员间自动填充

---

## 3. 文件操作封装

配置参数存储、日志落盘、固件数据读写，几乎每项目都要写。

```c
#include <stdio.h>

static int file_opt_write(const char *filename, void *ptr, int size)
{
    FILE *fp;
    size_t num;

    fp = fopen(filename, "wb");  // 二进制写
    if (NULL == fp)
    {
        printf("open %s file error!\n", filename);
        return -1;
    }

    num = fwrite(ptr, 1, size, fp);
    if (num != size)
    {
        fclose(fp);
        printf("write %s file error!\n", filename);
        return -1;
    }
    fclose(fp);
    return (int)num;
}

static int file_opt_read(const char *filename, void *ptr, int size)
{
    FILE *fp;
    size_t num;

    fp = fopen(filename, "rb");  // 二进制读
    if (NULL == fp)
    {
        printf("open %s file error!\n", filename);
        return -1;
    }

    num = fread(ptr, 1, size, fp);
    if (num != size)
    {
        fclose(fp);
        printf("read %s file error!\n", filename);
        return -1;
    }
    fclose(fp);
    return (int)num;
}
```

**注意**：写结构体数据用二进制模式 `"wb"` / `"rb"`，Windows 上文本模式会对换行符做转换，可能多出 `\r`。

---

## 4. 后台运行生成 core 文件

程序跑着跑着突然挂了，段错误、非法访问这类问题最头疼。如果程序崩溃时能自动吐出 core 文件，事后用 gdb 加载分析，就能精准定位问题。

```c
#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <sys/resource.h>

#define SHELL_CMD_CONF_CORE_FILE    "echo /var/core-%e-%p-%t > /proc/sys/kernel/core_pattern"
#define SHELL_CMD_DEL_CORE_FILE     "rm -f /var/core*"

static int enable_core_dump(void)
{
    int resource = RLIMIT_CORE;
    struct rlimit rlim;

    rlim.rlim_cur = RLIM_INFINITY;
    rlim.rlim_max = RLIM_INFINITY;

    system(SHELL_CMD_DEL_CORE_FILE);

    if (0 != setrlimit(resource, &rlim))
    {
        printf("setrlimit error!\n");
        return -1;
    }

    system(SHELL_CMD_CONF_CORE_FILE);
    printf("core dump enabled, pattern: /var/core-%%e-%%p-%%t\n");
    return 0;
}

int main(int argc, char **argv)
{
    enable_core_dump();
    printf("==================segmentation fault test==================\n");
    
    // 故意触发段错误，仅为演示 core dump 功能
    int *p = NULL;
    *p = 1234;

    return 0;
}
```

**使用方法**：
```bash
gdb ./your_program /var/core-xxx
(gdb) bt  # 查看调用栈，锁定崩溃位置
```

---

## 代码片段汇总

| 代码片段 | 适用场景 |
|---------|---------|
| 终端进度条 | OTA升级、固件烧写、批量操作 |
| 结构体成员大小/偏移 | 协议解析、内存布局分析 |
| 文件读写封装 | 配置存储、日志落盘、数据持久化 |
| core dump使能 | 崩溃后定位、事后调试 |

---

*抓取时间: 2026-03-20*  
*分类: 知识技能 > 嵌入式开发 > 实用代码*
