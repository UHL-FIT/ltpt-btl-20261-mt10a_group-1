"""
views/main_window.py
====================
Cửa sổ chính của ứng dụng Quản lý Hồ sơ Bệnh nhân.
Giao diện sidebar navigation với 4 tab: Bệnh nhân, Lịch sử khám, Thuốc, Thống kê.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os


# ─── Color Scheme Y tế ───
COLOR_PRIMARY = "#1565C0"       # Xanh dương đậm
COLOR_PRIMARY_LIGHT = "#1E88E5" # Xanh dương nhạt
COLOR_ACCENT = "#42A5F5"        # Xanh accent
COLOR_BG = "#F5F7FA"            # Nền xám rất nhạt
COLOR_SIDEBAR = "#0D47A1"       # Sidebar xanh đậm
COLOR_SIDEBAR_HOVER = "#1565C0" # Hover sidebar
COLOR_SIDEBAR_ACTIVE = "#1E88E5"# Active sidebar
COLOR_WHITE = "#FFFFFF"
COLOR_TEXT = "#212121"
COLOR_TEXT_LIGHT = "#757575"
COLOR_BORDER = "#E0E0E0"
COLOR_SUCCESS = "#43A047"
COLOR_WARNING = "#FB8C00"
COLOR_DANGER = "#E53935"
COLOR_STAT_BG = "#E3F2FD"


def tao_cua_so_chinh(root):
    """
    Khởi tạo giao diện chính với sidebar navigation và content area.

    Args:
        root (tk.Tk): Cửa sổ gốc.

    Returns:
        dict: Tham chiếu tới các widget chính.
    """
    root.title("🏥 Quản Lý Hồ Sơ Bệnh Nhân")
    root.geometry("1280x720")
    root.minsize(1024, 600)
    root.configure(bg=COLOR_BG)

    # Thiết lập icon
    try:
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, "assets", "app_icon.ico")
        if os.path.exists(icon_path):
            root.iconbitmap(default=icon_path)
    except Exception:
        pass

    # ─── Style Configuration ───
    style = ttk.Style()
    style.theme_use('clam')

    # Treeview style
    style.configure("Treeview.Heading",
                     font=('Segoe UI', 10, 'bold'),
                     background=COLOR_PRIMARY,
                     foreground=COLOR_WHITE,
                     relief="flat")
    style.map("Treeview.Heading",
              background=[('active', COLOR_PRIMARY_LIGHT)])
    style.configure("Treeview",
                     font=('Segoe UI', 10),
                     rowheight=28,
                     background=COLOR_WHITE,
                     fieldbackground=COLOR_WHITE)
    style.map("Treeview",
              background=[('selected', COLOR_ACCENT)],
              foreground=[('selected', COLOR_WHITE)])

    # Button styles
    style.configure("Primary.TButton",
                     font=('Segoe UI', 10),
                     padding=(12, 6))
    style.configure("Danger.TButton",
                     font=('Segoe UI', 10),
                     padding=(12, 6))
    style.configure("TButton",
                     font=('Segoe UI', 10),
                     padding=(10, 5))

    # Entry style
    style.configure("TEntry", padding=(8, 4))

    ui = {}

    # ─── SIDEBAR (LEFT) ───
    sidebar = tk.Frame(root, bg=COLOR_SIDEBAR, width=220)
    sidebar.pack(side=tk.LEFT, fill=tk.Y)
    sidebar.pack_propagate(False)
    ui['sidebar'] = sidebar

    # Logo / Title
    logo_frame = tk.Frame(sidebar, bg=COLOR_SIDEBAR, pady=20)
    logo_frame.pack(fill=tk.X)

    tk.Label(logo_frame, text="🏥", font=('Segoe UI Emoji', 28),
             bg=COLOR_SIDEBAR, fg=COLOR_WHITE).pack()
    tk.Label(logo_frame, text="QUẢN LÝ", font=('Segoe UI', 14, 'bold'),
             bg=COLOR_SIDEBAR, fg=COLOR_WHITE).pack()
    tk.Label(logo_frame, text="HỒ SƠ BỆNH NHÂN", font=('Segoe UI', 10),
             bg=COLOR_SIDEBAR, fg=COLOR_ACCENT).pack()

    # Separator
    tk.Frame(sidebar, bg=COLOR_PRIMARY_LIGHT, height=2).pack(fill=tk.X, padx=15, pady=10)

    # Navigation buttons
    nav_items = [
        ("📋  Bệnh nhân", "benh_nhan"),
        ("🩺  Lịch sử khám", "lich_su_kham"),
        ("💊  Thuốc", "thuoc"),
        ("📊  Thống kê", "thong_ke"),
    ]

    ui['nav_buttons'] = {}
    for text, key in nav_items:
        btn = tk.Button(
            sidebar, text=text, font=('Segoe UI', 11),
            bg=COLOR_SIDEBAR, fg=COLOR_WHITE,
            activebackground=COLOR_SIDEBAR_ACTIVE, activeforeground=COLOR_WHITE,
            bd=0, relief="flat", anchor="w", padx=20, pady=12,
            cursor="hand2"
        )
        btn.pack(fill=tk.X, padx=5, pady=1)

        # Hover effects
        btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=COLOR_SIDEBAR_HOVER))
        btn.bind("<Leave>", lambda e, b=btn, k=key: _on_nav_leave(b, k, ui))

        ui['nav_buttons'][key] = btn

    # About button at bottom
    about_frame = tk.Frame(sidebar, bg=COLOR_SIDEBAR)
    about_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

    tk.Frame(about_frame, bg=COLOR_PRIMARY_LIGHT, height=1).pack(fill=tk.X, padx=15, pady=5)

    ui['btn_about'] = tk.Button(
        about_frame, text="ℹ️  Giới thiệu", font=('Segoe UI', 10),
        bg=COLOR_SIDEBAR, fg=COLOR_TEXT_LIGHT,
        activebackground=COLOR_SIDEBAR_HOVER, activeforeground=COLOR_WHITE,
        bd=0, relief="flat", anchor="w", padx=20, pady=8,
        cursor="hand2"
    )
    ui['btn_about'].pack(fill=tk.X, padx=5)

    # ─── MAIN CONTENT AREA (RIGHT) ───
    main_area = tk.Frame(root, bg=COLOR_BG)
    main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Header bar
    header = tk.Frame(main_area, bg=COLOR_WHITE, height=60)
    header.pack(fill=tk.X)
    header.pack_propagate(False)

    ui['lbl_page_title'] = tk.Label(
        header, text="📋 Danh sách Bệnh nhân",
        font=('Segoe UI', 16, 'bold'), bg=COLOR_WHITE, fg=COLOR_TEXT,
        padx=20
    )
    ui['lbl_page_title'].pack(side=tk.LEFT, fill=tk.Y)

    # Separator line under header
    tk.Frame(main_area, bg=COLOR_BORDER, height=1).pack(fill=tk.X)

    # Content frame (switchable)
    content = tk.Frame(main_area, bg=COLOR_BG)
    content.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
    ui['content_frame'] = content

    # ─── STATUS BAR (BOTTOM) ───
    status_bar = tk.Frame(main_area, bg=COLOR_STAT_BG, height=40)
    status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    status_bar.pack_propagate(False)

    ui['lbl_tong_bn'] = tk.Label(
        status_bar, text="Tổng bệnh nhân: 0",
        font=('Segoe UI', 10, 'bold'), bg=COLOR_STAT_BG, fg=COLOR_PRIMARY, padx=15
    )
    ui['lbl_tong_bn'].pack(side=tk.LEFT)

    ui['lbl_gioi_tinh'] = tk.Label(
        status_bar, text="Nam: 0 | Nữ: 0",
        font=('Segoe UI', 10), bg=COLOR_STAT_BG, fg=COLOR_TEXT_LIGHT, padx=15
    )
    ui['lbl_gioi_tinh'].pack(side=tk.LEFT)

    ui['lbl_tuoi_tb'] = tk.Label(
        status_bar, text="Tuổi TB: 0",
        font=('Segoe UI', 10), bg=COLOR_STAT_BG, fg=COLOR_TEXT_LIGHT, padx=15
    )
    ui['lbl_tuoi_tb'].pack(side=tk.LEFT)

    ui['lbl_bmi_tb'] = tk.Label(
        status_bar, text="BMI TB: 0.0",
        font=('Segoe UI', 10), bg=COLOR_STAT_BG, fg=COLOR_TEXT_LIGHT, padx=15
    )
    ui['lbl_bmi_tb'].pack(side=tk.LEFT)

    ui['lbl_benh'] = tk.Label(
        status_bar, text="Bệnh phổ biến: N/A",
        font=('Segoe UI', 10, 'italic'), bg=COLOR_STAT_BG, fg=COLOR_WARNING, padx=15
    )
    ui['lbl_benh'].pack(side=tk.RIGHT)

    # Set active page mặc định
    ui['active_page'] = 'benh_nhan'

    return ui


def _on_nav_leave(btn, key, ui):
    """Xử lý hover leave cho nav button - giữ active state."""
    if ui.get('active_page') == key:
        btn.configure(bg=COLOR_SIDEBAR_ACTIVE)
    else:
        btn.configure(bg=COLOR_SIDEBAR)


def set_active_nav(ui, active_key):
    """
    Đặt trạng thái active cho navigation button.

    Args:
        ui (dict): Dictionary UI widgets.
        active_key (str): Key của button đang active.
    """
    ui['active_page'] = active_key
    for key, btn in ui['nav_buttons'].items():
        if key == active_key:
            btn.configure(bg=COLOR_SIDEBAR_ACTIVE, font=('Segoe UI', 11, 'bold'))
        else:
            btn.configure(bg=COLOR_SIDEBAR, font=('Segoe UI', 11))

    # Cập nhật tiêu đề trang
    titles = {
        "benh_nhan": "📋 Danh sách Bệnh nhân",
        "lich_su_kham": "🩺 Lịch sử Khám bệnh",
        "thuoc": "💊 Lịch sử Thuốc",
        "thong_ke": "📊 Thống kê & Biểu đồ",
    }
    ui['lbl_page_title'].config(text=titles.get(active_key, ""))


def cap_nhat_status_bar(ui, stats):
    """
    Cập nhật thanh trạng thái phía dưới với dữ liệu thống kê.

    Args:
        ui (dict): Dictionary UI widgets.
        stats (dict): Dữ liệu thống kê từ model.
    """
    if not stats:
        return

    tong = stats.get('tong_bn', 0)
    nam = stats.get('nam', 0)
    nu = stats.get('nu', 0)
    tuoi_tb = stats.get('tuoi_tb', 0)
    bmi_tb = stats.get('bmi_tb', 0)
    benh = stats.get('benh_pho_bien', 'N/A')

    ui['lbl_tong_bn'].config(text=f"Tổng bệnh nhân: {tong}")
    ui['lbl_gioi_tinh'].config(text=f"Nam: {nam} | Nữ: {nu}")
    ui['lbl_tuoi_tb'].config(text=f"Tuổi TB: {tuoi_tb:.1f}")
    ui['lbl_bmi_tb'].config(text=f"BMI TB: {bmi_tb:.1f}")
    ui['lbl_benh'].config(text=f"Bệnh phổ biến: {benh}")
