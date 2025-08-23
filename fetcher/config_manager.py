"""
配置管理器
负责加载、验证和管理内容筛选配置
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class FilterConfigManager:
    """筛选配置管理器"""
    
    def __init__(self, config_path: str = "configs/filter_config.yaml"):
        self.config_path = config_path
        self.system_config = {}
        self.user_configs = {}
        self.active_config = {}
        self.config_version = "1.0.0"
        
        # 加载配置
        self._load_config()
        self._validate_config()
        self._merge_configs()
        
        logger.info("筛选配置管理器初始化成功")
    
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                    self.system_config = config_data.get('system', {})
                    self.user_configs = config_data.get('user_templates', {})
                    logger.info(f"成功加载配置文件: {self.config_path}")
            else:
                logger.warning(f"配置文件不存在: {self.config_path}，使用默认配置")
                self._load_default_config()
                
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}，使用默认配置")
            self._load_default_config()
    
    def _load_default_config(self):
        """加载默认配置"""
        self.system_config = {
            'filter_strictness': 'strict',
            'retention_rates': {
                'rss': 0.25,
                'arxiv': 0.20,
                'twitter': 0.15,
                'huggingface': 0.30,
                'github': 0.25,
                'web_scrape': 0.20
            },
            'fallback_rules': {
                'enable_rule_based': True,
                'min_importance_score': 0.7
            }
        }
        logger.info("已加载默认配置")
    
    def _validate_config(self):
        """验证配置有效性"""
        try:
            # 基础验证
            if not self.system_config:
                raise ValueError("系统配置为空")
            
            # 验证保留率
            retention_rates = self.system_config.get('retention_rates', {})
            for source, rate in retention_rates.items():
                if not isinstance(rate, (int, float)) or rate < 0 or rate > 1:
                    logger.warning(f"无效的保留率配置: {source}={rate}，使用默认值0.25")
                    retention_rates[source] = 0.25
            
            # 验证严格度
            strictness = self.system_config.get('filter_strictness', 'strict')
            if strictness not in ['strict', 'moderate', 'loose']:
                logger.warning(f"无效的严格度配置: {strictness}，使用默认值strict")
                self.system_config['filter_strictness'] = 'strict'
            
            logger.info("配置验证通过")
            
        except Exception as e:
            logger.error(f"配置验证失败: {e}")
            self._load_default_config()
    
    def _merge_configs(self):
        """合并系统配置和用户配置"""
        try:
            # 获取默认用户配置
            default_user = self.user_configs.get('default', {})
            
            # 合并配置
            self.active_config = {
                'system': self.system_config.copy(),
                'user': default_user.copy(),
                'merged': {}
            }
            
            # 应用用户配置覆盖
            if default_user.get('strictness'):
                self.active_config['merged']['filter_strictness'] = default_user['strictness']
            else:
                self.active_config['merged']['filter_strictness'] = self.system_config.get('filter_strictness', 'strict')
            
            # 应用保留率配置
            if default_user.get('retention_rates') == 'custom' and default_user.get('custom_retention_rates'):
                self.active_config['merged']['retention_rates'] = default_user['custom_retention_rates']
            else:
                self.active_config['merged']['retention_rates'] = self.system_config.get('retention_rates', {})
            
            # 应用其他配置
            self.active_config['merged']['fallback_rules'] = self.system_config.get('fallback_rules', {})
            self.active_config['merged']['performance'] = self.system_config.get('performance', {})
            
            logger.info("配置合并完成")
            
        except Exception as e:
            logger.error(f"配置合并失败: {e}")
            self.active_config = {'system': self.system_config, 'user': {}, 'merged': self.system_config}
    
    def get_config(self, section: str = 'merged') -> Dict[str, Any]:
        """获取指定配置段"""
        return self.active_config.get(section, {})
    
    def get_retention_rate(self, source_type: str) -> float:
        """获取指定信源类型的保留率"""
        retention_rates = self.active_config.get('merged', {}).get('retention_rates', {})
        return retention_rates.get(source_type, 0.25)
    
    def get_filter_strictness(self) -> str:
        """获取筛选严格度"""
        return self.active_config.get('merged', {}).get('filter_strictness', 'strict')
    
    def get_fallback_rules(self) -> Dict[str, Any]:
        """获取备用规则配置"""
        return self.active_config.get('merged', {}).get('fallback_rules', {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """获取性能配置"""
        return self.active_config.get('merged', {}).get('performance', {})
    
    def reload_config(self):
        """重新加载配置"""
        logger.info("重新加载配置...")
        self._load_config()
        self._validate_config()
        self._merge_configs()
        logger.info("配置重新加载完成")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """获取配置摘要"""
        return {
            'config_version': self.config_version,
            'filter_strictness': self.get_filter_strictness(),
            'retention_rates': self.active_config.get('merged', {}).get('retention_rates', {}),
            'fallback_rules_enabled': self.get_fallback_rules().get('enable_rule_based', True),
            'config_source': self.config_path
        }


# 全局配置管理器实例
config_manager = FilterConfigManager()
