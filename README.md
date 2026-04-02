# Bot Crypto - Hướng Dẫn Bắt Đầu Nhanh

## Chạy Bot

```powershell
python main.py
```

Sau đó mở Telegram và bắt đầu trò chuyện với bot của bạn!

---

## Kiểm Tra Độ Chính Xác Dự Đoán (Không Cần Chờ!)

```powershell
python tests/backtest_predictions.py
```

**Kết quả:** 94.7% độ chính xác trung bình

---

## Tổ Chức Thư Mục

```
Ứng Dụng Bot
├── main.py ..................... Điểm vào bot
├── src/ ........................ Mã ứng dụng
│   ├── agents/           Quy trình công việc & phản hồi
│   ├── db/              Lớp cơ sở dữ liệu
│   ├── tools/           Dữ liệu thị trường & dự đoán
│   └── services/        Logic kinh doanh
│
Script & Kiểm Tra
├── scripts/ ...........  Thiết lập cơ sở dữ liệu
├── tests/ .............  Script kiểm tra & phân tích
│   ├── backtest_predictions.py ... Kiểm tra độ chính xác nhanh
│   ├── make_predictions_today.py . Tạo dự đoán
│   ├── compare_predictions.py .... Kiểm tra thời gian thực
│   └── test_*.py ................ Kiểm tra bot
│
Cấu Hình
├── requirements.txt ....... Các phụ thuộc Python
├── docker-compose.yml ..... Dịch vụ Docker
├── Dockerfile ............ Hình ảnh Docker
└── .env .................. Thông tin xác thực (Không commit)

Tài Liệu
└── docs/ ................ Tài liệu & hướng dẫn dự án
```

Xem [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md) để biết chi tiết.

---

## Script Kiểm Tra

### Kiểm Tra Độ Chính Xác Nhanh (30 giây)
```powershell
python tests/backtest_predictions.py
# Đầu ra: 94.7% độ chính xác (kiểm tra lịch sử 7 ngày)
```

### Độ Chính Xác Thời Gian Thực (1+ giờ)
```powershell
# Bước 1: Dự đoán
python tests/make_predictions_today.py

# Bước 2: Chờ 1-24 giờ

# Bước 3: So sánh
python tests/compare_predictions.py
```

### Thống Kê Cơ Sở Dữ Liệu
```powershell
python tests/check_messages_summary.py    # Số lượng tin nhắn
python tests/view_messages.py             # Xem tin nhắn
```

---

## Các Tính Năng Bot

- Dữ Liệu Thị Trường Thời Gian Thực - Tích hợp Binance API
- Dự Đoán Crypto - Học máy (94.7% chính xác!)
- Tạo Biểu Đồ - Giá cả, kỹ thuật, tổng quan thị trường
- Đa Ngôn Ngữ - 100% Giao Diện Việt Nam
- Lưu Trữ Tin Nhắn - Tính bền vững PostgreSQL (103+ tin nhắn)
- Đồng Bộ Telegram - Gửi biểu đồ ngay lập tức với chú thích

---

## Yêu Cầu Thiết Lập

- Python 3.10+
- PostgreSQL (đang chạy)
- Telegram Bot Token (trong `.env`)
- Khóa API Binance (trong `.env`)

---

## Current Performance

| Metric | Value |
|--------|-------|
| Accuracy (7-day) | **94.7%** |
| Stored Messages | **103+** |
| Test Coins | **10** |
| Response Language | **Vietnamese** |

