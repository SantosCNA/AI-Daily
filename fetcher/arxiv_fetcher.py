"""
arXiv论文抓取器
负责抓取arXiv上最新的AI/ML相关论文
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import time
import random
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArxivFetcher:
    """arXiv论文抓取器"""
    
    def __init__(self):
        """初始化arXiv抓取器"""
        self.base_url = "http://export.arxiv.org/api/query"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_recent_papers(self, category: str = "cs.AI", max_results: int = 50) -> List[Dict]:
        """
        抓取指定类别的最新论文
        
        Args:
            category: arXiv类别，如 cs.AI, cs.LG, cs.CL
            max_results: 最大结果数量
            
        Returns:
            论文信息列表
        """
        try:
            logger.info(f"开始抓取arXiv {category} 类别的最新论文")
            
            # 构建查询参数
            params = {
                'search_query': f'cat:{category}',
                'start': 0,
                'max_results': max_results,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending'
            }
            
            # 发送请求
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            
            # 解析XML响应
            papers = self._parse_arxiv_xml(response.text)
            
            logger.info(f"成功抓取 {len(papers)} 篇论文来自 {category}")
            return papers
            
        except Exception as e:
            logger.error(f"抓取arXiv论文失败 {category}: {e}")
            return []
    
    def fetch_ai_related_papers(self, max_results: int = 100) -> List[Dict]:
        """
        抓取AI相关的多个类别论文
        
        Args:
            max_results: 每个类别的最大结果数量
            
        Returns:
            所有论文的合并列表
        """
        # AI相关的主要类别
        ai_categories = [
            "cs.AI",      # Artificial Intelligence
            "cs.LG",      # Machine Learning
            "cs.CL",      # Computation and Language
            "cs.CV",      # Computer Vision
            "cs.NE",      # Neural and Evolutionary Computing
            "cs.RO",      # Robotics
            "stat.ML"     # Machine Learning (Statistics)
        ]
        
        all_papers = []
        
        for category in ai_categories:
            try:
                papers = self.fetch_recent_papers(category, max_results // len(ai_categories))
                all_papers.extend(papers)
                
                # 添加延迟避免请求过快
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.error(f"抓取类别 {category} 失败: {e}")
                continue
        
        # 去重（基于论文ID）
        unique_papers = {}
        for paper in all_papers:
            if paper['arxiv_id'] not in unique_papers:
                unique_papers[paper['arxiv_id']] = paper
        
        unique_papers_list = list(unique_papers.values())
        logger.info(f"总共抓取到 {len(unique_papers_list)} 篇唯一论文")
        
        return unique_papers_list
    
    def _parse_arxiv_xml(self, xml_content: str) -> List[Dict]:
        """解析arXiv XML响应"""
        try:
            root = ET.fromstring(xml_content)
            
            # 定义命名空间
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            papers = []
            
            # 查找所有entry元素
            for entry in root.findall('.//atom:entry', namespaces):
                try:
                    paper = self._parse_paper_entry(entry, namespaces)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    logger.error(f"解析论文条目时出错: {e}")
                    continue
            
            return papers
            
        except Exception as e:
            logger.error(f"解析arXiv XML失败: {e}")
            return []
    
    def _parse_paper_entry(self, entry, namespaces) -> Optional[Dict]:
        """解析单个论文条目"""
        try:
            # 提取基本信息
            title = entry.find('.//atom:title', namespaces)
            title_text = title.text.strip() if title is not None and title.text else "无标题"
            
            # 提取摘要
            summary = entry.find('.//atom:summary', namespaces)
            summary_text = summary.text.strip() if summary is not None and summary.text else ""
            
            # 提取发布时间
            published = entry.find('.//atom:published', namespaces)
            published_date = None
            if published is not None and published.text:
                try:
                    published_date = datetime.fromisoformat(published.text.replace('Z', '+00:00'))
                except:
                    published_date = datetime.now()
            
            # 提取arXiv ID
            arxiv_id = entry.find('.//arxiv:id', namespaces)
            arxiv_id_text = arxiv_id.text if arxiv_id is not None else ""
            
            # 提取作者信息
            authors = []
            for author in entry.findall('.//atom:author/atom:name', namespaces):
                if author.text:
                    authors.append(author.text.strip())
            
            # 提取分类
            categories = []
            for category in entry.findall('.//arxiv:primary_category', namespaces):
                if category.get('term'):
                    categories.append(category.get('term'))
            
            # 构建论文信息
            paper = {
                'title': title_text,
                'content': f"摘要: {summary_text}\n\n作者: {', '.join(authors)}\n分类: {', '.join(categories)}",
                'url': f"https://arxiv.org/abs/{arxiv_id_text}",
                'published_at': published_date,
                'source_name': f"arXiv {', '.join(categories)}",
                'source_type': 'arxiv',
                'arxiv_id': arxiv_id_text,
                'authors': authors,
                'categories': categories,
                'summary': summary_text
            }
            
            return paper
            
        except Exception as e:
            logger.error(f"解析论文条目时出错: {e}")
            return None
    
    def search_papers(self, query: str, max_results: int = 50) -> List[Dict]:
        """
        搜索论文
        
        Args:
            query: 搜索关键词
            max_results: 最大结果数量
            
        Returns:
            搜索结果列表
        """
        try:
            logger.info(f"开始搜索arXiv论文: {query}")
            
            # 构建搜索查询
            params = {
                'search_query': query,
                'start': 0,
                'max_results': max_results,
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            # 发送请求
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            
            # 解析XML响应
            papers = self._parse_arxiv_xml(response.text)
            
            logger.info(f"搜索 '{query}' 成功找到 {len(papers)} 篇论文")
            return papers
            
        except Exception as e:
            logger.error(f"搜索论文失败 '{query}': {e}")
            return []
    
    def fetch_trending_ai_papers(self) -> List[Dict]:
        """
        抓取AI领域热门论文
        
        Returns:
            热门论文列表
        """
        # 热门AI关键词
        trending_keywords = [
            "large language models",
            "transformer",
            "GPT",
            "BERT",
            "diffusion models",
            "reinforcement learning",
            "computer vision",
            "natural language processing",
            "neural networks",
            "deep learning"
        ]
        
        all_papers = []
        
        for keyword in trending_keywords[:5]:  # 限制关键词数量
            try:
                papers = self.search_papers(keyword, max_results=10)
                all_papers.extend(papers)
                
                # 添加延迟
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.error(f"搜索关键词 '{keyword}' 失败: {e}")
                continue
        
        # 去重
        unique_papers = {}
        for paper in all_papers:
            if paper['arxiv_id'] not in unique_papers:
                unique_papers[paper['arxiv_id']] = paper
        
        unique_papers_list = list(unique_papers.values())
        logger.info(f"总共抓取到 {len(unique_papers_list)} 篇热门论文")
        
        return unique_papers_list
    
    def clean_content(self, content: str) -> str:
        """清理论文内容"""
        if not content:
            return ""
        
        # 移除多余的空白字符
        content = re.sub(r'\s+', ' ', content)
        
        # 移除特殊字符
        content = re.sub(r'[^\w\s\-.,;:!?()]', '', content)
        
        return content.strip()


if __name__ == "__main__":
    # 测试代码
    fetcher = ArxivFetcher()
    
    print("开始测试arXiv抓取器...")
    
    # 测试抓取最新论文
    papers = fetcher.fetch_recent_papers("cs.AI", max_results=5)
    print(f"测试抓取结果: {len(papers)} 篇论文")
    
    for paper in papers[:3]:
        print(f"标题: {paper['title']}")
        print(f"摘要长度: {len(paper['summary'])}")
        print(f"发布时间: {paper['published_at']}")
        print(f"分类: {paper['categories']}")
        print("---")
