"""
seed_patients.py
================
Script sinh 500 bệnh nhân giả + lịch sử khám + thuốc để test.
Yêu cầu: pip install faker (hoặc uv add faker --dev)

Cách dùng:
    python seed_patients.py
"""

import random
from datetime import datetime, timedelta

# Kiểm tra faker
try:
    from faker import Faker
    fake = Faker('vi_VN')
except ImportError:
    print("❌ Cần cài đặt thư viện faker:")
    print("   uv add faker --dev")
    print("   hoặc: pip install faker")
    exit(1)

from models.db_manager import khoi_tao_database, lay_ket_noi
from models import patient as patient_model
from models import examination as exam_model
from models import medication as med_model

# ─── Danh sách bệnh phổ biến ───
BENH_CHINH = [
    "Viêm họng", "Cảm cúm", "Viêm phổi", "Tiểu đường type 2",
    "Tăng huyết áp", "Viêm dạ dày", "Đau lưng mãn tính", "Viêm khớp",
    "Hen suyễn", "Viêm xoang", "Sốt xuất huyết", "Viêm gan B",
    "Rối loạn tiêu hóa", "Thiếu máu", "Đau nửa đầu", "Viêm phế quản",
    "Trào ngược dạ dày", "Viêm da cơ địa", "Sỏi thận", "Gout"
]

BENH_PHU = [
    "", "", "", "",  # Nhiều trường hợp không có bệnh phụ
    "Mất ngủ", "Đau đầu", "Rối loạn lo âu", "Táo bón",
    "Viêm mũi dị ứng", "Thiếu vitamin D", "Béo phì", "Loãng xương"
]

THUOC = [
    ("Paracetamol 500mg", "1 viên", "3 lần/ngày"),
    ("Amoxicillin 500mg", "1 viên", "2 lần/ngày"),
    ("Omeprazole 20mg", "1 viên", "1 lần/ngày"),
    ("Metformin 500mg", "1 viên", "2 lần/ngày"),
    ("Amlodipine 5mg", "1 viên", "1 lần/ngày"),
    ("Ibuprofen 400mg", "1 viên", "3 lần/ngày"),
    ("Cetirizine 10mg", "1 viên", "1 lần/ngày"),
    ("Vitamin C 500mg", "1 viên", "1 lần/ngày"),
    ("Prednisolone 5mg", "1 viên", "2 lần/ngày"),
    ("Losartan 50mg", "1 viên", "1 lần/ngày"),
]

BAC_SI = [
    "BS. Nguyễn Văn A", "BS. Trần Thị B", "BS. Lê Minh C",
    "BS. Phạm Hồng D", "BS. Hoàng Anh E", "BS. Vũ Thanh F",
    "BS. Đặng Quốc G", "BS. Bùi Thị H"
]


def seed():
    """Sinh 500 bệnh nhân giả + lịch sử khám + thuốc."""
    khoi_tao_database()
    print("🌱 Bắt đầu seed dữ liệu...")
    print(f"   Đang tạo 500 bệnh nhân...")

    for i in range(1, 501):
        # Thông tin bệnh nhân
        gioi_tinh = random.choice(["Nam", "Nữ"])
        if gioi_tinh == "Nam":
            ho_ten = fake.name_male()
        else:
            ho_ten = fake.name_female()

        tuoi = random.randint(1, 95)
        chieu_cao = round(random.uniform(100, 190), 1) if tuoi >= 10 else round(random.uniform(50, 130), 1)
        can_nang = round(random.uniform(20, 120), 1) if tuoi >= 10 else round(random.uniform(5, 40), 1)

        ngay_tn = fake.date_between(start_date='-2y', end_date='today').strftime("%d/%m/%Y")

        data = {
            "ho_ten": ho_ten,
            "tuoi": tuoi,
            "gioi_tinh": gioi_tinh,
            "sdt": f"0{random.randint(300000000, 999999999)}",
            "dia_chi": fake.address().replace("\n", ", "),
            "chieu_cao": chieu_cao,
            "can_nang": can_nang,
            "ngay_tiep_nhan": ngay_tn,
            "benh_chinh": random.choice(BENH_CHINH),
            "benh_phu": random.choice(BENH_PHU),
            "ghi_chu": ""
        }

        ok, msg, ma_bn = patient_model.them_benh_nhan(data)

        if ok and ma_bn:
            # Tạo 1-3 lần khám ngẫu nhiên
            num_exams = random.randint(0, 3)
            for _ in range(num_exams):
                ngay_kham = fake.date_between(start_date='-1y', end_date='today').strftime("%d/%m/%Y")
                exam_data = {
                    "ngay_kham": ngay_kham,
                    "trieu_chung": random.choice(["Đau đầu, mệt mỏi", "Sốt, ho", "Đau bụng", "Khó thở", "Chóng mặt", "Đau ngực"]),
                    "chan_doan": data["benh_chinh"],
                    "huyet_ap": f"{random.randint(90, 180)}/{random.randint(60, 110)}",
                    "nhiet_do": round(random.uniform(36.0, 39.5), 1),
                    "bac_si": random.choice(BAC_SI),
                    "ghi_chu": ""
                }
                exam_model.them_lan_kham(ma_bn, exam_data)

            # Tạo 0-2 thuốc ngẫu nhiên
            num_meds = random.randint(0, 2)
            for _ in range(num_meds):
                thuoc = random.choice(THUOC)
                start = fake.date_between(start_date='-6m', end_date='today')
                end = start + timedelta(days=random.randint(7, 90))
                med_data = {
                    "ten_thuoc": thuoc[0],
                    "lieu_luong": thuoc[1],
                    "tan_suat": thuoc[2],
                    "ngay_bat_dau": start.strftime("%d/%m/%Y"),
                    "ngay_ket_thuc": end.strftime("%d/%m/%Y"),
                    "ghi_chu": ""
                }
                med_model.them_thuoc(ma_bn, med_data)

        if i % 100 == 0:
            print(f"   ✅ Đã tạo {i}/500 bệnh nhân...")

    print("\n🎉 Hoàn tất! Đã seed 500 bệnh nhân + lịch sử khám + thuốc.")
    print("   Chạy: python main.py để xem kết quả.")


if __name__ == "__main__":
    seed()
