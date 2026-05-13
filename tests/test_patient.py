"""
tests/test_patient.py
=====================
Unit tests cho CRUD bệnh nhân và tính BMI.
"""

import os
import unittest
from models import db_manager
from models import patient as patient_model
from utils.bmi_calculator import tinh_bmi, phan_loai_bmi


class TestBMI(unittest.TestCase):
    """Test công thức tính BMI và phân loại."""

    def test_tinh_bmi_binh_thuong(self):
        """BMI = 70 / (1.70^2) = 24.2"""
        bmi = tinh_bmi(170, 70)
        self.assertAlmostEqual(bmi, 24.2, places=1)

    def test_tinh_bmi_du_lieu_loi(self):
        """Chiều cao hoặc cân nặng <= 0 trả về 0."""
        self.assertEqual(tinh_bmi(0, 70), 0.0)
        self.assertEqual(tinh_bmi(170, 0), 0.0)
        self.assertEqual(tinh_bmi("abc", 70), 0.0)

    def test_phan_loai_bmi(self):
        """Test các ngưỡng phân loại BMI."""
        self.assertEqual(phan_loai_bmi(16.0), "Thiếu cân")
        self.assertEqual(phan_loai_bmi(22.0), "Bình thường")
        self.assertEqual(phan_loai_bmi(24.0), "Thừa cân")
        self.assertEqual(phan_loai_bmi(28.0), "Béo phì độ I")
        self.assertEqual(phan_loai_bmi(35.0), "Béo phì độ II")


class TestPatientCRUD(unittest.TestCase):
    """Test CRUD bệnh nhân."""

    @classmethod
    def setUpClass(cls):
        """Dùng database test riêng."""
        cls.test_db = os.path.join(os.path.dirname(__file__), "test_patients.db")
        db_manager.DB_PATH = cls.test_db
        db_manager.khoi_tao_database()

    def setUp(self):
        """Xóa sạch dữ liệu trước mỗi test."""
        conn = db_manager.lay_ket_noi()
        conn.execute("DELETE FROM medications")
        conn.execute("DELETE FROM examinations")
        conn.execute("DELETE FROM patients")
        conn.commit()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        """Xóa file database test."""
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)

    def test_them_benh_nhan(self):
        """Test thêm bệnh nhân thành công."""
        data = {
            "ho_ten": "Nguyễn Văn A",
            "tuoi": 30,
            "gioi_tinh": "Nam",
            "sdt": "0912345678",
            "benh_chinh": "Viêm họng"
        }
        ok, msg, ma_bn = patient_model.them_benh_nhan(data)
        self.assertTrue(ok)
        self.assertIsNotNone(ma_bn)
        self.assertTrue(ma_bn.startswith("BN-"))

    def test_lay_danh_sach(self):
        """Test lấy danh sách sau khi thêm."""
        data = {"ho_ten": "Test", "tuoi": 25, "benh_chinh": "Test"}
        patient_model.them_benh_nhan(data)

        df, ok = patient_model.lay_danh_sach()
        self.assertTrue(ok)
        self.assertEqual(len(df), 1)

    def test_sua_benh_nhan(self):
        """Test sửa thông tin bệnh nhân."""
        data = {"ho_ten": "Trần B", "tuoi": 40, "benh_chinh": "Cảm cúm"}
        ok, _, ma_bn = patient_model.them_benh_nhan(data)

        new_data = {"ho_ten": "Trần B Updated", "tuoi": 41, "benh_chinh": "Viêm phổi"}
        ok_sua, msg = patient_model.sua_benh_nhan(ma_bn, new_data)
        self.assertTrue(ok_sua)

        df, _ = patient_model.lay_danh_sach()
        row = df[df["ma_bn"] == ma_bn].iloc[0]
        self.assertEqual(row["ho_ten"], "Trần B Updated")

    def test_xoa_benh_nhan(self):
        """Test xóa bệnh nhân."""
        data = {"ho_ten": "Xóa Test", "tuoi": 50, "benh_chinh": "Test"}
        ok, _, ma_bn = patient_model.them_benh_nhan(data)

        ok_xoa, msg = patient_model.xoa_benh_nhan(ma_bn)
        self.assertTrue(ok_xoa)

        df, _ = patient_model.lay_danh_sach()
        self.assertTrue(df[df["ma_bn"] == ma_bn].empty)

    def test_xoa_nhieu(self):
        """Test xóa nhiều bệnh nhân."""
        ma_list = []
        for i in range(3):
            _, _, ma = patient_model.them_benh_nhan(
                {"ho_ten": f"BN {i}", "tuoi": 20 + i, "benh_chinh": "Test"}
            )
            ma_list.append(ma)

        ok, _ = patient_model.xoa_nhieu_benh_nhan(ma_list[:2])
        self.assertTrue(ok)

        df, _ = patient_model.lay_danh_sach()
        self.assertEqual(len(df), 1)

    def test_tim_kiem(self):
        """Test tìm kiếm bệnh nhân."""
        patient_model.them_benh_nhan({"ho_ten": "Nguyễn Minh", "tuoi": 30, "benh_chinh": "Cảm"})
        patient_model.them_benh_nhan({"ho_ten": "Trần Anh", "tuoi": 25, "benh_chinh": "Sốt"})

        df, ok = patient_model.tim_kiem("Nguyễn", "ho_ten")
        self.assertTrue(ok)
        self.assertEqual(len(df), 1)

    def test_thong_ke(self):
        """Test hàm thống kê."""
        patient_model.them_benh_nhan({"ho_ten": "A", "tuoi": 30, "gioi_tinh": "Nam", "benh_chinh": "X"})
        patient_model.them_benh_nhan({"ho_ten": "B", "tuoi": 25, "gioi_tinh": "Nữ", "benh_chinh": "Y"})

        df, _ = patient_model.lay_danh_sach()
        stats = patient_model.thong_ke(df)

        self.assertEqual(stats["tong_bn"], 2)
        self.assertEqual(stats["nam"], 1)
        self.assertEqual(stats["nu"], 1)


if __name__ == '__main__':
    unittest.main()
