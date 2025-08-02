# 📊 Data Directory Structure

## 📁 Cấu trúc thư mục

```
data/
├── sources/              # Dữ liệu thô từ từng website
│   ├── demo/            # Demo data for testing
│   ├── lichviet/        # Data từ lichviet.app
│   ├── lichvn/          # Data từ lichvn.net  
│   ├── tuvi/            # Data từ tuvi.vn
│   ├── lichvannien/     # Data từ lichvannien.net
│   ├── lichngaytot/     # Data từ lichngaytot.com
│   ├── licham365/       # Data từ licham365.vn
│   └── lichvannien365/  # Data từ lichvannien365.com
├── processed/           # Dữ liệu đã xử lý và chuẩn hóa
├── merged/             # Dữ liệu đã ghép từ nhiều nguồn  
├── backup/             # Backup dữ liệu cũ
└── temp/               # Files tạm thời
```

## 📝 Quy tắc đặt tên file

Format: `{source}_{date_range}_{data_type}_{timestamp}.json`

- **source**: Tên nguồn (demo, lichviet, lichvn, ...)
- **date_range**: Khoảng thời gian (YYYY-MM-DD hoặc YYYY-MM)  
- **data_type**: Loại dữ liệu (raw, processed, merged)
- **timestamp**: Thời gian tạo file (YYYYMMDD_HHMMSS)

## 📋 Ví dụ tên file

- `lichviet_2024-07-16_raw_20250716_210652.json`
- `lichvn_2024-07_processed_20250716_210652.json`  
- `merged_2024-07-16_merged_20250716_210652.json`

## 🏷️ Mapping nguồn dữ liệu

| Website | Thư mục | Mô tả |
|---------|---------|-------|
| demo_data | demo | Dữ liệu demo cho test |
| lichviet.app | lichviet | Lịch Việt |
| lichvn.net | lichvn | Lịch VN |
| tuvi.vn | tuvi | Tử vi |
| lichvannien.net | lichvannien | Lịch Vạn Niên |
| lichngaytot.com | lichngaytot | Lịch Ngày Tốt |
| licham365.vn | licham365 | Lịch Âm 365 |
| lichvannien365.com | lichvannien365 | Lịch Vạn Niên 365 |
