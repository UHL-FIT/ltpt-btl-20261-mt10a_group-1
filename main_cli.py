"""
main_cli.py
===========
Khởi chạy ứng dụng ở chế độ CLI (dùng cho build exe riêng biệt).
"""

import sys
from utils.logger import setup_logger
from controllers import cli_controller

__version__ = "1.0.0"
logger = setup_logger("main_cli")

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

if __name__ == "__main__":
    logger.info(f"=== Khởi chạy CLI v{__version__} ===")
    cli_controller.chay_ung_dung()
