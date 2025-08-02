# 🗓️ Lich Crawler - Vietnamese Lunar Calendar Data Scraper

Một công cụ Python hiện đại để crawl dữ liệu lịch âm từ các trang web Việt Nam.

## � TÌNH TRẠNG DỰ ÁN

**Cập nhật: 16/07/2025**

Hiện tại dự án đang trong giai đoạn tái cấu trúc do các vấn đề sau:

### ❌ Vấn đề với các crawler hiện tại:
- **lichviet.app**: Trả về 404, có thể đã thay đổi URL structure
- **lichvn.net**: 404 error cho các URL calendar
- **tuvi.vn**: Không tìm thấy calendar data trong response
- **Các trang khác**: Phần lớn không khả dụng hoặc đã thay đổi cấu trúc

### ✅ Giải pháp đang triển khai:
- **Improved Generic Crawler**: Crawler thông minh có thể tự động tìm kiếm API và trang web hoạt động
- **Hybrid Data Generator**: Tạo dữ liệu cơ bản khi không tìm thấy nguồn online
- **Multiple Fallback Strategy**: Thử nhiều nguồn dữ liệu khác nhau

### 🔄 Tình trạng hiện tại:
- ✅ **Generic Crawler**: Hoạt động, tạo dữ liệu cơ bản
- ✅ **Improved Crawler**: Hoạt động, có hybrid data với lunar info
- ⚠️ **Legacy Crawlers**: Tạm ngưng hoạt động
- ❌ **Demo Crawlers**: Đã loại bỏ vì làm nhiễu dữ liệu

---

## 📋 Tính năng

- ✅ **Intelligent Crawler**: Tự động tìm kiếm các nguồn dữ liệu khả dụng
- ✅ **Multiple Fallback**: Thử API → Website → Hybrid Generator
- ✅ **Hybrid Data Generation**: Tạo dữ liệu cơ bản khi cần
- ✅ Lưu dữ liệu đa định dạng (JSON, SQLite, CSV)
- ✅ Xử lý lỗi thông minh
- ✅ Rate limiting để tôn trọng server

## 🎯 Các nguồn dữ liệu

### Crawlers Hoạt động
- **Improved Generic Crawler** - Crawler thông minh với khả năng tự động tìm kiếm nguồn
- **Hybrid Data Generator** - Tạo dữ liệu cơ bản với thông tin lunar và can chi

### Crawlers Legacy (Tạm ngưng)
- [lichviet.app](https://lichviet.app/) - ❌ 404 Error
- [tuvi.vn](https://tuvi.vn/) - ❌ Không có calendar data  
- [lichvn.net](https://lichvn.net/) - ❌ 404 Error
- [lichvannien.net](https://lichvannien.net/) - ❌ 404 Error
- [lichngaytot.com](https://lichngaytot.com/) - ❌ 404 Error
- [licham365.vn](https://licham365.vn/) - ❌ 404 Error
- [lichvannien365.com](https://lichvannien365.com/) - ❌ Không có calendar data

## 🚀 Cài đặt nhanh

```bash
# Clone và setup
git clone <your-repo>
cd lich-crawler

# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# hoặc
venv\Scripts\activate     # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Cài đặt browser cho Playwright
playwright install chromium
```

## 💻 Sử dụng

### Crawler mới (Khuyến nghị)
```python
from crawlers.improved_crawler import ImprovedCalendarCrawler

# Tạo crawler thông minh
crawler = ImprovedCalendarCrawler()

# Crawl dữ liệu năm 2025 (tự động tìm nguồn tốt nhất)
data = crawler.crawl_month(2025, 7)

# Lưu kết quả
crawler.save_to_json("lich_2025_07.json")
```

### Crawler legacy (Không khuyến nghị - chỉ để tham khảo)
```python
from crawlers.lichviet_crawler import LichVietCrawler

# ⚠️ Có thể không hoạt động do các trang web đã thay đổi
crawler = LichVietCrawler()
data = crawler.crawl_year(2024)  # Có thể trả về dữ liệu trống
```

### Crawl tự động
```python
from scheduler.auto_crawler import AutoCrawler

# Chạy crawl tự động hàng ngày
auto_crawler = AutoCrawler()
auto_crawler.start_daily_crawl()
```

### Xử lý dữ liệu
```python
from processors.data_processor import LichDataProcessor

processor = LichDataProcessor("lich_2024.json")
cleaned_data = processor.clean_and_process()
processor.export_to_sqlite("lich_database.db")
```

## 📁 Cấu trúc dự án

```
lich-crawler/
├── crawlers/           # Các crawler cho từng trang web
├── processors/         # Xử lý và làm sạch dữ liệu
├── scheduler/          # Tự động hóa crawl
├── config/            # Cấu hình và settings
├── data/              # Dữ liệu đã crawl
├── logs/              # Log files
└── tests/             # Unit tests
```

## ⚙️ Cấu hình

Chỉnh sửa `config/settings.py` để tùy chỉnh:

```python
# Cấu hình crawl
CRAWL_DELAY = 1  # Giây nghỉ giữa các request
MAX_RETRIES = 3  # Số lần retry khi lỗi
USER_AGENT = "Lich Crawler Bot 1.0"

# Cấu hình database
DATABASE_PATH = "data/lich_database.db"
JSON_OUTPUT_DIR = "data/json/"
```

## 🔧 Development

```bash
# Chạy tests
python -m pytest tests/

# Chạy crawler đơn lẻ
python -m crawlers.lichviet_crawler

# Chạy scheduler
python -m scheduler.auto_crawler

# Format code
black .
isort .
```

## 📊 Output Data Format

```json
{
  "solar_date": "2024-01-15",
  "lunar_date": "05/12/2023",
  "can_chi_day": "Giáp Thìn",
  "can_chi_month": "Ất Sửu", 
  "can_chi_year": "Quý Mão",
  "holiday": "Tết Dương lịch",
  "notes": "Ngày tốt",
  "source": "lichviet.app"
}
```

## 🤝 Đóng góp

1. Fork project
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🙏 Acknowledgments

- [lichviet.app](https://lichviet.app/) - Nguồn dữ liệu lịch âm
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML parsing
- [Playwright](https://playwright.dev/) - Browser automation
