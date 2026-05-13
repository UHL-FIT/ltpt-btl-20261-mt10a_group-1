"""
models/examination.py
=====================
Module Model xử lý nghiệp vụ CRUD cho lịch sử khám bệnh.
"""

import pandas as pd
from models.db_manager import lay_ket_noi
from utils.logger import setup_logger

logger = setup_logger()


def lay_lich_su_kham(ma_bn):
    """
    Lấy toàn bộ lịch sử khám bệnh của một bệnh nhân.

    Args:
        ma_bn (str): Mã bệnh nhân.

    Returns:
        tuple: (pandas.DataFrame, bool)
    """
    conn = lay_ket_noi()
    try:
        df = pd.read_sql_query(
            "SELECT * FROM examinations WHERE ma_bn = ? ORDER BY ngay_kham DESC",
            conn, params=(ma_bn,)
        )
        return df, True
    except Exception as e:
        logger.error(f"Lỗi đọc lịch sử khám ({ma_bn}): {e}", exc_info=True)
        return pd.DataFrame(), False
    finally:
        conn.close()


def them_lan_kham(ma_bn, data):
    """
    Thêm một lần khám mới cho bệnh nhân.

    Args:
        ma_bn (str): Mã bệnh nhân.
        data (dict): ngay_kham, trieu_chung, chan_doan, huyet_ap, nhiet_do, bac_si, ghi_chu.

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
            INSERT INTO examinations (ma_bn, ngay_kham, trieu_chung, chan_doan, huyet_ap, nhiet_do, bac_si, ghi_chu)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ma_bn,
            data.get("ngay_kham", ""),
            data.get("trieu_chung", ""),
            data.get("chan_doan", ""),
            data.get("huyet_ap", ""),
            data.get("nhiet_do", None),
            data.get("bac_si", ""),
            data.get("ghi_chu", "")
        ))
        conn.commit()
        logger.info(f"Đã thêm lần khám cho BN: {ma_bn}")
        return True, "Thêm lần khám thành công!"
    except Exception as e:
        conn.rollback()
        logger.error(f"Lỗi thêm lần khám: {e}", exc_info=True)
        return False, f"Lỗi: {e}"
    finally:
        conn.close()


def xoa_lan_kham(exam_id):
    """
    Xóa một lần khám theo ID.

    Args:
        exam_id (int): ID lần khám.

    Returns:
        tuple: (bool, str)
    """
    conn = lay_ket_noi()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM examinations WHERE id = ?", (exam_id,))
        if cursor.rowcount == 0:
            return False, "Không tìm thấy lần khám!"
        conn.commit()
        logger.info(f"Đã xóa lần khám ID: {exam_id}")
        return True, "Xóa lần khám thành công!"
    except Exception as e:
        conn.rollback()
        logger.error(f"Lỗi xóa lần khám: {e}", exc_info=True)
        return False, f"Lỗi: {e}"
    finally:
        conn.close()
