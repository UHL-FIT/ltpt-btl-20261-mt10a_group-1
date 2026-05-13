"""
Module phân tích dữ liệu sức khỏe bệnh nhân.
Sử dụng pandas để:
  - Tính chỉ số BMI theo công thức
  - Tính trung bình huyết áp theo nhóm tuổi (pandas groupby)
  - Thống kê tần suất khám bệnh theo loại bệnh
"""

import pandas as pd
import numpy as np


# ============================================================
# 1. TÍNH CHỈ SỐ BMI
# ============================================================

def tinh_bmi(can_nang, chieu_cao):
    """
    Tính chỉ số BMI theo công thức:
        BMI = cân nặng (kg) / chiều cao² (m²)

    Args:
        can_nang (float): Cân nặng tính bằng kg.
        chieu_cao (float): Chiều cao tính bằng mét.

    Returns:
        float: Chỉ số BMI làm tròn 2 chữ số thập phân.
    """
    if chieu_cao <= 0:
        return 0.0
    return round(can_nang / (chieu_cao ** 2), 2)


def phan_loai_bmi(bmi):
    """
    Phân loại BMI theo tiêu chuẩn WHO cho người châu Á.

    Returns:
        str: Phân loại BMI.
    """
    if bmi < 18.5:
        return "Thiếu cân"
    elif bmi < 23.0:
        return "Bình thường"
    elif bmi < 25.0:
        return "Thừa cân"
    elif bmi < 30.0:
        return "Béo phì độ 1"
    else:
        return "Béo phì độ 2"


def phan_tich_bmi(df):
    """
    Tính BMI cho toàn bộ DataFrame bệnh nhân và thống kê.

    Args:
        df (pd.DataFrame): DataFrame chứa cột 'can_nang' và 'chieu_cao'.

    Returns:
        pd.DataFrame: DataFrame đã thêm cột 'bmi' và 'phan_loai_bmi'.
        dict: Thống kê BMI tổng hợp.
    """
    df = df.copy()

    # Tính BMI: BMI = cân nặng (kg) / chiều cao² (m²)
    df["bmi"] = df.apply(
        lambda row: tinh_bmi(row["can_nang"], row["chieu_cao"]),
        axis=1,
    )
    df["phan_loai_bmi"] = df["bmi"].apply(phan_loai_bmi)

    # Thống kê tổng hợp
    thong_ke = {
        "BMI trung bình": round(df["bmi"].mean(), 2),
        "BMI cao nhất": round(df["bmi"].max(), 2),
        "BMI thấp nhất": round(df["bmi"].min(), 2),
        "Độ lệch chuẩn": round(df["bmi"].std(), 2),
    }

    # Phân loại BMI
    phan_loai = df["phan_loai_bmi"].value_counts()

    # BMI trung bình theo giới tính
    bmi_gioi_tinh = df.groupby("gioi_tinh")["bmi"].agg(["mean", "min", "max", "count"])
    bmi_gioi_tinh.columns = ["TB", "Thấp nhất", "Cao nhất", "Số BN"]
    bmi_gioi_tinh = bmi_gioi_tinh.round(2)

    return df, thong_ke, phan_loai, bmi_gioi_tinh


# ============================================================
# 2. HUYẾT ÁP TRUNG BÌNH THEO NHÓM TUỔI (pandas groupby)
# ============================================================

def nhom_tuoi(tuoi):
    """Phân nhóm tuổi cho bệnh nhân."""
    if tuoi < 18:
        return "Trẻ em (0-17)"
    elif tuoi < 30:
        return "Thanh niên (18-29)"
    elif tuoi < 45:
        return "Trung niên (30-44)"
    elif tuoi < 60:
        return "Trung cao (45-59)"
    else:
        return "Cao tuổi (60+)"


def phan_tich_huyet_ap_theo_nhom_tuoi(df):
    """
    Sử dụng pandas groupby để tính trung bình huyết áp theo nhóm tuổi.

    Phương pháp:
        1. Tạo cột 'nhom_tuoi' dựa trên tuổi
        2. Sử dụng df.groupby("nhom_tuoi").agg() để tính trung bình
        3. Kết quả gồm: HA tâm thu, HA tâm trương, nhịp tim, đường huyết

    Args:
        df (pd.DataFrame): DataFrame chứa thông tin bệnh nhân.

    Returns:
        pd.DataFrame: Bảng thống kê trung bình theo nhóm tuổi.
    """
    df = df.copy()
    df["nhom_tuoi"] = df["tuoi"].apply(nhom_tuoi)

    # ===============================================================
    # SỬ DỤNG PANDAS GROUPBY ĐỂ TÍNH TRUNG BÌNH THEO NHÓM TUỔI
    # ===============================================================
    grouped = df.groupby("nhom_tuoi").agg(
        so_benh_nhan=("id", "count"),
        tuoi_tb=("tuoi", "mean"),
        ha_tam_thu_tb=("huyet_ap_tam_thu", "mean"),
        ha_tam_truong_tb=("huyet_ap_tam_truong", "mean"),
        nhip_tim_tb=("nhip_tim", "mean"),
        duong_huyet_tb=("duong_huyet", "mean"),
    ).round(1)

    # Sắp xếp theo thứ tự nhóm tuổi
    thu_tu = [
        "Trẻ em (0-17)", "Thanh niên (18-29)",
        "Trung niên (30-44)", "Trung cao (45-59)", "Cao tuổi (60+)",
    ]
    grouped = grouped.reindex([t for t in thu_tu if t in grouped.index])

    # Đổi tên cột cho dễ đọc
    grouped.columns = [
        "Số BN", "Tuổi TB",
        "HA Tâm thu TB", "HA Tâm trương TB",
        "Nhịp tim TB", "Đường huyết TB",
    ]

    return grouped


