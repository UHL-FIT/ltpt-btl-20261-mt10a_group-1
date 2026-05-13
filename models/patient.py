"""
models/patient.py
=================
Module Model xử lý nghiệp vụ CRUD cho bệnh nhân.
Sử dụng Pandas DataFrame làm cấu trúc dữ liệu trung gian và SQLite để lưu trữ.
"""

import pandas as pd
import numpy as np
from models.db_manager import lay_ket_noi, lay_ma_bn_moi
from utils.bmi_calculator import tinh_bmi, phan_loai_bmi
from utils.logger import setup_logger

logger = setup_logger()


def lay_danh_sach():
    """
    Đọc toàn bộ danh sách bệnh nhân từ database và tính toán BMI.

    Returns:
        tuple: (pandas.DataFrame chứa dữ liệu, bool Trạng thái thành công)
    """
    conn = lay_ket_noi()
    try:
        df = pd.read_sql_query("SELECT * FROM patients ORDER BY ngay_tao DESC", conn)

        if df.empty:
            return df, True

        # Xử lý giá trị NaN cho các cột text
        for text_col in ["ho_ten", "gioi_tinh", "sdt", "dia_chi", "benh_chinh", "benh_phu", "ghi_chu"]:
            if text_col in df.columns:
                df[text_col] = df[text_col].fillna("").astype(str).replace("nan", "")

        # Xử lý giá trị NaN cho các cột số
        for num_col in ["tuoi", "chieu_cao", "can_nang"]:
            if num_col in df.columns:
                df[num_col] = pd.to_numeric(df[num_col], errors="coerce").fillna(0)

        # TÍNH TOÁN BMI BẰNG NUMPY (Vectorization)
        chieu_cao_arr = df["chieu_cao"].values
        can_nang_arr = df["can_nang"].values

        # Tính BMI: kg / (m^2)
        chieu_cao_m = np.where(chieu_cao_arr > 0, chieu_cao_arr / 100.0, 1.0)
        bmi_arr = np.where(
            (chieu_cao_arr > 0) & (can_nang_arr > 0),
            can_nang_arr / (chieu_cao_m ** 2),
            0.0
        )
        bmi_arr = np.round(bmi_arr, 1)

        df["bmi"] = bmi_arr
        df["phan_loai_bmi"] = df["bmi"].apply(phan_loai_bmi)

        return df, True

    except Exception as e:
        logger.error(f"Lỗi đọc danh sách bệnh nhân: {e}", exc_info=True)
        return pd.DataFrame(), False
    finally:
        conn.close()


def them_benh_nhan(data):
    """
    Thêm bệnh nhân mới vào database.

    Args:
        data (dict): Thông tin bệnh nhân gồm các khóa:
            ho_ten, tuoi, gioi_tinh, sdt, dia_chi,
            chieu_cao, can_nang, ngay_tiep_nhan, benh_chinh, benh_phu, ghi_chu.

    Returns:
        tuple: (bool Trạng thái, str Thông báo, str Mã BN mới)
    """
    ma_bn = lay_ma_bn_moi()
    conn = lay_ket_noi()

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO patients (ma_bn, ho_ten, tuoi, gioi_tinh, sdt, dia_chi,
                                  chieu_cao, can_nang, ngay_tiep_nhan, benh_chinh, benh_phu, ghi_chu)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ma_bn,
            data.get("ho_ten", ""),
            data.get("tuoi", None),
            data.get("gioi_tinh", "Nam"),
            data.get("sdt", ""),
            data.get("dia_chi", ""),
            data.get("chieu_cao", None),
            data.get("can_nang", None),
            data.get("ngay_tiep_nhan", ""),
            data.get("benh_chinh", ""),
            data.get("benh_phu", ""),
            data.get("ghi_chu", "")
        ))
        conn.commit()
        logger.info(f"Đã thêm bệnh nhân: {data.get('ho_ten', '')} ({ma_bn})")
        return True, f"Thêm bệnh nhân thành công: {ma_bn}", ma_bn

    except Exception as e:
        conn.rollback()
        logger.error(f"Lỗi thêm bệnh nhân: {e}", exc_info=True)
        return False, f"Lỗi: {e}", None
    finally:
        conn.close()


def sua_benh_nhan(ma_bn, data):
    """
    Cập nhật thông tin bệnh nhân đã tồn tại.

    Args:
        ma_bn (str): Mã bệnh nhân cần sửa.
        data (dict): Thông tin mới của bệnh nhân.

    Returns:
        tuple: (bool Trạng thái, str Thông báo)
    """
    conn = lay_ket_noi()

    try:
        cursor = conn.cursor()

        # Kiểm tra bệnh nhân có tồn tại không
        cursor.execute("SELECT ma_bn FROM patients WHERE ma_bn = ?", (ma_bn,))
        if cursor.fetchone() is None:
            return False, f"Không tìm thấy bệnh nhân {ma_bn}!"

        cursor.execute("""
            UPDATE patients SET
                ho_ten = ?, tuoi = ?, gioi_tinh = ?, sdt = ?, dia_chi = ?,
                chieu_cao = ?, can_nang = ?, ngay_tiep_nhan = ?,
                benh_chinh = ?, benh_phu = ?, ghi_chu = ?
            WHERE ma_bn = ?
        """, (
            data.get("ho_ten", ""),
            data.get("tuoi", None),
            data.get("gioi_tinh", "Nam"),
            data.get("sdt", ""),
            data.get("dia_chi", ""),
            data.get("chieu_cao", None),
            data.get("can_nang", None),
            data.get("ngay_tiep_nhan", ""),
            data.get("benh_chinh", ""),
            data.get("benh_phu", ""),
            data.get("ghi_chu", ""),
            ma_bn
        ))
        conn.commit()
        logger.info(f"Đã sửa bệnh nhân: {ma_bn}")
        return True, f"Cập nhật thành công: {ma_bn}"

    except Exception as e:
        conn.rollback()
        logger.error(f"Lỗi sửa bệnh nhân: {e}", exc_info=True)
        return False, f"Lỗi: {e}"
    finally:
        conn.close()


