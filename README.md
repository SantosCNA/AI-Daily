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

### 5. 测试配置
```bash
python test_config.py
```

### 6. 运行完整流水线
```bash
python main.py
```

### 7. 启动审核界面
```bash
python start_review_app.py
```

## 🔧 配置说明

### 内容筛选配置
配置文件：`configs/filter_config.yaml`
- 筛选严格度：strict/moderate/loose
- 保留率配置：各信源类型的内容保留比例
- LLM提示词：可自定义的筛选提示词
- 备用规则：规则基础筛选配置

### GitHub Pages配置
配置文件：`.github/workflows/deploy.yml`
- 自动触发：推送代码或API调用
- Jekyll构建：静态网站生成
- 自动部署：GitHub Pages发布

## 📊 信源配置

### 技术核心
- **arXiv**：AI/ML学术论文
- **Hugging Face**：开源AI模型
- **GitHub Trending**：热门AI项目
- **Twitter List**：AI领域KOL动态

### 产品与发布
- **OpenAI Blog**：官方发布
- **DeepMind Blog**：研究进展
- **TechCrunch AI**：行业新闻
- **Product Hunt AI**：新产品

### 市场与生态
- **机器之心**：国内AI动态
- **AI前线**：技术实践
- **A16Z AI**：投资动向

## 🌐 访问地址

### 本地开发
- 审核界面：http://localhost:9000
- API端点：http://localhost:9000/api/*

### GitHub Pages（部署后）
- 主页：https://your-username.github.io/ai-daily/
- 日报索引：https://your-username.github.io/ai-daily/digest/
- 具体日报：https://your-username.github.io/ai-daily/digest/YYYY-MM-DD.html

## 📝 日报格式

### 七叔AI洞察日报结构
```
# 七叔AI洞察日报 - YYYY-MM-DD

## 🎯 核心动态（总览）
用2-3句话概括今日AI世界的主要动向

## 📈 趋势、启示与展望
资深分析师视角的趋势分析和未来展望

## 🔍 今日精选（分述）
### 🤖 技术突破
### 🚀 产品发布  
### 💼 行业动态

## 📋 其他动态
完整的信息列表
```

## 🔄 工作流程

1. **定时触发**：每日自动运行数据抓取
2. **内容筛选**：LLM智能筛选 + 规则备用
3. **AI处理**：DeepSeek API生成洞察
4. **日报生成**：结构化Markdown格式
5. **邮件通知**：发送审核通知
6. **人工审核**：Web界面预览编辑
7. **一键发布**：自动部署到GitHub Pages
8. **在线访问**：几分钟后即可访问

## 🛠️ 开发指南

### 项目结构
```
ai-insight-assistant/
├── .github/workflows/     # GitHub Actions工作流
├── configs/               # 配置文件
├── prompts/               # LLM提示词
├── fetcher/               # 数据获取层
├── ai_processor/          # AI处理层
├── digest_generator/      # 日报生成层
├── review_app/            # Web审核界面
├── notification/           # 通知系统
├── logs/                  # 日志文件
└── digest/                # 日报文件（Jekyll）
```

### 添加新信源
1. 在`fetcher/`目录下创建新的抓取器
2. 在`init_db.py`中添加信源配置
3. 在`orchestrator.py`中集成新抓取器
4. 更新相关测试和文档

### 自定义筛选规则
1. 编辑`configs/filter_config.yaml`
2. 修改`prompts/`目录下的提示词
3. 调整`fetcher/content_filter.py`中的规则

## 🧪 测试

### 运行所有测试
```bash
# 配置测试
python test_config.py

# 筛选功能测试
python test_filter_config.py

# GitHub Pages功能测试
python test_github_pages.py

# 完整流水线测试
python main.py
```

## 🚨 故障排除

### 常见问题
1. **API调用失败**：检查API密钥和网络连接
2. **数据库错误**：运行`python init_db.py`重新初始化
3. **邮件发送失败**：确认SMTP配置和Gmail应用密码
4. **GitHub部署失败**：检查Token权限和工作流配置

### 日志查看
- 应用日志：`logs/app.log`
- 控制台输出：运行时实时显示
- GitHub Actions：查看工作流执行日志

## 📞 支持与反馈

- **问题报告**：创建GitHub Issue
- **功能建议**：提交Feature Request
- **贡献代码**：Fork项目并提交Pull Request

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🙏 致谢

- DeepSeek团队提供的AI API服务
- 开源社区的各种工具和库
- 所有为AI领域做出贡献的研究者和开发者

---

**注意**：请妥善保管您的API密钥和访问令牌，不要将其提交到代码仓库中！
