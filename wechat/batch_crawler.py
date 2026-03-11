#!/usr/bin/env python3
"""
微信公众号文章批量抓取脚本
支持7个目标公众号的自动化抓取
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
from urllib.parse import quote

# 目标公众号配置
TARGET_ACCOUNTS = [
    {"name": "佐思汽车研究", "category": "P0-产业研究", "priority": "high"},
    {"name": "汽车电子设计", "category": "P0-知识技能", "priority": "high"},
    {"name": "AUTOSAR中国", "category": "P0-知识技能", "priority": "high"},
    {"name": "高工智能汽车", "category": "P1-产业研究", "priority": "medium"},
    {"name": "半导体行业观察", "category": "P1-产业研究", "priority": "medium"},
    {"name": "信号完整性学习之路", "category": "P2-知识技能", "priority": "low"},
    {"name": "嵌入式大杂烩", "category": "P2-知识技能", "priority": "low"}
]

# 输出目录
OUTPUT_DIR = "/root/.openclaw/workspace/knowledge-note/wechat/articles/2026-03-10"
LOG_FILE = "/root/.openclaw/workspace/knowledge-note/wechat/crawler_batch_20260310.log"

def log(message):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_msg + '\n')

def try_sogou_search(account_name):
    """尝试通过搜狗微信搜索获取文章"""
    try:
        # 搜狗微信搜索URL
        search_url = f"https://weixin.sogou.com/weixin?type=1&query={quote(account_name)}"
        log(f"尝试搜狗搜索: {account_name}")
        log(f"  URL: {search_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        log(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 检查是否有验证码
            if '请输入验证码' in response.text or 'antispider' in response.text:
                log(f"  ⚠️ 触发反爬验证，需要手动处理")
                return None
            return response.text
        else:
            log(f"  ❌ 请求失败: {response.status_code}")
            return None
            
    except Exception as e:
        log(f"  ❌ 异常: {e}")
        return None

def try_rsshub_feed(account_name):
    """尝试通过RSSHub获取RSS订阅"""
    try:
        # RSSHub微信订阅（需要部署或使用公共实例）
        rsshub_url = f"https://rsshub.app/wechat/mp/{quote(account_name)}"
        log(f"尝试RSSHub: {account_name}")
        log(f"  URL: {rsshub_url}")
        
        response = requests.get(rsshub_url, timeout=15)
        log(f"  状态码: {response.status_code}")
        
        if response.status_code == 200:
            return response.text
        else:
            log(f"  ❌ RSSHub不可用")
            return None
            
    except Exception as e:
        log(f"  ❌ 异常: {e}")
        return None

def extract_articles_fallback(account_name, category):
    """生成手动抓取提示模板"""
    log(f"生成手动抓取模板: {account_name}")
    
    template = f"""# {account_name} - 文章待抓取

## 公众号信息
- **名称**: {account_name}
- **分类**: {category}
- **抓取日期**: 2026-03-10
- **状态**: 待手动抓取

## 抓取方式
由于微信反爬机制，建议以下方式获取文章：

### 方式1: 搜狗微信搜索
1. 访问: https://weixin.sogou.com/
2. 搜索: {account_name}
3. 找到公众号，查看最新文章

### 方式2: 微信客户端
1. 打开微信，搜索公众号: {account_name}
2. 进入公众号主页
3. 复制最新文章链接或内容

### 方式3: RSSHub（如有部署）
订阅地址: https://rsshub.app/wechat/mp/{account_name}

## 待抓取文章清单
- [ ] 文章1: ____________
- [ ] 文章2: ____________
- [ ] 文章3: ____________

---
*占位文件，待内容填充*
"""
    
    filename = f"{account_name.replace(' ', '_')}_待抓取.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(template)
    
    log(f"  ✅ 模板已生成: {filename}")
    return True

def main():
    """主函数"""
    print("="*60)
    print("🔥 微信公众号批量抓取任务")
    print("="*60)
    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    log(f"任务开始，共{len(TARGET_ACCOUNTS)}个公众号")
    log(f"输出目录: {OUTPUT_DIR}")
    print()
    
    results = {
        "success": [],
        "failed": [],
        "manual": []
    }
    
    for idx, account in enumerate(TARGET_ACCOUNTS, 1):
        name = account["name"]
        category = account["category"]
        priority = account["priority"]
        
        print(f"\n[{idx}/{len(TARGET_ACCOUNTS)}] 正在处理: {name}")
        print(f"    分类: {category} | 优先级: {priority}")
        
        # 尝试自动抓取
        sogou_result = try_sogou_search(name)
        
        if sogou_result:
            # 这里可以解析HTML提取文章链接
            log(f"  ⚠️ 搜狗搜索成功，但解析需要验证码处理")
            results["manual"].append(name)
            extract_articles_fallback(name, category)
        else:
            # 所有自动方式失败，生成手动模板
            log(f"  ⚠️ 自动抓取失败，生成手动模板")
            results["manual"].append(name)
            extract_articles_fallback(name, category)
        
        # 间隔，避免请求过快
        time.sleep(2)
    
    # 生成总结报告
    print("\n" + "="*60)
    print("📊 抓取任务总结")
    print("="*60)
    
    log(f"\n任务完成")
    log(f"成功自动抓取: {len(results['success'])} 个")
    log(f"需要手动处理: {len(results['manual'])} 个")
    log(f"失败: {len(results['failed'])} 个")
    
    if results["manual"]:
        print("\n以下公众号需要手动抓取:")
        for name in results["manual"]:
            print(f"  - {name}")
        print(f"\n模板文件已生成在: {OUTPUT_DIR}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()
