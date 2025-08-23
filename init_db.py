"""
数据库初始化脚本
创建数据库表并插入初始信源配置
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import init_db, SessionLocal, SourceConfig

# 加载环境变量
load_dotenv()


def insert_default_sources():
    """插入默认的信源配置"""
    session = SessionLocal()
    
    try:
        # 检查是否已有数据
        existing_sources = session.query(SourceConfig).count()
        if existing_sources > 0:
            print("信源配置已存在，跳过初始化")
            return
        
        # 默认信源配置 - 基于新的信源列表
        default_sources = [
            # ===== 技术核心 (Technical Core) =====
            # arXiv - 论文预印本
            SourceConfig(
                source_type="arxiv",
                source_name="arXiv AI/ML Papers",
                source_url="http://export.arxiv.org/api/query?search_query=cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.CV&sortBy=submittedDate&order=descending&max_results=50",
                priority=1
            ),
            
            # Hugging Face Trending
            SourceConfig(
                source_type="huggingface",
                source_name="Hugging Face Trending Models",
                source_url="https://huggingface.co/api/models?sort=trending&limit=50",
                priority=1
            ),
            
            # GitHub Trending
            SourceConfig(
                source_type="github",
                source_name="GitHub Trending AI/ML",
                source_url="https://github.com/trending?since=daily&language=python",
                priority=2
            ),
            
            # Twitter List (需要配置List ID)
            SourceConfig(
                source_type="twitter_list",
                source_name="AI KOL Twitter List",
                source_url="1959163650708840833",  # 用户配置的Twitter List ID
                priority=1
            ),
            
            # ===== 产品与发布 (Product & Launch) =====
            # OpenAI Blog
            SourceConfig(
                source_type="rss",
                source_name="OpenAI Blog",
                source_url="https://openai.com/blog/rss.xml",
                priority=1
            ),
            
            # Anthropic Blog
            SourceConfig(
                source_type="web_scrape",
                source_name="Anthropic Blog",
                source_url="https://www.anthropic.com/index",
                priority=1
            ),
            
            # DeepMind Blog
            SourceConfig(
                source_type="rss",
                source_name="DeepMind Blog",
                source_url="https://www.deepmind.com/blog/rss.xml",
                priority=1
            ),
            
            # Mistral AI News
            SourceConfig(
                source_type="web_scrape",
                source_name="Mistral AI News",
                source_url="https://mistral.ai/news/",
                priority=2
            ),
            
            # Replicate Blog
            SourceConfig(
                source_type="rss",
                source_name="Replicate Blog",
                source_url="https://replicate.com/blog/rss.xml",
                priority=2
            ),
            
            # Product Hunt AI
            SourceConfig(
                source_type="rss",
                source_name="Product Hunt AI",
                source_url="https://www.producthunt.com/feed/topics/1-artificial-intelligence",
                priority=2
            ),
            
            # ===== 市场与生态 (Market & Ecosystem) =====
            # TechCrunch AI
            SourceConfig(
                source_type="rss",
                source_name="TechCrunch AI",
                source_url="https://techcrunch.com/tag/ai/feed/",
                priority=1
            ),
            
            # 机器之心
            SourceConfig(
                source_type="rss",
                source_name="机器之心",
                source_url="https://www.jiqizhixin.com/rss",
                priority=1
            ),
            
            # AI前线 (InfoQ)
            SourceConfig(
                source_type="rss",
                source_name="AI前线",
                source_url="https://feed.infoq.com/ai/",
                priority=2
            ),
            
            # A16Z AI
            SourceConfig(
                source_type="rss",
                source_name="A16Z AI",
                source_url="https://a16z.com/feed/",
                priority=2
            ),
            
            # ===== 保留原有重要信源 =====
            # Google AI Blog
            SourceConfig(
                source_type="rss",
                source_name="Google AI Blog",
                source_url="https://ai.googleblog.com/feeds/posts/default",
                priority=1
            ),
            
            # Microsoft AI Blog
            SourceConfig(
                source_type="rss",
                source_name="Microsoft AI Blog",
                source_url="https://blogs.microsoft.com/ai/feed/",
                priority=2
            ),
            
            # VentureBeat AI
            SourceConfig(
                source_type="rss",
                source_name="VentureBeat AI",
                source_url="https://venturebeat.com/category/ai/feed/",
                priority=2
            ),
        ]
        
        # 批量插入
        session.add_all(default_sources)
        session.commit()
        
        print(f"成功插入 {len(default_sources)} 个默认信源配置")
        print("\n=== 信源配置说明 ===")
        print("1. arXiv: 自动获取AI/ML领域最新论文")
        print("2. Hugging Face: 获取热门开源模型")
        print("3. GitHub Trending: 获取热门AI项目")
        print("4. Twitter List: 需要配置您的Twitter List ID")
        print("5. 各公司博客: OpenAI, Anthropic, DeepMind等")
        print("6. 媒体信源: TechCrunch, 机器之心, AI前线等")
        print("\n⚠️  重要提醒:")
        print("1. Twitter API密钥已配置完成")
        print("2. 您需要创建Twitter List并添加AI KOL")
        print("3. 获取List ID后，更新数据库中的配置")
        print("4. 某些信源可能需要额外的配置或API密钥")
        
    except Exception as e:
        print(f"插入默认信源时出错: {e}")
        session.rollback()
    finally:
        session.close()


def main():
    """主函数"""
    print("开始初始化AI洞察助手数据库...")
    
    try:
        # 创建数据库表
        init_db()
        print("✓ 数据库表创建成功")
        
        # 插入默认信源配置
        insert_default_sources()
        print("✓ 默认信源配置插入成功")
        
        print("\n🎉 数据库初始化完成！")
        print("现在可以运行 main.py 开始数据抓取和AI处理流程")
        print("\n⚠️  重要提醒:")
        print("1. ✅ DeepSeek API密钥已配置")
        print("2. ✅ Twitter API密钥已配置")
        print("3. ✅ Twitter Access Token已配置")
        print("4. ✅ Twitter List ID已配置: 1959163650708840833")
        print("5. ✅ 邮件通知已配置: tahminasantos273@gmail.com")
        print("6. 📝 查看 SOURCE_CONFIG.md 了解详细配置步骤")
        print("\n📋 下一步操作:")
        print("1. 运行 python test_config.py 测试所有配置")
        print("2. 运行 python main.py 测试完整流水线")
        print("3. 检查邮件通知是否正常")
        print("4. 访问审核界面查看生成的日报")
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
