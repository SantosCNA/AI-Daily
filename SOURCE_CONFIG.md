# 🔗 AI洞察助手 - 信源配置说明

## 📋 信源概览

AI洞察助手现在支持以下类型的信源，为您提供全面的AI领域信息覆盖：

### 🎯 技术核心 (Technical Core)
- **arXiv**: AI/ML学术论文预印本
- **Hugging Face**: 热门开源AI模型
- **GitHub Trending**: AI/ML相关热门项目
- **Twitter List**: AI领域KOL动态

### 🚀 产品与发布 (Product & Launch)
- **OpenAI Blog**: GPT系列等重大发布
- **Anthropic Blog**: Claude系列更新
- **DeepMind Blog**: Alpha系列研究进展
- **Mistral AI**: 开源模型发布
- **Replicate**: 模型应用平台动态
- **Product Hunt**: AI产品发布

### 💼 市场与生态 (Market & Ecosystem)
- **TechCrunch AI**: 融资、收购等市场新闻
- **机器之心**: 国内AI动态
- **AI前线**: 技术实践分享
- **A16Z**: 投资机构AI观点

## ⚙️ 配置步骤

### 1. 环境变量配置

复制并编辑环境变量文件：
```bash
cp env.example .env
```

编辑 `.env` 文件，配置必要的API密钥：
```ini
# DeepSeek API配置（必需）
DEEPSEEK_API_KEY=sk-7ff8f534b0304f268100e43934f53515

# Twitter API配置（可选，用于Twitter List）
TWITTER_BEARER_TOKEN=your-twitter-bearer-token-here
TWITTER_API_KEY=your-twitter-api-key
TWITTER_API_SECRET=your-twitter-api-secret
TWITTER_ACCESS_TOKEN=your-twitter-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-twitter-access-token-secret

# 其他配置
DATABASE_URL=sqlite:///./app.db
FLASK_SECRET_KEY=your-secret-key-here
```

### 2. Twitter List配置（重要）

#### 第一步：创建Twitter List
1. 登录Twitter开发者账户
2. 在Twitter上创建一个新的List，命名为"AI KOL"
3. 将以下推荐的AI领域KOL添加到列表中：

**技术向KOL:**
- @karpathy (Andrej Karpathy)
- @ylecun (Yann LeCun)
- @AndrewYNg (Andrew Ng)
- @sama (Sam Altman)
- @gdb (Geoffrey Hinton)
- @jasonwei (Jason Wei)
- @JimFan (Jim Fan)
- @_akhaliq (Aran Komatsuzaki)

**产品/市场向KOL:**
- @rowancheung (Rowan Cheung)
- @alexandra_amos (Alexandra Amos)
- @mckaywrigley (McKay Wrigley)
- @lennysan (Lenny Rachitsky)

#### 第二步：获取List ID
1. 访问您的List页面
2. 从URL中提取List ID
3. 更新数据库中的配置

```sql
-- 更新Twitter List的source_url
UPDATE source_config 
SET source_url = 'your_actual_list_id_here' 
WHERE source_name = 'AI KOL Twitter List';
```

或者重新运行初始化脚本：
```bash
rm app.db
python init_db.py
```

### 3. 数据库初始化

```bash
python init_db.py
```

## 🔧 信源类型说明

### RSS信源 (rss)
- **优点**: 稳定、标准化、易于处理
- **配置**: 直接使用RSS URL
- **示例**: OpenAI Blog, TechCrunch AI

### API信源 (arxiv, huggingface)
- **优点**: 数据规范、实时性好
- **配置**: 无需额外配置，直接使用
- **示例**: arXiv论文, Hugging Face模型

### Web爬虫信源 (web_scrape)
- **优点**: 覆盖范围广、内容丰富
- **缺点**: 易受网站改版影响
- **配置**: 系统自动处理
- **示例**: Anthropic Blog, Mistral AI News

### GitHub信源 (github)
- **优点**: 获取开源项目动态
- **配置**: 无需额外配置
- **示例**: AI/ML热门项目

### Twitter信源 (twitter, twitter_list)
- **优点**: 实时性强、观点多样
- **配置**: 需要Twitter API密钥和List ID
- **示例**: AI KOL推文

## 📊 信源优先级

### 优先级1 (Priority 1) - 核心信源
- arXiv AI/ML论文
- OpenAI Blog
- Anthropic Blog
- DeepMind Blog
- AI KOL Twitter List

### 优先级2 (Priority 2) - 重要信源
- Hugging Face热门模型
- GitHub Trending AI项目
- TechCrunch AI
- 机器之心
- Product Hunt AI

### 优先级3 (Priority 3) - 补充信源
- Mistral AI News
- Replicate Blog
- AI前线
- A16Z AI

## 🚨 注意事项

### 1. API限制
- **DeepSeek API**: 注意调用频率和Token限制
- **Twitter API**: 遵守速率限制，避免被封禁
- **GitHub**: 注意请求频率，避免触发限制

### 2. 网站结构变化
- Web爬虫信源可能因网站改版而失效
- 定期检查爬虫是否正常工作
- 必要时更新选择器配置

### 3. 内容质量
- 某些信源可能包含重复或低质量内容
- 系统会自动去重，但建议定期检查
- 可根据需要调整信源的优先级

### 4. 法律合规
- 遵守各网站的robots.txt规则
- 合理控制抓取频率
- 注意版权和内容使用规范

## 🔍 故障排除

### 常见问题

**问题1: Twitter List抓取失败**
```bash
# 检查List ID是否正确
python -c "
from models import SessionLocal, SourceConfig
session = SessionLocal()
source = session.query(SourceConfig).filter_by(source_name='AI KOL Twitter List').first()
print(f'List ID: {source.source_url}')
session.close()
"
```

**问题2: Web爬虫失败**
```bash
# 检查网站是否可访问
curl -I "https://www.anthropic.com/index"
curl -I "https://mistral.ai/news/"
```

**问题3: API调用失败**
```bash
# 检查API密钥
cat .env | grep DEEPSEEK_API_KEY
cat .env | grep TWITTER
```

### 调试方法

1. **查看日志**: `logs/app.log`
2. **检查状态**: `python main.py --mode status`
3. **分步测试**: 使用 `--mode fetch` 单独测试数据获取
4. **数据库检查**: 查看 `source_config` 表

## 📈 性能优化

### 1. 抓取频率控制
- RSS信源: 每4-6小时抓取一次
- API信源: 每2-4小时抓取一次
- Web爬虫: 每6-8小时抓取一次
- Twitter: 每1-2小时抓取一次

### 2. 内容过滤
- 设置最小内容长度阈值
- 过滤重复或相似内容
- 根据重要性评分排序

### 3. 存储优化
- 定期清理旧内容
- 压缩长文本内容
- 建立内容索引

## 🎯 自定义信源

### 添加新的RSS信源
```python
# 在init_db.py中添加
SourceConfig(
    source_type="rss",
    source_name="新信源名称",
    source_url="https://example.com/rss.xml",
    priority=2
)
```

### 添加新的Web爬虫信源
```python
# 在init_db.py中添加
SourceConfig(
    source_type="web_scrape",
    source_name="新网站名称",
    source_url="https://example.com",
    priority=2
)
```

### 添加新的API信源
需要创建对应的抓取器类，并在协调器中集成。

---

**配置完成后，您就可以享受全面的AI领域信息覆盖了！** 🚀

如有问题，请查看日志文件或联系技术支持。
