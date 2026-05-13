"""
tests/test_db.py
================
Unit tests cho kết nối database và schema.
"""

import os
import unittest
import sqlite3
from models import db_manager


class TestDatabase(unittest.TestCase):
    """Test kết nối và schema database."""

    @classmethod
    def setUpClass(cls):
        cls.test_db = os.path.join(os.path.dirname(__file__), "test_db.db")
        db_manager.DB_PATH = cls.test_db
        db_manager.khoi_tao_database()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)

    def test_ket_noi(self):
        """Test kết nối database thành công."""
        conn = db_manager.lay_ket_noi()
        self.assertIsNotNone(conn)
        conn.close()

    def test_bang_patients_ton_tai(self):
        """Test bảng patients đã được tạo."""
        conn = db_manager.lay_ket_noi()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='patients'")
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        conn.close()

    def test_bang_examinations_ton_tai(self):
        """Test bảng examinations đã được tạo."""
        conn = db_manager.lay_ket_noi()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='examinations'")
        self.assertIsNotNone(cursor.fetchone())
        conn.close()

    def test_bang_medications_ton_tai(self):
        """Test bảng medications đã được tạo."""
        conn = db_manager.lay_ket_noi()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='medications'")
        self.assertIsNotNone(cursor.fetchone())
        conn.close()

    def test_ma_bn_moi(self):
        """Test sinh mã bệnh nhân tự động."""
        ma = db_manager.lay_ma_bn_moi()
        self.assertTrue(ma.startswith("BN-"))
        self.assertEqual(len(ma), 8)  # BN-XXXXX

    def test_foreign_key(self):
        """Test foreign key constraint hoạt động."""
        conn = db_manager.lay_ket_noi()
        cursor = conn.cursor()

        # Thử insert examination cho BN không tồn tại
        with self.assertRaises(sqlite3.IntegrityError):
            cursor.execute("""
                INSERT INTO examinations (ma_bn, ngay_kham) VALUES ('KHONG_TON_TAI', '01/01/2024')
            """)
            conn.commit()

        conn.close()


if __name__ == '__main__':
    unittest.main()
