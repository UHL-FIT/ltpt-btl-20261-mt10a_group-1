"""
tests/test_stats.py
===================
Unit tests cho module thống kê.
"""

import os
import unittest
from models import db_manager
from models import patient as patient_model
from controllers import stats_controller


class TestStats(unittest.TestCase):
    """Test thống kê tổng hợp."""

    @classmethod
    def setUpClass(cls):
        cls.test_db = os.path.join(os.path.dirname(__file__), "test_stats.db")
        db_manager.DB_PATH = cls.test_db
        db_manager.khoi_tao_database()

    def setUp(self):
        conn = db_manager.lay_ket_noi()
        conn.execute("DELETE FROM medications")
        conn.execute("DELETE FROM examinations")
        conn.execute("DELETE FROM patients")
        conn.commit()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)

    def test_thong_ke_rong(self):
        """Thống kê khi chưa có dữ liệu."""
        stats = stats_controller.thong_ke_tong_hop()
        self.assertEqual(stats, {})

    def test_thong_ke_co_du_lieu(self):
        """Thống kê khi có dữ liệu."""
        patient_model.them_benh_nhan({
            "ho_ten": "A", "tuoi": 30, "gioi_tinh": "Nam",
            "chieu_cao": 170, "can_nang": 70, "benh_chinh": "Cảm cúm"
        })
        patient_model.them_benh_nhan({
            "ho_ten": "B", "tuoi": 25, "gioi_tinh": "Nữ",
            "chieu_cao": 160, "can_nang": 55, "benh_chinh": "Cảm cúm"
        })

        stats = stats_controller.thong_ke_tong_hop()
        self.assertEqual(stats["tong_bn"], 2)
        self.assertGreater(stats["bmi_tb"], 0)

    def test_thong_ke_benh(self):
        """Test thống kê tần suất bệnh."""
        for _ in range(3):
            patient_model.them_benh_nhan({"ho_ten": "X", "tuoi": 30, "benh_chinh": "Viêm họng"})
        patient_model.them_benh_nhan({"ho_ten": "Y", "tuoi": 25, "benh_chinh": "Cảm cúm"})

        df_benh = stats_controller.thong_ke_benh()
        self.assertFalse(df_benh.empty)
        self.assertEqual(df_benh.iloc[0]["Bệnh"], "Viêm họng")
        self.assertEqual(df_benh.iloc[0]["Số ca"], 3)


if __name__ == '__main__':
    unittest.main()
