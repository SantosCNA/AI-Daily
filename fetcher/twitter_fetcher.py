"""
Twitter数据抓取器
负责抓取Twitter上的AI相关内容和讨论
"""

import tweepy
import os
from typing import List, Dict, Optional
import logging
from datetime import datetime
from dotenv import load_dotenv
import time
import random

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwitterFetcher:
    """Twitter数据抓取器"""
    
    def __init__(self):
        """初始化Twitter抓取器"""
        # 加载Twitter API配置
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        # 检查配置完整性
        if not all([self.bearer_token, self.api_key, self.api_secret, 
                   self.access_token, self.access_token_secret]):
            logger.warning("Twitter API配置不完整，某些功能可能无法使用")
            self.client = None
            self.api = None
        else:
            try:
                # 初始化Twitter API v2客户端
                self.client = tweepy.Client(
                    bearer_token=self.bearer_token,
                    consumer_key=self.api_key,
                    consumer_secret=self.api_secret,
                    access_token=self.access_token,
                    access_token_secret=self.access_token_secret,
                    wait_on_rate_limit=True
                )
                
                # 初始化Twitter API v1.1（用于某些高级功能）
                auth = tweepy.OAuthHandler(self.api_key, self.api_secret)
                auth.set_access_token(self.access_token, self.access_token_secret)
                self.api = tweepy.API(auth, wait_on_rate_limit=True)
                
                logger.info("Twitter API客户端初始化成功")
                
            except Exception as e:
                logger.error(f"Twitter API客户端初始化失败: {e}")
                self.client = None
                self.api = None
    
    def is_available(self) -> bool:
        """检查Twitter API是否可用"""
        return self.client is not None and self.api is not None
    
    def fetch_user_tweets(self, username: str, count: int = 20) -> List[Dict]:
        """
        获取指定用户的推文
        
        Args:
            username: Twitter用户名（不含@）
            count: 获取推文数量
            
        Returns:
            推文列表
        """
        if not self.is_available():
            logger.error("Twitter API不可用")
            return []
        
        try:
            logger.info(f"开始获取用户 @{username} 的推文")
            
            # 获取用户ID
            user = self.client.get_user(username=username)
            if not user.data:
                logger.error(f"未找到用户: {username}")
                return []
            
            user_id = user.data.id
            
            # 获取用户推文
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=count,
                tweet_fields=['created_at', 'public_metrics', 'context_annotations']
            )
            
            if not tweets.data:
                logger.info(f"用户 @{username} 没有推文")
                return []
            
            # 处理推文数据
            processed_tweets = []
            for tweet in tweets.data:
                try:
                    processed_tweet = self._process_tweet(tweet, username)
                    if processed_tweet:
                        processed_tweets.append(processed_tweet)
                except Exception as e:
                    logger.error(f"处理推文失败: {e}")
                    continue
            
            logger.info(f"成功获取 @{username} 的 {len(processed_tweets)} 条推文")
            return processed_tweets
            
        except Exception as e:
            logger.error(f"获取用户推文失败 @{username}: {e}")
            return []
    
    def fetch_ai_influencers_tweets(self, usernames: List[str] = None) -> List[Dict]:
        """
        获取AI影响者的推文
        
        Args:
            usernames: 用户名列表，如果为None则使用默认列表
            
        Returns:
            推文列表
        """
        if not usernames:
            # 默认的AI影响者列表
            usernames = [
                'karpathy',      # Andrej Karpathy
                'ylecun',        # Yann LeCun
                'AndrewYNg',     # Andrew Ng
                'sama',          # Sam Altman
                'gdb',           # Geoffrey Hinton
                'jasonwei',      # Jason Wei
                'JimFan',        # Jim Fan
                '_akhaliq',      # Aran Komatsuzaki
                'rowancheung',   # Rowan Cheung
                'alexandra_amos', # Alexandra Amos
                'mckaywrigley',  # McKay Wrigley
                'lennysan'       # Lenny Rachitsky
            ]
        
        all_tweets = []
        
        for username in usernames[:8]:  # 限制用户数量避免请求过多
            try:
                logger.info(f"获取AI影响者 @{username} 的推文")
                
                tweets = self.fetch_user_tweets(username, count=10)
                all_tweets.extend(tweets)
                
                # 添加延迟避免请求过快
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.error(f"获取用户 @{username} 推文失败: {e}")
                continue
        
        logger.info(f"总共获取到 {len(all_tweets)} 条AI影响者推文")
        return all_tweets
    
    def fetch_trending_ai_topics(self, count: int = 20) -> List[Dict]:
        """
        获取AI相关热门话题
        
        Args:
            count: 获取话题数量
            
        Returns:
            热门话题列表
        """
        if not self.is_available():
            logger.error("Twitter API不可用")
            return []
        
        try:
            logger.info("开始获取AI相关热门话题")
            
            # 搜索AI相关推文
            query = "(AI OR artificial intelligence OR machine learning OR deep learning OR GPT OR LLM) -is:retweet lang:en"
            
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=count,
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                user_fields=['username', 'name'],
                expansions=['author_id']
            )
            
            if not tweets.data:
                logger.info("未找到AI相关热门话题")
                return []
            
            # 处理推文数据
            processed_tweets = []
            for tweet in tweets.data:
                try:
                    # 获取作者信息
                    author = None
                    if tweets.includes and 'users' in tweets.includes:
                        for user in tweets.includes['users']:
                            if user.id == tweet.author_id:
                                author = user
                                break
                    
                    processed_tweet = self._process_tweet(tweet, author.username if author else 'unknown')
                    if processed_tweet:
                        processed_tweets.append(processed_tweet)
                        
                except Exception as e:
                    logger.error(f"处理热门话题推文失败: {e}")
                    continue
            
            logger.info(f"成功获取 {len(processed_tweets)} 条AI相关热门话题")
            return processed_tweets
            
        except Exception as e:
            logger.error(f"获取AI热门话题失败: {e}")
            return []
    
    def fetch_list_tweets(self, list_id: str, count: int = 20) -> List[Dict]:
        """
        获取Twitter List中的推文
        
        Args:
            list_id: List ID
            count: 获取推文数量
            
        Returns:
            推文列表
        """
        if not self.is_available():
            logger.error("Twitter API不可用")
            return []
        
        try:
            logger.info(f"开始获取List {list_id} 中的推文")
            
            # 获取List中的推文
            tweets = self.client.get_list_tweets(
                id=list_id,
                max_results=count,
                tweet_fields=['created_at', 'public_metrics', 'author_id'],
                user_fields=['username', 'name'],
                expansions=['author_id']
            )
            
            if not tweets.data:
                logger.info(f"List {list_id} 中没有推文")
                return []
            
            # 处理推文数据
            processed_tweets = []
            for tweet in tweets.data:
                try:
                    # 获取作者信息
                    author = None
                    if tweets.includes and 'users' in tweets.includes:
                        for user in tweets.includes['users']:
                            if user.id == tweet.author_id:
                                author = user
                                break
                    
                    processed_tweet = self._process_tweet(tweet, author.username if author else 'unknown')
                    if processed_tweet:
                        processed_tweets.append(processed_tweet)
                        
                except Exception as e:
                    logger.error(f"处理List推文失败: {e}")
                    continue
            
            logger.info(f"成功获取List {list_id} 中的 {len(processed_tweets)} 条推文")
            return processed_tweets
            
        except Exception as e:
            logger.error(f"获取List推文失败 {list_id}: {e}")
            return []
    
    def _process_tweet(self, tweet, username: str) -> Optional[Dict]:
        """处理单条推文数据"""
        try:
            # 提取推文内容
            text = tweet.text
            
            # 过滤掉转发和回复
            if text.startswith('RT ') or text.startswith('@'):
                return None
            
            # 构建内容摘要
            content_summary = f"""
推文内容: {text}
作者: @{username}
发布时间: {tweet.created_at}
互动数据: 点赞 {tweet.public_metrics.get('like_count', 0)}, 转发 {tweet.public_metrics.get('retweet_count', 0)}, 回复 {tweet.public_metrics.get('reply_count', 0)}
            """.strip()
            
            # 构建推文信息
            tweet_info = {
                'title': f"Twitter: @{username} 的推文",
                'content': content_summary,
                'url': f"https://twitter.com/{username}/status/{tweet.id}",
                'published_at': tweet.created_at,
                'source_name': f"Twitter @{username}",
                'source_type': 'twitter',
                'tweet_id': tweet.id,
                'author': username,
                'text': text,
                'metrics': tweet.public_metrics,
                'created_at': tweet.created_at
            }
            
            return tweet_info
            
        except Exception as e:
            logger.error(f"处理推文数据失败: {e}")
            return None
    
    def test_connection(self) -> bool:
        """测试Twitter API连接"""
        if not self.client:
            logger.error("Twitter API客户端未初始化")
            return False
        
        try:
            # 尝试获取用户信息来测试连接
            user = self.client.get_user(username="twitter")
            if user.data:
                logger.info("Twitter API连接测试成功")
                return True
            else:
                logger.error("Twitter API连接测试失败: 无法获取用户数据")
                return False
        except Exception as e:
            logger.error(f"Twitter API连接测试失败: {e}")
            logger.error(f"请检查以下配置:")
            logger.error(f"  - TWITTER_BEARER_TOKEN: {'已设置' if self.bearer_token else '未设置'}")
            logger.error(f"  - TWITTER_API_KEY: {'已设置' if self.api_key else '未设置'}")
            logger.error(f"  - TWITTER_API_SECRET: {'已设置' if self.api_secret else '未设置'}")
            logger.error(f"  - TWITTER_ACCESS_TOKEN: {'已设置' if self.access_token else '未设置'}")
            logger.error(f"  - TWITTER_ACCESS_TOKEN_SECRET: {'已设置' if self.access_token_secret else '未设置'}")
            return False


if __name__ == "__main__":
    # 测试代码
    fetcher = TwitterFetcher()
    
    if fetcher.is_available():
        print("✅ Twitter API配置正常")
        
        # 测试连接
        if fetcher.test_connection():
            print("✅ Twitter API连接成功")
            
            # 测试获取推文
            tweets = fetcher.fetch_user_tweets('OpenAI', count=2)
            print(f"测试获取推文: {len(tweets)} 条")
            
            for tweet in tweets[:2]:
                print(f"作者: {tweet['author']}")
                print(f"内容: {tweet['text'][:100]}...")
                print("---")
        else:
            print("❌ Twitter API连接失败")
    else:
        print("❌ Twitter API不可用，请检查环境变量配置")
