import sys
import io

# Đảm bảo hiển thị tiếng Việt trên Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

"""
===================================================================
 ỨNG DỤNG QUẢN LÝ HỒ SƠ BỆNH NHÂN
===================================================================
 Dữ liệu đầu vào: Tuổi, Giới tính, Lịch sử khám,
                    Chỉ số sức khỏe, Lịch sử dùng thuốc

 Chức năng:
   1. Quản lý thông tin sức khỏe cá nhân
   2. Phân tích xu hướng sức khỏe theo nhóm
   3. Tính chỉ số BMI theo công thức
   4. Tính trung bình huyết áp theo nhóm tuổi (pandas groupby)
   5. Thống kê tần suất khám bệnh theo loại bệnh

 Cách chạy:
   python main.py
===================================================================
"""

import json
from tabulate import tabulate

from du_lieu_mau import tai_du_lieu, luu_du_lieu, tao_du_lieu_mau
from phan_tich import (
    tao_dataframe,
    phan_tich_bmi,
    phan_tich_huyet_ap_theo_nhom_tuoi,
    thong_ke_tan_suat_kham,
    thong_ke_dung_thuoc,
    thong_ke_tong_quan,
    tinh_bmi,
    phan_loai_bmi,
)
from bieu_do import ve_tat_ca


# ============================================================
# TIỆN ÍCH HIỂN THỊ
# ============================================================

def in_duong_ke(ky_tu="═", do_dai=70):
    print(ky_tu * do_dai)


def in_tieu_de(text):
    print()
    in_duong_ke()
    print(f"  {text}")
    in_duong_ke()


def in_tieu_de_phu(text):
    print(f"\n── {text} ──")


# ============================================================
# CÁC CHỨC NĂNG CHÍNH
# ============================================================

def xem_tong_quan(df, patients):
    """Hiển thị thống kê tổng quan."""
    in_tieu_de("📋 THỐNG KÊ TỔNG QUAN")

    stats = thong_ke_tong_quan(df, patients)
    for key, value in stats.items():
        print(f"  {key:.<30s} {value}")


def xem_danh_sach_benh_nhan(df):
    """Hiển thị danh sách bệnh nhân dạng bảng."""
    in_tieu_de("👥 DANH SÁCH BỆNH NHÂN")

    df_show = df.copy()
    df_show["bmi"] = df_show.apply(
        lambda r: tinh_bmi(r["can_nang"], r["chieu_cao"]), axis=1
    )
    df_show["huyet_ap"] = (
        df_show["huyet_ap_tam_thu"].astype(str) + "/" +
        df_show["huyet_ap_tam_truong"].astype(str)
    )

    cols = ["id", "ho_ten", "tuoi", "gioi_tinh", "bmi", "huyet_ap", "nhip_tim", "so_lan_kham"]
    headers = ["ID", "Họ tên", "Tuổi", "GT", "BMI", "Huyết áp", "Nhịp tim", "Số lần khám"]

    print(tabulate(
        df_show[cols].values.tolist(),
        headers=headers,
        tablefmt="rounded_grid",
        floatfmt=".2f",
    ))
    print(f"\n  Tổng cộng: {len(df_show)} bệnh nhân")


def xem_chi_tiet_benh_nhan(patients):
    """Xem chi tiết một bệnh nhân theo ID."""
    in_tieu_de("🔍 CHI TIẾT BỆNH NHÂN")

    try:
        ma_bn = int(input("  Nhập ID bệnh nhân: "))
    except ValueError:
        print("  [!] ID không hợp lệ.")
        return

    patient = next((p for p in patients if p["id"] == ma_bn), None)
    if patient is None:
        print(f"  [!] Không tìm thấy bệnh nhân với ID = {ma_bn}")
        return

    bmi = tinh_bmi(patient["can_nang"], patient["chieu_cao"])

    print(f"""
  ┌─────────────────────────────────────────────┐
  │  {patient['ho_ten']:^43s}  │
  └─────────────────────────────────────────────┘

  Thông tin cơ bản:
    ID ............... {patient['id']}
    Tuổi ............. {patient['tuoi']}
    Giới tính ........ {patient['gioi_tinh']}

  Chỉ số sức khỏe:
    Chiều cao ........ {patient['chieu_cao']} m
    Cân nặng ......... {patient['can_nang']} kg
    BMI .............. {bmi} ({phan_loai_bmi(bmi)})
    Huyết áp ......... {patient['huyet_ap_tam_thu']}/{patient['huyet_ap_tam_truong']} mmHg
    Nhịp tim ......... {patient['nhip_tim']} bpm
    Đường huyết ...... {patient['duong_huyet']} mg/dL
""")

    in_tieu_de_phu("Lịch sử khám bệnh")
    if patient.get("lich_su_kham"):
        kham_data = [
            [v["ngay_kham"], v["loai_benh"], v["bac_si"]]
            for v in patient["lich_su_kham"]
        ]
        print(tabulate(kham_data, headers=["Ngày khám", "Loại bệnh", "Bác sĩ"],
                       tablefmt="rounded_grid"))
    else:
        print("  Chưa có lịch sử khám.")

    in_tieu_de_phu("Lịch sử dùng thuốc")
    if patient.get("lich_su_thuoc"):
        thuoc_data = [
            [t["ten_thuoc"], t["lieu_luong"], t["tan_suat"],
             t["ngay_bat_dau"], t["ngay_ket_thuc"]]
            for t in patient["lich_su_thuoc"]
        ]
        print(tabulate(thuoc_data,
                       headers=["Thuốc", "Liều", "Tần suất", "Bắt đầu", "Kết thúc"],
                       tablefmt="rounded_grid"))
    else:
        print("  Chưa có lịch sử dùng thuốc.")


