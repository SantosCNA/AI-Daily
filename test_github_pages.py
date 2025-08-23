#!/usr/bin/env python3
"""
测试GitHub Pages部署功能
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_github_config():
    """测试GitHub配置"""
    print("🔧 测试GitHub Pages配置...")
    
    # 检查环境变量
    gh_token = os.getenv('GH_TOKEN')
    github_repo = os.getenv('GITHUB_REPO')
    
    if gh_token:
        print(f"  ✅ GH_TOKEN: {'已设置' if gh_token != 'your_github_personal_access_token_here' else '需要配置'}")
    else:
        print("  ❌ GH_TOKEN: 未设置")
    
    if github_repo:
        print(f"  ✅ GITHUB_REPO: {github_repo}")
    else:
        print("  ❌ GITHUB_REPO: 未设置")
    
    return bool(gh_token and github_repo and gh_token != 'your_github_personal_access_token_here')

def test_github_api():
    """测试GitHub API连接"""
    print("\n🌐 测试GitHub API连接...")
    
    try:
        import requests
        
        gh_token = os.getenv('GH_TOKEN')
        github_repo = os.getenv('GITHUB_REPO', 'your-username/ai-daily')
        
        if not gh_token or gh_token == 'your_github_personal_access_token_here':
            print("  ⚠️  跳过API测试：未配置有效的GH_TOKEN")
            return False
        
        # 测试GitHub API连接
        url = f"https://api.github.com/repos/{github_repo}"
        headers = {
            "Authorization": f"token {gh_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            repo_info = response.json()
            print(f"  ✅ GitHub API连接成功")
            print(f"     - 仓库: {repo_info['full_name']}")
            print(f"     - 描述: {repo_info.get('description', '无描述')}")
            print(f"     - 可见性: {repo_info['visibility']}")
            return True
        else:
            print(f"  ❌ GitHub API连接失败: {response.status_code}")
            print(f"     - 错误信息: {response.text}")
            return False
            
    except ImportError:
        print("  ❌ 缺少requests库，请运行: pip install requests")
        return False
    except Exception as e:
        print(f"  ❌ API测试异常: {e}")
        return False

def test_workflow_files():
    """测试工作流文件"""
    print("\n📁 测试GitHub Actions工作流文件...")
    
    workflow_file = ".github/workflows/deploy.yml"
    if os.path.exists(workflow_file):
        print(f"  ✅ 工作流文件存在: {workflow_file}")
        
        # 检查文件内容
        with open(workflow_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if "deploy-daily" in content:
            print("  ✅ 工作流包含正确的触发类型")
        else:
            print("  ❌ 工作流缺少deploy-daily触发类型")
            
        if "repository_dispatch" in content:
            print("  ✅ 工作流支持API触发")
        else:
            print("  ❌ 工作流不支持API触发")
            
        return True
    else:
        print(f"  ❌ 工作流文件不存在: {workflow_file}")
        return False

def test_jekyll_config():
    """测试Jekyll配置"""
    print("\n🔧 测试Jekyll配置...")
    
    config_file = "digest/_config.yml"
    if os.path.exists(config_file):
        print(f"  ✅ Jekyll配置文件存在: {config_file}")
        
        # 检查Gemfile
        if os.path.exists("Gemfile"):
            print("  ✅ Gemfile存在")
        else:
            print("  ❌ Gemfile不存在")
            
        return True
    else:
        print(f"  ❌ Jekyll配置文件不存在: {config_file}")
        return False

def test_digest_files():
    """测试日报文件"""
    print("\n📰 测试日报文件...")
    
    digest_dir = "digest"
    if os.path.exists(digest_dir):
        print(f"  ✅ 日报目录存在: {digest_dir}")
        
        # 检查README
        readme_file = os.path.join(digest_dir, "README.md")
        if os.path.exists(readme_file):
            print("  ✅ 日报索引文件存在")
        else:
            print("  ❌ 日报索引文件不存在")
            
        # 检查示例日报
        example_file = os.path.join(digest_dir, "2025-08-23.md")
        if os.path.exists(example_file):
            print("  ✅ 示例日报文件存在")
        else:
            print("  ❌ 示例日报文件不存在")
            
        return True
    else:
        print(f"  ❌ 日报目录不存在: {digest_dir}")
        return False

def main():
    """主测试函数"""
    print("🧪 GitHub Pages部署功能测试")
    print("=" * 60)
    
    # 运行所有测试
    tests = [
        test_github_config,
        test_github_api,
        test_workflow_files,
        test_jekyll_config,
        test_digest_files
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ❌ 测试异常: {e}")
    
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print(f"  通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！GitHub Pages功能配置完成。")
        print("\n📋 下一步操作:")
        print("1. 创建GitHub仓库")
        print("2. 配置Personal Access Token")
        print("3. 推送代码到GitHub")
        print("4. 启用GitHub Pages")
        print("5. 测试自动部署")
    else:
        print(f"⚠️  有 {total - passed} 项测试失败，请检查配置。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
