"""
Crawler cho trang tuvi.vn
Crawler đơn giản sử dụng requests + BeautifulSoup
"""

from datetime import datetime, timedelta
from typing import List, Optional
from bs4 import BeautifulSoup
import re

from .base_crawler import BaseCrawler, LichData

class TuviCrawler(BaseCrawler):
    """Crawler cho tuvi.vn"""
    
    def __init__(self, delay: float = 1.0, max_retries: int = 3):
        super().__init__(delay, max_retries)
        self.base_url = "https://tuvi.vn"
        self.source_name = "tuvi.vn"
    
    def crawl_month(self, year: int, month: int) -> List[LichData]:
        """Crawl dữ liệu một tháng"""
        data = []
        url = f"{self.base_url}/lich-am/{year}/{month}"
        
        try:
            response = self.retry_request(url)
            if not response:
                return data
            
            soup = BeautifulSoup(response.content, 'html.parser')
            self.logger.info(f"Đang phân tích: {url}")
            
            # Tìm bảng lịch
            calendar_table = soup.find('table', class_=['calendar', 'lich-table', 'month-view'])
            
            if not calendar_table:
                # Thử tìm container khác
                calendar_table = soup.find('div', class_=['calendar-wrapper', 'lich-wrapper'])
            
            if calendar_table:
                # Tìm tất cả các ô chứa ngày
                day_cells = calendar_table.find_all(['td', 'div'], class_=re.compile(r'(day|ngay|date)'))
                
                for cell in day_cells:
                    try:
                        # Skip empty cells
                        if not cell.get_text(strip=True):
                            continue
                        
                        # Lấy ngày dương lịch
                        solar_day = None
                        
                        # Tìm trong data attribute
                        if cell.get('data-day'):
                            solar_day = cell.get('data-day')
                        elif cell.get('data-date'):
                            solar_day = cell.get('data-date')
                        else:
                            # Tìm trong text
                            day_text = cell.get_text(strip=True)
                            day_match = re.search(r'(\d{1,2})', day_text)
                            if day_match:
                                solar_day = day_match.group(1)
                        
                        # Lấy ngày âm lịch
                        lunar_day = None
                        lunar_span = cell.find(['span', 'div'], class_=re.compile(r'(lunar|am|moon)'))
                        if lunar_span:
                            lunar_day = lunar_span.get_text(strip=True)
                        
                        # Lấy can chi
                        can_chi = None
                        can_chi_span = cell.find(['span', 'div'], class_=re.compile(r'(can-chi|canchi)'))
                        if can_chi_span:
                            can_chi = can_chi_span.get_text(strip=True)
                        
                        # Lấy ngày lễ/sự kiện
                        holiday = None
                        event_span = cell.find(['span', 'div'], class_=re.compile(r'(holiday|event|le)'))
                        if event_span:
                            holiday = event_span.get_text(strip=True)
                        
                        # Lấy ghi chú từ title
                        notes = cell.get('title', '')
                        
                        if solar_day and solar_day.isdigit():
                            day_num = int(solar_day)
                            if 1 <= day_num <= 31:
                                solar_formatted = f"{year}-{month:02d}-{day_num:02d}"
                                
                                lich_data = LichData(
                                    solar_date=solar_formatted,
                                    lunar_date=lunar_day if lunar_day else "",
                                    can_chi_day=can_chi,
                                    holiday=holiday,
                                    notes=notes if notes else None,
                                    source=self.source_name
                                )
                                
                                data.append(lich_data)
                    
                    except Exception as e:
                        self.logger.warning(f"Lỗi xử lý cell: {e}")
                        continue
            
            else:
                self.logger.warning(f"Không tìm thấy calendar table trong {url}")
        
        except Exception as e:
            self.logger.error(f"Lỗi crawl tháng {month}/{year}: {e}")
        
        return data
    
    def crawl_date(self, date: datetime) -> Optional[LichData]:
        """Crawl dữ liệu cho một ngày cụ thể"""
        month_data = self.crawl_month(date.year, date.month)
        date_str = date.strftime("%Y-%m-%d")
        
        for item in month_data:
            if item.solar_date == date_str:
                return item
        
        return None

# Chạy thử nghiệm  
if __name__ == "__main__":
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    crawler = TuviCrawler()
    
    # Test crawl một tháng
    print("🚀 Testing Tuvi Crawler...")
    data = crawler.crawl_month(2024, 1)
    print(f"✅ Crawled {len(data)} days for January 2024")
    
    if data:
        print("\n📋 Sample data:")
        for i, item in enumerate(data[:3]):
            print(f"  {i+1}. {item.solar_date} - {item.lunar_date}")
    
    # Lưu dữ liệu test
    if data:
        crawler.data = data
        crawler.save_to_json("test_tuvi.json")
        print("💾 Saved test data to test_tuvi.json")
