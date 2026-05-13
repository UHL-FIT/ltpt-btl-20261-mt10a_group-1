"""
controllers/stats_controller.py
===============================
Controller cho module thống kê. Dùng Pandas groupby, agg để tính toán.
"""

import pandas as pd
import numpy as np
from models import patient as patient_model
from models import examination as exam_model
from models.db_manager import lay_ket_noi
from utils.logger import setup_logger

logger = setup_logger()


def thong_ke_tong_hop():
    """
    Tính toán thống kê tổng hợp cho toàn bộ bệnh nhân.

    Returns:
        dict: Chứa các trường thống kê chi tiết.
    """
    df, ok = patient_model.lay_danh_sach()
    if not ok or df.empty:
        return {}

    stats = patient_model.thong_ke(df)

    # Thống kê BMI theo phân loại
    if 'phan_loai_bmi' in df.columns:
        bmi_groups = df[df['bmi'] > 0].groupby('phan_loai_bmi').size().to_dict()
        stats['bmi_phan_loai'] = bmi_groups

    # Thống kê tuổi theo nhóm
    bins = [0, 18, 30, 45, 60, 150]
    labels = ['<18', '18-30', '31-45', '46-60', '>60']
    df['nhom_tuoi'] = pd.cut(df['tuoi'], bins=bins, labels=labels, right=True)
    stats['nhom_tuoi'] = df['nhom_tuoi'].value_counts().to_dict()

    return stats


def thong_ke_benh():
    """
    Thống kê tần suất các bệnh.

    Returns:
        pandas.DataFrame: Bảng thống kê bệnh (tên, số lượng, tỉ lệ).
    """
    df, ok = patient_model.lay_danh_sach()
    if not ok or df.empty:
        return pd.DataFrame()

    benh_series = df['benh_chinh'].replace("", np.nan).dropna()
    if benh_series.empty:
        return pd.DataFrame()

    benh_counts = benh_series.value_counts().reset_index()
    benh_counts.columns = ['Bệnh', 'Số ca']
    benh_counts['Tỉ lệ (%)'] = (benh_counts['Số ca'] / benh_counts['Số ca'].sum() * 100).round(1)

    return benh_counts


def thong_ke_kham_theo_thang():
    """
    Thống kê tần suất khám bệnh theo tháng.

    Returns:
        pandas.DataFrame: Bảng thống kê (tháng, số lần khám).
    """
    conn = lay_ket_noi()
    try:
        df = pd.read_sql_query("SELECT ngay_kham FROM examinations", conn)
        if df.empty:
            return pd.DataFrame()

        # Parse ngày
        df['thang'] = pd.to_datetime(df['ngay_kham'], format='%d/%m/%Y', errors='coerce').dt.to_period('M')
        result = df.groupby('thang').size().reset_index(name='Số lần khám')
        result.columns = ['Tháng', 'Số lần khám']
        return result
    except Exception as e:
        logger.error(f"Lỗi thống kê khám theo tháng: {e}", exc_info=True)
        return pd.DataFrame()
    finally:
        conn.close()
