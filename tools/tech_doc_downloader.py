#!/usr/bin/env python3
"""
技术资料下载助手 - 公开资源版
用于下载公开可访问的PDF/文档
"""

import requests
import os
from urllib.parse import urlparse
from pathlib import Path

class TechDocDownloader:
    def __init__(self, save_dir="downloads"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        
        # 模拟浏览器请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def download_pdf(self, url, filename=None):
        """下载公开PDF"""
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            if not filename:
                filename = urlparse(url).path.split('/')[-1]
            
            save_path = self.save_dir / filename
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ 下载成功: {save_path}")
            return save_path
            
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            return None
    
    def download_with_retry(self, url, filename=None, max_retry=3):
        """带重试的下载"""
        for i in range(max_retry):
            result = self.download_pdf(url, filename)
            if result:
                return result
            print(f"重试 {i+1}/{max_retry}...")
        return None

# 使用示例
if __name__ == "__main__":
    downloader = TechDocDownloader(save_dir="tech_docs")
    
    # 示例：下载公开PDF（需要真实的公开直链）
    # url = "https://example.com/public_doc.pdf"
    # downloader.download_pdf(url, "制动系统资料.pdf")
