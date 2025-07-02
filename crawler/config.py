# 通用新闻爬虫配置

# 基础配置
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
CONNECTION_TEST_TIMEOUT = 5

# 爬虫配置
MAX_NEWS_COUNT = 20  # 最大爬取新闻数量
DELAY_RANGE = (1, 3)  # 请求间隔范围(秒)
SUMMARY_MAX_LENGTH = 200  # 摘要最大长度
MIN_TITLE_LENGTH = 10  # 最小标题长度
MIN_SUMMARY_LENGTH = 20  # 最小摘要长度

# 数据保存配置
DATA_DIR = "data"
SAVE_FORMATS = ['json', 'csv', 'excel']

# 日志配置
LOG_LEVEL = "INFO"
LOG_FILE = "data/spider.log"

# 请求头配置
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# 支持的新闻网站配置
NEWS_SITES = {
    "网易财经": {
        "url": "https://money.163.com/",
        "name": "网易财经",
        "encoding": "utf-8",
        "selectors": {
            "title": [
                "h1", "h2", "h3",
                ".news_title", ".post_title", 
                ".titleBar", ".cm_news_title",
                "a[href*='money.163.com']"
            ],
            "content": [
                ".post_content_main", ".post_body", 
                ".article_body", ".content", 
                ".news_content", ".endText", "p"
            ],
            "links": [
                "a[href*='money.163.com']",
                "a[href*='/finance/']",
                ".news_title a", ".titleBar a",
                ".cm_news_main a"
            ]
        }
    },
    "新浪财经": {
        "url": "https://finance.sina.com.cn/",
        "name": "新浪财经",
        "encoding": "utf-8",
        "selectors": {
            "title": [
                "h1", "h2", "h3",
                ".news-item-title", ".news-title",
                ".blk_A h3 a", ".news_txt h2 a"
            ],
            "content": [
                ".article-content", ".content",
                ".news_content", ".article p"
            ],
            "links": [
                "a[href*='finance.sina.com.cn']",
                ".news-item-title a", ".blk_A h3 a"
            ]
        }
    },
    "腾讯财经": {
        "url": "https://finance.qq.com/",
        "name": "腾讯财经",
        "encoding": "utf-8",
        "selectors": {
            "title": [
                "h1", "h2", "h3",
                ".title", ".news-title",
                ".item-title", ".article-title"
            ],
            "content": [
                ".content", ".article-content",
                ".news-content", ".text p"
            ],
            "links": [
                "a[href*='finance.qq.com']",
                ".title a", ".item-title a"
            ]
        }
    },
    "央视网财经": {
        "url": "http://finance.cctv.com/",
        "name": "央视网财经",
        "encoding": "utf-8",
        "selectors": {
            "title": [
                "h1", "h2", "h3",
                ".title", ".news_title",
                ".article_tit", ".tit"
            ],
            "content": [
                ".content", ".article_content",
                ".news_content", ".cnt_bd p"
            ],
            "links": [
                "a[href*='finance.cctv.com']",
                ".title a", ".tit a"
            ]
        }
    },
    "人民网财经": {
        "url": "http://finance.people.com.cn/",
        "name": "人民网财经",
        "encoding": "utf-8",
        "selectors": {
            "title": [
                "h1", "h2", "h3",
                ".title", ".news_title",
                ".p2j_title", ".fl a"
            ],
            "content": [
                ".content", ".article_content",
                ".news_content", ".show_text p"
            ],
            "links": [
                "a[href*='finance.people.com.cn']",
                ".title a", ".p2j_title a"
            ]
        }
    }
}
