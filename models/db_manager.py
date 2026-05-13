"""
models/db_manager.py
====================
Quản lý kết nối SQLite và khởi tạo schema cho hệ thống quản lý bệnh nhân.
Tự động tạo file database và các bảng nếu chưa tồn tại.
"""

import os
import sys
import sqlite3
from utils.logger import setup_logger

logger = setup_logger()

# ─── Đường dẫn file Database ──────────────────────────
if getattr(sys, 'frozen', False):
    _USER_DIR = os.path.join(os.path.expanduser("~"), "PatientManagement_Data")
    _BASE_DIR = _USER_DIR
else:
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_DIR = os.path.join(_BASE_DIR, "data")
DB_PATH = os.path.join(DB_DIR, "patients.db")


def lay_ket_noi():
    """
    Tạo và trả về kết nối SQLite tới file database.
    Tự động tạo thư mục data/ nếu chưa tồn tại.

    Returns:
        sqlite3.Connection: Kết nối SQLite đã bật foreign keys.
    """
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def khoi_tao_database():
    """
    Tạo các bảng trong database nếu chưa tồn tại.
    Gồm 3 bảng chính: patients, examinations, medications.
    """
    conn = lay_ket_noi()
    cursor = conn.cursor()

    try:
        # ── Bảng Bệnh nhân ──
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                ma_bn       TEXT PRIMARY KEY,
                ho_ten      TEXT NOT NULL,
                tuoi        INTEGER,
                gioi_tinh   TEXT DEFAULT 'Nam',
                sdt         TEXT,
                dia_chi     TEXT,
                chieu_cao   REAL,
                can_nang    REAL,
                ngay_tiep_nhan TEXT,
                benh_chinh  TEXT,
                benh_phu    TEXT,
                ghi_chu     TEXT,
                ngay_tao    TEXT DEFAULT (datetime('now', 'localtime'))
            )
        """)

        # ── Bảng Lịch sử Khám bệnh ──
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS examinations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_bn       TEXT NOT NULL,
                ngay_kham   TEXT NOT NULL,
                trieu_chung TEXT,
                chan_doan    TEXT,
                huyet_ap    TEXT,
                nhiet_do    REAL,
                bac_si      TEXT,
                ghi_chu     TEXT,
                FOREIGN KEY (ma_bn) REFERENCES patients(ma_bn) ON DELETE CASCADE
            )
        """)

        # ── Bảng Lịch sử Thuốc ──
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medications (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_bn           TEXT NOT NULL,
                examination_id  INTEGER,
                ten_thuoc       TEXT NOT NULL,
                lieu_luong      TEXT,
                tan_suat        TEXT,
                ngay_bat_dau    TEXT,
                ngay_ket_thuc   TEXT,
                ghi_chu         TEXT,
                FOREIGN KEY (ma_bn) REFERENCES patients(ma_bn) ON DELETE CASCADE,
                FOREIGN KEY (examination_id) REFERENCES examinations(id) ON DELETE SET NULL
            )
        """)

        conn.commit()
        logger.info(f"Khởi tạo database thành công tại: {DB_PATH}")

    except Exception as e:
        logger.error(f"Lỗi khởi tạo database: {e}", exc_info=True)
        conn.rollback()
        raise
    finally:
        conn.close()


def lay_ma_bn_moi():
    """
    Sinh mã bệnh nhân mới tự động theo format BN-XXXXX.

    Returns:
        str: Mã bệnh nhân mới (VD: 'BN-00001', 'BN-00002'...).
    """
    conn = lay_ket_noi()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ma_bn FROM patients ORDER BY ma_bn DESC LIMIT 1")
        row = cursor.fetchone()

        if row is None:
            return "BN-00001"

        last_ma = row["ma_bn"]
        # Trích xuất số từ mã cuối cùng
        try:
            num = int(last_ma.replace("BN-", ""))
            return f"BN-{num + 1:05d}"
        except ValueError:
            # Nếu mã không đúng format, đếm tổng + 1
            cursor.execute("SELECT COUNT(*) as total FROM patients")
            total = cursor.fetchone()["total"]
            return f"BN-{total + 1:05d}"
    finally:
        conn.close()


# Khởi tạo database ngay khi import module
khoi_tao_database()
