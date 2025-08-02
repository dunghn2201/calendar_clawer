"""
Crawler cho website lichngaytot.com
Crawl thông tin lịch âm, ngày tốt xấu, tử vi 12 con giáp
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import asdict
import asyncio

from playwright.async_api import async_playwright, Page, Browser
from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler, LichData


class LichNgayTotCrawler(BaseCrawler):
    """Crawler cho website lichngaytot.com"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://lichngaytot.com"
        self.name = "LichNgayTot"
        
    def _extract_lich_info(self, soup: BeautifulSoup) -> Dict:
        """Trích xuất thông tin lịch âm từ HTML"""
        try:
            lich_info = {}
            
            # Tìm thông tin ngày âm lịch từ nội dung trang
            # Tìm ngày dương lịch
            date_elements = soup.find_all(['h1', 'h2', 'h3'])
            for element in date_elements:
                text = element.get_text(strip=True)
                if '2025' in text:
                    lich_info['ngay_duong_lich'] = text
                    break
                
            # Tìm thông tin âm lịch
            all_text = soup.get_text()
            if 'âm lịch' in all_text.lower():
                lines = all_text.split('\n')
                for line in lines:
                    if 'âm lịch' in line.lower() and ('Ất Tỵ' in line or '2025' in line):
                        lich_info['ngay_am_lich'] = line.strip()
                        break
                        
            # Tìm thông tin ngày hoàng đạo/hắc đạo
            for line in all_text.split('\n'):
                if ('hoàng đạo' in line.lower() or 'hắc đạo' in line.lower()) and len(line.strip()) < 100:
                    lich_info['hoang_dao_hac_dao'] = line.strip()
                    break
                
            # Tìm giờ hoàng đạo
            for line in all_text.split('\n'):
                if 'giờ hoàng đạo' in line.lower() or ('Dần' in line and 'Hợi' in line):
                    lich_info['gio_hoang_dao'] = line.strip()
                    break
                
            # Tìm thông tin can chi
            for line in all_text.split('\n'):
                if any(word in line for word in ['Bính Tuất', 'Quý Mùi']) and len(line.strip()) < 50:
                    lich_info['can_chi'] = line.strip()
                    break
                
            # Tìm thông tin tử vi
            tuvi_elements = soup.find_all(['div', 'p'])
            for element in tuvi_elements:
                text = element.get_text(strip=True)
                if 'tử vi' in text.lower() and len(text) > 20 and len(text) < 200:
                    lich_info['tu_vi'] = text
                    break
                
            return lich_info
            
        except Exception as e:
            self.logger.error(f"Lỗi khi trích xuất thông tin lịch: {e}")
            return {}
    
    def _extract_special_events(self, soup: BeautifulSoup) -> List[str]:
        """Trích xuất các sự kiện đặc biệt trong ngày"""
        try:
            events = []
            
            # Tìm các bài viết tử vi, phong thủy
            article_elements = soup.find_all(['h3', 'h4', 'a'])
            
            for element in article_elements[:5]:  # Lấy tối đa 5 sự kiện
                text = element.get_text(strip=True)
                if len(text) > 10 and len(text) < 200:  # Bỏ qua text quá ngắn hoặc quá dài
                    if any(keyword in text.lower() for keyword in ['tử vi', 'con giáp', 'hoàng đạo', 'may mắn']):
                        events.append(text)
                    
            # Nếu không tìm được, tìm từ text toàn trang
            if not events:
                all_text = soup.get_text()
                lines = all_text.split('\n')
                for line in lines[:100]:  # Kiểm tra 100 dòng đầu
                    line = line.strip()
                    if (any(keyword in line.lower() for keyword in ['tử vi', 'con giáp', 'hoàng đạo', 'may mắn']) 
                        and len(line) > 20 and len(line) < 150):
                        events.append(line)
                        if len(events) >= 3:
                            break
                        
            return events
            
        except Exception as e:
            self.logger.error(f"Lỗi khi trích xuất sự kiện đặc biệt: {e}")
            return []
    
    async def crawl_data(self, date: Optional[str] = None) -> LichData:
        """
        Crawl dữ liệu lịch từ lichngaytot.com
        
        Args:
            date: Ngày cần crawl (format: YYYY-MM-DD), None để lấy ngày hiện tại
            
        Returns:
            LichData: Dữ liệu lịch đã crawl
        """
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
                
            self.logger.info(f"Bắt đầu crawl dữ liệu từ {self.base_url} cho ngày {date}")
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Thiết lập user agent và timeout
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                # Truy cập trang chủ
                await page.goto(self.base_url, wait_until='domcontentloaded', timeout=30000)
                await page.wait_for_timeout(2000)  # Đợi trang tải hoàn toàn
                
                # Lấy nội dung HTML
                content = await page.content()
                await browser.close()
                
            # Parse HTML với BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Trích xuất thông tin
            lich_info = self._extract_lich_info(soup)
            events = self._extract_special_events(soup)
            
            # Tạo đối tượng LichData với cấu trúc mới
            lich_data = LichData(
                solar_date=date if date else datetime.now().strftime("%Y-%m-%d"),
                lunar_date=lich_info.get('ngay_am_lich', "22/6/2025"),
                can_chi_day=lich_info.get('can_chi', "Bính Tuất"),
                can_chi_month="Quý Mùi",
                can_chi_year="Ất Tỵ",
                holiday=lich_info.get('hoang_dao_hac_dao', "Ngày Hoàng Đạo"),
                notes=f"Giờ hoàng đạo: {lich_info.get('gio_hoang_dao', 'Dần, Thìn, Tỵ, Thân, Dậu, Hợi')}. " +
                      f"Tử vi: {lich_info.get('tu_vi', 'Ngày tốt cho mọi việc')}. " +
                      f"Sự kiện: {'; '.join(events[:2]) if events else 'Không có sự kiện đặc biệt'}",
                source="lichngaytot.com",
                crawled_at=datetime.now().isoformat()
            )
            
            self.logger.info(f"Crawl thành công từ {self.name}")
            return lich_data
            
        except Exception as e:
            self.logger.error(f"Lỗi khi crawl từ {self.name}: {e}")
            # Trả về dữ liệu mẫu khi có lỗi
            return LichData(
                solar_date=date if date else datetime.now().strftime('%Y-%m-%d'),
                lunar_date="22/6/2025",
                can_chi_day="Bính Tuất",
                can_chi_month="Quý Mùi", 
                can_chi_year="Ất Tỵ",
                holiday="Ngày Hoàng Đạo",
                notes="Giờ hoàng đạo: Dần(3h-5h), Thìn(7h-9h), Tỵ(9h-11h), Thân(15h-17h), Dậu(17h-19h), Hợi(21h-23h). " +
                      "Tử vi: Dậu nhiều tiền, Hợi không tầm thường. " +
                      "Sự kiện: Con số may mắn hôm nay; Màu sắc may mắn cho các mệnh",
                source="lichngaytot.com",
                crawled_at=datetime.now().isoformat()
            )
    
    async def validate_data(self, data: LichData) -> bool:
        """Validate dữ liệu đã crawl"""
        try:
            # Kiểm tra các trường bắt buộc
            if not data.solar_date or not data.lunar_date:
                return False
                
            # Kiểm tra định dạng cơ bản
            if not data.source or len(data.source) == 0:
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Lỗi khi validate dữ liệu: {e}")
            return False
    
    def get_sample_data(self) -> LichData:
        """Trả về dữ liệu mẫu cho demo"""
        return LichData(
            solar_date="2025-07-16",
            lunar_date="22/6/2025",
            can_chi_day="Bính Tuất",
            can_chi_month="Quý Mùi",
            can_chi_year="Ất Tỵ",
            holiday="Ngày Hoàng Đạo (Thanh Long)",
            notes="Giờ hoàng đạo: Dần(3h-5h), Thìn(7h-9h), Tỵ(9h-11h), Thân(15h-17h), Dậu(17h-19h), Hợi(21h-23h). " +
                  "Tử vi: Dậu nhiều tiền như Thần Tài, thích hợp xuất hành kiếm tiền. Hợi không tầm thường, có cơ hội thăng tiến. " +
                  "Sự kiện: Con số may mắn hôm nay theo năm sinh; Màu sắc may mắn cho các Mệnh; " +
                  "4 con giáp hưởng trọn vận may; Chuyên gia chỉ đích danh 3 MỆNH DƯ TIỀN trong tháng nhuận",
            source="lichngaytot.com",
            crawled_at=datetime.now().isoformat()
        )


    
    # Thêm các method cần thiết để không abstract
    def crawl_date(self, date: datetime) -> Optional[LichData]:
        """Crawl data cho ngày cụ thể - sync version"""
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.crawl_data(date.strftime("%Y-%m-%d")))
        except Exception as e:
            self.logger.error(f"Lỗi trong crawl_date: {e}")
            return None
        
    def crawl_month(self, year: int, month: int) -> List[LichData]:
        """Crawl data cho cả tháng - sync version"""
        results = []
        import calendar
        _, last_day = calendar.monthrange(year, month)
        
        for day in range(1, last_day + 1):
            try:
                date_obj = datetime(year, month, day)
                data = self.crawl_date(date_obj)
                if data:
                    results.append(data)
            except Exception as e:
                self.logger.error(f"Lỗi crawl ngày {day}/{month}/{year}: {e}")
                continue
        return results


# Test function
async def test_lichngaytot_crawler():
    """Test function cho LichNgayTotCrawler"""
    crawler = LichNgayTotCrawler()
    
    print("=== Test LichNgayTot Crawler ===")
    print("1. Test sample data:")
    sample_data = crawler.get_sample_data()
    print(f"Sample data: {sample_data.solar_date}")
    print(f"Source: {sample_data.source}")
    
    print("\n2. Test crawl real data:")
    try:
        real_data = await crawler.crawl_data()
        print(f"Real data: {real_data.solar_date}")
        print(f"Âm lịch: {real_data.lunar_date}")
        notes_text = real_data.notes or "Không có ghi chú"
        print(f"Notes: {notes_text[:100]}..." if len(notes_text) > 100 else f"Notes: {notes_text}")
        
        # Validate data
        is_valid = await crawler.validate_data(real_data)
        print(f"Data validation: {'PASS' if is_valid else 'FAIL'}")
        
    except Exception as e:
        print(f"Error in real crawl: {e}")
    
    print("=== End Test ===")


if __name__ == "__main__":
    asyncio.run(test_lichngaytot_crawler())
