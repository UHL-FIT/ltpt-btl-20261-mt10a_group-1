# Software Architecture Document (SAD) - Quản Lý Hồ Sơ Bệnh Nhân

## 1. Giới thiệu
Kiến trúc phần mềm hệ thống Quản Lý Hồ Sơ Bệnh Nhân theo mô hình **MVC (Model-View-Controller)**.

---

## 2. Kiến trúc Tổng thể

### Model
* Giao tiếp SQLite thông qua module `db_manager.py`.
* Sử dụng **Pandas DataFrame** làm cấu trúc dữ liệu trung gian.
* Tính toán BMI bằng **Numpy Vectorization**.
* 3 bảng: `patients`, `examinations`, `medications`.

### View
* Giao diện GUI: **Tkinter** với sidebar navigation.
* 4 trang: Bệnh nhân (TreeView), Lịch sử khám, Thuốc, Thống kê (Matplotlib).
* Giao diện CLI: Terminal text-based.

### Controller
* `patient_controller.py`: Điều phối GUI — nhận events, validation, gọi Model, render View.
* `stats_controller.py`: Pandas groupby/agg cho thống kê.
* `cli_controller.py`: Điều phối CLI.

---

## 3. Cấu trúc Source Code
```text
patient_management/
├── assets/                  # Icon app
├── controllers/             # Layer Controller
│   ├── patient_controller.py
│   ├── stats_controller.py
│   └── cli_controller.py
├── data/                    # SQLite DB (gitignore)
├── models/                  # Layer Model
│   ├── db_manager.py        # Kết nối SQLite, init schema
│   ├── patient.py           # CRUD bệnh nhân + BMI
│   ├── examination.py       # CRUD lịch sử khám
│   └── medication.py        # CRUD thuốc
├── templates/               # CSV template import
├── tests/                   # Unit tests
├── utils/                   # Utilities
│   ├── bmi_calculator.py
│   ├── validators.py
│   └── logger.py
├── views/                   # Layer View
│   ├── main_window.py       # Cửa sổ chính + sidebar
│   ├── patient_view.py      # TreeView bệnh nhân
│   ├── patient_form.py      # Form thêm/sửa
│   ├── examination_view.py  # Tab lịch sử khám
│   ├── medication_view.py   # Tab thuốc
│   ├── stats_view.py        # Biểu đồ Matplotlib
│   └── cli_view.py          # CLI terminal
├── main.py                  # Entry point GUI
├── main_cli.py              # Entry point CLI
└── pyproject.toml           # UV project config
```

---

## 4. Công nghệ
* **Python 3.11+**, **SQLite**, **Pandas**, **Numpy**, **Matplotlib**, **Tkinter**
* **UV** để quản lý dependencies và đồng bộ môi trường dev.
* **PyInstaller** để đóng gói `.exe`.

---

## 5. Luồng dữ liệu — Ví dụ: Thêm Bệnh nhân
1. **View** (`patient_form.py`): User nhập form → click "Lưu".
2. **Controller** (`patient_controller.py`): Nhận dữ liệu, validate, gọi `patient_model.them_benh_nhan(data)`.
3. **Model** (`patient.py`): Sinh mã BN, INSERT vào SQLite, trả `(True, msg, ma_bn)`.
4. **Controller**: Hiển thị thông báo, gọi `_tai_du_lieu()` để reload TreeView.
5. **View** (`patient_view.py`): Xóa cũ, render lại bảng từ DataFrame mới.
