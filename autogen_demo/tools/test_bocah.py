#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试从bocah API提取数据的功能
"""

import sys
import os
import json
from pprint import pprint

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.utils import extract_bocah_data

def main():
    """测试从bocah API提取数据的功能"""
    # 模拟bocah API返回的数据
    sample_response = {
        "code": 200,
        "log_id": "5a16f8c6b7bd30c5",
        "msg": None,
        "data": {
            "_type": "SearchResponse",
            "queryContext": {
                "originalQuery": "新能源汽车发展报告"
            },
            "webPages": {
                "webSearchUrl": "https://bochaai.com/search?q=新能源汽车发展报告",
                "totalEstimatedMatches": 10000000,
                "value": [
                    {
                        "id": "https://api.bochaai.com/v1/#WebPages.0",
                        "name": "新能源汽车行业发展状况分析报告.pdf_淘豆网",
                        "url": "https://www.taodocs.com/p-1105683895.html",
                        "snippet": "下载提示 1.该资料是网友上传的,本站提供全文预览,预览什么样,下载就什么样。"
                    },
                    {
                        "id": "https://api.bochaai.com/v1/#WebPages.1",
                        "name": "新能源汽车研究报告.doc_淘豆网",
                        "url": "https://www.taodocs.com/p-69849917.html",
                        "snippet": "文档列表 文档介绍 新能源汽车研究报告篇一: 2016 年新能源汽车项目分析报告"
                    }
                ]
            },
            "images": {
                "value": [
                    {
                        "thumbnailUrl": "https://img.book118.com/sr2/M01/2E/3F/wKh2E2aTocGAWl2ZAAD_JMhLy90647.jpg",
                        "contentUrl": "https://img.book118.com/sr2/M01/2E/3F/wKh2E2aTocGAWl2ZAAD_JMhLy90647.jpg",
                        "hostPageUrl": "https://max.book118.com/html/2024/0714/8134054071006111.shtm"
                    },
                    {
                        "thumbnailUrl": "https://view-cache.book118.com/view11/M01/22/3B/wKh2DmE5pkeAW0e0AAAl2iEep-8188.png",
                        "contentUrl": "https://view-cache.book118.com/view11/M01/22/3B/wKh2DmE5pkeAW0e0AAAl2iEep-8188.png",
                        "hostPageUrl": "https://max.book118.com/html/2021/0909/5120111014004002.shtm"
                    }
                ]
            }
        }
    }

    # 提取数据
    news_data, image_data = extract_bocah_data(sample_response)
    
    print("提取的新闻数据:")
    print(f"共 {len(news_data)} 条新闻")
    for i, news in enumerate(news_data, 1):
        print(f"\n新闻 {i}:")
        print(f"标题: {news.get('name')}")
        print(f"URL: {news.get('url')}")
        print(f"摘要: {news.get('snippet')[:50]}...")
    
    print("\n提取的图片数据:")
    print(f"共 {len(image_data)} 张图片")
    for i, image in enumerate(image_data, 1):
        print(f"\n图片 {i}:")
        print(f"缩略图URL: {image.get('thumbnailUrl')}")
        print(f"原图URL: {image.get('contentUrl')}")
        print(f"来源页面: {image.get('hostPageUrl')}")

if __name__ == "__main__":
    main() 