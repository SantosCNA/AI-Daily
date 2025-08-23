"""
GitHub Trending数据抓取器
负责抓取GitHub上的热门AI/ML项目
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional
import logging
import time
import random
import re

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitHubFetcher:
    """GitHub Trending数据抓取器"""
    
    def __init__(self):
        """初始化GitHub抓取器"""
        self.base_url = "https://github.com/trending"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch_trending_repos(self, language: str = "python", since: str = "daily", spoken_language: str = "") -> List[Dict]:
        """
        抓取GitHub Trending仓库
        
        Args:
            language: 编程语言 (python, jupyter-notebook, javascript等)
            since: 时间范围 (daily, weekly, monthly)
            spoken_language: 语言代码 (zh, en等)
            
        Returns:
            仓库信息列表
        """
        try:
            logger.info(f"开始抓取GitHub Trending仓库，语言: {language}, 时间: {since}")
            
            # 构建URL
            url = self.base_url
            params = []
            
            if language:
                params.append(f"language={language}")
            if since:
                params.append(f"since={since}")
            if spoken_language:
                params.append(f"spoken_language_code={spoken_language}")
            
            if params:
                url += "?" + "&".join(params)
            
            # 发送请求
            response = self.session.get(url)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找仓库列表
            repos = self._parse_trending_page(soup)
            
            logger.info(f"成功抓取 {len(repos)} 个热门仓库")
            return repos
            
        except Exception as e:
            logger.error(f"抓取GitHub Trending失败: {e}")
            return []
    
    def fetch_ai_ml_trending(self, limit: int = 30) -> List[Dict]:
        """
        抓取AI/ML相关的热门仓库
        
        Args:
            limit: 获取仓库数量
            
        Returns:
            AI/ML仓库信息列表
        """
        # AI/ML相关的编程语言
        ai_languages = [
            "python",           # Python是AI/ML的主要语言
            "jupyter-notebook", # Jupyter notebooks
            "javascript",       # 前端AI应用
            "typescript",       # TypeScript AI项目
            "rust",            # Rust AI项目
            "go",              # Go AI项目
            "java",            # Java AI项目
            "c++",             # C++ AI项目
        ]
        
        all_repos = []
        
        for lang in ai_languages[:4]:  # 限制语言数量避免请求过多
            try:
                repos = self.fetch_trending_repos(language=lang, since="daily")
                
                # 过滤AI/ML相关项目
                ai_repos = self._filter_ai_ml_repos(repos)
                all_repos.extend(ai_repos)
                
                # 添加延迟避免请求过快
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.error(f"抓取语言 {lang} 失败: {e}")
                continue
        
        # 去重（基于repo_name）
        unique_repos = {}
        for repo in all_repos:
            repo_key = f"{repo['owner']}/{repo['name']}"
            if repo_key not in unique_repos:
                unique_repos[repo_key] = repo
        
        unique_repos_list = list(unique_repos.values())
        
        # 限制数量
        if len(unique_repos_list) > limit:
            unique_repos_list = unique_repos_list[:limit]
        
        logger.info(f"总共抓取到 {len(unique_repos_list)} 个唯一AI/ML仓库")
        return unique_repos_list
    
    def _parse_trending_page(self, soup: BeautifulSoup) -> List[Dict]:
        """解析Trending页面"""
        repos = []
        
        try:
            # 查找仓库文章
            repo_articles = soup.find_all('article', class_='Box-row')
            
            for article in repo_articles:
                try:
                    repo_info = self._parse_repo_article(article)
                    if repo_info:
                        repos.append(repo_info)
                except Exception as e:
                    logger.error(f"解析仓库文章时出错: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"解析Trending页面失败: {e}")
        
        return repos
    
    def _parse_repo_article(self, article: BeautifulSoup) -> Optional[Dict]:
        """解析单个仓库文章"""
        try:
            # 提取仓库名称和所有者
            repo_link = article.find('h2', class_='h3').find('a')
            if not repo_link:
                return None
            
            repo_path = repo_link.get('href', '').strip('/')
            if not repo_path:
                return None
            
            owner, name = repo_path.split('/', 1)
            
            # 提取描述
            description_elem = article.find('p')
            description = description_elem.get_text().strip() if description_elem else ""
            
            # 提取编程语言
            language_elem = article.find('span', {'itemprop': 'programmingLanguage'})
            language = language_elem.get_text().strip() if language_elem else "未知"
            
            # 提取星标数
            stars_elem = article.find('a', href=re.compile(r'/stargazers'))
            stars = 0
            if stars_elem:
                stars_text = stars_elem.get_text().strip()
                stars = self._parse_number(stars_text)
            
            # 提取fork数
            forks_elem = article.find('a', href=re.compile(r'/forks'))
            forks = 0
            if forks_elem:
                forks_text = forks_elem.get_text().strip()
                forks = self._parse_number(forks_text)
            
            # 提取今日星标数
            today_stars_elem = article.find('span', class_='d-inline-block float-sm-right')
            today_stars = 0
            if today_stars_elem:
                today_stars_text = today_stars_elem.get_text().strip()
                today_stars = self._parse_number(today_stars_text)
            
            # 构建内容摘要
            content_summary = f"""
