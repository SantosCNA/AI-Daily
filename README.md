# 七叔AI洞察助手 (AI Insight Assistant)

## 🎯 项目概述

AI洞察助手是一个自动化程序，运行在服务器上，每天自动抓取预设的AI领域信源，使用AI生成结构化的"AI洞察日报"草稿，并支持人工审核和自动发布到GitHub Pages。

## ✨ 核心功能

### 🤖 AI自动化流水线
- **多信源抓取**：RSS、Twitter、arXiv、Hugging Face、GitHub等
- **智能内容筛选**：LLM + 规则基础的双重筛选机制
- **AI洞察生成**：使用DeepSeek API生成专业分析
- **日报自动生成**：结构化的"七叔AI洞察日报"格式

### 📧 邮件通知系统
- 自动发送日报审核通知
- 支持Gmail应用专用密码
- 可配置的邮件模板

### 🌐 Web审核界面
- Flask Web应用
- 实时预览和编辑日报
- 一键发布功能
- 历史日报管理

### 🚀 GitHub Pages自动发布
- 自动触发GitHub Actions工作流
- Jekyll静态网站生成
- 实时在线访问
- 完整的部署自动化

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   数据获取层     │    │   AI处理层      │    │   日报生成层     │
│                 │    │                 │    │                 │
│ • RSS抓取器     │───▶│ • DeepSeek API  │───▶│ • 模板渲染器    │
│ • Twitter API   │    │ • 内容筛选器    │    │ • Markdown生成  │
│ • arXiv API     │    │ • 洞察生成器    │    │ • 邮件通知      │
│ • Web爬虫       │    │ • 协调器        │    │ • GitHub发布    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Web审核界面    │
                       │                 │
                       │ • Flask应用     │
                       │ • 实时预览      │
                       │ • 编辑发布      │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  GitHub Pages   │
                       │                 │
                       │ • 自动部署      │
                       │ • 静态网站      │
                       │ • 在线访问      │
                       └─────────────────┘
```

## 🚀 快速开始

### 1. 环境要求
- Python 3.10+
- 虚拟环境支持
- 网络连接（用于API调用）

### 2. 安装依赖
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量
```bash
# 复制环境变量模板
cp env.example .env

# 编辑.env文件，配置以下内容：
# - DEEPSEEK_API_KEY: DeepSeek API密钥
# - TWITTER_*: Twitter API配置
# - SMTP_*: 邮件服务器配置
# - GH_TOKEN: GitHub Personal Access Token
# - GITHUB_REPO: GitHub仓库路径
```

### 4. 初始化数据库
```bash
python init_db.py
```

### 5. 运行系统
```bash
# 运行完整流水线
python main.py

# 启动审核界面
python start_review_app.py
```

## 📁 项目结构

```
AI-Daily/
├── ai_processor/          # AI处理核心
├── fetcher/              # 数据获取模块
├── digest_generator/     # 日报生成器
├── notification/         # 通知系统
├── review_app/          # Web审核界面
├── configs/             # 配置文件
├── prompts/             # AI提示词
├── digest/              # 生成的日报
├── .github/             # GitHub Actions
├── _config.yml          # Jekyll配置
├── Gemfile              # Ruby依赖
└── README.md            # 项目说明
```

## 🔧 配置说明

### 环境变量配置
所有敏感信息都通过环境变量配置，不会提交到代码仓库：

- **API密钥**：DeepSeek、Twitter等第三方服务的API密钥
- **数据库配置**：数据库连接字符串
- **邮件配置**：SMTP服务器和认证信息
- **GitHub配置**：Personal Access Token和仓库信息

### 安全措施
- `.env` 文件已添加到 `.gitignore`
- 所有测试文件都排除在部署之外
- 数据库文件不会上传到GitHub
- 敏感配置使用环境变量

## 📊 部署状态

[![Deploy to GitHub Pages](https://github.com/SantosCNA/AI-Daily/workflows/Deploy%20AI%20Daily%20to%20GitHub%20Pages/badge.svg)](https://github.com/SantosCNA/AI-Daily/actions)

- **在线访问**：[https://santoscna.github.io/AI-Daily/](https://santoscna.github.io/AI-Daily/)
- **自动部署**：通过GitHub Actions实现
- **构建工具**：Jekyll静态网站生成器

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 创建 GitHub Issue
- 发送邮件到项目维护者

---

**注意**：本项目不包含任何敏感信息或API密钥，所有配置都通过环境变量管理。
