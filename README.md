# Knowledge Note / 知识库

> 汽车电子、AUTOSAR、AI工具的学习笔记与技术总结

[![Deploy to GitHub Pages](https://github.com/zjb1001/knowledge-note/actions/workflows/deploy.yml/badge.svg)](https://github.com/zjb1001/knowledge-note/actions/workflows/deploy.yml)

---

## 内容导航

### 📚 AUTOSAR MCAL 笔记

系统学习 AUTOSAR MCAL 13个核心模块：PORT、DIO、ADC、PWM、ICU、OCU、SPI、CAN、LIN、FLS、GPT、WDG、ETH

→ [查看 AUTOSAR 笔记](./autosar/README.md)

### 🏢 行业咨询

产业研究、市场分析、公司追踪等内容

→ [查看咨询内容](./consulting/README.md)

### 🛠 工具与实践

- [Beautiful Mermaid](./tools/beautiful-mermaid/deployment-guide.md) — 高性能 Mermaid 图表渲染库部署实践
- [Gantt AI](./tools/gantt-ai/project-overview.md) — AI 增强甘特图项目管理工具
- [Beautiful Mermaid Showcase](./tools/beautiful-mermaid-showcase/README.md) — 图表展示案例

### 📰 微信文章

→ [ROS2 Launch 指南](./wechat-articles/ros2-launch-guide.md)

---

## 部署到 GitHub Pages

本仓库已配置 GitHub Actions，可自动将内容发布为 GitHub Pages 网站。

### 快速启用步骤

1. **Fork 或克隆本仓库**

   ```bash
   git clone https://github.com/zjb1001/knowledge-note.git
   cd knowledge-note
   ```

2. **在仓库 Settings 中启用 GitHub Pages**

   - 打开仓库页面，进入 **Settings → Pages**
   - 在 **Source** 下选择 **GitHub Actions**
   - 保存设置

3. **触发部署**

   推送任意提交到 `main` 分支，GitHub Actions 会自动构建并部署：

   ```bash
   git add .
   git commit -m "update notes"
   git push origin main
   ```

4. **访问网站**

   部署完成后，网站地址为：

   ```
   https://<your-username>.github.io/knowledge-note/
   ```

### 手动触发部署

在 GitHub 仓库页面：**Actions → Deploy to GitHub Pages → Run workflow**

### 工作流说明

部署由 [`.github/workflows/deploy.yml`](./.github/workflows/deploy.yml) 控制：

| 步骤 | 说明 |
|------|------|
| Checkout | 拉取最新代码 |
| Setup Pages | 配置 GitHub Pages 环境 |
| Jekyll Build | 将 Markdown 文件编译为静态网站 |
| Upload artifact | 上传构建产物 |
| Deploy | 发布到 GitHub Pages |

---

## 贡献规范

→ [查看贡献规范](./CONTRIBUTING.md)

---

*维护者: zjb1001*
