"""
通用Web爬虫抓取器
负责抓取没有RSS或API的信源网页内容
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import logging
import time
import random
import re
from urllib.parse import urljoin, urlparse

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebScraper:
    """通用Web爬虫抓取器"""
    
    def __init__(self):
        """初始化Web爬虫"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_anthropic_blog(self) -> List[Dict]:
        """抓取Anthropic博客"""
        try:
            logger.info("开始抓取Anthropic博客")
            
            url = "https://www.anthropic.com/index"
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = []
            
            # 查找博客文章链接
            # 注意：Anthropic的网站结构可能会变化，需要根据实际情况调整
            article_links = soup.find_all('a', href=re.compile(r'/news|/blog|/research'))
            
            for link in article_links[:10]:  # 限制数量
                try:
                    article_url = urljoin(url, link.get('href', ''))
                    article_title = link.get_text().strip()
                    
                    if article_title and article_url:
                        # 获取文章详情
                        article_detail = self._scrape_article_detail(article_url, article_title)
                        if article_detail:
                            articles.append(article_detail)
                        
                        # 添加延迟
                        time.sleep(random.uniform(1, 3))
                        
                except Exception as e:
                    logger.error(f"处理Anthropic文章链接失败: {e}")
                    continue
            
            logger.info(f"成功抓取 {len(articles)} 篇Anthropic博客文章")
            return articles
            
        except Exception as e:
            logger.error(f"抓取Anthropic博客失败: {e}")
            return []
    
    def scrape_mistral_news(self) -> List[Dict]:
        """抓取Mistral AI新闻"""
        try:
            logger.info("开始抓取Mistral AI新闻")
            
            url = "https://mistral.ai/news/"
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = []
            
            # 查找新闻文章
            # 根据Mistral网站的实际结构调整选择器
            news_items = soup.find_all(['article', 'div'], class_=re.compile(r'news|article|post'))
            
            for item in news_items[:10]:
                try:
                    # 提取标题
                    title_elem = item.find(['h1', 'h2', 'h3', 'h4'])
                    title = title_elem.get_text().strip() if title_elem else ""
                    
                    # 提取链接
                    link_elem = item.find('a')
                    article_url = urljoin(url, link_elem.get('href', '')) if link_elem else ""
                    
                    # 提取摘要
                    summary_elem = item.find(['p', 'div'], class_=re.compile(r'summary|excerpt|description'))
                    summary = summary_elem.get_text().strip() if summary_elem else ""
                    
                    if title and article_url:
                        article_info = {
                            'title': f"Mistral AI: {title}",
                            'content': f"标题: {title}\n\n摘要: {summary}",
                            'url': article_url,
                            'published_at': datetime.now(),  # Mistral可能不显示具体时间
                            'source_name': 'Mistral AI News',
                            'source_type': 'web_scrape',
                            'summary': summary
                        }
                        articles.append(article_info)
                        
                except Exception as e:
                    logger.error(f"处理Mistral新闻项失败: {e}")
                    continue
            
            logger.info(f"成功抓取 {len(articles)} 条Mistral AI新闻")
            return articles
            
        except Exception as e:
            logger.error(f"抓取Mistral AI新闻失败: {e}")
            return []
    
    def scrape_product_hunt_ai(self) -> List[Dict]:
        """抓取Product Hunt AI产品"""
        try:
            logger.info("开始抓取Product Hunt AI产品")
            
            url = "https://www.producthunt.com/topics/artificial-intelligence"
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            products = []
            
            # 查找产品项
            # Product Hunt的页面结构可能会变化
            product_items = soup.find_all(['div', 'article'], class_=re.compile(r'product|item|card'))
            
            for item in product_items[:15]:
                try:
                    # 提取产品名称
                    name_elem = item.find(['h3', 'h4', 'h5'])
                    product_name = name_elem.get_text().strip() if name_elem else ""
                    
                    # 提取产品链接
                    link_elem = item.find('a')
                    product_url = urljoin(url, link_elem.get('href', '')) if link_elem else ""
                    
                    # 提取描述
                    desc_elem = item.find(['p', 'div'], class_=re.compile(r'description|tagline'))
                    description = desc_elem.get_text().strip() if desc_elem else ""
                    
                    # 提取标签
                    tag_elements = item.find_all(['span', 'div'], class_=re.compile(r'tag|category'))
                    tags = [tag.get_text().strip() for tag in tag_elements if tag.get_text().strip()]
                    
                    if product_name and product_url:
                        product_info = {
                            'title': f"Product Hunt AI产品: {product_name}",
                            'content': f"产品名称: {product_name}\n\n描述: {description}\n\n标签: {', '.join(tags[:3])}",
                            'url': product_url,
                            'published_at': datetime.now(),
                            'source_name': 'Product Hunt AI',
                            'source_type': 'web_scrape',
                            'product_name': product_name,
                            'description': description,
                            'tags': tags
                        }
                        products.append(product_info)
                        
                except Exception as e:
                    logger.error(f"处理Product Hunt产品项失败: {e}")
                    continue
            
            logger.info(f"成功抓取 {len(products)} 个Product Hunt AI产品")
            return products
            
        except Exception as e:
            logger.error(f"抓取Product Hunt AI产品失败: {e}")
            return []
    
    def scrape_a16z_ai(self) -> List[Dict]:
        """抓取A16Z AI相关内容"""
        try:
            logger.info("开始抓取A16Z AI内容")
            
            url = "https://a16z.com/category/ai/"
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            articles = []
            
            # 查找AI相关文章
            article_items = soup.find_all(['article', 'div'], class_=re.compile(r'post|article|entry'))
            
            for item in article_items[:10]:
                try:
                    # 提取标题
                    title_elem = item.find(['h1', 'h2', 'h3', 'h4'])
                    title = title_elem.get_text().strip() if title_elem else ""
                    
                    # 提取链接
                    link_elem = item.find('a')
                    article_url = urljoin(url, link_elem.get('href', '')) if link_elem else ""
                    
                    # 提取摘要
                    summary_elem = item.find(['p', 'div'], class_=re.compile(r'excerpt|summary|description'))
                    summary = summary_elem.get_text().strip() if summary_elem else ""
                    
                    # 提取作者
                    author_elem = item.find(['span', 'div'], class_=re.compile(r'author|byline'))
                    author = author_elem.get_text().strip() if author_elem else ""
                    
                    if title and article_url:
                        article_info = {
                            'title': f"A16Z AI: {title}",
                            'content': f"标题: {title}\n\n作者: {author}\n\n摘要: {summary}",
                            'url': article_url,
                            'published_at': datetime.now(),
                            'source_name': 'A16Z AI',
                            'source_type': 'web_scrape',
                            'author': author,
                            'summary': summary
                        }
                        articles.append(article_info)
                        
                except Exception as e:
                    logger.error(f"处理A16Z文章项失败: {e}")
                    continue
            
            logger.info(f"成功抓取 {len(articles)} 篇A16Z AI文章")
            return articles
            
        except Exception as e:
            logger.error(f"抓取A16Z AI内容失败: {e}")
            return []
    
    def _scrape_article_detail(self, article_url: str, title: str) -> Optional[Dict]:
        """抓取文章详情"""
        try:
            response = self.session.get(article_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取文章内容
            content_elem = soup.find(['article', 'div', 'main'], class_=re.compile(r'content|post|article'))
            if not content_elem:
                content_elem = soup.find('body')
            
            content = content_elem.get_text().strip() if content_elem else ""
            
            # 提取发布时间
            time_elem = soup.find(['time', 'span'], {'datetime': True})
            published_time = None
            if time_elem:
                try:
                    published_time = datetime.fromisoformat(time_elem['datetime'].replace('Z', '+00:00'))
                except:
                    published_time = datetime.now()
            else:
                published_time = datetime.now()
            
            # 构建文章信息
            article_info = {
                'title': f"Anthropic: {title}",
                'content': f"标题: {title}\n\n内容: {content[:500]}{'...' if len(content) > 500 else ''}",
                'url': article_url,
                'published_at': published_time,
                'source_name': 'Anthropic Blog',
                'source_type': 'web_scrape',
                'full_content': content
            }
            
            return article_info
            
        except Exception as e:
            logger.error(f"抓取文章详情失败 {article_url}: {e}")
            return None
    
    def scrape_generic_website(self, url: str, source_name: str, selectors: Dict) -> List[Dict]:
        """
        通用网站抓取方法
        
        Args:
            url: 网站URL
            source_name: 信源名称
            selectors: 选择器配置
            
        Returns:
            抓取的内容列表
        """
        try:
            logger.info(f"开始抓取通用网站: {source_name}")
            
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            items = []
            
            # 使用配置的选择器查找内容
            container_selector = selectors.get('container', 'body')
            title_selector = selectors.get('title', 'h1, h2, h3')
            link_selector = selectors.get('link', 'a')
            content_selector = selectors.get('content', 'p')
            
            containers = soup.select(container_selector)
            
            for container in containers[:20]:  # 限制数量
                try:
                    # 提取标题
                    title_elem = container.select_one(title_selector)
                    title = title_elem.get_text().strip() if title_elem else ""
                    
                    # 提取链接
                    link_elem = container.select_one(link_selector)
                    item_url = urljoin(url, link_elem.get('href', '')) if link_elem else ""
                    
                    # 提取内容
                    content_elem = container.select_one(content_selector)
                    content = content_elem.get_text().strip() if content_elem else ""
                    
                    if title and item_url:
                        item_info = {
                            'title': f"{source_name}: {title}",
                            'content': f"标题: {title}\n\n内容: {content[:300]}{'...' if len(content) > 300 else ''}",
                            'url': item_url,
                            'published_at': datetime.now(),
                            'source_name': source_name,
                            'source_type': 'web_scrape'
                        }
                        items.append(item_info)
                        
                except Exception as e:
                    logger.error(f"处理通用网站内容项失败: {e}")
                    continue
            
            logger.info(f"成功抓取 {len(items)} 条{source_name}内容")
            return items
            
        except Exception as e:
            logger.error(f"抓取通用网站失败 {source_name}: {e}")
            return []
    
    def scrape_multiple_sources(self, source_configs: List[Dict]) -> List[Dict]:
        """
        批量抓取多个信源
        
        Args:
            source_configs: 信源配置列表
            
        Returns:
            所有内容的合并列表
        """
        all_content = []
        
        for config in source_configs:
            try:
                source_type = config.get('source_type', '')
                source_name = config.get('source_name', 'Unknown')
                source_url = config.get('source_url', '')
                
                logger.info(f"开始抓取Web爬虫信源: {source_name}")
                
                if source_type == 'web_scrape':
                    if 'anthropic' in source_name.lower():
                        content = self.scrape_anthropic_blog()
                    elif 'mistral' in source_name.lower():
                        content = self.scrape_mistral_news()
                    elif 'product hunt' in source_name.lower():
                        content = self.scrape_product_hunt_ai()
                    elif 'a16z' in source_name.lower():
                        content = self.scrape_a16z_ai()
                    else:
                        # 使用通用抓取方法
                        selectors = config.get('selectors', {})
                        content = self.scrape_generic_website(source_url, source_name, selectors)
                    
                    if content:
                        all_content.extend(content)
                        logger.info(f"成功抓取 {source_name}: {len(content)} 条内容")
                    else:
                        logger.warning(f"信源 {source_name} 未抓取到内容")
                    
                    # 添加延迟
                    time.sleep(random.uniform(2, 5))
                    
            except Exception as e:
                logger.error(f"抓取信源失败 {source_name}: {e}")
                continue
        
        logger.info(f"批量抓取完成，总共获取 {len(all_content)} 条内容")
        return all_content


if __name__ == "__main__":
    # 测试代码
    scraper = WebScraper()
    
    print("开始测试Web爬虫抓取器...")
    
    # 测试抓取Anthropic博客
    print("\n测试抓取Anthropic博客...")
    anthropic_articles = scraper.scrape_anthropic_blog()
    print(f"抓取结果: {len(anthropic_articles)} 篇文章")
    
    for article in anthropic_articles[:2]:
        print(f"标题: {article['title']}")
        print(f"URL: {article['url']}")
        print("---")
    
    # 测试抓取Mistral新闻
    print("\n测试抓取Mistral新闻...")
    mistral_news = scraper.scrape_mistral_news()
    print(f"抓取结果: {len(mistral_news)} 条新闻")
    
    for news in mistral_news[:2]:
        print(f"标题: {news['title']}")
        print(f"URL: {news['url']}")
        print("---")
