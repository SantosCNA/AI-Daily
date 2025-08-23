# GitHub Pages 部署设置指南

## 🎯 概述

本指南将帮助您设置自动化的GitHub Pages部署，实现AI日报的自动发布。

## 📋 前置要求

1. **GitHub账户**：需要一个GitHub账户
2. **GitHub仓库**：创建一个新的仓库用于存放AI日报
3. **Personal Access Token**：需要生成GitHub个人访问令牌

## 🚀 设置步骤

### 1. 创建GitHub仓库

1. 访问 [GitHub](https://github.com)
2. 点击 "New repository"
3. 仓库名称建议：`ai-daily` 或 `ai-insight-daily`
4. 选择 "Public"（GitHub Pages免费版需要公开仓库）
5. 勾选 "Add a README file"
6. 点击 "Create repository"

### 2. 生成Personal Access Token

1. 在GitHub中，点击右上角头像 → "Settings"
2. 左侧菜单选择 "Developer settings" → "Personal access tokens" → "Tokens (classic)"
3. 点击 "Generate new token (classic)"
4. 设置令牌名称：`AI Daily Deploy`
5. 选择权限范围：
   - `repo` (完整的仓库访问权限)
   - `workflow` (允许触发工作流)
6. 点击 "Generate token"
7. **重要**：复制生成的令牌，它只会显示一次！

### 3. 配置环境变量

1. 在您的项目根目录创建 `.env` 文件（如果还没有的话）
2. 添加以下配置：

```bash
# GitHub Pages部署配置
GH_TOKEN=your_github_personal_access_token_here
GITHUB_REPO=your-username/ai-daily
```

**注意**：
- 将 `your_github_personal_access_token_here` 替换为实际的令牌
- 将 `your-username/ai-daily` 替换为您的实际仓库路径

### 4. 推送代码到GitHub

```bash
# 初始化Git仓库（如果还没有）
git init

# 添加远程仓库
git remote add origin https://github.com/your-username/ai-daily.git

# 添加所有文件
git add .

# 提交更改
git commit -m "Initial commit: AI Daily MVP with GitHub Pages"

# 推送到GitHub
git push -u origin main
```

### 5. 启用GitHub Pages

1. 在GitHub仓库页面，点击 "Settings"
2. 左侧菜单选择 "Pages"
3. 在 "Source" 部分，选择 "GitHub Actions"
4. 点击 "Configure" 按钮

### 6. 设置仓库Secrets

1. 在GitHub仓库页面，点击 "Settings"
2. 左侧菜单选择 "Secrets and variables" → "Actions"
3. 点击 "New repository secret"
4. 名称：`GH_TOKEN`
5. 值：粘贴您的Personal Access Token
6. 点击 "Add secret"

## 🔧 测试部署

### 手动测试

1. 在GitHub仓库页面，点击 "Actions" 标签
2. 选择 "Deploy AI Daily to GitHub Pages" 工作流
3. 点击 "Run workflow" → "Run workflow"
4. 观察工作流执行情况

### 通过应用测试

1. 启动您的AI洞察助手应用
2. 生成一份日报
3. 在审核界面点击 "发布"
4. 检查GitHub Actions是否自动触发

## 📱 访问您的AI日报

部署成功后，您可以通过以下URL访问：

- **主页**：`https://your-username.github.io/ai-daily/`
- **日报索引**：`https://your-username.github.io/ai-daily/digest/`
- **具体日报**：`https://your-username.github.io/ai-daily/digest/2025-08-23.html`

## 🚨 故障排除

### 常见问题

1. **工作流未触发**
   - 检查 `GH_TOKEN` 是否正确设置
   - 确认仓库权限设置
   - 检查工作流文件语法

2. **部署失败**
   - 查看GitHub Actions日志
   - 确认Jekyll配置正确
   - 检查Markdown文件格式

3. **页面无法访问**
   - 确认GitHub Pages已启用
   - 检查仓库是否为公开
   - 等待几分钟让部署完成

### 调试技巧

1. **查看工作流日志**：在Actions标签页查看详细执行日志
2. **检查环境变量**：确认所有必要的环境变量都已设置
3. **验证API调用**：检查GitHub API调用是否成功

## 🔄 自动化流程

设置完成后，您的AI日报发布流程将变为：

1. **AI生成日报** → 自动发送审核邮件
2. **人工审核** → 在审核界面点击发布
3. **自动部署** → 触发GitHub Actions工作流
4. **即时访问** → 几分钟后即可通过GitHub Pages访问

## 📞 获取帮助

如果遇到问题：

1. 检查GitHub Actions日志
2. 查看本项目的Issues
3. 参考GitHub Pages官方文档
4. 联系项目维护者

---

**注意**：请妥善保管您的Personal Access Token，不要将其提交到代码仓库中！
