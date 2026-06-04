"""
generate_fake_db.py
───────────────────
Tạo database SQLite giả (patients_data.db) tương thích với hệ thống
Quản Lý Hồ Sơ Bệnh Nhân (MVC).

Cấu trúc bảng khớp hoàn toàn với patient_model.py:
  • patients               – hồ sơ bệnh nhân
  • follow_up_appointments – lịch tái khám

Chạy:
  python generate_fake_db.py
  → Chọn số lượng bệnh nhân trong menu hiện ra
  → File patients_data.db xuất hiện cùng thư mục
"""

import sqlite3
import random
import os
from datetime import datetime, timedelta, date

# ─── Dữ liệu mẫu tiếng Việt ────────────────────────────────────────────────

HO = [
    "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan",
    "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương",
    "Lý", "Đinh", "Mai", "Tô", "Trương",
]

TEN_DEM_NAM = ["Văn", "Hữu", "Đức", "Minh", "Quốc", "Trung", "Thành", "Bá", "Công", "Gia"]
TEN_NAM = [
    "An", "Bình", "Cường", "Dũng", "Hải", "Hùng", "Khoa",
    "Long", "Minh", "Nam", "Phong", "Quân", "Sơn", "Tài",
    "Thắng", "Tiến", "Toàn", "Trung", "Tuấn", "Việt",
]

TEN_DEM_NU = ["Thị", "Ngọc", "Thanh", "Thùy", "Phương", "Bích", "Kim", "Lan", "Thu"]
TEN_NU = [
    "Anh", "Chi", "Dung", "Hà", "Hoa", "Hương", "Lan",
    "Linh", "Mai", "Nhung", "Phương", "Thảo", "Thu",
    "Thủy", "Trang", "Trinh", "Uyên", "Vân", "Xuân", "Yến",
]

BENH_CHINH = [
    "Tăng huyết áp", "Tiểu đường type 2", "Viêm phổi", "Viêm dạ dày",
    "Đau lưng mãn tính", "Suy tim", "Hen phế quản", "Viêm khớp",
    "Rối loạn lipid máu", "Suy thận mãn tính", "Đau đầu mãn tính",
    "Viêm gan B", "Loét dạ dày tá tràng", "Trào ngược dạ dày",
    "Thiếu máu", "Suy giáp", "Cường giáp", "Viêm đại tràng",
    "Bệnh tim mạch vành", "Đột quỵ nhẹ (TIA)",
]

LICH_SU_MAU = [
    "Bệnh nhân đến khám định kỳ. Không có triệu chứng mới.",
    "Tái khám sau điều trị. Tình trạng cải thiện rõ rệt.",
    "Nhập viện cấp cứu do khó thở. Đã ổn định sau 2 ngày điều trị.",
    "Phẫu thuật cắt ruột thừa. Hồi phục tốt sau 5 ngày.",
    "Điều trị ngoại trú 3 tuần. Tuân thủ tốt phác đồ thuốc.",
    "Dị ứng với Penicillin. Cần lưu ý khi kê đơn kháng sinh.",
    "Tiền sử gia đình có bệnh tim mạch. Theo dõi định kỳ 3 tháng/lần.",
    "Hút thuốc lá 10 gói-năm. Đã tư vấn cai thuốc.",
    "Bệnh nhân cao tuổi, cần hỗ trợ di chuyển. Người nhà thường đi kèm.",
    "Đang sử dụng: Metformin 500mg x2, Amlodipine 5mg x1 mỗi ngày.",
    "Tiền sử gãy xương hông năm 2022. Đang dùng Calcium + Vitamin D.",
    "Chỉ số HbA1c gần nhất: 7.2%. Cần kiểm soát đường huyết tốt hơn.",
    "Siêu âm bụng cho thấy gan nhiễm mỡ độ I. Khuyến nghị giảm cân.",
    "ECG bình thường. X-quang ngực không có bất thường.",
    "Bệnh nhân tuân thủ tốt lịch tái khám. Tâm lý ổn định.",
]

LY_DO_TAI_KHAM = [
    "Tái khám kiểm tra huyết áp",
    "Xét nghiệm định kỳ – đường huyết, mỡ máu",
    "Theo dõi sau phẫu thuật",
    "Tiêm phòng cúm định kỳ",
    "Kiểm tra kết quả xét nghiệm",
    "Điều chỉnh liều thuốc",
    "Siêu âm kiểm tra định kỳ",
    "Tư vấn dinh dưỡng",
    "Theo dõi sau điều trị viêm phổi",
    "Kiểm tra sức khỏe tổng quát định kỳ",
]

