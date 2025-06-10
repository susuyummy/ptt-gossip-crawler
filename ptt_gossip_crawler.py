#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import time
import random
import sqlite3
from datetime import datetime
import re
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
import openpyxl

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ptt_crawler.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class Article:
    """文章資料類別"""
    title: str
    author: str
    date: str
    url: str
    content: str

class PTTGossipCrawler:
    """PTT 八卦板爬蟲類別"""
    
    def __init__(self):
        """初始化爬蟲設定"""
        self.base_url = "https://www.ptt.cc"
        self.gossip_url = f"{self.base_url}/bbs/Gossiping/index.html"
        
        # 設定請求標頭
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        # 建立 Session 並設定 cookie
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.session.cookies.set('over18', '1', domain='.ptt.cc')
        
        # 建立資料庫連線
        self.db_path = Path('ptt_gossip.db')
        self._init_database()

    def _init_database(self) -> None:
        """初始化 SQLite 資料庫"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 刪除舊的資料表（如果存在）
            cursor.execute('DROP TABLE IF EXISTS articles')
            
            # 建立新的資料表
            cursor.execute('''
            CREATE TABLE articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                author TEXT,
                date TEXT,
                url TEXT UNIQUE,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            conn.commit()
            conn.close()
            logging.info("資料庫初始化成功")
        except sqlite3.Error as e:
            logging.error(f"資料庫初始化失敗: {e}")
            raise

    def get_page(self, url: str) -> Optional[str]:
        """取得頁面內容，加入隨機延遲避免被封鎖"""
        try:
            time.sleep(random.uniform(0.5, 1))  # 隨機延遲 0.5-1 秒
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logging.error(f"取得頁面失敗 {url}: {e}")
            return None

    def parse_article_list(self, html: str) -> List[Article]:
        """解析文章列表頁面"""
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        
        # 使用指定的 selector 取得文章列表
        for article in soup.select('div.r-ent'):
            try:
                # 取得文章標題和連結
                title_element = article.select_one('div.title a')
                if not title_element:
                    continue
                
                title = title_element.text.strip()
                url = self.base_url + title_element['href']
                
                # 取得作者和日期
                author = article.select_one('div.author').text.strip()
                date = article.select_one('div.date').text.strip()
                
                # 取得文章內容
                content = self.get_article_content(url)
                
                # 只保留有內容的文章
                if content:
                    articles.append(Article(
                        title=title,
                        author=author,
                        date=date,
                        url=url,
                        content=content
                    ))
                
            except Exception as e:
                logging.error(f"解析文章失敗: {e}")
                continue
                
        return articles

    def get_article_content(self, url: str) -> str:
        """取得文章內容並清理"""
        html = self.get_page(url)
        if not html:
            return ""
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # 找到文章主體
        main_content = soup.select_one('#main-content')
        if not main_content:
            return ""
            
        # 移除不需要的元素
        for element in main_content.select('div.push, div.article-metaline, div.article-metaline-right, span.f2'):
            element.decompose()
            
        # 取得純文字內容
        content = main_content.text.strip()
        
        # 清理內容
        # 移除發文時間行
        content = re.sub(r'時間.*\n', '', content)
        # 移除編輯記錄
        content = re.sub(r'※ 編輯:.*\n', '', content)
        # 移除多餘的空白行
        content = re.sub(r'\n\s*\n', '\n\n', content)
        # 移除文章開頭的標題和作者資訊
        content = re.sub(r'^.*\n', '', content, count=3)
        # 移除文章結尾的簽名檔
        content = re.sub(r'--\n.*$', '', content, flags=re.DOTALL)
        
        return content.strip()

    def save_to_database(self, articles: List[Article]) -> None:
        """將文章儲存到資料庫"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for article in articles:
                cursor.execute('''
                INSERT OR REPLACE INTO articles (title, author, date, url, content)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    article.title,
                    article.author,
                    article.date,
                    article.url,
                    article.content
                ))
                
            conn.commit()
            conn.close()
            logging.info(f"成功儲存 {len(articles)} 篇文章到資料庫")
        except sqlite3.Error as e:
            logging.error(f"儲存到資料庫失敗: {e}")
            raise

    def crawl(self, pages: int = 1) -> List[Article]:
        """爬取指定頁數的文章"""
        all_articles = []
        current_url = self.gossip_url
        
        for page in range(pages):
            logging.info(f"正在爬取第 {page + 1} 頁")
            html = self.get_page(current_url)
            if not html:
                break
                
            articles = self.parse_article_list(html)
            all_articles.extend(articles)
            
            # 取得上一頁的連結
            soup = BeautifulSoup(html, 'html.parser')
            prev_link = soup.select_one('a.btn.wide:contains("上頁")')
            if not prev_link:
                break
            current_url = self.base_url + prev_link['href']
            
        # 儲存到資料庫
        self.save_to_database(all_articles)
        
        return all_articles

    def save_to_excel(self, articles, filename='ptt_gossip.xlsx'):
        """將文章資訊和內容分別寫入 Excel 檔案的不同工作表"""
        wb = openpyxl.Workbook()
        # 文章資訊 sheet
        ws_info = wb.active
        ws_info.title = '文章資訊'
        ws_info.append(['標題', '作者', '日期', '連結'])
        for article in articles:
            ws_info.append([
                article.title,
                article.author,
                article.date,
                article.url
            ])
        # 文章內容 sheet
        ws_content = wb.create_sheet('文章內容')
        ws_content.append(['標題', '內容'])
        for article in articles:
            ws_content.append([
                article.title,
                article.content
            ])
        wb.save(filename)
        print(f"已將資料寫入 {filename}")

def main():
    """主程式"""
    try:
        # 建立爬蟲實例
        crawler = PTTGossipCrawler()
        
        # 爬取 3 頁文章
        articles = crawler.crawl(pages=3)
        
        # 寫入 Excel
        crawler.save_to_excel(articles)
        
        # 印出結果
        print(f"\n總共爬取到 {len(articles)} 篇文章")
        for article in articles:
            print("\n" + "="*50)
            print(f"標題: {article.title}")
            print(f"作者: {article.author}")
            print(f"日期: {article.date}")
            print(f"連結: {article.url}")
            print(f"內容預覽: {article.content[:100]}...")
            
    except Exception as e:
        logging.error(f"程式執行失敗: {e}")
        raise

if __name__ == "__main__":
    main() 