# ============================================================
# 3. THỐNG KÊ TẦN SUẤT KHÁM BỆNH THEO LOẠI BỆNH
# ============================================================

def thong_ke_tan_suat_kham(patients):
    """
    Thống kê tần suất khám bệnh theo loại bệnh.

    Args:
        patients (list): Danh sách dict hồ sơ bệnh nhân.

    Returns:
        pd.DataFrame: Bảng thống kê tần suất khám theo loại bệnh.
    """
    # Trích xuất tất cả lượt khám
    all_visits = []
    for p in patients:
        for visit in p.get("lich_su_kham", []):
            all_visits.append({
                "benh_nhan_id": p["id"],
                "loai_benh": visit["loai_benh"],
                "ngay_kham": visit["ngay_kham"],
            })

    if not all_visits:
        return pd.DataFrame()

    df_visits = pd.DataFrame(all_visits)

    # Đếm số lượt khám theo loại bệnh
    tan_suat = df_visits["loai_benh"].value_counts().reset_index()
    tan_suat.columns = ["Loại bệnh", "Số lượt khám"]

    # Số bệnh nhân riêng biệt cho mỗi loại bệnh
    bn_unique = df_visits.groupby("loai_benh")["benh_nhan_id"].nunique().reset_index()
    bn_unique.columns = ["Loại bệnh", "Số BN"]

    # Ghép kết quả
    result = tan_suat.merge(bn_unique, on="Loại bệnh")

    # Tính tỷ lệ phần trăm
    tong = result["Số lượt khám"].sum()
    result["Tỷ lệ (%)"] = (result["Số lượt khám"] / tong * 100).round(1)

    return result


# ============================================================
# 4. THỐNG KÊ DÙNG THUỐC
# ============================================================

def thong_ke_dung_thuoc(patients):
    """
    Thống kê tần suất sử dụng thuốc.

    Args:
        patients (list): Danh sách dict hồ sơ bệnh nhân.

    Returns:
        pd.DataFrame: Bảng thống kê sử dụng thuốc.
    """
    all_meds = []
    for p in patients:
        for med in p.get("lich_su_thuoc", []):
            all_meds.append({
                "benh_nhan_id": p["id"],
                "ten_thuoc": med["ten_thuoc"],
                "lieu_luong": med["lieu_luong"],
            })

    if not all_meds:
        return pd.DataFrame()

    df_meds = pd.DataFrame(all_meds)
    tan_suat = df_meds["ten_thuoc"].value_counts().reset_index()
    tan_suat.columns = ["Tên thuốc", "Số lượt dùng"]

    bn_unique = df_meds.groupby("ten_thuoc")["benh_nhan_id"].nunique().reset_index()
    bn_unique.columns = ["Tên thuốc", "Số BN"]

    result = tan_suat.merge(bn_unique, on="Tên thuốc")
    tong = result["Số lượt dùng"].sum()
    result["Tỷ lệ (%)"] = (result["Số lượt dùng"] / tong * 100).round(1)

    return result


# ============================================================
# 5. THỐNG KÊ TỔNG QUAN
# ============================================================

def thong_ke_tong_quan(df, patients):
    """
    Tạo bảng thống kê tổng quan về toàn bộ dữ liệu bệnh nhân.

    Returns:
        dict: Các chỉ số tổng quan.
    """
    df = df.copy()
    df["bmi"] = df.apply(lambda r: tinh_bmi(r["can_nang"], r["chieu_cao"]), axis=1)

    tong_luot_kham = sum(len(p.get("lich_su_kham", [])) for p in patients)

    return {
        "Tổng số bệnh nhân": len(patients),
        "Nam": int((df["gioi_tinh"] == "Nam").sum()),
        "Nữ": int((df["gioi_tinh"] == "Nữ").sum()),
        "Tuổi trung bình": round(df["tuoi"].mean(), 1),
        "Tuổi nhỏ nhất": int(df["tuoi"].min()),
        "Tuổi lớn nhất": int(df["tuoi"].max()),
        "BMI trung bình": round(df["bmi"].mean(), 2),
        "HA tâm thu TB": round(df["huyet_ap_tam_thu"].mean(), 1),
        "HA tâm trương TB": round(df["huyet_ap_tam_truong"].mean(), 1),
        "Tổng lượt khám": tong_luot_kham,
    }


def tao_dataframe(patients):
    """
    Chuyển danh sách hồ sơ bệnh nhân (list of dict) thành pandas DataFrame.

    Args:
        patients (list): Danh sách dict.

    Returns:
        pd.DataFrame: DataFrame bệnh nhân (chỉ các cột chính).
    """
    records = []
    for p in patients:
        records.append({
            "id": p["id"],
            "ho_ten": p["ho_ten"],
            "tuoi": p["tuoi"],
            "gioi_tinh": p["gioi_tinh"],
            "chieu_cao": p["chieu_cao"],
            "can_nang": p["can_nang"],
            "huyet_ap_tam_thu": p["huyet_ap_tam_thu"],
            "huyet_ap_tam_truong": p["huyet_ap_tam_truong"],
            "nhip_tim": p["nhip_tim"],
            "duong_huyet": p["duong_huyet"],
            "so_lan_kham": len(p.get("lich_su_kham", [])),
        })
    return pd.DataFrame(records)
