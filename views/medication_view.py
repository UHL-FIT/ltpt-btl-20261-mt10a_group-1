"""
views/medication_view.py
========================
Giao diện hiển thị lịch sử thuốc của bệnh nhân đang chọn.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from views.main_window import (COLOR_BG, COLOR_WHITE, COLOR_PRIMARY,
                                COLOR_TEXT, COLOR_BORDER, COLOR_SUCCESS,
                                COLOR_DANGER, COLOR_TEXT_LIGHT)
from utils.validators import kiem_tra_ngay


def tao_medication_view(parent_frame):
    """
    Tạo giao diện lịch sử thuốc bên trong content frame.

    Args:
        parent_frame (tk.Frame): Frame cha.

    Returns:
        dict: Tham chiếu tới các widget.
    """
    mv = {}

    # ─── Patient Selection ───
    select_frame = tk.Frame(parent_frame, bg=COLOR_WHITE, pady=8, padx=10)
    select_frame.pack(fill=tk.X, pady=(0, 8))

    tk.Label(select_frame, text="Mã BN:", font=('Segoe UI', 10, 'bold'),
             bg=COLOR_WHITE, fg=COLOR_TEXT).pack(side=tk.LEFT, padx=(0, 5))

    mv['ent_ma_bn'] = ttk.Entry(select_frame, width=15, font=('Segoe UI', 10))
    mv['ent_ma_bn'].pack(side=tk.LEFT, padx=3)

    mv['btn_load'] = tk.Button(
        select_frame, text="🔍 Xem thuốc", font=('Segoe UI', 10),
        bg=COLOR_PRIMARY, fg=COLOR_WHITE, bd=0, padx=12, pady=5, cursor="hand2"
    )
    mv['btn_load'].pack(side=tk.LEFT, padx=5)

    mv['lbl_patient_name'] = tk.Label(
        select_frame, text="", font=('Segoe UI', 10, 'italic'),
        bg=COLOR_WHITE, fg=COLOR_TEXT_LIGHT
    )
    mv['lbl_patient_name'].pack(side=tk.LEFT, padx=10)

    mv['btn_them_thuoc'] = tk.Button(
        select_frame, text="➕ Thêm thuốc", font=('Segoe UI', 10),
        bg=COLOR_SUCCESS, fg=COLOR_WHITE, bd=0, padx=12, pady=5, cursor="hand2"
    )
    mv['btn_them_thuoc'].pack(side=tk.RIGHT, padx=3)

    mv['btn_xoa_thuoc'] = tk.Button(
        select_frame, text="🗑️ Xóa", font=('Segoe UI', 10),
        bg=COLOR_DANGER, fg=COLOR_WHITE, bd=0, padx=12, pady=5, cursor="hand2"
    )
    mv['btn_xoa_thuoc'].pack(side=tk.RIGHT, padx=3)

    # ─── TREEVIEW ───
    tree_frame = tk.Frame(parent_frame, bg=COLOR_WHITE)
    tree_frame.pack(fill=tk.BOTH, expand=True)

    scroll_y = ttk.Scrollbar(tree_frame)
    scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

    cols = ["ID", "Tên thuốc", "Liều lượng", "Tần suất", "Ngày bắt đầu", "Ngày kết thúc", "Ghi chú"]
    mv['cols'] = cols

    tree = ttk.Treeview(tree_frame, columns=cols, show="headings",
                         yscrollcommand=scroll_y.set)
    mv['tree'] = tree
    scroll_y.config(command=tree.yview)

    col_widths = {"ID": 50, "Tên thuốc": 180, "Liều lượng": 120, "Tần suất": 120,
                  "Ngày bắt đầu": 110, "Ngày kết thúc": 110, "Ghi chú": 150}

    for col in cols:
        tree.heading(col, text=col)
        w = col_widths.get(col, 100)
        anchor = tk.W if col in ["Tên thuốc", "Ghi chú"] else tk.CENTER
        tree.column(col, width=w, anchor=anchor)

    tree.pack(fill=tk.BOTH, expand=True)

    return mv


def hien_thi_lich_su_thuoc(mv, df):
    """
    Hiển thị dữ liệu lịch sử thuốc lên TreeView.

    Args:
        mv (dict): Dictionary UI widgets.
        df (pandas.DataFrame): Dữ liệu thuốc.
    """
    tree = mv['tree']
    for row in tree.get_children():
        tree.delete(row)

    if df.empty:
        return

    for _, row in df.iterrows():
        values = [
            row.get("id", ""),
            row.get("ten_thuoc", ""),
            row.get("lieu_luong", ""),
            row.get("tan_suat", ""),
            row.get("ngay_bat_dau", ""),
            row.get("ngay_ket_thuc", ""),
            row.get("ghi_chu", "")
        ]
        tree.insert("", tk.END, values=values)


def hien_thi_form_thuoc(parent_root):
    """
    Popup form thêm thuốc mới.

    Args:
        parent_root (tk.Tk): Cửa sổ cha.

    Returns:
        dict/None: Dữ liệu thuốc hoặc None.
    """
    top = tk.Toplevel(parent_root)
    top.title("➕ Thêm thuốc")
    top.configure(bg=COLOR_BG)
    top.resizable(False, False)
    top.grab_set()

    result = []

    header = tk.Frame(top, bg=COLOR_PRIMARY, height=45)
    header.pack(fill=tk.X)
    header.pack_propagate(False)
    tk.Label(header, text="💊 Thêm thuốc mới", font=('Segoe UI', 12, 'bold'),
             bg=COLOR_PRIMARY, fg=COLOR_WHITE, padx=15).pack(side=tk.LEFT, fill=tk.Y)

    form = tk.Frame(top, bg=COLOR_BG, padx=20, pady=15)
    form.pack(fill=tk.BOTH, expand=True)

    from datetime import datetime
    fields = {}

    def add_entry(label, key, row, width=30, required=False):
        lbl_text = f"{label} (*):" if required else f"{label}:"
        tk.Label(form, text=lbl_text, font=('Segoe UI', 10),
                 bg=COLOR_BG, fg=COLOR_TEXT).grid(row=row, column=0, padx=(0, 10), pady=7, sticky=tk.E)
        ent = ttk.Entry(form, width=width, font=('Segoe UI', 10))
        ent.grid(row=row, column=1, pady=7, sticky=tk.W)
        fields[key] = ent

    add_entry("Tên thuốc", "ten_thuoc", 0, required=True)
    add_entry("Liều lượng", "lieu_luong", 1)
    add_entry("Tần suất (VD: 2 lần/ngày)", "tan_suat", 2)
    add_entry("Ngày bắt đầu (dd/mm/yyyy)", "ngay_bat_dau", 3)
    fields["ngay_bat_dau"].insert(0, datetime.now().strftime("%d/%m/%Y"))
    add_entry("Ngày kết thúc (dd/mm/yyyy)", "ngay_ket_thuc", 4)
    add_entry("Ghi chú", "ghi_chu", 5)

    def on_save():
        ten_thuoc = fields["ten_thuoc"].get().strip()
        if not ten_thuoc:
            messagebox.showwarning("Lỗi", "Mời nhập tên thuốc!", parent=top)
            return

        nbd = fields["ngay_bat_dau"].get().strip()
        ok_nbd, _ = kiem_tra_ngay(nbd)
        if not ok_nbd:
            messagebox.showwarning("Lỗi", "Ngày bắt đầu không hợp lệ!", parent=top)
            return

        nkt = fields["ngay_ket_thuc"].get().strip()
        ok_nkt, _ = kiem_tra_ngay(nkt)
        if not ok_nkt:
            messagebox.showwarning("Lỗi", "Ngày kết thúc không hợp lệ!", parent=top)
            return

        result.append({
            "ten_thuoc": ten_thuoc,
            "lieu_luong": fields["lieu_luong"].get().strip(),
            "tan_suat": fields["tan_suat"].get().strip(),
            "ngay_bat_dau": nbd,
            "ngay_ket_thuc": nkt,
            "ghi_chu": fields["ghi_chu"].get().strip()
        })
        top.destroy()

    btn_frame = tk.Frame(form, bg=COLOR_BG)
    btn_frame.grid(row=6, column=0, columnspan=2, pady=(15, 5))

    tk.Button(btn_frame, text="💾 Lưu", font=('Segoe UI', 11, 'bold'),
              bg=COLOR_SUCCESS, fg=COLOR_WHITE, bd=0, padx=20, pady=6,
              command=on_save, cursor="hand2").pack(side=tk.LEFT, padx=8)
    tk.Button(btn_frame, text="❌ Hủy", font=('Segoe UI', 11),
              bg="#9E9E9E", fg=COLOR_WHITE, bd=0, padx=20, pady=6,
              command=top.destroy, cursor="hand2").pack(side=tk.LEFT, padx=8)

    top.update_idletasks()
    x = parent_root.winfo_x() + (parent_root.winfo_width() - top.winfo_reqwidth()) // 2
    y = parent_root.winfo_y() + (parent_root.winfo_height() - top.winfo_reqheight()) // 2
    top.geometry(f"+{x}+{y}")

    top.wait_window()
    return result[0] if result else None
