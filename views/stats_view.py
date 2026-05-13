"""
views/stats_view.py
===================
Giao diện hiển thị biểu đồ thống kê sử dụng Matplotlib nhúng vào Tkinter.
Bao gồm: Phân bố BMI, Phân bố tuổi, Top 10 bệnh phổ biến, Tần suất khám theo tháng.
"""

import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import pandas as pd
from views.main_window import (COLOR_BG, COLOR_WHITE, COLOR_PRIMARY,
                                COLOR_TEXT, COLOR_ACCENT)


def tao_stats_view(parent_frame):
    """
    Tạo giao diện thống kê với các biểu đồ Matplotlib.

    Args:
        parent_frame (tk.Frame): Frame cha.

    Returns:
        dict: Tham chiếu tới các widget thống kê.
    """
    sv = {}

    # Toolbar
    toolbar = tk.Frame(parent_frame, bg=COLOR_WHITE, pady=8, padx=10)
    toolbar.pack(fill=tk.X, pady=(0, 8))

    sv['btn_refresh'] = tk.Button(
        toolbar, text="🔄 Làm mới biểu đồ", font=('Segoe UI', 10),
        bg=COLOR_PRIMARY, fg=COLOR_WHITE, bd=0, padx=15, pady=5, cursor="hand2"
    )
    sv['btn_refresh'].pack(side=tk.LEFT)

    # Canvas for charts
    chart_frame = tk.Frame(parent_frame, bg=COLOR_WHITE)
    chart_frame.pack(fill=tk.BOTH, expand=True)
    sv['chart_frame'] = chart_frame

    return sv


def ve_bieu_do(sv, df_patients, df_examinations=None):
    """
    Vẽ các biểu đồ thống kê vào chart frame.

    Args:
        sv (dict): Dictionary UI widgets.
        df_patients (pandas.DataFrame): Dữ liệu bệnh nhân.
        df_examinations (pandas.DataFrame): Dữ liệu lịch sử khám (optional).
    """
    chart_frame = sv['chart_frame']

    # Xóa biểu đồ cũ
    for widget in chart_frame.winfo_children():
        widget.destroy()

    if df_patients.empty:
        lbl = tk.Label(chart_frame, text="📊 Chưa có dữ liệu để thống kê",
                       font=('Segoe UI', 14), bg=COLOR_WHITE, fg=COLOR_TEXT)
        lbl.pack(expand=True)
        return

    # Tạo figure 2x2
    fig = Figure(figsize=(12, 8), dpi=90, facecolor=COLOR_WHITE)
    fig.subplots_adjust(hspace=0.4, wspace=0.3)

    colors_blue = ['#1565C0', '#1E88E5', '#42A5F5', '#90CAF9', '#BBDEFB',
                   '#0D47A1', '#2196F3', '#64B5F6', '#E3F2FD', '#1976D2']
    colors_warm = ['#E53935', '#FB8C00', '#43A047', '#1E88E5', '#8E24AA',
                   '#00ACC1', '#FFB300', '#5E35B1', '#00897B', '#C0CA33']

    # ── 1. Phân bố Giới tính (Pie) ──
    ax1 = fig.add_subplot(221)
    gt_counts = df_patients['gioi_tinh'].value_counts()
    if not gt_counts.empty:
        wedges, texts, autotexts = ax1.pie(
            gt_counts.values, labels=gt_counts.index,
            autopct='%1.1f%%', colors=colors_blue[:len(gt_counts)],
            startangle=90, textprops={'fontsize': 9}
        )
        ax1.set_title('Phân bố Giới tính', fontsize=11, fontweight='bold', pad=10)

    # ── 2. Phân bố Tuổi (Histogram) ──
    ax2 = fig.add_subplot(222)
    tuoi_data = df_patients['tuoi'].values
    tuoi_valid = tuoi_data[tuoi_data > 0]
    if len(tuoi_valid) > 0:
        ax2.hist(tuoi_valid, bins=15, color=COLOR_ACCENT, edgecolor='white', alpha=0.85)
        ax2.set_xlabel('Tuổi', fontsize=9)
        ax2.set_ylabel('Số bệnh nhân', fontsize=9)
        ax2.set_title('Phân bố Tuổi', fontsize=11, fontweight='bold', pad=10)
        ax2.axvline(np.mean(tuoi_valid), color=COLOR_PRIMARY, linestyle='--',
                    label=f'TB: {np.mean(tuoi_valid):.1f}')
        ax2.legend(fontsize=8)

    # ── 3. Top 10 Bệnh phổ biến (Bar) ──
    ax3 = fig.add_subplot(223)
    benh_counts = df_patients['benh_chinh'].replace("", np.nan).dropna().value_counts().head(10)
    if not benh_counts.empty:
        bars = ax3.barh(range(len(benh_counts)), benh_counts.values,
                        color=colors_warm[:len(benh_counts)], edgecolor='white')
        ax3.set_yticks(range(len(benh_counts)))
        ax3.set_yticklabels(benh_counts.index, fontsize=8)
        ax3.set_xlabel('Số ca', fontsize=9)
        ax3.set_title('Top 10 Bệnh phổ biến', fontsize=11, fontweight='bold', pad=10)
        ax3.invert_yaxis()

        # Hiển thị số trên thanh
        for bar, val in zip(bars, benh_counts.values):
            ax3.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                     str(val), va='center', fontsize=8, fontweight='bold')

    # ── 4. Phân bố BMI (Box plot hoặc Bar) ──
    ax4 = fig.add_subplot(224)
    bmi_data = df_patients['bmi'].values
    bmi_valid = bmi_data[bmi_data > 0]
    if len(bmi_valid) > 0:
        # Group by BMI category
        phan_loai = df_patients[df_patients['bmi'] > 0]['phan_loai_bmi'].value_counts()
        if not phan_loai.empty:
            bars = ax4.bar(range(len(phan_loai)), phan_loai.values,
                           color=colors_blue[:len(phan_loai)], edgecolor='white')
            ax4.set_xticks(range(len(phan_loai)))
            ax4.set_xticklabels(phan_loai.index, fontsize=8, rotation=15)
            ax4.set_ylabel('Số bệnh nhân', fontsize=9)
            ax4.set_title('Phân loại BMI', fontsize=11, fontweight='bold', pad=10)

            for bar, val in zip(bars, phan_loai.values):
                ax4.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                         str(val), ha='center', fontsize=8, fontweight='bold')

    # Embed vào Tkinter
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
