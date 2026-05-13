"""
Module tạo dữ liệu mẫu cho Hồ sơ Bệnh nhân.
Bao gồm: Tuổi, Giới tính, Lịch sử khám, Chỉ số sức khỏe, Lịch sử dùng thuốc.
"""

import random
import json
import os
from datetime import datetime, timedelta

# Seed cố định để dữ liệu nhất quán
random.seed(42)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "patients.json")

# ============================
# Danh sách dữ liệu gốc
# ============================
HO_LIST = [
    "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng",
    "Huỳnh", "Phan", "Vũ", "Võ", "Đặng",
    "Bùi", "Đỗ", "Hồ", "Ngô", "Dương",
]

TEN_LIST = [
    "An", "Bình", "Cường", "Dũng", "Phúc",
    "Giang", "Hạnh", "Khoa", "Linh", "Mai",
    "Nam", "Phong", "Quân", "Sơn", "Tâm",
    "Uyên", "Vinh", "Xuân", "Hùng", "Thảo",
    "Tuấn", "Hà", "Đạt", "Trang", "Lan",
]

LOAI_BENH = [
    "Cảm cúm", "Viêm họng", "Đau dạ dày", "Tăng huyết áp",
    "Tiểu đường", "Viêm phổi", "Đau lưng", "Viêm khớp",
    "Dị ứng", "Viêm gan", "Sốt xuất huyết", "Viêm xoang",
    "Đau đầu migraine", "Hen suyễn", "Thiếu máu",
]

THUOC_LIST = [
    "Paracetamol", "Amoxicillin", "Omeprazole", "Amlodipine",
    "Metformin", "Ibuprofen", "Cetirizine", "Losartan",
    "Aspirin", "Vitamin C", "Prednisolone", "Salbutamol",
    "Diclofenac", "Azithromycin", "Clopidogrel",
]


def tao_ten(gioi_tinh):
    """Tạo họ tên ngẫu nhiên theo giới tính."""
    ho = random.choice(HO_LIST)
    ten_dem = "Thị" if gioi_tinh == "Nữ" else random.choice(["Văn", "Minh", "Đức", "Quốc"])
    ten = random.choice(TEN_LIST)
    return f"{ho} {ten_dem} {ten}"


def tao_chi_so_suc_khoe(tuoi, gioi_tinh):
    """Tạo chỉ số sức khỏe phù hợp theo tuổi và giới tính."""
    # Chiều cao (m) và cân nặng (kg)
    if tuoi < 18:
        chieu_cao = round(random.uniform(1.00, 1.65), 2)
        can_nang = round(random.uniform(20, 55), 1)
    elif gioi_tinh == "Nam":
        chieu_cao = round(random.uniform(1.55, 1.85), 2)
        can_nang = round(random.uniform(50, 95), 1)
    else:
        chieu_cao = round(random.uniform(1.48, 1.72), 2)
        can_nang = round(random.uniform(42, 75), 1)

    # Huyết áp tâm thu / tâm trương (mmHg)
    if tuoi < 18:
        ha_tam_thu = random.randint(90, 120)
        ha_tam_truong = random.randint(55, 75)
    elif tuoi < 40:
        ha_tam_thu = random.randint(100, 140)
        ha_tam_truong = random.randint(60, 90)
    elif tuoi < 60:
        ha_tam_thu = random.randint(110, 160)
        ha_tam_truong = random.randint(65, 100)
    else:
        ha_tam_thu = random.randint(115, 170)
        ha_tam_truong = random.randint(70, 105)

    return {
        "chieu_cao": chieu_cao,
        "can_nang": can_nang,
        "huyet_ap_tam_thu": ha_tam_thu,
        "huyet_ap_tam_truong": ha_tam_truong,
        "nhip_tim": random.randint(58, 105),
        "duong_huyet": round(random.uniform(70, 200), 1),
    }


def tao_lich_su_kham(so_lan):
    """Tạo lịch sử khám bệnh ngẫu nhiên."""
    lich_su = []
    for _ in range(so_lan):
        ngay = datetime.now() - timedelta(days=random.randint(1, 730))
        loai = random.choice(LOAI_BENH)
        lich_su.append({
            "ngay_kham": ngay.strftime("%Y-%m-%d"),
            "loai_benh": loai,
            "bac_si": f"BS. {random.choice(HO_LIST)} {random.choice(TEN_LIST)}",
            "ghi_chu": f"Khám và điều trị {loai.lower()}",
        })
    lich_su.sort(key=lambda x: x["ngay_kham"], reverse=True)
    return lich_su


def tao_lich_su_thuoc(so_thuoc):
    """Tạo lịch sử dùng thuốc ngẫu nhiên."""
    lich_su = []
    for _ in range(so_thuoc):
        ngay_bd = datetime.now() - timedelta(days=random.randint(30, 365))
        so_ngay = random.randint(5, 30)
        lich_su.append({
            "ten_thuoc": random.choice(THUOC_LIST),
            "lieu_luong": f"{random.choice([250, 500, 1000])}mg",
            "tan_suat": random.choice(["1 lần/ngày", "2 lần/ngày", "3 lần/ngày"]),
            "ngay_bat_dau": ngay_bd.strftime("%Y-%m-%d"),
            "ngay_ket_thuc": (ngay_bd + timedelta(days=so_ngay)).strftime("%Y-%m-%d"),
        })
    return lich_su


def tao_du_lieu_mau(so_benh_nhan=100):
    """
    Tạo danh sách hồ sơ bệnh nhân mẫu.

    Args:
        so_benh_nhan: Số lượng bệnh nhân cần tạo (mặc định 100).

    Returns:
        list: Danh sách dict chứa thông tin bệnh nhân.
    """
    patients = []
    for i in range(1, so_benh_nhan + 1):
        gioi_tinh = random.choice(["Nam", "Nữ"])
        tuoi = random.randint(5, 85)
        chi_so = tao_chi_so_suc_khoe(tuoi, gioi_tinh)

        patient = {
            "id": i,
            "ho_ten": tao_ten(gioi_tinh),
            "tuoi": tuoi,
            "gioi_tinh": gioi_tinh,
            **chi_so,
            "lich_su_kham": tao_lich_su_kham(random.randint(1, 8)),
            "lich_su_thuoc": tao_lich_su_thuoc(random.randint(1, 5)),
        }
        patients.append(patient)

    return patients


def luu_du_lieu(data, filepath=DATA_FILE):
    """Lưu dữ liệu ra file JSON."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[✓] Đã lưu {len(data)} hồ sơ bệnh nhân vào {filepath}")


def tai_du_lieu(filepath=DATA_FILE):
    """Tải dữ liệu từ file JSON. Nếu chưa có thì tạo mới."""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"[✓] Đã tải {len(data)} hồ sơ bệnh nhân từ {filepath}")
        return data
    else:
        print("[i] Chưa có dữ liệu, đang tạo dữ liệu mẫu...")
        data = tao_du_lieu_mau()
        luu_du_lieu(data, filepath)
        return data


if __name__ == "__main__":
    data = tao_du_lieu_mau(100)
    luu_du_lieu(data)
    print(f"\nMẫu hồ sơ đầu tiên:")
    print(json.dumps(data[0], ensure_ascii=False, indent=2))