TAN_SUAT = ["1 tuần/lần", "2 tuần/lần", "1 tháng/lần", "3 tháng/lần", "6 tháng/lần"]


# ─── Hàm tạo dữ liệu ───────────────────────────────────────────────────────

def random_phone() -> str:
    prefix = random.choice(["03", "07", "08", "09"])
    suffix = random.choice(["2", "3", "4", "5", "6", "7", "8", "9"])
    digits = "".join(str(random.randint(0, 9)) for _ in range(7))
    return f"{prefix}{suffix}{digits}"


def random_receive_time(days_back: int = 730) -> str:
    """Ngày nhận trong vòng 2 năm gần nhất."""
    delta = random.randint(0, days_back)
    dt = datetime.now() - timedelta(days=delta)
    # ~20% hôm nay, còn lại ngẫu nhiên
    if random.random() < 0.02:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M")


def random_name(gender: str) -> str:
    ho = random.choice(HO)
    if gender == "Nam":
        return f"{ho} {random.choice(TEN_DEM_NAM)} {random.choice(TEN_NAM)}"
    elif gender == "Nu":
        return f"{ho} {random.choice(TEN_DEM_NU)} {random.choice(TEN_NU)}"
    else:
        return f"{ho} {random.choice(TEN_NAM + TEN_NU)}"


def generate_patient(idx: int) -> tuple:
    """
    Trả về tuple khớp với INSERT của patient_model.py:
    (name, age, gender, phone, receive_time, primary_disease, history, height, weight)
    """
    gender_raw = random.choices(["Nam", "Nữ", "Khác"], weights=[48, 48, 4])[0]
    gender_key = "Nam" if gender_raw == "Nam" else ("Nu" if gender_raw == "Nữ" else "Khac")
    name = random_name(gender_key)

    age = random.choices(
        range(1, 95),
        weights=[
            # Trẻ em (1-17): 10%
            *[0.6] * 17,
            # Người trẻ (18-40): 25%
            *[1.1] * 23,
            # Trung niên (41-65): 40%
            *[1.6] * 25,
            # Cao tuổi (66-94): 25%
            *[0.9] * 29,
        ]
    )[0]

    phone = random_phone()
    receive_time = random_receive_time()
    primary_disease = random.choice(BENH_CHINH)

    # Lịch sử: 1-3 ghi chú ngẫu nhiên, đôi khi để trống
    if random.random() < 0.1:
        history = ""
    else:
        num_notes = random.randint(1, 3)
        history = "\n".join(random.sample(LICH_SU_MAU, min(num_notes, len(LICH_SU_MAU))))

    # Chiều cao / cân nặng – ~80% có đủ cả hai
    if random.random() < 0.80:
        if gender_raw == "Nam":
            height = round(random.gauss(168, 7), 1)
            weight = round(random.gauss(67, 12), 1)
        else:
            height = round(random.gauss(158, 6), 1)
            weight = round(random.gauss(54, 10), 1)
        height = max(100.0, min(220.0, height))
        weight = max(30.0,  min(180.0, weight))
    else:
        height = None
        weight = None

    return (name, age, gender_raw, phone, receive_time,
            primary_disease, history, height, weight)


def generate_follow_up(patient_id: int) -> tuple:
    """
    Trả về tuple:
    (patient_id, appointment_date, reason, frequency)
    """
    delta = random.randint(-30, 180)   # -30 ngày (quá hạn) đến +180 ngày tương lai
    appt_date = (date.today() + timedelta(days=delta)).isoformat()
    reason = random.choice(LY_DO_TAI_KHAM)
    frequency = random.choice(TAN_SUAT)
    return (patient_id, appt_date, reason, frequency)


# ─── Khởi tạo schema (copy từ patient_model.py) ───────────────────────────

