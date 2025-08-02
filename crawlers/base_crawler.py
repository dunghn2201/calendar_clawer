"""
Base crawler class cho tất cả các crawler
Cung cấp các chức năng chung như retry, logging, rate limiting
"""

import time
import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import sqlite3
from pathlib import Path

# Tạo thư mục logs nếu chưa có
Path('logs').mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/crawler.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class LichData:
    """Cấu trúc dữ liệu lịch âm chuẩn"""
    solar_date: str  # YYYY-MM-DD
    lunar_date: str  # DD/MM/YYYY
    can_chi_day: Optional[str] = None
    can_chi_month: Optional[str] = None
    can_chi_year: Optional[str] = None
    holiday: Optional[str] = None
    notes: Optional[str] = None
    source: Optional[str] = None
    crawled_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi sang dictionary"""
        return {
            'solar_date': self.solar_date,
            'lunar_date': self.lunar_date,
            'can_chi_day': self.can_chi_day,
            'can_chi_month': self.can_chi_month,
            'can_chi_year': self.can_chi_year,
            'holiday': self.holiday,
            'notes': self.notes,
            'source': self.source,
            'crawled_at': self.crawled_at or datetime.now().isoformat()
        }

class BaseCrawler(ABC):
    """Base class cho tất cả các crawler"""
    
    def __init__(self, delay: float = 1.0, max_retries: int = 3):
        self.delay = delay
        self.max_retries = max_retries
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.data: List[LichData] = []
        
        # Tạo thư mục logs nếu chưa có
        Path('logs').mkdir(exist_ok=True)
        Path('data').mkdir(exist_ok=True)
    
    def rate_limit(self):
        """Rate limiting để tránh spam server"""
        if self.delay > 0:
            time.sleep(self.delay)
    
    def retry_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Thực hiện request với retry logic"""
        for attempt in range(self.max_retries):
            try:
                self.rate_limit()
                response = self.session.get(url, **kwargs)
                response.raise_for_status()
                return response
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == self.max_retries - 1:
                    self.logger.error(f"All attempts failed for {url}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        return None
    
    @abstractmethod
    def crawl_date(self, date: datetime) -> Optional[LichData]:
        """Crawl dữ liệu cho một ngày cụ thể"""
        pass
    
    @abstractmethod
    def crawl_month(self, year: int, month: int) -> List[LichData]:
        """Crawl dữ liệu cho một tháng"""
        pass
    
    def crawl_year(self, year: int) -> List[LichData]:
        """Crawl dữ liệu cho cả năm"""
        self.logger.info(f"Bắt đầu crawl năm {year}")
        all_data = []
        
        for month in range(1, 13):
            self.logger.info(f"Crawl tháng {month}/{year}")
            month_data = self.crawl_month(year, month)
            all_data.extend(month_data)
            self.logger.info(f"Hoàn thành tháng {month}/{year}: {len(month_data)} ngày")
        
        self.data = all_data
        self.logger.info(f"Hoàn thành crawl năm {year}: {len(all_data)} ngày")
        return all_data
    
    def save_to_json(self, filename: str) -> None:
        """Lưu dữ liệu ra file JSON"""
        filepath = Path('data') / filename
        data_dict = [item.to_dict() for item in self.data]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Đã lưu {len(self.data)} records vào {filepath}")
    
    def save_to_sqlite(self, db_path: str = "data/lich_database.db") -> None:
        """Lưu dữ liệu vào SQLite database"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Tạo bảng nếu chưa có
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lich_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                solar_date TEXT NOT NULL,
                lunar_date TEXT,
                can_chi_day TEXT,
                can_chi_month TEXT, 
                can_chi_year TEXT,
                holiday TEXT,
                notes TEXT,
                source TEXT,
                crawled_at TEXT,
                UNIQUE(solar_date, source)
            )
        ''')
        
        # Insert dữ liệu
        for item in self.data:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO lich_data 
                    (solar_date, lunar_date, can_chi_day, can_chi_month, 
                     can_chi_year, holiday, notes, source, crawled_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.solar_date,
                    item.lunar_date,
                    item.can_chi_day,
                    item.can_chi_month,
                    item.can_chi_year,
                    item.holiday,
                    item.notes,
                    item.source,
                    item.crawled_at or datetime.now().isoformat()
                ))
            except sqlite3.IntegrityError:
                pass  # Skip duplicates
        
        conn.commit()
        conn.close()
        self.logger.info(f"Đã lưu {len(self.data)} records vào SQLite database")
    
    def get_stats(self) -> Dict[str, Any]:
        """Thống kê dữ liệu đã crawl"""
        if not self.data:
            return {"total": 0}
        
        return {
            "total": len(self.data),
            "sources": list(set(item.source for item in self.data if item.source)),
            "date_range": {
                "from": min(item.solar_date for item in self.data),
                "to": max(item.solar_date for item in self.data)
            },
            "holidays": len([item for item in self.data if item.holiday])
        }

    def save_data(self, data: Optional[List[LichData]] = None, filename: Optional[str] = None) -> str:
        """Lưu dữ liệu với cấu trúc có tổ chức sử dụng DataManager"""
        # Sử dụng self.data nếu không truyền data
        if data is None:
            data = self.data
            
        if not data:
            print("⚠️ Không có dữ liệu để lưu")
            return ""
        
        # Import data manager
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).parent.parent))
        from data_manager import DataManager
        dm = DataManager()
        
        # Convert LichData objects to dict
        data_dicts = []
        for item in data:
            if isinstance(item, LichData):
                data_dicts.append(item.to_dict())
            else:
                data_dicts.append(item)
        
        # Xác định date range từ dữ liệu
        date_range = None
        if data_dicts:
            first_date = data_dicts[0].get('solar_date', '')
            last_date = data_dicts[-1].get('solar_date', '') if len(data_dicts) > 1 else first_date
            
            if first_date:
                if first_date == last_date:
                    date_range = first_date
                else:
                    date_range = f"{first_date}_to_{last_date}"
        
        # Lưu với data manager
        source_name = getattr(self, 'source_name', 'unknown')
        filepath = dm.save_data(data_dicts, source_name, date_range)
        return filepath
