#!/usr/bin/env python3
"""
检查数据库状态
"""

from models import SessionLocal, RawContent, Insight
from datetime import datetime

def check_database():
    """检查数据库状态"""
    session = SessionLocal()
    
    try:
        # 获取今天的日期
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"📅 今天日期: {today}")
        
        # 检查原始内容
        today_raw_content = session.query(RawContent).filter(
            RawContent.created_at.like(f'{today}%')
        ).all()
        
        print(f"\n📥 原始内容检查:")
        print(f"   今天数量: {len(today_raw_content)}")
        print(f"   总数量: {session.query(RawContent).count()}")
        
        if today_raw_content:
            print(f"   最新内容:")
            latest_raw = today_raw_content[0]
            print(f"     标题: {latest_raw.title[:50]}...")
            print(f"     来源: {latest_raw.source_name}")
            print(f"     类型: {latest_raw.source_type}")
            print(f"     创建时间: {latest_raw.created_at}")
            print(f"     已处理: {latest_raw.is_processed}")
        
        # 检查洞察数据
        today_insights = session.query(Insight).filter(
            Insight.created_at.like(f'{today}%')
        ).all()
        
        print(f"\n🧠 洞察数据检查:")
        print(f"   今天数量: {len(today_insights)}")
        print(f"   总数量: {session.query(Insight).count()}")
        
        if today_insights:
            print(f"   最新洞察:")
            latest_insight = today_insights[0]
            print(f"     摘要: {latest_insight.summary[:50]}...")
            print(f"     分类: {latest_insight.category}")
            print(f"     重要性: {latest_insight.importance_score}")
            print(f"     创建时间: {latest_insight.created_at}")
        
        # 检查未处理的内容
        unprocessed = session.query(RawContent).filter_by(is_processed=False).count()
        print(f"\n⏳ 处理状态:")
        print(f"   未处理内容: {unprocessed}")
        print(f"   已处理内容: {session.query(RawContent).filter_by(is_processed=True).count()}")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    check_database()
