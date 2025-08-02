"""
Crawler cho trang lichvn.net
Sử dụng BeautifulSoup cho web tĩnh
"""

from datetime import datetime, timedelta
from typing import List, Optional
from bs4 import BeautifulSoup
import re

from .base_crawler import BaseCrawler, LichData

class LichVnCrawler(BaseCrawler):
    """Crawler cho lichvn.net sử dụng BeautifulSoup"""
    
    def __init__(self, delay: float = 1.0, max_retries: int = 3):
        super().__init__(delay, max_retries)
        self.base_url = "https://lichvn.net"
        self.source_name = "lichvn.net"
    
    def crawl_month(self, year: int, month: int) -> List[LichData]:
        """Crawl dữ liệu một tháng"""
        data = []
        url = f"{self.base_url}/lich-van-nien/{year}-{month:02d}"
        
        try:
            response = self.retry_request(url)
            if not response:
                return data
            
            soup = BeautifulSoup(response.content, 'html.parser')
            self.logger.info(f"Đang phân tích: {url}")
            
            # Tìm container của lịch
            calendar_container = soup.find('div', class_=['calendar-container', 'calendar-table', 'month-calendar'])
            
            if not calendar_container:
                # Thử tìm table
                calendar_container = soup.find('table', class_=['calendar', 'month-table'])
            
            if calendar_container:
                # Tìm tất cả các ô ngày
                day_cells = calendar_container.find_all(['td', 'div'], class_=re.compile(r'(day|date|cell)'))
                
                for cell in day_cells:
                    try:
                        # Lấy ngày dương lịch
                        solar_day = None
                        solar_element = cell.find(class_=re.compile(r'(solar|duong|date)'))
                        if solar_element:
                            solar_day = solar_element.get_text(strip=True)
                        elif cell.get('data-date'):
                            solar_day = cell.get('data-date')
                        else:
                            # Tìm số trong cell
                            text = cell.get_text(strip=True)
                            numbers = re.findall(r'\d+', text)
                            if numbers:
                                solar_day = numbers[0]
                        
                        # Lấy ngày âm lịch
                        lunar_day = None
                        lunar_element = cell.find(class_=re.compile(r'(lunar|am|moon)'))
                        if lunar_element:
                            lunar_day = lunar_element.get_text(strip=True)
                        
                        # Lấy can chi
                        can_chi = None
                        can_chi_element = cell.find(class_=re.compile(r'(can-chi|canchi|horoscope)'))
                        if can_chi_element:
                            can_chi = can_chi_element.get_text(strip=True)
                        
                        # Lấy ngày lễ
                        holiday = None
                        holiday_element = cell.find(class_=re.compile(r'(holiday|le|event)'))
                        if holiday_element:
                            holiday = holiday_element.get_text(strip=True)
                        
                        # Kiểm tra title attribute cho thông tin bổ sung
                        title = cell.get('title', '')
                        if title and not lunar_day:
                            # Tìm thông tin âm lịch trong title
                            lunar_match = re.search(r'(\d+/\d+)', title)
                            if lunar_match:
                                lunar_day = lunar_match.group(1)
                        
                        if solar_day and solar_day.isdigit():
                            day_num = int(solar_day)
                            if 1 <= day_num <= 31:
                                solar_formatted = f"{year}-{month:02d}-{day_num:02d}"
                                
                                lich_data = LichData(
                                    solar_date=solar_formatted,
                                    lunar_date=lunar_day if lunar_day else "",
                                    can_chi_day=can_chi,
                                    holiday=holiday,
                                    notes=title if title else None,
                                    source=self.source_name
                                )
                                
                                data.append(lich_data)
                    
                    except Exception as e:
                        self.logger.warning(f"Lỗi xử lý cell: {e}")
                        continue
            
            else:
                self.logger.warning(f"Không tìm thấy calendar container trong {url}")
        
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
    
    crawler = LichVnCrawler()
    
    # Test crawl một tháng
    print("🚀 Testing LichVN Crawler...")
    data = crawler.crawl_month(2024, 1)
    print(f"✅ Crawled {len(data)} days for January 2024")
    
    if data:
        print("\n📋 Sample data:")
        for i, item in enumerate(data[:3]):
            print(f"  {i+1}. {item.solar_date} - {item.lunar_date}")
    
    # Lưu dữ liệu test
    if data:
        crawler.data = data
        crawler.save_to_json("test_lichvn.json")
        print("💾 Saved test data to test_lichvn.json")