def xem_phan_tich_bmi(df):
    """Hiển thị phân tích BMI."""
    in_tieu_de("⚖️  PHÂN TÍCH CHỈ SỐ BMI")

    print("""
  Công thức: BMI = Cân nặng (kg) / Chiều cao² (m²)

  Phân loại (WHO - châu Á):
    • Thiếu cân:     BMI < 18.5
    • Bình thường:   18.5 ≤ BMI < 23
    • Thừa cân:      23 ≤ BMI < 25
    • Béo phì độ 1:  25 ≤ BMI < 30
    • Béo phì độ 2:  BMI ≥ 30
""")

    df_bmi, thong_ke, phan_loai, bmi_gt = phan_tich_bmi(df)

    in_tieu_de_phu("Thống kê tổng hợp BMI")
    for key, value in thong_ke.items():
        print(f"  {key:.<30s} {value}")

    in_tieu_de_phu("Phân loại BMI")
    pl_data = [[k, v, f"{v/len(df)*100:.1f}%"] for k, v in phan_loai.items()]
    print(tabulate(pl_data, headers=["Phân loại", "Số BN", "Tỷ lệ"],
                   tablefmt="rounded_grid"))

    in_tieu_de_phu("BMI trung bình theo giới tính")
    print(tabulate(bmi_gt, headers="keys", tablefmt="rounded_grid", floatfmt=".2f"))


def xem_huyet_ap_nhom_tuoi(df):
    """Hiển thị huyết áp trung bình theo nhóm tuổi."""
    in_tieu_de("🩺 HUYẾT ÁP TRUNG BÌNH THEO NHÓM TUỔI")

    print("""
  Phương pháp: Sử dụng pandas.DataFrame.groupby("nhom_tuoi")
               để tính giá trị trung bình (.mean()) cho mỗi nhóm.
""")

    grouped = phan_tich_huyet_ap_theo_nhom_tuoi(df)

    print(tabulate(grouped, headers="keys", tablefmt="rounded_grid",
                   floatfmt=".1f", showindex=True))

    print("""
  Ghi chú:
    • HA Tâm thu bình thường: < 120 mmHg
    • HA Tâm thu cao: 130-139 mmHg  |  Tăng HA giai đoạn 2: ≥ 140 mmHg
    • HA Tâm trương bình thường: < 80 mmHg
""")


def xem_tan_suat_kham(patients):
    """Hiển thị tần suất khám bệnh theo loại bệnh."""
    in_tieu_de("📅 TẦN SUẤT KHÁM BỆNH THEO LOẠI BỆNH")

    result = thong_ke_tan_suat_kham(patients)
    if result.empty:
        print("  Chưa có dữ liệu khám bệnh.")
        return

    print(tabulate(result, headers="keys", tablefmt="rounded_grid",
                   showindex=False, floatfmt=".1f"))
    print(f"\n  Tổng số lượt khám: {result['Số lượt khám'].sum()}")


def xem_thong_ke_thuoc(patients):
    """Hiển thị thống kê dùng thuốc."""
    in_tieu_de("💊 THỐNG KÊ SỬ DỤNG THUỐC")

    result = thong_ke_dung_thuoc(patients)
    if result.empty:
        print("  Chưa có dữ liệu dùng thuốc.")
        return

    print(tabulate(result, headers="keys", tablefmt="rounded_grid",
                   showindex=False, floatfmt=".1f"))


def them_benh_nhan(patients):
    """Thêm bệnh nhân mới."""
    in_tieu_de("➕ THÊM BỆNH NHÂN MỚI")

    try:
        ho_ten = input("  Họ tên: ").strip()
        tuoi = int(input("  Tuổi: "))
        gioi_tinh = input("  Giới tính (Nam/Nữ): ").strip()
        chieu_cao = float(input("  Chiều cao (m): "))
        can_nang = float(input("  Cân nặng (kg): "))
        ha_tt = int(input("  Huyết áp tâm thu (mmHg): "))
        ha_ttr = int(input("  Huyết áp tâm trương (mmHg): "))
        nhip_tim = int(input("  Nhịp tim (bpm): "))
        duong_huyet = float(input("  Đường huyết (mg/dL): "))
    except (ValueError, EOFError):
        print("  [!] Dữ liệu nhập không hợp lệ.")
        return

    new_id = max((p["id"] for p in patients), default=0) + 1
    new_patient = {
        "id": new_id,
        "ho_ten": ho_ten,
        "tuoi": tuoi,
        "gioi_tinh": gioi_tinh,
        "chieu_cao": chieu_cao,
        "can_nang": can_nang,
        "huyet_ap_tam_thu": ha_tt,
        "huyet_ap_tam_truong": ha_ttr,
        "nhip_tim": nhip_tim,
        "duong_huyet": duong_huyet,
        "lich_su_kham": [],
        "lich_su_thuoc": [],
    }
    patients.append(new_patient)
    luu_du_lieu(patients)

    bmi = tinh_bmi(can_nang, chieu_cao)
    print(f"\n  [✓] Đã thêm bệnh nhân: {ho_ten} (ID: {new_id})")
    print(f"  BMI: {bmi} - {phan_loai_bmi(bmi)}")


