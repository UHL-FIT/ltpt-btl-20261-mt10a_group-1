# Mã nguồn chuẩn (Coding Conventions)

Dự án `Quản lý Hồ sơ Bệnh nhân` hướng đến độ ổn định, khả năng bảo trì và có thể bàn giao thương mại. Mọi đoạn code phải tuân thủ các tiêu chuẩn sau:

## 1. Naming Conventions (Quy chuẩn Đặt tên)
Áp dụng tiêu chuẩn **PEP 8**:
- **Biến và Hàm**: `snake_case`. (VD: `lay_danh_sach()`, `tong_bn`)
- **Hằng số**: `UPPER_SNAKE_CASE`. (VD: `DB_PATH`, `COLOR_PRIMARY`)
- **Lớp**: `PascalCase`. (VD: `Patient`, `Examination`)

## 2. Quản lý Phiên bản (Versioning)
Sử dụng **Semantic Versioning** `v[MAJOR].[MINOR].[PATCH]`:
- **MAJOR**: Thay đổi cấu trúc DB hoặc luồng lớn.
- **MINOR**: Thêm tính năng mới.
- **PATCH**: Vá lỗi, chỉnh sửa UI nhỏ.
- Phiên bản hiện tại: `__version__ = "1.0.0"` tại `main.py`.

## 3. Khối Chú thích (Docstrings)
Mọi hàm, module bắt buộc phải có Docstring theo **Google Python Style Guide**:
```python
def them_benh_nhan(data):
    """
    Thêm bệnh nhân mới vào database.

    Args:
        data (dict): Thông tin bệnh nhân (ho_ten, tuoi, gioi_tinh, ...).

    Returns:
        tuple: (bool Trạng thái, str Thông báo, str Mã BN mới)
    """
```

## 4. Hệ thống Vết (Logging)
Sử dụng module `utils/logger.py` thay vì `print()`:
- `logger.debug()`: Chi tiết xử lý nội bộ.
- `logger.info()`: Ghi VẾT thao tác user: Thêm/Sửa/Xóa/Tìm kiếm.
- `logger.warning()`: Lỗi logic nhỏ, cảnh báo.
- `logger.error()`: Bắt buộc trong mọi `try...except`.

## 5. Quản lý Dependencies (UV Sync)
- Sử dụng `uv` để quản lý dependencies qua `pyproject.toml`.
- Dev đồng bộ môi trường bằng lệnh: `uv sync`.
- Fallback: `pip install -r requirements.txt`.
