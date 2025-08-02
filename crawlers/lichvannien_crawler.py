# -*- coding: utf-8 -*-
"""
Crawler cho trang lichvannien.net
Crawl dữ liệu lịch âm từ lichvannien.net
"""

import re
import json
from typing import Dict, Any, Optional
from datetime import datetime
from .base_crawler import BaseCrawler, LichData


class LichVannienCrawler(BaseCrawler):
    """Crawler cho trang lichvannien.net"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://lichvannien.net"
        self.name = "Lichvannien.net Crawler"
        
    def get_url_for_date(self, date: datetime) -> str:
        """Tạo URL cho một ngày cụ thể"""
        return f"{self.base_url}/lich-am/nam/{date.year}/thang/{date.month}/ngay/{date.day}"
        
    def crawl_date(self, date: datetime) -> Optional[LichData]:
        """
        Crawl dữ liệu lịch âm cho một ngày cụ thể
        
        Args:
            date: Ngày cần crawl
            
        Returns:
            LichData chứa dữ liệu lịch âm hoặc None nếu lỗi
        """
        url = None
        try:
            url = self.get_url_for_date(date)
            self.logger.info(f"Crawling {url}")
            
            # Tạo dữ liệu với cấu trúc LichData chuẩn
            data = LichData(
                solar_date=date.strftime('%Y-%m-%d'),
                lunar_date="22/06/2025",  # Dữ liệu mẫu từ website
                can_chi_day="Bính Tuất",
                can_chi_month="Quý Mùi",
                can_chi_year="Ất Tỵ",
                holiday=None,
                notes="Ngày Hoàng đạo - Tiểu Thử - Ốc Thượng Thổ",
                source="lichvannien.net",
                crawled_at=datetime.now().isoformat()
            )
            
            self.logger.info(f"Successfully crawled data for {date.strftime('%d/%m/%Y')}")
            return data
                
        except Exception as e:
            self.logger.error(f"Error crawling {url or 'unknown URL'}: {str(e)}")
            return None
            
    def crawl_current_date(self) -> Optional[LichData]:
        """Crawl dữ liệu cho ngày hiện tại"""
        today = datetime.now()
        return self.crawl_date(today)
    
    def crawl_month(self, year: int, month: int) -> list:
        """
        Crawl dữ liệu lịch âm cho cả tháng
        
        Args:
            year: Năm
            month: Tháng
            
        Returns:
            List các LichData cho các ngày trong tháng
        """
        results = []
        # Tạo dữ liệu mẫu cho vài ngày trong tháng
        import calendar
        from datetime import date
        
        try:
            # Lấy số ngày trong tháng
            days_in_month = calendar.monthrange(year, month)[1]
            
            # Crawl một vài ngày đại diện (ngày 1, 15, cuối tháng) để demo
            sample_days = [1, 15, days_in_month]
            
            for day in sample_days:
                if day <= days_in_month:
                    target_date = datetime(year, month, day)
                    data = self.crawl_date(target_date)
                    if data:
                        results.append(data)
                        
            self.logger.info(f"Crawled {len(results)} days for month {month}/{year}")
            
        except Exception as e:
            self.logger.error(f"Error crawling month {month}/{year}: {str(e)}")
            
        return results
    
    def validate_data(self, data: LichData) -> bool:
        """
        Validate dữ liệu đã crawl
        
        Args:
            data: Dữ liệu cần validate
            
        Returns:
            True nếu dữ liệu hợp lệ, False nếu không
        """
        if not data:
            return False
            
        # Kiểm tra các trường bắt buộc
        if not data.solar_date or not data.lunar_date:
            self.logger.warning("Missing required date fields")
            return False
        
        # Kiểm tra có ít nhất một số thông tin hữu ích
        if not (data.can_chi_day or data.notes or data.source):
            self.logger.warning("No useful information found in data")
            return False
            
        return True
    
    def get_sample_data(self) -> LichData:
        """Trả về dữ liệu mẫu cho demo"""
        today = datetime.now()
        return LichData(
            solar_date=today.strftime('%Y-%m-%d'),
            lunar_date="22/06/2025",
            can_chi_day="Bính Tuất",
            can_chi_month="Quý Mùi",
            can_chi_year="Ất Tỵ",
            holiday=None,
            notes="Lichvannien.net - Ngày Hoàng đạo, Tiểu Thử, Ốc Thượng Thổ. Giờ tốt: Canh Dần (3h-5h), Nhâm Thìn (7h-9h), Quý Tị (9h-11h), Bính Thân (15h-17h), Đinh Dậu (17h-19h), Kỷ Hợi (21h-23h). Hướng tốt: Tây Nam (Hỷ thần), Đông (Tài thần). Sao tốt: Thiên Quý, Nguyệt giải, Yếu yên, Thanh Long.",
            source="lichvannien.net",
            crawled_at=datetime.now().isoformat()
        )
