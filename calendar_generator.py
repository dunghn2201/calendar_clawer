"""
Vietnamese Lunar Calendar Generator
Tạo dữ liệu lịch âm Việt Nam dựa trên thuật toán
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import calendar

class VietnameseLunarCalendar:
    """Generator cho lịch âm Việt Nam"""
    
    def __init__(self):
        # Dữ liệu can chi
        self.can = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
        self.chi = ["Tí", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
        
        # Ngày lễ cố định dương lịch
        self.solar_holidays = {
            "01-01": "Tết Dương lịch",
            "02-14": "Lễ tình nhân",
            "03-08": "Ngày Quốc tế Phụ nữ",
            "04-30": "Ngày Giải phóng miền Nam",
            "05-01": "Ngày Quốc tế Lao động", 
            "06-01": "Ngày Quốc tế Thiếu nhi",
            "09-02": "Ngày Quốc khánh",
            "10-20": "Ngày Phụ nữ Việt Nam",
            "11-20": "Ngày Nhà giáo Việt Nam",
            "12-25": "Lễ Giáng sinh"
        }
        
        # Ngày lễ âm lịch (tính gần đúng)
        self.lunar_holidays = {
            "01-01": "Tết Nguyên đán",
            "01-15": "Tết Nguyên tiêu",
            "03-03": "Tết Hàn thực",
            "04-15": "Phật đản",
            "05-05": "Tết Đoan ngọ",
            "07-15": "Vu lan",
            "08-15": "Tết Trung thu",
            "10-10": "Tết Thường tân",
            "12-23": "Ông Táo về trời"
        }
        
        # Giờ hoàng đạo cơ bản
        self.good_hours_by_day = {
            0: ["Tý (23h-1h)", "Dần (3h-5h)", "Thìn (7h-9h)", "Ngọ (11h-13h)"],  # Chủ nhật
            1: ["Sửu (1h-3h)", "Mão (5h-7h)", "Tỵ (9h-11h)", "Mùi (13h-15h)"],  # Thứ 2
            2: ["Tý (23h-1h)", "Dần (3h-5h)", "Thìn (7h-9h)", "Thân (15h-17h)"],  # Thứ 3  
            3: ["Sửu (1h-3h)", "Mão (5h-7h)", "Tỵ (9h-11h)", "Dậu (17h-19h)"],  # Thứ 4
            4: ["Tý (23h-1h)", "Dần (3h-5h)", "Thìn (7h-9h)", "Tuất (19h-21h)"], # Thứ 5
            5: ["Sửu (1h-3h)", "Mão (5h-7h)", "Tỵ (9h-11h)", "Hợi (21h-23h)"],  # Thứ 6
            6: ["Tý (23h-1h)", "Dần (3h-5h)", "Thìn (7h-9h)", "Ngọ (11h-13h)"]   # Thứ 7
        }
        
        # Hoạt động tốt/xấu theo ngày
        self.good_activities = [
            "Cưới hỏi", "Khai trương", "Khởi công", "Du lịch", "Ký hợp đồng",
            "Gặp gỡ đối tác", "Họp hành", "Học hành", "Cầu an", "Cúng tế",
            "Chuyển nhà", "Mua sắm", "Đầu tư", "Kinh doanh", "Xuất hành"
        ]
        
        self.bad_activities = [
            "Động thổ xấu", "Khai trương xấu", "Cưới hỏi xấu", "Du lịch xa",
            "Ký hợp đồng quan trọng", "Phẫu thuật", "Tranh tụng", "Kiện cáo"
        ]
    
    def get_can_chi_day(self, date):
        """Tính can chi của ngày (tính gần đúng)"""
        # Công thức đơn giản để tính can chi
        days_from_epoch = (date - datetime(1900, 1, 1)).days
        can_index = (days_from_epoch + 6) % 10  # Offset để align với lịch thực
        chi_index = (days_from_epoch + 8) % 12  # Offset để align với lịch thực
        return f"{self.can[can_index]} {self.chi[chi_index]}"
    
    def get_lunar_date(self, solar_date):
        """Tính ngày âm lịch (gần đúng)"""
        # Đây là thuật toán đơn giản, không chính xác 100%
        # Trong thực tế cần thuật toán phức tạp hơn
        year = solar_date.year
        month = solar_date.month
        day = solar_date.day
        
        # Offset gần đúng giữa âm và dương lịch
        lunar_offset = -30 if month <= 6 else -35
        
        # Tính ngày âm gần đúng
        total_days = day + lunar_offset
        if total_days <= 0:
            lunar_month = month - 1 if month > 1 else 12
            lunar_year = year if month > 1 else year - 1
            lunar_day = 30 + total_days
        else:
            lunar_month = month
            lunar_year = year
            lunar_day = total_days
        
        # Đảm bảo lunar_day trong khoảng hợp lệ
        lunar_day = max(1, min(30, lunar_day))
        
        return f"{lunar_day:02d}/{lunar_month:02d}/{lunar_year}"
    
    def get_feng_shui_info(self, date):
        """Lấy thông tin phong thủy cho ngày"""
        weekday = date.weekday()
        good_hours = self.good_hours_by_day[weekday]
        
        # Đánh giá ngày tốt/xấu dựa trên một số yếu tố
        day_score = (date.day + date.month + weekday) % 10
        is_good_day = day_score >= 5
        
        return {
            "good_hours": good_hours,
            "bad_hours": [],
            "is_good_day": is_good_day,
            "score": day_score * 10,
            "lucky_direction": "Đông Nam" if day_score >= 7 else "Tây Nam",
            "unlucky_direction": "Tây Bắc" if day_score < 5 else "Đông Bắc"
        }
    
    def get_activities(self, date, feng_shui_info):
        """Lấy hoạt động nên/không nên làm"""
        day_value = (date.day + date.month) % len(self.good_activities)
        
        if feng_shui_info["is_good_day"]:
            good_count = 3 + (day_value % 3)
            selected_good = [self.good_activities[(day_value + i) % len(self.good_activities)] 
                           for i in range(good_count)]
            selected_bad = [self.bad_activities[day_value % len(self.bad_activities)]]
        else:
            good_count = 1 + (day_value % 2)
            selected_good = [self.good_activities[(day_value + i) % len(self.good_activities)] 
                           for i in range(good_count)]
            bad_count = 2 + (day_value % 2)
            selected_bad = [self.bad_activities[(day_value + i) % len(self.bad_activities)] 
                          for i in range(bad_count)]
        
        return {
            "good_activities": selected_good,
            "bad_activities": selected_bad
        }
    
    def check_holiday(self, date):
        """Kiểm tra ngày lễ"""
        date_str = date.strftime("%m-%d")
        
        solar_holiday = self.solar_holidays.get(date_str)
        
        # Tính lunar holiday gần đúng (cần thuật toán chính xác hơn)
        lunar_date_str = self.get_lunar_date(date)
        lunar_md = lunar_date_str.split('/')[0] + "-" + lunar_date_str.split('/')[1]
        lunar_holiday = self.lunar_holidays.get(lunar_md)
        
        return {
            "solar": solar_holiday,
            "lunar": lunar_holiday
        }
    
    def generate_month_data(self, year, month):
        """Tạo dữ liệu cho một tháng"""
        days_in_month = calendar.monthrange(year, month)[1]
        month_data = {
            "year": year,
            "month": month,
            "total_days": days_in_month,
            "days": []
        }
        
        for day in range(1, days_in_month + 1):
            date = datetime(year, month, day)
            lunar_date = self.get_lunar_date(date)
            can_chi = self.get_can_chi_day(date)
            feng_shui = self.get_feng_shui_info(date)
            activities = self.get_activities(date, feng_shui)
            holidays = self.check_holiday(date)
            
            day_data = {
                "solar_date": date.strftime("%Y-%m-%d"),
                "lunar_date": lunar_date,
                "day_of_week": date.weekday() + 1,  # 1=Monday, 7=Sunday
                "can_chi": {
                    "day": can_chi,
                    "month": None,  # Cần thuật toán phức tạp hơn
                    "year": None
                },
                "feng_shui": {
                    "good_hours": feng_shui["good_hours"],
                    "bad_hours": feng_shui["bad_hours"],
                    "lucky_direction": feng_shui["lucky_direction"],
                    "unlucky_direction": feng_shui["unlucky_direction"]
                },
                "activities": {
                    "is_good_day": feng_shui["is_good_day"],
                    "good_activities": activities["good_activities"],
                    "bad_activities": activities["bad_activities"]
                },
                "holidays": holidays,
                "solar_term": None,  # Cần data 24 tiết khí
                "notes": f"Ngày {'tốt' if feng_shui['is_good_day'] else 'bình thường'}. Can chi: {can_chi}. Giờ hoàng đạo: {', '.join(feng_shui['good_hours'])}.",
                "metadata": {
                    "source": "vietnamese_lunar_generator",
                    "generated_at": datetime.now().isoformat()
                }
            }
            
            month_data["days"].append(day_data)
        
        return month_data

def generate_calendar_data():
    """Tạo dữ liệu lịch cho nhiều tháng"""
    generator = VietnameseLunarCalendar()
    
    # Tạo data cho 2024 (có nhiều tháng)
    months_to_generate = [
        (2024, 7), (2024, 8), (2024, 9), (2024, 10),
        (2024, 11), (2024, 12), (2025, 1), (2025, 2)
    ]
    
    for year, month in months_to_generate:
        print(f"🗓️ Generating calendar data for {year}-{month:02d}...")
        
        month_data = generator.generate_month_data(year, month)
        
        # Lưu file calendar
        calendar_file = f"data/api/calendar_{year}_{month:02d}.json"
        Path(calendar_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(calendar_file, 'w', encoding='utf-8') as f:
            json.dump(month_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {calendar_file}")
        
        # Tạo good days data
        good_days = [day for day in month_data["days"] if day["activities"]["is_good_day"]]
        good_days_file = f"data/api/good_days/{year}_{month:02d}.json"
        Path(good_days_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(good_days_file, 'w', encoding='utf-8') as f:
            json.dump(good_days, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Saved {good_days_file} with {len(good_days)} good days")
    
    # Tạo holidays data
    holidays_2024 = [
        {"name": "Tết Dương lịch", "date": "2024-01-01", "description": "Năm mới Dương lịch", "type": "national"},
        {"name": "Tết Nguyên đán", "date": "2024-02-10", "description": "Tết cổ truyền Việt Nam", "type": "traditional"},
        {"name": "Giỗ tổ Hùng Vương", "date": "2024-04-18", "description": "Ngày Giỗ tổ Hùng Vương", "type": "traditional"},
        {"name": "Ngày Giải phóng miền Nam", "date": "2024-04-30", "description": "Ngày thống nhất đất nước", "type": "national"},
        {"name": "Ngày Quốc tế Lao động", "date": "2024-05-01", "description": "Ngày Quốc tế Lao động", "type": "international"},
        {"name": "Ngày Quốc khánh", "date": "2024-09-02", "description": "Ngày Quốc khánh Việt Nam", "type": "national"},
        {"name": "Ngày Nhà giáo Việt Nam", "date": "2024-11-20", "description": "Ngày tôn vinh các nhà giáo", "type": "national"}
    ]
    
    holidays_file = "data/api/holidays/2024.json"
    Path(holidays_file).parent.mkdir(parents=True, exist_ok=True)
    
    with open(holidays_file, 'w', encoding='utf-8') as f:
        json.dump(holidays_2024, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved {holidays_file} with {len(holidays_2024)} holidays")
    
    print("\n🎉 Calendar data generation completed!")
    print("📁 Generated files:")
    print(f"  • Calendar data: {len(months_to_generate)} months")
    print(f"  • Good days data: {len(months_to_generate)} months") 
    print(f"  • Holidays data: 1 year")

if __name__ == "__main__":
    generate_calendar_data()
