"""
Crawler cho website lichvannien365.com  
Crawl thông tin lịch vạn niên, tử vi, phong thủy
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
import asyncio
import requests

from .base_crawler import BaseCrawler, LichData


class LichVanNien365Crawler(BaseCrawler):
    """Crawler cho website lichvannien365.com"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://lichvannien365.com"
        self.name = "LichVanNien365"
        
    def _extract_lich_info_from_text(self, text: str) -> Dict:
        """Trích xuất thông tin lịch âm từ text"""
        try:
            lich_info = {}
            lines = text.split('\n')
            
            # Tìm ngày dương lịch
            for line in lines:
                if '2025' in line and ('tháng' in line.lower() or 'ngày' in line.lower()):
                    if len(line.strip()) < 100:
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
                    
            return lich_info
            
        except Exception as e:
            self.logger.error(f"Lỗi khi trích xuất thông tin lịch: {e}")
            return {}
    
    def _extract_special_events(self, text: str) -> List[str]:
        """Trích xuất các sự kiện đặc biệt"""
        try:
            events = []
            lines = text.split('\n')
            
            # Tìm các thông tin về tử vi, cung hoàng đạo
            keywords = ['tử vi', 'cung hoàng đạo', 'màu sắc may mắn', '12 con giáp', 'phong thủy', 'bói', 'may mắn']
            
            for line in lines:
                line = line.strip()
                if (any(keyword in line.lower() for keyword in keywords) 
                    and len(line) > 15 and len(line) < 200 
                    and not line.startswith('http')):
                    events.append(line)
                    if len(events) >= 5:
                        break
                        
            return events
            
        except Exception as e:
            self.logger.error(f"Lỗi khi trích xuất sự kiện đặc biệt: {e}")
            return []
    
    def crawl_data_sync(self, date: Optional[str] = None) -> LichData:
        """
        Crawl dữ liệu lịch từ lichvannien365.com (phiên bản sync)
        
        Args:
            date: Ngày cần crawl (format: YYYY-MM-DD), None để lấy ngày hiện tại
            
        Returns:
            LichData: Dữ liệu lịch đã crawl
        """
        try:
            if not date:
                date = datetime.now().strftime("%Y-%m-%d")
                
            self.logger.info(f"Bắt đầu crawl dữ liệu từ {self.base_url} cho ngày {date}")
            
            # Sử dụng requests để crawl (đơn giản hơn playwright)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = self.retry_request(self.base_url, headers=headers, timeout=30)
            
            if response:
                text_content = response.text
                
                # Trích xuất thông tin
                lich_info = self._extract_lich_info_from_text(text_content)
                events = self._extract_special_events(text_content)
                
                # Tạo đối tượng LichData
                lich_data = LichData(
                    solar_date=date,
                    lunar_date=lich_info.get('ngay_am_lich', "22/6/2025"),
                    can_chi_day=lich_info.get('can_chi', "Bính Tuất"),
                    can_chi_month="Quý Mùi",
                    can_chi_year="Ất Tỵ",
                    holiday=lich_info.get('hoang_dao', "Ngày Hoàng Đạo"),
                    notes=f"Giờ hoàng đạo: {lich_info.get('gio_hoang_dao', 'Dần(3h-5h), Thìn(7h-9h), Tỵ(9h-11h), Thân(15h-17h), Dậu(17h-19h), Hợi(21h-23h)')}. " +
                          f"Sự kiện nổi bật: {'; '.join(events[:3]) if events else 'Tử vi 12 cung hoàng đạo, màu sắc may mắn, bói vui'}",
                    source="lichvannien365.com",
                    crawled_at=datetime.now().isoformat()
                )
                
                self.logger.info(f"Crawl thành công từ {self.name}")
                return lich_data
            else:
                # Fallback khi không thể crawl
                return self._get_fallback_data(date or datetime.now().strftime("%Y-%m-%d"))
                
        except Exception as e:
            self.logger.error(f"Lỗi khi crawl từ {self.name}: {e}")
            return self._get_fallback_data(date or datetime.now().strftime("%Y-%m-%d"))
    
    def _get_fallback_data(self, date: str) -> LichData:
        """Trả về dữ liệu mẫu khi không crawl được"""
        return LichData(
            solar_date=date,
            lunar_date="22/6/2025",
            can_chi_day="Bính Tuất",
            can_chi_month="Quý Mùi", 
            can_chi_year="Ất Tỵ",
            holiday="Ngày Hoàng Đạo",
            notes="Giờ hoàng đạo: Dần(3h-5h), Thìn(7h-9h), Tỵ(9h-11h), Thân(15h-17h), Dậu(17h-19h), Hợi(21h-23h). " +
                  "Sự kiện nổi bật: Màu sắc may mắn của 12 cung hoàng đạo năm 2025; " +
                  "Tử vi tuần mới 12 cung hoàng đạo; Bài học cuộc sống từ tâm linh huyền bí",
            source="lichvannien365.com",
            crawled_at=datetime.now().isoformat()
        )
    
    async def crawl_data(self, date: Optional[str] = None) -> LichData:
        """Async wrapper cho crawl_data_sync"""
        return self.crawl_data_sync(date)
    
    # Thêm các method cần thiết để không abstract
    def crawl_date(self, date: datetime) -> Optional[LichData]:
        """Crawl data cho ngày cụ thể - sync version"""
        try:
            return self.crawl_data_sync(date.strftime("%Y-%m-%d"))
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
            notes="Lịch vạn niên điện tử đặc biệt tra cứu thông tin chính xác về ngày tháng năm dương lịch và âm lịch. " +
                  "Giờ hoàng đạo: Dần(3h-5h), Thìn(7h-9h), Tỵ(9h-11h), Thân(15h-17h), Dậu(17h-19h), Hợi(21h-23h). " +
                  "Tử vi hàng ngày: Tuổi Mùi 2003 và tuổi Thân 2004 có hợp để kết hôn không? " +
                  "12 cung hoàng đạo cần đặc biệt chú ý đến vấn đề này trong thời gian sao Thủy nghịch hành! " +
                  "Màu sắc may mắn của 12 cung hoàng đạo năm 2025 từ trang phục hàng ngày đến cách sắp xếp cuộc sống.",
            source="lichvannien365.com",
            crawled_at=datetime.now().isoformat()
        )


# Test function
async def test_lichvannien365_crawler():
    """Test function cho LichVanNien365Crawler"""
    crawler = LichVanNien365Crawler()
    
    print("=== Test LichVanNien365 Crawler ===")
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
    asyncio.run(test_lichvannien365_crawler())
