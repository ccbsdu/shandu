import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from serpapi import GoogleSearch
import os

def search_google(query: str, num_results: int = 5) -> list:
    """使用 Google 搜索并返回结果"""
    try:
        api_key = os.getenv("SERPAPI_KEY", "your_serpapi_key")  # 需要设置环境变量
        params = {
            "q": query,
            "num": num_results,
            "api_key": api_key,
            "engine": "google"
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        formatted_results = []
        for result in results.get("organic_results", [])[:num_results]:
            title = result.get("title", "")
            link = result.get("link", "")
            snippet = result.get("snippet", "")
            formatted_results.append(f"标题：{title}\n链接：{link}\n内容：{snippet}\n")
            
        return formatted_results
        
    except Exception as e:
        print(f"Google搜索错误: {str(e)}")
        return []

def search_web(query: str, num_results: int = 5) -> list:
    """执行网络搜索并返回结果"""
    # 优先使用 Google 搜索
    google_results = search_google(query, num_results)
    if google_results:
        return google_results
        
    # 如果 Google 搜索失败，使用备用搜索
    try:
        # 原有的 DuckDuckGo 搜索代码保持不变
        encoded_query = quote(query)
        url = f"https://lite.duckduckgo.com/lite?q={encoded_query}"
        
        response = requests.get(
            url,
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=10
        )
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # 提取搜索结果
            for item in soup.select('.result-link')[:num_results]:
                title = item.get_text(strip=True)
                link = item.get('href', '')
                
                try:
                    # 获取页面内容摘要
                    page_response = requests.get(
                        link,
                        headers={'User-Agent': 'Mozilla/5.0'},
                        timeout=5
                    )
                    if page_response.status_code == 200:
                        page_soup = BeautifulSoup(page_response.text, 'html.parser')
                        content = page_soup.get_text()[:500]  # 获取前500个字符
                        results.append(f"标题：{title}\n链接：{link}\n内容：{content}\n")
                except:
                    continue
            
            return results
        
        return []
        
    except Exception as e:
        print(f"搜索错误: {str(e)}")
        return []