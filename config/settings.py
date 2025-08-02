"""
Configuration settings cho Lich Crawler
"""

import os
from pathlib import Path

# Đường dẫn cơ bản
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Tạo thư mục nếu chưa có
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
(DATA_DIR / "daily").mkdir(exist_ok=True)
(DATA_DIR / "monthly").mkdir(exist_ok=True)
(DATA_DIR / "yearly").mkdir(exist_ok=True)

# Crawler settings
CRAWLER_SETTINGS = {
    'delay': 1.0,  # Giây nghỉ giữa các request
    'max_retries': 3,  # Số lần retry
    'timeout': 30,  # Timeout cho request (giây)
    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Website URLs
WEBSITES = {
    'lichviet': {
        'base_url': 'https://lichviet.app',
        'delay': 2.0,  # Chậm hơn vì sử dụng JavaScript
        'type': 'dynamic'  # Cần Playwright
    },
    'lichvn': {
        'base_url': 'https://lichvn.net',
        'delay': 1.5,
        'type': 'static'  # Có thể dùng BeautifulSoup
    },
    'tuvi': {
        'base_url': 'https://tuvi.vn',
        'delay': 1.0,
        'type': 'static'
    }
}

# Database settings
DATABASE_SETTINGS = {
    'sqlite_path': str(DATA_DIR / "lich_database.db"),
    'backup_enabled': True,
    'backup_dir': str(DATA_DIR / "backups")
}

# Scheduler settings
SCHEDULER_SETTINGS = {
    'daily_time': "06:00",  # Crawl hàng ngày
    'weekly_day': "sunday",  # Crawl hàng tuần
    'weekly_time': "08:00",
    'monthly_day': 1,  # Ngày trong tháng
    'monthly_time': "07:00"
}

# Logging settings
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_path': str(LOGS_DIR / "crawler.log"),
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# Export settings
EXPORT_FORMATS = ['json', 'csv', 'sqlite', 'excel']

# Data validation rules
VALIDATION_RULES = {
    'required_fields': ['solar_date', 'source'],
    'date_format': '%Y-%m-%d',
    'lunar_date_pattern': r'\d{1,2}/\d{1,2}(/\d{4})?',
    'can_chi_valid': [
        'Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý'  # Can
    ] + [
        'Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi'  # Chi
    ]
}

# Rate limiting để tôn trọng servers
RATE_LIMITS = {
    'requests_per_minute': 30,
    'concurrent_requests': 2,
    'respect_robots_txt': True
}

# Error handling
ERROR_HANDLING = {
    'retry_delays': [1, 2, 4],  # Exponential backoff (seconds)
    'max_consecutive_failures': 5,
    'notification_enabled': False,  # Có thể thêm email/Slack notification
    'fallback_crawlers': True  # Sử dụng crawler khác nếu một cái fail
}

# Development settings
DEVELOPMENT = {
    'debug_mode': False,
    'test_mode': False,
    'sample_size': 10,  # Số lượng records để test
    'skip_weekends': False
}

# Environment-specific settings
ENV = os.getenv('ENVIRONMENT', 'development')

if ENV == 'production':
    LOGGING_CONFIG['level'] = 'WARNING'
    DEVELOPMENT['debug_mode'] = False
elif ENV == 'testing':
    DEVELOPMENT['test_mode'] = True
    CRAWLER_SETTINGS['delay'] = 0.1  # Nhanh hơn cho test

# API Keys (nếu cần trong tương lai)
API_KEYS = {
    'weather_api': os.getenv('WEATHER_API_KEY'),
    'notification_service': os.getenv('NOTIFICATION_API_KEY')
}
