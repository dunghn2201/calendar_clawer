"""
Crawler cho trang lichviet.app
Sử dụng Playwright để xử lý JavaScript
"""

from datetime import datetime, timedelta
from typing import List, Optional
import asyncio
from playwright.async_api import async_playwright
import json
import re

from .base_crawler import BaseCrawler, LichData

class LichVietCrawler(BaseCrawler):
    """Crawler cho lichviet.app sử dụng Playwright"""
    
    def __init__(self, delay: float = 1.0, max_retries: int = 3):
        super().__init__(delay, max_retries)
        self.base_url = "https://lichviet.app"
        self.source_name = "lichviet.app"
    
    async def crawl_month_async(self, year: int, month: int) -> List[LichData]:
        """Crawl dữ liệu một tháng bằng Playwright"""
        data = []
        url = f"{self.base_url}/{year}/{month:02d}"
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Thiết lập User-Agent
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                })
                
                self.logger.info(f"Đang crawl: {url}")
                await page.goto(url, wait_until='networkidle')
                
                # Đợi calendar load
                await page.wait_for_selector('.calendar-container', timeout=10000)
                
                # Lấy tất cả các ngày trong tháng
                days = await page.query_selector_all('.day-cell')
                
                for day_element in days:
                    try:
                        # Lấy ngày dương lịch
                        solar_day = await day_element.get_attribute('data-date')
                        if not solar_day:
                            solar_span = await day_element.query_selector('.solar-date')
                            if solar_span:
                                solar_day = await solar_span.text_content()
                        
                        # Lấy ngày âm lịch
                        lunar_element = await day_element.query_selector('.lunar-date')
                        lunar_date = await lunar_element.text_content() if lunar_element else ""
                        
                        # Lấy can chi
                        can_chi_element = await day_element.query_selector('.can-chi')
                        can_chi = await can_chi_element.text_content() if can_chi_element else ""
                        
                        # Lấy ngày lễ/sự kiện
                        holiday_element = await day_element.query_selector('.holiday, .event')
                        holiday = await holiday_element.text_content() if holiday_element else ""
                        
                        # Lấy ghi chú
                        note_element = await day_element.query_selector('.note, .description')
                        notes = await note_element.text_content() if note_element else ""
                        
                        if solar_day and lunar_date:
                            # Format ngày dương lịch
                            if len(solar_day.strip()) <= 2:  # Chỉ có ngày
                                solar_formatted = f"{year}-{month:02d}-{int(solar_day):02d}"
                            else:
                                solar_formatted = solar_day
                            
                            lich_data = LichData(
                                solar_date=solar_formatted,
                                lunar_date=lunar_date.strip(),
                                can_chi_day=can_chi.strip() if can_chi else None,
                                holiday=holiday.strip() if holiday else None,
                                notes=notes.strip() if notes else None,
                                source=self.source_name
                            )
                            
                            data.append(lich_data)
                    
                    except Exception as e:
                        self.logger.warning(f"Lỗi khi xử lý ngày: {e}")
                        continue
                
                await browser.close()
                
        except Exception as e:
            self.logger.error(f"Lỗi crawl tháng {month}/{year}: {e}")
        
        return data
    
    def crawl_month(self, year: int, month: int) -> List[LichData]:
        """Wrapper đồng bộ cho crawl_month_async"""
        return asyncio.run(self.crawl_month_async(year, month))
    
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
    
    crawler = LichVietCrawler()
    
    # Test crawl một tháng
    print("🚀 Testing LichViet Crawler...")
    data = crawler.crawl_month(2024, 1)
    print(f"✅ Crawled {len(data)} days for January 2024")
    
    if data:
        print("\n📋 Sample data:")
        for i, item in enumerate(data[:3]):
            print(f"  {i+1}. {item.solar_date} - {item.lunar_date}")
    
    # Lưu dữ liệu test
    if data:
        crawler.data = data
        crawler.save_to_json("test_lichviet.json")
        print("💾 Saved test data to test_lichviet.json")
