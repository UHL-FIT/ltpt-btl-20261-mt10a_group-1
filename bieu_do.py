"""
Module vẽ biểu đồ thống kê sức khỏe bệnh nhân.
Sử dụng matplotlib để tạo các biểu đồ và lưu thành file PNG.
"""

import matplotlib
matplotlib.use("Agg")  # Backend không cần GUI
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os

from phan_tich import tinh_bmi, phan_loai_bmi, nhom_tuoi

# Thư mục lưu biểu đồ
CHART_DIR = os.path.join(os.path.dirname(__file__), "bieu_do")


def _setup_style():
    """Thiết lập style chung cho biểu đồ."""
    plt.rcParams.update({
        "figure.facecolor": "#1a1a2e",
        "axes.facecolor": "#16213e",
        "axes.edgecolor": "#444",
        "axes.labelcolor": "white",
        "text.color": "white",
        "xtick.color": "#ccc",
        "ytick.color": "#ccc",
        "grid.color": "#333",
        "grid.alpha": 0.3,
        "font.size": 11,
    })


def _save(fig, filename):
    """Lưu biểu đồ."""
    os.makedirs(CHART_DIR, exist_ok=True)
    path = os.path.join(CHART_DIR, filename)
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  [✓] Đã lưu biểu đồ: {path}")
    return path


def ve_bieu_do_bmi(df):
    """Vẽ biểu đồ phân bố BMI."""
    _setup_style()
    df = df.copy()
    df["bmi"] = df.apply(lambda r: tinh_bmi(r["can_nang"], r["chieu_cao"]), axis=1)
    df["phan_loai"] = df["bmi"].apply(phan_loai_bmi)

    colors_map = {
        "Thiếu cân": "#3b82f6",
        "Bình thường": "#10b981",
        "Thừa cân": "#f59e0b",
        "Béo phì độ 1": "#ef4444",
        "Béo phì độ 2": "#7c3aed",
    }

    counts = df["phan_loai"].value_counts()
    labels = counts.index.tolist()
    values = counts.values
    colors = [colors_map.get(l, "#888") for l in labels]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Biểu đồ tròn
    wedges, texts, autotexts = ax1.pie(
        values, labels=labels, colors=colors, autopct="%1.1f%%",
        startangle=90, textprops={"fontsize": 10},
    )
    for t in autotexts:
        t.set_color("white")
        t.set_fontweight("bold")
    ax1.set_title("Phân loại BMI", fontsize=14, fontweight="bold", pad=15)

    # Biểu đồ histogram
    ax2.hist(df["bmi"], bins=20, color="#6366f1", edgecolor="#1a1a2e", alpha=0.85)
    ax2.axvline(18.5, color="#3b82f6", linestyle="--", linewidth=1, label="18.5")
    ax2.axvline(23, color="#10b981", linestyle="--", linewidth=1, label="23")
    ax2.axvline(25, color="#f59e0b", linestyle="--", linewidth=1, label="25")
    ax2.axvline(30, color="#ef4444", linestyle="--", linewidth=1, label="30")
    ax2.set_xlabel("Chỉ số BMI")
    ax2.set_ylabel("Số bệnh nhân")
    ax2.set_title("Phân bố chỉ số BMI", fontsize=14, fontweight="bold", pad=15)
    ax2.legend(title="Ngưỡng BMI", fontsize=9)
    ax2.grid(True, axis="y")

    fig.suptitle("PHÂN TÍCH CHỈ SỐ BMI", fontsize=16, fontweight="bold", y=1.02)
    fig.tight_layout()
    return _save(fig, "phan_tich_bmi.png")