def tao_bieu_do(df, patients):
    """Tạo tất cả biểu đồ và lưu thành file PNG."""
    in_tieu_de("📊 TẠO BIỂU ĐỒ")

    grouped = phan_tich_huyet_ap_theo_nhom_tuoi(df)
    visit_df = thong_ke_tan_suat_kham(patients)
    med_df = thong_ke_dung_thuoc(patients)

    ve_tat_ca(df, grouped, visit_df, med_df)


def tim_kiem_benh_nhan(patients):
    """Tìm kiếm bệnh nhân theo tên."""
    in_tieu_de("🔎 TÌM KIẾM BỆNH NHÂN")

    keyword = input("  Nhập từ khóa (tên): ").strip().lower()
    if not keyword:
        print("  [!] Vui lòng nhập từ khóa.")
        return

    results = [p for p in patients if keyword in p["ho_ten"].lower()]

    if not results:
        print(f"  Không tìm thấy bệnh nhân với từ khóa '{keyword}'")
        return

    data = []
    for p in results:
        bmi = tinh_bmi(p["can_nang"], p["chieu_cao"])
        data.append([
            p["id"], p["ho_ten"], p["tuoi"], p["gioi_tinh"],
            bmi, f"{p['huyet_ap_tam_thu']}/{p['huyet_ap_tam_truong']}",
        ])

    print(f"\n  Tìm thấy {len(results)} kết quả:\n")
    print(tabulate(data, headers=["ID", "Họ tên", "Tuổi", "GT", "BMI", "Huyết áp"],
                   tablefmt="rounded_grid", floatfmt=".2f"))


# ============================================================
# MENU CHÍNH
# ============================================================

def hien_menu():
    print("""
╔══════════════════════════════════════════════════════════════╗
║            QUẢN LÝ HỒ SƠ BỆNH NHÂN                        ║
╠══════════════════════════════════════════════════════════════╣
║  1. Xem thống kê tổng quan                                  ║
║  2. Danh sách bệnh nhân                                     ║
║  3. Xem chi tiết bệnh nhân                                  ║
║  4. Tìm kiếm bệnh nhân                                      ║
║  5. Phân tích chỉ số BMI                                     ║
║  6. Huyết áp TB theo nhóm tuổi (pandas groupby)             ║
║  7. Tần suất khám bệnh theo loại bệnh                       ║
║  8. Thống kê sử dụng thuốc                                   ║
║  9. Thêm bệnh nhân mới                                      ║
║ 10. Tạo biểu đồ (lưu PNG)                                   ║
║  0. Thoát                                                    ║
╚══════════════════════════════════════════════════════════════╝""")


def main():
    print("\n" + "=" * 62)
    print("  🏥 ỨNG DỤNG QUẢN LÝ HỒ SƠ BỆNH NHÂN")
    print("  Phân tích sức khỏe | BMI | Huyết áp | Lịch sử khám")
    print("=" * 62)

    # Tải dữ liệu
    patients = tai_du_lieu()
    df = tao_dataframe(patients)

    while True:
        hien_menu()
        lua_chon = input("\n  Chọn chức năng (0-10): ").strip()

        if lua_chon == "1":
            xem_tong_quan(df, patients)
        elif lua_chon == "2":
            xem_danh_sach_benh_nhan(df)
        elif lua_chon == "3":
            xem_chi_tiet_benh_nhan(patients)
        elif lua_chon == "4":
            tim_kiem_benh_nhan(patients)
        elif lua_chon == "5":
            xem_phan_tich_bmi(df)
        elif lua_chon == "6":
            xem_huyet_ap_nhom_tuoi(df)
        elif lua_chon == "7":
            xem_tan_suat_kham(patients)
        elif lua_chon == "8":
            xem_thong_ke_thuoc(patients)
        elif lua_chon == "9":
            them_benh_nhan(patients)
            df = tao_dataframe(patients)  # Cập nhật DataFrame
        elif lua_chon == "10":
            tao_bieu_do(df, patients)
        elif lua_chon == "0":
            print("\n  Cảm ơn đã sử dụng! Tạm biệt. 👋\n")
            break
        else:
            print("  [!] Lựa chọn không hợp lệ. Vui lòng chọn 0-10.")

        input("\n  Nhấn Enter để tiếp tục...")


if __name__ == "__main__":
    main()
