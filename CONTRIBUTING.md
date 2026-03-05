# 知识库贡献规范

## 分支命名规范

```
feature/autosar-mcal-xxx     # AUTOSAR MCAL模块相关内容
feature/industry-report      # 产业研究报告
feature/consulting-xxxx      # 咨询分析内容
feature/tool-xxxx            # 工具脚本
```

## 提交信息规范

```
[content] 添加AUTOSAR ADC模块笔记
[consulting] 更新VinFast制动系统分析
[industry] 智驾新程股权变更追踪
[fix] 修复MCAL文档链接
```

## 目录结构规范

```
autosar/
  mcal/           # MCAL模块笔记
  bsw/            # 基础软件
  rte/            # 运行时环境
  docs/           # 总览文档

consulting/
  industry/       # 产业研究
  market/         # 市场分析
  company/        # 公司追踪

wechat-articles/  # 公众号原文存档
daily-notes/      # 每日笔记
tools/            # 工具脚本
```

## 文档模板

每个模块README.md包含：
- 模块定位
- 核心API
- 关键概念
- 常见陷阱
- 模块关系
- 来源标注

---

*维护者: zjb1001*
