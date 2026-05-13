# 🏥 Quản Lý Hồ Sơ Bệnh Nhân — Patient Management System

Phần mềm Desktop quản lý hồ sơ bệnh nhân với giao diện trực quan, lịch sử khám bệnh, đơn thuốc và biểu đồ thống kê y tế.

> **Lưu ý**: Dự án tuân thủ kiến trúc **MVC (Model-View-Controller)** với **SQLite** database và **Tkinter** GUI.

## ✨ Tính năng
1. **CRUD Bệnh nhân**: Thêm, sửa, xóa, tìm kiếm với validation đầy đủ.
2. **Tính BMI tự động**: Nhập chiều cao + cân nặng → auto tính BMI + phân loại WHO.
3. **Lịch sử Khám bệnh**: Ghi nhận triệu chứng, chẩn đoán, huyết áp, nhiệt độ, bác sĩ.
4. **Quản lý Thuốc**: Tên thuốc, liều lượng, tần suất, ngày dùng.
5. **Import/Export CSV**: Nhập hàng loạt và xuất báo cáo.
6. **Biểu đồ Thống kê**: Phân bố giới tính, tuổi, BMI, top 10 bệnh phổ biến.
7. **CLI Mode**: Giao diện dòng lệnh cho môi trường terminal.

## 🚀 Hướng dẫn Cài đặt

### Cách 1: Dùng UV (Khuyến nghị)
```bash
# Cài uv (nếu chưa có)
pip install uv

# Đồng bộ môi trường
uv sync

# Chạy ứng dụng
uv run python main.py
```

### Cách 2: Dùng pip + venv
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Cách 3: Chạy script (Windows)
Nhấp đúp `setup_env.bat` → sau đó chạy `python main.py`.

## 📋 Sử dụng

### GUI (Mặc định)
```bash
python main.py
```

### CLI (Terminal)
```bash
python main.py --cli
```

### Seed dữ liệu mẫu (500 bệnh nhân)
```bash
uv add faker --dev   # hoặc pip install faker
python seed_patients.py
```

## 🧪 Chạy Tests
```bash
uv run python -m unittest discover -s tests -v
# hoặc
run_tests.bat
```

## 📦 Đóng gói .exe
```bash
python build.py
# hoặc
build.bat
```

## 📁 Cấu trúc Dự án
```
patient_management/
├── assets/              # Icon app
├── controllers/         # Layer Controller (GUI + CLI)
├── data/                # SQLite database (gitignore)
├── models/              # Layer Model (CRUD + DB)
├── templates/           # CSV template import
├── tests/               # Unit tests
├── utils/               # Utilities (BMI, validators, logger)
├── views/               # Layer View (Tkinter GUI + CLI)
├── main.py              # Entry point
├── pyproject.toml       # UV project config
└── requirements.txt     # Pip fallback
```

## 👥 Tác giả / Contributors
* Nhóm 1 — Lớp MT10A
