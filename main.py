"""
ENTRY POINT – main.py
Nhiệm vụ DUY NHẤT: lắp ráp (wire up) Model, View, Controller rồi chạy.
File này ngắn gọn là dấu hiệu kiến trúc tốt.
"""
import tkinter as tk
from tkinter import ttk

from models.patient_model          import PatientModel
from views.manage_view             import ManageView
from views.stats_view              import StatsView
from controllers.patient_controller import PatientController


def main():
    root = tk.Tk()
    root.title("Hệ Thống Quản Lý Hồ Sơ Bệnh Nhân")
    root.geometry("1500x700")

    style = ttk.Style()
    style.theme_use('clam')

    # Tạo Notebook (tab container)
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True)

    # Khởi tạo Model
    model = PatientModel()

    # Khởi tạo các View (chỉ vẽ khung, chưa có dữ liệu)
    manage_view = ManageView(notebook)
    stats_view  = StatsView(notebook)

    notebook.add(manage_view, text="Quản lý Bệnh nhân")
    notebook.add(stats_view,  text="Thống kê & Báo cáo")

    # KHỞI TẠO CONTROLLER
    controller = PatientController(model, manage_view, stats_view, root)

    # Khởi tạo Controller – nó tự bind sự kiện và load dữ liệu ban đầu
    menubar = tk.Menu(root)
    
    # Menu Hệ Thống (Chứa Import / Export DB)
    system_menu = tk.Menu(menubar, tearoff=0)
    system_menu.add_command(label="📥 Nhập Database (Import)", command=controller.import_database)
    system_menu.add_command(label="📤 Sao lưu Database (Export)", command=controller.export_database)
    system_menu.add_separator()
    system_menu.add_command(label="❌ Thoát", command=root.quit)
    menubar.add_cascade(label="Hệ Thống", menu=system_menu)

    # Menu Trợ Giúp (Chứa Giới thiệu)
    help_menu = tk.Menu(menubar, tearoff=0)
    help_menu.add_command(label="ℹ️ Giới thiệu phần mềm", command=controller.show_about)
    menubar.add_cascade(label="Trợ Giúp", menu=help_menu)
    
    root.config(menu=menubar) # Gắn menubar vào cửa sổ chính
    
    # Khi người dùng chuyển sang tab Thống kê → tự động làm mới
    def on_tab_changed(event):
        if notebook.index(notebook.select()) == 1:
            controller.load_statistics()

    notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

    root.mainloop()


if __name__ == "__main__":
    main()