def init_schema(conn: sqlite3.Connection):
    conn.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            name             TEXT NOT NULL,
            age              INTEGER,
            gender           TEXT,
            phone            TEXT,
            receive_time     TEXT,
            primary_disease  TEXT,
            history          TEXT,
            height           REAL,
            weight           REAL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS follow_up_appointments (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id       INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            reason           TEXT,
            frequency        TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()


# ─── Hàm sinh database ─────────────────────────────────────────────────────

def generate_database(num_patients: int, output_path: str):
    print(f"\n{'─'*55}")
    print(f"  Đang tạo {num_patients:,} bệnh nhân → {output_path}")
    print(f"{'─'*55}")

    if os.path.exists(output_path):
        os.remove(output_path)
        print(f"  [!] Đã xóa file cũ: {output_path}")

    conn = sqlite3.connect(output_path)
    init_schema(conn)

    # ── Bệnh nhân ──────────────────────────────────────────────────────
    print(f"  Đang chèn bệnh nhân...", end="", flush=True)
    patient_batch = [generate_patient(i) for i in range(num_patients)]
    conn.executemany('''
        INSERT INTO patients
            (name, age, gender, phone, receive_time,
             primary_disease, history, height, weight)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', patient_batch)
    conn.commit()
    print(f" ✓ {num_patients:,} bản ghi")

    # ── Lịch tái khám – trung bình ~60% bệnh nhân có ít nhất 1 lịch ──
    print(f"  Đang chèn lịch tái khám...", end="", flush=True)
    follow_up_batch = []
    for pid in range(1, num_patients + 1):
        r = random.random()
        if r < 0.30:
            count = 0        # 30% không có lịch
        elif r < 0.70:
            count = 1        # 40% có 1 lịch
        elif r < 0.90:
            count = 2        # 20% có 2 lịch
        else:
            count = random.randint(3, 5)  # 10% có 3-5 lịch
        for _ in range(count):
            follow_up_batch.append(generate_follow_up(pid))

    conn.executemany('''
        INSERT INTO follow_up_appointments
            (patient_id, appointment_date, reason, frequency)
        VALUES (?, ?, ?, ?)
    ''', follow_up_batch)
    conn.commit()
    print(f" ✓ {len(follow_up_batch):,} bản ghi")

    conn.close()

    # ── Thống kê nhanh ─────────────────────────────────────────────────
    size_kb = os.path.getsize(output_path) / 1024
    print(f"\n  ✅ Hoàn tất!")
    print(f"     File     : {os.path.abspath(output_path)}")
    print(f"     Kích thước: {size_kb:.1f} KB")
    print(f"     Bệnh nhân : {num_patients:,}")
    print(f"     Tái khám  : {len(follow_up_batch):,}")
    print(f"{'─'*55}\n")


# ─── Menu lựa chọn ─────────────────────────────────────────────────────────

OPTIONS = {
    "1": (200,    "200 bệnh nhân   (~nhỏ, demo nhanh)"),
    "2": (1_000,  "1.000 bệnh nhân (~vừa, kiểm thử)"),
    "3": (5_000,  "5.000 bệnh nhân (~lớn, hiệu năng)"),
    "4": (10_000, "10.000 bệnh nhân (~rất lớn, stress test)"),
    "5": (None,   "Nhập số tùy chỉnh"),
}

def main():
    print("\n" + "═"*55)
    print("   CÔNG CỤ TẠO DATABASE GIẢ – Quản Lý Bệnh Nhân")
    print("═"*55)
    print("  Chọn số lượng bệnh nhân cần tạo:\n")
    for key, (_, label) in OPTIONS.items():
        print(f"    [{key}]  {label}")
    print()

    while True:
        choice = input("  Nhập lựa chọn (1-5): ").strip()
        if choice in OPTIONS:
            break
        print("  ❌ Lựa chọn không hợp lệ. Vui lòng nhập 1–5.")

    num_patients, _ = OPTIONS[choice]

    if num_patients is None:
        while True:
            raw = input("  Nhập số bệnh nhân muốn tạo: ").strip()
            try:
                num_patients = int(raw)
                if num_patients < 1:
                    raise ValueError
                break
            except ValueError:
                print("  ❌ Vui lòng nhập một số nguyên dương.")

    # Tên file output
    default_name = "patients_data.db"
    print(f"\n  Tên file mặc định: {default_name}")
    custom = input("  Nhấn Enter để dùng tên mặc định hoặc nhập tên khác: ").strip()
    output_path = custom if custom else default_name

    # Xác nhận nếu file đã tồn tại
    if os.path.exists(output_path):
        confirm = input(f"\n  ⚠️  File '{output_path}' đã tồn tại. Ghi đè? (y/n): ").strip().lower()
        if confirm != "y":
            print("  Đã hủy. Không có thay đổi nào được thực hiện.\n")
            return

    generate_database(num_patients, output_path)
    print("  💡 Đổi tên file thành 'patients_data.db' rồi đặt vào thư mục gốc")
    print("     của dự án để ứng dụng tự nhận diện.\n")


if __name__ == "__main__":
    main()