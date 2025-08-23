#!/usr/bin/env python3
"""
检查今天的日报状态
"""

from models import SessionLocal, Digest
from datetime import datetime

def check_today_digest():
    """检查今天的日报"""
    session = SessionLocal()
    
    try:
        # 获取今天的日期
        today = datetime.now().strftime('%Y-%m-%d')
        print(f"📅 今天日期: {today}")
        
        # 检查是否有今天的日报
        today_digest = session.query(Digest).filter(
            Digest.created_at.like(f'{today}%')
        ).first()
        
        if today_digest:
            print(f"✅ 今天的日报已存在")
            print(f"   标题: {today_digest.title}")
            print(f"   状态: {today_digest.status}")
            print(f"   创建时间: {today_digest.created_at}")
            print(f"   内容长度: {len(today_digest.content)} 字符")
        else:
            print(f"❌ 今天的日报不存在")
            
            # 检查最近的日报
            latest = session.query(Digest).order_by(Digest.created_at.desc()).first()
            if latest:
                print(f"📰 最新日报:")
                print(f"   标题: {latest.title}")
                print(f"   创建时间: {latest.created_at}")
                print(f"   状态: {latest.status}")
        
        # 统计所有日报
        total_digests = session.query(Digest).count()
        published_digests = session.query(Digest).filter(Digest.status == 'published').count()
        draft_digests = session.query(Digest).filter(Digest.status == 'draft').count()
        
        print(f"\n📊 日报统计:")
        print(f"   总数: {total_digests}")
        print(f"   已发布: {published_digests}")
        print(f"   草稿: {draft_digests}")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    check_today_digest()
