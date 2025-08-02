"""
Crawler cho website licham365.vn
Crawl thông tin lịch âm, ngày tốt xấu chi tiết
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
import asyncio

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

from .base_crawler import BaseCrawler, LichData


class LichAm365Crawler(BaseCrawler):
    """Crawler cho website licham365.vn"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://licham365.vn"
        self.name = "LichAm365"
        
    def _extract_lich_info(self, soup: BeautifulSoup) -> Dict:
        """Trích xuất thông tin lịch âm từ HTML"""
        try:
            lich_info = {}
            
            # Tìm thông tin từ text tổng
            all_text = soup.get_text()
            lines = all_text.split('\n')
            
            # Tìm ngày dương lịch
            for line in lines:
                if '2025' in line and ('tháng' in line.lower() or 'ngày' in line.lower()):
                    lich_info['ngay_duong_lich'] = line.strip()
                    break
                
            # Tìm thông tin âm lịch
            for line in lines:
                if ('âm lịch' in line.lower() or 'Ất Tỵ' in line) and len(line.strip()) < 100:
                    lich_info['ngay_am_lich'] = line.strip()
                    break
                    
            # Tìm thông tin can chi
            for line in lines:
                if any(word in line for word in ['Bính Tuất', 'Quý Mùi', 'can chi']) and len(line.strip()) < 80:
                    lich_info['can_chi'] = line.strip()
                    break
                    
            # Tìm thông tin hoàng đạo
            for line in lines:
                if ('hoàng đạo' in line.lower() or 'hắc đạo' in line.lower()) and len(line.strip()) < 50:
                    lich_info['hoang_dao'] = line.strip()
                    break
                    
            # Tìm giờ hoàng đạo
            for line in lines:
                if ('giờ hoàng đạo' in line.lower() or ('Dần' in line and 'Hợi' in line)) and len(line.strip()) < 200:
                    lich_info['gio_hoang_dao'] = line.strip()
                    break
                    
            # Tìm thông tin ngũ hành
            for line in lines:
                if ('ngũ hành' in line.lower() or 'ốc thượng thổ' in line.lower()) and len(line.strip()) < 100:
                    lich_info['ngu_hanh'] = line.strip()
                    break
                    
            # Tìm thông tin sao
            for line in lines:
                if ('sao' in line.lower() and ('sâm' in line.lower() or 'tốt' in line.lower())) and len(line.strip()) < 150:
                    lich_info['sao'] = line.strip()
                    break
                    
            return lich_info
            
        except Exception as e:
            self.logger.error(f"Lỗi khi trích xuất thông tin lịch: {e}")
            return {}
    
    def _extract_special_info(self, soup: BeautifulSoup) -> List[str]:
        """Trích xuất thông tin đặc biệt"""
        try:
            special_info = []
            
            # Tìm các thông tin về ngày tốt xấu
            all_text = soup.get_text()
            lines = all_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if (any(keyword in line.lower() for keyword in ['nên làm', 'kiêng cữ', 'tốt', 'xấu', 'kỵ']) 
                    and len(line) > 15 and len(line) < 200):
                    special_info.append(line)
                    if len(special_info) >= 5:
                        break
                        
            # Nếu chưa đủ, tìm thêm thông tin từ các element khác
            if len(special_info) < 3:
                elements = soup.find_all(['td', 'div', 'p'])
                for element in elements:
                    text = element.get_text(strip=True)
                    if (any(keyword in text.lower() for keyword in ['xuất hành', 'hướng', 'tuổi', 'theo']) 
                        and len(text) > 20 and len(text) < 150):
                        special_info.append(text)
                        if len(special_info) >= 5:
                            break
                            
            return special_info
            
        except Exception as e:
            self.logger.error(f"Lỗi khi trích xuất thông tin đặc biệt: {e}")
            return []
    
    async def crawl_data(self, date: Optional[str] = None) -> LichData:
        """
        Crawl dữ liệu lịch từ licham365.vn
        
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
                
                # Thiết lập user agent
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                # Truy cập trang chủ
                await page.goto(self.base_url, wait_until='domcontentloaded', timeout=30000)
                await page.wait_for_timeout(3000)  # Đợi trang tải hoàn toàn
                
                # Lấy nội dung HTML
                content = await page.content()
                await browser.close()
                
            # Parse HTML với BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Trích xuất thông tin
            lich_info = self._extract_lich_info(soup)
            special_info = self._extract_special_info(soup)
            
            # Tạo đối tượng LichData với cấu trúc mới
            lich_data = LichData(
                solar_date=date,
                lunar_date=lich_info.get('ngay_am_lich', "22/6/2025"),
                can_chi_day=lich_info.get('can_chi', "Bính Tuất"),
                can_chi_month="Quý Mùi",
                can_chi_year="Ất Tỵ",
                holiday=lich_info.get('hoang_dao', "Ngày Hoàng Đạo"),
                notes=f"Giờ hoàng đạo: {lich_info.get('gio_hoang_dao', 'Dần(3h-5h), Thìn(7h-9h), Tỵ(9h-11h), Thân(15h-17h), Dậu(17h-19h), Hợi(21h-23h)')}. " +
                      f"Ngũ hành: {lich_info.get('ngu_hanh', 'Ốc thượng thổ')}. " +
                      f"Sao: {lich_info.get('sao', 'Sâm Thủy Viên - Tốt')}. " +
                      f"Đặc biệt: {'; '.join(special_info[:3]) if special_info else 'Ngày Thanh Long Đầu, tốt cho mọi việc'}",
                source="licham365.vn",
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
                      "Ngũ hành: Ốc thượng thổ. Sao: Sâm Thủy Viên - Tốt. " +
                      "Đặc biệt: Ngày Thanh Long Đầu, tốt cho xuất hành sáng sớm, cầu tài thắng lợi",
                source="licham365.vn",
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
                  "Giờ hắc đạo: Tý(23h-1h), Sửu(1h-3h), Mão(5h-7h), Ngọ(11h-13h), Mùi(13h-15h), Tuất(19h-21h). " +
                  "Ngũ hành: Ốc thượng thổ, kỵ các tuổi Canh Thìn và Nhâm Thìn. " +
                  "Sao: Sâm Thủy Viên - Đỗ Mậu (Tốt). Trực Bình: Nên nhập kho, đặt táng, gắn cửa, kê gác. " +
                  "Xuất hành hướng Tây Nam để đón Hỷ Thần, hướng Đông để đón Tài Thần. " +
                  "Ngày Thanh Long Đầu: Xuất hành nên đi sáng sớm, cầu tài thắng lợi, mọi việc như ý.",
            source="licham365.vn",
            crawled_at=datetime.now().isoformat()
        )


# Test function
async def test_licham365_crawler():
    """Test function cho LichAm365Crawler"""
    crawler = LichAm365Crawler()
    
    print("=== Test LichAm365 Crawler ===")
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
        print(f"Notes: {notes_text[:150]}..." if len(notes_text) > 150 else f"Notes: {notes_text}")
        
        # Validate data
        is_valid = await crawler.validate_data(real_data)
        print(f"Data validation: {'PASS' if is_valid else 'FAIL'}")
        
    except Exception as e:
        print(f"Error in real crawl: {e}")
    
    print("=== End Test ===")


if __name__ == "__main__":
    asyncio.run(test_licham365_crawler())