def xoa_benh_nhan(ma_bn):
    """
    Xóa một bệnh nhân khỏi database (cascade xóa lịch sử khám + thuốc).

    Args:
        ma_bn (str): Mã bệnh nhân cần xóa.

    Returns:
        tuple: (bool Trạng thái, str Thông báo)
    """
    conn = lay_ket_noi()

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE ma_bn = ?", (ma_bn,))

        if cursor.rowcount == 0:
            return False, f"Không tìm thấy bệnh nhân {ma_bn}!"

        conn.commit()
        logger.info(f"Đã xóa bệnh nhân: {ma_bn}")
        return True, "Xóa thành công!"

    except Exception as e:
        conn.rollback()
        logger.error(f"Lỗi xóa bệnh nhân: {e}", exc_info=True)
        return False, f"Lỗi: {e}"
    finally:
        conn.close()


def xoa_nhieu_benh_nhan(ma_bn_list):
    """
    Xóa nhiều bệnh nhân cùng lúc.

    Args:
        ma_bn_list (list): Danh sách mã bệnh nhân cần xóa.

    Returns:
        tuple: (bool Trạng thái, str Thông báo)
    """
    if not ma_bn_list:
        return False, "Danh sách trống!"

    conn = lay_ket_noi()

    try:
        cursor = conn.cursor()
        placeholders = ",".join(["?" for _ in ma_bn_list])
        cursor.execute(f"DELETE FROM patients WHERE ma_bn IN ({placeholders})", ma_bn_list)
        deleted = cursor.rowcount
        conn.commit()
        logger.info(f"Đã xóa {deleted} bệnh nhân")
        return True, f"Đã xóa {deleted} bệnh nhân!"

    except Exception as e:
        conn.rollback()
        logger.error(f"Lỗi xóa nhiều bệnh nhân: {e}", exc_info=True)
        return False, f"Lỗi: {e}"
    finally:
        conn.close()


def tim_kiem(keyword, field="tat_ca"):
    """
    Tìm kiếm bệnh nhân theo từ khóa và trường chỉ định.

    Args:
        keyword (str): Từ khóa tìm kiếm.
        field (str): Trường tìm kiếm ('tat_ca', 'ma_bn', 'ho_ten', 'gioi_tinh', 'sdt', 'benh_chinh').

    Returns:
        tuple: (pandas.DataFrame kết quả, bool Trạng thái)
    """
    df, ok = lay_danh_sach()
    if not ok or df.empty:
        return df, ok

    keyword = str(keyword).strip().lower()
    if not keyword:
        return df, True

    if field == "ma_bn":
        mask = df["ma_bn"].astype(str).str.lower().str.contains(keyword, na=False)
    elif field == "ho_ten":
        mask = df["ho_ten"].astype(str).str.lower().str.contains(keyword, na=False)
    elif field == "gioi_tinh":
        mask = df["gioi_tinh"].astype(str).str.lower().str.contains(keyword, na=False)
    elif field == "sdt":
        mask = df["sdt"].astype(str).str.lower().str.contains(keyword, na=False)
    elif field == "benh_chinh":
        mask = df["benh_chinh"].astype(str).str.lower().str.contains(keyword, na=False)
    else:  # "tat_ca"
        mask = df.apply(
            lambda row: row.astype(str).str.lower().str.contains(keyword).any(),
            axis=1
        )

    return df[mask], True


def thong_ke(df=None):
    """
    Trích xuất thống kê tổng quan từ dữ liệu bệnh nhân.

    Args:
        df (pandas.DataFrame, optional): DataFrame bệnh nhân. Nếu None, sẽ tự lấy từ DB.

    Returns:
        dict: Chứa các trường thống kê (tong_bn, nam, nu, tuoi_tb, bmi_tb...).
    """
    if df is None:
        df, ok = lay_danh_sach()
        if not ok:
            return {}

    if df.empty:
        return {
            "tong_bn": 0, "nam": 0, "nu": 0,
            "tuoi_tb": 0.0, "bmi_tb": 0.0,
            "benh_pho_bien": "N/A"
        }

    stats = {
        "tong_bn": len(df),
        "nam": int(np.sum(df["gioi_tinh"].str.strip().str.lower() == "nam")),
        "nu": int(np.sum(df["gioi_tinh"].str.strip().str.lower() == "nữ")),
        "tuoi_tb": float(np.mean(df["tuoi"].values)) if df["tuoi"].sum() > 0 else 0.0,
    }

    # BMI trung bình (chỉ tính các giá trị > 0)
    bmi_valid = df["bmi"].values[df["bmi"].values > 0]
    stats["bmi_tb"] = float(np.mean(bmi_valid)) if len(bmi_valid) > 0 else 0.0

    # Bệnh phổ biến nhất
    benh_series = df["benh_chinh"].replace("", np.nan).dropna()
    if not benh_series.empty:
        stats["benh_pho_bien"] = benh_series.mode().iloc[0]
    else:
        stats["benh_pho_bien"] = "N/A"

    return stats
