"""
utils/logger.py
===============
Cấu hình logging cho toàn bộ ứng dụng Quản lý Hồ sơ Bệnh nhân.
Ghi log ra file (data/app.log) và hiển thị trên console (WARNING trở lên).
"""

import os
import sys
import logging

if getattr(sys, 'frozen', False):
    # Khi cài vào Program Files không có quyền ghi, dùng thư mục User
    _BASE_DIR = os.path.join(os.path.expanduser("~"), "PatientManagement_Data")
else:
    _BASE_DIR = os.path.dirname(os.path.dirname(__file__))

_LOG_DIR = os.path.join(_BASE_DIR, "data")
_LOG_FILE = os.path.join(_LOG_DIR, "app.log")


def setup_logger(name="patient_mgmt"):
    """
    Tạo và trả về logger.

    Args:
        name (str): Tên logger. Mặc định là 'patient_mgmt'.

    Returns:
        logging.Logger: Logger đã được cấu hình sẵn.

    Notes:
        - File handler: ghi TẤT CẢ log (DEBUG trở lên) vào data/app.log
        - Console handler: chỉ hiện WARNING trở lên trên terminal
    """
    os.makedirs(_LOG_DIR, exist_ok=True)

    logger = logging.getLogger(name)

    # Tránh thêm handler trùng khi gọi nhiều lần
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # ── File Handler ──
    fh = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fmt_file = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(module)s.%(funcName)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(fmt_file)

    # ── Console Handler ──
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    fmt_console = logging.Formatter("  ⚠️ [%(levelname)s] %(message)s")
    ch.setFormatter(fmt_console)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
