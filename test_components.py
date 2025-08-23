#!/usr/bin/env python3
"""
测试各个组件的功能
"""

def test_rss_fetcher():
    """测试RSS抓取器"""
    print("🔍 测试RSS抓取器...")
    try:
        from fetcher.rss_fetcher import RSSFetcher
        fetcher = RSSFetcher()
        
        # 测试单个RSS源
        test_url = "https://openai.com/blog/rss.xml"
        articles = fetcher.fetch_rss_feed(test_url, "OpenAI Blog")
        
        if articles:
            print(f"✅ RSS抓取成功: {len(articles)} 篇文章")
            print(f"   示例文章: {articles[0]['title'][:50]}...")
        else:
            print("❌ RSS抓取失败: 没有获取到文章")
            
    except Exception as e:
        print(f"❌ RSS抓取器测试失败: {e}")

def test_content_filter():
    """测试内容筛选器"""
    print("\n🔍 测试内容筛选器...")
    try:
        from fetcher.content_filter import ContentFilter
        
        # 创建测试内容
        test_content = [
            {
                'title': 'Test Article 1',
                'content': 'This is a test article about AI technology',
                'url': 'http://test1.com',
                'source_name': 'Test Source',
                'source_type': 'rss'
            },
            {
                'title': 'Test Article 2',
                'content': 'Another test article about machine learning',
                'url': 'http://test2.com',
                'source_name': 'Test Source',
                'source_type': 'rss'
            }
        ]
        
        filter_instance = ContentFilter()
        filtered = filter_instance.filter_rss_content(test_content)
        
        print(f"✅ 内容筛选成功: {len(filtered)} 篇文章通过筛选")
        
    except Exception as e:
        print(f"❌ 内容筛选器测试失败: {e}")

def test_ai_client():
    """测试AI客户端"""
    print("\n🔍 测试AI客户端...")
    try:
        from ai_processor.openai_client import DeepSeekClient
        
        client = DeepSeekClient()
        print("✅ DeepSeek客户端初始化成功")
        
        # 测试简单的洞察生成
        test_content = "OpenAI发布了新的GPT-5模型，性能大幅提升"
        insight = client.generate_insight(test_content, "rss")
        
        if insight and 'summary' in insight:
            print(f"✅ AI洞察生成成功: {insight['summary'][:50]}...")
        else:
            print("❌ AI洞察生成失败")
            
    except Exception as e:
        print(f"❌ AI客户端测试失败: {e}")

def test_database():
    """测试数据库操作"""
    print("\n🔍 测试数据库操作...")
    try:
        from models import SessionLocal, RawContent, Insight
        
        session = SessionLocal()
        
        # 测试查询
        raw_count = session.query(RawContent).count()
        insight_count = session.query(Insight).count()
        
        print(f"✅ 数据库查询成功")
        print(f"   原始内容: {raw_count} 条")
        print(f"   洞察数据: {insight_count} 条")
        
        # 测试最新数据
        latest_raw = session.query(RawContent).order_by(RawContent.created_at.desc()).first()
        if latest_raw:
            print(f"   最新内容: {latest_raw.title[:50]}...")
        
        session.close()
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")

def test_main_pipeline():
    """测试主流水线"""
    print("\n🔍 测试主流水线...")
    try:
        from ai_processor.orchestrator import AIOrchestrator
        
        orchestrator = AIOrchestrator()
        print("✅ AI协调器初始化成功")
        
        # 测试数据获取（限制数量）
        print("   开始测试数据获取...")
        raw_contents = orchestrator._fetch_all_content()
        
        if raw_contents:
            print(f"✅ 数据获取成功: {len(raw_contents)} 条内容")
        else:
            print("❌ 数据获取失败")
            
    except Exception as e:
        print(f"❌ 主流水线测试失败: {e}")

if __name__ == "__main__":
    print("🚀 开始全面功能检测...\n")
    
    test_rss_fetcher()
    test_content_filter()
    test_ai_client()
    test_database()
    test_main_pipeline()
    
    print("\n🎉 全面功能检测完成！")
