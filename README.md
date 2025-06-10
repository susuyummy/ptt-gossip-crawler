# PTT Gossiping Board Crawler

一個用於爬取 PTT 八卦板文章的 Python 爬蟲程式。這個程式可以自動處理 over18 驗證，並將爬取的文章內容整理成結構化的資料。

## 功能特點

- 🔐 自動處理 over18 驗證
- 📄 支援自定義爬取頁數
- 🌐 使用真實瀏覽器 User-Agent
- 🧹 清理文章內容，移除推文和簽名檔
- 💾 將結果儲存為 Excel 檔案和 SQLite 資料庫
- 📝 完整的錯誤處理和日誌記錄

## 系統需求

- Python 3.6 或更高版本
- 以下 Python 套件：
  - requests
  - beautifulsoup4
  - openpyxl

## 安裝步驟

1. 克隆專案：
```bash
git clone https://github.com/susuyummy/ptt-gossip-crawler.git
cd ptt-gossip-crawler
```

2. 安裝所需套件：
```bash
pip install -r requirements.txt
```

## 使用方法

1. 執行程式：
```bash
python ptt_gossip_crawler.py
```

2. 程式會自動：
   - 爬取指定頁數的文章
   - 清理文章內容
   - 將結果儲存到 Excel 和資料庫

## 輸出格式

程式會生成以下檔案：

### Excel 檔案 (ptt_gossip.xlsx)
- 文章列表工作表：
  - 標題
  - 作者
  - 日期
  - 連結
- 文章內容工作表：
  - 完整文章內容

### SQLite 資料庫 (ptt_gossip.db)
- articles 表格：
  - id (主鍵)
  - title (標題)
  - author (作者)
  - date (日期)
  - url (連結)
  - content (內容)
  - created_at (建立時間)

### 日誌檔案 (ptt_crawler.log)
- 記錄程式執行過程
- 包含錯誤和警告訊息

## 程式碼結構

```python
class PTTGossipCrawler:
    def __init__(self):
        # 初始化爬蟲設定
        pass

    def get_page(self, url):
        # 獲取頁面內容
        pass

    def parse_article_list(self, html):
        # 解析文章列表
        pass

    def get_article_content(self, url):
        # 獲取文章內容
        pass

    def crawl(self, pages=3):
        # 執行爬蟲
        pass

    def save_to_database(self, articles):
        # 儲存到資料庫
        pass
```

## 注意事項

- 請遵守 PTT 的使用規範
- 建議在爬取時加入適當的延遲，避免對伺服器造成負擔
- 爬取的內容僅供個人研究使用
- 請勿用於商業用途

## 常見問題

1. Q: 為什麼需要 over18 驗證？
   A: PTT 八卦板需要確認使用者已滿 18 歲才能訪問。

2. Q: 如何修改爬取頁數？
   A: 在 `main()` 函數中修改 `pages` 參數。

3. Q: 如何處理爬取失敗的情況？
   A: 程式會自動記錄錯誤到日誌檔案，並繼續爬取下一篇文章。

## 貢獻指南

歡迎提交 Pull Request 或開 Issue 來改進這個專案！

1. Fork 這個專案
2. 創建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟一個 Pull Request

## 授權

MIT License

## 作者

susuyummy

## 致謝

- PTT 提供平台
- Python 社群提供的優秀套件
- 所有貢獻者的支持 
