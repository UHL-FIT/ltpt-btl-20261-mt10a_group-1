"""
utils/validators.py
===================
Các hàm kiểm tra tính hợp lệ của dữ liệu nhập vào từ người dùng.
Đảm bảo dữ liệu đầu vào đúng format trước khi lưu vào database.
"""

import re
from datetime import datetime


def kiem_tra_tuoi(tuoi_str):
    """
    Kiểm tra giá trị tuổi có hợp lệ không.

    Args:
        tuoi_str (str): Chuỗi tuổi cần kiểm tra.

    Returns:
        tuple: (bool hợp lệ, int giá trị tuổi hoặc None nếu lỗi)
    """
    if not tuoi_str or not str(tuoi_str).strip():
        return False, None

    try:
        tuoi = int(str(tuoi_str).strip())
    except ValueError:
        return False, None

    if tuoi < 0 or tuoi > 150:
        return False, None

    return True, tuoi


def kiem_tra_sdt(sdt):
    """
    Kiểm tra số điện thoại có hợp lệ không.
    Chấp nhận chuỗi 10-11 chữ số, có thể bắt đầu bằng 0 hoặc +84.

    Args:
        sdt (str): Chuỗi số điện thoại cần kiểm tra.

    Returns:
        bool: True nếu hợp lệ, False nếu không hợp lệ.
    """
    if not sdt or not str(sdt).strip():
        return True  # SĐT không bắt buộc, trống cũng hợp lệ

    sdt = str(sdt).strip()

    # Cho phép bắt đầu bằng +84 hoặc 0, theo sau là 9-10 chữ số
    pattern = r"^(\+84|0)\d{9,10}$"
    return bool(re.match(pattern, sdt))


def kiem_tra_ngay(ngay_str, fmt="%d/%m/%Y"):
    """
    Kiểm tra chuỗi ngày tháng có đúng format hay không.

    Args:
        ngay_str (str): Chuỗi ngày cần kiểm tra (VD: '15/03/2024').
        fmt (str): Định dạng ngày (mặc định: dd/mm/yyyy).

    Returns:
        tuple: (bool hợp lệ, datetime object hoặc None nếu lỗi)
    """
    if not ngay_str or not str(ngay_str).strip():
        return True, None  # Ngày không bắt buộc, trống cũng hợp lệ

    ngay_str = str(ngay_str).strip()

    try:
        dt = datetime.strptime(ngay_str, fmt)
        return True, dt
    except ValueError:
        return False, None


def kiem_tra_huyet_ap(ha_str):
    """
    Kiểm tra chuỗi huyết áp có đúng format 'SYS/DIA' hay không.

    Args:
        ha_str (str): Chuỗi huyết áp (VD: '120/80').

    Returns:
        bool: True nếu hợp lệ, False nếu không hợp lệ.
    """
    if not ha_str or not str(ha_str).strip():
        return True  # Không bắt buộc

    ha_str = str(ha_str).strip()
    pattern = r"^\d{2,3}/\d{2,3}$"
    if not re.match(pattern, ha_str):
        return False

    parts = ha_str.split("/")
    sys_val = int(parts[0])
    dia_val = int(parts[1])

    # Giá trị huyết áp hợp lý: 50-300 / 30-200
    if sys_val < 50 or sys_val > 300:
        return False
    if dia_val < 30 or dia_val > 200:
        return False

    return True


def kiem_tra_nhiet_do(nhiet_do_str):
    """
    Kiểm tra nhiệt độ cơ thể có hợp lệ không.

    Args:
        nhiet_do_str (str): Chuỗi nhiệt độ cần kiểm tra.

    Returns:
        tuple: (bool hợp lệ, float giá trị hoặc None nếu lỗi)
    """
    if not nhiet_do_str or not str(nhiet_do_str).strip():
        return True, None  # Không bắt buộc

    try:
        nhiet_do = float(str(nhiet_do_str).strip())
    except ValueError:
        return False, None

    if nhiet_do < 30.0 or nhiet_do > 45.0:
        return False, None

    return True, nhiet_do


def kiem_tra_chieu_cao(chieu_cao_str):
    """
    Kiểm tra chiều cao (cm) có hợp lệ không.

    Args:
        chieu_cao_str (str): Chuỗi chiều cao cần kiểm tra.

    Returns:
        tuple: (bool hợp lệ, float giá trị hoặc None nếu lỗi)
    """
    if not chieu_cao_str or not str(chieu_cao_str).strip():
        return True, None

    try:
        chieu_cao = float(str(chieu_cao_str).strip())
    except ValueError:
        return False, None

    if chieu_cao < 20 or chieu_cao > 300:
        return False, None

    return True, chieu_cao


def kiem_tra_can_nang(can_nang_str):
    """
    Kiểm tra cân nặng (kg) có hợp lệ không.

    Args:
        can_nang_str (str): Chuỗi cân nặng cần kiểm tra.

    Returns:
        tuple: (bool hợp lệ, float giá trị hoặc None nếu lỗi)
    """
    if not can_nang_str or not str(can_nang_str).strip():
        return True, None

    try:
        can_nang = float(str(can_nang_str).strip())
    except ValueError:
        return False, None

    if can_nang < 0.5 or can_nang > 500:
        return False, None

    return True, can_nang
