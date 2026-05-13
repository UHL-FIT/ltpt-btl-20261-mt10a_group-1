"""
models/medication.py
====================
Module Model xử lý nghiệp vụ CRUD cho lịch sử thuốc.
"""

import pandas as pd
from models.db_manager import lay_ket_noi
from utils.logger import setup_logger

logger = setup_logger()


def lay_lich_su_thuoc(ma_bn):
    """
    Lấy toàn bộ lịch sử thuốc của một bệnh nhân.

    Args:
        ma_bn (str): Mã bệnh nhân.

    Returns:
        tuple: (pandas.DataFrame, bool)
    """
    conn = lay_ket_noi()
    try:
        df = pd.read_sql_query(
            "SELECT * FROM medications WHERE ma_bn = ? ORDER BY ngay_bat_dau DESC",
            conn, params=(ma_bn,)
        )
        return df, True
    except Exception as e:
        logger.error(f"Lỗi đọc lịch sử thuốc ({ma_bn}): {e}", exc_info=True)
        return pd.DataFrame(), False
    finally:
        conn.close()


def them_thuoc(ma_bn, data):
    """
    Thêm một loại thuốc mới cho bệnh nhân.

    Args:
        ma_bn (str): Mã bệnh nhân.
        data (dict): ten_thuoc, lieu_luong, tan_suat, ngay_bat_dau, ngay_ket_thuc, ghi_chu.

    Returns:
        tuple: (bool, str)
    """
    conn = lay_ket_noi()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ma_bn FROM patients WHERE ma_bn = ?", (ma_bn,))
        if cursor.fetchone() is None:
            return False, f"Không tìm thấy bệnh nhân {ma_bn}!"

        cursor.execute("""
            INSERT INTO medications (ma_bn, examination_id, ten_thuoc, lieu_luong, tan_suat,
                                     ngay_bat_dau, ngay_ket_thuc, ghi_chu)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ma_bn,
            data.get("examination_id", None),
            data.get("ten_thuoc", ""),
            data.get("lieu_luong", ""),
            data.get("tan_suat", ""),
            data.get("ngay_bat_dau", ""),
            data.get("ngay_ket_thuc", ""),
            data.get("ghi_chu", "")
        ))
        conn.commit()
        logger.info(f"Đã thêm thuốc cho BN: {ma_bn}")
        return True, "Thêm thuốc thành công!"
    except Exception as e:
        conn.rollback()
        logger.error(f"Lỗi thêm thuốc: {e}", exc_info=True)
        return False, f"Lỗi: {e}"
    finally:
        conn.close()


def xoa_thuoc(med_id):
    """
    Xóa một loại thuốc theo ID.

    Args:
        med_id (int): ID thuốc.

    Returns:
        tuple: (bool, str)
    """
    conn = lay_ket_noi()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM medications WHERE id = ?", (med_id,))
        if cursor.rowcount == 0:
            return False, "Không tìm thấy thuốc!"
        conn.commit()
        logger.info(f"Đã xóa thuốc ID: {med_id}")
        return True, "Xóa thuốc thành công!"
    except Exception as e:
        conn.rollback()
        logger.error(f"Lỗi xóa thuốc: {e}", exc_info=True)
        return False, f"Lỗi: {e}"
    finally:
        conn.close()
