"""
RSS源数据抓取器
负责抓取各种RSS源的最新AI相关内容
"""

import feedparser
import requests
from datetime import datetime
from typing import List, Dict, Optional
import logging
from bs4 import BeautifulSoup
import time
import random

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RSSFetcher:
    """RSS源数据抓取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch_rss_feed(self, feed_url: str, source_name: str) -> List[Dict]:
        """
        抓取单个RSS源
        
        Args:
            feed_url: RSS源URL
            source_name: 信源名称
            
        Returns:
            包含文章信息的字典列表
        """
        try:
            logger.info(f"开始抓取RSS源: {source_name} ({feed_url})")
            
            # 添加随机延迟避免被反爬
            time.sleep(random.uniform(1, 3))
            
            # 解析RSS源
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"RSS源解析异常: {source_name}")
            
            articles = []
            
            for entry in feed.entries[:20]:  # 限制最新20篇文章
                try:
                    # 提取文章信息
                    article = {
                        'title': entry.get('title', ''),
                        'content': self._extract_content(entry),
                        'url': entry.get('link', ''),
                        'published_at': self._parse_date(entry.get('published', '')),
                        'source_name': source_name,
                        'source_type': 'rss'
                    }
                    
                    # 过滤掉标题或内容为空的文章
                    if article['title'] and article['content']:
                        articles.append(article)
                        
                except Exception as e:
                    logger.error(f"处理文章时出错: {e}")
                    continue
            
            logger.info(f"成功抓取 {len(articles)} 篇文章来自 {source_name}")
            return articles
            
        except Exception as e:
            logger.error(f"抓取RSS源失败 {source_name}: {e}")
            return []
    
    def _extract_content(self, entry) -> str:
        """提取文章内容"""
        # 优先使用content字段
        if hasattr(entry, 'content') and entry.content:
            return entry.content[0].value
        
        # 使用summary字段
        if hasattr(entry, 'summary'):
            return entry.summary
        
        # 使用description字段
        if hasattr(entry, 'description'):
            return entry.description
        
        return ""
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """解析日期字符串"""
        if not date_str:
            return None
        
        try:
            # 尝试多种日期格式
            date_formats = [
                '%a, %d %b %Y %H:%M:%S %z',  # RFC 822
                '%a, %d %b %Y %H:%M:%S %Z',  # RFC 822 with timezone name
                '%Y-%m-%dT%H:%M:%S%z',       # ISO 8601
                '%Y-%m-%dT%H:%M:%S',         # ISO 8601 without timezone
                '%Y-%m-%d %H:%M:%S',         # Common format
                '%Y-%m-%d'                    # Date only
            ]
            
            for fmt in date_formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # 如果都失败了，使用当前时间
            logger.warning(f"无法解析日期: {date_str}，使用当前时间")
            return datetime.now()
            
        except Exception as e:
            logger.error(f"日期解析失败: {date_str}, 错误: {e}")
            return datetime.now()
    
    def fetch_multiple_feeds(self, feed_configs: List[Dict]) -> List[Dict]:
        """
        批量抓取多个RSS源
        
        Args:
            feed_configs: 包含feed_url和source_name的配置列表
            
        Returns:
            所有文章的合并列表
        """
        all_articles = []
        
        for config in feed_configs:
            try:
                articles = self.fetch_rss_feed(
                    config['source_url'], 
                    config['source_name']
                )
                all_articles.extend(articles)
                
            except Exception as e:
                logger.error(f"抓取RSS源失败 {config['source_name']}: {e}")
                continue
        
        logger.info(f"总共抓取到 {len(all_articles)} 篇文章")
        return all_articles
    
    def clean_content(self, content: str) -> str:
        """清理HTML内容，提取纯文本"""
        if not content:
            return ""
        
        try:
            # 使用BeautifulSoup清理HTML标签
            soup = BeautifulSoup(content, 'html.parser')
            
            # 移除script和style标签
            for script in soup(["script", "style"]):
                script.decompose()
            
            # 获取纯文本
            text = soup.get_text()
            
            # 清理多余的空白字符
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            logger.error(f"内容清理失败: {e}")
            return content


if __name__ == "__main__":
    # 测试代码
    fetcher = RSSFetcher()
    
    test_feeds = [
        {
            'source_url': 'https://openai.com/blog/rss.xml',
            'source_name': 'OpenAI Blog'
        }
    ]
    
    articles = fetcher.fetch_multiple_feeds(test_feeds)
    print(f"测试抓取结果: {len(articles)} 篇文章")
    
    for article in articles[:3]:
        print(f"标题: {article['title']}")
        print(f"内容长度: {len(article['content'])}")
        print(f"发布时间: {article['published_at']}")
        print("---")
