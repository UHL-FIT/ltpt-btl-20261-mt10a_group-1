"""
main.py
=======
Khởi chạy ứng dụng "Quản Lý Hồ Sơ Bệnh Nhân".
Thiết kế theo mô hình MVC sử dụng Tkinter (GUI) + SQLite (Database).

Sử dụng:
    python main.py          # Chạy GUI (mặc định)
    python main.py --cli    # Chạy CLI
"""

import sys
from utils.logger import setup_logger

__version__ = "1.0.0"
logger = setup_logger("main")

# Ép console sử dụng UTF-8 khi chạy file .exe để tránh lỗi UnicodeEncodeError
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')


def main():
    """Entry point chính."""
    logger.info(f"=== Khởi chạy Quản Lý Bệnh Nhân v{__version__} ===")

    if len(sys.argv) > 1 and sys.argv[1] == '--cli':
        logger.info("Chuyển sang giao diện CLI.")
        from controllers import cli_controller
        cli_controller.chay_ung_dung()
    else:
        logger.info("Khởi động giao diện GUI.")
        from controllers import patient_controller
        patient_controller.chay_ung_dung()


if __name__ == "__main__":
    main()
