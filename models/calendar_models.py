"""
Models cho dữ liệu lịch - chuẩn hóa cho Android app
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

@dataclass
class CalendarDay:
    """Model chuẩn cho một ngày trong lịch"""
    
    # Thông tin cơ bản
    solar_date: str          # Ngày dương lịch (YYYY-MM-DD)
    lunar_date: str          # Ngày âm lịch (DD/MM)
    day_of_week: int         # Thứ trong tuần (1=CN, 2=T2, ..., 7=T7)
    
    # Can Chi
    can_chi_day: Optional[str] = None     # Can chi ngày
    can_chi_month: Optional[str] = None   # Can chi tháng
    can_chi_year: Optional[str] = None    # Can chi năm
    
    # Thông tin phong thủy
    good_hours: Optional[List[str]] = None    # Giờ hoàng đạo
    bad_hours: Optional[List[str]] = None     # Giờ hắc đạo
    lucky_direction: Optional[str] = None     # Hướng may mắn
    unlucky_direction: Optional[str] = None   # Hướng xấu
    
    # Ngày tốt xấu
    is_good_day: Optional[bool] = None        # Ngày tốt/xấu
    good_activities: Optional[List[str]] = None   # Việc nên làm
    bad_activities: Optional[List[str]] = None    # Việc không nên làm
    
    # Lễ tết
    solar_holiday: Optional[str] = None       # Lễ dương lịch
    lunar_holiday: Optional[str] = None       # Lễ âm lịch
    
    # Tiết khí
    solar_term: Optional[str] = None          # Tiết khí 24 mùa
    
    # Thông tin bổ sung
    notes: Optional[str] = None               # Ghi chú
    source: str = "unknown"                   # Nguồn dữ liệu
    crawled_at: Optional[str] = None          # Thời gian crawl
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "solar_date": self.solar_date,
            "lunar_date": self.lunar_date,
            "day_of_week": self.day_of_week,
            "can_chi": {
                "day": self.can_chi_day,
                "month": self.can_chi_month,
                "year": self.can_chi_year
            },
            "feng_shui": {
                "good_hours": self.good_hours or [],
                "bad_hours": self.bad_hours or [],
                "lucky_direction": self.lucky_direction,
                "unlucky_direction": self.unlucky_direction
            },
            "activities": {
                "is_good_day": self.is_good_day,
                "good_activities": self.good_activities or [],
                "bad_activities": self.bad_activities or []
            },
            "holidays": {
                "solar": self.solar_holiday,
                "lunar": self.lunar_holiday
            },
            "solar_term": self.solar_term,
            "notes": self.notes,
            "metadata": {
                "source": self.source,
                "crawled_at": self.crawled_at
            }
        }
    
    @classmethod
    def from_raw_data(cls, raw_data: Dict[str, Any]) -> 'CalendarDay':
        """Tạo CalendarDay từ raw data"""
        
        # Parse solar date để lấy day_of_week
        try:
            date_obj = datetime.strptime(raw_data.get('solar_date', ''), '%Y-%m-%d')
            day_of_week = date_obj.isoweekday() % 7 + 1  # Convert to 1=CN format
        except:
            day_of_week = 1
        
        # Parse good hours từ notes nếu có
        good_hours = []
        bad_hours = []
        notes = raw_data.get('notes', '') or ''
        
        if 'giờ hoàng đạo' in notes.lower():
            # Extract hours from notes
            import re
            hour_pattern = r'(\w+)\((\d+h-\d+h)\)'
            matches = re.findall(hour_pattern, notes)
            good_hours = [f"{match[0]} ({match[1]})" for match in matches]
        
        # Determine if good day from holiday field
        holiday = raw_data.get('holiday', '')
        is_good_day = None
        if holiday:
            if 'hoàng đạo' in holiday.lower() or 'tốt' in holiday.lower():
                is_good_day = True
            elif 'hắc đạo' in holiday.lower() or 'xấu' in holiday.lower():
                is_good_day = False
        
        return cls(
            solar_date=raw_data.get('solar_date', ''),
            lunar_date=raw_data.get('lunar_date', ''),
            day_of_week=day_of_week,
            can_chi_day=raw_data.get('can_chi_day'),
            can_chi_month=raw_data.get('can_chi_month'),
            can_chi_year=raw_data.get('can_chi_year'),
            good_hours=good_hours,
            bad_hours=bad_hours,
            is_good_day=is_good_day,
            solar_holiday=holiday if holiday and 'hoàng đạo' not in holiday.lower() else None,
            notes=notes,
            source=raw_data.get('source', 'unknown'),
            crawled_at=raw_data.get('crawled_at')
        )

@dataclass 
class MonthlyCalendar:
    """Model cho dữ liệu lịch theo tháng"""
    
    year: int
    month: int
    days: List[CalendarDay]
    total_days: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "year": self.year,
            "month": self.month,
            "total_days": self.total_days,
            "days": [day.to_dict() for day in self.days],
            "summary": {
                "good_days": len([d for d in self.days if d.is_good_day is True]),
                "bad_days": len([d for d in self.days if d.is_good_day is False]),
                "holidays": len([d for d in self.days if d.solar_holiday or d.lunar_holiday]),
                "sources": list(set(d.source for d in self.days))
            }
        }

class DataNormalizer:
    """Chuẩn hóa dữ liệu từ các nguồn khác nhau"""
    
    @staticmethod
    def normalize_lunar_date(lunar_date: str) -> str:
        """Chuẩn hóa format ngày âm lịch về DD/MM"""
        if not lunar_date:
            return ""
        
        # Remove extra text and normalize
        lunar_date = lunar_date.strip()
        
        # Handle different formats
        if '/' in lunar_date:
            parts = lunar_date.split('/')
            if len(parts) >= 2:
                day = parts[0].strip().zfill(2)
                month = parts[1].strip().zfill(2)
                return f"{day}/{month}"
        
        return lunar_date
    
    @staticmethod
    def normalize_can_chi(can_chi: str) -> str:
        """Chuẩn hóa can chi"""
        if not can_chi:
            return ""
        
        # Remove extra spaces and normalize
        return can_chi.strip().title()
    
    @staticmethod
    def extract_activities(notes: str) -> tuple:
        """Trích xuất việc nên làm và không nên làm từ notes"""
        if not notes:
            return [], []
        
        good_activities = []
        bad_activities = []
        
        # Simple keyword extraction
        notes_lower = notes.lower()
        
        # Good activities keywords
        good_keywords = ['tốt', 'nên', 'thích hợp', 'may mắn', 'xuất hành', 'khai trương']
        for keyword in good_keywords:
            if keyword in notes_lower:
                # Extract sentence containing keyword
                sentences = notes.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        good_activities.append(sentence.strip())
                        break
        
        # Bad activities keywords  
        bad_keywords = ['không nên', 'tránh', 'xấu', 'hung', 'kiêng']
        for keyword in bad_keywords:
            if keyword in notes_lower:
                sentences = notes.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        bad_activities.append(sentence.strip())
                        break
        
        return good_activities, bad_activities
