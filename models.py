"""
AI洞察助手数据模型定义
使用SQLAlchemy ORM管理数据库表结构
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建数据库引擎
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./app.db')
engine = create_engine(DATABASE_URL, echo=False)

# 创建基类
Base = declarative_base()

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class RawContent(Base):
    """原始内容表 - 存储从各信源抓取的原始数据"""
    __tablename__ = "raw_content"
    
    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String(50), nullable=False)  # rss, twitter, arxiv
    source_name = Column(String(100), nullable=False)  # 信源名称
    title = Column(String(500), nullable=True)  # 标题
    content = Column(Text, nullable=False)  # 原始内容
    url = Column(String(1000), nullable=True)  # 原文链接
    published_at = Column(DateTime, nullable=True)  # 发布时间
    created_at = Column(DateTime, default=func.now())
    is_processed = Column(Boolean, default=False)  # 是否已被AI处理
    processing_error = Column(Text, nullable=True)  # 处理错误信息
    
    # 关联关系
    insights = relationship("Insight", back_populates="raw_content")


class Insight(Base):
    """AI洞察表 - 存储AI分析后的结构化洞察"""
    __tablename__ = "insight"
    
    id = Column(Integer, primary_key=True, index=True)
    raw_content_id = Column(Integer, ForeignKey("raw_content.id"), nullable=False)
    summary = Column(Text, nullable=False)  # AI生成的摘要
    analysis = Column(Text, nullable=False)  # AI生成的深度分析
    category = Column(String(100), nullable=True)  # 分类标签
    importance_score = Column(Float, nullable=True)  # 重要性评分
    created_at = Column(DateTime, default=func.now())
    
    # 关联关系
    raw_content = relationship("RawContent", back_populates="insights")


class Digest(Base):
    """日报表 - 存储生成的日报内容"""
    __tablename__ = "digest"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)  # 日报标题
    content = Column(Text, nullable=False)  # Markdown格式的日报内容
    status = Column(String(20), default='draft')  # draft, published
    published_at = Column(DateTime, nullable=True)  # 发布时间
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class SourceConfig(Base):
    """信源配置表 - 存储各信源的配置信息"""
    __tablename__ = "source_config"
    
    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String(50), nullable=False)  # rss, twitter, arxiv
    source_name = Column(String(100), nullable=False)  # 信源名称
    source_url = Column(String(1000), nullable=False)  # 信源URL
    is_active = Column(Boolean, default=True)  # 是否启用
    priority = Column(Integer, default=1)  # 优先级
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