def ve_bieu_do_huyet_ap(grouped_df):
    """Vẽ biểu đồ huyết áp trung bình theo nhóm tuổi."""
    _setup_style()

    labels = grouped_df.index.tolist()
    # Rút ngắn nhãn
    short_labels = [l.split("(")[0].strip() for l in labels]

    ha_tt = grouped_df["HA Tâm thu TB"].values
    ha_ttr = grouped_df["HA Tâm trương TB"].values

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))

    bars1 = ax.bar(x - width/2, ha_tt, width, color="#ef4444", alpha=0.85, label="HA Tâm thu TB")
    bars2 = ax.bar(x + width/2, ha_ttr, width, color="#3b82f6", alpha=0.85, label="HA Tâm trương TB")

    # Thêm giá trị lên cột
    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{bar.get_height():.1f}", ha="center", va="bottom", fontsize=9, fontweight="bold")
    for bar in bars2:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{bar.get_height():.1f}", ha="center", va="bottom", fontsize=9, fontweight="bold")

    # Đường ngưỡng
    ax.axhline(140, color="#fbbf24", linestyle="--", linewidth=1, alpha=0.7, label="Ngưỡng HA cao (140)")
    ax.axhline(90, color="#a78bfa", linestyle="--", linewidth=1, alpha=0.7, label="Ngưỡng HA TT cao (90)")

    ax.set_xlabel("Nhóm tuổi")
    ax.set_ylabel("Huyết áp (mmHg)")
    ax.set_title("HUYẾT ÁP TRUNG BÌNH THEO NHÓM TUỔI\n(Sử dụng pandas groupby)", fontsize=14, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(short_labels, fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, axis="y")

    fig.tight_layout()
    return _save(fig, "huyet_ap_nhom_tuoi.png")


def ve_bieu_do_tan_suat_kham(visit_df):
    """Vẽ biểu đồ tần suất khám bệnh theo loại bệnh."""
    _setup_style()

    top_n = visit_df.head(10)  # Top 10 loại bệnh
    labels = top_n["Loại bệnh"].tolist()
    values = top_n["Số lượt khám"].tolist()

    colors = plt.cm.plasma(np.linspace(0.2, 0.85, len(labels)))

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(range(len(labels)), values, color=colors, edgecolor="#1a1a2e", height=0.6)

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("Số lượt khám")
    ax.set_title("TẦN SUẤT KHÁM BỆNH THEO LOẠI BỆNH (Top 10)", fontsize=14, fontweight="bold", pad=15)
    ax.grid(True, axis="x")

    # Thêm giá trị
    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                str(val), va="center", fontsize=10, fontweight="bold")

    fig.tight_layout()
    return _save(fig, "tan_suat_kham.png")


def ve_bieu_do_thuoc(med_df):
    """Vẽ biểu đồ thống kê dùng thuốc."""
    _setup_style()

    top_n = med_df.head(10)
    labels = top_n["Tên thuốc"].tolist()
    values = top_n["Số lượt dùng"].tolist()

    colors = plt.cm.viridis(np.linspace(0.2, 0.85, len(labels)))

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(range(len(labels)), values, color=colors, edgecolor="#1a1a2e", height=0.6)

    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=10)
    ax.invert_yaxis()
    ax.set_xlabel("Số lượt sử dụng")
    ax.set_title("THỐNG KÊ SỬ DỤNG THUỐC (Top 10)", fontsize=14, fontweight="bold", pad=15)
    ax.grid(True, axis="x")

    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                str(val), va="center", fontsize=10, fontweight="bold")

    fig.tight_layout()
    return _save(fig, "thong_ke_thuoc.png")


def ve_tat_ca(df, grouped_df, visit_df, med_df):
    """Vẽ tất cả biểu đồ."""
    print("\n📊 Đang tạo biểu đồ...")
    paths = []
    paths.append(ve_bieu_do_bmi(df))
    paths.append(ve_bieu_do_huyet_ap(grouped_df))
    paths.append(ve_bieu_do_tan_suat_kham(visit_df))
    paths.append(ve_bieu_do_thuoc(med_df))
    print(f"\n[✓] Đã tạo {len(paths)} biểu đồ trong thư mục: {CHART_DIR}")
    return paths
