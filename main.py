"""
ENTRY POINT – main.py
Nhiệm vụ DUY NHẤT: lắp ráp (wire up) Model, View, Controller rồi chạy.
"""
import tkinter as tk
from tkinter import ttk

# import sys
# import os

# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.patient_model            import PatientModel
from views.manage_view               import ManageView
from views.stats_view                import StatsView
from views.follow_up_view            import FollowUpView
from controllers.patient_controller  import PatientController
from utils.theme_manager             import ThemeManager, MODE_LABELS


def main():
    root = tk.Tk()
    root.title("Hệ Thống Quản Lý Hồ Sơ Bệnh Nhân")
    root.geometry("1500x700")
    root.minsize(1100, 600)

    style = ttk.Style()
    theme_manager = ThemeManager(root, style)

    # Tạo Notebook (tab container)
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Khởi tạo MVC
    model          = PatientModel()
    manage_view    = ManageView(notebook)
    stats_view     = StatsView(notebook)
    follow_up_view = FollowUpView(notebook)

    notebook.add(manage_view,    text="  Quản lý Bệnh nhân  ")
    notebook.add(stats_view,     text="  Thống kê & Báo cáo  ")
    notebook.add(follow_up_view, text="  📅 Lịch Tái Khám  ")

    # Khởi tạo Controller
    controller = PatientController(
        model, manage_view, stats_view, follow_up_view, root
    )

    # ── Đăng ký callback theme ──────────────────────────────────────────
    theme_manager.register_callback(manage_view.apply_theme)
    theme_manager.register_callback(stats_view.apply_theme)
    theme_manager.register_callback(follow_up_view.apply_theme)

    # ── Áp theme mặc định ──────────────────────────────────────────────
    theme_manager.set_mode('system')

    # ── Menu bar ────────────────────────────────────────────────────────
    menubar = tk.Menu(root)

    # Menu Hệ Thống
    system_menu = tk.Menu(menubar, tearoff=0)
    system_menu.add_command(label="📥 Nhập Database (Import)",
                            command=controller.import_database)
    system_menu.add_command(label="📤 Sao lưu Database (Export)",
                            command=controller.export_database)
    system_menu.add_separator()
    system_menu.add_command(label="❌ Thoát", command=root.quit)
    menubar.add_cascade(label="Hệ Thống", menu=system_menu)

    # Menu Giao Diện
    theme_var = tk.StringVar(value='system')

    def switch_theme(mode: str):
        theme_var.set(mode)
        theme_manager.set_mode(mode)

    theme_menu = tk.Menu(menubar, tearoff=0)
    for mode, label in MODE_LABELS.items():
        theme_menu.add_radiobutton(
            label=label,
            variable=theme_var,
            value=mode,
            command=lambda m=mode: switch_theme(m)
        )
    menubar.add_cascade(label="🎨 Giao Diện", menu=theme_menu)

    # Menu Trợ Giúp
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="ℹ️ Giới thiệu phần mềm",
                          command=controller.show_about)
    menubar.add_cascade(label="Trợ Giúp", menu=help_menu)

    root.config(menu=menubar)

    # ── Sự kiện chuyển tab ──────────────────────────────────────────────
    def on_tab_changed(event):
        idx = notebook.index(notebook.select())
        if idx == 1:                        # Tab Thống kê
            controller.load_statistics()
        elif idx == 2:                      # Tab Lịch Tái Khám
            controller.load_follow_ups()

    notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

    root.mainloop()


if __name__ == "__main__":
    main()