#!/usr/bin/env python3
"""
检查数据库时间戳
"""

from models import SessionLocal, Insight, RawContent
from datetime import datetime

def check_timestamps():
    """检查数据库时间戳"""
    session = SessionLocal()
    
    try:
        # 当前时间
        now = datetime.now()
        print(f"🕐 当前时间: {now}")
        print(f"   当前日期: {now.strftime('%Y-%m-%d')}")
        
        # 检查最近的洞察
        latest_insights = session.query(Insight).order_by(Insight.created_at.desc()).limit(5).all()
        print(f"\n🧠 最近5条洞察:")
        for i, insight in enumerate(latest_insights):
            print(f"   {i+1}. {insight.created_at} - {insight.summary[:40]}...")
        
        # 检查今天的洞察（使用日期字符串匹配）
        today_str = now.strftime('%Y-%m-%d')
        today_insights = session.query(Insight).filter(
            Insight.created_at.like(f'{today_str}%')
        ).all()
        
        print(f"\n📅 今天({today_str})的洞察:")
        print(f"   数量: {len(today_insights)}")
        
        if today_insights:
            for i, insight in enumerate(today_insights[:3]):
                print(f"   {i+1}. {insight.created_at} - {insight.summary[:40]}...")
        
        # 检查原始内容时间戳
        latest_raw = session.query(RawContent).order_by(RawContent.created_at.desc()).limit(3).all()
        print(f"\n📥 最近3条原始内容:")
        for i, content in enumerate(latest_raw):
            print(f"   {i+1}. {content.created_at} - {content.title[:40]}...")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    check_timestamps()
