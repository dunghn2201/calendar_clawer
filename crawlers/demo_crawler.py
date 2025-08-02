"""
Demo crawler để test hoạt động
Crawl từ API hoặc trang web đơn giản
"""

from datetime import datetime, timedelta
from typing import List, Optional
import requests
import json
import re

from .base_crawler import BaseCrawler, LichData

class DemoCrawler(BaseCrawler):
    """Demo crawler để test các chức năng"""
    
    def __init__(self, delay: float = 0.5, max_retries: int = 3):
        super().__init__(delay, max_retries)
        self.source_name = "demo_data"
    
    def generate_demo_data(self, year: int, month: int) -> List[LichData]:
        """Tạo dữ liệu demo để test"""
        data = []
        
        # Danh sách can chi đơn giản
        can = ['Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý']
        chi = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi']
        
        # Số ngày trong tháng
        if month in [4, 6, 9, 11]:
            days_in_month = 30
        elif month == 2:
            days_in_month = 29 if year % 4 == 0 else 28
        else:
            days_in_month = 31
        
        for day in range(1, days_in_month + 1):
            try:
                # Tạo ngày dương lịch
                solar_date = f"{year}-{month:02d}-{day:02d}"
                
                # Tạo ngày âm lịch giả (chỉ để demo)
                lunar_day = (day + 10) % 30 + 1
                lunar_month = month if lunar_day <= 15 else (month % 12) + 1
                lunar_date = f"{lunar_day:02d}/{lunar_month:02d}"
                
                # Tạo can chi
                can_index = (day - 1) % 10
                chi_index = (day - 1) % 12
                can_chi = f"{can[can_index]} {chi[chi_index]}"
                
                # Thêm ngày lễ cho một số ngày
                holiday = None
                if month == 1 and day == 1:
                    holiday = "Tết Dương lịch"
                elif month == 2 and day == 14:
                    holiday = "Valentine"
                elif month == 4 and day == 30:
                    holiday = "Giải phóng miền Nam"
                elif month == 9 and day == 2:
                    holiday = "Quốc khánh"
                
                lich_data = LichData(
                    solar_date=solar_date,
                    lunar_date=lunar_date,
                    can_chi_day=can_chi,
                    holiday=holiday,
                    notes=f"Demo data cho ngày {day}/{month}/{year}",
                    source=self.source_name
                )
                
                data.append(lich_data)
                
            except Exception as e:
                self.logger.warning(f"Lỗi tạo demo data cho ngày {day}: {e}")
                continue
        
        return data
    
    def crawl_month(self, year: int, month: int) -> List[LichData]:
        """Crawl dữ liệu một tháng (demo)"""
        self.logger.info(f"Tạo demo data cho tháng {month}/{year}")
        
        # Giả lập delay như crawl thật
        self.rate_limit()
        
        data = self.generate_demo_data(year, month)
        self.logger.info(f"Đã tạo {len(data)} ngày demo data")
        
        return data
    
    def crawl_date(self, date: datetime) -> Optional[LichData]:
        """Crawl dữ liệu cho một ngày cụ thể"""
        month_data = self.crawl_month(date.year, date.month)
        date_str = date.strftime("%Y-%m-%d")
        
        for item in month_data:
            if item.solar_date == date_str:
                return item
        
        return None

# Crawler thực tế cho một API lịch âm
class VietnameseCalendarAPI(BaseCrawler):
    """Crawler sử dụng API thực tế"""
    
    def __init__(self, delay: float = 1.0, max_retries: int = 3):
        super().__init__(delay, max_retries)
        self.source_name = "api_calendar"
        # API này có thể không tồn tại, chỉ là ví dụ
        self.api_base = "https://api.calendar-vietnam.com"
    
    def crawl_month(self, year: int, month: int) -> List[LichData]:
        """Crawl từ API"""
        data = []
        
        try:
            # Thử gọi API (có thể không hoạt động)
            url = f"{self.api_base}/lunar-calendar/{year}/{month}"
            response = self.retry_request(url)
            
            if response and response.status_code == 200:
                api_data = response.json()
                
                for day_info in api_data.get('days', []):
                    lich_data = LichData(
                        solar_date=day_info.get('solar_date'),
                        lunar_date=day_info.get('lunar_date'),
                        can_chi_day=day_info.get('can_chi'),
                        holiday=day_info.get('holiday'),
                        source=self.source_name
                    )
                    data.append(lich_data)
            
            else:
                # Fallback to demo data
                self.logger.info("API không khả dụng, sử dụng demo data")
                demo_crawler = DemoCrawler()
                data = demo_crawler.crawl_month(year, month)
                # Đổi source
                for item in data:
                    item.source = self.source_name + "_demo"
        
        except Exception as e:
            self.logger.error(f"Lỗi API crawl: {e}")
            # Fallback to demo data
            demo_crawler = DemoCrawler()
            data = demo_crawler.crawl_month(year, month)
        
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
    
    print("🧪 Testing Demo Crawler...")
    
    # Test demo crawler
    demo_crawler = DemoCrawler()
    data = demo_crawler.crawl_month(2024, 7)
    print(f"✅ Demo crawler: {len(data)} ngày")
    
    if data:
        print("\n📋 Demo data sample:")
        for i, item in enumerate(data[:5]):
            print(f"  {i+1}. {item.solar_date} - {item.lunar_date} - {item.can_chi_day}")
    
    # Test API crawler
    print("\n🌐 Testing API Crawler...")
    api_crawler = VietnameseCalendarAPI()
    api_data = api_crawler.crawl_month(2024, 7)
    print(f"✅ API crawler: {len(api_data)} ngày")
    
    # Lưu demo data
    if data:
        demo_crawler.data = data
        demo_crawler.save_to_json("demo_data.json")
        demo_crawler.save_to_sqlite("demo_data.db")
        print("💾 Đã lưu demo data")
