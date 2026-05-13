"""
utils/bmi_calculator.py
=======================
Công thức tính chỉ số BMI (Body Mass Index) và phân loại theo WHO.
"""


def tinh_bmi(chieu_cao_cm, can_nang_kg):
    """
    Tính chỉ số BMI từ chiều cao (cm) và cân nặng (kg).

    Args:
        chieu_cao_cm (float): Chiều cao tính bằng centimet.
        can_nang_kg (float): Cân nặng tính bằng kilogram.

    Returns:
        float: Giá trị BMI (làm tròn 1 chữ số thập phân), hoặc 0.0 nếu dữ liệu không hợp lệ.
    """
    try:
        chieu_cao_cm = float(chieu_cao_cm)
        can_nang_kg = float(can_nang_kg)
    except (ValueError, TypeError):
        return 0.0

    if chieu_cao_cm <= 0 or can_nang_kg <= 0:
        return 0.0

    chieu_cao_m = chieu_cao_cm / 100.0
    bmi = can_nang_kg / (chieu_cao_m ** 2)
    return round(bmi, 1)


def phan_loai_bmi(bmi):
    """
    Phân loại BMI theo tiêu chuẩn WHO dành cho người châu Á.

    Args:
        bmi (float): Giá trị BMI.

    Returns:
        str: Chuỗi phân loại tình trạng cân nặng.
    """
    try:
        bmi = float(bmi)
    except (ValueError, TypeError):
        return "N/A"

    if bmi <= 0:
        return "N/A"
    elif bmi < 18.5:
        return "Thiếu cân"
    elif bmi < 23.0:
        return "Bình thường"
    elif bmi < 25.0:
        return "Thừa cân"
    elif bmi < 30.0:
        return "Béo phì độ I"
    else:
        return "Béo phì độ II"
