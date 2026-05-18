# 🏥 Hệ Thống Quản Lý Hồ Sơ Bệnh Nhân

> **Phiên bản:** alpha 0.2  
> **Kiến trúc:** MVC (Model – View – Controller)  
> **Môn học:** Lập Trình Python Thực Tế – Bài Tập Lớn 2026.1  
> **Nhóm:** MT10A – Group 1

Phần mềm desktop hỗ trợ bác sĩ / nhân viên y tế **lưu trữ, tìm kiếm, quản lý và thống kê** hồ sơ bệnh nhân một cách nhanh chóng và trực quan.

---

## 📋 Mục Lục

- [Tính Năng Chính](#-tính-năng-chính)
- [Ảnh Chụp Màn Hình](#-ảnh-chụp-màn-hình)
- [Kiến Trúc Dự Án](#-kiến-trúc-dự-án)
- [Cấu Trúc Thư Mục](#-cấu-trúc-thư-mục)
- [Yêu Cầu Hệ Thống](#-yêu-cầu-hệ-thống)
- [Cài Đặt & Chạy](#-cài-đặt--chạy)
- [Hướng Dẫn Sử Dụng](#-hướng-dẫn-sử-dụng)
- [Công Nghệ Sử Dụng](#-công-nghệ-sử-dụng)
- [Thành Viên Nhóm](#-thành-viên-nhóm)

---

## ✨ Tính Năng Chính

### 📁 Quản Lý Hồ Sơ Bệnh Nhân
- **Thêm / Sửa / Xóa** hồ sơ bệnh nhân (CRUD đầy đủ)
- **Tìm kiếm** theo tên hoặc số điện thoại (hỗ trợ **tìm không dấu** tiếng Việt)
- **Xem chi tiết** hồ sơ qua cửa sổ popup (nháy đúp)
- **Xuất danh sách** ra file CSV

### 📊 Thống Kê & Báo Cáo
- Tổng quan số hồ sơ, bệnh nhân hôm nay
- **Biểu đồ tròn** tỉ lệ giới tính
- **Biểu đồ ngang** Top 5 bệnh lý phổ biến
- Xuất biểu đồ ra file **PNG**

### 📅 Lịch Tái Khám
- Đặt lịch tái khám cho bệnh nhân với nút tắt nhanh (+1 tuần, +1 tháng, +3 tháng)
- Tra cứu nhanh tên bệnh nhân theo ID
- Theo dõi trạng thái: **Quá hạn** ⚠️ / **Hôm nay** 🔔 / **Chờ khám** ✓
- Dashboard tóm tắt tổng quan lịch hẹn

### 🎨 Giao Diện
- Hỗ trợ **4 chế độ theme**: Sáng ☀️ / Tối 🌙 / Theo hệ thống 💻 / Theo thời gian 🕐
- Tự động phát hiện Dark Mode của hệ điều hành (Windows, macOS, Linux)
- Biểu đồ tự động đổi màu theo theme

### 💾 Sao Lưu & Phục Hồi
- **Export** (sao lưu) toàn bộ database ra file `.db`
- **Import** (phục hồi) database từ file `.db` đã sao lưu

---

## 🏗 Kiến Trúc Dự Án

Dự án tuân theo mô hình **MVC (Model – View – Controller)** rõ ràng:

```
┌──────────────┐     callback     ┌──────────────────┐     CRUD / Query     ┌─────────────┐
│     VIEW     │ ──────────────▶ │    CONTROLLER    │ ──────────────────▶  │    MODEL    │
│  (Tkinter)   │ ◀────────────── │  (Business Logic)│ ◀──────────────────  │  (SQLite)   │
│              │   update UI      │                  │   return data        │             │
└──────────────┘                  └──────────────────┘                      └─────────────┘
```

| Tầng | Trách nhiệm | Không biết về |
|------|-------------|---------------|
| **Model** | Truy vấn SQLite, CRUD, thống kê | Giao diện (Tkinter) |
| **View** | Vẽ giao diện, nhận sự kiện người dùng | Database, SQL |
| **Controller** | Logic nghiệp vụ, validate, điều phối Model ↔ View | SQL, widget cụ thể |

---

## 📂 Cấu Trúc Thư Mục

```
ltpt-btl-20261-mt10a_group-1/
├── main.py                      # Entry point – lắp ráp MVC rồi chạy
├── pyproject.toml               # Cấu hình project & dependencies (uv)
├── uv.lock                      # Lock file cho uv
├── .python-version              # Python 3.14
├── .gitignore
├── README.md
├── patients_data.db             # SQLite database (tự tạo khi chạy)
├── clear_cache.py               # Script dọn cache __pycache__
│
├── models/
│   ├── __init__.py
│   └── patient_model.py         # Model – CRUD bệnh nhân, lịch tái khám, thống kê
│
├── views/
│   ├── __init__.py
│   ├── manage_view.py           # View Tab 1 – Quản lý bệnh nhân
│   ├── stats_view.py            # View Tab 2 – Thống kê & biểu đồ (Matplotlib)
│   └── follow_up_view.py        # View Tab 3 – Lịch tái khám
│
├── controllers/
│   ├── __init__.py
│   └── patient_controller.py    # Controller – cầu nối Model ↔ View
│
└── utils/
    ├── __init__.py
    ├── helpers.py               # Hàm tiện ích (bỏ dấu tiếng Việt)
    └── theme_manager.py         # Quản lý theme sáng/tối/hệ thống/thời gian
```

---

## 💻 Yêu Cầu Hệ Thống

| Yêu cầu | Phiên bản |
|----------|-----------|
| Python | ≥ 3.14 |
| Hệ điều hành | Windows / macOS / Linux |
| Tkinter | Đi kèm Python (built-in) |

### Thư viện bên thứ ba

| Thư viện | Phiên bản | Mục đích |
|----------|-----------|----------|
| `matplotlib` | ≥ 3.10.9 | Vẽ biểu đồ thống kê |
| `numpy` | ≥ 2.4.5 | Hỗ trợ tính toán cho Matplotlib |
| `pandas` | ≥ 3.0.3 | Xử lý dữ liệu |

---

## 🚀 Cài Đặt & Chạy

### Cách 1: Sử dụng `uv` (khuyến nghị)

```bash
# 1. Cài uv (nếu chưa có)
pip install uv

# 2. Clone repository
git clone https://github.com/UHL-FIT/ltpt-btl-20261-mt10a_group-1.git
cd ltpt-btl-20261-mt10a_group-1

# 3. Cài đặt dependencies
uv sync

# 4. Chạy ứng dụng
uv run main.py
```

### Cách 2: Sử dụng `pip` truyền thống

```bash
# 1. Clone repository
git clone https://github.com/UHL-FIT/ltpt-btl-20261-mt10a_group-1.git
cd ltpt-btl-20261-mt10a_group-1

# 2. Tạo môi trường ảo
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Cài đặt dependencies
pip install matplotlib numpy pandas

# 4. Chạy ứng dụng
python main.py
```

> **Lưu ý:** Khi chạy lần đầu, file `patients_data.db` sẽ được tự động tạo trong thư mục gốc của project.

---

## 📖 Hướng Dẫn Sử Dụng

### Tab 1 – Quản Lý Bệnh Nhân

1. **Thêm hồ sơ:** Điền thông tin vào form bên trái → nhấn **"Lưu Hồ Sơ"**
2. **Sửa hồ sơ:** Chọn dòng trong bảng → nhấn **"Sửa Hồ Sơ Đã Chọn"** → chỉnh sửa → **"Lưu Hồ Sơ"**
3. **Xóa hồ sơ:** Chọn dòng → nhấn **"Xóa Hồ Sơ Đã Chọn"**
4. **Tìm kiếm:** Gõ tên hoặc SĐT vào ô tìm kiếm → nhấn **"Tìm"** hoặc Enter
5. **Xem chi tiết:** Nháy đúp vào một dòng trong bảng
6. **Xuất CSV:** Nhấn **"Xuất ra CSV"** trên thanh công cụ

### Tab 2 – Thống Kê & Báo Cáo

- Chuyển sang tab này để xem biểu đồ tự động cập nhật
- Nhấn **"Làm mới dữ liệu"** để tải lại
- Nhấn **"Xuất biểu đồ PNG"** để lưu ảnh biểu đồ

### Tab 3 – Lịch Tái Khám

1. Nhập **ID bệnh nhân** → nhấn **"Tra cứu"** để xác nhận
2. Chọn ngày tái khám (nhập tay hoặc dùng nút tắt nhanh)
3. Nhập lí do và chọn định kì → nhấn **"💾 Lưu Lịch"**
4. Xóa lịch: chọn dòng → nhấn **"🗑 Xóa Lịch Đã Chọn"** hoặc nháy đúp

### Menu Hệ Thống

- **Hệ Thống → Nhập Database:** Phục hồi dữ liệu từ file `.db` đã sao lưu
- **Hệ Thống → Sao lưu Database:** Tạo bản sao lưu database hiện tại
- **🎨 Giao Diện:** Chuyển đổi giữa 4 chế độ theme
- **Trợ Giúp → Giới thiệu:** Xem thông tin phần mềm

---

## 🛠 Công Nghệ Sử Dụng

| Công nghệ | Vai trò |
|-----------|---------|
| **Python 3.14** | Ngôn ngữ chính |
| **Tkinter + ttk** | Giao diện người dùng (GUI) |
| **SQLite3** | Cơ sở dữ liệu nhúng |
| **Matplotlib** | Vẽ biểu đồ thống kê |
| **uv** | Quản lý dependencies & môi trường ảo |


## 📄 Giấy Phép

Dự án này được phát triển phục vụ mục đích học tập tại **UHL-FIT**.

---

<p align="center">
  Made with ❤️ by MT10A – Group 1
</p>