仓库: {owner}/{name}
语言: {language}
描述: {description}
总星标: {stars:,}
总Fork: {forks:,}
今日新增星标: {today_stars:,}
            """.strip()
            
            # 构建仓库信息
            repo_info = {
                'title': f"GitHub热门项目: {owner}/{name}",
                'content': content_summary,
                'url': f"https://github.com/{owner}/{name}",
                'published_at': datetime.now(),  # GitHub不提供具体时间，使用当前时间
                'source_name': f"GitHub Trending {language}",
                'source_type': 'github',
                'owner': owner,
                'name': name,
                'full_name': f"{owner}/{name}",
                'description': description,
                'language': language,
                'stars': stars,
                'forks': forks,
                'today_stars': today_stars
            }
            
            return repo_info
            
        except Exception as e:
            logger.error(f"解析仓库文章失败: {e}")
            return None
    
    def _parse_number(self, text: str) -> int:
        """解析数字文本"""
        if not text:
            return 0
        
        try:
            # 移除逗号和k/m等后缀
            text = text.replace(',', '').replace('k', '000').replace('m', '000000')
            return int(float(text))
        except:
            return 0
    
    def _filter_ai_ml_repos(self, repos: List[Dict]) -> List[Dict]:
        """过滤AI/ML相关的仓库"""
        ai_keywords = [
            'ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning',
            'neural network', 'nlp', 'natural language processing', 'computer vision',
            'cv', 'transformer', 'gpt', 'bert', 'llm', 'large language model',
            'diffusion', 'stable diffusion', 'chatbot', 'recommendation',
            'reinforcement learning', 'rl', 'data science', 'data mining',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'opencv',
            'huggingface', 'transformers', 'datasets', 'accelerate'
        ]
        
        ai_repos = []
        
        for repo in repos:
            # 检查仓库名称、描述和标签
            repo_text = f"{repo['full_name']} {repo['description']} {repo['language']}".lower()
            
            if any(keyword in repo_text for keyword in ai_keywords):
                ai_repos.append(repo)
        
        return ai_repos
    
    def search_ai_repos(self, query: str, limit: int = 20) -> List[Dict]:
        """
        搜索AI相关的仓库
        
        Args:
            query: 搜索关键词
            limit: 搜索结果数量
            
        Returns:
            搜索结果列表
        """
        try:
            logger.info(f"开始搜索AI仓库: {query}")
            
            # 构建搜索URL
            search_url = f"https://github.com/search?q={query}&type=repositories&s=stars&o=desc"
            
            response = self.session.get(search_url)
            response.raise_for_status()
            
            # 解析搜索结果页面
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找仓库列表
            repos = self._parse_search_results(soup, limit)
            
            logger.info(f"搜索 '{query}' 成功找到 {len(repos)} 个仓库")
            return repos
            
        except Exception as e:
            logger.error(f"搜索AI仓库失败 '{query}': {e}")
            return []
    
    def _parse_search_results(self, soup: BeautifulSoup, limit: int) -> List[Dict]:
        """解析搜索结果页面"""
        repos = []
        
        try:
            # 查找仓库列表
            repo_items = soup.find_all('div', class_='repo-list-item')
            
            for item in repo_items[:limit]:
                try:
                    repo_info = self._parse_search_repo_item(item)
                    if repo_info:
                        repos.append(repo_info)
                except Exception as e:
                    logger.error(f"解析搜索结果项时出错: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"解析搜索结果页面失败: {e}")
        
        return repos
    
    def _parse_search_repo_item(self, item: BeautifulSoup) -> Optional[Dict]:
        """解析搜索结果中的仓库项"""
        try:
            # 提取仓库名称
            repo_link = item.find('a', class_='v-align-middle')
            if not repo_link:
                return None
            
            repo_path = repo_link.get('href', '').strip('/')
            if not repo_path:
                return None
            
            owner, name = repo_path.split('/', 1)
            
            # 提取描述
            description_elem = item.find('p', class_='mb-1')
            description = description_elem.get_text().strip() if description_elem else ""
            
            # 提取编程语言
            language_elem = item.find('span', {'itemprop': 'programmingLanguage'})
            language = language_elem.get_text().strip() if language_elem else "未知"
            
            # 提取星标数
            stars_elem = item.find('a', href=re.compile(r'/stargazers'))
            stars = 0
            if stars_elem:
                stars_text = stars_elem.get_text().strip()
                stars = self._parse_number(stars_text)
            
            # 构建仓库信息
            repo_info = {
                'title': f"GitHub搜索结果: {owner}/{name}",
                'content': f"仓库: {owner}/{name}\n语言: {language}\n描述: {description}\n星标: {stars:,}",
                'url': f"https://github.com/{owner}/{name}",
                'published_at': datetime.now(),
                'source_name': f"GitHub搜索 {language}",
                'source_type': 'github',
                'owner': owner,
                'name': name,
                'full_name': f"{owner}/{name}",
                'description': description,
                'language': language,
                'stars': stars
            }
            
            return repo_info
            
        except Exception as e:
            logger.error(f"解析搜索结果项失败: {e}")
            return None


if __name__ == "__main__":
    # 测试代码
    fetcher = GitHubFetcher()
    
    print("开始测试GitHub Trending抓取器...")
    
    # 测试抓取Python热门仓库
    python_repos = fetcher.fetch_trending_repos(language="python", since="daily")
    print(f"测试抓取结果: {len(python_repos)} 个Python仓库")
    
    for repo in python_repos[:3]:
        print(f"仓库: {repo['full_name']}")
        print(f"语言: {repo['language']}")
        print(f"星标: {repo['stars']}")
        print("---")
    
    # 测试抓取AI/ML相关仓库
    ai_repos = fetcher.fetch_ai_ml_trending(limit=5)
    print(f"\nAI/ML相关仓库: {len(ai_repos)} 个")
    
    for repo in ai_repos[:3]:
        print(f"仓库: {repo['full_name']}")
        print(f"描述: {repo['description'][:100]}...")
        print("---")
