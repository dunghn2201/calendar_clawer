"""
Xử lý và làm sạch dữ liệu lịch âm
Chuẩn hóa format, loại bỏ duplicate, validate dữ liệu
"""

import json
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import re
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LichDataProcessor:
    """Class xử lý và làm sạch dữ liệu lịch âm"""
    
    def __init__(self, input_file: Optional[str] = None):
        self.input_file = input_file
        self.df: Optional[pd.DataFrame] = None
        self.cleaned_data: List[Dict[str, Any]] = []
        
        if input_file and Path(input_file).exists():
            self.load_data()
    
    def load_data(self) -> None:
        """Load dữ liệu từ file JSON hoặc CSV"""
        try:
            if self.input_file.endswith('.json'):
                with open(self.input_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.df = pd.DataFrame(data)
            elif self.input_file.endswith('.csv'):
                self.df = pd.read_csv(self.input_file)
            else:
                raise ValueError("Chỉ hỗ trợ file JSON và CSV")
            
            logger.info(f"Đã load {len(self.df)} records từ {self.input_file}")
            
        except Exception as e:
            logger.error(f"Lỗi load dữ liệu: {e}")
            self.df = pd.DataFrame()
    
    def clean_solar_date(self, date_str: str) -> Optional[str]:
        """Chuẩn hóa ngày dương lịch về format YYYY-MM-DD"""
        if not date_str:
            return None
        
        try:
            # Đã đúng format
            if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                return date_str
            
            # Format DD/MM/YYYY
            if re.match(r'\d{1,2}/\d{1,2}/\d{4}', date_str):
                day, month, year = date_str.split('/')
                return f"{year}-{int(month):02d}-{int(day):02d}"
            
            # Format DD-MM-YYYY
            if re.match(r'\d{1,2}-\d{1,2}-\d{4}', date_str):
                day, month, year = date_str.split('-')
                return f"{year}-{int(month):02d}-{int(day):02d}"
            
            # Chỉ có số ngày (cần thêm thông tin tháng/năm)
            if date_str.isdigit() and 1 <= int(date_str) <= 31:
                return None  # Cần context để xử lý
            
        except Exception as e:
            logger.warning(f"Không thể parse ngày: {date_str} - {e}")
        
        return None
    
    def clean_lunar_date(self, lunar_str: str) -> Optional[str]:
        """Chuẩn hóa ngày âm lịch"""
        if not lunar_str:
            return None
        
        try:
            # Loại bỏ ký tự không cần thiết
            cleaned = re.sub(r'[^\d/]', '', lunar_str)
            
            # Format DD/MM hoặc DD/MM/YYYY
            if re.match(r'\d{1,2}/\d{1,2}(/\d{4})?', cleaned):
                return cleaned
            
            # Tách số
            numbers = re.findall(r'\d+', lunar_str)
            if len(numbers) >= 2:
                day, month = numbers[0], numbers[1]
                if len(numbers) >= 3:
                    year = numbers[2]
                    return f"{int(day):02d}/{int(month):02d}/{year}"
                else:
                    return f"{int(day):02d}/{int(month):02d}"
            
        except Exception as e:
            logger.warning(f"Không thể parse ngày âm: {lunar_str} - {e}")
        
        return lunar_str.strip() if lunar_str else None
    
    def clean_can_chi(self, can_chi_str: str) -> Optional[str]:
        """Chuẩn hóa can chi"""
        if not can_chi_str:
            return None
        
        # Danh sách can chi hợp lệ
        can = ['Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ', 'Canh', 'Tân', 'Nhâm', 'Quý']
        chi = ['Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi']
        
        cleaned = can_chi_str.strip()
        
        # Kiểm tra format hợp lệ
        for c in can:
            for ch in chi:
                if f"{c} {ch}" in cleaned or f"{c}{ch}" in cleaned:
                    return f"{c} {ch}"
        
        return cleaned if cleaned else None
    
    def validate_date(self, solar_date: str) -> bool:
        """Validate ngày dương lịch"""
        try:
            datetime.strptime(solar_date, "%Y-%m-%d")
            return True
        except:
            return False
    
    def clean_and_process(self) -> pd.DataFrame:
        """Làm sạch và xử lý toàn bộ dữ liệu"""
        if self.df is None or self.df.empty:
            logger.warning("Không có dữ liệu để xử lý")
            return pd.DataFrame()
        
        logger.info("Bắt đầu làm sạch dữ liệu...")
        
        # Copy dataframe
        cleaned_df = self.df.copy()
        
        # Làm sạch ngày dương lịch
        cleaned_df['solar_date'] = cleaned_df['solar_date'].astype(str).apply(self.clean_solar_date)
        
        # Loại bỏ records không có ngày dương lịch hợp lệ
        cleaned_df = cleaned_df.dropna(subset=['solar_date'])
        cleaned_df = cleaned_df[cleaned_df['solar_date'].apply(self.validate_date)]
        
        # Làm sạch ngày âm lịch
        if 'lunar_date' in cleaned_df.columns:
            cleaned_df['lunar_date'] = cleaned_df['lunar_date'].astype(str).apply(self.clean_lunar_date)
        
        # Làm sạch can chi
        if 'can_chi_day' in cleaned_df.columns:
            cleaned_df['can_chi_day'] = cleaned_df['can_chi_day'].astype(str).apply(self.clean_can_chi)
        
        # Loại bỏ duplicates (based on solar_date và source)
        before_dedup = len(cleaned_df)
        cleaned_df = cleaned_df.drop_duplicates(subset=['solar_date', 'source'], keep='first')
        after_dedup = len(cleaned_df)
        
        if before_dedup > after_dedup:
            logger.info(f"Đã loại bỏ {before_dedup - after_dedup} duplicates")
        
        # Sắp xếp theo ngày
        cleaned_df = cleaned_df.sort_values('solar_date')
        
        # Reset index
        cleaned_df = cleaned_df.reset_index(drop=True)
        
        # Thêm metadata
        cleaned_df['processed_at'] = datetime.now().isoformat()
        
        logger.info(f"Hoàn thành làm sạch: {len(cleaned_df)} records hợp lệ")
        
        self.df = cleaned_df
        return cleaned_df
    
    def get_statistics(self) -> Dict[str, Any]:
        """Thống kê dữ liệu"""
        if self.df is None or self.df.empty:
            return {}
        
        stats = {
            'total_records': len(self.df),
            'date_range': {
                'from': self.df['solar_date'].min(),
                'to': self.df['solar_date'].max()
            },
            'sources': self.df['source'].value_counts().to_dict() if 'source' in self.df.columns else {},
            'missing_data': {
                'lunar_date': self.df['lunar_date'].isna().sum() if 'lunar_date' in self.df.columns else 0,
                'can_chi_day': self.df['can_chi_day'].isna().sum() if 'can_chi_day' in self.df.columns else 0,
                'holiday': self.df['holiday'].isna().sum() if 'holiday' in self.df.columns else 0
            },
            'holidays_count': len(self.df[self.df['holiday'].notna()]) if 'holiday' in self.df.columns else 0
        }
        
        return stats
    
    def export_to_json(self, output_file: str) -> None:
        """Xuất dữ liệu ra JSON"""
        if self.df is None or self.df.empty:
            logger.warning("Không có dữ liệu để xuất")
            return
        
        # Chuyển NaN thành None
        data = self.df.where(pd.notna(self.df), None).to_dict('records')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Đã xuất {len(data)} records ra {output_file}")
    
    def export_to_sqlite(self, db_path: str) -> None:
        """Xuất dữ liệu ra SQLite"""
        if self.df is None or self.df.empty:
            logger.warning("Không có dữ liệu để xuất")
            return
        
        conn = sqlite3.connect(db_path)
        
        # Tạo bảng với indexes
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lich_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                solar_date TEXT NOT NULL,
                lunar_date TEXT,
                can_chi_day TEXT,
                can_chi_month TEXT,
                can_chi_year TEXT,
                holiday TEXT,
                notes TEXT,
                source TEXT,
                crawled_at TEXT,
                processed_at TEXT,
                UNIQUE(solar_date, source)
            )
        ''')
        
        # Tạo indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_solar_date ON lich_data(solar_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON lich_data(source)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_holiday ON lich_data(holiday)')
        
        # Insert dữ liệu
        self.df.to_sql('lich_data', conn, if_exists='replace', index=False)
        
        conn.commit()
        conn.close()
        
        logger.info(f"Đã xuất {len(self.df)} records ra SQLite database: {db_path}")
    
    def export_to_csv(self, output_file: str) -> None:
        """Xuất dữ liệu ra CSV"""
        if self.df is None or self.df.empty:
            logger.warning("Không có dữ liệu để xuất")
            return
        
        self.df.to_csv(output_file, index=False, encoding='utf-8-sig')
        logger.info(f"Đã xuất {len(self.df)} records ra {output_file}")

# Chạy thử nghiệm
if __name__ == "__main__":
    # Tạo dữ liệu test
    test_data = [
        {
            "solar_date": "2024-01-01",
            "lunar_date": "20/11/2023",
            "can_chi_day": "Giáp Thìn",
            "holiday": "Tết Dương lịch",
            "source": "test"
        },
        {
            "solar_date": "1/1/2024",  # Format khác
            "lunar_date": "20-11",
            "can_chi_day": "Giáp Thìn",
            "holiday": "",
            "source": "test"
        }
    ]
    
    # Lưu test data
    with open('test_data.json', 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
    
    # Test processor
    processor = LichDataProcessor('test_data.json')
    cleaned = processor.clean_and_process()
    
    print("🧹 Cleaned data:")
    print(cleaned)
    
    print("\n📊 Statistics:")
    stats = processor.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Export các format
    processor.export_to_json('cleaned_data.json')
    processor.export_to_sqlite('test_database.db')
    processor.export_to_csv('cleaned_data.csv')
    
    print("✅ Export hoàn thành!")
